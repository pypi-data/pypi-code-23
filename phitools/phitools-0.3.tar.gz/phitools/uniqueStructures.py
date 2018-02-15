#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Description    Tool for removing duplicates in an SDFile
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

from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Draw, Descriptors
from phitools import moleculeHelper as mh
import os, sys, argparse

sep = '\t'

def writeStructure(q, mol, args):

    if args.sdf:
        if type(mol) is str:
            try:
                mol = Chem.MolFromSmiles(mol)
                Chem.AllChem.Compute2DCoords(mol)
            except:
                sys.stdout.write('Error processing', q)

        mh.writeSDF(mol, args.out, {args.field: q}, q)
        
    elif args.smi:
        args.out.write('{}\n'.format('\t'.join([q, mol])))

def findDuplicates (args): 

    lg = RDLogger.logger()
    lg.setLevel(RDLogger.ERROR)

    iddict = {}

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

            if mol is None: continue
            try:
                inchi = Chem.MolToInchi(mol)
                inkey = Chem.InchiToInchiKey(inchi)[:-3]
            except:
                continue

            name = fields[args.id]

            if inkey not in iddict:
                iddict[inkey] = [[name], smiles]
            else:
                iddict[inkey][0].append(name)

    else:
        # SD file
        sys.stdout.write('reading SDFile...\n')
        suppl = Chem.ForwardSDMolSupplier(args.fn,removeHs=False, sanitize=False)

        counter = 0
        for mol in suppl:
            counter+=1
        
            if mol is None: continue
            try:
                inchi = Chem.MolToInchi(mol)
                inkey = Chem.InchiToInchiKey(inchi)[:-3]
                smiles = Chem.MolToSmiles(mol)
            except:
                continue

            name = mh.getName(mol, count= counter, field= args.id)

            if inkey not in iddict:
                iddict[inkey] = [[name], smiles, mol]
            else:
                iddict[inkey][0].append(name)
    args.fn.close()
    
    n = len(iddict)

    sys.stdout.write('\n%d unique molecules found\n' %n)

    if args.type == 'smi':
        # Write header
        args.out.write('{}\n'.format('\t'.join(['smiles', 'InChI key', 'IDs'])))

    for inkey in iddict:
        ids = '; '.join(iddict[inkey][0])
        smiles = iddict[inkey][1]

        if args.type == 'smi':
            args.out.write('{}\n'.format('\t'.join([smiles, inkey, ids])))
        else:
            mol = iddict[inkey][2]
            fieldsD = {'IDs': ids, 'InChI key': inkey, 'smiles': smiles}
            mh.writeSDF(mol, args.out, fieldsD, inkey)
    args.out.close()

def main ():

    parser = argparse.ArgumentParser(description='Find duplicated molecules. In the output file, the first columns present the properties of the first molecule duplicated, the last columns contain data about the second molecule identified.')
    parser.add_argument('-f', '--fn', type=argparse.FileType('rb'), help='Input file', required=True)
    parser.add_argument('-i', '--id', type=str, help='If the input is an SD file, specify the field (if any) with the molecule ID. If the input has smiles, specify the column with the molecule ID.')
    parser.add_argument('-x', '--format', action='store', dest='type', choices=['smi', 'sdf'], default='smi', help='Specify the input format (smiles strings (default) or SD file).')
    parser.add_argument('-c', '--col', type=int, default=1, help='If the input file has smiles, indicate which column contains the smiles strings.')
    parser.add_argument('-n', '--noheader', action='store_false', dest='header', help='Input data file doesn\'t have a header line.')
    parser.add_argument('-o', '--out', type=argparse.FileType('w'), default='unique.txt', help='Output file name (default: unique.txt)')
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
