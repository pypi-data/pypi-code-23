#!/usr/bin/env python2.7

from __future__ import print_function

'''

outputDir is optional. It is only used when there is a density file to output. 

'''
import os,sys
import dataset_class as DC
import helper_funcs as HF
import shutil

class FigureClass():
    def __init__(self):
        self.paramDict = dict()
        
    def initialize_from_mat(self, paramMat):
        self.paramDict = HF.initialize_from_paramMat(paramMat)
        HF.setVar(self, self.paramDict)

    def setup(self, datasetDict, inputDirPath, outputDirPath):
        '''
        Note, this is set as a separate function, because intializing should occur after everything else?
        '''
        print("Initializing Figure: ", self.paramDict["figurekey"])
        self.convert_colors()
        
        
        self.autofill_columns(datasetDict)
            #self.autofill_figure_mat(datasetDict)
        if self.figuretype=="density":
            self.prepare_density_file(datasetDict, outputDirPath)
        elif self.figuretype=="carousel":
            self.prepare_image_files(inputDirPath, outputDirPath)
        #elif self.figuretype=="mdscatter":
            #self.prepare_mdscatter()
            #self.prepare_multidim_file(datasetDict, outputDirPath)

    def autofill_columns(self, datasetDict):

        if "metakey" in self.paramDict: 
            metaData = HF.read_file_to_list(datasetDict[self.metakey].datasetfilepath)
        newParamList = list()
        for i in self.paramList:
            if "meta" in i[2]:
                rowName = i[2].split("meta.")[1].split("==")[0]
                rowVal = i[2].split("==")[1]
                matchingRow = [x for x in metaData if x[0]==rowName][0]
                
                colNums = [str(idx+ 1) for idx, val in enumerate(matchingRow) if val==rowVal]
                colString = "$".join(colNums)
                i[2]= colString
                
            if "--" in i[2]:
                colStart = int(i[2].split("--")[0])
                colEnd = int(i[2].split("--")[-1])
                i[2] = "$".join([str(x) for x in range(colStart, colEnd+1)])
            if "-" in i[2]:
                colStart = int(i[2].split("-")[0])
                colEnd = int(i[2].split("-")[-1])
                i[2] = "$".join([str(x) for x in range(colStart, colEnd+1)])
            newParamList.append(i)
        self.paramList = newParamList
        self.paramDict["paramList"] = self.paramList
        

    def convert_colors(self):
        '''
        Color should always be the third element in the list. 
        '''
        newParamList = list()
        for i in self.paramList:
            if ";" in str(i[4]):
                rgbcolor = "rgb(" + ",".join(i[4].replace("(", "").replace(")", "").split(";")) + ")"
                i[4]=rgbcolor
            if ";" in str(i[3]):
                rgbcolor = "rgb(" + ",".join(i[3].replace("(", "").replace(")", "").split(";")) + ")"
                i[3]=rgbcolor
            newParamList.append(i)
        self.paramList = newParamList
        self.paramDict["paramList"] = self.paramList

    def read_in_figure_param_file(self):
        '''
        We need to develop a more flexible framework for handling colors.
        - The problem is that with a csv file, we are running into problems with commas in the color name itself. 
 
        Ideas:
        - We can add a color page. 
        - We can add a smart parser. 
            - If it starts with rgb(  )
            - If it has (   ;   ; )
            - If it has #HEX
            - If it has a name
        '''
        fileIN = open(self.figureParamFile)
        startFlag = 0
        for i in fileIN:
            i =i.rstrip().split(",")            
            if startFlag ==0:
                if i[0]=="START": 
                    startFlag +=1
                else:
                    self.figureParamDict[i[0]]  = ",".join(i[1:])
                    if i[0]=="figurekey": self.figurekey = i[1]
                    if i[0]=="figuretype": self.figuretype = i[1]
                    if i[0]=="valuelab": self.valuelab = i[1]
            else:
                if ";" in i[-1]:
                    a = "rgb(" + ",".join(i[-1].replace("(", "").replace(")", "").split(";")) + ")"
                    i[-1]=a
                self.figureMat.append(i)
                
        self.figureParamDict["figureMat"] = self.figureMat

    def prepare_image_files(self, inputDirPath, outDirPath):
        '''
        For the carousel files, we will need to copy the images into the image location.
        '''
        for i in self.paramList:
            if i[0]=="IMAGE": 
                imagePath  = os.path.join(inputDirPath, i[1])
                outputPath = os.path.join(outDirPath, "web", "images", i[1])
                shutil.copyfile(imagePath, outputPath)

    def autofill_figure_mat(self, datasetDict):
        '''
        Description: Auto-fill command for filling in the columns automatically based on meta variables.
        '''
        #Step 1: Create the name and column name dictionary for the main dataset.  
        datasetfilepath = datasetDict[self.datasetkey].datasetfilepath
        with open(datasetfilepath) as F:
            header =F.readline().rstrip().split(",")
        columnNameNumDict = {name: str(x+2)    for x,name in enumerate(header[1:])} #Add one for first column skip. Add one for conversion to column num (not idx)

        #Step 2: Create the header file for the meta file. 
        metadatafilepath  = datasetDict[self.autofillfilekey].datasetfilepath
        #Create a search column and search start match
        colIdx = int(self.autofillcolumn) - 1
        groupDict = dict()
        with open(metadatafilepath) as F:
            F.readline()
            for i in F:
                i =i.rstrip().split(",")
                groupDict[i[0]]  = i[colIdx]

        #Step 3: 
        newFigureMat = list()
        for i in self.paramList:
            if "AUTO" in i[0]:
                groups = set(i[2].split("$"))
                newcols = [columnNameNumDict[x]  for x in groupDict if groupDict[x] in groups ]
                newFigureVec = [i[0][4:], i[1], "$".join(newcols) , i[3]]
                newFigureMat.append(newFigureVec)
            else:
                newFigureMat.append(i)
       
        self.paramList = newFigureMat
        self.paramDict["paramList"] = self.paramList

    def prepare_scatter(self):
        pass

    def prepare_multidim_file(self, datasetDict, outDir):
        '''
        Prepares a multi-dimensional file. 
        - The dataset lookup will be for the z values. 
        - This function creates a file with the x and y values. 
        '''
        metadatakey = self.paramList[0][1]
        metadataset = datasetDict[metadatakey]
        metadatafile = os.path.join(metadataset.inputDir, metadataset.datasetfile)
       
        columnIdx = [int(x)-1 for x in self.paramList[0][2].split("$")]
        
        #Load the dataset file header line to get the info. 
        dataset = datasetDict[self.datasetkey]
        datasetfile = os.path.join(dataset.inputDir, dataset.datasetfile)

        with open(datasetfile) as F:
            header =F.readline().rstrip().split(",")
        columnNameNumDict = {name: str(x+2)    for x,name in enumerate(header[1:])} #Add one for first column skip. Add one for conversion to column num (not idx)

        outpath = os.path.join(outDir, "static", self.figurekey + ".mdscatter.csv")
        with open(outpath, "w") as Fout:
            if metadatafile[-5:]==".xlrd":
                pass
            else:
                with open(metadatafile) as F:
                    F.readline()
                    for i in F:
                        i = i.rstrip().split(",")
                        x,y,z = i[0], i[columnIdx[0]], i[columnIdx[1]]
                        Fout.write(",".join([columnNameNumDict[x],x, y,z]) + "\n")

        self.mdscatterfile = self.figurekey + ".mdscatter.csv"
        self.paramDict["mdscatterfile"]= self.figurekey + '.mdscatter.csv'

    def prepare_density_file(self,datasetDict, outDir):
        '''
        Description: Because a density plot does not need to be recalculated every single time. 
        - We will calculate it beforehand. 
        - We will also create percentile dataset. 
        Notes: And log the histogram
        '''
        print("\tPreparing density file")
        from scipy.stats import gaussian_kde, tstd
        import xlrd
        import math
        columnIdx = [int(x)-1 for x in self.paramList[0][2].split("$")]

        dataset = datasetDict[self.datasetkey]
        datasetfilepath = dataset.datasetfilepath

        NAvals = set(["NA", "", "NAN", "nan", "na", "none", "NaN", "Nan"])
        meanList = list()
        if datasetfilepath[-5:]==".xlsx":
            xl_workbook = xlrd.open_workbook(datasetfilepath)
            xl_sheet = xl_workbook.sheet_by_index(0)
            startRowIndex = 1 ### EDIT HERE
            endRowIndex = xl_sheet.nrows
            num_cols = xl_sheet.ncols   # Number of columns
            outMat = list()
            for row_idx in range(startRowIndex, endRowIndex):    # Iterate through rows
                outVec = list()
                for col_idx in columnIdx:  # Iterate through columns
                    cell_obj = xl_sheet.cell(row_idx, col_idx)  # Get cell object by row, col
                    outVec.append(cell_obj.value)
                vals = [math.log10(float(x)) if float(x) > 0.1 else math.log10(0.1) for x in outVec if x not in NAvals]
                mean = sum(vals)/ len(vals)
                meanList.append(mean)
        else:
            with open(datasetfilepath) as F:
                for i in range(int(dataset.searchstart)):
                    F.readline()
                for line in F:
                    if datasetfilepath[-4:]==".txt": i = line.rstrip().split("\t")
                    if datasetfilepath[-4:]==".csv": i = line.rstrip().split(",")
                    vals = [math.log10(float(i[x])) if float(i[x]) > 0.1 else math.log10(0.1) for x in columnIdx if i[x] not in NAvals]
                    mean = sum(vals)/ len(vals)
                    meanList.append(mean)      

        density = gaussian_kde(meanList, bw_method = 0.2)
        steps = (3 - min(meanList))/1000 #Maximum value will be 3. 
        minVal = min(meanList)
        xvals = [ minVal + x*steps  for x in range(1000)]
        yvals = density(xvals)
        outMat = [ [xvals[x], yvals[x]]  for x in range(len(xvals))]
        
        #Create a vector with percentile values for the 0th, 99th percentile. 
        sortedMeanList = sorted(meanList)
        
        percentileVec = [ sortedMeanList[int(len(meanList)/100.0*i)] for i in range(100)]
        
        outpath = os.path.join(outDir, "static", self.figurekey + ".density.csv")
        with open(outpath, "w") as F:
            F.write(",".join([str(x) for x in percentileVec]) + "\n")
            for i in outMat:
                F.write(",".join([str(x) for x in i]) + "\n")

        self.densityfile = self.figurekey + ".density.csv"
        self.paramDict["densityfile"]= self.figurekey + '.density.csv'


        