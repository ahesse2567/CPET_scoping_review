library(tidyverse)

A <- rep("A", 50)
B <- rep("B", 30)
C <- rep("C", 20)

choices <- tibble(choice = c(A, B, C))

reps <- 1000

freq_a <- numeric(length = reps)
freq_b <- numeric(length = reps)
freq_c <- numeric(length = reps)

for(i in 1:reps) {
    rand_choices <- sample(choices$choice, size = nrow(choices), replace = TRUE)
    count_summary <- plyr::count(rand_choices)
    freq_a[i] <- count_summary[1, "freq"]
    freq_b[i] <- count_summary[2, "freq"]
    freq_c[i] <- count_summary[3, "freq"]
}

res <- tibble(A = freq_a, B = freq_b, C = freq_c)
res_long <- res %>% 
    pivot_longer(cols=everything(), names_to = "group", values_to = "count") %>% 
    mutate(group = as.factor(group))
res_long

ggplot(data = res_long, aes(x = count, fill = group)) +
    geom_histogram(data = res_long[res_long$group == "A",], alpha = 0.2, bins = 50) +
    geom_histogram(data = res_long[res_long$group == "B",], alpha = 0.2, bins = 50) +
    geom_histogram(data = res_long[res_long$group == "C",], alpha = 0.2, bins = 50) +
    theme_minimal() +
    geom_vline(xintercept = 20) +
    geom_vline(xintercept = 30) +
    geom_vline(xintercept = 50)

res_long %>% 
    group_by(group) %>% 
    summarize(n = n(),
              sd = sd(count),
              se = sd / sqrt(n))
