library(tidyverse)
library(lubridate)

file_list = list.files("data/raw/auto_vts_by_avg/", full.names = TRUE)

ids <- str_extract(file_list, "\\d{3}")
avg_method <- str_extract(file_list, "(?<=_\\d{3}_)[a-zA-Z0-9_]*")

data_list <- vector(mod = "list", length = length(file_list))

for(i in 1:length(file_list)) {
    fname <- file_list[i]
    id <- str_extract(fname, "\\d{3}")
    avg_method <- str_extract(fname, "(?<=_\\d{3}_)[a-zA-Z0-9_]*")
    test <- read_delim(fname, show_col_types = FALSE)
    time <- test[which(test["ABC"] == "Time (min)"),
                            c("AT", "RC", "V02 Max")] %>% 
        mutate(across(everything(), ms)) %>% 
        mutate(across(everything(), as.numeric))
    vo2_rel <- test[which(test["ABC"] == "VO2 (mL/kg/min)"), c("AT", "RC", "V02 Max")]
    vo2_abs <- test[which(test["ABC"] == "VO2 (L/min)"), c("AT", "RC", "V02 Max")]
    vco2 <- test[which(test["ABC"] == "VCO2 (L/min)"), c("AT", "RC", "V02 Max")]
    ve <- test[which(test["ABC"] == "VE BTPS (L/min)"), c("AT", "RC", "V02 Max")]
    vars <- tibble(var = c("time", "vo2_rel", "vo2_abs", "vco2", "ve"))
    data_list[[i]] <- rbind(time, vo2_rel, vo2_abs, vco2, ve) %>% 
        cbind(id, avg_method, vars, .)
}

auto_vt_long <- bind_rows(data_list) %>% 
    as_tibble() %>% 
    mutate(across(c("AT", "RC", "V02 Max"), as.numeric)) %>% 
    mutate(across(c(avg_method, var), as.factor))

auto_vt_wide <- auto_vt_long %>% 
    pivot_wider(names_from = "var", values_from = c("AT", "RC", "V02 Max"))

write_csv(auto_vt_wide, "data/processed/auto_vt_wide.csv")

