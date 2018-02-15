#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Description    Add molecular information to a data file
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
from phitools import moleculeHelper as mh
import os, sys, argparse, re

sep = '\t'

def fields2file (args): 
  
    suppl = Chem.ForwardSDMolSupplier(args.sdf,removeHs=False, sanitize=False)
    molL = []
    propS = set([])
    for mol in suppl:
        # Store all molecules' field names to write the output file's header
        if mol is None: continue
        propS = propS.union(set(mh.getProperties(mol).keys()))
        molL.append(mol)

    propL = ['ID']
    tmp = list(propS)
    if args.id is not None:
        tmp.remove(args.id)
    propL.extend(tmp)
    args.out.write('{}\n'.format(sep.join(propL)))

    count = 0
    for mol in molL:
        count += 1
        name = mh.getName(mol, count= count, field= args.id)
        propD = mh.getProperties(mol)
        
        line = [name]
        for prop in propL[1:]:
            if prop in propD:
                line.append(str(propD[prop]).replace('\n', '; '))
            else:
                line.append('N/A')

        args.out.write('{}\n'.format(sep.join(line)))
        
    args.out.close()

def main ():
    parser = argparse.ArgumentParser(description='Write data from an input SD file\'s fields into a table file.')
    parser.add_argument('-f', '--sdf', type=argparse.FileType('rb'), help='SD file', required=True)
    parser.add_argument('-i', '--id', type=str, help='Field containing the molecule ID. If it is not provided, the SD file compound name will be used.')
    parser.add_argument('-o', '--out', type=argparse.FileType('w+'), default='output.txt', help='Output file name (default: output.txt)')
    args = parser.parse_args()

    fields2file(args)    

if __name__ == '__main__':    
    main()
