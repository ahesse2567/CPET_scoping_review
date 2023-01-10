library(tidyverse)
library(stringr)
library(scales)
library(janitor)

ineligible_articles <- read_csv("data/cpet_articles/text_analysis/combined_ineligible_articles.csv") %>% 
    clean_names()

# load_bbb articles, removing potential douglas bag or mixing chamber articles
bbb_articles <- read_csv("data/cpet_articles/text_analysis/all_bbb_articles.csv",
         show_col_types = FALSE) %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    filter(!(doi_suffix %in% ineligible_articles$doi_suffix))

avg_data <- read_csv(
    "data/cpet_articles/text_analysis/Averaging - Rand Avg.csv",
                     show_col_types = FALSE) %>% 
    clean_names()

merge_df <- full_join(avg_data, bbb_articles, by = "doi_suffix") %>% 
    select(colnames(avg_data)) %>% 
    filter(doi_suffix %in% avg_data$doi_suffix)

######## Averaging methods #################

total_articles <- merge_df %>% 
    distinct(doi_suffix, .keep_all = FALSE) %>% 
    nrow()

pct_reporting_avg_methods <- merge_df %>% 
    count(no_avg_details) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    filter(no_avg_details == FALSE) %>% 
    select(prop) %>% 
    pull()

z <- qnorm(0.025, lower.tail = FALSE)

margin_of_error <- z * sqrt(
    pct_reporting_avg_methods * (1 - pct_reporting_avg_methods) / 
        total_articles) * 100
margin_of_error

#### Averaging method types



# count by averaging type
n_avg <- merge_df %>% 
    filter(!is.na(avg_type)) %>% 
    nrow()

avg_by_type_tab <- merge_df %>% 
    filter(!is.na(avg_type)) %>% 
    count(avg_type) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_type = str_to_title(avg_type))
avg_by_type_tab






# avg by subtype count
n_avg_subtype <- merge_df %>% 
    filter(!is.na(avg_subtype)) %>% 
    nrow()

avg_by_subtype_tab <- merge_df %>% 
    filter(!is.na(avg_subtype)) %>% 
    count(avg_subtype) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_subtype = str_to_title(avg_subtype))
avg_by_subtype_tab




# avg by type and subtype
avg_by_type_subtype_tab <- merge_df %>% 
    filter(!is.na(avg_subtype) | !is.na(avg_type)) %>% 
    count(avg_type, avg_subtype) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_type_subtype = paste(avg_type, "-", avg_subtype, sep = ""),
           avg_type_subtype = str_to_title(avg_type_subtype)) %>% 
    arrange(desc(pct))
avg_by_type_subtype_tab



# avg by full avg method
avg_by_full_method_tab <- merge_df %>% 
    filter(!is.na(avg_type)) %>% 
    group_by(avg_type, avg_subtype, avg_amount, avg_mos, avg_mean_type) %>% 
    summarize(n = n()) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    arrange(desc(n))
avg_by_full_method_tab
View(avg_by_full_method_tab)
