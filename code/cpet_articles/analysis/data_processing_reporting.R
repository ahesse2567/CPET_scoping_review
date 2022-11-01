# Analysis of how often papers report data processing procedures and what
# those procedures are

library(tidyverse)

text_data <- read_csv("data/cpet_articles/text_analysis/Manual text analysis - Data.csv",
                      show_col_types = FALSE)

bbb_articles <- read_csv("data/cpet_articles/text_analysis/bbb_articles.csv",
                         show_col_types = FALSE)

merge_df <- inner_join(text_data, bbb_articles, by = "doi_suffix") %>% 
    janitor::clean_names()

############### OUTLIERS #################

# count by outlier cutoff type
merge_df %>% 
    group_by(outliers) %>% 
    summarize(n = n())

# pct outlier cutoff by type
merge_df %>% 
    select(outliers) %>% 
    drop_na() %>% 
    group_by(outliers) %>% 
    summarize(n = n()) %>% 
    mutate(freq = n / sum(n) * 100)

# count of articles that specify outlier removal
merge_df %>% 
    select(outliers) %>% 
    summarize_all(list(count_outlier_procedure_described = ~ sum(!is.na(.))))

# percentage of articles that specify outlier removal
merge_df %>% 
    select(outliers) %>% 
    summarize_all(list(
        pct_outlier_procedure_described = ~ sum(!is.na(.)) / length(.)*100))

############### INTERPOLATION #################

# count of articles that specify interpolation procedures
merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    summarise(across(everything(), .fns = ~!is.na(.))) %>% 
    summarize(interpolation_details = interpolation_type | interpolation_time_s) %>% 
    sum()

# percentage of articles that specify interpolation procedures
merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    summarise(across(everything(), .fns = ~!is.na(.))) %>% 
    summarize(interpolation_details = interpolation_type | interpolation_time_s) %>% 
    summarize(pct = sum(interpolation_details) / n() * 100)

# pct interpolation method by type
merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    mutate(interpolation_details = 
               !is.na(interpolation_type) | !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    mutate(procedure = paste0(interpolation_type, "-", interpolation_time_s)) %>% 
    group_by(procedure) %>% 
    summarize(n = n()) %>% 
    mutate(freq = n / sum(n) * 100)

# pct interpolation method by time only
merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    mutate(interpolation_details = !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    group_by(interpolation_time_s) %>% 
    summarize(n = n()) %>% 
    mutate(freq = n / sum(n) * 100)

# pct interpolation method by type only
merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    mutate(interpolation_details = !is.na(interpolation_type)) %>% 
    filter(interpolation_details == TRUE) %>% 
    group_by(interpolation_type) %>% 
    summarize(n = n()) %>% 
    mutate(freq = n / sum(n) * 100)
