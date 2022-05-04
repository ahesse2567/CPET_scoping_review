library(gasExchangeR)
library(tidyverse)
library(gridExtra)
library(lubridate)

df_raw <- read_csv("data/presentations/37818_vo2max_unavg.csv")
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

br_5_roll <- avg_exercise_test(df_unavg,
                                type = "breath",
                                subtype = "rolling",
                                roll_window = 5)

br_10_roll <- avg_exercise_test(df_unavg,
                               type = "breath",
                               subtype = "rolling",
                               roll_window = 10)

br_15_roll <- avg_exercise_test(df_unavg,
                                type = "breath",
                                subtype = "rolling",
                                roll_window = 15)

br_20_roll <- avg_exercise_test(df_unavg,
                                type = "breath",
                                subtype = "rolling",
                                roll_window = 20)

br_25_roll <- avg_exercise_test(df_unavg,
                                type = "breath",
                                subtype = "rolling",
                                roll_window = 25)

plot_unavg <- ggplot(data = df_unavg, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("Unaveraged") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_unavg

plot_5roll <- ggplot(data = br_5_roll, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("5 breath rolling average") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_5roll

plot_10roll <- ggplot(data = br_10_roll, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("10 breath rolling average") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_10roll

plot_15roll <- ggplot(data = br_15_roll, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("15 breath rolling average") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_15roll

plot_20roll <- ggplot(data = br_20_roll, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("20 breath rolling average") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_20roll

plot_25roll <- ggplot(data = br_25_roll, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("25 breath rolling average") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_25roll

grid.arrange(plot_unavg, plot_5roll, plot_10roll,
             plot_15roll, plot_20roll, plot_25roll, ncol = 3)

######## Time bin

time_10s_bin <- avg_exercise_test(df_unavg,
                                  type = "time",
                                  subtype = "bin",
                                  bin_w = 10)

time_15s_bin <- avg_exercise_test(df_unavg,
                            type = "time",
                            subtype = "bin",
                            bin_w = 15)

time_20s_bin <- avg_exercise_test(df_unavg,
                                  type = "time",
                                  subtype = "bin",
                                  bin_w = 20)

time_30s_bin <- avg_exercise_test(df_unavg,
                                  type = "time",
                                  subtype = "bin",
                                  bin_w = 30)

time_60s_bin <- avg_exercise_test(df_unavg,
                                  type = "time",
                                  subtype = "bin",
                                  bin_w = 60)
plot_bin_unavg <- ggplot(data = df_unavg, aes(x = time, y = vo2_abs)) +
    geom_point(alpha = 0.5) +
    geom_line() +
    theme_bw() +
    ggtitle("Unaveraged") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_bin_unavg

plot_bin_10s <- ggplot(data = time_10s_bin, aes(x = time, y = vo2_abs)) +
    geom_point(alpha = 0.5) +
    geom_line() +
    theme_bw() +
    ggtitle("10 second bins") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_bin_10s

plot_bin_15s <- ggplot(data = time_15s_bin, aes(x = time, y = vo2_abs)) +
    geom_point(alpha = 0.5) +
    geom_line() +
    theme_bw() +
    ggtitle("15 second bins") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_bin_15s

plot_bin_20s <- ggplot(data = time_20s_bin, aes(x = time, y = vo2_abs)) +
    geom_point(alpha = 0.5) +
    geom_line() +
    theme_bw() +
    ggtitle("20 second bins") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_bin_20s

plot_bin_30s <- ggplot(data = time_30s_bin, aes(x = time, y = vo2_abs)) +
    geom_point(alpha = 0.5) +
    geom_line() +
    theme_bw() +
    ggtitle("30 second bins") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_bin_30s

plot_bin_60s <- ggplot(data = time_60s_bin, aes(x = time, y = vo2_abs)) +
    geom_point(alpha = 0.5) +
    geom_line() +
    theme_bw() +
    ggtitle("60 second bins") +
    xlim(c(0, 900)) +
    ylim(500, 4500)
plot_bin_60s

grid.arrange(plot_bin_unavg,
             plot_bin_10s,
             plot_bin_15s,
             plot_bin_20s,
             plot_bin_30s,
             plot_bin_60s,
             ncol = 3)

########## Digital filtering

butter0.01 <- avg_exercise_test(df_unavg,
                                type = "digital",
                                cutoff = 0.01)

butter0.03 <- avg_exercise_test(df_unavg,
                                type = "digital",
                                cutoff = 0.03)

butter0.04 <- avg_exercise_test(df_unavg,
                                type = "digital",
                                cutoff = 0.04)

butter0.08 <- avg_exercise_test(df_unavg,
                                type = "digital",
                                cutoff = 0.08)

butter0.15 <- avg_exercise_test(df_unavg,
                                type = "digital",
                                cutoff = 0.15)

plot_butter_unavg <- ggplot(data = df_unavg, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("Unaveraged") +
    xlim(c(0, 900)) +
    ylim(0, 4500)
plot_butter_unavg

plot_butter0.01 <- ggplot(data = butter0.01, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("0.01 Hz Cutoff") +
    xlim(c(0, 900)) +
    ylim(0, 4500)
plot_butter0.01

plot_butter0.03 <- ggplot(data = butter0.03, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("0.03 Hz Cutoff") +
    xlim(c(0, 900)) +
    ylim(0, 4500)
plot_butter0.03

plot_butter0.04 <- ggplot(data = butter0.04, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("0.04 Hz Cutoff") +
    xlim(c(0, 900)) +
    ylim(0, 4500)
plot_butter0.04

plot_butter0.08 <- ggplot(data = butter0.08, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("0.08 Hz Cutoff") +
    xlim(c(0, 900)) +
    ylim(0, 4500)
plot_butter0.08

plot_butter0.15 <- ggplot(data = butter0.15, aes(x = time, y = vo2_abs)) +
    geom_line() +
    theme_bw() +
    ggtitle("0.15 Hz Cutoff") +
    xlim(c(0, 900)) +
    ylim(0, 4500)
plot_butter0.15

grid.arrange(plot_butter_unavg,
             plot_butter0.15,
             plot_butter0.08,
             plot_butter0.04,
             plot_butter0.03,
             plot_butter0.01, ncol = 3)
