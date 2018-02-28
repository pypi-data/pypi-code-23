#!/usr/bin/env python2.7

import os


def search_term_file_auto_generate(self):
    '''
    Should this be user generated?
    There are only going to be a few types.
    This can be automatically generated - but can also be user generated.    Automatically generate -
 by specifying the Type.

    ["SEARCHTYPE"] - if MULTIPLE - then there are multiple images.
        - if NONE - then there is only a single image. For example a reference image that you want someone to be able to jump to.
    
    #Step 2: If a dataset has a single search term. Then use that. 

    NOTES:
        - Currently - removes all the directories before in the search directory. 

    '''
    
    #Step 1: Go through each of the datasets. And gather the search terms. 
    searchSet = set()
    for dataset in self.datasets:
        if dataset.search.lower()=="multiple":
            fileIN = open(dataset.genesP) 
            dataset.searchDict = dict()
            for i in fileIN:
                i = i.rstrip().split("\t") 
                dataset.searchDict[i[0]] = i[1].split("/")[-1]
                if i[0] not in searchSet: searchSet.add(i[0]) 
            fileIN.close()
        if dataset.search.lower()=="single":
            fileIN = open(dataset.genesP)
            dataset.singleFilePath = fileIN.readline().rstrip().split("\t")[-1].split("/")[-1]
            fileIN.close()
            
   
    #Step 2: Create a file that has [Search term] [Dataset 1 File]  [Dataset 2 File]...
    #For each search term - there should only be one file. 
    #But - each file can be associated with multiple search terms. 
    #And output file to google cloud

    outputFile = "tmp/search_lookup_file.txt"
    fileOUT = open(outputFile, "w")
    search_lookup_table  = list() 
    for searchTerm in searchSet:
        searchVec = list()
        for dataset in self.datasets:
            if dataset.search.lower()=="multiple":
                if searchTerm not in dataset.searchDict:
                    matchFileName = "NA"
                else:
                    matchFileName = dataset.searchDict[searchTerm]
            #The actual location of the image is now going to be different because it will be with google cloud storage. 
            #Location: [setKey] + "/"  + [fileName]
            elif dataset.search.lower()=="single":
                matchFileName = dataset.singleFilePath
            location = dataset.setkey + "/" + matchFileName
            searchVec.append(location) 
        search_lookup_table.append([searchTerm]  + searchVec) 
        outString = searchTerm + "\t" + "\t".join(searchVec) + "\n"
        fileOUT.write(outString)
    fileOUT.close()
    self.search_lookup_file = outputFile


def upload_search_lookup_to_google_cloud(self):
    cmd = ["gsutil", "cp", self.search_lookup_file, "gs://" + self.appid + ".appspot.com"]
#    cmd = ["gsutil", "cp", self.search_lookup_file, "gs://" + self.appid]
    os.system(" ".join(cmd))



