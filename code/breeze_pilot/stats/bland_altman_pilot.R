library(tidyverse)
library(blandr)
library(BlandAltmanLeh)
library(gridExtra)

auto_vt_wide <- read_csv("data/breeze_pilot/auto_vt_wide.csv", )

AT_vo2_abs <- auto_vt_wide %>% 
    select(id, avg_method, AT_vo2_abs) %>% 
    pivot_wider(names_from = avg_method,
                values_from = AT_vo2_abs) %>% 
    select(-id)

cor(AT_vo2_abs) # correlations are pretty good, but BA plots are better

mod_AT_vo2_abs <- lm(AT_vo2_abs ~ 1 + avg_method, data = auto_vt_wide)
anova(mod_AT_vo2_abs)
summary(mod_AT_vo2_abs)

pairwise.t.test(auto_vt_wide$AT_vo2_abs,
                g = auto_vt_wide$avg_method,
                paired = TRUE,
                p.adjust.method = "BH")

ggplot(data = auto_vt_wide, aes(x = AT_vo2_abs)) +
    geom_density(aes(color = avg_method)) +
    theme_bw()

ggplot(data = auto_vt_wide, aes(x = avg_method, y = AT_vo2_abs)) +
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
no_unavg <- auto_vt_wide %>% 
    filter(avg_method != "unavg")

auto_vt_wide %>% 
    filter(avg_method != "unavg") %>% 
    select(AT_vo2_abs) %>% 
    summary()

t.test(no_unavg$AT_vo2_abs, mu = 2.5)

vo2_refs <- c("ss1" = 1.35, "ss2" = 2.5, "vo2max" = 4.53)
accum_err <- c("ss1" = 0.055, "ss2" = 0.091, "vo2max" = 0.18)
vo2_err <- tibble(vo2_refs, accum_err)

vo2_err_mod <- lm(accum_err ~ 1 + vo2_refs, data = vo2_err)
summary(vo2_err_mod)
err <- vo2_err_mod$coefficients[1] + 
    vo2_err_mod$coefficients[2]*mean(auto_vt_wide$AT_vo2_abs)

ba_plots <- vector(mode = "list", length = nrow(combinations))

for(i in 1:nrow(combinations)) {
    ba_plots[[i]] <- blandr.draw(auto_vt_wide[auto_vt_wide[["avg_method"]] ==
                                            combinations[["method1"]][i],
                             "AT_vo2_abs"] %>% pull(),
                auto_vt_wide[auto_vt_wide[["avg_method"]] == combinations[["method2"]][i],
                             "AT_vo2_abs"] %>% pull()) +
        theme_bw() +
        ggtitle(paste0("Agreement between\n",
                       combinations[["method1"]][i],
                       " and ",
                       combinations[["method2"]][i])) +
        xlab("Mean of VO2 at VT1") +
        ylab("Difference in VO2 at VT1") +
        theme(plot.title = element_text(hjust = 0.5)) +
        geom_hline(yintercept = err, color = "red") +
        geom_hline(yintercept = -1*err, color = "red")
}

do.call("grid.arrange", c(ba_plots, ncol = 5))

# for(i in seq_along(1:10)) {
#     print(ba_plots[[i]])
# }

tiff("data/breeze_pilot/bland_altman_pilot.png",
     width = 1174,
     height = 591,
     res = 1200,
     units = "px")
do.call("grid.arrange", c(ba_plots, ncol = 5))
dev.off()


comb_no_unavg <- combinations %>% 
    filter(method2 != "unavg")

ba_stats <- vector(mode = "list", length = nrow(comb_no_unavg))

for(i in 1:nrow(comb_no_unavg)) {
    ba_stats[[i]] <- blandr.statistics(
        auto_vt_wide[auto_vt_wide[["avg_method"]] ==
                         comb_no_unavg[["method1"]][i],"AT_vo2_abs"] %>% pull(),
        auto_vt_wide[auto_vt_wide[["avg_method"]] ==
                         comb_no_unavg[["method2"]][i],"AT_vo2_abs"] %>% pull())
}

loa_stats <- numeric(length = length(ba_stats))

for(i in 1:length(loa_stats)) {
    loa_stats[i] <- (ba_stats[[i]]$upperLOA - ba_stats[[i]]$lowerLOA) / 2
}

summary(loa_stats)
