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

comb_ineligible <- bind_rows(
    douglas_bag_mixing_chamber_articles,
    non_human,
    no_gas_data,
    not_op_rr) %>% 
    distinct(doi_suffix)

write_csv(comb_ineligible,
          "data/cpet_articles/text_analysis/ineligible_articles_combined.csv")

bbb_articles <- read_csv(
    fs::path("data/cpet_articles/text_analysis/bbb_articles.csv"),
    show_col_types = FALSE)

bbb_eligible <- anti_join(bbb_articles, comb_ineligible, by = "doi_suffix")

write_csv(bbb_eligible, 
          fs::path("data/cpet_articles/text_analysis/bbb_eligible.csv"))
