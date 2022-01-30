import os 
import csv 
import itertools
from operator import itemgetter

def extract_m06(ls):
    """ Given a list of dictionaries, returns only contemporaneous data from 
    month 6 time point.
    """
    # iterate through list and create new list with only observations where 
    #     values of "m06" are associated with "VISCODE2"
    output_list = []
    for row in ls:
        if row["VISCODE2"] == "m06":
            output_list.append(row)
    return output_list

def read_csv_at_m06(filename):
    """ Returns a list of dictionaries, where each dictionary is a row from 
    specified csv file. Only 
    """
    # open file
    file_in = open(filename)
    
    # extract data from file as dictionaries
    dict_from_csv = csv.DictReader(file_in)
    
    # add each row to ls
    ls = []
    for row in dict_from_csv: 
        ls.append(row)
    
    # extract data from month 6; only examining contemoraneous data 
    output_list = extract_m06(ls)
    
    # close file
    file_in.close
    return output_list
    
def get_RID(dict_list):
    """ Given a dictionary of lists, returns a list of RID (subject ID)
    """
    # iterate through dictionary list and append subject ID to list
    ls = []
    for dic in dict_list: 
        ls.append(dic["RID"])
    return ls

def remove_dic(dic_ls_1, dic_ls_2):
    """ returns a new list of dictionaries with dictionaries of the second
    list of dictionaries that only have the same RIDs as the the first specified
    list of dictionaries.
    """
    # get list of subject IDs from first list of dictionaries
    id_1 = get_RID(dic_ls_1)
    
    # iterate through second list of dictionaries and test if subject ID of each
    #     observation is in first list of dictionaries. if so, append this
    #     information to output dictionary list.
    output_dic_ls = []
    for line in dic_ls_2:
        if line["RID"] in id_1:
            output_dic_ls.append(line)
    return output_dic_ls

def list_from_txt(filename):
    """ Generate a list from information in file with newline characters removed
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

def format_data_type(dic_ls):
    """ For all values in dictionary list, returns a list of dictionaries 
    from string to integers or floats (dependening on column names)
    """
    # iterate through dic_ls and append proper formaty of values
    output_list = []
    for row in dic_ls:
        output_dic = {}
        for col in row:
            if col == "GDTOTAL" or col == "RID":
                output_dic[col] = int(row[col]) # GDS data or subject ID
            else: 
                output_dic[col] = float(row[col]) # DTI data 
        output_list.append(output_dic)
    return output_list

def write_dictionary_list_to_csv(data, filename):
    """ Writing clean, specified merged data to specified csv filename. 
    Syntax from this website: https://docs.python.org/2/library/csv.html
    """
    # exract column names
    columns = data[0].keys()
    
    # write csv file from given data
    with open(filename, 'wb') as output_file:
        write_csv = csv.DictWriter(output_file, columns) # create object
        write_csv.writeheader() # rows organized with dictionary keys as columns
        write_csv.writerows(data) # write row to csv file

    

def main():
    # load DTI data from csv file
    file_dti = read_csv_at_m06("./data/DTIROI_04_30_14-1.csv")
    
    # load GDS data from csv file
    file_gds = read_csv_at_m06("./data/GDSCALE-4.csv")
    
    # modify GDS data and remove data with subject IDs not in DTI data
    file_gds = remove_dic(file_dti, file_gds)
    
    # check that subject IDs are correct
    assert get_RID(file_dti).sort() == get_RID(file_gds).sort()
    
    # extract columns names of relevant DTI data
    fa_cols = list_from_txt("column_names/FA_ID.txt")
    
    # extract column names of relevant GDS data 
    gds_cols = list_from_txt("column_names/GDS.txt")
    
    # extract relevant GDS data
    fa_dic_ls = relevant_cols(file_dti, fa_cols)
    
    # extract relevant GDS data
    gds_dic_ls = relevant_cols(file_gds, gds_cols)
    
    # merge data sets by subject ID
    merged = merge_by_RID(fa_dic_ls, gds_dic_ls)
    
    # test length of merged
    assert len(merged) == 150
    
    # modify the data types to be integer or float (depedent on data)
    merged_cleaned = format_data_type(merged)
    
    # check number of observations 
    assert len(merged_cleaned) == 150
    
    # sort our data
    sorted(merged_cleaned, key = itemgetter("RID"))
    
    # write data to csv file
    write_dictionary_list_to_csv(merged_cleaned, "./data/merged.csv")

if __name__ == "__main__":
    main()