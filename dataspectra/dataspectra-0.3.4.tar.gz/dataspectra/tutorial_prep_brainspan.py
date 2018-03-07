#!/usr/bin/env python2.7

from __future__ import print_function

import sys, os
import argparse

'''
Create a dataset file 1 - Meta.
Create a dataset file 2 - Meta.

Create a file with dataset2. 
DonorID on the column headers. 
GeneNames on  the row headers. 

DataExpression:   Add column names. 

'''


def create_main_dataset(fileDirectoryPath, fileExpOut, fileMetaOut ):
    #Read in column file
    fileCol = os.path.join(fileDirectoryPath, "columns_metadata.csv")
    colMat = list()
    with open(fileCol) as F:
        header = F.readline().rstrip().split(',')
        colMat.append(header)
        colDict = dict()
        for i in F:
            i = i.rstrip().split(',')
            colDict[i[0]] = i
            colMat.append(i)

    #Read in row file
    fileRow = os.path.join(fileDirectoryPath, "rows_metadata.csv")
    ids2keep = list()
    gene2include = {"SOX4", "HSD11B1", "ARX"}
    with open(fileRow) as F:
        header  = F.readline()
        rowDict = dict()
        rowInvDict = dict()
        for i in F:
            i = i.rstrip().split(',')
            geneName = i[3].replace('"', "")
            rowDict[i[0]] =  geneName
            if geneName in gene2include:
                ids2keep.append(i[0])

    sampleMat = list()
    counter = 0
    #Create big data file while reading in the old file.
    #Make sure to output SOX4 , HSD11B1, ARX
    #Also output random set of genes. 
    import random 
    ids2keep += random.sample(rowDict.keys(),500)
    ids2keep = set(ids2keep)

    with open(fileExpOut, "w") as Fout:
        #Write header line
        headerline =  [x[2] for x in colMat]
        headerline[0] = "gene"
        Fout.write(",".join(headerline) + "\n")
        sampleMat.append(headerline)
        fileExp = os.path.join(fileDirectoryPath, "expression_matrix.csv")
        with open(fileExp) as F:
            for i in F:
                i = i.rstrip().split(',')
                if i[0] in ids2keep:
                    geneName = rowDict[i[0]]
                    i[0] = geneName
                    Fout.write(",".join(i) + "\n")
                    counter +=1
#                    if counter < 100:  
#                        sampleMat.append(i)
   
    #Create a sample file
#    with open(fileExpOut.replace(".csv", ".sample.csv"), "w") as Fsample:
#        for i in sampleMat:
#            Fsample.write(",".join(i) + "\n")
    
    #Create metadata file. Transpose, remove quotes, and add a new age
    metaMat = list()
    outVecAge = list()
    for colidx in range(len(colMat[0])):
        outVec = list()
        for rowidx in range(len(colMat)):
            val = colMat[rowidx][colidx].replace('"', "")
            outVec.append(val)
            if colidx==3:
                if rowidx==0:
                    outVecAge.append("ageNum")
                else:
                    outVecAge.append(str(convert_age_values_to_number(val)))
        metaMat.append(outVec)
    metaMat.append(outVecAge)

    with open(fileMetaOut, "w") as Fout:
        for i in metaMat:
            Fout.write(",".join(i) + "\n")

def convert_age_values_to_number(age):
    if "pcw" in age:
        return 0
    if "mos" in age:
        return float(age.split()[0].replace('"', ""))/12.0
    else:
        return age.split()[0].replace('"', "")


def prep_brainspan():
    defaultDirectoryPath = os.path.dirname(os.path.realpath(__file__))
    defaultExpOut = os.path.join(defaultDirectoryPath, "ds.tutorial.data.csv")
    defaultMetaOut = os.path.join(defaultDirectoryPath, "ds.tutorial.metadata.csv")
    parser = argparse.ArgumentParser(description= "prep brainspan data for dataspectra tutorial")
    parser.add_argument("-dir", help="Directory for brain span", default=defaultDirectoryPath)
    parser.add_argument("-exp", help="Output path for expression", default=defaultExpOut)
    parser.add_argument("-meta", help="Output path for meta", default= defaultMetaOut)
    args = parser.parse_args() 
    create_main_dataset(args.dir, args.exp, args.meta )


if __name__=="__main__":
    prep_brainspan()
