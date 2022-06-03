library(tidyverse)
library(stringr)

rm(list = ls())

file_list <- list.files("data/cpet_articles/txts", full.names = TRUE)

file_info <- map_df(file_list, file.info)

file_sizes <- map_dbl(file_list, file.size) %>% 
    as_tibble() %>% 
    mutate(fname = list.files("data/cpet_articles/txts"),
           scaled_size = scale(value)) %>% 
    relocate(fname) %>% 
    rename(size = value)
file_sizes

set.seed(29847)
random500 <- file_sizes %>% 
    filter(value > 5000) %>% 
    sample_n(500) %>% 
    mutate(pdf_name = str_replace(fname, ".txt", ".pdf"))

pdf_file_list = list.files("data/cpet_articles/pdfs/unpaywall_oa/")

pdf_idxs <- which(pdf_file_list %in% random500$pdf_name)
pdfs_to_copy <- pdf_file_list[pdf_idxs]

file.copy(from = paste0("/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/pdfs/unpaywall_oa/",
                        pdfs_to_copy),
          to = paste0("/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/pdfs/manual_pdf_analysis/",
                      pdfs_to_copy))


