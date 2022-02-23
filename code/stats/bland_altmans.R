library(tidyverse)
library(blandr)
library(BlandAltmanLeh)

auto_vt_wide <- read_csv("data/processed/auto_vt_wide.csv", )

auto_vt_wide

mod_at_vo2_rel <- lm(AT_vo2_rel ~ 1 + avg_method, data = auto_vt_wide)
anova(mod_at_vo2_rel)
summary(mod_at_vo2_rel)

pairwise.t.test(auto_vt_wide$AT_vo2_rel,
                g = auto_vt_wide$avg_method,
                paired = TRUE,
                p.adjust.method = "BH")

ggplot(data = auto_vt_wide, aes(x = AT_vo2_rel)) +
    geom_density(aes(color = avg_method)) +
    theme_bw()

ggplot(data = auto_vt_wide, aes(x = avg_method, y = AT_vo2_rel)) +
    geom_boxplot(aes(fill = avg_method)) +
    theme_bw()

methods <- unique(auto_vt_wide["avg_method"]) %>% 
    pull()

methods

combinations <- combn(methods, 2) %>% 
    t() %>% 
    as_tibble() %>% 
    rename(method1 = V1, method2 = V2) %>% 
    mutate(across(everything(), as.factor))
combinations

auto_vt_wide[auto_vt_wide[["avg_method"]] == combinations$method1[1], 3] %>% pull()

ba_plots <- vector(mode = "list", length = nrow(combinations))

for(i in 1:nrow(combinations)) {
    ba_plots[[i]] <- blandr.draw(auto_vt_wide[auto_vt_wide[["avg_method"]] ==
                                            combinations[["method1"]][i],
                             "RC_vo2_rel"] %>% pull(),
                auto_vt_wide[auto_vt_wide[["avg_method"]] == combinations[["method2"]][i],
                             "RC_vo2_rel"] %>% pull()) +
        theme_bw() +
        ggtitle(paste0("Bland-Altman plot for comparison of ",
                       combinations[["method1"]][i],
                       " and ",
                       combinations[["method2"]][i]))
}


for(i in seq_along(1:10)) {
    print(ba_plots[[i]])
}

ggplot(data = auto_vt_wide, aes(x = avg_method, y = RC_vo2_rel)) +
    geom_boxplot(aes(fill = avg_method)) +
    theme_bw()


auto_vt_wide[auto_vt_wide["avg_method"] == combinations$method1[1],
                  "AT_vo2_rel"] %>% pull()

auto_vt_wide[auto_vt_wide["avg_method"] == methods[2], "AT_vo2_rel"] %>% pull()

bland.al

ba_stats <- blandr.statistics(a, b)

ba_stats$upperLOA - ba_stats$bias
ba_stats$lowerLOA - ba_stats$bias

blandr.draw(a, b)
