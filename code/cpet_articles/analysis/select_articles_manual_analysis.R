library(tidyverse)
library(stringr)
library(janitor)

rm(list = ls())

file_list_full <- list.files("data/cpet_articles/full_texts/txts",
                             full.names = TRUE)
file_list_short <- list.files("data/cpet_articles/full_texts/txts",
                              full.names = FALSE) %>% 
    tools::file_path_sans_ext() %>% 
    as.character()

manual_analysis <- read_csv("data/cpet_articles/Manual text analysis - Data.csv",
                            show_col_types = FALSE) %>% 
    clean_names()

partially_analyzed <- manual_analysis %>% 
    filter(!is.na(gas_data) | eligible == 'i')

file_list_short_tib <- file_list_short %>% 
    as_tibble() %>% 
    rename(doi_suffix = value)

to_be_analyzed <- which(!(file_list_short %in% partially_analyzed$doi_suffix))

set.seed(239847)
random50 <- sample(file_list_short[to_be_analyzed], 50) %>% 
    as_tibble() %>% 
    rename(doi_suffix = value)

partially_analyzed <- bind_rows(partially_analyzed, random50)
partially_analyzed %>% 
    write_csv("data/cpet_articles/full_texts/manual_analysis/running_manual_analysis.csv")

# update spreadsheet of articles to review manually    
# find articles NOT already in manual_analysis folder
# copy full-texts into the articles folder within manual_analysis


