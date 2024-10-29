library(tidyverse)
library(stringr)
library(scales)
library(janitor)
library(binom)
# load fonts so Times works with ggplot2 + pdf rendering
extrafont::loadfonts(quiet = TRUE)
# theme_replace(text = element_text(family = "Times"))

# re-find which articles are ineligible in case I forgot to update this manually
source("code/cpet_articles/tidying/combine_ineligible_articles.R")

ineligible_articles <- read_csv(
    "data/cpet_articles/text_analysis/ineligible_articles_combined.csv",
    show_col_types = FALSE) %>% 
    clean_names()

# load_bbb articles, removing potential Douglas bag or mixing chamber articles
bbb_articles <- read_csv("data/cpet_articles/text_analysis/bbb_articles.csv",
                         show_col_types = FALSE) %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    filter(!(doi_suffix %in% ineligible_articles$doi_suffix))

outlier_data <- read_csv(
    "data/cpet_articles/text_analysis/Outliers - Outliers.csv",
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
    mutate(prop = prop.table(n))
articles_reporting_outliers_tib

n_articles_reporting_outliers <- articles_reporting_outliers_tib %>%
    filter(outlier_documentation == TRUE) %>% 
    select(n) %>% pull()

prop_articles_reporting_outliers <- articles_reporting_outliers_tib %>%
    filter(outlier_documentation == TRUE) %>% 
    select(prop) %>%
    pull() %>% 
    round(3)

# z <- qnorm(0.025, lower.tail = FALSE)
# Using agresti-coull method for confidence intervals
moe_prop_articles_reporting <- binom.confint(x = n_articles_reporting_outliers,
                                             n = total_articles,
                                             conf.level = 0.95,
                                             methods = "ac")
    # z * sqrt((prop_articles_reporting_outliers * (1 - prop_articles_reporting_outliers)) / total_articles)



# count by outlier cutoff type
outlier_cutoff_by_type <- outlier_df %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    arrange(desc(n))
outlier_cutoff_by_type

label_size <- 10
caption_size <- 20
axes_text_size <- 25

outlier_reporting_frequency_plot <- outlier_df %>% 
    count(outlier_limit) %>% 
    mutate(prop = round(prop.table(n),4)) %>% 
    mutate(outlier_limit = if_else(
        is.na(outlier_limit), "Unspecified", str_to_title(outlier_limit)),
        outlier_limit = if_else(prop < 0.01, "other", outlier_limit)) %>% 
    group_by(outlier_limit) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    ggplot(aes(x = outlier_limit, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)),
              # family = "Times", 
              vjust = -0.5) +
    geom_text(aes(label = n),
              # family = "Times", 
              vjust = -2) +
    xlab("Outlier Limit") +
    ylab("Count") +
    ylim(0, plyr::round_any(max(outlier_cutoff_by_type$n),
                                2250, ceiling)) +
    theme_minimal() +
    # labs(
    #     caption = str_wrap(
    #         paste(
    #             "Outlier cutoff reporting frequency. Data are expressed as counts and percentages. N = ",
    #             total_articles, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    theme(text=element_text(
        # family="Times", 
        size=12))
outlier_reporting_frequency_plot

outlier_reporting_frequency_plot_ACSM <- outlier_df %>% 
    count(outlier_limit) %>% 
    mutate(prop = round(prop.table(n),4)) %>% 
    mutate(outlier_limit = if_else(is.na(outlier_limit),
                                   "Unspecified",
                                   str_to_upper(outlier_limit)),
           outlier_limit = str_remove(outlier_limit, " / 99%"),
           outlier_limit = if_else(prop < 0.01, "Other", outlier_limit)) %>% 
    group_by(outlier_limit) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    ggplot(aes(x = outlier_limit, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)),
              family = "Times", 
              vjust = -0.5, size = label_size) +
    geom_text(aes(label = n),
              family = "Times", vjust = -2, size = label_size) +
    xlab("Outlier Limit") +
    ylab("Count") +
    ylim(0, plyr::round_any(max(outlier_cutoff_by_type$n),
                            2250, ceiling)) +
    theme_minimal() +
    # labs(
    #     caption = str_wrap(
    #         paste(
    #             "Outlier cutoff reporting frequency. Data are expressed as counts and percentages. N = ",
    #             total_articles, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    labs(caption = "Counts and percentages of articles reporting outlier methods and their types.") +
    theme(text=element_text(family="Times", size=12),
          axis.text.x = element_text(size = axes_text_size),
          axis.text.y = element_text(size = axes_text_size),
          axis.title = element_text(size = axes_text_size),
          plot.caption = element_text(size = caption_size,
                                      hjust = 0))
outlier_reporting_frequency_plot_ACSM

ggsave("graphics/outlier_reporting_ACSM.tiff",
       outlier_reporting_frequency_plot_ACSM,
       width = 13,
       height = 8.5,
       units = "in",
       bg = "white")

# prop outlier cutoff by type
specified_outlier_cutoffs_by_type <- outlier_df %>% 
    select(outlier_limit) %>% 
    drop_na() %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n))
specified_outlier_cutoffs_by_type

# count of articles that specify outlier removal
count_outlier_procedure_described <- outlier_df %>% 
    select(outlier_limit) %>% 
    summarize_all(list(count_outlier_procedure_described = ~ sum(!is.na(.)))) %>% 
    pull()

prop_outlier_limits_plot <- outlier_df %>% 
    select(outlier_limit) %>% 
    drop_na() %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    mutate(prop = prop.table(n),
           outlier_limit = if_else(prop < 0.02, "other", outlier_limit)) %>%
    group_by(outlier_limit) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    mutate(outlier_limit = if_else(outlier_limit == "other",
                                   str_to_title(outlier_limit),
                                   outlier_limit)) %>% 
    ggplot(aes(x = outlier_limit, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)),
              # family = "Times",
              vjust = -0.5) +
    geom_text(aes(label = n),
              # family = "Times", 
              vjust = -2) +
    xlab("Outlier Limit") +
    ylab("Count") +
    ylim(0, 250) +
    theme_minimal() +
    # labs(
    #     caption = str_wrap(
    #         paste("Outlier cutoff frequencies. Data are expressed as counts and percentages. N = ",
    #               count_outlier_procedure_described, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    theme(text=element_text(
        # family="Times", 
                            size=12))
prop_outlier_limits_plot

ggsave(here::here("graphics/prop_outlier_limits_plot.jpg"),
       prop_outlier_limits_plot)

prop_outlier_limits_plot_ACSM <- outlier_df %>% 
    select(outlier_limit) %>% 
    drop_na() %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    mutate(prop = prop.table(n),
           outlier_limit = if_else(prop < 0.02, "Other", outlier_limit),
           outlier_limit = str_remove(outlier_limit, " / \\d{2}%")) %>%
    group_by(outlier_limit) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    mutate(outlier_limit = if_else(outlier_limit == "Other",
                                   str_to_title(outlier_limit),
                                   outlier_limit)) %>% 
    ggplot(aes(x = outlier_limit, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)),
              family = "Times", vjust = -0.5, size = label_size) +
    geom_text(aes(label = n),
              family = "Times", vjust = -2, size = label_size) +
    xlab("Outlier Limit") +
    ylab("Count") +
    ylim(0, 250) +
    theme_minimal() +
    # labs(
    #     caption = str_wrap(
    #         paste("Outlier cutoff frequencies. Data are expressed as counts and percentages. N = ",
    #               count_outlier_procedure_described, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    labs(caption = "Counts and percentages of specified outlier removal limits.") +
    theme(text=element_text(family="Times", size=12),
          axis.text.x = element_text(size = axes_text_size),
          axis.text.y = element_text(size = axes_text_size),
          axis.title = element_text(size = axes_text_size),
          plot.caption = element_text(size = caption_size,
                                      hjust = 0))
prop_outlier_limits_plot_ACSM

ggsave("graphics/outlier_prevalence_by_type_ACSM.tiff",
       prop_outlier_limits_plot_ACSM,
       width = 13,
       height = 8.5,
       units = "in",
       bg = "white")

# percentage of articles that specify outlier removal
outlier_df %>% 
    select(outlier_limit) %>% 
    summarize_all(list(
        prop_outlier_procedure_described = ~ sum(!is.na(.)) / length(.)*100))

outlier_function_tib <- outlier_df %>% 
    rowwise() %>% 
    mutate(outlier_avg_func = any(!is.na(c(outlier_avg_type,
                                           outlier_avg_subtype,
                                           outlier_avg_amount,
                                           outlier_avg_mos,
                                           outlier_avg_mean_type)))) %>% 
    count(outlier_avg_func) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n))
outlier_function_tib

n_outlier_func_reporting <- outlier_function_tib %>% 
    filter(outlier_avg_func == TRUE) %>% 
    select(n) %>% 
    pull()

prop_outlier_func_reporting <- outlier_function_tib %>% 
    filter(outlier_avg_func == TRUE) %>% 
    select(prop) %>% 
    pull()

moe_prop_outlier_func_reporting <- binom.confint(
    x = n_outlier_func_reporting,
    n = total_articles,
    conf.level = 0.95,
    methods = "ac")

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
    mutate(prop = prop.table(n)) %>% 
    arrange(desc(n))
outlier_func_by_type

###### By type

n_breath_outlier_funcs <- outlier_func_by_type %>% 
    filter(outlier_avg_type == "breath") %>% 
    select(n) %>% 
    pull()

prop_breath_outlier_funcs <- outlier_func_by_type %>% 
    filter(outlier_avg_type == "breath") %>% 
    select(prop) %>% 
    pull()
prop_breath_outlier_funcs <- sprintf("%.1f", prop_breath_outlier_funcs * 100)

n_time_outlier_funcs <- outlier_func_by_type %>% 
    filter(outlier_avg_type == "time") %>% 
    select(n) %>% 
    pull()

prop_time_outlier_funcs <- outlier_func_by_type %>% 
    filter(outlier_avg_type == "time") %>% 
    select(prop) %>% 
    pull()
prop_time_outlier_funcs <- sprintf("%.1f", prop_time_outlier_funcs * 100)

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
    mutate(prop = prop.table(n)) %>% 
    arrange(outlier_avg_type, desc(n))
outlier_func_by_type_amount

# organize by type and THEN by frequency
# some kind of double line between breath and time methods so readers
# can differentiate those faster

outlier_func_by_type_amount

#$ calculate number and prop that did both limit and function but no table


###### 5 breath functions

n_5_breath_func <- outlier_func_by_type_amount %>% 
    filter(outlier_avg_amount == 5 & outlier_avg_type == "breath") %>% 
    select(n) %>% 
    pull()

prop_5_breath_func <- outlier_func_by_type_amount %>% 
    filter(outlier_avg_amount == 5 & outlier_avg_type == "breath") %>% 
    select(prop) %>% 
    pull()
prop_5_breath_func <- sprintf("%.1f", prop_5_breath_func * 100)
