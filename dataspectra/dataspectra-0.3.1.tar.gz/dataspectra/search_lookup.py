#!/usr/bin/env python2.7

from __future__ import print_function


'''
#GOAL#
- From a searchterm, get the terms that need to be searched in each dataset.
- Take the searched term in each dataset, and create a object so that the javascript datacan easily extract the info.
- Also, allow intersection with homolog matcher.

#NOTES#
#What about incomplete or missing terms? 
    Specify beforehand - so that we don't have to go looking for them in the dataset.

ex. 
SearchTerm entered. 
- Go through lookup table. Find the terms needed for each figure.  Do this calculation beforehand - so that we don't have to waste time going through trees. 
- Go through each dataset and extract the terms and put into DataJson
- create figure1 - DataJson[datasetkey]
'''
import sys, os, itertools
import xlrd

def create_search_lookup(datasetDict, inputDir):
    '''

    Note: Ignores metafiles, or for meta files - will look up accordingly. 

    Output:  
    { searchTerm:  ,  data: [data1Val,data2Val,data3Val]; ...}
    '''
    #Read in the search terms for all of the datasets.
    #First do this for all of the non-meta files. 
    datasetTermDict = dict()
    for datasetkey in datasetDict:
        Dataset = datasetDict[datasetkey]
        if "datasettype" in Dataset.paramDict and Dataset.datasettype=="meta":
            pass
        else:
            searchTerms = read_column(
                os.path.join(inputDir, Dataset.datasetfile), 
                int(Dataset.searchcol)-1,
                int(Dataset.searchrowstart)-1) #search col is 1 indexed
            datasetTermDict[datasetkey]= dict()
            if "species" in Dataset.paramDict: 
                datasetTermDict[datasetkey]["species"] = Dataset.species
            datasetTermDict[datasetkey]["searchterms"] = set(searchTerms)

    #See if multiple species are present
    speciesSet = set([datasetTermDict[datasetkey]["species"]  
        for datasetkey in datasetTermDict if "species" in datasetTermDict[datasetkey]])

    if len(speciesSet)>1: 
        return create_lookup_table_with_homologs(datasetTermDict)
    else:
        return create_lookup_table_standard(datasetTermDict)

def create_lookup_table_with_homologs(datasetTermDict):
    #We want to enter a list of search terms - with their assigned species.
    print("\tMultiple species detected, Running code for homology mapping")
    sys.path.append("/Users/ryosukekita/Desktop/PROJECTS/SCIWIRC/homolog_matcher")
    import homolog_matcher as HM
    datasetLookupTable = HM.create_lookup_table_from_datasetDict(datasetTermDict)
    return datasetLookupTable

def create_lookupfile(outputFilePath, datasetLookupTable, searchTermFilter = None):
    '''
    Restricts to the search terms that were uploaded on prior datasets. 
    '''
    if searchTermFilter != None: 
        searchTermSet = set(searchTermFilter)
    with open(outputFilePath, "w") as F:
        for i in datasetLookupTable[1:]:
            if searchTermFilter == None:
                F.write(",".join(i)  + '\n')
            elif i[0] in searchTermSet:
                F.write(",".join(i)  + '\n')
            else:
                continue


def create_lookup_table_standard(datasetTermDict):
    '''
    For consistency with the homology analysis - we are adding a blank "NA" after search term. 
    '''
    totalSearchTerms = list(itertools.chain.from_iterable([ list(datasetTermDict[datasetkey]["searchterms"])   for datasetkey in datasetTermDict]))
    totalSearchTerms = list(set(totalSearchTerms))
    keylistsrt = sorted(datasetTermDict.keys())
    datasetLookupTable  = [["searchterm"] + ["NA"] + [datasetkey for datasetkey in  keylistsrt ] ]
    datasetLookupTable += [[searchTerm] + ["NA"] +  [searchTerm if searchTerm in datasetTermDict[datasetkey]["searchterms"] else "NA" 
        for datasetkey in keylistsrt]  
        for searchTerm in totalSearchTerms]
    return datasetLookupTable

def read_column(filepath, col, start):
    if filepath[-4:]==".txt":
        with open(filepath) as F:
            for i in range(start):
                F.readline()
            searchTermList = [line.rstrip().split("\t")[col] for line in F]
    elif filepath[-4:]==".csv":
        with open(filepath) as F:
            for i in range(start):
                F.readline()
            searchTermList = [line.rstrip().split(",")[col] for line in F]  
    elif filepath[-5:]==".xlsx":
        xl_workbook = xlrd.open_workbook(filepath)
        xl_sheet = xl_workbook.sheet_by_index(0)
        endRowIndex = xl_sheet.nrows
        num_cols = xl_sheet.ncols   # Number of columns
        outMat = list()
        searchTermList = [xl_sheet.cell(row_idx, col).value   for row_idx in range(start, endRowIndex)]

    print("\tNumber of search terms: ", len(searchTermList))
    print("\tExample search terms: ", searchTermList[0:3])
    return searchTermList

def create_search_autofill_javascript_file(searchTerms, outpath):
    searchTermBlobs = [ '{ value:"' + term + '"}'  for term in searchTerms]
    outline = 'var allTerms = ['
    outline += ",".join(searchTermBlobs)
    outline += ']'
    with open(outpath, "w") as F:
        F.write(outline)


if __name__=="__main__":
    main()
