#!/usr/bin/env python#!/usr/bin/env python
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


from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from phitools import moleculeHelper as mh
import argparse, sys

sep = '\t'

def compare(args):

    ###########################
    ### Store the compounds ###
    ###########################
    fpType = args.descriptor[0:4]
    fpRadius = int(args.descriptor[4:])

    fpA = mh.getFPdict (args.format, args.filea, molID= args.id, smilesI= args.col, header= args.header, fpType= fpType, radius= fpRadius)
    namesA = list(fpA.keys())
    nA = len(namesA)

    if args.fileb is not None:
        fpB = mh.getFPdict (args.format, args.fileb, molID= args.id, smilesI= args.col, header= args.header, fpType= fpType, radius= fpRadius)
        namesB = list(fpB.keys())
        nB = len(namesB)
    
    #################################
    ### Get compound similarities ###
    #################################

    simD = {}
    if args.sim == 'max': startSim = 0
    else: startSim = 1

    # Work with only one input file
    if args.fileb is None:
        for name in namesA:
            simD[name] = ['', startSim]

        for i in range(nA):
            name1 = namesA[i]
            [fp1, smiles1] = fpA[name1]
            for j in range(i+1, nA):
                name2 = namesA[j]
                [fp2, smiles2] = fpA[name2]
                sim = DataStructs.TanimotoSimilarity(fp1, fp2)
                if args.cutoff is not None and sim < args.cutoff:
                    continue

                if args.sim == 'all':
                    args.out.write('{}\t{}\t{}\t{}\t{}\n'.format(name1, smiles1, name2, smiles2, sim))
                    args.out.write('{}\t{}\t{}\t{}\t{}\n'.format(name2, smiles2, name1, smiles1, sim))
                else:
                    if args.sim == 'max':
                        if sim > simD[name1][1]: simD[name1] = [name2, smiles2, sim]
                        if sim > simD[name2][1]: simD[name2] = [name1, smiles1, sim]
                    else:
                        if sim < simD[name1][1]: simD[name1] = [name2, smiles2, sim]
                        if sim < simD[name2][1]: simD[name2] = [name1, smiles1, sim]

        if args.sim != 'all':
            for name in simD:
                args.out.write('{}\t{}\t{}\t{}\n'.format(name, simD[name][0], simD[name][1], simD[name][2]))

    # Work with two input files
    else:
        for name in namesA:
            simD[name] = [None, '', startSim]
        for name in namesB:
            simD[name] = [None, '', startSim]

        for i in range(nA):
            name1 = namesA[i]
            [fp1, smiles1] = fpA[name1]            
            for j in range(nB):
                name2 = namesB[j]
                [fp2, smiles2] = fpB[name2]

                sim = DataStructs.TanimotoSimilarity(fp1, fp2) #DataStructs.DiceSimilarity(fp1, fp2)
                if args.cutoff is not None and sim < args.cutoff:
                    continue

                if args.sim == 'all':
                    args.out.write('{}\t{}\t{}\t{}\t{}\n'.format(name1, smiles1, name2, smiles2, sim))
                else:
                    if args.sim == 'max':
                        if sim > simD[name1][-1]: simD[name1] = [name2, smiles2, sim]
                    else:
                        if sim < simD[name1][-1]: simD[name1] = [name2, smiles2, sim]

        if args.sim != 'all':
            for name in simD:
                if simD[name][0] is None:
                    continue
                buffer = [name]
                buffer.extend(simD[name])
                args.out.write('{}\n'.format('\t'.join(str(v) for v in buffer)))
                        


def main ():
    parser = argparse.ArgumentParser(description='Get the smilarity between the compounds in the input file if only one is provided or between files if two are provided.')
    parser.add_argument('-a', '--filea', type=argparse.FileType('rb'), help='Input file.', required=True)
    parser.add_argument('-b', '--fileb', type=argparse.FileType('rb'), help='Optional input file. If it is provided he compounds in this file will be compared to the compounds in the first input file.')
    parser.add_argument('-f', '--format', action='store', dest='format', choices=['smi', 'sdf'], default='smi', help='Specify the input format (smiles strings (default) or SD file).')
    parser.add_argument('-s', '--sim', action='store', choices=['min', 'max', 'all'], default='max', help='Get only the closest compounds (\'max\', default), the most dissimilar (\'min\'), or all v all similarties (\'all\')')
    parser.add_argument('-d', '--descriptor', action='store', dest='descriptor', default='ecfp4', help='Specify the descriptor to be used in the similarity calculation (ecfp4 (default), fcfp4, ecfp2, etc.).')
    parser.add_argument('-c', '--cutoff', type=float, help='If wanted, set a minimum similarity cutoff.')
    parser.add_argument('-i', '--id', type=str, help='Field containing the molecule ID. If it is not provided for the SD file format, the SD file compound name will be used.')
    parser.add_argument('-x', '--col', type=int, default=1, help='If the input file has smiles, indicate which column contains the smiles strings.')
    parser.add_argument('-n', '--noheader', action='store_false', dest='header', help='Smiles input data file doesn\'t have a header line.')
    parser.add_argument('-o', '--out', type=argparse.FileType('w+'), default='output.txt', help='Output file name (default: output.txt)')
    args = parser.parse_args()
    
    if args.format == 'smi':
        if args.col is not None:
            args.col -= 1

    if args.format == 'smi' and args.id is not None:
        try:
            args.id = int(args.id)-1
        except:
            sys.stderr('The ID argument must be a column index if the input file is of smiles format.\n')
            sys.exit()

    compare(args)    

if __name__ == '__main__':    
    main()