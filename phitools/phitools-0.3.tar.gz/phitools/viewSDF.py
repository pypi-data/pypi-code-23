#!/usr/bin/env python
# -*- coding: utf-8 -*-

##    Description    Visualize a SDFile as a web page
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
from rdkit.Chem import AllChem,Draw,Descriptors
import os, sys, getopt

def viewSDF (sdf_id,out_id,prop_id):

    # Read SDF
    suppl = Chem.SDMolSupplier(sdf_id)

    # Create directory to save images
    imagedir =  os.path.basename(out_id).split('.')[0]
    imagedir += '_images/'
    if not os.path.exists(imagedir):
        os.makedirs(imagedir)

    # Create a list containing the sdf data
    counter=1
    l=[]

    # Create header
    l.append(['#','structure',prop_id])
        
    for mol in suppl:
        l1=[]
        l1.append(str(counter)) # counter is created, even if no mol was found
        
        if not (mol is None): 

            name = 'mol%0.8d'%counter # fallback name
            try:
                name=mol.GetProp(prop_id)
            except:
                pass

            Draw.MolToFile(mol,imagedir+name+'.png')
            
            #l1.append('<img src="'+imagedir+name+'.png" height=200 width=200>')
            l1.append('<img src="'+imagedir+name+'.png" ')
            l1.append(name)

        l.append(l1)
        counter+=1
        
    saveListAsHTML(l, out_id)
        
def saveListAsHTML(l,out):

    fo = open (out,'w+')

    fo.write ('<html xmlns="http://www.w3.org/1999/xhtml">'+
              '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'+
              '<title>'+out+'</title></head><body>')
  
    fo.write('<table border="1">\n')

    for column in l:
        fo.write('<tr>',)    
        for i in column:
            fo.write('<td>'+i+'</td>')      
        fo.write('</tr>\n')
        
    fo.write('</table></body></html>')
    fo.close()

def usage ():
    """Prints in the screen the command syntax and argument"""
    print('viewSDF [-f file.sdf] [-o output.html] [--name=name]')
    sys.exit(1)

def main ():
    sdf = None
    out = 'output.html'
    prop = 'name'
    
    try:
       opts, args = getopt.getopt(sys.argv[1:],'f:o:', ['name='])
    except getopt.GetoptError:
       usage()
       print("False, Arguments not recognized")
       sys.exit(1)

    if len(opts)>0:
        for opt, arg in opts:
            if opt in '-f':
                sdf = arg
            elif opt in '-o':
                out = arg
            elif opt in '--name':
                prop = arg

    if sdf is None:
        usage()

    viewSDF(sdf,out,prop)

if __name__ == '__main__':    
    main()
