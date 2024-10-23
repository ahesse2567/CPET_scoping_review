library(tidyverse)
library(fs)

ovid_records <- read_csv(path(
    "data/cpet_articles/database_search/ovid/doi_merged_ovid.csv"),
    show_col_types = FALSE) %>% 
    select(doi)

scopus_records <- read_csv(path(
    "data/cpet_articles/database_search/scopus/no_exer/scopus_records_tidy.csv"),
    show_col_types = FALSE) %>% 
    select(doi)

wos_records <- read_csv(path(
    "data/cpet_articles/database_search/web_of_science/web_of_science_records_tidy.csv"),
    show_col_types = FALSE) %>% 
    select(doi)

all_dois <- reduce(list(ovid_records, scopus_records, wos_records), rbind)
