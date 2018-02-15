#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Description    Tool for finding duplicates in an SDFile
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
from rdkit import RDLogger
from rdkit.Chem import AllChem,Draw,Descriptors
from phitools import moleculeHelper as mh
import os, sys, argparse

sep = '\t'

def findDuplicates (args): 

    lg = RDLogger.logger()
    lg.setLevel(RDLogger.ERROR)

    idlist = []
    nmlist = []
    smlist = []

    counter = 0
    if args.type == 'smi':  
        sys.stdout.write('reading file with smiles...\n')
        if args.header:
            args.fn.readline()
        for line in args.fn:
            fields = line.decode('utf-8').rstrip().split(sep)
            if len(fields) > args.col:
                smiles = fields[args.col]
            else:
                continue
            mol = Chem.MolFromSmiles(smiles)
            counter+=1

            if mol is None: continue
            try:
                inchi = Chem.MolToInchi(mol)
                inkey = Chem.InchiToInchiKey(inchi)
            except:
                continue

            name = fields[args.id]

            idlist.append(inkey[:-3])
            nmlist.append(name)
            smlist.append(smiles)

    else:
        # SD file
        sys.stdout.write('reading SDFile...\n')
        suppl = Chem.ForwardSDMolSupplier(args.fn,removeHs=False, sanitize=False)

        for mol in suppl:
            counter+=1
        
            if mol is None: continue
            try:
                inchi = Chem.MolToInchi(mol)
                inkey = Chem.InchiToInchiKey(inchi)
                smiles = Chem.MolToSmiles(mol)
            except:
                continue

            name = mh.getName(mol, count= counter, field= args.id)

            idlist.append(inkey[:-3])
            nmlist.append(name)
            smlist.append(smiles)
    args.fn.close()
    
    n = len(idlist)

    sys.stdout.write('analizing duplicates...\n')

    args.out.write('{}\n'.format('\t'.join(['i', 'j', 'namei', 'namej', 'smilesi', 'smilesj'])))  # Header
    duplicates = 0
    for i in range (n):
        for j in range (i+1,n):
            if idlist[i]==idlist[j]:
                args.out.write('{}\n'.format('\t'.join([str(i), str(j), nmlist[i], nmlist[j], smlist[i], smlist[j]])))
                duplicates+=1
    args.out.close()

    sys.stdout.write('\n%d duplicate molecules found\n' %duplicates)

def main ():

    parser = argparse.ArgumentParser(description='Find duplicated molecules. In the output file, the first columns present the properties of the first molecule duplicated, the last columns contain data about the second molecule identified.')
    parser.add_argument('-f', '--fn', type=argparse.FileType('rb'), help='Input file', required=True)
    parser.add_argument('-i', '--id', type=str, help='If the input is an SD file, specify the field (if any) with the molecule ID. If the input has smiles, specify the column with the molecule ID.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--smi', action='store_const', dest='type', const='smi', default='smi', help='The input format is a file with smiles strings (default).')
    group.add_argument('-m', '--sdf', action='store_const', dest='type', const='sdf', help='The input format is an SD file.')
    parser.add_argument('-c', '--col', type=int, default=1, help='If the input file has smiles, indicate which column contains the smiles strings.')
    parser.add_argument('-n', '--noheader', action='store_false', dest='header', help='Input data file doesn\'t have a header line.')
    parser.add_argument('-o', '--out', type=argparse.FileType('w'), default='duplicates.txt', help='Output file name (default: duplicates.txt)')
    args = parser.parse_args()

    if args.type == 'smi':
        try:
            args.id = int(args.id)-1
            args.col = args.col-1
        except:
            sys.stderr.write('If the input file has smiles strings, the id field (-i) must contain the index of the column with the comound identifier.\n')
            sys.exit()

    findDuplicates(args)
    
if __name__ == '__main__':    
    main()
