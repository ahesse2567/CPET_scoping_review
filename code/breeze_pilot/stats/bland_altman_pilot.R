library(tidyverse)
library(blandr)
library(BlandAltmanLeh)
library(gridExtra)

auto_vt_wide <- read_csv("data/breeze_pilot/auto_vt_wide.csv",
                         show_col_types = FALSE)

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

library(car)
leveneTest(AT_vo2_abs ~ avg_method, data = auto_vt_wide)

library(rstatix)
anova_res <- anova_test(data = auto_vt_wide, dv = AT_vo2_abs, wid = id, within = avg_method)
get_anova_table(anova_res)

pwc <- auto_vt_wide %>%
    pairwise_t_test(
        AT_vo2_abs ~ avg_method, paired = TRUE,
        p.adjust.method = "BH"
    )
pwc
library(effectsize)
pwc %>% 
    mutate(eta_sq = t_to_d(t = statistic, df_error = df, paired = TRUE))

library(emmeans)
pairwise_comps <- emmeans(mod_AT_vo2_abs, ~ avg_method, adjust = "BH")
summary(pairwise_comps)

mod_AT_time <- lm(AT_time ~ 1 + avg_method, data = auto_vt_wide)
anova(mod_AT_time)
summary(mod_AT_time)

pairwise.t.test(auto_vt_wide$AT_time,
                g = auto_vt_wide$avg_method,
                paired = TRUE,
                p.adjust.method = "BH")



ggplot(data = auto_vt_wide, aes(x = AT_vo2_abs)) +
    geom_density(aes(color = avg_method)) +
    theme_bw() +
    xlab("Averaging method") +
    ylab("Absolute VO2 (L/min) at VT1")

ggplot(data = auto_vt_wide, aes(x = avg_method, y = AT_vo2_abs)) +
    geom_boxplot(aes(fill = avg_method)) +
    theme_bw() +
    xlab("Averaging method") +
    ylab("Absolute VO2 (L/min) at VT1")

ggplot(data = auto_vt_wide, aes(x = AT_time)) +
    geom_density(aes(color = avg_method)) +
    theme_bw()

ggplot(data = auto_vt_wide, aes(x = avg_method, y = AT_time)) +
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
var_name <- "AT_vo2_abs"

#### VO2 at VT1 agreement

for(i in 1:nrow(combinations)) {
    ba_plots[[i]] <- blandr.draw(auto_vt_wide[auto_vt_wide[["avg_method"]] ==
                                            combinations[["method1"]][i],
                             var_name] %>% pull(),
                auto_vt_wide[auto_vt_wide[["avg_method"]] == combinations[["method2"]][i],
                             var_name] %>% pull()) +
        theme_bw() +
        ggtitle(paste0(combinations[["method1"]][i],"\n",
                       " and ",
                       combinations[["method2"]][i])) +
        xlab(paste("Mean of VO2 (L/min) at VT1")) +
        ylab(paste("Difference in VO2 (L/min) at VT1")) +
        theme(plot.title = element_text(hjust = 0.5)) +
        geom_hline(yintercept = 0.091, color = "red") +
        geom_hline(yintercept = -1*0.091, color = "red")
}

do.call("grid.arrange", c(ba_plots, ncol = 5))

# for(i in seq_along(1:10)) {
#     print(ba_plots[[i]])
# }

png("data/breeze_pilot/bland_altman_pilot_AT_vo2_abs.png",
     width = 10,
     height = 5.5,
     res = 1200,
     units = "in")
do.call("grid.arrange", c(ba_plots, ncol = 5))
dev.off()

comb_no_unavg <- combinations %>% 
    filter(method2 != "unavg")

ba_stats_at_vo2 <- vector(mode = "list", length = nrow(comb_no_unavg))
var_name <- "AT_vo2_abs"

for(i in 1:nrow(comb_no_unavg)) {
    ba_stats_at_vo2[[i]] <- blandr.statistics(
        auto_vt_wide[auto_vt_wide[["avg_method"]] ==
                         comb_no_unavg[["method1"]][i],var_name] %>% pull(),
        auto_vt_wide[auto_vt_wide[["avg_method"]] ==
                         comb_no_unavg[["method2"]][i],var_name] %>% pull())
}

loa_stats <- numeric(length = length(ba_stats_at_vo2))

for(i in 1:length(loa_stats)) {
    loa_stats[i] <- (ba_stats_at_vo2[[i]]$upperLOA - ba_stats_at_vo2[[i]]$lowerLOA) / 2
}

summary(loa_stats)
0.3148 / 0.091

###### Time at VT1
ba_time_vt1 <- vector(mode = "list", length = nrow(combinations))
var_name <- "AT_time"

for(i in 1:nrow(combinations)) {
    ba_time_vt1[[i]] <- blandr.draw(auto_vt_wide[auto_vt_wide[["avg_method"]] ==
                                                  combinations[["method1"]][i],
                                              var_name] %>% pull() / 60,
                                 auto_vt_wide[auto_vt_wide[["avg_method"]] == combinations[["method2"]][i],
                                              var_name] %>% pull() / 60) +
        theme_bw() +
        ggtitle(paste0(combinations[["method1"]][i],"\n",
                       " and ",
                       combinations[["method2"]][i])) +
        xlab(paste("Mean of time (min) at VT1")) +
        ylab(paste("Difference in time (min) at VT1")) +
        theme(plot.title = element_text(hjust = 0.5)) +
        geom_hline(yintercept = 1, color = "red") +
        geom_hline(yintercept = -1, color = "red")
}

do.call("grid.arrange", c(ba_time_vt1, ncol = 5))

# for(i in seq_along(1:10)) {
#     print(ba_time_vt1[[i]])
# }

png("data/breeze_pilot/bland_altman_pilot_time_AT.png",
    width = 10,
    height = 5.5,
    res = 1200,
    units = "in")
do.call("grid.arrange", c(ba_time_vt1, ncol = 5))
dev.off()


ba_stats_AT_time <- vector(mode = "list", length = nrow(comb_no_unavg))
var_name <- "AT_time"

for(i in 1:nrow(comb_no_unavg)) {
    ba_stats_AT_time[[i]] <- blandr.statistics(
        auto_vt_wide[auto_vt_wide[["avg_method"]] ==
                         comb_no_unavg[["method1"]][i],var_name] %>% pull(),
        auto_vt_wide[auto_vt_wide[["avg_method"]] ==
                         comb_no_unavg[["method2"]][i],var_name] %>% pull())
}

loa_stats_AT_time <- numeric(length = length(ba_stats_AT_time))

for(i in 1:length(loa_stats_AT_time)) {
    loa_stats_AT_time[i] <- (ba_stats_AT_time[[i]]$upperLOA - 
                                 ba_stats_AT_time[[i]]$lowerLOA) / 2
}

summary(loa_stats_AT_time) / 60
(summary(loa_stats_AT_time) / 60 - 1)*60


