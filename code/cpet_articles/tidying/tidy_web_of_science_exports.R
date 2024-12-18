library(tidyverse)
library(readxl)
library(janitor)

files <- list.files("data/cpet_articles/web_of_science/raw_web_of_science_exports/",
                    full.names = TRUE)
file_list <- map(files, read_xls, skip = 10)
file_list <- map(file_list, function(x) x %>% 
                     clean_names %>% 
                     mutate(across(where(is.numeric), as.character)))

all_records <- bind_rows(file_list)
all_records <- all_records[, colSums(is.na(all_records)) < nrow(all_records)]

all_records <- all_records %>% 
    select(c(title,
             authors,
             source_title,
             publication_year,
             issn,
             publication_year,
             doi))
    
write_csv(all_records,
          "data/cpet_articles/web_of_science/web_of_science_records_tidy.csv")
