
#!/usr/bin/env python2.7

from __future__ import print_function


'''
For frequently used functions .

'''


import sys
import xlrd

def read_file_to_dict(filepath):
    '''
    Returns dictionary with the first column as key and second column as value
    '''
    paramDict = dict()
    with open(filepath) as F:
        for i in F:
            i = i.rstrip().split(",")
            paramDict[i[0]] = i[1].strip()
    return paramDict

def read_file_to_dict_with_start(filepath):
    '''
    Returns dictionary with the first column as key and second column as value. 
    Allows for a start column, at which point there is a data key added and the info is added as a list. 
    '''
    with open(filepath) as F:
        fileDict = dict()
        startFlag = 0
        dataList = list()
        for i in F:
            i =i.rstrip().split(",")
            if startFlag==0 and i[0]!="START":
                fileDict[i[0]] = i[1] 
            elif i[0]=="START": 
                startFlag +=1
            else:
                dataList.append(i)
        fileDict['data'] = dataList
    return fileDict

def read_file_to_list(filePath):
    ''' 
    Reads file (.csv, .txt, .xlsx") and returns a list.  
    '''
    fileList = list()
    if filePath[-5:]==".xlsx":
        xl_workbook = xlrd.open_workbook(filePath)
        xl_sheet = xl_workbook.sheet_by_index(0)
        for row_idx in range(0, xl_sheet.nrows):    # Iterate through rows
            outVec = list()
            for col_idx in range(0, xl_sheet.ncols):  # Iterate through columns
                cell_obj = xl_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
                val = cell_obj.value
                if type(val)== unicode:
                    val = val.rstrip()
                if type(val)==float:
                    val = str(int(val))
                outVec.append(val)
            fileList.append(outVec)
    elif filePath[-4:] in {".csv", ".txt"}:
        with open(filePath) as F:
            for i in F:
                if filePath[-4:]==".csv": i = i.rstrip().split(",")
                elif filePath[-4:]==".txt": i = i.rstrip().split("\t")
                i = [x.rstrip() for x  in i]
                fileList.append(i)
    else:
        sys.exit("Error. Suffix of file is not in .csv, .txt, or .xlsx. Exiting.")
    return fileList

def setVar(classObj, var):
    for key, value in var.items():
        setattr(classObj, key, value)

def initialize_from_paramMat(paramMat):
    '''
    Initializes a parameter list. If there is a "START" row, then everything below it will be saved as a list. 

    '''
    startFlag = 0
    paramDict = dict()
    paramList = list()
    for i in paramMat:
        if startFlag ==0:
            if i[0]=="START":
                startFlag +=1
            else: 
                paramDict[i[0]] = i[1]
        else:
            paramList.append(i)

    paramDict["paramList"] = paramList
    return paramDict


def convert_xlsx_to_csv(filename,startRowIndex = 0 , endRowIndex = "NA"):
    '''
    endRowIndex: specifies the number of rows to return.
        - Put "NA" if you want to go to the end.
    '''
    xl_workbook = xlrd.open_workbook(filename)
    xl_sheet = xl_workbook.sheet_by_index(0)
    row = xl_sheet.row(0)  # 1st row
#    colVec = list()
#    for idx, cell_obj in enumerate(row):
#        print(cell_obj.value)
    if endRowIndex ==  "NA": endRowIndex = xl_sheet.nrows
    num_cols = xl_sheet.ncols   # Number of columns
    outMat = list()
    for row_idx in range(startRowIndex, endRowIndex):    # Iterate through rows
        outVec = list()
        for col_idx in range(0, num_cols):  # Iterate through columns
            cell_obj = xl_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
            outVec.append(cell_obj.value)
        outMat.append(outVec)
    return outMat


def read_delimited_file(filename, delimiter="\t", startRowIndex = 0, endRowIndex = "NA"):
    outMat = list()
    counter = 0
    with open(filename) as F:
        for i in F:
            if counter >= startRowIndex and (endRowIndex=="NA" or counter <= endRowIndex):
                i = i.rstrip().split(delimiter)
                outMat.append(i) 
                counter +=1
    return outMat



def save_csv_file(outMat, outFile):
    fileOUT = open(outFile, "w")
    for i in outMat:
        fileOUT.write(",".join([str(x) for x in i]) + "\n")
    fileOUT.close()

