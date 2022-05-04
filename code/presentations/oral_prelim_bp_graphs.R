library(gasExchangeR)
library(tidyverse)
library(devtools)
library(lubridate)

df_raw <- read_csv("data/presentations/37818_vo2max_unavg.csv",
                   show_col_types = FALSE)
df_unavg <- df_raw %>%
    rename_with(.fn = tolower) %>%
    rename(vo2_rel = vo2...4,
           vo2_abs = vo2...5,
           ve = `ve btps`,
           vt = `vt btps`) %>%
    select(time, speed, grade, vo2_rel, vo2_abs, vco2, ve) %>%
    trim_pre_post(intensity_col = "grade",
                  pre_ex_intensity = 300.1,
                  post_ex_intensity = 300.1) %>%
    mutate(ve_vo2 = ve / (vo2_abs/1000),
           ve_vco2 = ve / (vco2/1000),
           time = as.numeric(ms(str_remove(as.character(time), ":00"))))

df_avg <- avg_exercise_test(df_unavg,
                            type = "breath",
                            subtype = "rolling",
                            roll_window = 15,
                            roll_trim = 2,
                            time_col = "time")

ggplot(data = df_unavg, aes(x = vco2, y = ve)) +
    geom_point() +
    geom_point(data = df_avg, aes(x = vco2, y = ve), color = "red")

ggplot(data = df_unavg, aes(x = as.numeric(time), y = ve)) +
    geom_point() +
    geom_point(data = df_avg, aes(x = time, y = ve), color = "red")

ggplot(data = df_unavg, aes(x = as.numeric(time), y = vo2_abs)) +
    geom_point() +
    geom_point(data = df_avg, aes(x = time, y = vo2_abs), color = "red")


################################# JM

jm_dat <- breakpoint(.data = df_avg,
           x_vt1 = "vo2_abs",
           y_vt1 = "vco2",
           algorithm_vt1 = "jm",
           x_vt2 = "vco2",
           y_vt2 = "ve",
           algorithm_vt2 = "jm",
           vo2 = "vo2_abs",
           bps = "both")

jm_plot <- ggplot(data = df_avg, aes(x = vo2_abs, y = vco2)) +
    geom_point(color = "blue", alpha = 0.5) +
    geom_vline(xintercept = jm_dat$vt1_dat$breakpoint_data$vo2_abs) +
    geom_line(data = jm_dat$vt1_dat$fitted_vals, aes(x = vo2_abs, y = vco2)) +
    theme_bw() +
    xlab("Absolute VO2 (mL/min)") +
    ylab("VCO2 (mL/min)") +
    xlim(750, 4000) +
    ylim(750, 4000)
jm_plot

################################# Orr

orr_dat <- breakpoint(.data = df_avg,
                     x_vt1 = "vo2_abs",
                     y_vt1 = "vco2",
                     algorithm_vt1 = "orr",
                     x_vt2 = "vco2",
                     y_vt2 = "ve",
                     algorithm_vt2 = "jm",
                     vo2 = "vo2_abs",
                     bps = "both")

orr_plot_data <- tibble(vo2_abs = seq(min(df_avg$vo2_abs),
                                      max(df_avg$vo2_abs),
                                      by = 1),
                    vco2_left = seq(min(df_avg$vo2_abs),
                                    max(df_avg$vo2_abs),
                                    by = 1) * orr_dat$vt1_dat$lm_left$coefficients[2] +
                        orr_dat$vt1_dat$lm_left$coefficients[1],
                    vco2_right = seq(min(df_avg$vo2_abs),
                                     max(df_avg$vo2_abs),
                                     by = 1) * orr_dat$vt1_dat$lm_right$coefficients[2] +
                        orr_dat$vt1_dat$lm_right$coefficients[1])

orr_plot <- ggplot(data = df_avg, aes(x = vo2_abs, y = vco2)) +
    geom_point(color = "blue", alpha = 0.5) +
    geom_line(data = orr_plot_data, aes(x = vo2_abs, y = vco2_left)) +
    geom_line(data = orr_plot_data, aes(x = vo2_abs, y = vco2_right)) +
    geom_vline(xintercept = orr_dat$vt1_dat$breakpoint_data$vo2_abs) +
    theme_bw() +
    ylim(0, max(df_avg$vco2)) +
    geom_vline(xintercept = intersection_point(orr_dat$vt1_dat$lm_left,
                                               orr_dat$vt1_dat$lm_right)["x"],
               color = "green") +
    xlab("Absolute VO2 (mL/min)") +
    ylab("VCO2 (mL/min)") +
    xlim(750, 4000) +
    ylim(750, 4000)
    
orr_plot
################################# V-slope

v_slope_dat <- breakpoint(.data = df_avg,
                      x_vt1 = "vo2_abs",
                      y_vt1 = "vco2",
                      algorithm_vt1 = "v-slope",
                      x_vt2 = "vco2",
                      y_vt2 = "ve",
                      algorithm_vt2 = "jm",
                      vo2 = "vo2_abs",
                      bps = "both")

v_slope_plot_data <- tibble(vo2_abs = seq(min(df_avg$vo2_abs),
                                          max(df_avg$vo2_abs),
                                          by = 1),
                        vco2_left = seq(min(df_avg$vo2_abs),
                                        max(df_avg$vo2_abs),
                                        by = 1) * v_slope_dat$vt1_dat$lm_left$coefficients[2] +
                            v_slope_dat$vt1_dat$lm_left$coefficients[1],
                        vco2_right = seq(min(df_avg$vo2_abs),
                                         max(df_avg$vo2_abs),
                                         by = 1) * v_slope_dat$vt1_dat$lm_right$coefficients[2] +
                            v_slope_dat$vt1_dat$lm_right$coefficients[1],
                        vco2_simple = seq(min(df_avg$vo2_abs),
                                          max(df_avg$vo2_abs),
                                          by = 1) * v_slope_dat$vt1_dat$lm_simple$coefficients[2] +
                            v_slope_dat$vt1_dat$lm_simple$coefficients[1])

recip_slope <- (-1 / v_slope_dat$vt1_dat$lm_simple$coefficients[2])

lr_intersect <- intersection_point(v_slope_dat$vt1_dat$lm_left,
                                   v_slope_dat$vt1_dat$lm_right)

# y = mx + b
# b = y - mx
# b = lr_intersect["y"] - recip_slope*lr_intersect["x"]

b_recip <- recip_slope * (-1) * lr_intersect["x"] + lr_intersect["y"]

x_simple_recip <- (b_recip - v_slope_dat$vt1_dat$lm_simple$coefficients[1]) /
    (v_slope_dat$vt1_dat$lm_simple$coefficients[2] - (-1 / v_slope_dat$vt1_dat$lm_simple$coefficients[2]))

y_simple_recip <- v_slope_dat$vt1_dat$lm_simple$coefficients[1] +
    v_slope_dat$vt1_dat$lm_simple$coefficients[2]*x_simple_recip

dist_line <- tibble(vo2_abs = c(x_simple_recip,
                                lr_intersect["x"]),
                    vco2 = c(y_simple_recip,
                             lr_intersect["y"]))

d <- sqrt((x_simple_recip - lr_intersect["x"])^2 +
              (y_simple_recip - lr_intersect["y"])^2)
d

v_slope_plot <- ggplot(data = df_avg, aes(x = vo2_abs, y = vco2)) +
    geom_point(color = "blue", alpha = 0.5) +
    geom_line(data = v_slope_plot_data, aes(x = vo2_abs, y = vco2_left)) +
    geom_line(data = v_slope_plot_data, aes(x = vo2_abs, y = vco2_right)) +
    geom_vline(xintercept = v_slope_dat$vt1_dat$breakpoint_data$vo2_abs) +
    theme_bw() +
    geom_vline(xintercept = intersection_point(
        v_slope_dat$vt1_dat$lm_left,
        v_slope_dat$vt1_dat$lm_right)["x"],
               color = "green") +
    geom_line(data = v_slope_plot_data, aes(x = vo2_abs, y = vco2_simple)) +
    geom_line(data = dist_line, aes(x = vo2_abs, y = vco2), color = "red") +
    xlim(1500, 4000) +
    ylim(1500, 4000) +
    xlab("Absolute VO2 (mL/min)") +
    ylab("VCO2 (mL/min)")
    
v_slope_plot

bp_tib <- tibble(vo2_abs = c(jm_dat$vt1_dat$breakpoint_data$vo2_abs,
                             orr_dat$vt1_dat$breakpoint_data$vo2_abs,
                             v_slope_dat$vt1_dat$breakpoint_data$vo2_abs),
                 vco2 = c(jm_dat$vt1_dat$breakpoint_data$vco2,
                          orr_dat$vt1_dat$breakpoint_data$vco2,
                          v_slope_dat$vt1_dat$breakpoint_data$vco2),
                 algorithm = c("jm", "orr", "v-slope"))
bp_tib
###### Combined plot

comb_plot <- ggplot(data = df_avg, aes(x = vo2_abs, y = vco2)) + 
    geom_point(color = "blue", alpha = 0.5) +
    theme_bw() +
    geom_vline(data = bp_tib, aes(xintercept = vo2_abs, color = algorithm)) +
    xlim(1500, 4000) +
    ylim(1500, 4000) +
    xlab("Absolute VO2 (mL/min)") +
    ylab("VCO2 (mL/min)")
comb_plot

##### Dmax

dmax_dat <- breakpoint(.data = df_avg,
                          x_vt1 = "vo2_abs",
                          y_vt1 = "vco2",
                          algorithm_vt1 = "dmax",
                          x_vt2 = "vco2",
                          y_vt2 = "ve",
                          algorithm_vt2 = "jm",
                          vo2 = "vo2_abs",
                          bps = "both")

dmax_plot_data <- tibble(vo2_abs = seq(min(df_avg$vo2_abs),
                                          max(df_avg$vo2_abs),
                                          by = 1)) %>% 
    mutate(vco2_left = vo2_abs * dmax_dat$vt1_dat$lm_left$coefficients[2] +
               dmax_dat$vt1_dat$lm_left$coefficients[1],
           vco2_right = vo2_abs * dmax_dat$vt1_dat$lm_right$coefficients[2] +
               dmax_dat$vt1_dat$lm_right$coefficients[1],
           vco2_poly = vo2_abs * dmax_dat$vt1_dat$poly_model$coefficients[2] +
               vo2_abs^2 * dmax_dat$vt1_dat$poly_model$coefficients[3] +
               vo2_abs^3 * dmax_dat$vt1_dat$poly_model$coefficients[4] +
               dmax_dat$vt1_dat$poly_model$coefficients[1])

y_hat_min <- min(dmax_dat$vt1_dat$poly_model$fitted.values)
y_hat_max <- max(dmax_dat$vt1_dat$poly_model$fitted.values)

xmin = min(df_avg$vo2_abs, na.rm = T)
xmax = max(df_avg$vo2_abs, na.rm = T)

end_point_line <- tibble(vo2_abs = c(xmin, xmax),
                         vco2 = c(y_hat_min, y_hat_max))

dmax_plot <- ggplot(data = df_avg, aes(x = vo2_abs, y = vco2)) +
    geom_point(color = "blue", alpha = 0.5) +
    geom_line(data = dmax_plot_data, aes(x = vo2_abs, y = vco2_left)) +
    geom_line(data = dmax_plot_data, aes(x = vo2_abs, y = vco2_right)) +
    geom_line(data = dmax_plot_data, aes(x = vo2_abs, y = vco2_poly)) +
    geom_line(data = end_point_line, aes(x = vo2_abs, y = vco2))
    # geom_vline(xintercept = dmax_dat$vt1_dat$breakpoint_data$vo2_abs) +
    theme_bw() +
    geo
    geom_vline(xintercept = intersection_point(
        dmax_dat$vt1_dat$lm_left,
        dmax_dat$vt1_dat$lm_right)["x"],
        color = "green") +
    geom_line(data = dmax_plot_data, aes(x = vo2_abs, y = vco2_simple)) +
    geom_line(data = dist_line, aes(x = vo2_abs, y = vco2), color = "red") +
    xlim(1000, 4600) +
    ylim(1000, 4600)

