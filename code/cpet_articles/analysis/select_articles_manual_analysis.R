library(tidyverse)
library(stringr)
library(janitor)
library(progress)

rm(list = ls())

file_list_full <- list.files("data/cpet_articles/full_texts/txts",
                             full.names = TRUE)
# get list of files by their doi_suffix name
file_list_short <- list.files("data/cpet_articles/full_texts/txts",
                              full.names = FALSE) %>% 
    tools::file_path_sans_ext() %>% 
    as.character()

# load articles I've at least partially analyzed
manual_analysis <- read_csv("data/cpet_articles/Manual text analysis - Data.csv",
                            show_col_types = FALSE) %>% 
    clean_names()

# screen out articles I haven't yet analyzed
partially_analyzed <- manual_analysis %>% 
    filter(!is.na(gas_data) | eligible == 'i')

to_be_analyzed <- which(!(file_list_short %in% partially_analyzed$doi_suffix))

set.seed(239847)
n <- 50
random_n <- sample(file_list_short[to_be_analyzed], n) %>% 
    as_tibble() %>% 
    rename(doi_suffix = value)

clipr::write_clip(random_n) # make it easy to paste into Google Sheet

# update spreadsheet of articles to review manually    
partially_analyzed <- bind_rows(partially_analyzed, random_n)
partially_analyzed %>% 
    write_csv("data/cpet_articles/full_texts/manual_analysis/running_manual_analysis.csv")

manual_analysis_article_folder <- "data/cpet_articles/full_texts/manual_analysis/articles/"
manual_analysis_articles <- list.files(manual_analysis_article_folder) %>% 
    tools::file_path_sans_ext()

full_text_dirs <- list.dirs("data/cpet_articles/full_texts")[list.dirs("data/cpet_articles/full_texts") %>% 
                                                                 str_which("/(pdfs|txts|epubs)")]

# add full texts to manual analysis folder
pb <- progress_bar$new(total = length(partially_analyzed$doi_suffix))
for(article in partially_analyzed$doi_suffix) {
    # check if full text is already folder
    if(!(article %in% manual_analysis_articles)) {
        # if not, locate the full-text
        for(file_type in c('pdf', 'txt')){
            folder <- paste0("data/cpet_articles/full_texts/",file_type, "s")
            files <-  list.files(folder) %>% 
                map_chr(tools::file_path_sans_ext)
            if(article %in% files){ # check for PDF first
                source <- list.files(folder, full.names = TRUE) %>% 
                    str_subset(article)
                dest <- paste0(
                    "data/cpet_articles/full_texts/manual_analysis/articles/",
                    article, ".", file_type)
                file.copy(from = source, to = dest) # copy file over
                break # no need to move txt over if pdf is available
            }
        }
    }
    pb$tick()
}

# repeat the above loop, but only for the most recent 50 articles
update_manual_analysis_fts <- function(){
    pb <- progress_bar$new(total = length(partially_analyzed$doi_suffix))
    # browser()
    for(article in partially_analyzed$doi_suffix) {
        # check if full text is already folder
        if(!(article %in% manual_analysis_articles)) {
            # if not, locate the full-text
            for(file_type in c('pdf', 'txt')){
                folder <- paste0("data/cpet_articles/full_texts/",file_type, "s")
                files <-  list.files(folder) %>% 
                    map_chr(tools::file_path_sans_ext)
                if(article %in% files){ # check for PDF first
                    source <- list.files(folder, full.names = TRUE) %>% 
                        str_subset(article)
                    dest <- paste0(
                        "data/cpet_articles/full_texts/manual_analysis/articles/",
                        article, ".", file_type)
                    file.copy(from = source, to = dest) # copy file over
                }
                break # no need to move txt over if pdf is available
            }
        }
        pb$tick()
    }
}

update_manual_analysis_fts()

update_newest_manual_analysis_fts <- function(){
    pb <- progress_bar$new(total = length(random_n))
    # browser()
    new_files_folder <- "data/cpet_articles/full_texts/manual_analysis/newest_to_analyze/"
    current_files <- list.files(new_files_folder, full.names = TRUE)
    for(file in current_files){
        file.remove(file)
    }
    
    for(article in random_n$doi_suffix) {
        # check if full text is already folder
        if(!(article %in% new_files_folder)) {
            # if not, locate the full-text
            for(file_type in c('pdf', 'txt')){
                folder <- paste0("data/cpet_articles/full_texts/",file_type, "s")
                files <-  list.files(folder) %>% 
                    map_chr(tools::file_path_sans_ext)
                if(article %in% files){ # check for PDF first
                    source <- list.files(folder, full.names = TRUE) %>% 
                        str_subset(article)
                    dest <- paste0(new_files_folder, article, ".", file_type)
                    file.copy(from = source, to = dest) # copy file over
                    break # no need to move txt over if pdf is available
                }
            }
        }
        pb$tick()
    }
}
update_newest_manual_analysis_fts()
# copy these into the "To be analyzed" folder in Google Drive
