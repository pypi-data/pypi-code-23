#!/usr/bin/env python

def create_dict_from_file(filePath, skip=1, ncol=1, strict=False):
    '''
    create_dict_from_file

    DESCRIPTION 
        - Creates dictionary with the first col as the key and the other columns as a list. 
        - If ncol==1, then the value is only the 2nd column value and not a list. 

    INPUT:
        - filePath
        - skip
        - ncol

    OUTPUT:
        - dict

    OPTIONS:
        - strict: If true: Will throw error if a row does not have enough columns. Otherwise, it will just throw a warning. 
    '''

    fileIN = open(filePath, "U")
    
    for i in range(skip):
        fileIN.readline()

    warnings = list()
    file_dict = dict()
    for i in fileIN:
        i =i.rstrip().split("\t")
        if ncol==1:
            if not strict and len(i)<2:
                warnings.append(i)
                continue
            else:
                file_dict[i[0]] = i[1]
        else:
            if not strict and len(i)<1+ncol:
                warnings.append(i)
                continue
            else:
                file_dict[i[0]] = i[1:1+ncol]
    fileIN.close()
    print "Number of warnings: ", len(warnings)
    print warnings
    return file_dict


def create_file_list(filePath, skip=1):
    '''
    create_file_list 

    DESCRIPTON: Takes a file and creates a list of a list
   
    INPUT: 
        - filePath
        - skip: Number of lines to skip when reading in. 

    '''
    fileIN = open(filePath)
    
    for i in range(skip):
        fileIN.readline()

    file_list = list()
    for i in fileIN:
        i =i.rstrip().split("\t")
        file_list.append(i)
    fileIN.close()

    return file_list








