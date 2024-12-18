library(tidyverse)
library(stringr)
library(scales)
library(janitor)
library(binom)
extrafont::loadfonts(quiet=TRUE)
# theme_update(text = element_text(family = "Times"))

source("code/cpet_articles/tidying/combine_ineligible_articles.R")

ineligible_articles <- read_csv(
    "data/cpet_articles/text_analysis/ineligible_articles_combined.csv",
    show_col_types = FALSE) %>% 
    clean_names()

# load_bbb articles, removing potential douglas bag or mixing chamber articles
# bbb_articles <- read_csv("data/cpet_articles/text_analysis/all_bbb_articles.csv",
#          show_col_types = FALSE) %>% 
#     distinct(doi_suffix, .keep_all = TRUE) %>% 
#     filter(!(doi_suffix %in% ineligible_articles$doi_suffix))

# load_bbb articles, removing potential douglas bag or mixing chamber articles
bbb_articles <- read_csv("data/cpet_articles/text_analysis/bbb_articles.csv",
                         show_col_types = FALSE) %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    filter(!(doi_suffix %in% ineligible_articles$doi_suffix))

avg_data <- read_csv(
    "data/cpet_articles/text_analysis/Averaging - Rand Avg.csv",
                     show_col_types = FALSE) %>% 
    clean_names()

avg_df <- full_join(avg_data, bbb_articles, by = "doi_suffix") %>% 
    select(colnames(avg_data)) %>% 
    filter(doi_suffix %in% avg_data$doi_suffix)

######## Averaging methods #################

n_total_articles_avg <- avg_df %>% 
    distinct(doi_suffix, .keep_all = FALSE) %>% 
    nrow()

yn_avg_methods <- avg_df %>% 
    group_by(doi_suffix) %>% 
    summarize(avg_details = if_else(sum(!no_avg_details) > 0, TRUE, FALSE)) %>% 
    count(avg_details) %>% 
    mutate(prop = prop.table(n))

n_reporting_avg_methods <- yn_avg_methods %>% 
    filter(avg_details) %>% 
    select(n) %>% 
    pull()

multiple_avg_methods <- avg_df %>% 
    group_by(doi_suffix) %>% 
    summarize(n_avg_methods = sum(!no_avg_details)) %>% 
    count(n_avg_methods) %>% 
    mutate(multiple_methods = if_else(n_avg_methods > 1, TRUE, FALSE)) %>% 
    summarize(count_multiple_methods = sum(n), 
              .by = multiple_methods)

prop_multiple_methods <- multiple_avg_methods %>% 
    mutate(prop = prop.table(count_multiple_methods)) %>% 
    filter(multiple_methods) %>% 
    select(prop) %>% 
    pull()

# z <- qnorm(0.025, lower.tail = FALSE)
# z * sqrt(
# prop_reporting_avg_methods * (1 - prop_reporting_avg_methods) / 
# n_total_articles_avg)

moe_avg_reporting <- binom.confint(
    x = n_reporting_avg_methods,
    n = n_total_articles_avg,
    conf.level = 0.95,
    methods = "ac")

moe_avg_reporting

#### Averaging method types


# count by averaging type
n_avg <- avg_df %>% 
    filter(!is.na(avg_type)) %>% 
    nrow()

avg_by_type_tab <- avg_df %>% 
    filter(!is.na(avg_type)) %>% 
    count(avg_type) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    mutate(avg_type = str_to_title(avg_type)) %>% 
    arrange(desc(n))
avg_by_type_tab


# avg by subtype count
n_avg_subtype <- avg_df %>% 
    filter(!is.na(avg_subtype)) %>% 
    nrow()

avg_by_subtype_tab <- avg_df %>% 
    filter(!is.na(avg_subtype)) %>% 
    count(avg_subtype) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    mutate(avg_subtype = str_to_title(avg_subtype)) %>% 
    arrange(desc(n))
avg_by_subtype_tab




# avg by type and subtype
avg_by_type_subtype_tab <- avg_df %>% 
    filter(!is.na(avg_subtype) | !is.na(avg_type)) %>% 
    count(avg_type, avg_subtype) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    mutate(avg_type_subtype = paste(avg_type, "-", avg_subtype, sep = ""),
           avg_type_subtype = str_to_title(avg_type_subtype)) %>% 
    arrange(desc(prop))
avg_by_type_subtype_tab # this is an appendix kinda deal



# avg by full avg method
avg_by_full_method_tab <- avg_df %>% 
    filter(!is.na(avg_type)) %>% 
    group_by(avg_type, avg_subtype, avg_amount, avg_mos, avg_mean_type) %>% 
    summarize(n = n()) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    arrange(desc(n))
avg_by_full_method_tab
# View(avg_by_full_method_tab)


avg_by_full_method_plot <- avg_by_full_method_tab %>% 
    mutate(avg_procedure = paste(
        avg_type, avg_subtype, avg_amount, avg_mos, avg_mean_type, sep = "-"),
        avg_procedure = if_else(prop < 0.01, "Other", str_to_title(avg_procedure))) %>% 
    group_by(avg_procedure) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    mutate(avg_procedure = str_remove(avg_procedure, "-Mean-Whole"),
           avg_procedure = str_remove_all(avg_procedure, "-Na")) %>% 
    ggplot(aes(x = reorder(avg_procedure, -n), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop, accuracy = 0.1)), 
              # family = "Times", 
              vjust = -0.5) +
    geom_text(aes(label = n),
              # family = "Times", 
              vjust = -2) +
    xlab("Averaging Procedure") +
    ylab("Count") +
    ylim(0, 300) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste(
    #         "Prevalence of averaging method by full procedure. 
    #         Data are expressed as counts and percentages. ",
    #         sum(avg_by_full_method_tab$n), ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    theme(axis.text.x = element_text(angle=90, hjust=1)) # +
    # theme(text = element_text(family = "Times"))
avg_by_full_method_plot

ggsave(here::here("graphics/avg_by_full_method_plot.jpg"),
       avg_by_full_method_plot,
       dpi = 300)

label_size <- 15
caption_size <- 20
axes_text_size <- 30

avg_by_full_method_plot_ACSM <- avg_by_full_method_tab %>% 
    mutate(avg_procedure = paste(
        avg_type, avg_subtype, avg_amount, avg_mos, avg_mean_type, sep = "-"),
        avg_procedure = if_else(prop < 0.01, "Other", str_to_title(avg_procedure))) %>% 
    group_by(avg_procedure) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n)) %>% 
    mutate(avg_procedure = str_remove(avg_procedure, "-Mean-Whole"),
           avg_procedure = str_remove_all(avg_procedure, "-Na")) %>% 
    ggplot(aes(x = reorder(avg_procedure, -n), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop, accuracy = 0.1)), 
              family = "Times", vjust = -0.5, size = label_size) +
    geom_text(aes(label = n),
              family = "Times", vjust = -2, size = label_size) +
    xlab("Averaging Procedure") +
    ylab("Count") +
    ylim(0, 350) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste(
    #         "Prevalence of averaging method by full procedure. 
    #         Data are expressed as counts and percentages. ",
    #         sum(avg_by_full_method_tab$n), ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    labs(caption = "Counts and percentages of averaging procedure by type (time, bin, other), calculation type (bin, rolling), and number of units (seconds, breaths).") +
    theme(axis.text.x = element_text(angle=90, hjust=1)) +
    theme(text = element_text(family = "Times"),
          axis.text.x = element_text(size = axes_text_size),
          axis.text.y = element_text(size = axes_text_size),
          axis.title = element_text(size = axes_text_size),
          plot.caption = element_text(size = caption_size,
                                      hjust = 0))
    

ggsave("graphics/avg_by_full_method_plot_ACSM.tiff",
       avg_by_full_method_plot_ACSM,
       width = 18,
       height = 8.5,
       units = "in",
       dpi = 200,
       bg = "white")

pct_reporting_avg_plot_ACSM <- avg_df %>% 
    count(no_avg_details) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n),
           no_avg_details = if_else(no_avg_details,
                                    "Not Reported",
                                    "Reported"),
           no_avg_details = as.factor(no_avg_details),
           no_avg_details = forcats::fct_relevel(
               no_avg_details,
               "Reported",
               "Not Reported")) %>% 
    ggplot(aes(x = no_avg_details, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(prop, accuracy = 0.1)), 
              family = "Times", vjust = -0.5, size = label_size) +
    geom_text(aes(label = n),
              family = "Times", vjust = -2, size = label_size) +
    ylim(c(0, 1050)) +
    xlab("Averaging Method Documentation") +
    ylab("Count") +
    theme_bw() +
    labs(
        caption = "Counts and percentages of articles reporting\ntheir averaging methods") +
    theme(text = element_text(family = "Times"),
          axis.text.x = element_text(size = axes_text_size),
          axis.text.y = element_text(size = axes_text_size),
          axis.title = element_text(size = axes_text_size),
          plot.caption = element_text(size = caption_size,
                                      hjust = 0),
          panel.border = element_blank())

ggsave("graphics/avg_reporting_ACSM.tiff",
       pct_reporting_avg_plot_ACSM,
       width = 7.25,
       height = 8.5,
       units = "in",
       dpi = 200,
       bg = "white")
    
