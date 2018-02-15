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

from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from standardiser import standardise
from compoundDB import querytools as qt

from pathlib import Path
import sys, os, tempfile

try:
    __import__('EPA')
except ImportError:
    useEPA = False
    sys.stderr.write('\n*** Could not find EPA module. Will use only the CACTVS web service to resolve CAS number structures. ***\n\n')
else:
    useEPA = True
    import EPA

rand_str = lambda n: ''.join([random.choice(string.ascii_lowercase) for i in range(n)])

def resolveCAS(cas, conn=None):
    # First try using compounds DB to retrieve the SMILES
    if not conn:
        sys.stdout.write('Could not connect to the compound DB.\n')
    else:
        # If the connection to the compounds DB is available check there first if the structures have already been resolved
        smi = qt.getStructureFromSyn(conn, cas)

    
    # Then try using the CACTVS web service to retrieve the SMILES
    try:
        smi = urllib.request.urlopen('http://cactus.nci.nih.gov/chemical/structure/'+cas+'/smiles')
        smi = smi.readline().decode("utf-8").rstrip().replace('|', '')
        smi = smi.readline().decode("utf-8").rstrip()
    except:
        smi = ''
        
    # And finally try to use Francis Atkinson's code to call EPA if it's available
    if useEPA and smi == '':
        try:
            tmp = EPA.comptox_lookup(cas)
        except:
            sys.stdout.write('Connection error at molecule {}\n'.format(cas))
            tmp = None
            
        if tmp is not None:
            smi = tmp.smiles
        else:
            sys.stdout.write('Could not resolve {}\n'.format(cas))
            smi = None
            
    return smi
    
def getSmiSupplier(fname, molID, smilesI, header):
    with open(fname) as f:
        if header: f.readline()
        suppl = []
        for line in f:
            fields = line.rstrip().split('\n')
            smi = fields[smilesI]
            id = fields[molID]

            try:
                mol = Chem.MolFromSmiles(smi)
            except:
                continue
            if mol is not None:
                setName(mol, id)
            suppl.append(mol)
    
    return suppl

def morgan(mol, fpType, r=4):
    # r is the radius parameter. For instance, r=4 will yield ECFP4 or FCFP4 fingerprints
    if fpType == 'fcfp': feat = True
    else: feat = False

    return AllChem.GetMorganFingerprint(mol,r,useFeatures=feat)

def getFP(mol, fpType, r=4):
    if fpType in ('ecfp', 'fcfp'):
        return morgan(mol, fpType, r)

def getFPdict_smi (fh, molID= None, fpType= 'ecfp', radius= 4, smilesI= 1, header= False):

    if header:
        fh.readline()
        
    fpD = {}
    count = 0
    for line in fh:
        count += 1
        fields = line.decode('utf-8').rstrip().split('\t')
        if len(fields) > smilesI:
            smiles = fields[smilesI]
        else: continue
        mol = Chem.MolFromSmiles(smiles)
        if mol is None: continue

        if molID is not None and len(fields) > molID: name = fields[molID]
        else: name = 'mol%0.8d'%count

        mh=Chem.AddHs(mol, addCoords=False)
        fp = getFP(mh, fpType, radius)

        fpD[name] = [fp, smiles]
    
    return fpD

def getFPdict_sdf (fh, molID= None, fpType= 'ecfp', radius= 4):

    suppl = Chem.ForwardSDMolSupplier(fh,removeHs=False)
    fpD = {}
    count = 0
    for mol in suppl:
        count += 1
        if mol is None: continue
        name = getName(mol, count, molID)
        mol.UpdatePropertyCache(strict=False)
        mh=Chem.AddHs(mol, addCoords=True)
        fpD[name] = [getFP(mh, fpType, radius), Chem.MolToSmiles(mol)]
    
    return fpD

def getFPdict_pandas (df, molID= 'mol', fpType= 'ecfp', radius= None):

    fp = '{}.{}'.format(fpType, radius)
    fpD = [ getFP(Chem.AddHs(mol, addCoords=False), fpType, radius) \
              for mol in df[molID] ]
    
    return fpD

def getFPdict (inFormat, fh, molID= None, smilesI= None, fpType= 'ecfp', radius= 4, header= False):

    if inFormat == 'smi':
        if molID is not None:
            try:
                molID = int(molID)
            except:
                print ('The ID argument must be a column index if \
                the input file is of smiles format.\n')
                sys.exit()
        return getFPdict_smi (fh, molID= molID, smilesI= smilesI, fpType= fpType, radius= radius, header= header)
    elif inFormat == 'sdf':
        return getFPdict_sdf (fh, molID, fpType, radius)
    elif inFormat == 'df':
        return getFPdict_pandas (fh, molID, fpType, radius)

#def sim(fp1, fp2, simType='Tanimoto'):
#    if simType == '':
#    return 

def RemoveSalts(mol, fh):
    f = open('HighQuality.smi')
    o = open('HighQuality.NoSalts.smi', 'w')
    remover = SaltRemover.SaltRemover()
    for line in f:
        cas, smi = line.rstrip().split('\t')
        try:
            mol = Chem.MolFromSmiles(smi)
            mol = remover.StripMol(mol,dontRemoveEverything=True)
        except:
            pass
        else:
            smi = Chem.MolToSmiles(mol)
        fh.write('{}\t{}\n'.format(cas, smi))
    o.close()

def getName(mol, count=1, field=None, suppl= None):

    if not mol and suppl:
        # The molecule object is empty but it comes from an 
        # SD file and the suppl is provided
        name = getNameFromEmpty(suppl, count, field)
    else:
        name = ''

        if field and mol.HasProp (field):
            name = mol.GetProp(field)
        else:
            name = mol.GetProp('_Name')
            
        if name == '':
            name = 'mol%0.8d'%count

        # get rid of strange characters
        #name = name.decode('utf-8')
        #name = name.encode('ascii','ignore')  # use 'replace' to insert '?'

        if ' ' in name:
            name = name.replace(' ','_')

    return name

def getNameFromEmpty(suppl, count=1, field=None):

    molText = suppl.GetItemText(count)
    name = ''
    if field is not None:
        fieldName = '> <%s>' %field
        found = False
        for line in molText.split('\n'):
            if line.rstrip() == fieldName:
                found = True
                continue
            if found:
                name = line.rstrip()
                break
    else:
        name = molText.split('\n')[0].rstrip()
        
    if name == '':
        name = 'mol%0.8d'%(count+1)

    # get rid of strange characters
    #name = name.decode('utf-8')
    #name = name.encode('ascii','ignore')  # use 'replace' to insert '?'

    if ' ' in name:
        name = name.replace(' ','_')

    return name
    
def setName(mol, ID):
    mol.SetProp("_Name", ID)
    return mol

def getProperties(mol):
    propD = mol.GetPropsAsDict()
    return propD

def readSmi(fname, smiI, nameI):
    with open(fname) as f:
        suppl = []
        for line in fname:
            fields = line.rstrip().split(sep)
            smi = fields[smiI]
            name = fields[nameI]
            mol = Chem.MolFromSmiles(smi)
            setName(mol, name)
    return suppl

def writePropertiesSD(fh, propD):
    for prop in propD:
        fh.write('>  <{}>\n{}\n\n'.format(prop, propD[prop])) 

def writeSDF(mol, fh, propD=None, ID=None):
    if ID:
        mol = setName(mol, ID)
    fh.write(Chem.MolToMolBlock(mol))
    if propD == None:
        propD = getProperties(mol)
    writePropertiesSD(fh, propD)
    fh.write('$$$$\n')

def standardize(mol):
    """
    Wrapper to aply the structure normalization protocol provided by Francis Atkinson (EBI). If no non-salt components can be found in the mixture, the original mixture is returned.

    Returns a tuple containing:
        1) True/False: depending on the result of the method
        2) (if True ) The output molecule
           (if False) The error message
    """
    try:
        parent = standardise.run(Chem.MolToMolBlock(mol))
    except standardise.StandardiseException as e:
        if e.name == "no_non_salt":
            parent = Chem.MolToMolBlock(mol)
        else:
            return (False, e.name)

    return (True, parent)

def protonateMol(mol, pH= 7.4, mokaPath= os.environ.get('MOKA_PATH'), clean= True):
    """Adjusts the ionization state of the molecule.

        In this implementation, it uses blabber_sd from Molecular Discovery
        The result is a tuple containing:
           1) True/False: describes the success of the protonation for this compound
           2) (if True ) The name of the protonated molecules and its formal charge
              (if False) The error message
    """
    stderrf = open (os.devnull, 'w')
    stdoutf = open (os.devnull, 'w')

    if mokaPath == None:
        return (False, 'Moka path not found.', None)

    name = getName(mol)
    fnameI = '.'.join([name, 'sdf'])
    if not fnameI.is_file():
        with open(fnameI, 'w') as f:
            writeSDF(mol, f)

    fnameO = '.'.join([name, 'prot', 'sdf'])
    call = [mokaPath+'/blabber_sd', fnameI,
            '-p',  str(pH),
            '-o',  fnameO]

    try:
        retcode = subprocess.call(call,stdout=stdoutf, stderr=stderrf)
    except:
        return (False, 'Blabber execution error', 0.0)

    stdoutf.close()
    stderrf.close()

    if 'blabber110' in mokaPath: # in old blabber versions, error is reported as '0'
        if retcode == 0:
            return (False, 'Blabber 1.0 execution error', 0.0)
    else:
        if retcode != 0:
            return (False, 'Blabber execution error', 0.0)

    try:
        if os.stat(fnameO).st_size==0:
            return (False, 'Blabber output is empty', 0.0)

        finp = open (fnameO)
    except:
        return (False, 'Blabber output not found', 0.0)

    charge = 0
    for line in finp:
        if line.startswith ('M  CHG'):
            items = line.split()
            if int(items[2]):
                for c in range (4,len(items),2): charge+=int(items[c])
            break
    finp.close()

    suppl = SDMolSupplier(fnameO)
    molO = suppl.next()

    if clean:
        removefile (fnameI)
        removefile (fnameO)

    return (True, molO, charge)

def protonateFile(fnameI, pH= 7.4, mokaPath= os.environ.get('MOKA_PATH'), clean= True):
    """Adjusts the ionization state of the molecule.

        In this implementation, it uses blabber_sd from Molecular Discovery
        The result is a tuple containing:
           1) True/False: describes the success of the protonation for this compound
           2) (if True ) The name of the protonated molecules and its formal charge
              (if False) The error message
    """
    stderrf = open (os.devnull, 'w')
    stdoutf = open (os.devnull, 'w')

    pre, ext = os.path.splitext(fnameI)
    fnameO = pre + '.protonated' + ext

    mokaRun = mokaPath+'/blabber_sd'
    if mokaPath == None or  not mokaRun.is_file():
        return (False, 'Moka path not found.')
    call = [mokaRun, fnameI, 
            '-p',  str(pH),
            '-o',  fnameO]

    try:
        retcode = subprocess.call(call,stdout=stdoutf, stderr=stderrf)
    except:
        return (False, 'Blabber execution error')

    stdoutf.close()
    stderrf.close()

    if 'blabber110' in mokaPath: # in old blabber versions, error is reported as '0'
        if retcode == 0:
            return (False, 'Blabber 1.0 execution error')
    else:
        if retcode != 0:
            return (False, 'Blabber execution error')

    try:
        if os.stat(fnameO).st_size==0:
            return (False, 'Blabber output is empty')
    except:
        return (False, 'Blabber output not found')

    return (True, fnameO)

def convert3DMol(mol, corinaPath= os.environ.get('CORINA_PATH'), clean= False):
    """Converts the 2D structure of the molecule "moli" to 3D

        In this implementation, it uses CORINA from Molecular Networks
        The result is a tuple containing:
           1) suucTrue/False: describes the success of the 3D conversion for this compound
           2) (if True ) The name of the 3D molecule
              (if False) The error mesage
    """

    stderrf = open (os.devnull, 'w')
    stdoutf = open (os.devnull, 'w')

    name = getName(mol)
    fnameI = '.'.join([name, 'sdf'])
    if not fnameI.is_file():
        with open(fnameI, 'w') as f:
            writeSDF(mol, f)

    fnameO = '.'.join([name, '3D', 'sdf'])
    call = [corinaPath+'/corina',
            '-dwh','-dori',
            '-ttracefile=corina.trc',
            '-it=sdf', fnameI,
            '-ot=sdf', fnameO]

    try:
        retcode = subprocess.call(call, stdout=stdoutf, stderr=stderrf)
    except:
        return (False, 'Corina execution error')

    stdoutf.close()
    stderrf.close()

    if retcode != 0:
        return (False, 'Corina execution error')

    if not os.path.exists(fnameO):
        return (False, 'Corina output not found')

    suppl = SDMolSupplier(fnameO)
    molO = suppl.next()

    if clean:
        removefile(fnameI)
        removefile(fnameO)
        removefile('corina.trc')

    return (True, molO)

def convert3DFile(fnameI, corinaPath= os.environ.get('CORINA_PATH'), clean= False):
    """Converts the 2D structures in the SD file to 3D

        In this implementation, it uses CORINA from Molecular Networks
        The result is a tuple containing:
           1) True/False: describes the success of the 3D conversion for this compound
           2) (if True ) The name of the output file with the 3D structures
              (if False) The error mesage
    """

    stderrf = open (os.devnull, 'w')
    stdoutf = open (os.devnull, 'w')

    pre, ext = os.path.splitext(fnameI)
    fnameO = pre + '.3D' + ext

    corinaRun = mokaPath+'/corina'
    if corinaPath == None or  not corinaRun.is_file():
        return (False, 'Corina path not found.')
    call = [corinaRun,
            '-dwh','-dori',
            '-ttracefile=corina.trc',
            '-it=sdf', fnameI,
            '-ot=sdf', fnameO]

    try:
        retcode = subprocess.call(call, stdout=stdoutf, stderr=stderrf)
    except:
        return (False, 'Corina execution error')

    stdoutf.close()
    stderrf.close()

    if retcode != 0:
        return (False, 'Corina execution error')

    if not os.path.exists(fnameO):
        return (False, 'Corina output not found')

    if clean:
        removefile('corina.trc')

    return (True, fnameO)