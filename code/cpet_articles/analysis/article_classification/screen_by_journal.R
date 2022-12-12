library(tidyverse)
library(stringr)

get_doi_suffix <- function(x){
    doi_suffix <- str_split(x, pattern = "/", n = 2)[[1]][2] %>% 
        str_replace_all("[()\\\\*\\[\\],\"': /?;<>]", "_._") %>% 
        str_replace("(_._){2,}", "_._")
    doi_suffix
}

all_articles <- read_csv("data/cpet_articles/unpaywall/unpaywall_info.csv",
                         show_col_types = FALSE) %>% 
    rowwise() %>% 
    mutate(doi_suffix = get_doi_suffix(doi)) %>% 
    relocate(doi_suffix)

eligibility_df <- read_csv("data/cpet_articles/text_analysis/Manual text analysis - eligibility.csv")

merge_df <- inner_join(eligibility_df, all_articles)
counts_by_journal_human <- merge_df %>% 
    group_by(journal_name, human) %>% 
    summarize(n = n()) %>% 
    arrange(desc(n), journal_name)
counts_by_journal_human

write_doi_suffix_to_clip <- function(df, journal){
    filtered_articles <- df %>% 
        filter(str_detect(tolower(journal_name), tolower(journal))) %>% 
        select(doi_suffix) %>% 
        drop_na() %>% 
        pull()
    clipr::write_clip(filtered_articles)
    print(paste(length(filtered_articles), "articles written to clipboard"))
}

write_doi_suffix_to_clip(all_articles,
                         "review")
