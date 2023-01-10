library(tidyverse)
library(stringr)
library(scales)
library(janitor)

ineligible_articles <- read_csv("data/cpet_articles/text_analysis/combined_ineligible_articles.csv") %>% 
    clean_names()

# load_bbb articles, removing potential Douglas bag or mixing chamber articles
bbb_articles <- read_csv("data/cpet_articles/text_analysis/all_bbb_articles.csv",
                         show_col_types = FALSE) %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    filter(!(doi_suffix %in% ineligible_articles$doi_suffix))

outlier_data <- read_csv("data/cpet_articles/text_analysis/Outliers - Outliers.csv",
                         show_col_types = FALSE) %>% 
    clean_names()

merge_df <- full_join(bbb_articles, outlier_data, by = "doi_suffix") %>% 
    select(colnames(outlier_data)) %>% 
    filter(doi_suffix %in% bbb_articles$doi_suffix)
    

############### OUTLIERS #################

total_articles <- merge_df %>% 
    distinct(doi_suffix, .keep_all = FALSE) %>% 
    nrow()

articles_reporting_outliers <- merge_df %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    mutate(outlier_documentation = is.na(outlier_limit)) %>% 
    count(outlier_documentation) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n))
articles_reporting_outliers

# count by outlier cutoff type
outlier_cutoff_by_type <- merge_df %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    ungroup() %>% 
    mutate(freq = prop.table(n)) %>% 
    arrange(desc(n))
outlier_cutoff_by_type

outlier_reporting_frequency_plot <- merge_df %>% 
    count(outlier_limit) %>% 
    mutate(pct = round(prop.table(n),4)) %>% 
    mutate(outlier_limit = if_else(
        is.na(outlier_limit), "Unspecified", str_to_title(outlier_limit)),
        outlier_limit = if_else(pct < 0.01, "other", outlier_limit)) %>% 
    group_by(outlier_limit) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    ggplot(aes(x = outlier_limit, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Outlier Limit") +
    ylab("Count") +
    ylim(0, 2000 * ceiling(max(outlier_cutoff_by_type$n) / 2000)) +
    theme_minimal() +
    # labs(
    #     caption = str_wrap(
    #         paste(
    #             "Outlier cutoff reporting frequency. Data are expressed as counts and percentages. N = ",
    #             total_articles, ".", sep = ""), width = 100)) +
    theme(plot.caption = element_text(hjust=0))
outlier_reporting_frequency_plot


# pct outlier cutoff by type
specified_outlier_cutoffs_by_type <- merge_df %>% 
    select(outlier_limit) %>% 
    drop_na() %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    mutate(freq = n / sum(n) * 100)
specified_outlier_cutoffs_by_type

# count of articles that specify outlier removal
count_outlier_procedure_described <- merge_df %>% 
    select(outlier_limit) %>% 
    summarize_all(list(count_outlier_procedure_described = ~ sum(!is.na(.)))) %>% 
    pull()

pct_outlier_limits_plot <- merge_df %>% 
    select(outlier_limit) %>% 
    drop_na() %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    mutate(pct = prop.table(n),
           outlier_limit = if_else(pct < 0.02, "other", outlier_limit)) %>%
    group_by(outlier_limit) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(outlier_limit = str_to_title(outlier_limit)) %>% 
    ggplot(aes(x = outlier_limit, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Outlier Limit") +
    ylab("Count") +
    ylim(0, 200 * ceiling(max(specified_outlier_cutoffs_by_type$n) / 200)) +
    theme_minimal() +
    # labs(
    #     caption = str_wrap(
    #         paste("Outlier cutoff frequencies. Data are expressed as counts and percentages. N = ",
    #               count_outlier_procedure_described, ".", sep = ""), width = 100)) +
    theme(plot.caption = element_text(hjust=0))
pct_outlier_limits_plot


# percentage of articles that specify outlier removal
merge_df %>% 
    select(outlier_limit) %>% 
    summarize_all(list(
        pct_outlier_procedure_described = ~ sum(!is.na(.)) / length(.)*100))
