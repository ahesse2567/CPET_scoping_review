library(tidyverse)
library(stringr)
library(scales)

text_data <- read_csv("data/cpet_articles/text_analysis/Manual text analysis - Avg.csv",
                      show_col_types = FALSE) %>% 
    janitor::clean_names()

douglas_bag_mixing_chamber_articles <- read_csv(
    "data/cpet_articles/text_analysis/Manual text analysis - DB or MC.csv",
    show_col_types = FALSE)

# load_bbb articles, removing potential douglas bag or mixing chamber articles
bbb_articles <- read_csv("data/cpet_articles/text_analysis/bbb_articles.csv",
         show_col_types = FALSE) %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    filter(!(doi_suffix %in% douglas_bag_mixing_chamber_articles$doi_suffix))

merge_df <- inner_join(text_data, bbb_articles, by = "doi_suffix") %>% 
    select(colnames(text_data)) %>% 
    rowwise() %>%
    mutate(all_NA = all(is.na(
        c(avg_type, avg_subtype, avg_amount,
          avg_mos, avg_mean_type)
    ))) %>% 
    filter(!is.na(avg_text) | all_NA == FALSE) # there are a few articles
# that excaped my regex. However, I still found that they had averaging methods
# when reading them manually.

######## Averaging methods #################

total_articles <- merge_df %>% 
    distinct(doi_suffix, .keep_all = FALSE) %>% 
    nrow()

# initial estimate of how many articles have averaging methods
# only considering if they have avg details or not

merge_df %>%
    distinct(doi_suffix, .keep_all = TRUE) %>%
    mutate(has_avg_details = case_when(
            avg_text == FALSE ~ FALSE,
            avg_text != FALSE & !is.na(avg_text) ~ TRUE,
            is.na(avg_text) & all_NA == FALSE ~ TRUE)) %>%
    count(has_avg_details) %>%
    ungroup() %>%
    mutate(prop = prop.table(n))
# so about 70% have averaging method details of some kind. This percentage will
# drop because not all avg_text actually indicates avg_methods

documented_details_tab <- merge_df %>% 
    filter(documented == TRUE | done == TRUE | all_NA == FALSE)  %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    count(all_NA) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n))
documented_details_tab

# unique articles WITH averaging details
documented_has_avg_details <- documented_details_tab %>% 
    filter(all_NA == FALSE) %>% 
    select(n) %>% 
    pull()

# unique articles WITHOUT averaging details
documented_no_avg_details <- documented_details_tab %>% 
    filter(all_NA == TRUE) %>% 
    select(n) %>% 
    pull()

total_documented <- documented_has_avg_details + documented_no_avg_details

pct_documented_no_avg_details <- documented_details_tab %>% 
    filter(all_NA == TRUE) %>% 
    select(prop) %>% 
    pull()

documented_doi_suffixes <- merge_df %>% 
    filter(documented == TRUE | done == TRUE | all_NA == FALSE)  %>% 
    distinct(doi_suffix) %>% 
    pull()

undocumented_doi_suffixes <- merge_df %>%
    filter(!(doi_suffix %in% documented_doi_suffixes)) %>% 
    distinct(doi_suffix) %>% 
    pull()

total_undocumented <- total_articles - total_documented


count_undocumented_no_avg_text <- merge_df %>%
    filter(doi_suffix %in% undocumented_doi_suffixes) %>% 
    filter(avg_text == FALSE) %>%
    nrow()

count_undocumented_with_avg_text <- merge_df %>% 
    filter(doi_suffix %in% undocumented_doi_suffixes) %>% 
    filter(avg_text != FALSE) %>% 
    nrow()

est_count_undocumented_with_avg_text_no_avg_method <- 
    round(count_undocumented_with_avg_text * pct_documented_no_avg_details,0)

est_total_undoc_no_avg_text <- 
    count_undocumented_no_avg_text + est_count_undocumented_with_avg_text_no_avg_method

est_total_undoc_with_avg_text <- 
    round(count_undocumented_with_avg_text * (1 - pct_documented_no_avg_details),0)

documented_has_avg_details + documented_no_avg_details + 
    est_total_undoc_no_avg_text + est_total_undoc_with_avg_text ==
    total_articles

est_total_with_avg_details <- 
    documented_has_avg_details + est_total_undoc_with_avg_text

est_total_no_avg_details <- 
    documented_no_avg_details + est_total_undoc_no_avg_text

avg_documentation_tib <- tibble(
    has_avg_documentation = c(TRUE, FALSE),
    estimate = c(est_total_with_avg_details,
                 est_total_no_avg_details)) %>%
    mutate(prop = prop.table(estimate),
           documentation = if_else(has_avg_documentation == TRUE,
                                   "Describes Averaging Methods",
                                   "Does NOT Describe Averaging Methods"))
avg_documentation_tib

ggplot(data = avg_documentation_tib) +
    geom_col(aes(x = documentation, y = estimate)) +
    xlab("Averaging Method Documentation") +
    ylab("Count")

# number of documents w/o any averaging text
with_avg_text <- merge_df %>% 
    filter(avg_text != FALSE) %>% 
    nrow()

avg_text_no_documentation_est <- round(with_avg_text * pct_documented_no_avg_details, 0)

# total - has avg_text + estimate with text but w/o documentation = num undocumented
nrow(merge_df) - with_avg_text + avg_text_no_documentation_est


# count by averaging type
n_avg <- merge_df %>% 
    filter(!is.na(avg_type)) %>% 
    nrow()

# avg by type plot
merge_df %>% 
    filter(!is.na(avg_type)) %>% 
    count(avg_type) %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_type = str_to_title(avg_type)) %>% 
    ggplot(aes(x = avg_type, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Averaging Method Type") +
    ylab("Count") +
    ylim(0,600) +
    theme_minimal() +
    labs(caption = "Averaging method by type. Data are expressed as counts and percentages.\nN = 541.") +
    theme(plot.caption = element_text(hjust=0)) +
    theme(axis.text.x = element_text(angle=45, hjust=1))

# avg by subtype count
n_avg_subtype <- merge_df %>% 
    filter(!is.na(avg_subtype)) %>% 
    nrow()

# avg by subtype plot
merge_df %>% 
    filter(!is.na(avg_subtype)) %>% 
    count(avg_subtype) %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_subtype = str_to_title(avg_subtype)) %>% 
    ggplot(aes(x = avg_subtype, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Averaging Method Subtype") +
    ylab("Count") +
    ylim(0,600) +
    theme_minimal() +
    labs(caption = "Averaging method by subtype. Data are expressed as counts and percentages.\nN = 537") +
    theme(plot.caption = element_text(hjust=0)) +
    theme(axis.text.x = element_text(angle=45, hjust=1))


# avg by full avg method plot

merge_df %>% 
    filter(!is.na(avg_type)) %>% 
    group_by(avg_type, avg_subtype, avg_amount, avg_mos, avg_mean_type) %>% 
    summarize(n = n()) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_procedure = paste(
        avg_type, avg_subtype, avg_amount, avg_mos, avg_mean_type, sep = "-"),
        avg_procedure = if_else(n < 3, "Other", str_to_title(avg_procedure))) %>% 
    group_by(avg_procedure) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_procedure = str_remove(avg_procedure, "-Whole")) %>% 
    ggplot(aes(x = reorder(avg_procedure, -n), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Averaging Procedure") +
    ylab("Count") +
    ylim(0,250) +
    theme_minimal() +
    labs(caption = "Averaging method by full procedure. Data are expressed as counts and percentages. N = 541") +
    theme(plot.caption = element_text(hjust=0)) +
    theme(axis.text.x = element_text(angle=90, hjust=1))


merge_df %>% 
    select(avg_text) %>% 
    mutate(reports_avg = if_else(avg_text == FALSE, FALSE, TRUE)) %>% 
    group_by(reports_avg) %>% 
    summarize(n = n()) %>% 
    drop_na() %>% 
    mutate(pct = prop.table(n)*100)
