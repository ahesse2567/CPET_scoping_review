library(tidyverse)
library(stringr)
library(scales)
library(janitor)
# load fonts so Times New Roman works with ggplot2 + pdf rendering
extrafont::loadfonts(quiet = TRUE)
theme_update(text = element_text(family = "Times New Roman"))

# re-find which articles are ineligible in case I forgot to update this manaully
source("code/cpet_articles/tidying/combine_ineligible_articles.R")

ineligible_articles <- read_csv(
    "data/cpet_articles/text_analysis/ineligible_articles_combined.csv",
    show_col_types = FALSE) %>% 
    clean_names()

# load_bbb articles, removing potential Douglas bag or mixing chamber articles
bbb_articles <- read_csv("data/cpet_articles/text_analysis/all_bbb_articles.csv",
                         show_col_types = FALSE) %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    filter(!(doi_suffix %in% ineligible_articles$doi_suffix))

outlier_data <- read_csv("data/cpet_articles/text_analysis/Outliers - Outliers.csv",
                         show_col_types = FALSE) %>% 
    clean_names()

outlier_df <- full_join(bbb_articles, outlier_data, by = "doi_suffix") %>% 
    select(colnames(outlier_data)) %>% 
    filter(doi_suffix %in% bbb_articles$doi_suffix)


############### OUTLIERS #################

total_articles <- outlier_df %>% 
    distinct(doi_suffix, .keep_all = FALSE) %>% 
    nrow()

articles_reporting_outliers_tib <- outlier_df %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    mutate(outlier_documentation = !is.na(outlier_limit)) %>% 
    count(outlier_documentation) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n))
articles_reporting_outliers_tib

articles_reporting_outliers <- articles_reporting_outliers_tib %>%
    filter(outlier_documentation == TRUE) %>% 
    select(n) %>% pull()

pct_articles_reporting_outliers <- articles_reporting_outliers_tib %>%
    filter(outlier_documentation == TRUE) %>% 
    select(pct) %>%
    pull() %>% 
    round(3)

z <- qnorm(0.025, lower.tail = FALSE)
moe_pct_articles_reporting <-
    z * sqrt((pct_articles_reporting_outliers * (1 - pct_articles_reporting_outliers)) / total_articles)


# count by outlier cutoff type
outlier_cutoff_by_type <- outlier_df %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    ungroup() %>% 
    mutate(freq = prop.table(n)) %>% 
    arrange(desc(n))
outlier_cutoff_by_type

outlier_reporting_frequency_plot <- outlier_df %>% 
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
    geom_text(aes(label = scales::percent(pct)),
              family = "Times New Roman", vjust = -0.5) +
    geom_text(aes(label = n),
              family = "Times New Roman", vjust = -2) +
    xlab("Outlier Limit") +
    ylab("Count") +
    ylim(0, 2500 * ceiling(max(outlier_cutoff_by_type$n) / 2500)) +
    theme_minimal() +
    # labs(
    #     caption = str_wrap(
    #         paste(
    #             "Outlier cutoff reporting frequency. Data are expressed as counts and percentages. N = ",
    #             total_articles, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    theme(text=element_text(family="Times New Roman", size=12))
outlier_reporting_frequency_plot


# pct outlier cutoff by type
specified_outlier_cutoffs_by_type <- outlier_df %>% 
    select(outlier_limit) %>% 
    drop_na() %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    ungroup() %>% 
    mutate(freq = prop.table(n))
specified_outlier_cutoffs_by_type

# count of articles that specify outlier removal
count_outlier_procedure_described <- outlier_df %>% 
    select(outlier_limit) %>% 
    summarize_all(list(count_outlier_procedure_described = ~ sum(!is.na(.)))) %>% 
    pull()

pct_outlier_limits_plot <- outlier_df %>% 
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
    mutate(outlier_limit = if_else(outlier_limit == "other",
                                   str_to_title(outlier_limit),
                                   outlier_limit)) %>% 
    ggplot(aes(x = outlier_limit, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)),
              family = "Times New Roman", vjust = -0.5) +
    geom_text(aes(label = n),
              family = "Times New Roman", vjust = -2) +
    xlab("Outlier Limit") +
    ylab("Count") +
    ylim(0, 250) +
    theme_minimal() +
    # labs(
    #     caption = str_wrap(
    #         paste("Outlier cutoff frequencies. Data are expressed as counts and percentages. N = ",
    #               count_outlier_procedure_described, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    theme(text=element_text(family="Times New Roman", size=12))
pct_outlier_limits_plot


# percentage of articles that specify outlier removal
outlier_df %>% 
    select(outlier_limit) %>% 
    summarize_all(list(
        pct_outlier_procedure_described = ~ sum(!is.na(.)) / length(.)*100))

outlier_function_tib <- outlier_df %>% 
    rowwise() %>% 
    mutate(outlier_avg_func = any(!is.na(c(outlier_avg_type,
                                           outlier_avg_subtype,
                                           outlier_avg_amount,
                                           outlier_avg_mos,
                                           outlier_avg_mean_type)))) %>% 
    count(outlier_avg_func) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n))
outlier_function_tib

n_outlier_func_reporting <- outlier_function_tib %>% 
    filter(outlier_avg_func == TRUE) %>% 
    select(n) %>% 
    pull()

pct_outlier_func_reporting <- outlier_function_tib %>% 
    filter(outlier_avg_func == TRUE) %>% 
    select(pct) %>% 
    pull()

moe_pct_outlier_func_reporting <-
    z * sqrt((pct_outlier_func_reporting * (1 - pct_outlier_func_reporting)) / total_articles)


outlier_func_by_type <- outlier_df %>% 
    rowwise() %>% 
    mutate(outlier_avg_func = any(!is.na(c(outlier_avg_type,
                                           outlier_avg_subtype,
                                           outlier_avg_amount,
                                           outlier_avg_mos,
                                           outlier_avg_mean_type)))) %>% 
    filter(outlier_avg_func== TRUE) %>% 
    count(outlier_avg_type) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    arrange(desc(n))
outlier_func_by_type

###### By type

n_breath_outlier_funcs <- outlier_func_by_type %>% 
    filter(outlier_avg_type == "breath") %>% 
    select(n) %>% 
    pull()

pct_breath_outlier_funcs <- outlier_func_by_type %>% 
    filter(outlier_avg_type == "breath") %>% 
    select(pct) %>% 
    pull()
pct_breath_outlier_funcs <- sprintf("%.1f", pct_breath_outlier_funcs * 100)

n_time_outlier_funcs <- outlier_func_by_type %>% 
    filter(outlier_avg_type == "time") %>% 
    select(n) %>% 
    pull()

pct_time_outlier_funcs <- outlier_func_by_type %>% 
    filter(outlier_avg_type == "time") %>% 
    select(pct) %>% 
    pull()
pct_time_outlier_funcs <- sprintf("%.1f", pct_time_outlier_funcs * 100)

outlier_func_by_type_amount <- outlier_df %>% 
    rowwise() %>% 
    mutate(outlier_avg_func = any(!is.na(c(outlier_avg_type,
                                           outlier_avg_subtype,
                                           outlier_avg_amount,
                                           outlier_avg_mos,
                                           outlier_avg_mean_type)))) %>% 
    filter(outlier_avg_func== TRUE) %>% 
    count(outlier_avg_type, outlier_avg_amount) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    arrange(desc(n))

# organize by type and THEN by frequency
# some kind of double line between breath and time methods so readers
# can differentiate those faster

outlier_func_by_type_amount

#$ calculate number and pct that did both limit and function but no table


###### 5 breath functions

n_5_breath_func <- outlier_func_by_type_amount %>% 
    filter(outlier_avg_amount == 5 & outlier_avg_type == "breath") %>% 
    select(n) %>% 
    pull()

pct_5_breath_func <- outlier_func_by_type_amount %>% 
    filter(outlier_avg_amount == 5 & outlier_avg_type == "breath") %>% 
    select(pct) %>% 
    pull()
pct_5_breath_func <- sprintf("%.1f", pct_5_breath_func * 100)
