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
           time = as.numeric(ms(str_remove(as.character(time), ":00"))),
           time = time - time[1])

#### unaveraged

head(df_unavg, 16)
write_clip(df_unavg[1:16, c("time", "vo2_abs")])

write_clip(map_chr(df_unavg$time[1:16], function(x) sprintf("%02d:%02d",x%/%60,x%%60)))

### 5-breath bin average

br_bin5 <- avg_exercise_test(df_unavg, type = "breath", subtype = "bin",
                             bin_w = 5)
head(br_bin5, 15)
write_clip(br_bin5[1:3, c("time", "vo2_abs")])

### 15-second time-bin average

time_bin15 <- avg_exercise_test(df_unavg, type = "time", subtype = "bin",
                                bin_w = 15)
head(time_bin15)
write_clip(time_bin15[1:3, c("time", "vo2_abs")])


### 7-breath time-bin average

breath_roll7 <- avg_exercise_test(df_unavg, type = "breath",
                                  subtype = "rolling", roll_window = 7)

head(breath_roll7)
write_clip(breath_roll7[1:12, c("time", "vo2_abs")])

