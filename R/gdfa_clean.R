# R script for performing data cleaning 
#### set working directory to ADNIMachineLearning first

# install and load "dplyr" package --> for rearranging columns of data.frame
#install.packages("dplyr")
library("dplyr")

# change working directory
setwd("./data")

# capture contents of merged.csv as data.frame
temp_data <- read.csv("merged.csv")

# TODO: do not hard code this --> set variables for column number of GDTOTAL
# rearrange columns so GD column is first
temp_data <- temp_data %>%
  select(3, 1, everything())

# save subject ID in seperate variable
dataID <- sort(temp_data$RID)

# obtain demographic variables


