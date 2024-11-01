# Make a PRISMA flow diagram

# I made the CSV file by manually entering in the data based on the template
# found here: https://estech.shinyapps.io/prisma_flowdiagram/

# The data I entered comes from the PRISMA_flowchart_calcs.R script

library(tidyverse)
library(PRISMA2020)

prisma_csv <- read_csv(fs::path("data/cpet_articles/PRISMA.csv"),
                       show_col_types = FALSE)

prisma_data <- PRISMA_data(prisma_csv)

# debugonce(PRISMA_flowdiagram)
prisma_plot <- PRISMA_flowdiagram(prisma_data,
                                  interactive = FALSE,
                                  previous = FALSE,
                                  other = FALSE,
                                  detail_databases = TRUE,
                                  detail_registers = FALSE,
                                  fontsize = 11,
                                  font = "Helvetica",
                                  title_colour = "Goldenrod1",
                                  greybox_colour = "Gainsboro",
                                  main_colour = "Black",
                                  arrow_colour = "Black",
                                  arrow_head = "normal",
                                  arrow_tail = "none",
                                  side_boxes = TRUE)
prisma_plot
saveRDS(prisma_plot, fs::path("graphics/PRISMA_flowdiagram.rds"))

PRISMA_save(prisma_plot,
            fs::path("graphics/PRISA_flowdiagram.png"),
            overwrite = TRUE)
