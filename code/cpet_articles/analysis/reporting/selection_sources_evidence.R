# Calculating the number of articles for the Selection of Sources of Evidence
# flow chart

library(tidyverse)
library(janitor)
library(here)

# update ineligible articles
source(here("code", "cpet_articles", "tidying", "combine_ineligible_articles.R"))

# original_wd <- getwd()
# setwd("CPET_scoping_review/")
# source("code/cpet_articles/tidying/combine_ineligible_articles.R")
# setwd(original_wd)

get_doi_suffix <- function(doi) {
    doi_suffix <- str_remove(doi, r"(10.\d+/)") %>% 
        str_replace_all(r"([()\\*,"': /?;<>])", "_._") %>% 
        str_replace_all(r"((_._){2,})", "_._")
    doi_suffix
}

all_dois <- read_csv(here("data/cpet_articles/dois_combined.csv"),
                     show_col_types = FALSE) %>% 
    clean_names() %>% 
    distinct(doi, .keep_all = TRUE) %>% 
    mutate(doi_suffix = get_doi_suffix(doi) %>% 
               tolower())
# all_dois
n_total_articles <- nrow(all_dois)

# recursive set to true b/c some txt files were moved to other folders to 
# simply regex analysis
txt_files <- list.files(
    here("data/cpet_articles/full_texts/"),
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

n_unobtained_articles <- n_total_articles - n_downloaded_files_in_doi_list

# all of the txt files we obtained in the master list
n_txt_files_in_list <- txt_files[txt_files %in% all_dois$doi_suffix] %>% 
    length()

n_unavailable_in_txt <- n_downloaded_files_in_doi_list - n_txt_files_in_list

n_non_english <- list.files(
    here("data/cpet_articles/full_texts/non-english/"),
    pattern = "\\.txt") %>% 
    length()

n_conversion_error_files <- list.files(
    here("data/cpet_articles/full_texts/empty_txt_conv/"),
    pattern = "\\.txt") %>% 
    length()

n_resolvable_articles <- n_txt_files_in_list - n_non_english - n_conversion_error_files

all_bbb_articles <- read_csv(
    here("data/cpet_articles/text_analysis/all_bbb_articles.csv"),
    show_col_types = FALSE) %>% 
    clean_names()
n_all_bbb_articles <- nrow(all_bbb_articles)

ineligible_articles <- read_csv(
    here("data/cpet_articles/text_analysis/ineligible_articles_combined.csv"),
                                show_col_types = FALSE) %>% 
    clean_names()
n_ineligible_articles <- nrow(ineligible_articles)

eligible_bbb_articles <- all_bbb_articles %>% 
    filter(!(doi_suffix %in% ineligible_articles$doi_suffix))
n_eligible_bbb_articles <- nrow(eligible_bbb_articles)

ineligible_bbb_articles <- all_bbb_articles %>% 
    filter(doi_suffix %in% ineligible_articles$doi_suffix)
n_ineligible_bbb_articles <- nrow(ineligible_bbb_articles)


ovid_records <- read_csv(here::here(
  "data/cpet_articles/database_search/ovid/doi_merged_ovid.csv"),
  show_col_types = FALSE) %>% 
  clean_names()
scopus_records <- read_csv(here::here(
  "data/cpet_articles/database_search/scopus/scopus_records_tidy.csv"),
  show_col_types = FALSE) %>% 
  clean_names()
wos_records <- read_csv(here::here(
  "data/cpet_articles/database_search/web_of_science/web_of_science_records_tidy.csv"), show_col_types = FALSE) %>% 
  clean_names()

n_total_with_na <- bind_rows(ovid_records['doi'],
                             scopus_records['doi'],
                             wos_records['doi']) %>% 
  distinct() %>% 
  nrow()


# ::: {.content-hidden when-format="docx"}
# ```{r selection_sources_evidence_flowchart}
# #| label: fig-selection_sources_evidence_flowchart
# #| fig-cap: Selection of sources of evidence flowchart. Dashed lines point to articles that were removed. Solid lines indicate the path of articles that remained in analysis. Details are provided in the main text. "Unobtained" articles were those unavailable due to University library licensing limitations or faulty download links. "Resolvable" files could be analyzed by RegExs and ML.
# #| fig-pos: 't'

flowchart <- DiagrammeR::grViz("
digraph selection_sources_evidence {
    # graph statements set attributes for ALL components of the graph
    
    # node statements provide statements for graph nodes
    # a node is a 'thing', like a box, a circle, etc.
    node [shape = oval]
    'All Articles: @@12'
    'Articles\nwithout DOI: @@13'
    'Articles\nwith DOI: @@1'
    'Unobtained\nArticles: @@10'
    'Files Unavailable\nin TXT format: @@11'
    'Downloaded Full-Text\nFiles: @@2'
    'TXT Files: @@3'
    'Non-English: @@4'
    'Conversion\nError: @@5'
    'Resolvable\nFiles: @@6'
    'All Breath-by-Breath: @@7'
    'Ineligible\nBreath-by-Breath: @@8'
    'Eligible\nBreath-by-Breath: @@9'
    
    # edge statements direct operations between nodes
    'All Articles: @@12' -> 'Articles\nwith DOI: @@1'
    'All Articles: @@12'-> 'Articles\nwithout DOI: @@13' [style=dashed]
    'Articles\nwith DOI: @@1' -> 'Downloaded Full-Text\nFiles: @@2'
    'Articles\nwith DOI: @@1' -> 'Unobtained\nArticles: @@10' [style=dashed]
    'Downloaded Full-Text\nFiles: @@2' -> 'TXT Files: @@3'
    'Downloaded Full-Text\nFiles: @@2' -> 'Files Unavailable\nin TXT format: @@11' [style=dashed]
    'TXT Files: @@3' -> {'Non-English: @@4' 'Conversion\nError: @@5'} [style=dashed]
    'TXT Files: @@3' -> 'Resolvable\nFiles: @@6'
    'Resolvable\nFiles: @@6' -> 'All Breath-by-Breath: @@7'
    'All Breath-by-Breath: @@7' -> 'Ineligible\nBreath-by-Breath: @@8' [style=dashed]
    'All Breath-by-Breath: @@7' -> 'Eligible\nBreath-by-Breath: @@9'

    # each statement will have a list nodes or edges
    
}

[1]: format(n_total_articles, big.mark = ',', scientific = FALSE)
[2]: format(n_downloaded_files_in_doi_list, big.mark = ',', scientific = FALSE)
[3]: format(n_txt_files_in_list, big.mark = ',', scientific = FALSE)
[4]: format(n_non_english, big.mark = ',', scientific = FALSE)
[5]: format(n_conversion_error_files, big.mark = ',', scientific = FALSE)
[6]: format(n_resolvable_articles, big.mark = ',', scientific = FALSE)
[7]: format(n_all_bbb_articles, big.mark = ',', scientific = FALSE)
[8]: format(n_ineligible_bbb_articles, big.mark = ',', scientific = FALSE)
[9]: format(n_eligible_bbb_articles, big.mark = ',', scientific = FALSE)
[10]: format(n_unobtained_articles, big.mark = ',', scientific = FALSE)
[11]: format(n_unavailable_in_txt, big.mark = ',', scientific = FALSE)
[12]: format(n_total_with_na, big.mark = ',', scientific = FALSE)
[13]: format(n_total_with_na - n_total_articles, big.mark = ',', scientific = FALSE)
    ")

# flowchart

# save html version of flowchart
htmlwidgets::saveWidget(
  flowchart,
  here::here("graphics/selection_sources_evidence_flowchart.html"))
# convert html to jph
webshot::webshot(
  here::here("graphics/selection_sources_evidence_flowchart.html"),
  here::here("graphics/selection_sources_evidence_flowchart.jpg"),
  zoom = 2)
# for now, use a free DPI converter tool to get up to 300 dpi
# https://convert.town/image-dpi
# ```
# :::