library(tidyverse)
library(janitor)

douglas_bag_mixing_chamber_articles <- read_csv(
    "data/cpet_articles/text_analysis/eligibility/Mixing Chamber Douglas Bag - Sheet1.csv",
    show_col_types = FALSE) %>% 
    filter(bbb == FALSE) %>% 
    select(doi_suffix)

non_human <- read_csv("data/cpet_articles/text_analysis/eligibility/Eligibility - human.csv",
                      show_col_types = FALSE) %>% 
    clean_names() %>% 
    filter(human == FALSE) %>% 
    select(doi_suffix)

not_op_rr <- read_csv(
    "data/cpet_articles/text_analysis/eligibility/Eligibility - op-rr.csv",
    show_col_types = FALSE) %>% 
    clean_names() %>% 
    filter(op_rr == FALSE) %>% 
    select(doi_suffix)

no_gas_data <- read_csv("data/cpet_articles/text_analysis/eligibility/No Gas Data - Sheet1.csv",
                        show_col_types = FALSE) %>% 
    clean_names() %>% 
    select(doi_suffix)

bbb_articles <- read_csv("data/cpet_articles/text_analysis/bbb_articles.csv",
                         show_col_types = FALSE) %>% 
    clean_names() %>% 
    select(doi_suffix)

no_gas_bbb <- semi_join(no_gas_data, bbb_articles)

db_mix_bbb <- semi_join(douglas_bag_mixing_chamber_articles, bbb_articles)
nrow(db_mix_bbb)

non_human_bbb <- semi_join(non_human, bbb_articles)
nrow(non_human_bbb)

not_op_rr_bbb <- semi_join(not_op_rr, bbb_articles)
nrow(not_op_rr_bbb)

comb_ineligible <- bind_rows(
    douglas_bag_mixing_chamber_articles,
    non_human,
    no_gas_data,
    not_op_rr) %>%
    distinct(doi_suffix)

bbb_eligible <- anti_join(bbb_articles, comb_ineligible)
nrow(bbb_eligible)

