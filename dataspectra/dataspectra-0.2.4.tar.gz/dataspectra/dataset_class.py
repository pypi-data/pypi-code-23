#!/usr/bin/env python2.7

from __future__ import print_function


'''
 Two levels of dataset storing. 
 - LocalSample - puts it into the static file.
'''


import os, sys
import helper_funcs as HF

class DatasetClass():
    def __init__(self):
        self.paramDict = dict()

    def setup(self):
        pass

    def initialize_from_mat(self, paramMat, paramDir):
        self.paramDict= HF.initialize_from_paramMat(paramMat)
        HF.setVar(self, self.paramDict)

        samplefile = "sample." + self.datasetkey + ".csv"
        self.paramDict["samplefile"] = samplefile

        self.inputDir = paramDir
        self.datasetfilepath = os.path.join(self.inputDir, self.datasetfile)

    def create_dataset_sample(self, inputDir, outputDir):
        '''
        Saves the data into a CSV file within the output direcotyr. 
        OUTPUT: 
            List of searchterms that were added
        '''
        datasetFilePath = os.path.join(inputDir, self.datasetfile)
        if self.datasetfile[-5:]==".xlsx":
            outMat = HF.convert_xlsx_to_csv(datasetFilePath, 0, 100) #
        elif self.datasetfile[-4:]==".txt":
            outMat = HF.read_delimited_file(datasetFilePath, "\t", 0, 100)
        elif self.datasetfile[-4:]==".csv":
            outMat = HF.read_delimited_file(datasetFilePath, ",", 0, 100)
        
        self.samplefilepath = os.path.join(outputDir, "static", self.paramDict["samplefile"])
        HF.save_csv_file(outMat, self.samplefilepath)
        searchTermList = [x[int(self.searchcol)-1] for x in outMat]
        return searchTermList


