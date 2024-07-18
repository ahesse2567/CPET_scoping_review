library(tidyverse)
library(stringr)
library(scales)
library(janitor)
# load fonts so Times works with ggplot2 + pdf rendering
extrafont::loadfonts(quiet = TRUE)
# theme_update(text = element_text(family = "Times"))

# re-find which articles are ineligible in case I forgot to update this manaully
source("code/cpet_articles/tidying/combine_ineligible_articles.R")

ineligible_articles <- read_csv(
    "data/cpet_articles/text_analysis/ineligible_articles_combined.csv",
    show_col_types = FALSE) %>% 
    clean_names()

# load_bbb articles, removing potential douglas bag or mixing chamber articles
bbb_articles <- read_csv("data/cpet_articles/text_analysis/all_bbb_articles.csv",
                         show_col_types = FALSE) %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    filter(!(doi_suffix %in% ineligible_articles$doi_suffix))

interpolation_data <- read_csv("data/cpet_articles/text_analysis/Interpolation - Interpolation.csv",
                               show_col_types = FALSE) %>% 
    clean_names()

interpolation_df <- full_join(bbb_articles, interpolation_data, by = "doi_suffix") %>% 
    select(colnames(interpolation_data)) %>% 
    filter(doi_suffix %in% bbb_articles$doi_suffix)


############### INTERPOLATION #################

total_articles <- interpolation_df %>% 
    distinct(doi_suffix, .keep_all = FALSE) %>% 
    nrow()

######## how many did or did not specify interpolation
interpolation_specification_summary <- interpolation_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    summarise(across(everything(), .fns = ~!is.na(.))) %>% 
    mutate(interpolation_details = interpolation_type | interpolation_time_s) %>% 
    count(interpolation_details) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n))
interpolation_specification_summary

count_specified_interpolation <- interpolation_specification_summary %>% 
    filter(interpolation_details == TRUE) %>% 
    select(n) %>% 
    pull()

prop_specified_interpolation <- interpolation_specification_summary %>% 
    filter(interpolation_details == TRUE) %>% 
    select(prop) %>% 
    pull()

# calc MOE for number reporting interpolation details
z <- qnorm(0.025, lower.tail = FALSE)
moe_prop_articles_reporting_interpolation <-
    z * sqrt((prop_specified_interpolation * (1 - prop_specified_interpolation)) / total_articles)


####### Interpolation by procedure

interpolation_by_specified_procedure <- interpolation_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    mutate(interpolation_details = 
               !is.na(interpolation_type) | !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    count(interpolation_type, interpolation_time_s) %>% 
    mutate(procedure = paste0(interpolation_type, "-", interpolation_time_s),
           prop = prop.table(n)) %>% 
    relocate(procedure, .after = interpolation_time_s) %>% 
    arrange(desc(n))
interpolation_by_specified_procedure


###### Most popular interpolation by time

most_popular_interpolation_time <- interpolation_by_specified_procedure %>% 
    group_by(interpolation_time_s) %>% 
    summarize(n = sum(n)) %>% 
    filter(n == max(n)) %>% 
    select(interpolation_time_s) %>% 
    pull()

n_most_popular_interpolation_time <- interpolation_by_specified_procedure %>% 
    group_by(interpolation_time_s) %>% 
    summarize(n = sum(n)) %>% 
    filter(n == max(n)) %>% 
    select(n) %>% 
    pull()

prop_most_popular_interpolation_time <- interpolation_by_specified_procedure %>% 
    group_by(interpolation_time_s) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    # filter out NAs as these correspond to UNreported interpolation times 
    # (although there were other details reported about interpolation for these
    # articles
    filter(!is.na(interpolation_time_s)) %>% 
    mutate(prop = prop.table(n)) %>% 
    filter(n == max(n)) %>% 
    select(prop) %>% 
    pull()


##### Most popular interpolation by method

n_most_popular_interpolation_method <- interpolation_by_specified_procedure %>% 
    group_by(interpolation_type) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>%
    mutate(prop = prop.table(n)) %>% 
    filter(n == max(n)) %>% 
    select(n) %>% 
    pull()
n_most_popular_interpolation_method

prop_most_popular_interpolation_method <- interpolation_by_specified_procedure %>% 
    group_by(interpolation_type) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>%
    mutate(prop = prop.table(n)) %>% 
    filter(n == max(n)) %>% 
    select(prop) %>% 
    pull()
prop_most_popular_interpolation_method

most_popular_stated_interpolation_method <- 
    interpolation_by_specified_procedure %>% 
    group_by(interpolation_type) %>% 
    filter(!is.na(interpolation_type)) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>%
    mutate(prop = prop.table(n)) %>% 
    filter(n == max(n)) %>% 
    select(interpolation_type) %>% 
    pull()
most_popular_stated_interpolation_method

n_most_popular_stated_interpolation_method <- interpolation_by_specified_procedure %>% 
    group_by(interpolation_type) %>% 
    filter(!is.na(interpolation_type)) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>%
    mutate(prop = prop.table(n)) %>% 
    filter(n == max(n)) %>% 
    select(n) %>% 
    pull()
n_most_popular_stated_interpolation_method

prop_most_popular_stated_interpolation_method <- interpolation_by_specified_procedure %>% 
    # filter out unspecified interpolation procedures/types
    filter(!is.na(interpolation_type)) %>% 
    group_by(interpolation_type) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>%
    mutate(prop = prop.table(n)) %>% 
    filter(n == max(n)) %>% 
    select(prop) %>% 
    pull()
prop_most_popular_stated_interpolation_method



##### Condensing interpolation results

condensed_interpolation_summary <- interpolation_df %>% 
    select(interpolation_type, interpolation_time_s) %>% 
    mutate(interpolation_details = 
               !is.na(interpolation_type) | !is.na(interpolation_time_s)) %>% 
    mutate(procedure = paste0(interpolation_type, "-", interpolation_time_s)) %>% 
    group_by(procedure) %>% 
    summarize(n = n()) %>% 
    mutate(prop = n / sum(n) * 100) %>% 
    mutate(type = case_when(procedure == "NA-NA" ~ "Unspecified",
                            procedure == "linear-1" ~ '1-second',
                            procedure == "NA-1" ~ "1-second")) %>% 
    mutate(type = if_else(is.na(type), "Other", type)) %>% 
    group_by(type) %>% 
    summarize(n = sum(n)) %>% 
    mutate(prop = n / sum(n)) %>% 
    arrange(desc(n))
condensed_interpolation_summary

interpolation_reporting_frequency_plot <- condensed_interpolation_summary %>% 
    ggplot(aes(x = type, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)),
              # family = "Times",
              vjust = -0.5) +
    geom_text(aes(label = n),
              # family = "Times", 
              vjust = -2) +
    xlab("Interpolation Procedure") +
    ylab("Count") +
    ylim(0, plyr::round_any(max(condensed_interpolation_summary$n),
                            3000, f = ceiling)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Interpolation method reporting frequencies. 
    #           Data are expressed as counts and percentages. N = ",
    #           total_articles, ".", sep = ""), width = 100)) +
    theme(plot.caption = element_text(hjust=0)) +
    theme(text=element_text(
        # family="Times", 
                            size=12))
interpolation_reporting_frequency_plot

label_size <- 10
caption_size <- 20
axes_text_size <- 25

interpolation_reporting_frequency_plot_ACSM <- 
    condensed_interpolation_summary %>% 
    ggplot(aes(x = type, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)),
              family = "Times", vjust = -0.5, size = label_size) +
    geom_text(aes(label = n),
              family = "Times", vjust = -2, size = label_size) +
    xlab("Interpolation Procedure") +
    ylab("Count") +
    ylim(0, plyr::round_any(max(condensed_interpolation_summary$n),
                            3000, f = ceiling)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Interpolation method reporting frequencies. 
    #           Data are expressed as counts and percentages. N = ",
    #           total_articles, ".", sep = ""), width = 100)) +
    labs(caption = "Counts and percentages of articles reporting interpolation\nmethods and their types") +
    theme(plot.caption = element_text(hjust=0)) +
    theme(text=element_text(family="Times", size=12),
          axis.text.x = element_text(size = axes_text_size),
          axis.text.y = element_text(size = axes_text_size),
          axis.title = element_text(size = axes_text_size),
          plot.caption = element_text(size = caption_size,
                                      hjust = 0))
interpolation_reporting_frequency_plot_ACSM

ggsave("graphics/interpolation_reporting_frequency_plot_ACSM.tiff",
       interpolation_reporting_frequency_plot_ACSM,
       width = 8.666667,
       height = 8.5,
       units = "in",
       bg = "white")

interpolation_by_time_tib <- interpolation_df %>% 
    select(interpolation_time_s) %>% 
    filter(!is.na(interpolation_time_s)) %>% 
    count(interpolation_time_s) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    arrange(desc(n))
interpolation_by_time_tib

interpolation_by_type_tib <- interpolation_df %>% 
    select(interpolation_type) %>% 
    filter(!is.na(interpolation_type)) %>% 
    count(interpolation_type) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n),
           interpolation_type = str_to_title(interpolation_type)) %>% 
    arrange(desc(n))
interpolation_by_type_tib

condensed_interpolation_by_specified_procedure <-
    interpolation_by_specified_procedure %>% 
    mutate(condensed_procedure = case_when(interpolation_time_s == 1 ~ procedure,
                                           interpolation_time_s == 5 ~ "Other-5"),
           condensed_procedure = if_else(is.na(condensed_procedure),
                                         "other",
                                         condensed_procedure),
           condensed_procedure = str_to_title(condensed_procedure),
           condensed_procedure = if_else(
               str_to_lower(condensed_procedure) == "na-1",
               "Unspecified-1", condensed_procedure)) %>% 
    group_by(condensed_procedure) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    arrange((desc(n)))
condensed_interpolation_by_specified_procedure

condensed_interpolation_by_specified_procedure_plot <-
    condensed_interpolation_by_specified_procedure %>% 
    ggplot(aes(x = condensed_procedure, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)),
              # family = "Times", 
              vjust = -0.5) +
    geom_text(aes(label = n), 
              # family = "Times",
              vjust = -2) +
    xlab("Interpolation Procedure") +
    ylab("Count") +
    ylim(0, 175 * ceiling(max(interpolation_by_specified_procedure$n) / 175)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste(
    #         "Interpolation method by time and type. Data are expressed as counts and \npercentages. N = ",
    #         count_specified_interpolation, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    theme(axis.text.x = element_text(angle=90, hjust=1)) +
    theme(text=element_text(
        # family="Times", 
                            size=12))
condensed_interpolation_by_specified_procedure_plot
ggsave(
    here::here("graphics/condensed_interpolation_by_specified_procedure_plot.jpg"),
    condensed_interpolation_by_specified_procedure_plot)


condensed_interpolation_by_specified_procedure_plot_ACSM <-
    condensed_interpolation_by_specified_procedure %>% 
    ggplot(aes(x = condensed_procedure, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)),
              family = "Times", vjust = -0.5, size = label_size) +
    geom_text(aes(label = n), family = "Times", vjust = -2,
              size = label_size) +
    xlab("Interpolation Procedure") +
    ylab("Count") +
    ylim(0, 175 * ceiling(max(interpolation_by_specified_procedure$n) / 175)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste(
    #         "Interpolation method by time and type. Data are expressed as counts and \npercentages. N = ",
    #         count_specified_interpolation, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    labs(
        caption = "Counts and percentages of reported interpolation type and time.") +
    theme(axis.text.x = element_text(angle=90, hjust=1)) +
    theme(text=element_text(family="Times", size=12),
          axis.text.x = element_text(size = axes_text_size),
          axis.text.y = element_text(size = axes_text_size),
          axis.title = element_text(size = axes_text_size),
          plot.caption = element_text(size = caption_size,
                                      hjust = 0))
condensed_interpolation_by_specified_procedure_plot_ACSM

ggsave("graphics/condensed_interpolation_by_specified_procedure_plot_ACSM.tiff",
       condensed_interpolation_by_specified_procedure_plot_ACSM,
       width = 8.666667,
       height = 8.5,
       units = "in",
       bg = "white")

# prop interpolation method by time only
interpolation_df %>% 
    mutate(interpolation_details = !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    count() %>% pull()

interpolation_df %>% 
    mutate(interpolation_details = !is.na(interpolation_time_s)) %>% 
    filter(interpolation_details == TRUE) %>% 
    count() %>% pull()


condensed_interpolation_times <- interpolation_by_specified_procedure %>% 
    select(interpolation_time_s, n, prop) %>% 
    filter(!is.na(interpolation_time_s)) %>% 
    mutate(interpolation_time_s = if_else(
        interpolation_time_s %in% c("1", "5"),
        interpolation_time_s,
        "other"),
        interpolation_time_s = str_to_title(interpolation_time_s)) %>% 
    group_by(interpolation_time_s) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n))

interpolation_by_time_plot <- condensed_interpolation_times %>% 
    ggplot(aes(x = as.factor(interpolation_time_s), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Interpolation Time (s)") +
    ylab("Count") +
    ylim(0,100 * ceiling(max(condensed_interpolation_times$n) / 100)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Interpolation methods by time. Data are expressed as counts and percentages. N = ",
    #           sum(condensed_interpolation_times$n), ".", sep = ""), width = 100)) +
    theme(plot.caption = element_text(hjust=0))
interpolation_by_time_plot # write this in text

interpolation_by_time_plot_ACSM <- condensed_interpolation_times %>% 
    ggplot(aes(x = as.factor(interpolation_time_s), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)), family = "Times", 
              vjust = -0.5, size = label_size) +
    geom_text(aes(label = n), vjust = -2, family = "Times", size = label_size) +
    xlab("Interpolation Time (s)") +
    ylab("Count") +
    ylim(0,100 * ceiling(max(condensed_interpolation_times$n) / 100)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Interpolation methods by time. Data are expressed as counts and percentages. N = ",
    #           sum(condensed_interpolation_times$n), ".", sep = ""), width = 100)) +
    labs(caption = "Reported interpolation time in seconds") +
    theme(text=element_text(family="Times", size=12),
          axis.text.x = element_text(size = axes_text_size),
          axis.text.y = element_text(size = axes_text_size),
          axis.title = element_text(size = axes_text_size),
          plot.caption = element_text(size = caption_size,
                                      hjust = 0))
interpolation_by_time_plot_ACSM # write this in text

ggsave("graphics/interpolation_by_time_plot_ACSM.tiff",
       interpolation_by_time_plot_ACSM,
       width = 8.666667,
       height = 8.5,
       units = "in",
       bg = "white")

condensed_interpolation_types <-
    interpolation_by_specified_procedure %>% 
    select(interpolation_type, n, prop) %>% 
    # filter out NA as these are unreported interpolation types
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
    mutate(prop = prop.table(n))
condensed_interpolation_types

condensed_interpolation_types_plot <- condensed_interpolation_types %>% 
    ggplot(aes(x = as.factor(interpolation_type), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Interpolation Calculation Type") +
    ylab("Count") +
    ylim(0, plyr::round_any(max(condensed_interpolation_types$n), 50, f = ceiling)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Interpolation methods by type. Data are expressed as counts and percentages. N = ",
    #     sum(condensed_interpolation_types$n), ".", sep = ""), width = 100)) +
    theme(plot.caption = element_text(hjust=0))
condensed_interpolation_types_plot # just write in text instead
