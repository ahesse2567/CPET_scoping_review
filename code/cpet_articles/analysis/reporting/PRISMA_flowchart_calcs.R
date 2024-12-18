# Showing step-by-step calculations for PRISMA flow diagram
# this combines some different scripts, such as selection_sources_evidence.R

library(tidyverse)
library(fs)

##############################################################################
# Identification 
##############################################################################

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

##############################################################################
# Screening - Ability to obtain and analyze
##############################################################################

get_doi_suffix <- function(doi) {
    doi_suffix <- str_remove(doi, r"(10.\d+/)") %>% 
        str_replace_all(r"([()\\*,"': /?;<>])", "_._") %>% 
        str_replace_all(r"((_._){2,})", "_._")
    doi_suffix
}

# another way of getting the same thing as articles_unique

all_dois <- read_csv(here("data/cpet_articles/dois_combined.csv"),
                     show_col_types = FALSE) %>% 
    clean_names() %>% 
    distinct(doi, .keep_all = TRUE) %>% 
    mutate(doi_suffix = get_doi_suffix(doi) %>% 
               tolower())
# all_dois
n_total_articles <- nrow(all_dois)
n_total_articles

# Determine how many articles were unobtainable by first getting a list of 
# every downloaded file

# recursive set to true b/c some txt files were moved to other folders to 
# simply regex analysis
txt_files <- list.files(
    here("data/cpet_articles/full_texts/txts"),
    pattern = "\\.txt",
    recursive = TRUE) %>% 
    basename() %>% 
    unique() %>% 
    tools::file_path_sans_ext()

pdf_files <- list.files(
    here("data/cpet_articles/full_texts/pdfs/"),
    pattern = "\\.pdf") %>% 
    basename() %>% 
    unique() %>% 
    tools::file_path_sans_ext()

epub_files <- list.files(
    here("data/cpet_articles/full_texts/epubs/"),
    pattern = "\\.epub") %>% 
    basename() %>% 
    unique() %>% 
    tools::file_path_sans_ext()

unique_files <- c(txt_files, pdf_files, epub_files) %>% unique()

# every file from the master list that we obtained
n_downloaded_files_in_doi_list <- 
    unique_files[unique_files %in% all_dois$doi_suffix] %>% 
    length()
n_downloaded_files_in_doi_list

# Also known as "reports not retrieved per PRISMA
n_unobtained_articles <- n_total_articles - n_downloaded_files_in_doi_list
n_unobtained_articles

# all of the txt files we obtained in the master list
n_txt_files_in_list <- txt_files[txt_files %in% all_dois$doi_suffix] %>% 
    length()
n_txt_files_in_list

n_unavailable_in_txt <- n_downloaded_files_in_doi_list - n_txt_files_in_list
n_unavailable_in_txt

# of the files obtained, how many couldn't be analyzed

n_non_english <- list.files(
    here("data/cpet_articles/full_texts/non-english/"),
    pattern = "\\.txt") %>% 
    length()
n_non_english

n_conversion_error_files <- list.files(
    here("data/cpet_articles/full_texts/empty_txt_conv/"),
    pattern = "\\.txt") %>% 
    length()
n_conversion_error_files

n_resolvable_articles <- n_txt_files_in_list - n_non_english -
    n_conversion_error_files
n_unresolvable_files <- 
    n_unavailable_in_txt +
    n_non_english +
    n_conversion_error_files

# within those that could be analyzed, how many mentioned BBB

bbb_articles <- read_csv("data/cpet_articles/text_analysis/bbb_articles.csv",
                         show_col_types = FALSE) %>% 
    clean_names() %>% 
    select(doi_suffix)
n_bbb_articles <- nrow(bbb_articles)

n_non_bbb_articles <- n_resolvable_articles - n_bbb_articles

##############################################################################
# Screening - Eligibility
##############################################################################

# we found several articles that were ineligible, but not all of them also
# mentioned BBB data. This finds which mentioned BBB data and which were 
# ineligible.

douglas_bag_mixing_chamber_articles <- read_csv(
    "data/cpet_articles/text_analysis/eligibility/Mixing Chamber Douglas Bag - Sheet1.csv",
    show_col_types = FALSE) %>% 
    filter(bbb == FALSE) %>% 
    select(doi_suffix)
db_mix_bbb <- semi_join(douglas_bag_mixing_chamber_articles, bbb_articles)
n_db_mix_bbb <- nrow(db_mix_bbb)

non_human <- read_csv("data/cpet_articles/text_analysis/eligibility/Eligibility - human.csv",
                      show_col_types = FALSE) %>% 
    clean_names() %>% 
    filter(human == FALSE) %>% 
    select(doi_suffix)
non_human_bbb <- semi_join(non_human, bbb_articles)
n_non_human_bbb <- nrow(non_human_bbb)

not_op_rr <- read_csv(
    "data/cpet_articles/text_analysis/eligibility/Eligibility - op-rr.csv",
    show_col_types = FALSE) %>% 
    clean_names() %>% 
    filter(op_rr == FALSE) %>% 
    select(doi_suffix)
not_op_rr_bbb <- semi_join(not_op_rr, bbb_articles)
n_not_op_rr_bbb <- nrow(not_op_rr_bbb)

no_gas_data <- read_csv("data/cpet_articles/text_analysis/eligibility/No Gas Data - Sheet1.csv",
                        show_col_types = FALSE) %>% 
    clean_names() %>% 
    select(doi_suffix)

no_gas_bbb <- semi_join(no_gas_data, bbb_articles)
n_no_gas_bbb <- nrow(no_gas_bbb)

# make sure the exclusions line up
total_studies <- 
    # total files we tried to analyze
    n_downloaded_files_in_doi_list -
    # files we couldn't analyze at all because we couldn't get the data in a 
    # TXT format, because the language wasn't Enligh, or because the conversion
    # to TXT didn't work.
    n_unavailable_in_txt -
    n_non_english -
    n_conversion_error_files -
    # at this point, we're at the n_rsolvable_files
    # now subtract the files we found to be ineligible because they didn't
    # mention the correct terms or because of other criteria
    n_non_bbb_articles -
    n_db_mix_bbb -
    n_non_human_bbb -
    n_not_op_rr_bbb -
    n_no_gas_bbb
    
# check final number by cross referencing total BBB articles
# with the combination of ineligible articles
comb_ineligible <- bind_rows(
    douglas_bag_mixing_chamber_articles,
    non_human,
    no_gas_data,
    not_op_rr) %>%
    distinct(doi_suffix)

bbb_eligible <- anti_join(bbb_articles, comb_ineligible)
nrow(bbb_eligible)

# if(total_studies != nrow(bbb_eligible)) {
#     print("Total studies do NOT match elibible BBB articles! Boo...")
# } else {
#     print("Total studies MATCHES eligible BBB articles. Yay!")
# }
