#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Description    Tool for generating a SDFile from diverse sources
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

import urllib.request, urllib.parse, urllib.error
import os, sys, argparse

from rdkit import Chem
from rdkit.Chem import AllChem, SaltRemover
remover = SaltRemover.SaltRemover()

from phitools import moleculeHelper as mh
from compoundDB import querytools as qt
from compoundDB import inputtools as it

try:
    __import__('EPA')
except ImportError:
    useEPA = False
    sys.stderr.write('\n*** Could not find EPA module. Will use only the CACTVS web service. ***\n\n')
else:
    useEPA = True
    from EPA import comptox_lookup, comptox_link

def writeStructure(q, mol, args):

    if args.format == 'sdf':
        if type(mol) is str:
            try:
                mol = Chem.MolFromSmiles(mol)
                Chem.AllChem.Compute2DCoords(mol)
            except:
                sys.stdout.write('Error processing', q)

        mh.writeSDF(mol, args.out, {args.field: q}, q)
        
    elif args.format == 'smi':
        args.out.write('{}\n'.format('\t'.join([q, mol])))


def getStructure(args):
    #out,data,iformat,idname,header):

    if args.header: args.data.readline()  # Skip header
        
    queries = set([line.rstrip().split('\t')[args.column].strip() for line in args.data if len(line.rstrip().split('\t')) > args.column])
    args.data.close()

    # for inchis use RDKit to get the structure
    if args.type == 'inchis':
        for q in queries:
            try:
                mol = Chem.inchi.MolFromInchi (q)
                if args.removesalts:
                    mol = SaltRemover.StripMol(mol,dontRemoveEverything=True)
                AllChem.Compute2DCoords(mol)
            except:
                sys.stdout.write('Error processing {}\n'.format(q))
                pass
            writeStructure(q, mol, args)

    # for names ...
    else:
        # First try using compounds DB to retrieve the SMILES
        try:
            conn = it.openconnection(host='172.20.16.76', dbname='compounds', user='postgres', password=args.dbpass)
        except:
            sys.stdout.write('Could not connect to the compound DB.\n')
        else:
            # If the connection to the compounds DB is available check there first if the structures have already been resolved
            df = qt.getSubstancesFromSynonyms(conn, queries)
            df = df[['synonym', 'smiles']]
            dfound = df.dropna().groupby('synonym').first().reset_index()
            for index, row in dfound.iterrows():
                writeStructure(row['synonym'], row['smiles'], args)

            # Keep the ones that could not be resolved
            queries = queries.difference(set(dfound['synonym']))

        for q in queries:
            # Then try using the CACTVS web service to retrieve the SMILES
            try:
                smi = urllib.request.urlopen('http://cactus.nci.nih.gov/chemical/structure/'+q+'/smiles')
                smi = smi.readline().decode("utf-8").rstrip().replace('|', '')
            except:
                smi = ''
                
            # And finally try to use Francis Atkinson's code to call EPA if it's available
            if useEPA and smi == '':
                print ('EPA')
                try:
                    tmp = comptox_lookup(q)
                except:
                    sys.stdout.write('Connection error at molecule {}\n'.format(q))
                    tmp = None
                    
                if tmp is not None:
                    smi = tmp.smiles
                else:
                    sys.stdout.write('Could not resolve {}\n'.format(q))
                    smi = ''
            
            if args.removesalts:
                try:
                    mol = Chem.MolFromSmiles(smi)
                    mol = remover.StripMol(mol,dontRemoveEverything=True)
                except:
                    pass
                else:
                    smi = Chem.MolToSmiles(mol)
            writeStructure(q, smi, args)
    args.out.close()

def main ():

    parser = argparse.ArgumentParser(description='Get the structure of the compounds in the input data file.')
    parser.add_argument('-d', '--data', type=argparse.FileType('r'), required=True, help='File with molecule identifiers.')
    parser.add_argument('-c', '--column', type=int, default=1, help='Column in the input file that contains the molecule identifiers (default= 1).')
    parser.add_argument('-n', '--noheader', action='store_false', dest='header', help='Input data file doesn\'t have a header line.')
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('-x', '--identifier', action='store_const', dest='type', const= 'id', help='The input format will be compound indentifiers (default).', default= 'identifier')
    group1.add_argument('-i', '--inchis', action='store_const', dest='type', const= 'inchi', help='The input format will be molecule InChis.')
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('-s', '--smi', action='store_const', dest='format', const='smi', default='smi', help='The output format is a file with smiles strings (default).')
    group2.add_argument('-m', '--sdf', action='store_const', dest='format', const='sdf', help='The output format is an SD file.')
    parser.add_argument('-r', '--removesalts', action='store_true', help='Remove salts from the structure.')
    parser.add_argument('-f', '--field', type=str, default='name', help='Field in the output SD file that will contain the unique ID (default= name).')
    parser.add_argument('-p', '--dbpass', type=str, help='Password to connect to the compound DB.')
    parser.add_argument('-o', '--out', type=argparse.FileType('w+'), default='output.txt', help='Output file name (default: output.txt)')
    args = parser.parse_args()
    
    args.column = args.column-1
    
    getStructure(args)    

if __name__ == '__main__':    
    main()
