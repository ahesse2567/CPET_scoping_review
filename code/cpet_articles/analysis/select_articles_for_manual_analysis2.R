library(tidyverse)
library(stringr)

rm(list = ls())

file_list <- list.files("data/cpet_articles/txts") %>%
    str_replace(".txt", "")
manual1 <- list.files("data/cpet_articles/pdfs/manual_pdf_analysis1") %>% 
    str_replace(".pdf", "")

non_overlap_files <- c(setdiff(file_list, manual1), setdiff(manual1, file_list))

file_info <- map_df(non_overlap_files, file.info)

file_sizes <- map_dbl(non_overlap_files, file.size) %>% 
    as_tibble() %>% 
    mutate(fname = list.files("data/cpet_articles/txts"),
           scaled_size = scale(value)) %>% 
    relocate(fname) %>% 
    rename(size = value)
file_sizes

set.seed(93476)
random500 <- file_sizes %>% 
    filter(size > 5000) %>% 
    sample_n(500) %>% 
    mutate(pdf_name = str_replace(fname, ".txt", ".pdf"))

pdf_file_list = list(list.files("data/cpet_articles/pdfs/unpaywall_oa/"),
                     list.files("data/cpet_articles/pdfs/springer_non_oa_pdfs/"),
                     list.files("data/cpet_articles/pdfs/unpaywall_oa_ssl/")) %>% 
    unlist()

pdf_idxs <- which(pdf_file_list %in% random500$pdf_name)
pdfs_to_copy <- pdf_file_list[pdf_idxs]

folders <- c("unpaywall_oa", "unpaywall_oa_ssl", "springer_non_oa_pdfs")

for(folder in folders){
    folder_name = paste0("/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/pdfs/", folder, "/")
    file.copy(from = paste0(folder_name, pdfs_to_copy),
              to = paste0("/Users/antonhesse/Desktop/Anton/Education/UMN/Lab and Research/HSPL/CPET_scoping_review/data/cpet_articles/pdfs/manual_pdf_analysis/manual2",
                          pdfs_to_copy))
}


