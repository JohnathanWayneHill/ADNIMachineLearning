# To use rpy2, you must first install it through pip. If you do not have pip
# installed, the following website has instructions to do so: 
#   https://pip.pypa.io/en/stable/installing/
# The Makefile has calls to actually install the rpy2 package. If you have pip
# installed on your computer, type "make install" in the project directory to
# install the neccessary packages. 

# Packages to install in R: 
# ~ gam
# ~ mgcv
# ~ caret
# ~ e1071

#### import Python packages
# My understanding of how to use rpy2 and Pandas was from this website:
# https://sites.google.com/site/aslugsguidetopython/data-analysis/pandas/
#     calling-r-from-python
# and, therefore, my imports are very similar 
from pandas import * # to import Pandas tools
from rpy2.robjects.packages import importr # for using R libraries
import rpy2.robjects as renv # the R environment
#import pandas.rpy.common as pandr # for using Pandas and R dataframe together
from rpy2.robjects import pandas2ri as pandr
pandr.activate()
import pandas as pd # for creating Pandas dataframe from csv file 
import os # for creating results/.../gam_summary.txt directories
import matplotlib.pyplot as plt # for histogram

# to make error, "Initializing libiomp5.dylib, but found libiomp5.dylib already initialized."  go away
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

#### install R libraries
gam = importr("gam") # to fit gam model 
mgcv = importr("mgcv") # to fit gam model
caret = importr("caret") # for confusion matrix 
e1071 = importr("e1071") # for confusion matrix 

def read_csv_as_pandas_dataframe(file_path):
    """ Creates pandas dataframe with randomly arranged rows 
    from specified file. Rows must be randomly arranged because the fit of the
    predictive model is dependent on which observations are used as testing and 
    training data. Therefore, the predicted results will be independent of rows 
    arranged by RID number. 
    """
    # read csv file from specified path as pandas dataframe
    df = pd.read_csv(file_path)
    
    # rearrange the rows of pandas dataframe
    df = df.sample(frac=1).reset_index(drop=True)
    return df

def create_gam_summary_directories(summary, start, end):
    """ Creates directory for gam fit summary and places txt file with 
    appropriate summary in the directory. 
    """
    # creates directory names
    dir_name = "./results/test_data_" + str(start + 1) + "_to_" + str(end + 1)
    
    # create directory for testing data
    os.mkdir(dir_name)
    
    # save summary of model in results directory
    write_to_txt(renv.r('summary(model)'), "test_data_" + str(start + 1) \
        + "_to_", str(end + 1) + "/", "gam_summary")

def gam_fit(train, start, end):
    """ Fits and returns a generalized additive model from training data that 
    is passed to function. Summary information is saved as txt file in 
    results directory associated with testing data observation number.
    """
    # fit model to predict GDTOTAL column from specifed FA... columns 
    model =  renv.r('mgcv::gam(GDTOTAL ~ \
        s(FA_CST_L, bs="ps", sp=0.3) + s(FA_CST_R, bs="ps", sp=0.3) \
        + s(FA_GCC_L, bs="ps", sp=0.3) + s(FA_ICP_R, bs="ps", sp=0.3) \
        + s(FA_ML_R, bs="ps", sp=0.3) + s(FA_FX_L, bs="ps", sp=0.3) \
        + s(FA_SCP_R, bs="ps", sp=0.3) + s(FA_CP_L, bs="ps", sp=0.3) \
        + s(FA_CP_R, bs="ps", sp=0.3) + s(FA_ALIC_L, bs="ps", sp=0.3) \
        + s(FA_ALIC_R, bs="ps", sp=0.3) + s(FA_PLIC_L, bs="ps", sp=0.3) \
        + s(FA_PLIC_R, bs="ps", sp=0.3) + s(FA_FX_ST_L, bs="ps", sp=0.3) \
        + s(FA_PTR_R, bs = "ps", sp=0.3), \
        family.mgcv = ocat(R=15), data = train)')
    
    # save model to R global frame 
    renv.globalenv["model"] = model
    
    # create individual directory in summary directory for summary of individual
    #   gam fit
    create_gam_summary_directories(renv.r('summary(model)'), start, end)
    
    return model

def GDS_format(predicted):
    """ Properly formats predicted results. 
    First, the numeric (float) points 
    are rounded so results over 0.5 are set one value higher than result with 
    truncated decimal points and results under 0.5 just have decimal points 
    truncated (still floating points though). 
    Then, the range is set between
    0 and 15. 
    Finally, the predicted results are turned into integers and 
    '.0' decimal points are truncated. 
    This final result is returned as a python list. 
    """
    # predicted list is set to "predicted" in R global frame
    renv.globalenv['predicted'] = predicted
    
    # return formatted results as python list
    return list(renv.r('as.integer(pmin(pmax(round(predicted), 0),15))'))

def write_to_txt(information, string_1, string_2, info_type):
    """ Writes results of some operation to file in "results" directory.
    Uses parameters to create filename. "Start" refers to the first observation
    and "end" refers to last observation. 
    """
    # variable name to hold information in R global frame
    renv.globalenv['information'] = information
    
    # create filename from "string_1", "string_2" and "info_type parameters"
    renv.globalenv['filename'] = "./results/" \
        + string_1 + string_2 + info_type +  ".txt"
    
    # write file as txt in ./results directory
    renv.r("capture.output(information, file = filename)")

def predict(predicted, test, train, start, end):
    """ Creates/returns predicted results of testing data from generalized 
    additive model fit with training data. 
    """
    # create variable for training data in R global frame
    renv.globalenv['train'] = pandr.py2ri(train)
    
    # create variable for testing data in R global frame
    renv.globalenv['test'] = pandr.py2ri(test)
    
    # fit generalized additive model to training data
    renv.globalenv['model'] = gam_fit(renv.r('train'), start, end)
    
    # predict scores on the Geriatric Depression Scale from diffusion tensor 
    #     imaging results of testing data
    predicted.extend(GDS_format(renv.r('predict.gam(model, test)')))
    return predicted

def k_fold_cross_validation(df, k):
    """ Performs k-fold cross-validation of Pandas dataframe passed in. Will
    create testing data for every k observations in dataframe and all other 
    scores will be used as training data. This process will be repeated until
    all observations have been used as testing and training data. After fitting
    a generalized additive model (GAM) from the traininging data, testing data 
    Geriatric Depression Scale (GDS) scores are predicted from their fractional
    fractional anisotropy calculations using the fitted GAM. 
    Predicted GDS resultsare returned. 
    """
    # It takes a few seconds for the algorithm to run so, printing out where how
    # the algorithm is in predicted.
    print "Predicting:"
    print
    
    # k-fold cross validation: iterating 0 through size-of-data and skipping
    # every k data point. 
    predicted = []
    data_size = len(df)
    for i in range(0, data_size, k):
        # create index values of first and last observation 
        start = i
        end = i + (k - 1)
        
        # print out observations being predicted
        print "observations " + str(start + 1) + "-" + str(end + 1)
        
        # create testing and training data
        test = df.loc[start:end,] # testing data
        train = df.drop(test.index) # training data
        
        # predicting data
        predicted = predict(predicted, test, train, start, end) 
    return predicted

def compute_list_of_error(obs, exp):
    """ computes/returns a list of how far each predicted value was from each 
    observed value.
    """
    # iterate through lenth of obs list and create new list of error between
    # observed and reference
    error_list = []
    for index in range(0, len(obs)):
        # calculate error and append to list
        error_list.append(abs(obs[index] - exp[index]))
    return error_list

def extract_specified_error_porportion(error_list, error):
    """ Given a list of errors between each predicted and referencevalue & a 
    specified error, will compute what proportion of the error_list had that 
    error value in it. 
    """
    # count number total specified in list
    amount_error = 0
    for el in error_list:
        if el == error:
            amount_error = amount_error + 1 # number of specified error in list
    return float(amount_error) / float(len(error_list)) # return proporiton

def get_accuracy_levels(error_list, length):
    """ Returns the accuracy for error values of each observed value. For
    example, perfect predicteds will have an error of 0. A 0.20 accuracy level
    of perfect predicteds will mean that 20% of the values in error_list were 
    0. Further, predicted values that were one value away from observed values
    will have a error value of 1 and so on. If 0.20 of the predicted values were
    perfect, and 0.10 were 1 error value away, then the accuracy for 1 or under
    will be 0.30. Accuracy levels are returned this way. 
    """
    # initialized output string in R global frame
    print
    renv.globalenv['st'] = "Accuracy Levels within error values:\n"
    
    # print out accuracy levels 
    total = 0.0
    for error in range(0, length + 1): 
        # save error value in R global frame
        renv.globalenv['error'] = error
        
        # compute proportion of error in list and add to previous error's 
        #   proportion; accuracy is sum of proportion of lower error values
        total = extract_specified_error_porportion(error_list, error) + total
        
        # save total value in R global frame
        renv.globalenv['total'] = total
        
        # append new results to character (string) in R global frame
        renv.globalenv['st'] = renv.r('paste(st, "Model accuracy within", \
                                                error, "values:", total, "\n")')
    
    # use R's strsplit() to split character (string) by newline characters 
    return renv.r('strsplit(st, "\n")')

def convert_py_int_list_to_r_factor_vector(py_list):
    """ Converts Python list of integers to R vector of ordered factors.
    Returns R vector. 
    """
    # initialize R vector in R global frame 
    renv.globalenv['r_vet'] = renv.r('c()')
    
    # each element of Python list is appended to R vector
    for element in py_list:
        renv.globalenv['element'] = element
        renv.globalenv['r_vet'] = renv.r('c(r_vet, element)')
    
    # R vector integer elements converted to ordered factors
    renv.globalenv['r_vet'] = renv.r('factor(r_vet, \
        levels = c(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15), ordered = TRUE)')
    return renv.r('r_vet')

def get_confusion_matrix(predicted, reference):
    """ Returns confusion matrix from predicted and referencelists.
    """
    # create R vector of ordered factors from referenceand predicted, 
    #   and capture with R global frame 
    renv.globalenv['reference'] = convert_py_int_list_to_r_factor_vector( \
        reference)
    renv.globalenv['predicted'] = convert_py_int_list_to_r_factor_vector( \
        predicted)
    
    # capture values shared by both predicted and reference in R vector
    renv.globalenv['union'] = renv.r('paste(sort(as.integer(union(predicted, \
        reference))))')
    
    # create R table comparing predicted and reference values
    renv.globalenv['table'] = renv.r('table(factor(predicted, union, \
        ordered = TRUE), factor(reference, union, ordered = TRUE))')
    
    # capture/return confusion matrix of results from data using R table 
    return renv.r('confusionMatrix(table)')
    
def main():
    # Create Pandas dataframe from CSV file.
    df = read_csv_as_pandas_dataframe('./data/merged.csv')
    
    # Perform 10-fold cross-validation on Pandas dataframe to extract predicted
    #   Geriatric Depression Scale scores as list. 
    predicted = k_fold_cross_validation(df, 10)
    
    # save predicted to file 
    write_to_txt(str(predicted)[1:-1], "", "", "predicted")
    
    # Extract reference column of true Geriatric Depression Scale scores from 
    #   Pandas dataframe as list.
    reference = df['GDTOTAL'].tolist()
    
    ## plot reference data as histogram in plots directory
    plt.hist(reference)
    plt.savefig("./plots/reference_hist")
    plt.clf()
    
    ## plot predicted data s histogram in plots directory
    plt.hist(predicted)
    plt.savefig("./plots/predicted_hist")
    plt.clf()
    
    # Save reference to file 
    write_to_txt(str(reference)[1:-1], "", "", "reference")
    
    # Create error list from predicted and reference lists.
    error_list = compute_list_of_error(predicted, reference)
    
    # Save accurancy levels for deviations 0-15.
    accuracy_levels = get_accuracy_levels(error_list, 15)
    
    # Print results
    print accuracy_levels
    
    # Save results to txt file in ./results directory
    write_to_txt(accuracy_levels, "", "", "accuracy_within_error")
    
    # Print/save confusion matrix information of comparison between predicted 
    #   and reference list.
    #confusion_matrix = get_confusion_matrix(predicted, reference)
    
    # save confusion matrix to file 
    #write_to_txt(confusion_matrix, "", "", "confusion_matrix")
    
    # print confusion matrix 
    #print confusion_matrix
    

if __name__ == "__main__":
    main()
