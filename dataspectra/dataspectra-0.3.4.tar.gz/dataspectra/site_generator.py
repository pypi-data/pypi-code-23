#!/usr/bin/env python2.7

from __future__ import print_function


'''
Ideally, in the new version, there should be no connections between figures, buttons, etc. 
- This makes it simpler because it breaks dependencies. 

If specified in one big file - you can read it through. 
If specified in multiple files... You can enter the list of files in one long file list. ?

'''

import site_class as STC
import panel_class as PC
import sidebar_class as SBC
import figure_class as FC
import dataset_class as DC
import dsvisualizer_convert_input as DSCI
import sys, os
import filecmp, shutil
import json



import helper_funcs as HF
import search_lookup as SL
import datastore_funcs as DF
from google.cloud import datastore

class SiteGenerator():
    def __init__(self, paramPath,outputDirPath, sourceDir, appid):

        self.paramPath = paramPath
        self.paramDir = os.path.dirname(paramPath)
        self.outputDirPath = outputDirPath
    
        self.panelDict = dict()
        self.siteObj = ""
        self.sidebarObj = ""
        self.datasetDict = dict()
        self.figureDict = dict()

        self.aeDirPath  = os.path.join(sourceDir, "aefiles") # This holds the template app engine files.
        self.create_or_update_outputDir() #Sets up the output directory with the app engine files. 

        mode="onefile"
        if mode=="onefile":
            self.initialize_from_one_param_file(paramPath)      
            self.initialize_objects() #Now that all the info is loaded, ready to initialize.
            self.create_sample_data_for_local_testing() 
            self.create_search_files() #Access all the datasets and creates a search lookup table.
            self.siteObj.paramDict["appid"] = appid #Set appid. 
            self.create_json_files()

    def initialize_objects(self):
        for figure in self.figureDict.values():
            figure.setup(self.datasetDict, self.paramDir, self.outputDirPath)

        for dataset in self.datasetDict.values():
            dataset.setup()

        for panel in self.panelDict.values():
            panel.setup()

    def initialize_from_one_param_file(self,paramPath):
        '''
        Read in the parameter file and load in section. 
        '''
        allParamFileList = HF.read_file_to_list(paramPath)
       
        if allParamFileList[0][1]=="formfiller":
            allParamFileList = DSCI.revert_from_formfiller(allParamFileList)

        paramMat = list()
        for i in allParamFileList:
            if i[0]=="parameter":
                self.load_paramMat(paramMat)
                paramMat = list()
            paramMat.append(i)
        self.load_paramMat(paramMat) #parse the last chunk

    def load_paramMat(self,paramMat):
        '''
        Function that loads that info in the paramMat. 
        '''
        if len(paramMat)==0: 
            return 0
        else:
            paramType = paramMat[0][1]           
            if paramType==u"site":
                site = STC.SiteClass()
                site.initialize_from_mat(paramMat)
                self.siteObj = site
            if paramType==u"sidebar":
                sidebar = SBC.SidebarClass()
                sidebar.initialize_from_mat(paramMat)
                self.sidebarObj = sidebar
            if paramType==u"figure":
                figure = FC.FigureClass()
                figure.initialize_from_mat(paramMat)
                self.figureDict[figure.paramDict["figurekey"]] = figure
            if paramType==u"dataset":
                dataset = DC.DatasetClass()
                dataset.initialize_from_mat(paramMat, self.paramDir)
                self.datasetDict[dataset.paramDict["datasetkey"]] = dataset
            if paramType==u"panel":
                panel = PC.PanelClass()
                panel.initialize_from_mat(paramMat)
                self.panelDict[panel.paramDict["panelkey"]] = panel

    def create_json_files(self):

        with open(os.path.join(self.outputDirPath, "static", "sidebar.json"), 'w') as json_file:
            json.dump(self.sidebarObj.paramDict, json_file, indent=2)

        with open(os.path.join(self.outputDirPath, "static", "site.json"), 'w') as json_file:
            json.dump(self.siteObj.paramDict, json_file, indent=2)

        figureJsonDict = {figurekey:self.figureDict[figurekey].paramDict for figurekey in self.figureDict}
        with open(os.path.join(self.outputDirPath, "static", "figures.json"), 'w') as json_file:
            json.dump(figureJsonDict, json_file, indent=2)

        panelJsonDict = {panelkey:self.panelDict[panelkey].paramDict for panelkey in self.panelDict}
        with open(os.path.join(self.outputDirPath, "static", "panels.json"), 'w') as json_file:
            json.dump(panelJsonDict, json_file, indent=2)
        
        datasetJsonDict = {datasetkey:self.datasetDict[datasetkey].paramDict for datasetkey in self.datasetDict}
        with open(os.path.join(self.outputDirPath, "static", "datasets.json"), 'w') as json_file:
            json.dump(datasetJsonDict, json_file, indent=2)


    def create_or_update_outputDir(self):
        '''
        Description: Create the directory that holds all the files for running app engine.  
        '''
        src = os.path.normpath(self.aeDirPath)
        dest = os.path.normpath(self.outputDirPath)

        if os.path.exists(dest)==0:
            shutil.copytree(src, dest)
        else:
            #Delete any dirs and files that are in dest that are not in source
            for root, dirs, files in os.walk(dest):
                for each_dir in dirs:
                    dest_path = os.path.join(root, each_dir)
                    src_path =  os.path.join(root.replace(dest, src) , each_dir)
                    if os.path.exists(src_path)==0:
                        print("deleting directory: ", dest_path)
                        shutil.rmtree(dest_path)
                for each_file in files:
                    dest_path = os.path.join(root, each_file)
                    src_path =  os.path.join(root.replace(dest, src) , each_file)
                    if os.path.exists(src_path)==0:
                        print("deleting file: ", dest_path)
                        os.remove(dest_path)
            result = filecmp.dircmp(src, dest)
            for root, dirs, files in os.walk(src):
                for each_dir in dirs:
                    src_path = os.path.join(root, each_dir)
                    dest_path =  os.path.join(root.replace(src, dest) , each_dir)
                    if os.path.exists(dest_path)==0:
                        print("copying directory: ", src_path)
                        shutil.copytree(src_path, dest_path)
                for each_file in files:
                    src_path = os.path.join(root, each_file)
                    dest_path =  os.path.join(root.replace(src, dest) , each_file)
                    if os.path.exists(dest_path)==0 or filecmp.cmp(src_path, dest_path)==0:
                        print("copying file: ", src_path)
                        shutil.copyfile(src_path, dest_path)


    def create_sample_data_for_local_testing(self):
        '''
        #This will load 100 rows for each dataset into the local datastore for testing.
        '''
        sampleSearchTermList = list()
        for dataset in self.datasetDict.values():
            sampleSearchTermList += dataset.create_dataset_sample(self.paramDir, self.outputDirPath)
        self.sampleSearchTermList = list(set(sampleSearchTermList))

    def create_search_files(self):
        '''
        Description:
        - Creates lookup table to match a search term with other terms. 
        - Creates the javascript file for autofilling search names. 
        - Creates a search_lookup.json with the following info:
            - sample.search_lookup.csv path
            - Ordered list of the columns for the dataset columns. 

        Requirements:
        - Needs a self.sampleSearchTermList to be defined.  These are defined in create_sample_data_for_local_testing
        
        Notes:
        - Perhaps add this to a dataset file? But we may want to switch this to a search API in the future. 
        '''

        if len(self.sampleSearchTermList)==0: 
            sys.exit("Error in creating lookup. Needs to create samples first.")

        datasetLookupTable = SL.create_search_lookup(self.datasetDict, self.paramDir)
        #LATER - We should upload the full version of this to the datastore.
        searchLookupDict = dict()
        searchLookupDict["samplefile"]  = "sample.searchlookup.csv"
        searchLookupDict["fullfile"] = "full.searchlookup.csv"
        searchLookupDict["columns"] = datasetLookupTable[0][2:]
        with open(os.path.join(self.outputDirPath, "static", "search_lookup.json"), 'w') as json_file:
            json.dump(searchLookupDict, json_file, indent=2)
        
        SL.create_lookupfile(
            os.path.join(self.outputDirPath, "static", searchLookupDict["samplefile"]),
            datasetLookupTable,
            searchTermFilter = self.sampleSearchTermList
            )

        SL.create_lookupfile(
            os.path.join(self.paramDir, searchLookupDict["fullfile"] ),
            datasetLookupTable,
            searchTermFilter = None
            )    

        self.searchLookupDict = searchLookupDict
        searchTermPath = os.path.join(self.outputDirPath, "web", "js", "gene_name_auto.js")
        SL.create_search_autofill_javascript_file([x[0] for x in datasetLookupTable[1:]], searchTermPath)

    def production_upload_datastore(self, appid, files="all"):
        print("\tUploading data to production datastore: ", appid)
               
        client = datastore.Client(appid)   
        if files=="all": 
            for dataset in  self.datasetDict.values():
                DF.delete_dataset(appid, dataset.datasetkey) #overwrite
                DF.upload_dataset2datastore(dataset.datasetfilepath, 
                client, dataset.datasetkey, dataset.searchcol, 
                dataset.searchrowstart)

        filepath = os.path.join(self.paramDir, self.searchLookupDict["fullfile"] )
        DF.delete_dataset(appid, "searchterm")
        DF.upload_dataset2datastore(filepath, client, "searchterm", searchcol=1, searchrowstart=1)

    def production_push_website(self, appid):
        '''
        Push data to production. 
        '''
        import subprocess
        print("Pushing data to production")
        print("This step can take a long time.")
        p = subprocess.Popen(["gcloud","app", "deploy", "--project", appid], 
            cwd = self.outputDirPath, 
            stdout = subprocess.PIPE)
        print(p.communicate())

    def cloudstorage_upload_datasets(self, appid):
        '''
        Copy datasets to google cloud storage
        '''
        import subprocess
        for dataset in self.datasetDict.values():
            print("Uploading dataset from: ", dataset.datasetfilepath)
            p = subprocess.Popen(["gsutil", "cp",  dataset.datasetfilepath, "gs://" + appid + ".appspot.com"], 
                 stdout = subprocess.PIPE)
            p.communicate()
            filename = dataset.datasetfilepath.split("/")[-1]
            p = subprocess.Popen(["gsutil", "acl", "ch", "-u", "AllUsers:R", "gs://" + appid + ".appspot.com/" + filename], 
                stdout = subprocess.PIPE)
            p.communicate()
            
