##### Libraries & Data ####

library(tidyverse); library(ggplot2); library(BlandAltmanLeh); library(blandr)
library(performance); library(cowplot)

ba_data <- read_csv("Speed Incline Data ACSM VO2.csv")

ba_data <- janitor::remove_empty(ba_data, which = "rows")

colnames(ba_data) <- gsub(pattern = "\\%", replacement = "", x=colnames(ba_data))

#Names the columns so R recognizes them
names(ba_data)[1] <- "ID"
names(ba_data)[2] <- "Protocol"

inclines <- c(0,2,4,6,8,10)

#### Make simple BA plots w/trend line ####

#returns BA object with data for plotting
get_BA_obj <- function(num){
  
  incline_to_plot <- paste0("_", num) #look for cols with _#
  
  #remove cols with _2nd, which were causing problems
  cols_to_avoid <- grep("0_2nd",colnames(ba_data))
  
  #finds columns that match supplied incline
  cols_to_plot <- grep(pattern = incline_to_plot, x=colnames(ba_data)) 
  
  #finds location of cols that match cols to avoid
  remove_cols_from_plot <- which(cols_to_plot %in% cols_to_avoid)
  
  #if remove_cols is empty, don't subset it
  if (length(remove_cols_from_plot) == 0) {
    cols_to_plot <- cols_to_plot
  } else(
    cols_to_plot <- cols_to_plot[-remove_cols_from_plot]
    )
  
  #adjusts title for supplied incline
  plot_title <- paste0("B-A Plot for ", num, "%")
  
  #need to use pull here rather than [,] b/c ggplot needs numeric cols
  acsm_col <- ba_data %>% pull(cols_to_plot[1])
  vo2_col <- ba_data %>% pull(cols_to_plot[2])
  
  #creates axis text using expressions to add formatted units
  x_axis_txt <- expression(Mean~of~ACSM~"&"~Measured~VO[2]~"("*mL %.% kg^{-1} %.% min^{-1}*")")
  
  y_axis_txt <- expression(ACSM~'-'~Measured~VO[2]~"("*mL %.% kg^{-1} %.% min^{-1}*")")
  
  #makes simple bland-altman plot
  BAplot <- bland.altman.plot(vo2_col, acsm_col,
                    silent = FALSE, conf.int = 0.95,
                    graph.sys = "ggplot2") + 
    ggtitle(plot_title) + 
    xlab(x_axis_txt) + 
    ylab(y_axis_txt) +
    xlim(30,55) #per original manuscript
  
  
  return(BAplot)
}
  
#takes a dataframe of mean vs. diffs & plots B-A with regression line
BA_plot_lm <- function(BAplot, plot_line = TRUE){
  
  #makes linear model to test for trend
  ba_data <- BAplot$data 
  model1 <- lm(ba_data$d ~ ba_data$m, data = ba_data, method = "qr")
  
  #m and b in y=mx+b and p for p-value
  m <- round(as.numeric(model1$coefficients[2]), 2)
  b <- round(as.numeric(model1$coefficients[1]), 2)
  p <- round(summary(model1)$coefficients[2,4], 4)

  #put together regression eqn
  #ifelse to handle - b vs. + b
  if(b > 0){
    eqn <- paste0("y = ", m, "*x + ", b, "\n")
  } else(
    eqn <- paste0("y = ", m, "*x - ", abs(b)))

  p_val <- paste0("p-value for regression coefficient: ", p)
  
  #calculates partial r squared, a measure of effect size
  partial_r2 <- round(rsq::rsq.partial(model1, adj = T)$partial.rsq,4)
  partial_r2 <- paste0("R-squared: ", partial_r2)

  #get mean difference, upper limit, lower limit (light grey)
  major_lines <- as.data.frame(BAplot$layers[[2]]$data$yintercept) %>%
    rownames_to_column() %>%
    rename(line = rowname, yint = 2)

  #get all of the confidence intervals
  minor_lines <- as.data.frame(BAplot$layers[[3]]$data$yintercept) %>%
    rownames_to_column() %>%
    rename(line = rowname,
           yint = 2)
  
  #get n for each incline
  n_by_incline <- length(ba_data$m)
  partial_r2 <- paste0(partial_r2, " ; n = ", n_by_incline)

  eqn_location <-  minor_lines %>% #will set y-val as as upper limit +1.1
    filter(line == "upper.limit.ci.upper") %>%
    pull(yint) + 1.1
  p_val_location <-  eqn_location - 1

  #finds the center of the x-axis for each plot
  center_plot <- ((max(ba_data$m) - min(ba_data$m))/2) + min(ba_data$m)
  
  #remove previous lines
  BAplot <- gginnards::delete_layers(BAplot, idx = 3)
  BAplot <- gginnards::delete_layers(BAplot, idx = 2)
  
  #make geom_point small
  BAplot$layers[[1]]$geom$default_aes$size <- 0.5
  
  BAplot_shaded <- 
    BAplot + #base BA plot
    theme_classic() + #to remove grid in background
    annotate("rect", xmin=-Inf, xmax = Inf, #set to +/- Inf to avoid changing axes
             ymin = minor_lines$yint[1], ymax = minor_lines$yint[2], #limits of agreement
             alpha = 0.3) +
      #95% CI around mean difference
    annotate("rect", xmin=-Inf, xmax = Inf, #set to +/- Inf to avoid changing axes
             ymin = minor_lines$yint[3], ymax = minor_lines$yint[4], #95% CI on mean difference
             alpha = 0.6) +
      #95% CI around mean difference
    annotate("rect", xmin=-Inf, xmax = Inf, #set to +/- Inf to avoid changing axes
              ymin = minor_lines$yint[5], ymax = minor_lines$yint[6], #95% CI on mean difference
              alpha = 0.3) +
    geom_hline(yintercept = major_lines$yint[1], linetype = "dashed", size = 0.2) + #lower limit 
    geom_hline(yintercept = major_lines$yint[2], linetype = "longdash", size = 0.3) + #mean diff
    geom_hline(yintercept = major_lines$yint[3], linetype = "dashed", size = 0.2) + #upper limit
    geom_hline(yintercept = minor_lines$yint[1], linetype = "dotted", size = 0.1) + #lower limit low CI
    geom_hline(yintercept = minor_lines$yint[2], linetype = "dotted", size = 0.1) + #lower limit up CI
    geom_hline(yintercept = minor_lines$yint[3], linetype = "dotted", size = 0.1) + #mean diff low CI
    geom_hline(yintercept = minor_lines$yint[4], linetype = "dotted", size = 0.1) + #mean diff up CI
    geom_hline(yintercept = minor_lines$yint[5], linetype = "dotted", size = 0.1) + #up limit low CI
    geom_hline(yintercept = minor_lines$yint[6], linetype = "dotted", size = 0.1) + #up limit up CI
    #annotate("text", y = eqn_location, x=center_plot, label = eqn) +
    #annotate("text", y = eqn_location, x=center_plot, label = p_val) +
    #annotate("text", y = (eqn_location-1), x=center_plot, label = partial_r2) + 
    #labs(caption = paste0(p_val, " ; ", partial_r2)) + 
    theme(plot.caption = element_text(hjust = 0.5, size = 4),
          axis.line.x = element_blank(), #removes x-axis line and ticks
          axis.ticks.x = element_blank(),
          text = element_text(size = 6)
          )
  
  
  #gets incline from the title
  incline <- str_extract(BAplot$labels$title, pattern = "\\d+")
  
  #only adds regression line if it's significant
  #also doesn't add line for 6% since homoskedacity is violated
  if (p > 0.05) {
    plot_line = FALSE} else if (incline == 6) {
      plot_line = FALSE
    } else (plot_line = TRUE)

  #makes BA plot with trendline if plot_line set to T
  if (plot_line == T){
    BAplot_shaded <- BAplot_shaded + geom_smooth(method = "lm", se = F, size = 0.4)
  }
  
  print(BAplot_shaded)
  
  return(BAplot_shaded)
  
}  

#checks assumptions for linear model by incline
lm_by_incline <- function(num){
  
  print(num)
  incline <- which(inclines == num) #finds position pf %incline in inclines vector
  
  ba_data <- all_ba_objects[[incline]]$data
    
  lm_model <- lm(d ~ m, data = ba_data, method = "qr")
  check_heteroskedasticity(lm_model) #uses Breusch-Pagan test
  check_normality(lm_model)
  check_outliers(lm_model, method = "cook")
  check_plot <- check_model(lm_model, check = "all") 
  name <- paste0("assumption_check_", num, ".png")
  width = 1000; height = 729
  png(filename = name, width = width, height = height)
  print(check_plot)
  dev.off()
}

all_ba_objects <- lapply(inclines, FUN = get_BA_obj) #makes BA data

all_ba_plots <- lapply(all_ba_objects, BA_plot_lm) #makes plots

#outputs model check information to console
lapply(inclines, lm_by_incline)

p0 <- all_ba_plots[[1]] + 
  ggtitle("A - 0%") + 
  xlab("") + 
  labs(caption = "") + 
  theme(axis.text.x = element_blank(), line = element_line(size = 0.2), 
        plot.margin = grid::unit(c(2,2,-5,2), "mm"))
p2 <- all_ba_plots[[2]] + 
  ggtitle("B - 2%") + 
  xlab("") + ylab("") + 
  labs(caption = "") + 
  theme(axis.text.x = element_blank(), line = element_line(size = 0.2),
        plot.margin = grid::unit(c(2,2,-5,0), "mm"))
p4 <- all_ba_plots[[3]] + ggtitle("C - 4%") + xlab("") + 
  labs(caption = "") + 
  theme(axis.text.x = element_blank(), line = element_line(size = 0.2),
        plot.margin = grid::unit(c(2,2,-5,2), "mm"))
p6 <- all_ba_plots[[4]] + ggtitle("D - 6%") + xlab("") + ylab("") + 
  labs(caption = "") + 
  theme(axis.text.x = element_blank(), line = element_line(size = 0.2),
        plot.margin = grid::unit(c(2,2,-5,0), "mm"))

p8 <- all_ba_plots[[5]] + ggtitle("E - 8%") + 
  theme(line = element_line(size = 0.2), 
        #plot.margin = grid::unit(c(2,2,-5,2), "mm")
        ) 
p10 <- all_ba_plots[[6]] + ggtitle("F - 10%") + 
  ylab("") + 
  theme(line = element_line(size = 0.2), plot.margin = grid::unit(c(2,2,2,0), "mm")
        )

p0
p2
p4
p6
p8
p10

# ggsave(p0, filename = "merge_ba_0.png", width = 2.2, height = 2.1, units = "in")
# ggsave(p2, filename = "merge_ba_2.png", width = 2.2, height = 2.1, units = "in")
# ggsave(p4, filename = "merge_ba_4.png", width = 2.2, height = 2.1, units = "in")
# ggsave(p6, filename = "merge_ba_6.png", width = 2.2, height = 2.1, units = "in")
# ggsave(p8, filename = "merge_ba_8.png", width = 2.2, height = 2.1, units = "in")
# ggsave(p10, filename = "merge_ba_10.png", width = 2.2, height = 2.1, units = "in")


#explore ranges 
p0$layers[[3]]$data #95% CIs of all of the lines

my.range <- function(x){
  y <-  max(x) - min(x)
  return(y)
}

range(p0$layers[[2]]$data) #mean and 95% CI of mean
range(p2$layers[[2]]$data)
range(p4$layers[[2]]$data)
range(p6$layers[[2]]$data)
range(p8$layers[[2]]$data)
range(p10$layers[[2]]$data)

my.range(p0$layers[[2]]$data) #mean and 95% CI of mean
my.range(p2$layers[[2]]$data)
my.range(p4$layers[[2]]$data)
my.range(p6$layers[[2]]$data)
my.range(p8$layers[[2]]$data)
my.range(p10$layers[[2]]$data)


#tried arranging plots within R, didn't work...

# gridExtra::grid.arrange(p0, p2, p4, p6, p8, p10, nrow = 3, ncol = 2)
# ?gridExtra::grid.arrange()
# 
# library("ggpubr")
# ggarrange(p0, p2, p4, p6, p8, p10, nrow = 3, ncol = 2, labels = c("A-0%", "B-2%"))
# ?ggarrange()


#See if mean vs. diff relationship changes when accounting for experience
descrip_data <- read_csv("Subject Characteristics Data 03.31.2020.csv")

ba_data_descrip <- merge(ba_data, descrip_data, by = "ID")

colnames(ba_data_descrip) <- tolower(colnames(ba_data_descrip))

ba_data_descrip <- ba_data_descrip %>%
  tibble() %>%
  select(contains(c("height", "age", "vo2", "weight", "mpw", "vdot", "runs")))


#need to get eqn info for 8 and 10%
ba_eqn <- function(BAplot){
  
  #makes linear model to test for trend
  ba_data <- BAplot$data 
  model1 <- lm(ba_data$d ~ ba_data$m, data = ba_data, method = "qr")
  
  #m and b in y=mx+b and p for p-value
  m <- round(as.numeric(model1$coefficients[2]), 2)
  b <- round(as.numeric(model1$coefficients[1]), 2)
  p <- round(summary(model1)$coefficients[2,4], 4)
  
  #put together regression eqn
  #ifelse to handle - b vs. + b
  if(b > 0){
    eqn <- paste0("y = ", m, "*x + ", b, "\n")
  } else(
    eqn <- paste0("y = ", m, "*x - ", abs(b)))
  
  p_val <- paste0("p-value for regression coefficient: ", p)
  
  #calculates partial r squared, a measure of effect size
  partial_r2 <- round(rsq::rsq.partial(model1, adj = T)$partial.rsq,4)
  partial_r2 <- paste0("R-squared: ", partial_r2)
  
  my_data <- c(eqn, p_val, partial_r2)
  return(my_data)
}

lapply(all_ba_objects, ba_eqn)
