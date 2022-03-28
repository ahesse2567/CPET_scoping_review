library(tidyverse)
library(blandr)
library(BlandAltmanLeh)
library(gridExtra)

auto_vt_wide <- read_csv("data/processed/auto_vt_wide.csv", )

AT_vo2_rel <- auto_vt_wide %>% 
    select(id, avg_method, AT_vo2_rel) %>% 
    pivot_wider(names_from = avg_method,
                values_from = AT_vo2_rel) %>% 
    select(-id)

cor(AT_vo2_rel) # correlations are pretty good, but BA plots are better

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
        ggtitle(paste0("Agreement between\n",
                       combinations[["method1"]][i],
                       " and ",
                       combinations[["method2"]][i])) +
        xlab("Mean of VO2 at VT1") +
        ylab("Difference in VO2 at VT1") +
        theme(plot.title = element_text(hjust = 0.5)) +
        geom_hline(yintercept = 2, color = "red") +
        geom_hline(yintercept = -2, color = "red")
}


# for(i in seq_along(1:10)) {
#     print(ba_plots[[i]])
# }

do.call("grid.arrange", c(ba_plots, ncol = 5))

tiff("bland_altman_pilot.png",
     width = 1174,
     height = 591,
     res = 1200,
     units = "px")
do.call("grid.arrange", c(ba_plots, ncol = 5))
dev.off()
