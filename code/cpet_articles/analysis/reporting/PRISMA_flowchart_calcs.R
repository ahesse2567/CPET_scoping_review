library(tidyverse)
library(fs)

ovid_records <- read_csv(path(
    "data/cpet_articles/database_search/ovid/doi_merged_ovid.csv"),
    show_col_types = FALSE) %>% 
    janitor::clean_names() %>% 
    rename(title = ti)

scopus_records <- read_csv(path(
    "data/cpet_articles/database_search/scopus/scopus_records_tidy.csv"),
    show_col_types = FALSE) %>% 
    janitor::clean_names()

wos_records <- read_csv(path(
    "data/cpet_articles/database_search/web_of_science/web_of_science_records_tidy.csv"),
    show_col_types = FALSE) %>% 
    janitor::clean_names()

# The following code is technically wrong because DOIs are case insensitive
# and this does not account for that.
# bind_rows(ovid_records["doi"],
#           scopus_records["doi"],
#           wos_records["doi"]) %>% 
#     filter(!is.na(doi)) %>% 
#     distinct(doi) %>% 
#     nrow()

all_articles <- 
    map(list(ovid_records, scopus_records, wos_records),
        \(x) dplyr::select(x, all_of(c("doi", "title")))) %>%
    list_rbind() %>% 
    mutate(title = str_to_lower(title) %>%
               # remove periods, extra whitespace at end of titles
               str_remove("[\\.[:space:]]+$"),
           # some DOIs would be considered duplicates except for they
           # had different cases
           doi = str_to_lower(doi),
           # key = row_number()
           )

# articles w/o a doi
articles_wo_doi <- all_articles %>% 
    filter(is.na(doi))
nrow(articles_wo_doi)

# work with only those articles with a DOI
articles_doi <- all_articles %>% 
    filter(!is.na(doi))
nrow(articles_doi)


articles_unique <- articles_doi %>% 
    distinct(doi, .keep_all = TRUE)
nrow(articles_unique)

dupes_removed <- nrow(articles_doi) - nrow(articles_unique)
dupes_removed

# some articles may be duplicates by title
duplicate_titles_df <- articles_doi %>% 
    filter(!is.na(title)) %>%
    filter(n() > 1, .by = title) %>% 
    # distinct(title, .keep_all = TRUE) %>%
    arrange(title)

# other articles may be duplicates by doi
duplicate_dois_df <- articles_doi %>% 
    filter(!is.na(doi)) %>% 
    group_by(doi) %>% 
    filter(n() > 1) %>% 
    # distinct(doi, .keep_all = TRUE) %>%
    arrange(doi)

# there are more duplicate titles than duplicate dois
# do I need to find if there are differences between the duplicated titles
# and dois?



# get a full list of duplicates.
dupes_comb <- full_join(duplicate_titles_df, 
                        duplicate_dois_df,
                        by = "key")
    # there are some records that are recorded twice because 
    # they have a duplicate title but a missing (NA) doi. Remove blank fields
    # filter(!is.na(title)) %>% 
    # filter(!is.na(doi))
# this still has duplicates due to different DOIs or different titles

dupes_comb %>% 
    doi = 

# apparently there are multiple DOIs to the same article. 
diff_doi_same_title <- dupes_comb %>% 
    filter(n() > 1, .by = title) %>% 
    arrange(title)

# there are some articles with subtle differences in the title, such as
# different spaces or hyphenation
diff_title_same_doi <- dupes_comb %>% 
    filter(n() > 1, .by = doi) %>% 
    arrange(title)

# get rid of the multiple DOIs or multiple titles for the same article
all_dupes <- dupes_comb %>% 
    distinct(doi, .keep_all = TRUE) %>% 
    distinct(title, .keep_all = TRUE)

dup_titles <- all_articles %>% 
    



dupes_to_remove <- 

# These articles were excluded 


duplicates <- all_dois %>% 
    group_by(doi) %>% 
    filter(n() > 1)
nrow(duplicates)

unique_dois <- all_articles %>% 
    filter(!is.na(doi)) %>% 
    unique()
nrow(unique_dois)


all_dois <- reduce(map(list(ovid_records, scopus_records, wos_records),
                       \(x) dplyr::select(x, doi)),
                   rbind)
