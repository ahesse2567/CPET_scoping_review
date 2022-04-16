library(gasExchangeR)
library(tidyverse)
library(stringr)
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

df_unavg_interp <- interpolate(df_unavg,
            time_col = "time",
            method = "linear",
            every_s = 1)


ggplot(data = df_unavg_interp, aes(x = time, y = vo2_abs)) +
    geom_point() +
    theme_bw()
    geom_point(data = df_unavg_interp, aes(x = time, y = vo2_abs), color = "red")
       