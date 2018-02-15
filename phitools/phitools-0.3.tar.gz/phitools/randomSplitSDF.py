#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Description    Split an SDFile randomly in a two datasets
##                   
##    Authors:       Manuel Pastor (manuel.pastor@upf.edu)
##
##    Copyright 2016 Manuel Pastor
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
import os, sys, argparse
import numpy as np
from phitools import moleculeHelper as mh

def splitSDF (args):
#(sdf, prop, seed):

    args.fn.close()

    # Count number of molecules
    if args.type == 'sdf':
        suppl = Chem.SDMolSupplier(args.fn.name)
        nmols = len(suppl)
    else:
        with open(args.fn.name) as f:
            for nmols, l in enumerate(f):
                pass
        if args.header:
            nmols -= 1

    ntrai = int(np.round(args.prop*nmols/100.0))
    npred = nmols - ntrai
    
    print (nmols, "compounds found. Creating series of ", ntrai, " for training and ", npred, " for prediction")

    if args.seed != None :
        npseed = int(seed)
        np.random.seed(npseed)
        
    elements = np.random.choice(nmols, ntrai, False)
    moli = 0
    
    fp = open ('pr-'+args.fn.name,'w')
    ft = open ('tr-'+args.fn.name,'w')
    if args.type == 'sdf':
        for mol in suppl:
            if mol is None: continue
            if moli in elements :
                mh.writeSDF(mol, ft)
            else:
                mh.writeSDF(mol, fp)
            moli += 1
    else:
        with open(args.fn.name) as f:
            if header:
                line = f.readline()
                ft.write(line)
                fp.write(line)
            for line in f:
                if moli in elements :
                    ft.write(line)
                else:
                    fp.write(line)
                moli += 1
    fp.close()
    ft.close()

def usage ():
    """Prints in the screen the command syntax and argument"""
    print('randomSplitSDF -f file.sdf -p 70 [-s 2356]')
    sys.exit(1)

def main ():
    parser = argparse.ArgumentParser(description='Rndomly split he input file into the given number of chunks.')
    parser.add_argument('-f', '--fn', type=argparse.FileType('rb'), help='Input file', required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--smi', action='store_const', dest='type', const='smi', default='smi', help='The input format is a file with smiles strings (default).')
    group.add_argument('-m', '--sdf', action='store_const', dest='type', const='sdf', help='The input format is an SD file.')
    parser.add_argument('-c', '--col', type=int, default=1, help='If the input file has smiles, indicate which column contains the smiles strings.')
    parser.add_argument('-i', '--id', type=str, help='If the input is an SD file, specify the field (if any) with the molecule ID. If the input has smiles, specify the column with the molecule ID.')
    parser.add_argument('-n', '--noheader', action='store_false', dest='header', help='Input data file doesn\'t have a header line.')
    parser.add_argument('-d', '--seed', type=str, help='Seed for random generation.')
    parser.add_argument('-p', '--prop', type=int, help='Percentage of molecules to use as training set.')
    args = parser.parse_args()

    splitSDF(args)    

if __name__ == '__main__':    
    main()

