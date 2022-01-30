import os 
import csv 
import itertools
from operator import itemgetter

def read_csv(filename):
    """ returns list of dictionaries when given a file name 
    """
    
    # open filename
    file_in = open(filename)
    
    # create a varaible for input file that some dicitonaries
    file_1 = csv.DictReader(file_in)
    
    # add row of file_21 to ls
    ls = []
    for row in file_1: 
        ls.append(row)
    
    # iterate through list and create new list with only observations of m06
    output_list = []
    for row in ls:
        if row["VISCODE2"] == "m06":
            output_list.append(row)
    file_in.close() # close file
    return output_list

def get_RID(dict_list):
    """ Given a dictionary of lists, returns a list of RID (subject ID)
    """
    # iterate through dictionary list and append RID to list
    ls = []
    for dic in dict_list: 
        ls.append(dic["RID"])
    return ls

def remove_dic(dic_ls_1, dic_ls_2):
    """ returns a new list of dictionaries with dictionaries of the second
    list of dictionaries that only have the same RIDs as the the first specified
    list of dictionaries.
    """
    # get list of dictionaries 
    id_1 = get_RID(dic_ls_1)
    
    # iteratre through second list of dictionaries and append dictionaries that
    #   are in the list of RIDs from first list of dictionaries
    output_dic_ls = []
    for line in dic_ls_2:
        if line["RID"] in id_1:
            output_dic_ls.append(line)
    return output_dic_ls

def list_of_col(filename):
    """ Generate a list of column names in correct format from specified 
    filename.
    """
    # open file
    input_file = open(filename)
    
    # iterate through lines of file, replace newline characters by empty strings
    # and append line to to output_list
    output_list = []
    for line in input_file:
        output_list.append(line.replace("\n",""))
    
    # close file and return output_list
    input_file.close()
    return output_list

def relevant_cols(dic_ls, list_of_col):
    """ From dictionary list to list list of columns 
    """
    
    # iterate through dic_list and returns a list of columns to be appended 
    # to the end of the output list 
    output_list = []
    for row in dic_ls:
        output_dic = {}
        for col in row:
            if col in list_of_col:
                output_dic[col] = row[col]
        output_list.append(output_dic)
    return output_list

def merge_by_RID(dic_ls_1, dic_ls_2):
    """ Given two lists of dicitonaries, returns a list of dictionaries with
    both dictionaries of lists merged by "RID"
    """
    
    # iterate trhough dictionary lists and append values that contain specified
    # RID
    output_ls = []
    for row1 in dic_ls_1:
        for row2 in dic_ls_2:
            if row1["RID"] == row2["RID"]:
                output_ls.append(dict(itertools.chain(row1.iteritems(), row2.iteritems())))
    return output_ls

def string_values_to_int(dic_ls):
    """ For all values in dictionary list, returns a list of dictionaries 
    from string to integers
    """
    # iterate through dic_ls and append proper formaty of values
    output_list = []
    for row in dic_ls:
        output_dic = {}
        for col in row:
            if col == "GDTOTAL" or col == "RID":
                output_dic[col] = int(row[col])
            else: 
                output_dic[col] = float(row[col])
        output_list.append(output_dic)
    return output_list 

def main():
    # load dti data
    file_dti = read_csv("./data/DTIROI_04_30_14-1.csv")
    
    # load gds data
    file_gds = read_csv("./data/GDSCALE-4.csv")
    
    # get id of dti
    dti_id = get_RID(file_dti)
    
    # remove gds list of dictionaries with same observations of dti
    file_gds = remove_dic(file_dti, file_gds)
    
    # extract the id numbers within  
    gds_id = get_RID(file_gds)
    
    # get fa column names
    fa_cols = list_of_col("column_names/FA_ID.txt")
    
    # get gds column names
    gds_cols = list_of_col("column_names/GDS.txt")
    
    # get fa dicitonary list from fa_cols
    fa_dic_ls = relevant_cols(file_dti, fa_cols)
    
    # get gds dictionary list from gds_cols
    gds_dic_ls = relevant_cols(file_gds, gds_cols)
    
    # merge data sets
    merged = merge_by_RID(fa_dic_ls, gds_dic_ls)
    
    # change string values to integer
    merged_int = string_values_to_int(merged)
    
    # sort merge_int by RID
    sorted(merged_int, key = itemgetter("RID"))
    
    # output to file
    keys = merged_int[0].keys()
    with open('./data/merged.csv', 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(merged_int)


if __name__ == "__main__":
    main()