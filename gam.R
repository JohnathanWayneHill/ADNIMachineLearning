install.packages("mgcv")
install.packages("gam")
install.packages("caret")
install.packages("e1071")
library("gam")
library("mgcv")
library("caret")
library("e1071")

# extract data as data.frame
dat <- read.csv("/Users/johnathanwhill/ADNIMachineLearning/cse160_final_project/data/merged.csv")

# randomize order of rows 
dat <- dat[sample(nrow(dat)),]
rownames(dat) <- 1:nrow(dat) # re-adjust rownames 

# initial vector of prediction values
prediction_vet = c()

# 10-fold cross validation 
for (i in seq(1, 150, 10)) {
  start = i # row number of first testing data item
  end = i + 9 # row number of last testing data item
  
  # print range of testing columns 
  print(paste(start, "through", end))
  
  # assgin training and testing items 
  test <- dat[start:end, ] # testing vector 
  train <- dat[-c(as.integer(rownames(test))),] # training vector
  
  # fit generalized additive model using DTI FA values
  # using penalized splines of smoothness level 0.3 to estimate smooth functions
  b1 <- mgcv::gam(GDTOTAL ~ s(FA_CST_L, bs='ps', sp=0.3) + s(FA_CST_R, bs='ps', sp=0.3)
                  + s(FA_GCC_L, bs='ps', sp=0.3) + s(FA_ICP_R, bs='ps', sp=0.3)
                  + s(FA_ML_R, bs='ps', sp=0.3) + s(FA_FX_L, bs='ps', sp=0.3)
                  + s(FA_SCP_R, bs='ps', sp=0.3) + s(FA_CP_L, bs='ps', sp=0.3)
                  + s(FA_CP_R, bs='ps', sp=0.3) + s(FA_ALIC_L, bs='ps', sp=0.3)
                  + s(FA_ALIC_R, bs='ps', sp=0.3) + s(FA_PLIC_L, bs='ps', sp=0.3) 
                  + s(FA_PLIC_R, bs='ps', sp=0.3) + s(FA_FX_ST_L, bs='ps', sp=0.3)
                  + s(FA_PTR_R, bs = 'ps', sp=0.3), 
                  family.mgcv = ocat(R=15), # ordered categorical (ordinal) data
                  data = train) # use training data to build model
  
  # predict testing items 
  prediction_vet[start:end] <- round(predict.gam(b1, test))
}

prediction_vet[prediction_vet < 0] <- 0
prediction_vet[prediction_vet > 9] <- 9

# summary of relationships between GAM fit
summary(b1)

# compute/range accuracy from between 0 and 9 values
amount_error = 0
for (i in 0:9) {
  # calculate accurately predicted values within +/- i values
  amount_error = (sum(abs(prediction_vet - dat$GDTOTAL) == i) / 150) + amount_error
  
  # print accuracy levels within 
  print(paste("percentage of predicted values", i, "values from actual value:", amount_error))
}

# set predicted and actual values to factors
prediction_vet <- factor(prediction_vet, levels = c(0,1,2,3,4,5,6,7,8,9), ordered = TRUE)
dat$GDTOTAL <- factor(dat$GDTOTAL, levels = c(0,1,2,3,4,5,6,7,8,9), ordered = TRUE)

# confusion matrix 
confusionMatrix(prediction_vet, dat$GDTOTAL)
