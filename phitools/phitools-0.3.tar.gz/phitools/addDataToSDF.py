#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Description    Add Data to SDFile
##                   
##    Authors:       Inés Martínez (mmartinez4@imim.es)
##                   Manuel Pastor (manuel.pastor@upf.edu)
##
##    Copyright 2015 Manuel Pastor
##
##    This file is part of PhiTools
##
##    PhiTools is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation version 3.
##
##    PhiTools is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with PhiTools.  If not, see <http://www.gnu.org/licenses/>

from rdkit import Chem
import os, sys, re, argparse
from phitools import moleculeHelper as mh

sep = '\t'

def addData (args):
    
    ##############################################
    # Search compound ID column in the data file #
    ##############################################
    header = args.data.readline().rstrip().split(sep)  
    if not args.id in header:        
        for col in header:
            match=re.search(args.id[:5], col)
            if match:
                sys.stderr.write("Molecule identifier not found among data file\'s column names, please try again. However, a similar column name was found: {}\n".format(col))
                return
            else:
                match=re.search(args.id[len(args.id)-5:], col)
                if match:
                    sys.stderr.write("Molecule identifier not found among data file\'s column names, please try again. However, a similar column name was found: {}\n".format(col))
                    return                
        #not found 
        if col == header[-1]:
            sys.stderr.write("Molecule identifier not found among data file\'s column names.\n")
            return
    else:
        ind=header.index(args.id)

    ###################
    # Read data file
    ###################
    dataD = {}
    for line in args.data:
        line=line.rstrip().split(sep)
        dataD[line[ind]] = {header[i]:line[i] for i in range(len(header)) if i != ind}      
    args.data.close()  
        
    ###################
    # Process SDFile  #
    ###################
  
    suppl = Chem.ForwardSDMolSupplier(args.sdf, removeHs=False, sanitize=False)

    inL = 0
    outL = 0    
    for mol in suppl:

        inL += 1
        if mol is None: continue
            
        cmpdID = mh.getName(mol, field= args.id)
        propD = mh.getProperties(mol)
            
        if cmpdID not in dataD:
            # Add empty fields
            for field in dataD[cmpdID]:
                if field not in propD:
                    propD[field] = 'NA'
            outL += 1
            mh.writeSDF(mol, args.out, propD, ID=cmpdID)
        else:
            # Add field values from the data file
            for field in dataD[cmpdID]:
                fieldValue = dataD[cmpdID][field]
                if field in propD:
                    field = field+' (1)'
                propD[field] = fieldValue
            outL += 1
            mh.writeSDF(mol, args.out, propD, ID=cmpdID)
        
    args.sdf.close()
    args.out.close()
    
    sys.stdout.write("Input file has {} molecules\n".format(inL))
    sys.stdout.write("Output file has {} molecules\n".format(outL))

def main ():

    parser = argparse.ArgumentParser(description='Add data from an input table into SD file fields. The data file must be a tab separated file with a single line header. One of the columns must contain a unique id, present also in the SDFile, which is used for the matching. This field can be specified using the parameter -i | --id.')
    parser.add_argument('-f', '--sdf', type=argparse.FileType('rb'), help='SD file', required=True)
    parser.add_argument('-d', '--data', type=argparse.FileType('r'), help='Data file', required=True)
    parser.add_argument('-i', '--id', type=str, help='Field containing the moleculeID. If the field is not found in the SD file, the molecule name will be used instead.')
    parser.add_argument('-o', '--out', type=argparse.FileType('w'), default='output.sdf', help='Output file name (default: output.sdf)')
    args = parser.parse_args()

    addData(args)    

if __name__ == '__main__':    
    main()
