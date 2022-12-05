library(tidyverse)
library(stringr)
library(scales)
library(janitor)

text_data <- read_csv("data/cpet_articles/text_analysis/Manual text analysis - Data.csv",
                      show_col_types = FALSE) %>% 
    clean_names()

douglas_bag_mixing_chamber_articles <- read_csv(
    "data/cpet_articles/text_analysis/Manual text analysis - DB or MC.csv",
    show_col_types = FALSE) %>% 
    clean_names()

# load_bbb articles, removing potential douglas bag or mixing chamber articles
bbb_articles <- read_csv("data/cpet_articles/text_analysis/bbb_articles.csv",
                         show_col_types = FALSE) %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    filter(!(doi_suffix %in% douglas_bag_mixing_chamber_articles$doi_suffix))

merge_df <- inner_join(text_data, bbb_articles, by = "doi_suffix") %>% 
    select(colnames(text_data))
                                      
############### INTERPOLATION #################

total_articles <- merge_df %>% 
    distinct(doi_suffix, .keep_all = FALSE) %>% 
    nrow()

interpolation_specification_summary <- merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    summarise(across(everything(), .fns = ~!is.na(.))) %>% 
    mutate(interpolation_details = interpolation_type | interpolation_time_s) %>% 
    count(interpolation_details) %>% 
    ungroup() %>% 
    mutate(freq = prop.table(n))
interpolation_specification_summary

count_specified_interpolation <- interpolation_specification_summary %>% 
    filter(interpolation_details == TRUE) %>% 
    select(n) %>% 
    pull()

pct_specified_interpolation <- interpolation_specification_summary %>% 
    filter(interpolation_details == TRUE) %>% 
    select(freq) %>% 
    pull()

interpolation_by_specified_procedure <- merge_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    mutate(interpolation_details = 
               !is.na(interpolation_type) | !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    count(interpolation_type, interpolation_time_s) %>% 
    mutate(procedure = paste0(interpolation_type, "-", interpolation_time_s),
           pct = prop.table(n)) %>% 
    relocate(procedure, .after = interpolation_time_s) %>% 
    arrange(desc(n))
interpolation_by_specified_procedure

condensed_interpolation_summary <- merge_df %>% 
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
    arrange(desc(n))
condensed_interpolation_summary

interpolation_reproting_frequency_plot <- condensed_interpolation_summary %>% 
    ggplot(aes(x = type, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Interpolation Procedure") +
    ylab("Count") +
    ylim(0, 2000 * ceiling(max(condensed_interpolation_summary$n) / 2000)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Interpolation method reporting frequencies. 
    #           Data are expressed as counts and percentages. N = ",
    #           total_articles, ".", sep = ""), width = 100)) +
    theme(plot.caption = element_text(hjust=0))
interpolation_reproting_frequency_plot


merge_df %>% 
    select(interpolation_time_s) %>% 
    filter(!is.na(interpolation_time_s)) %>% 
    count(interpolation_time_s) %>% 
    arrange(desc(n))

merge_df %>% 
    select(interpolation_type) %>% 
    filter(!is.na(interpolation_type)) %>% 
    count(interpolation_type) %>% 
    arrange(desc(n))

condensed_interpolation_by_specified_procedure <-
    interpolation_by_specified_procedure %>% 
    mutate(condensed_procedure = case_when(interpolation_time_s == 1 ~ procedure,
                                           interpolation_time_s == 5 ~ "5-second"),
           condensed_procedure = if_else(is.na(condensed_procedure),
                                         "other",
                                         condensed_procedure),
           condensed_procedure = str_to_title(condensed_procedure)) %>% 
    group_by(condensed_procedure) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n))
condensed_interpolation_by_specified_procedure

condensed_interpolation_by_specified_procedure_plot <-
    condensed_interpolation_by_specified_procedure %>% 
    ggplot(aes(x = condensed_procedure, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)),
              vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Interpolation Procedure") +
    ylab("Count") +
    ylim(0, 150 * ceiling(max(interpolation_by_specified_procedure$n) / 150)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste(
    #         "Interpolation method by time and type. Data are expressed as counts and \npercentages. N = ",
    #         count_specified_interpolation, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    theme(axis.text.x = element_text(angle=90, hjust=1))
condensed_interpolation_by_specified_procedure_plot


# pct interpolation method by time only
merge_df %>% 
    mutate(interpolation_details = !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    count() %>% pull()

condensed_interpolation_times <- interpolation_by_specified_procedure %>% 
    select(interpolation_time_s, n, pct) %>% 
    filter(!is.na(interpolation_time_s)) %>% 
    mutate(interpolation_time_s = case_when(
        interpolation_time_s == 1 ~ 1,
        interpolation_time_s == 5 ~ 5),
        interpolation_time_s = if_else(
        is.na(interpolation_time_s),
        "other",
        as.character(interpolation_time_s)),
        interpolation_time_s = str_to_title(interpolation_time_s)) %>% 
    group_by(interpolation_time_s) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n))
condensed_interpolation_times

interpolation_by_time_plot <- condensed_interpolation_times %>% 
    ggplot(aes(x = as.factor(interpolation_time_s), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Interpolation Time (s)") +
    ylab("Count") +
    ylim(0,100 * ceiling(max(condensed_interpolation_times$n) / 100)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Interpolation methods by time. Data are expressed as counts and percentages. N = ",
    #           sum(condensed_interpolation_times$n), ".", sep = ""), width = 100)) +
    theme(plot.caption = element_text(hjust=0))
interpolation_by_time_plot

condensed_interpolation_types <-
    interpolation_by_specified_procedure %>% 
    select(interpolation_type, n, pct) %>% 
    filter(!is.na(interpolation_type)) %>% 
    mutate(interpolation_type = case_when(
        interpolation_type == "linear" ~ interpolation_type,
        interpolation_type == "cubic" ~ interpolation_type),
        interpolation_type = if_else(
            is.na(interpolation_type),
            "other",
            interpolation_type),
        interpolation_type = str_to_title(interpolation_type)) %>% 
    group_by(interpolation_type) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n))
condensed_interpolation_types

condensed_interpolation_types_plot <- condensed_interpolation_types %>% 
    ggplot(aes(x = as.factor(interpolation_type), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Interpolation Calculation Type") +
    ylab("Count") +
    ylim(0, plyr::round_any(max(condensed_interpolation_types$n), 50, f = ceiling)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Interpolation methods by type. Data are expressed as counts and percentages. N = ",
    #     sum(condensed_interpolation_types$n), ".", sep = ""), width = 100)) +
    theme(plot.caption = element_text(hjust=0))
condensed_interpolation_types_plot
