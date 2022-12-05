library(tidyverse)
library(gridExtra)

source("code/cpet_articles/analysis/outlier_reporting.R")
source("code/cpet_articles/analysis/interpolation_reporting.R")
source("code/cpet_articles/analysis/avg_methods_reporting.R")

overall_reporting_frequencies <- grid.arrange(outlier_reporting_frequency_plot,
                                              interpolation_reproting_frequency_plot,
                                              overall_avg_documentation_rate_plot,
                                              nrow = 1)
# dev.copy(png, "graphics/overall_reporting_frequencies.png",
#          width = 15, height = 9, units = "in", res = 300)
# dev.off()

grid.arrange(outlier_reporting_frequency_plot,
             pct_outlier_limits_plot,
             nrow = 1)

grid.arrange(interpolation_reproting_frequency_plot,
             interpolation_by_time_plot,
             condensed_interpolation_types_plot,
             nrow = 1)

grid.arrange(overall_avg_documentation_rate_plot,
             avg_by_full_method_plot,
             nrow = 1)
