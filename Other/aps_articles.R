library(tidyverse)
library(stringr)

articles <- read_csv("data/cpet_articles/unpaywall/unpaywall_info.csv",
                     show_col_types = FALSE)
articles <- articles %>% 
    mutate(doi_suffix = str_remove(doi, ".*/")) %>% 
    relocate(doi_suffix, .before = doi)

pdfs <- list.files("data/cpet_articles/full_texts/pdfs/",
                   pattern = ".pdf",
                   recursive = TRUE) %>% 
    str_remove("\\.pdf") %>% 
    str_remove("(.*/)+")

txts <- list.files("data/cpet_articles/full_texts/txts/",
                   pattern = ".txt",
                   recursive = TRUE) %>% 
    str_remove("\\.txt") %>% 
    str_remove("(.*/)+")

epubs <- list.files("data/cpet_articles/full_texts/epubs/",
                    pattern = ".epub",
                    recursive = TRUE) %>% 
    str_remove("\\.epub") %>% 
    str_remove("(.*/)+")
epubs

full_texts <- c(pdfs, txts, epubs) %>% 
    unique()

remaining_artilces <- articles[which(!(articles$doi_suffix %in% full_texts)),]
aps_articles <- remaining_artilces %>% 
    filter(publisher == "American Physiological Society") %>% 
    select(doi, journal_name)

write_csv(aps_articles, "other/aps_articles.csv")
