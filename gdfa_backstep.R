setwd("~/uw1617/s/radgy499/ADNIMachineLearning/")
# R script for performing backstep regression on GD ~ FA data.
source("./R/gdfa_clean.R") # sets working directory to data directory, then cleans data 

# TODO: fix errors!!!!!!

# environmental variables: 
## data: data frame with GD and FA means

# not part of model so set to null
data$RID <- NULL

# create linear regression model using GD and FA data
model <- lm(GDTOTAL ~ ., data = data)

# perform backward stepwise regression and capture output in file (results directory)
#capture.output(step(model, direction = "backward"), file = "../results/step_model_steps.txt")

# capture step model
step_model <- step(model, direction = "backward")

# create file for step model
#capture.output(step_model, file = "../results/step_model.txt")

# create file for summary of step model
#capture.output(summary(step_model), file = "../results/step_model_summary.txt")

model_demo <- lm(GDTOTAL ~ YOB + PTGENDER + PTEDUCAT, data = merged)

# symmetry --> same levels of predictive capabilities, same direction

# create linear regression model using GD and FA data
model_all <- lm(GDTOTAL ~ FA_SFO_R+ demo$YOB + demo$PTGENDER + demo$PTEDUCAT, 
                data = data)

model_all_step <- step(model_all, direction = "backward")

xyplot(GDTOTAL~FA_SFO_R, data=data)
abline(lm(GDTOTAL~FA_SFO_R, data = data), col="red")

# brain tracts --> jhu atlas --> correspondence; check 
# create color map --> color code intensities --> create picture --> visualize 
# same with executive functioning 
# coefficients for significant variables 

# look at multiple comparisons --> adjustment 
### come up with a study plan 
### false discovery rate correction --> spatial information 
### random sl