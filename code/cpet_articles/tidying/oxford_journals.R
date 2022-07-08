library(tidyverse)
library(janitor)

articles <- read_csv("data/cpet_articles/unpaywall/unpaywall_info.csv",
                     show_col_types = FALSE) %>% 
    clean_names()

articles_by_publisher <- articles %>% 
    group_by(publisher) %>% 
    summarize(count = n()) %>% 
    arrange(desc(count))

oxford_journals <- articles %>% 
    filter(publisher == "Oxford University Press (OUP)") %>% 
    select(journal_name) %>% 
    unique()
oxford_journals

library(clipr)
write_clip(oxford_journals)
