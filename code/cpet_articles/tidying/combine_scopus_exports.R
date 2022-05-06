library(tidyverse)
library(janitor)

files <- list.files("data/cpet_articles/scopus/raw_scopus_exports/",
                    full.names = TRUE)
file_list <- map(files, read_csv, show_col_types = FALSE)
file_list <- map(file_list, function(x) x %>% 
                     clean_names %>% 
                     mutate(across(where(is.numeric), as.character)))

all_records <- bind_rows(file_list)
all_records <- all_records[, colSums(is.na(all_records)) < nrow(all_records)]

write_csv(all_records,
          "data/cpet_articles/scopus/scopus_records_combined.csv")
