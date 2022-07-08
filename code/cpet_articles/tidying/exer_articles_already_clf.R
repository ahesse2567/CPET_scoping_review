library(tidyverse)
library(stringr)

manual_pdf_analysis <- read_csv("data/cpet_articles/Manual text analysis - Gas clf.csv")

file_list <- list.files("data/cpet_articles/pdfs/", recursive = TRUE) %>% 
    str_extract("(?<=/[:alnum:]{0,100}/).*(?=.pdf)")

exer_idx <- which(manual_pdf_analysis$Article %in% file_list)

exer <- manual_pdf_analysis[exer_idx,]
exer[296,]


exer %>% 
    mutate(Article = as.numeric(Article)) %>% 
    filter(!is.na(Article))

write_csv(exer, "data/cpet_articles/Manual text analysis - exer.csv")
