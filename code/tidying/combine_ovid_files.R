library(tidyverse)
library(readxl)

files <- list.files("data/raw/ovid_exports/", full.names = TRUE)
file_list <- map(files, read_xls, skip = 1)
all_records <- bind_rows(file_list)

write_csv(all_records, "data/raw/ovid_records_combined.csv")