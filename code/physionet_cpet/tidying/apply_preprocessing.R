# Remove outliers, then create 10, 30, and 60-second bin averages as
# these are the overall most popular

suppressPackageStartupMessages(library(tidyverse))
library(gasExchangeR)
library(progress)
library(fs)

# remove outliers, apply different averaging methods

cpets_comb <- read_csv(
    path("data/physionet_cpet//tidy/cpets_comb_bbb.csv"),
                      show_col_types = FALSE)

# get list names
list_names <- cpets_comb %>% 
    dplyr::select(id_test) %>% 
    unique() %>% 
    pull()

# split by test ID and remove outliers
cpet_df_list <- cpets_comb %>% 
    select(-id) %>% # we have the ID within id_test
    group_split(id_test) %>% 
    setNames(list_names) %>% 
    map(ventilatory_outliers, sd_lim = 4, max_passes = 1, .progress = TRUE)

# breath-by-breath (raw/unaveraged), 10, 30, and 60 second time-bin averages
averaging_settings <- list(time_bin_60 = list(
                               gasExchangeR::avg_exercise_test,
                               method = "time",
                               calc_type = "bin",
                               time_col = "time",
                               bin_w = 60),
                           time_bin_30 = list(
                               gasExchangeR::avg_exercise_test,
                               method = "time",
                               calc_type = "bin",
                               time_col = "time",
                               bin_w = 30),
                           time_bin_10 = list(
                               gasExchangeR::avg_exercise_test,
                               method = "time",
                               calc_type = "bin",
                               time_col = "time",
                               bin_w = 10)
)

# modeled after my dissertation code. It could probably be better.
processing_combinations <- expand_grid(averaging_settings)

process_cpet <- function(cpet_df, cpet_id, processing_settings) {
    # applies data processing to a cpet data frame and writes the
    # file to a csv. The csv file name uses the processing settings
    # and the cpet_id.
    
    out_df_list <- vector(mode = "list",
                          length = nrow(processing_settings))
    
    for(i in 1:nrow(processing_combinations)) {
        
        temp_df <- cpet_df
        
        if (!is.null(processing_settings[[i, "averaging_settings"]][[1]])) {
            # extract all params for readability
            all_params <- processing_settings[[i, "averaging_settings"]][[1]]
            params <- append(all_params[2:length(all_params)],
                             list(.data = temp_df),
                             after = 0)
            temp_df <- do.call(what = all_params[[1]], params)
        }
        
        averaging_procedure <-
            names(processing_settings[i, "averaging_settings"][[1]])
        
        temp_df <- temp_df %>%
            mutate(averaging_procedure = averaging_procedure)
        
        out_df_list[[i]] <- temp_df
        names(out_df_list)[i] <-
            paste0(cpet_id, "-", averaging_procedure)
        
    }
    
    out_df_list
}

# uncomment to test if function works
# i <- 1
# temp <- process_cpet(cpet_df_list[[i]],
#                      cpet_id = names(cpet_df_list[i]),
#                      processing_settings = processing_combinations)

pb <- progress_bar$new(
    total = length(cpet_df_list),
    format = "[:bar] :current/:total:percent eta: :eta ",
    clear = TRUE)

all_dfs <- vector(mode = "list", length = length(cpet_df_list))

print("Creating CPETs with different data processing combinations")
for(i in seq_along(cpet_df_list)) {
    pb$tick()
    all_dfs[[i]] <- process_cpet(
        cpet_df_list[[i]],
        cpet_id = names(cpet_df_list[i]),
        processing_settings = processing_combinations)
}

all_dfs_unlisted <- unlist(all_dfs, recursive = FALSE)

all_dfs_comb <- bind_rows(all_dfs_unlisted)
# saving as one giant CSV seems to get stuck less often
write_csv(all_dfs_comb, 
          path("data/physionet_cpet/tidy/processed_cpets_comb.csv.gz"))

