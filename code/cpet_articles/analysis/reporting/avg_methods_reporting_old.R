
merge_df <- inner_join(avg_data, bbb_articles, by = "doi_suffix") %>% 
    select(colnames(avg_data)) %>% 
    rowwise() %>%
    mutate(all_NA = all(is.na(
        c(avg_type, avg_subtype, avg_amount,
          avg_mos, avg_mean_type)
    ))) %>% 
    filter(!is.na(avg_text) | all_NA == FALSE) # there are a few articles
# that excaped my regex. However, I still found that they had averaging methods
# when reading them manually.

######## Averaging methods #################

total_articles <- merge_df %>% 
    distinct(doi_suffix, .keep_all = FALSE) %>% 
    nrow()

# initial estimate of how many articles have averaging methods
# only considering if they have avg details or not
merge_df %>%
    distinct(doi_suffix, .keep_all = TRUE) %>%
    mutate(has_avg_details = case_when(
        avg_text == FALSE ~ FALSE,
        avg_text != FALSE & !is.na(avg_text) ~ TRUE,
        is.na(avg_text) & all_NA == FALSE ~ TRUE)) %>%
    count(has_avg_details) %>%
    ungroup() %>%
    mutate(prop = prop.table(n))
# so about 70% have averaging method details of some kind. This percentage will
# drop because not all avg_text actually indicates avg_methods

documented_details_tab <- merge_df %>% 
    filter(documented == TRUE | done == TRUE | all_NA == FALSE)  %>% 
    distinct(doi_suffix, .keep_all = TRUE) %>% 
    count(all_NA) %>% 
    ungroup() %>% 
    mutate(prop = prop.table(n))
documented_details_tab

# unique articles WITH averaging details
documented_has_avg_details <- documented_details_tab %>% 
    filter(all_NA == FALSE) %>% 
    select(n) %>% 
    pull()

# unique articles WITHOUT averaging details
documented_no_avg_details <- documented_details_tab %>% 
    filter(all_NA == TRUE) %>% 
    select(n) %>% 
    pull()

total_documented <- documented_has_avg_details + documented_no_avg_details

pct_documented_no_avg_details <- documented_details_tab %>% 
    filter(all_NA == TRUE) %>% 
    select(prop) %>% 
    pull()

documented_doi_suffixes <- merge_df %>% 
    filter(documented == TRUE | done == TRUE | all_NA == FALSE)  %>% 
    distinct(doi_suffix) %>% 
    pull()

undocumented_doi_suffixes <- merge_df %>%
    filter(!(doi_suffix %in% documented_doi_suffixes)) %>% 
    distinct(doi_suffix) %>% 
    pull()

total_undocumented <- total_articles - total_documented


count_undocumented_no_avg_text <- merge_df %>%
    filter(doi_suffix %in% undocumented_doi_suffixes) %>% 
    filter(avg_text == FALSE) %>%
    nrow()

count_undocumented_with_avg_text <- merge_df %>% 
    filter(doi_suffix %in% undocumented_doi_suffixes) %>% 
    filter(avg_text != FALSE) %>% 
    nrow()

est_count_undocumented_with_avg_text_no_avg_method <- 
    round(count_undocumented_with_avg_text * pct_documented_no_avg_details,0)

est_total_undoc_no_avg_text <- 
    count_undocumented_no_avg_text + est_count_undocumented_with_avg_text_no_avg_method

est_total_undoc_with_avg_text <- 
    round(count_undocumented_with_avg_text * (1 - pct_documented_no_avg_details),0)

documented_has_avg_details + documented_no_avg_details + 
    est_total_undoc_no_avg_text + est_total_undoc_with_avg_text ==
    total_articles

est_total_with_avg_details <- 
    documented_has_avg_details + est_total_undoc_with_avg_text

est_total_no_avg_details <- 
    documented_no_avg_details + est_total_undoc_no_avg_text

avg_documentation_tib <- tibble(
    has_avg_documentation = c(TRUE, FALSE),
    estimate = c(est_total_with_avg_details,
                 est_total_no_avg_details)) %>%
    mutate(prop = prop.table(estimate),
           documentation = if_else(has_avg_documentation == TRUE,
                                   "Describes Averaging Methods",
                                   "Does NOT Describe Averaging Methods"))
avg_documentation_tib

overall_avg_documentation_rate_plot <-
    avg_documentation_tib %>%  ggplot(aes(x = documentation, y = estimate)) +
    geom_col() +
    xlab("Averaging Method Documentation") +
    ylab("Count") +
    geom_text(aes(label = estimate), vjust = -2) +
    geom_text(aes(label = scales::percent(prop)), vjust = -0.5) +
    ylim(0, plyr::round_any(max(avg_documentation_tib$estimate), 1000, f = ceiling)) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Estimated counts and percentages of data averaging reporting. N = ",
    #           total_articles, ".", sep = ""), width = 100)) +
    theme(plot.caption = element_text(hjust=0))
overall_avg_documentation_rate_plot
# ggsave("graphics/overall_avg_documentation_rate_plot.tiff", device = "tiff")

# count by averaging type
n_avg <- merge_df %>% 
    filter(!is.na(avg_type)) %>% 
    nrow()

avg_by_type_tab <- merge_df %>% 
    filter(!is.na(avg_type)) %>% 
    count(avg_type) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_type = str_to_title(avg_type))
avg_by_type_tab

log10_floor <- function(x) {
    10^(floor(log10(x)))
}

calc_upper_y_lim <- function(x) {
    closest_lower_order_mag <- log10_floor(x)
    upper_y_lim <- round(x / closest_lower_order_mag) * closest_lower_order_mag
    if(upper_y_lim < x) {
        upper_y_lim <- upper_y_lim + closest_lower_order_mag * 0.75
    }
    upper_y_lim
}

# avg by type plot
avg_by_type_plot <- avg_by_type_tab %>% 
    mutate(avg_type = if_else(pct < 0.01, "Other", avg_type)) %>% 
    group_by(avg_type) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    ggplot(aes(x = avg_type, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Averaging Method Type") +
    ylab("Count") +
    ylim(0,calc_upper_y_lim(max(avg_by_type_tab$n))) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Averaging method by type. Data are expressed as counts and percentages.\nN = ",
    #           n_avg, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    theme(axis.text.x = element_text(angle=45, hjust=1))
avg_by_type_plot

# avg by subtype count
n_avg_subtype <- merge_df %>% 
    filter(!is.na(avg_subtype)) %>% 
    nrow()

avg_by_subtype_tab <- merge_df %>% 
    filter(!is.na(avg_subtype)) %>% 
    count(avg_subtype) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_subtype = str_to_title(avg_subtype))
avg_by_subtype_tab

# avg by subtype plot
avg_by_subtype_tab %>% 
    mutate(avg_subtype = if_else(pct < 0.01, "Other", avg_subtype)) %>% 
    group_by(avg_subtype) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    ggplot(aes(x = avg_subtype, y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Averaging Method Subtype") +
    ylab("Count") +
    ylim(0, calc_upper_y_lim(max(avg_by_subtype_tab$n))) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste("Averaging method by subtype. Data are expressed as counts and percentages. N = ",
    #           n_avg_subtype, ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    theme(axis.text.x = element_text(angle=45, hjust=1))

# avg by type and subtype
avg_by_type_subtype_tab <- merge_df %>% 
    filter(!is.na(avg_subtype) | !is.na(avg_type)) %>% 
    count(avg_type, avg_subtype) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_type_subtype = paste(avg_type, "-", avg_subtype, sep = ""),
           avg_type_subtype = str_to_title(avg_type_subtype)) %>% 
    arrange(desc(pct))
avg_by_type_subtype_tab

# avg by full avg method plot
avg_by_full_method_tab <- merge_df %>% 
    filter(!is.na(avg_type)) %>% 
    group_by(avg_type, axvg_subtype, avg_amount, avg_mos, avg_mean_type) %>% 
    summarize(n = n()) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n))
avg_by_full_method_tab

avg_by_full_method_plot <- avg_by_full_method_tab %>% 
    mutate(avg_procedure = paste(
        avg_type, avg_subtype, avg_amount, avg_mos, avg_mean_type, sep = "-"),
        avg_procedure = if_else(pct < 0.01, "Other", str_to_title(avg_procedure))) %>% 
    group_by(avg_procedure) %>% 
    summarize(n = sum(n)) %>% 
    ungroup() %>% 
    mutate(pct = prop.table(n)) %>% 
    mutate(avg_procedure = str_remove(avg_procedure, "-Mean-Whole")) %>% 
    ggplot(aes(x = reorder(avg_procedure, -n), y = n)) +
    geom_col() +
    geom_text(aes(label = scales::percent(pct)), vjust = -0.5) +
    geom_text(aes(label = n), vjust = -2) +
    xlab("Averaging Procedure") +
    ylab("Count") +
    ylim(0, calc_upper_y_lim(max(avg_by_full_method_tab$n)) + 50) +
    theme_minimal() +
    # labs(caption = str_wrap(
    #     paste(
    #         "Prevalence of averaging method by full procedure. 
    #         Data are expressed as counts and percentages. ",
    #         sum(avg_by_full_method_tab$n), ".", sep = ""), width = 100)) +
    # theme(plot.caption = element_text(hjust=0)) +
    theme(axis.text.x = element_text(angle=90, hjust=1))
avg_by_full_method_plot
