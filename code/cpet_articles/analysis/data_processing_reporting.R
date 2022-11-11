# Analysis of how often papers report data processing procedures and what
# those procedures are

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

                                      

############### OUTLIERS #################

# count by outlier cutoff type
merge_df %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n())

outlier_reporting_frequency_plot <- merge_df %>% 
    count(outlier_limit) %>% 
    mutate(pct = round(prop.table(n),4)) %>% 
    mutate(outlier_limit = if_else(
        is.na(outlier_limit), "Unspecified", str_to_title(outlier_limit))) %>% 
    ggplot(aes(x = outlier_limit, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Outlier Limit") +
    ylab("Count") +
    ylim(0,8000) +
    theme_minimal() +
    labs(caption = "Outlier cutoff reporting frequency. Data are expressed as counts and percentages.\nN = 7833.") +
    theme(plot.caption = element_text(hjust=0))
outlier_reporting_frequency_plot

# pct outlier cutoff by type
merge_df %>% 
    select(outlier_limit) %>% 
    drop_na() %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    mutate(freq = n / sum(n) * 100)

pct_outlier_limits <- merge_df %>% 
    select(outlier_limit) %>% 
    drop_na() %>% 
    group_by(outlier_limit) %>% 
    summarize(n = n()) %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(outlier_limit = str_to_title(outlier_limit)) %>% 
    ggplot(aes(x = outlier_limit, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Outlier Limit") +
    ylab("Count") +
    ylim(0,200) +
    theme_minimal() +
    labs(caption = "Outlier cutoff frequencies. Data are expressed as counts and percentages.\nN = 330.") +
    theme(plot.caption = element_text(hjust=0))
pct_outlier_limits


# count of articles that specify outlier removal
merge_df %>% 
    select(outlier_limit) %>% 
    summarize_all(list(count_outlier_procedure_described = ~ sum(!is.na(.))))

# percentage of articles that specify outlier removal
merge_df %>% 
    select(outlier_limit) %>% 
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

# pct interpolation method by overall procedure (time + type)
merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    mutate(interpolation_details = 
               !is.na(interpolation_type) | !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    mutate(procedure = paste0(interpolation_type, "-", interpolation_time_s)) %>% 
    group_by(procedure) %>% 
    summarize(n = n()) %>% 
    mutate(freq = n / sum(n) * 100)

merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    mutate(interpolation_details = 
               !is.na(interpolation_type) | !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    mutate(procedure = paste0(interpolation_type, "-", interpolation_time_s)) %>% 
    group_by(procedure) %>% 
    summarize(n = n()) %>% 
    mutate(pct = n / sum(n)) %>% 
    ggplot(aes(x = procedure, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)),
              vjust = 0, hjust = -0.5, angle=90) +
    geom_text(aes(label = n), vjust = -0.5) +
    xlab("Interpolation Procedure") +
    ylab("Count") +
    ylim(0,325) +
    theme_minimal() +
    labs(caption = "Interpolation method by time and type. Data are expressed as counts and \npercentages. N = 472.") +
    theme(plot.caption = element_text(hjust=0)) +
    theme(axis.text.x = element_text(angle=90, hjust=1))

interpolation_reproting_frequency_plot <- merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    mutate(interpolation_details = 
               !is.na(interpolation_type) | !is.na(interpolation_time_s)) %>% 
    mutate(procedure = paste0(interpolation_type, "-", interpolation_time_s)) %>% 
    group_by(procedure) %>% 
    summarize(n = n()) %>% 
    mutate(pct = n / sum(n) * 100) %>% 
    mutate(type = case_when(procedure == "NA-NA" ~ "Unspecified",
                            procedure == "linear-1" ~ '1-second',
                            procedure == "NA-1" ~ "1-second")) %>% 
    mutate(type = if_else(is.na(type), "Other", type)) %>% 
    group_by(type) %>% 
    summarize(n = sum(n)) %>% 
    mutate(pct = n / sum(n)) %>% 
    ggplot(aes(x = type, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Interpolation Procedure") +
    ylab("Count") +
    ylim(0,8000) +
    theme_minimal() +
    labs(caption = "Interpolation method reporting frequencies. Data are expressed as counts and \npercentages. N = 7833.") +
    theme(plot.caption = element_text(hjust=0))
interpolation_reproting_frequency_plot

# pct interpolation method by time only
merge_df %>% 
    mutate(interpolation_details = !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    count()


merge_df %>% 
    mutate(interpolation_details = !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    group_by(interpolation_time_s) %>% 
    summarize(n = n()) %>% 
    mutate(pct = n / sum(n)) %>% 
    ggplot(aes(x = as.factor(interpolation_time_s), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Interpolation Time (s)") +
    ylab("Count") +
    ylim(0,500) +
    theme_minimal() +
    labs(caption = "Interpolation methods by time. Data are expressed as counts and percentages.\nN = 458") +
    theme(plot.caption = element_text(hjust=0))

# pct interpolation method by type only
merge_df %>% 
    mutate(interpolation_details = !is.na(interpolation_type)) %>% 
    filter(interpolation_details == TRUE) %>% 
    count()

merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    mutate(interpolation_details = !is.na(interpolation_type)) %>% 
    filter(interpolation_details == TRUE) %>% 
    group_by(interpolation_type) %>% 
    summarize(n = n()) %>% 
    mutate(pct = n / sum(n)) %>% 
    mutate(interpolation_type = str_to_title(interpolation_type)) %>% 
    ggplot(aes(x = as.factor(interpolation_type), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Interpolation Calculation Type") +
    ylab("Count") +
    ylim(0,250) +
    theme_minimal() +
    labs(caption = "Interpolation methods by type. Data are expressed as counts and percentages.\nN = 223.") +
    theme(plot.caption = element_text(hjust=0))
