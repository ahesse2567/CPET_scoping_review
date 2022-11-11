library(tidyverse)
library(stringr)
library(scales)


text_data <- read_csv("data/cpet_articles/text_analysis/Manual text analysis - Data.csv",
                      show_col_types = FALSE)

bbb_articles <- read_csv("data/cpet_articles/text_analysis/bbb_articles.csv",
                         show_col_types = FALSE)

merge_df <- inner_join(text_data, bbb_articles, by = "doi_suffix") %>% 
    janitor::clean_names() %>% 
    mutate(outlier_limit = str_remove(outlier_limit, "(?<=SD).*"))

######## Averaging methods #################

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
