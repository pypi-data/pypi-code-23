#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Description    Tool for extracting data within an SDFile
##                   
##    Authors:       Manuel Pastor (manuel.pastor@upf.edu) 
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

import os, sys, argparse
from rdkit import Chem
from phitools import moleculeHelper as mh

def extractAll (args):

    fields = set()
    # Cycle through all molecules to make sure all field names are stored
    suppl = Chem.ForwardSDMolSupplier(args.sdf)
    bufferD = {}
    names = []  # Store names on a list to preserve the order in the SD file
    count = 0
    # Get all information in SD file
    for m in suppl:
        count += 1
        if m is None: continue
        fields = fields.union(set(m.GetPropNames())) # Store all field names in the SD file
        name = mh.getName(m, count)
        bufferD[name] = mh.getProperties(m)
        names.append(name)

    fields = list(fields)
    header = ['Name']
    header.extend(fields)
    args.out.write('{}\n'.format('\t'.join(header)))
    
    suppl = Chem.ForwardSDMolSupplier(args.sdf)
    for name in names:
        line = [name]
        for field in fields:
            if field in bufferD[name]:
                value = bufferD[name][field]
            else:
                value = 'NA'
            line.append(str(value))
        args.out.write('{}\n'.format('\t'.join(line)))

def extractField (args):
    # Write header in output file
    args.out.write('{}\n'.format('\t'.join(['Name', args.field])))

    # Get data and print to output file
    suppl=Chem.ForwardSDMolSupplier(args.sdf)
    count = 0
    for m in suppl:
        count += 1
        if m is None: continue
        name = mh.getName(m, count)
        if m.HasProp (args.field):
            value = m.GetProp(args.field)
        else:
            value = 'NA'
        args.out.write('{}\n'.format('\t'.join([name, value])))

def extractNames (args):
    suppl=Chem.ForwardSDMolSupplier(args.sdf)
    count = 0
    for m in suppl:
        count +=1
        if m is None: continue
        name = mh.getName(m, count)
        args.out.write('{}\n'.format(name))


def main ():

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-i', '--sdf', type=argparse.FileType('rb'), help='SD file', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--all', action='store_true', help='Extract data in all fields (default).')
    group.add_argument('-f', '--field', type=str, help='Extract only the data in this field of the SD file.')
    group.add_argument('-n', '--name', action='store_true', help='Extract molecule names.')
    parser.add_argument('-o', '--out', type=argparse.FileType('w'), default='output.txt', help='Output file name (default: output.txt)')
    args = parser.parse_args()

    if args.name:
        extractNames (args)
    elif args.field:
        extractField (args)
    else:
        extractAll (args)

    args.sdf.close()
    args.out.close()
    
        
if __name__ == '__main__':
    
    main()
