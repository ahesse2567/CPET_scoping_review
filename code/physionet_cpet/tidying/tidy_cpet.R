# Turn the raw data provided by physionet into tidy breath-by-breath 
# data we can use for analysis. The tidy data has more variables, such as
# ventilatory equivalents, as well as some merged ID information. The tidy
# tests also have any warm-up periods removed.

suppressPackageStartupMessages(library(tidyverse))
library(fs)

# For additional details on the data, see the link below
# https://physionet.org/content/treadmill-exercise-cardioresp/1.0.1/

cpets_comb_raw <- read_csv(
    path("data/physionet_cpet/raw/test_measure.csv"),
                          show_col_types = FALSE) %>% 
    janitor::clean_names()

subject_info <- read_csv(
    path("data/physionet_cpet/raw/subject-info.csv"),
                         show_col_types = FALSE) %>% 
    janitor::clean_names()

# merging with demographics, calculating several derived vars
cpets_comb <- cpets_comb_raw %>% 
    relocate(contains("id")) %>% 
    left_join(subject_info, by = c("id", "id_test")) %>% 
    mutate(vo2_kg = vo2 / weight,
           rer = vco2 / vo2,
           vt = ve / rr * 1000,
           ve_vo2 = ve / vo2 * 1000,
           ve_vco2 = ve / vco2 * 1000,
           excess_co2 = (vco2^2 / vo2) - vco2) %>% 
    dplyr::select(-c("humidity", "temperature", "height", "weight")) %>% 
    relocate(c("age", "sex")) %>% 
    relocate(c("hr", "vo2_kg", "vo2", "vco2", "rer", "vt", "rr", "ve"),
             .after = speed)

# identify tests with missing core ventilatory variables
missing_vent_dat <- cpets_comb %>% 
    filter(is.na(vo2) | is.na(vco2) | is.na(ve)) %>% 
    summarize(id_test = unique(id_test), n = n(), .by = id_test)
missing_vent_dat
# all of the ids in the above output have many, many rows missing, suggesting
# ventilatory vars were missing for the essentially the entire test.

# remove test IDs with considerable missing ventilatory data
cpets_comb <- cpets_comb %>% 
    anti_join(missing_vent_dat, by = "id_test")

# examine if other variables are missing
other_missing_vars <- cpets_comb %>% 
    filter(if_any(everything(), \(x) is.na(x))) %>% 
    summarize(id_test = unique(id_test), n_row = n(), .by = id_test)
other_missing_vars
# other_missing_vars shows that the HR signal dropped 1-5 times in 322 tests.
# I won't interpolate that for now because we probably don't need to.

# Investigating step vs. incremental protocols 
cpets_comb %>% 
    mutate(speed_diff = round(speed - lag(speed), 1)) %>% 
    reframe(id_test = unique(id_test),
              speed_diff = unique(speed_diff, na.rm = TRUE),
              .by = id_test) %>%
    filter(speed_diff > 0.1)
# Not every test conforms EXACTLY to the online description, but
# it appears that jumps in speed by more than 0.1 kph indeed correspond
# to stage tests or tests that may have skipped (or at least not included) a
# warm up. I think filtering out speeds less than or equal to 5 mph is okay.

# removing warm-up and cool-down periods
cpets_comb <- cpets_comb %>% 
    filter(speed > 5) %>% 
    # restart the time to begin at 0 when graded exercise begins
    mutate(time = time - min(time), .by = "id_test")

if(!dir_exists("data/physionet_cpet/tidy")) {
    dir_create("data/physionet_cpet/tidy")
}

write_csv(cpets_comb, 
          path("data/physionet_cpet/tidy/cpets_comb_bbb.csv"))
