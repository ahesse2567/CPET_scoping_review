# Find how VO2max percentiles drop across different individuals using
# Physionet treadmill ramp data

library(tidyverse)
library(fs)

physionet_cpets_comb <- read_csv(
    path("data/physionet_cpet/tidy/processed_cpets_comb.csv.gz"),
    show_col_types = FALSE)

# remove data where the max RER was less than 1.0.
# I know this is NOT a VO2 plateau by any means, but it at least
# matches the FRIEND registry data
vo2peak_tbl <- physionet_cpets_comb %>% 
    filter(max(rer) >= 1, .by = id_test) %>% 
    # calculate VO2peak by test_id
    summarize(age = unique(age),
              sex = unique(sex),
              vo2_kg_peak = max(vo2_kg, na.rm = TRUE), 
              .by = c(id_test, averaging_procedure)) %>% 
    relocate(averaging_procedure, .after = "sex") %>% 
    # remove all ages outside of 20-89 for looking up FRIEND data
    filter(age >= 20 & age <= 89) %>% 
    # round age down to the nearest year
    mutate(age = floor(age))


# load FRIEND registry VO2peak table
vo2peak_friend_lookup <- read_csv(
    path("data/physionet_cpet/raw/friend_vo2peak.csv"),
    show_col_types = FALSE) %>% 
    janitor::clean_names()

# convert m and f to 0 and 1, respectively
vo2peak_friend_lookup <- vo2peak_friend_lookup %>% 
    mutate(sex = if_else(sex == "m", 0, 1))

# use mean and standard deviation by age, sex, and modality
# to essentially get a Z score to percentile
vo2peak_percentile_calc <- function(lookup_tbl,
                                    age_lookup, 
                                    sex_lookup, 
                                    vo2peak, 
                                    modality_lookup = "treadmill") {
    # Determine the correct age group
    age_group <- lookup_tbl %>%
        dplyr::filter(age_group_min <= age_lookup & 
                          age_group_max >= age_lookup) %>% 
        dplyr::filter(sex == sex_lookup) %>% 
        dplyr::filter(modality == modality_lookup)
    
    if (nrow(age_group) != 1) {
        stop("No matching age group found in the lookup table.")
    }
    
    # Extract the mean and standard deviation for the age group
    mean_vo2 <- age_group$vo2peak_mean
    sd_vo2 <- age_group$vo2peak_sd
    
    # Calculate the percentile directly using the pnorm() function
    percentile <- pnorm(vo2peak, mean = mean_vo2, sd = sd_vo2) * 100
    
    percentile
}

vo2peak_tbl <- vo2peak_tbl %>% 
    mutate(vo2peak_percentile = 
               vo2peak_percentile_calc(lookup_tbl = vo2peak_friend_lookup,
                                       age_lookup = age,
                                       sex_lookup = sex,
                                       vo2peak = vo2_kg_peak),
           .by = c(id_test, averaging_procedure))

vo2peak_tbl %>% 
    mutate(avg_duration = str_extract(averaging_procedure,
                                      "\\d+") %>% 
               as.numeric()
           ) %>% 
    slice_head(n = 6) %>% 
    clipr::write_clip()

vo2peak_tbl_wide <- vo2peak_tbl %>%
    pivot_wider(
        id_cols = c(id_test, age, sex),
        names_from = averaging_procedure,
        values_from = vo2peak_percentile
    ) %>% 
    mutate(
        diff_10_vs_30 = time_bin_10 - time_bin_30,
        diff_10_vs_60 = time_bin_10 - time_bin_60,
        diff_30_vs_60 = time_bin_30 - time_bin_60
    )

physionet_cpets_comb %>% 
    filter(id_test == "534_1") %>% 
    ggplot(aes(x = time, y = vo2_kg, color = averaging_procedure)) +
    geom_point(alpha = 0.5)

# calculate some descriptive statistics


# repeat the same thing but using the ACSM reference standards
