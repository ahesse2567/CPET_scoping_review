library(tidyverse)
library(janitor)

douglas_bag_mixing_chamber_articles <- read_csv(
    "data/cpet_articles/text_analysis/Mixing Chamber Douglas Bag - Sheet1.csv",
    show_col_types = FALSE) %>% 
    filter(bbb == FALSE) %>% 
    select(doi_suffix)

eligibility <- read_csv("data/cpet_articles/text_analysis/Eligibility - eligibility.csv",
                        show_col_types = FALSE) %>% 
    clean_names() %>% 
    filter(eligible == FALSE) %>% 
    select(doi_suffix)

no_gas_data <- read_csv("data/cpet_articles/text_analysis/No Gas Data - Sheet1.csv",
                        show_col_types = FALSE) %>% 
    clean_names() %>% 
    select(doi_suffix)

not_op_rr <- read_csv("data/cpet_articles/text_analysis/Not OP-RR - Sheet1.csv",
                      show_col_types = FALSE) %>% 
    clean_names() %>% 
    select(doi_suffix)

comb_ineligible <- bind_rows(douglas_bag_mixing_chamber_articles,
          eligibility,
          no_gas_data,
          not_op_rr)

write_csv(comb_ineligible,
          "data/cpet_articles/text_analysis/combined_ineligible_articles.csv")
