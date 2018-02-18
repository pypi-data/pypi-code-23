# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import print_function
from __future__ import division

"""
**dataArray**

dataArray contain a single dataset.

- ndarray subclass containing matrix like data
- attributes are linked to the data e.g. from a measurement or simulation parameters.
- all numpy array functionality preserved as e.g. slicing, index tricks.
- fit routine 
- read/write in human readable ASCII text including attributes.

dataArray creation can be from read ASCII files or ndarrays as js.dA('filename.dat').
See :py:class:`~.dataArray` for details.

**Example**::

 #create from array or read from
 import jscatter as js
 import numpy as np
 x=np.r_[0:10:0.5]                                        # a list of values
 D,A,q=0.45,0.99,1.2
 data=js.dA(np.vstack([x,np.exp(-q**2*D*x),np.random.rand(len(x))*0.05]))    # creates dataArray
 data.D=D;data.A=A;data.q=q
 data.Y=data.Y*data.A                                     # change Y values
 data[2]*=2                                               # change 3rd column
 data.reason='just as a test'                             # add comment                            
 data.Temperature=273.15+20                               # add attribut
 data.savetxt('justasexample.dat')                        # save data
 data2=js.dA('justasexample.dat')                         # read data into dataArray
 data2.Y=data2.Y/data2.A

The dataarray module can be run standalone in a new project.

**dataList**

dataList contain a list of dataArray for several datasets.

- list subclass as lists of dataArrays (allowing variable sizes).
- basic list routines as read/save, appending, selection, filter, sort, prune, interpolate, spline... 
- multidimensional least square fit that uses the attributes of the dataArray elements.
- read/write in human readable ASCII text of multiple files in one run (gzip possible).

dataList creation can be from read ASCII files or ndarrays as js.dL('filename.dat').

A file may contain several datasets.

See :py:class:`~.dataList` for details.

**Example**::

 p=js.grace()
 dlist2=js.dL()
 x=np.r_[0:10:0.5]
 D,A,q=0.45,0.99,1.2
 for q in np.r_[0.1:2:0.2]:
    dlist2.append(js.dA(np.vstack([x,np.exp(-q**2*D*x),np.random.rand(len(x))*0.05])) )
    dlist2[-1].q=q
 p.clear()
 p.plot(dlist2,legend='Q=$q')
 p.legend()
 dlist2.save('test.dat.gz')


The dataarray module can be run standalone in a new project.

_end_

"""
import time
import sys
import os
import re
import copy
import collections
import string
import io
import gzip
import glob
import numpy as np
import scipy.optimize
import warnings
from functools import reduce


class notSuccesfullFitException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

# Control Sequence Introducer  =  "\x1B[" for print coloured text
#30–37  Set text color  30 + x = Black    Red     Green   Yellow[11]  Blue    Magenta     Cyan    White
#40–47  Set background color    40 + x,
CSIr="\x1B[31m"      # red
CSIrb="\x1B[31;40m"  # red black background
CSIy="\x1B[33m"      # yellow
CSIyb="\x1B[33;40m"  # yellow black background
CSIg="\x1B[32m"      # green
CSIgb="\x1B[32;40m"  # green black background
CSIe="\x1B[0m"  # sets to default

#: returns a log like distribution between mini and maxi with number points
loglist=lambda mini=0,maxi=0,number=10:np.exp(np.r_[np.log((mini if mini!=0. else 1e-6)):np.log((maxi if maxi!=0 else 1.)):(number if number!=0 else 10)*1j])

def _w2f(word):
    """
    converts strings if possible to float
    """
    try:
        return float(word)
    except ValueError:
        return word

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_dataline(wf,ws=None):
    """
    Test if line wf is a data line.  wf is list of strings
    """
    try:
        if ws is None:
            return is_float(wf[0])
        return (is_float(wf[0]) or re.match(ws,wf[0]))
    except:
        return False

# python 2.7 and >3 compatibility
_readmode='r'
if (sys.version_info > (3, 0)):
    def _deletechars(line,deletechar):
        return line.translate({ord(st):None for st in deletechar})
else:
    # older version uses universal newline as 'U', from python 3 it is supported by default in 'r' mode
    _readmode+='U'
    def _deletechars(line, deletechar):
        return line.translate(None,deletechar)

def _readfile(xfile):
    """
    Reads from normal file, gzip file or IOstring or returns list

    """
    if isinstance(xfile, list) and all([isinstance(zz,str) for zz in xfile]):
        # a list of strings
        return xfile
    try:
        # test if xfile is IOString which should contain list of  strings
        zeilen = xfile.getvalue()
        zeilen = zeilen.splitlines(True)
    except AttributeError:
        if os.path.isfile(xfile):
            if xfile.endswith('.gz'):
                _open=gzip.open
            else:  # normal file
                _open=open
            with _open(xfile, _readmode) as f:
                zeilen = f.readlines()
        else :
            raise  Exception( 'Nothing found in :',xfile)
    return zeilen

def _append_temp2raw(raw_data,temp,single_words,xfile,ende):
    """
    internal of _read
    appends new dataset temp to raw_data list and sets temp to empty structure
    including the single words and the original filename xfile
    ende is indicator if temp was last set in a _read file

    temp is dict {'com':[],'_original_comline':[],'para':{},'val':[]}
    raw_data is list of temp

    """
    # this function is only visited if lines change from nondata to data or from data to nodata
    # so we have data and para_com_words or only para_com_words or only data
    if len(temp['val'])==0 and (len(temp['para'])>0 or len(temp['com'])>0 or len(single_words)>0) and ende:
        # parameters found after the data lines at the end of a file
        # append it to last raw_data
        if len(raw_data)==0:
            raise ValueError('There were no data read; it was all about parameters ')
        else:
            for key in temp['para']:        # discriminate multiple  para with same name
                if key in raw_data[-1]['para']:
                    num=1
                    while key+str(num) in raw_data[-1]['para']: num+=1
                    keynum=str(num)
                else: keynum=''
                raw_data[-1]['para'][key+keynum]=temp['para'][key]
            if len(single_words)>0:
                temp['com'].append(' '.join(single_words.split()))
            for line in temp['com']:        # append comments not already in raw_data
                if line not in raw_data[-1]['com']:
                    raw_data[-1]['com'].append(line)
    elif (len(temp['val'])>0 and (len(temp['para'])>0 or len(temp['com'])>0 or len(single_words)>0)):
        # append to raw_data if a parameter and a data section was found
        # ende guarantes that at last line appending to raw_data is forced

        if '@name' not in temp['para']:                 # if not other given the filename is  the name
            temp['para']['@name']=[xfile]
        if len(single_words)>0:                               #add single word to comment
            temp['com'].append(' '.join(single_words.split()))
        #==>>>>> here we add new data from temp to raw_data
        raw_data.append(temp )
        try:                                                 # add the values to raw_data
            #raw_data[-1]['val']=np.squeeze(temp['val'])       # remove dimensions with length 1
            raw_data[-1]['val']=np.atleast_2d(temp['val'])
        except TypeError:                                   # if type error try this; but it will never be called
            raw_data[-1]['val']=[]
            for col in temp['val']:
                raw_data[-1]['val'].append(np.squeeze(col))

    else:
        #return unprocessed data but increase len of single_words to indicate visit here
        # this happens if only data lines separated by empty lines are in the file
        single_words+=' '
        return temp,single_words
    #pass empty temp
    single_words=''
    temp={'com':[],'_original_comline':[],'para':{},'val':[] }
    return temp,single_words

def _read(xfile,block=None,
          usecols=None,
          skiplines=None,
          replace=None,
          ignore='#',
          takeline=None,
          delimiter=None,
          lines2parameter=None):
    """
        **How files are interpreted** :

        | Reads simple formats as tables with rows and columns like numpy.loadtxt.
        | The difference is how to treat additional information like attributes or comments and non float data.

        **Line format rules**:
        A dataset consists of **comments**, **attributes** and **data**.
           (and optional another dataset  behind the first)
        First two words in a line decide what it is:
           - string + value     -> **attribute**     with attributename and list of values
           - string + string    -> **comment**       ignore or convert to attribute by getfromcomment
           - value  + value     -> **data**          line of an array; in sequence without break, input for the ndarray
           - single words       -> are appended to **comment**
           - string+\@unique_name-> **link** to other dataArray with unique_name
        Even complex ASCII file can be read with a few changes as options.

        Datasets are given as blocks of attributes and data.

        **A new dataArray is created if**:

        - a data block with a parameter block (preceded or appended) is found
        - a keyword as first word in line is found:

          - Keyword can be eg. the name of the first parameter.
          - Blocks are  separated as start or end of a number data block (like a matrix).
          - It is checked if parameters are prepended or append to the datablock.
          - If both is used, set block to the first keyword in first line of new block (name of the first parameter).
        - example of an ASCII file with attributes temp, pressure, name::

            this is just a comment or description of the data
            temp     293
            pressure 1013 14
            name     temp1bsa
            0.854979E-01  0.178301E+03  0.383044E+02
            0.882382E-01  0.156139E+03  0.135279E+02
            0.909785E-01  0.150313E+03  0.110681E+02
            0.937188E-01  0.147430E+03  0.954762E+01
            0.964591E-01  0.141615E+03  0.846613E+01
            0.991995E-01  0.141024E+03  0.750891E+01
            0.101940E+00  0.135792E+03  0.685011E+01
            0.104680E+00  0.140996E+03  0.607993E+01

            this is just a second comment
            temp     393
            pressure 1011 12
            name     temp2bsa
            0.236215E+00  0.107017E+03  0.741353E+00
            0.238955E+00  0.104532E+03  0.749095E+00
            0.241696E+00  0.104861E+03  0.730935E+00
            0.244436E+00  0.104052E+03  0.725260E+00
            0.247176E+00  0.103076E+03  0.728606E+00
            0.249916E+00  0.101828E+03  0.694907E+00
            0.252657E+00  0.102275E+03  0.712851E+00
            0.255397E+00  0.102052E+03  0.702520E+00
            0.258137E+00  0.100898E+03  0.690019E+00

        optional:

          - string + @name:
            Link to other data in same file with name given as "name".
            Content of @name is used as identifier. Think of an attribute with 2dim data.

        | to read something like a pdb structure file with lines like
        | ....
        | ATOM    529  CA  MET A  529      21.460  51.750  93.330  1.00  0.00
        | ATOM    530  CA  GLU A  530      18.030  53.510  93.390  1.00  0.00
        | .....
        | use replace={'ATOM':'1'} to read the lines and choose
        | with usecols=[6,7,8] the important columns as x,y,z positions or use
        | ==> js.dA('3rn3.pdb',takeline='ATOM',usecols=[6,7,8]) # ignore anything except with 'ATOM' lines.



    """
    # Returns
    # ------
    # list of dictionaries that will be converted to a dataArray
    # [{
    # 'val'    :data array,
    # 'para'   :{list_of_parameters {'name':value}},
    # 'com':['xxx','ddddddd',.....],
    # 'original_comline':['xxx','ddddddd',.....]
    # }]
    if delimiter=='':
        delimiter=None
    if takeline is not None:
        takeline=re.compile(takeline) # make a regular expression object
    # convenience for skiping lines
    if isinstance(skiplines,(list,tuple,set)):
        skip=lambda words:any(w in words for w in skiplines)
    elif isinstance(skiplines,str):
        skip=lambda words: any(skiplines in word for word in words)
    else:
        skip=skiplines
    # read the lines
    zeilen=_readfile(xfile)

    #################
    raw_data=[]                           #original read data
    temp={'com':[],'_original_comline':[],'para':{},'val':[] }   #temporary dataset
    single_words=''
    if lines2parameter is not None:
        if isinstance(lines2parameter,(int,float)):lines2parameter=[lines2parameter]
        for iline in lines2parameter:
            #prepend a line string in front
            zeilen[iline]='line_%i ' %iline+zeilen[iline]
    if block is not None:
        # block has indices used as slice so convert it to slice
        if isinstance(block,(list,tuple)):
            block=np.r_[block,[None,None,None]][:3]
            block=slice(*[int(b) if isinstance(b,(int, float)) else None for b in block])
            zeilen = zeilen[block]
            block =None
        elif isinstance(block,slice):
            zeilen=zeilen[block]
            block=None
        elif isinstance(block,str):
            # it is as string to indicate block start
            block='\s*'+block       ##only whitespace allowed in front
    # to simulate a new dataset at the end
    zeilen.append('')
    ##############                              now sort it
    lastlinewasnumber=False                     # a "last line was what" indicator
    isheader=False
    is_end=False
    i=0                                   # line number in original file
    iz=0                                  # non empty line number in original file
    for zeile in zeilen:                  # zeilen is german for lines
        i+=1
        if zeile.strip(): iz+=1         # non empty line
        is_end=(i==len(zeilen))
        if iz==1:
            firstwords=zeile.split()
            if firstwords[0]=='@name' and firstwords[1]=='header_of_common_parameters':
                isheader=True
        # line drop or change partialy
        if ignore!='' and zeile.startswith(ignore): #ignore this line
            continue
        if isinstance(replace,dict):
            for key in replace:
                zeile=zeile.replace(key,str(replace[key]))

        worte=zeile.split(delimiter)     # worte is german for words, so split lines in words
        # block assignement
        # test if block marker or change between dataline and nondataline
        # therefore lastlinewasnumber shows status of previous line
        if block is None:
            if isheader and not zeile.strip():
                # if is header we append it and later it is used as common data in dataList identified by @name content
                temp['val'].append([])  # this is needed to accept it as first dataArray
                temp,single_words=_append_temp2raw(raw_data,temp,single_words,xfile,is_end)
                isheader=False
            if ((is_dataline(worte,takeline) and not lastlinewasnumber) or       #change from nondata to    data
                    (not is_dataline(worte,takeline) and lastlinewasnumber)):    #change from    data to nondata
                temp,single_words=_append_temp2raw(raw_data,temp,single_words,xfile,is_end)
                lastlinewasnumber=True
        elif re.match(block,zeile):
            # a block marker block is found
            temp,single_words=_append_temp2raw(raw_data,temp,single_words,xfile,is_end)
            lastlinewasnumber=False

        # line assignement
        if is_dataline(worte,takeline):                   # read dataline
            lastlinewasnumber=True
            if isinstance(usecols,list):
                worte=[worte[ii] for ii in usecols]
            if skip is not None and skip(worte):
                continue
            while len(worte)>len(temp['val']):   ##    wenn neue Spalten benoetigt werden
                temp['val'].append([])           ##    hier anlegen
                try:                             ##    auffuellen bis aktuelle Zeile
                    for row in range(len(temp['val'][-2])):
                        temp['val'][-1].append(None)
                except IndexError:         ##     for first column no predecessor
                    pass
            for col in range(len(worte)):          ##     daten zuordnen
                try:
                    temp['val'][col].append(float(worte[col]))
                except:
                    temp['val'][col].append(worte[col])  # Ersatz bei Fehler(non float)
                    # do not change this!! sometimes data are something like u for up and d for down 
            continue
        else:  # not dataline                                            #  not a dataline
            lastlinewasnumber=False
            if len(worte)==0:                              # empty lines
                continue
            if  len(worte)==1:                             #single name
                single_words+=worte[0]+' '
                continue
            if is_float(worte[1]) or worte[1][0]=='@' or worte[0]=='@name':
                # is parameter (name number) or starts with '@'
                if worte[0] in temp['para']:
                    num=1
                    while worte[0]+str(num) in temp['para']: num+=1
                    keynum=str(num)
                else: keynum=''
                if worte[1][0] == '@' or worte[0] == '@name':  # is link to something or is name of a link
                    temp['para'][worte[0]+keynum] = ' '.join(worte[1:])
                elif len(worte[1:])>1:
                    temp['para'][worte[0]+keynum]=[_w2f(wort) for wort in worte[1:]]
                else:
                    temp['para'][worte[0]+keynum]=_w2f(worte[1])
                continue
            else:                              # comment  1.+2. word not number
                line=' '.join(worte)
                if  line not in temp[ 'com']: temp[ 'com'].append(line)
                if zeile!=line: # store original zeile if different from line
                    if line not in temp['_original_comline']: temp['_original_comline'].append(zeile)
                continue
        print('a line didnt match a rule\n' + i + 'Zeile:  ' + '   ' + zeile)
    #append last set if not empty
    temp,single_words=_append_temp2raw(raw_data,temp,single_words,xfile,True)
    del zeilen
    return raw_data

def _searchForLinks(input):
    """
    internal function
    check for links inside inputz and returns a list without internal links

    """
    for i in range(len(input)):
        try:
            for parameter in input[i]['para']:
                if type(input[i]['para'][parameter])==type('string') and input[i]['para'][parameter][0]== '@':
                    parname= input[i]['para'][parameter][1:]
                    for tolink in range(i+1, len(input)):
                        if input[tolink]['para']['@name']==parname:
                            input[i]['para'][parameter]=dataArray(input.pop(tolink))
                            break
        except: pass
    return input

def _maketxt(dataa, name=None,fmt='%.5e'):
    """
    Converts dataArray to ASCII text
    
    only ndarray content is stored; not dictionaries in parameters

    format rules:
    datasets are separated by a keyword line
    given in blockempty; "empty lines" is the default

    A dataset consists of comments, parameter and data (and optional to another dataset)
    first two words decide for a line
    string + value     -> parameter[also simple list of parameter]
    string + string    -> comment
    value  + value     -> data   (line of an array; in sequence without break)
    single words       -> are appended to comments
    optional:
    1string+@1string   -> as parameter but links to other dataArray
                          (content of parameter with name 1string) stored in the same
                          file after this dataset identified by parameter @name=1string
    internal parameters starting with underscore ('_') are ignored for writing eg _X, Y, ix
                        some others for internal usage too
    content of @name is used as identifier or filename

    passed to savetext with example for ndarray part:
    fmt : str or sequence of strs
        A single format (%10.5f), a sequence of formats, or a
        multi-format string, e.g. 'Iteration %d -- %10.5f', in which
        case `delimiter` is ignored.


    If dictionaries are used add the key to name_key and store content as parameter.

    """
    tail=[]
    partxt=[]
    comment= [dataa.comment]  if isinstance(dataa.comment,str) else dataa.comment
    comtxt=[com for com in comment if com.strip()]
    if name is not None:
        setattr(dataa,'@name',str(name))
    for parameter in dataa.attr:
        if parameter in ['comment','raw_data','internlink','lastfit']+protectedNames:
            continue
        if parameter[0]=='_':  # exclude internals
            continue
        dataapar=getattr(dataa,parameter)
        if isinstance(dataapar,dict):
            #these are not saved
            print( parameter,' not saved; is a dictionary')
            continue
        if isinstance(dataapar,dataArray):
            partxt+=[parameter+' @'+parameter+'\n']
            tail+=_maketxt(dataapar,parameter,fmt)
            continue
        if isinstance(dataapar,str):
            partxt+=[parameter+' '+dataapar+'\n']
            continue
        try:
            ndataapar=np.array(dataapar).squeeze()
        except:
            print( parameter,' not saved; is not a matrix format (np.array() returns error)')
            continue
        if isinstance(ndataapar,np.ndarray):
            if ndataapar.ndim==0:
                partxt+=[parameter+' '+' '.join([str(element) for element in [ndataapar]])+'\n']
            elif ndataapar.ndim==1:
                partxt+=[parameter+' '+' '.join([str(element) for element in ndataapar])+'\n']
            elif ndataapar.ndim==2:
                partxt+=[parameter+' @'+parameter+'\n']
                tail+=_maketxt(dataArray(ndataapar),parameter,fmt)
            else:
                raise IOError('to many dimensions; only ndim<3 supported ')
    output = io.BytesIO()
    #write the array as ndarray
    np.savetxt(output,dataa.array.T,fmt)
    datatxt= output.getvalue()           #this contains '\n' at the end of each line within this single line
    output.close()
    # return list of byte ascii data by using encode to write later only ascii data
    return [c.encode() for c in comtxt]+[p.encode() for p in partxt]+[datatxt]+tail

def shortprint(values,threshold=6,edgeitems=2):
    """
    Creates a short handy representation string for array values.
    
    Parameters
    ----------
    values
    threshold: int default 6
        number of elements to switch to reduced form
    edgeitems : int default 2
        number of elements shown in reduced form
        
    """
    opt = np.get_printoptions()
    np.set_printoptions(threshold=threshold,edgeitems=edgeitems)
    valuestr=np.array_str(values)
    np.set_printoptions(**opt)
    return valuestr

def inheritDocstringFrom(cls):
    """
    Copy docstring from parent.

    """
    def docstringInheritDecorator(fn):
        if isinstance(fn.__doc__,str):
            prepend=fn.__doc__+'\noriginal doc from '+cls.__name__+'\n'
        else:
            prepend=''
        if fn.__name__ in cls.__dict__:
            fn.__doc__=prepend + getattr(cls,fn.__name__).__doc__
        return fn
    return docstringInheritDecorator

#: Defined protected names which are not allowed as attribute names.
protectedNames=['X', 'Y', 'eY', 'eX', 'Z', 'eZ']

#: Indices attributes of protected names
protectedIndicesNames=['_i' + pN.lower() for pN in protectedNames]

class atlist(list):
    """
    A list of attributes extracted from dataList elements with additional methods for easier attribute list handling.

    Mainly to handle arrays with some basic properties respecting that missing values are allowed.

    """
    _isatlist=True
    @property
    def array(self):
        """returns ndarray if possible or list of arrays"""
        return np.asarray(self)

    @property
    def unique(self):
        """returns ndarray if possible or list of arrays"""
        return np.unique(self.array)

    @property
    def flatten(self):
        """returns flattened ndarray"""
        return np.hstack(self)

    @property
    def mean(self):
        """returns mean"""
        return np.mean(self.flatten)
    
    @property
    def std(self):
        """returns standard deviation from mean"""
        return np.std(self.flatten)

    @property
    def sum(self):
        """returns sum"""
        return self.flatten.sum()

    @property
    def min(self):
        """minimum value"""
        return np.min(self.flatten)
    
    @property
    def max(self):
        """maximum value"""
        return np.max(self.flatten)
    
    @property
    def hasNone(self):
        """
        This can be used to test if some dataArray elements do not have the attribute
        """
        return np.any([ele is None for ele in self])
    
# This is the base dataArray class without plotting (only dummies)

class dataListBase(list):

    def __init__(self,objekt=None,
                      block=None,
                      usecols=None,
                      delimiter=None,
                      takeline=None,
                      index=slice(None),
                      replace=None,
                      skiplines=None,
                      ignore='#',
                      XYeYeX=None,
                      lines2parameter=None):
        """
         A list of dataArrays with attributes for analysis, fitting and plotting.

         - Allows reading, appending, selection, filter, sort, prune, least square fitting, ....
         - Saves to human readable ASCII text format (possibly gziped). For file format see dataArray.
         - The dataList allows simulteneous fit of all dataArrays dependent on attributes.
         - and with different parameters for the dataArrays (see fit).
         - dataList creation parameters (below) mainly determine how a file is read from file.

         Parameters
         ----------
         objekt : strings, list of array or dataArray
             | Objects or filename(s) to read.
             | Filenames with extension '.gz' are decompressed (gzip).
             | Accepts filenames with asterisk like exda=dataList(objekt='aa12*') as input for multiple file input.
         usecols : list of integer
             Use only given columns and ignore others.
         skiplines : boolean function, list of string or single string
             Skip line if line meets condition. Function gets the list of words in a line.
             Examples:
              - lambda words: any(w in words for w in ['',' ','NAN',''*****])   #with exact match
              - lambda words: any(float(w)>3.1411 for w in words)
              - lambda words: len(words)==1
             If a list is given, the lambda function is generated automatically as in above example.
             If single string is given, it is tested if string is a substring of a word (  'abc' in '12 3abc4 56')
         block : None,list int, string
             | block separates parts of a file
             | If block is found a new dataArray is created from a part and appended.
             | block can be something like "#next"
             | or the first parameter name of a new block as  block='Temp'
             | block=slice(2,100,3) slices the lines in file as lines[i:j:k]
         index : integer, slice list of integer, default is a slice for all.
             Which datablock to use from single read file if multiple blocks are found.
             Can be integer , list of integer or slice notation.
         XYeYeX : list integers, default=[0,1,2,None,None,None]
             Columns for X, Y, eY, eX, Z, eZ.
             This is ignored for dataList and dataArary objekts as these have defined columns.
             Change later by: data.setColumnIndex(3,5,-1).
         delimiter : string, default any whitespace
             Separator between words (data fields) in a line.
             E.g. '\t' tabulator
         ignore : string, default '#'
            Ignore lines starting with string e.g. '#'.
            For more complex lines to ignore use skiplines.
         replace : dictionary of string:string
             String replacement in read lines as {'old':'new',...}.
             String pairs in this dictionary are replaced in each line.
             This is done prior to determining line type
             and can be used to convert strings to number or ',':'.'.
         takeline : string
             takeline string is first word in a line with data.
             E.g. if dataline start with 'atom' in PDB files takeline='atom' to select specific lines
         lines2parameter : list of integer
             List of lines i which to prepend with 'line_i' to be found as parameter line_i.
             Used to mark lines with parameters without name (only numbers in a line as in .pdh files in the header).
             E.g. to skip the first lines.

         Returns
         -------
             dataList : list of dataArray

         Notes
         -----
         **Attribute access as atlist**
           Attributes of the dataArray elements can be accessed like in dataArrays by .name notation.
           The difference is that a dataList returns atlist -a subclass of **list**- with some additional methods
           as the list of attributes in the dataList elements.
           This is necessary as it is allowed that dataList elements miss an attribute (indicated as None) or
           have different type. An numpy ndarray can be retrieved by the array property (as .name.array).

         **Global attributes**
          We have to discriminate attributes stored individual in each dataArray and in the dataList
          as a kind of global attribute. dataArray attributes belong to a dataArray and are saved
          with the dataArray, while global dataList attributes are only saved with
          the whole dataList at the beginning of a file. If dataArrays are saved as single files global attributes
          are lost.



         Examples
         --------
         ::

          import jscatter as js
          ex=js.dL('aa12*')        #read aa files
          ex.extend('bb12*')      #extend with other bb files
          ex.sort(...)            #sort by attribute "q"
          ex.prune(number=100)    # reduce number of points; default is to calc the mean in an intervall
          ex.filter(lambda a:a.Temperature>273)  to filter for an attribute "Temperature" or .X.mean() value
          # do linear fit
          ex.fit(model=lambda a,b,t:a*t+b,freepar={'a':1,'b':0},mapNames={'t':'X'})
          # fit using parameters in example the Temperature stored as parameter.
          ex.fit(model=lambda Temperature,b,x:Temperature*x+b,freepar={'b':0},mapNames={'x':'X'})

         more Examples
         ::

          import jscatter as js
          import numpy as np
          t=np.r_[1:100:5];D=0.05;amp=1
          # using list comprehension creating a numpy array
          i5=js.dL([np.c_[t,amp*np.exp(-q*q*D*t),np.ones_like(t)*0.05].T for q in np.r_[0.2:2:0.4]])
          # calling a function returning dataArrays
          i5=js.dL([js.dynamic.simpleDiffusion(q,t,amp,D) for q in np.r_[0.2:2:0.4]])
          # define a function and add dataArrays to dataList
          ff=lambda q,D,t,amp:np.c_[t,amp*np.exp(-q*q*D*t),np.ones_like(t)*0.05].T
          i5=js.dL()  # empty list
          for q in np.r_[0.2:2:0.4]:
             i5.append(ff(q,D,t,amp))

         Get elements of dataList with specific attribute values.
         ::

          i5=js.dL([js.dynamic.simpleDiffusion(q,t,amp,D) for q in np.r_[0.2:2:0.4]])
          # get q=0.6
          i5[i5.q.array==0.6]
          # get q > 0.5
          i5[i5.q.array > 0.5]



         """

        self._block=block
        if objekt is None:
            # return empty dataList
            list.__init__(self,[])
        else:
            # read objekt
            temp=self._read_objekt(objekt,
                                    index,
                                    usecols=usecols,
                                    replace=replace,
                                    skiplines=skiplines,
                                    ignore=ignore,
                                    XYeYeX=XYeYeX,
                                    delimiter=delimiter,
                                    takeline=takeline,
                                    lines2parameter=lines2parameter)
            if len(temp)>0:
                list.__init__(self,temp)
            else:
                raise IOError('nothing read, nothing usefull found in objekt '+str(objekt) )

        self._limits={}
        self._isdataList=True

    def __getattribute__(self, attr):
        """
        """
        if attr in protectedNames+['name']:
            return atlist([getattr(element, attr, None) for element in self])
        elif attr in ['lastfit']:
            return list.__getattribute__(self,attr)
        elif np.any([attr in element.attr for element in self]):
            return atlist([getattr(element, attr, None) for element in self])
        else:
            return list.__getattribute__(self,attr)

    def __getdatalistattr__(self,attr):
        """
        get attributes from dataList elements, if they exist
        otherwise get them from datalist attributes itself
        """
        return list.__getattribute__(self,attr)

    def __setattr__(self,attr,val):
        """
        set attribute in datList elements if shape is correct
        otherwise set as attribute of dataList
        """
        #if (hasattr(val,'__iter__') and len(val)==len(self)) and attr[0]!='_':
        #    for ele,va in zip(self,val):
        #        setattr(ele,attr,va)
        if attr not in protectedNames+['lastfit']:
            self.__setlistattr__(attr,val)
        else:
            raise NameError('%s is reserved keyword ' %(attr))

    def __setlistattr__(self,attr,val):
        """internal usage

        this separate method to bypass __setattr__ is used
        to set dataList attributes directly without distributing to list elements
        """
        list.__setattr__(self,attr,val)

    def __delattr__(self, attr):
        """del attribute in elements or in dataList"""
        try:
            for ele in self:
                ele.__delattr__(attr)
        except:
            list.__delattr__(self,attr)

    def _read_objekt(self,objekt=None,
                     index=slice(None),
                     usecols=None,
                     skiplines=None,
                     replace=None,
                     ignore='#',
                     XYeYeX=None,
                     delimiter=None,
                     takeline=None,
                     lines2parameter=None):
        """
        internal function to read data

        reads data from ASCII files or already read stuff in output format of "_read"
        and returns simple dataArray list
        see _read for details of parameters
        """
        #final return list
        datalist=[]
        #list of read input
        inputz=[]
        if isinstance(objekt,dataList):
            return objekt[index]
        elif isinstance(objekt,dataArray):
            datalist.append(objekt)
        elif isinstance(objekt,np.ndarray):
            datalist.append(dataArray(objekt, XYeYeX=XYeYeX))
        elif isinstance(objekt,dict):
            # single element from _read
            if 'val' in objekt:
                datalist.append(dataArray(objekt,XYeYeX=XYeYeX))
        elif isinstance(objekt,(list,tuple)):
            for obj in objekt:
                datalist.extend(self._read_objekt(obj,index=index,usecols=usecols,replace=replace,
                                                skiplines=skiplines,ignore=ignore,XYeYeX=XYeYeX,
                                                delimiter=delimiter,takeline=takeline,lines2parameter=lines2parameter))
        else:
            try:
                filelist=glob.glob(objekt)
            except AttributeError:
                raise AttributeError('No filename pattern in ', objekt)
            else:
                for ff in filelist:
                    # read file
                    inputz=_read(ff,block=self._block,
                                 usecols=usecols,
                                 skiplines=skiplines,
                                 replace=replace,
                                 ignore=ignore,
                                 delimiter=delimiter,
                                 takeline=takeline,
                                 lines2parameter=lines2parameter)
                    # search for internal links of more complex parameters stored as dataArray in same file
                    inputz=_searchForLinks(inputz)
                    # if first entry has special name it is common parameter and contains dataList attributes
                    if inputz[0]['para']['@name']=='header_of_common_parameters':
                        for k,v in inputz[0]['para'].items():
                            setattr(self,k,v)
                        inputz=inputz[1:]
                    if isinstance(inputz,str):
                        print( inputz)
                        inputz=[]
                    else:
                        # select according to index
                        if isinstance(index,int):
                            inputz=[inputz[index]]
                            indexi=slice(None)
                        elif isinstance(index,slice):
                            # is already slice
                            indexi=index
                        elif all([isinstance(a,int) for a in index]):
                            # is a list of integer
                            inputz=[inputz[i] for i in index]
                            indexi=slice(None)
                        else:
                            raise TypeError('use a proper index or slice notation')
                        # add to datalist only the indexed ones
                        for ipz in inputz[indexi]:
                            datalist.append(dataArray(ipz, XYeYeX=XYeYeX))
        if len(datalist)==0:
            raise IOError('nothing read, nothing usefull found in objekt with input "'+str(objekt)+'"' )
        return datalist

    @inheritDocstringFrom(list)
    def __setitem__(self,index,objekt,i=0,usecols=None):
        """puts the objekt into self
        needs to be a dataArray object
        """
        if isinstance(objekt,dataArray):
            list.__setitem__(self,index,objekt)
        else:
            raise TypeError('not a dataArray object')

    @inheritDocstringFrom(list)
    def __getitem__(self,index):
        if isinstance(index,int):
            return list.__getitem__(self,index)
        elif isinstance(index,list):
            out=dataList([self[i] for i in  index])
            return out
        elif isinstance(index,np.ndarray):
            if index.dtype is np.dtype('bool'):
                # this converts bool in integer indices where elements are True
                index=np.r_[:len(index)][index]
            out=dataList([self[i] for i in  index])
            return out
        elif isinstance(index,tuple):
            # this includes the slicing of the underlaying dataArrays whatever is in index1
            index0,index1=index[0],index[1:]
            out=[element[index1] for element in  self[index0]]
            if np.alltrue([hasattr(element,'_isdataArray') for element in out]):
                out=dataList(out)
            return out
        out=dataList(list.__getitem__(self,index))
        return out

    @inheritDocstringFrom(list)
    def __delitem__(self,index):
        list.__delitem__(self,index)

    @inheritDocstringFrom(list)
    def __setslice__(self,i,j,objekt):
        self[max(0, i):max(0, j):] = objekt

    @inheritDocstringFrom(list)
    def __delslice__(self,i,j):
        del self[max(0, i):max(0, j):]

    @inheritDocstringFrom(list)
    def __getslice__(self,i,j):
        return self[max(0, i):max(0, j):]

    @inheritDocstringFrom(list)
    def __add__(self,other):
        if hasattr(other,'_isdataList'):
            out=dataList(list.__add__(self,other))
        elif hasattr(other,'_isdataArray'):
            out=dataList(list.__add__(self,[other]))
        else:
            out=dataList(list.__add__(self,[dataArray(other)]))
        return out

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls([copy.deepcopy(da, memo) for da in self])
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            # copy only attributes in dataList as fit parameters
            if k[0]!='_': # but nothing private
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    def copy(self):
        """
        Deepcopy of dataList

        To make a normal shallow copy use copy.copy

        """
        return copy.deepcopy(self)

    def nakedcopy(self):
        """
        Returns copy without attributes, thus only the data.

        """
        cls = self.__class__
        return cls([ele.nakedcopy() for ele in self])

    @property
    def whoHasAttributes(self):
        """
        Lists which attribute is found in which element.

        Returns
        -------
        dictionary of attributes names: list of indices
            keys are the attribute names
            values are indices of dataList where attr is existent

        """
        attrInElements=set()
        for ele in self:attrInElements.update(ele.attr)
        whohasAttribute={}
        for attr in attrInElements:
            whohasAttribute[attr]= [i for i,j in enumerate(getattr(self,attr)) if j is not None]
        return whohasAttribute

    @property
    def shape(self):
        """
        Tuple with shapes of dataList elements.
        """
        return tuple([a.shape for a in self])

    @property
    def attr(self):
        """
        Returns all attribute names (including commonAttr of elements) of the dataList.
        """
        attr=filter(lambda key:key[0]!='_' and key not in ('@name','raw_data'),
                        list(self.__dict__.keys())+self.commonAttr)
        return sorted(attr)

    def showattr(self,maxlength=75,exclude=['comment','lastfit']):
        """
        Show data specific attributes for all elements.

        Parameters
        ----------
        maxlength : integer
            truncate string representation
        exclude : list of str
            list of attribute names to exclude from show

        """
        for element in self:
            print( '------------------------------------------------')
            element.showattr(maxlength=maxlength,exclude=exclude)
        print(  '==================================================')
        commonAttr=self.commonAttr
        for attr in self.attr:
            if attr not in commonAttr+exclude:
                values=getattr(self,attr)
                try:
                    valstr=shortprint(values).split('\n')
                    print(  '{:>24} = {:}'.format(attr, valstr[0]))
                    for vstr in valstr[1:]:
                        print(  '{:>25}  {:}'.format('', vstr))
                except:
                    print(  '%24s = %s' %(attr,str(values)[:maxlength]))
        print(  '------------------------------------------------')

    def copyattr2elements(self,maxndim=1,exclude=['comment']):
        """
        Copy dataList specific attributes to all elements.

        Parameters
        ----------
        exclude : list of str
            list of attr names to exclude from show
        maxndim : int, default 2
            maximum dimension e.g. to prevent copy of 2d arrays like covariance matrix

        Notes
        -----
        Main use is for copying fit parameters

        """
        commonAttr=self.commonAttr
        for attr in self.attr:
            if attr not in commonAttr+exclude+protectedNames+['lastfit', 'raw_data']:
                val=getattr(self,attr)
                if (hasattr(val,'__iter__') and len(val)==len(self)) and attr[0]!='_':
                    for ele,va in zip(self,val):
                        if np.array(va).ndim<=maxndim:
                            setattr(ele,attr,va)
                else:
                    for ele in self:
                        if np.array(val).ndim<=maxndim:
                            setattr(ele,attr,val)

    def getfromcomment(self,attrname):
        """
        Extract a non number parameter from comment with attrname in front

        If multiple names start with parname first one is used.
        Used comment line is deleted from comments

        Parameters
        ----------
        attrname : string
            name of the parameter in first place

        """
        for element in self:
            element.getfromcomment(attrname=attrname)

    @property
    def commonAttr(self):
        """
        Returns list of attribute names existing in elements.

        """
        common=[]
        try:
            for attr in self[0].attr:
                if np.alltrue([attr in element.attr for element in self]):
                    common.append(attr)
        except:
            return []
        return common

    @property
    def names(self):
        """
        List of element names.

        """
        return [element.name for element in self]

    @inheritDocstringFrom(list)
    def append(self,objekt=None,
                    index=slice(None),
                    usecols=None,
                    skiplines=None,
                    replace=None,
                    ignore='#',
                    XYeYeX=None,
                    delimiter=None,
                    takeline=None,
                    lines2parameter=None):
        """
        Reads/creates new dataArrays and appends to dataList.

        See dataList for description of all keywords.
        If objekt is dataArray or dataList all options except XYeYeX,index are ignored.

        Parameters
        ----------
        objekt,index,usecols,skiplines,replace,ignore,delimiter,takeline,lines2parameter : options
            See dataArray or dataList

        """
        obj=self._read_objekt(objekt,index=index,usecols=usecols,skiplines=skiplines,replace=replace,ignore=ignore,
                              XYeYeX=XYeYeX,delimiter=delimiter,takeline=takeline,lines2parameter=lines2parameter)
        list.extend(self,obj)

    # extend is same as append
    extend=append

    @inheritDocstringFrom(list)
    def insert(self,i,objekt=None,
                        index=0,
                        usecols=None,
                        skiplines=None,
                        replace=None,
                        ignore='#',
                        XYeYeX=None,
                        delimiter=None,
                        takeline=None,
                        lines2parameter=None):
        """
        Reads/creates new dataArrays and inserts in dataList.

        If objekt is dataArray or dataList all options except XYeYeX,index are ignored.

        Parameters
        ----------
        i : int, default 0
            Position where to insert.
        objekt,index,usecols,skiplines,replace,ignore,delimiter,takeline,lines2parameter : options
            See dataArray or dataList

         """
        obj=self._read_objekt(objekt,usecols=usecols,skiplines=skiplines,replace=replace,ignore=ignore,
                              XYeYeX=XYeYeX,delimiter=delimiter,takeline=takeline,lines2parameter=lines2parameter)
        list.insert(self,i,obj[index])

    @inheritDocstringFrom(list)
    def pop(self,i=-1):
        """ """
        out=list.pop(self,i)
        return out

    @inheritDocstringFrom(list)
    def delete(self,index):
        """
        Delete element at index

        """
        self.__delitem__(self,index)

    @inheritDocstringFrom(list)
    def index(self,value,start=0,stop=-1):
        """ """
        for i in range(len(self[start:stop])):
            if self[i] is value:
                return i
        raise ValueError('not in list')

    @property
    def aslist(self):
        """
        Return as simple list.
        """
        return [ele for ele in self]

    @inheritDocstringFrom(list)
    def reverse(self):
        """Reverse dataList -> INPLACE!!!"""
        list.reverse(self)

    def sort(self,key=None,reverse=False):
        """
        Sort dataList -> INPLACE!!!

        Parameters
        ----------
        key : function
            A function that is applied to all elements and the output is used for sorting.
            e.g.  'Temp' or lambda a:a.Temp
            convenience: If key is attribut name this attribute is used
        reverse : True, False
            Normal or reverse order.

        Examples
        --------
        ::

         dlist.sort('q',True)
         dlist.sort(key=lambda ee:ee.X.mean() )
         dlist.sort(key=lambda ee:ee.temperatur )
         dlist.sort(key=lambda ee:ee.Y.mean() )
         dlist.sort(key=lambda ee:ee[:,0].sum() )
         dlist.sort(key=lambda ee:getattr(ee,parname))
         dlist.sort(key='parname')


        """
        if isinstance(key,str):
            self.sort(key=lambda ee:getattr(ee,key),reverse=reverse)
            return
        try:
            list.sort(self,key=key,reverse=reverse)
        except ValueError:
            print(  'You have to define how to compare dataList elements for sorting; see help\n')

    @inheritDocstringFrom(list)
    def __repr__(self):
        if len(self)>0:
            attr=self.commonAttr[:7]
            shape=np.shape(self)
            if all([sh==shape[0] for sh in shape[1:]]):
                shape='all ==> '+str(shape[0])
            elif len(shape)>20:
                shape=shape[:5]+(('...','...'))+shape[-5:]
            desc="""dataList->
X = %(XX)s,
Y=  %(YY)s,
first attributes=%(attr)s...,
shape=[%(ll)s] %(length)s     """
            return desc % {'XX': shortprint(self.X.array),
                       'YY':  shortprint(self.Y.array),
                       'attr':attr,
                       'll':len(self),
                       'length':shape}
        else:
            return []

    @property
    def dtype(self):
        """return dtype of elements"""
        return [element.dtype for element in self]

    def filter(self,filterfunction):
        """
        Filter elements according to filterfunction.

        Parameters
        ----------
        filterfunction : function or lambda function returning boolean
            Return those items of sequence for which function(item) is true.

        Examples
        --------
        ::

         i5=js.dL('exampleData/iqt_1hho.dat')
         i1=i5.filter(lambda a:a.q>0.1)
         i1=i5.filter(lambda a:(a.q>0.1) )
         i5.filter(lambda a:(a.q>0.1) & (a.average[0]>1)).average
         i5.filter(lambda a:(max(a.q*a.X)>0.1) & (a.average[0]>1))

        """
        return dataList(filter(filterfunction,self))

    def setColumnIndex(self,*arg,**kwargs):
        """
        Set the columnIndex where to find X,Y,Z, eY, eX, eZ.....

        Default is ix=0,iy=1,iey=2,iz=None,iex=None,iez=None as it is the most used.
        There is no limitation and each dataArray can have different ones.

        Parameters
        ----------
        ix,iy,iey,iz,iex,iez: integer, None; default ix=0,iy=1,iey=2,iz=None,iex=None,iez=None
            | usability wins iey=2!!
            | if columnIndex differs in dataArrays set them individually

        Notes
        -----
        | A list of all X in the dataArray is dataArray.X
        | integer  column index as 0,1,2,-1 , should be in range
        | None     as not used eg iex=None -> no errors for x
        | anything else does not change

        Shortcut sCI

        """
        for element in self:
            element.setColumnIndex(*arg,**kwargs)

    sCI=setColumnIndex

    def savetxt(self, name=None,exclude=['comment','lastfit'],fmt='%.5e'):
        """
        Saves dataList as ASCII text file, optional compressed (gzip).

        Saves dataList with attributes to one file that can be reread.
        Dynamic created attributes as e.g. X, Y, eY, are not saved.
        If name extension is '.gz' the file is compressed (gzip).

        Parameters
        ----------
        name : string
            filename
        exclude : list of str, default ['comment','lastfit']
            List of dataList attribut names to exclude from being saved.
        fmt : string, default '%.5e'
            Format specifier for writing float as e.g. '%.5e' is exponential with 5 digits precision.

        Notes
        -----
        Saves a sequence of the dataArray elements.

        Format rules:

         Dataset consists of tabulated data with optional attributes and comments.
         Datasets are separated by empty lines, attributes and comments come before data.

         First two strings decide for a line:
          - string + value     -> attribute as attribute name + list of values
          - string + string    -> comment line
          - value  + value     -> data   (line of an array; in sequence without break)
          - single words       -> are appended to comments

         optional:
          - string + @name   ->  as attribute but links to other dataArray with .name="name" stored in the same file after this dataset.
          - internal parameters starting with underscore ('_') are ignored for writing, also X,Y,Z,eX,eY,eZ,
          - only ndarray content is stored; no dictionaries in parameters.
          - @name is used as identifier or filename can be accessed as name.
          - attributes of dataList are saved as common attributes marked with a line "@name header_of_common_parameters"

        """
        if name is None:
            raise IOError('filename for dataset missing! first original name in list is ',getattr(self[0],'@name'))
        if os.path.splitext(name)[-1] == '.gz':
            _open = gzip.open
        else:  # normal file
            _open = open
        with _open(name,'wb') as f:
            #prepare dataList attr
            if len([attr for attr in self.attr if attr not in self.commonAttr+exclude])>0:
                temp=dataArray()
                commonAttr=self.commonAttr
                for attr in [attr for attr in self.attr if attr not in self.commonAttr+exclude]:
                    setattr(temp,attr,getattr(self,attr))
                f.writelines( _maketxt(temp, name='header_of_common_parameters',fmt=fmt))
            for element in self:
                f.writelines( _maketxt(element, name=name,fmt=fmt))
        return

    savetext=savetxt
    save=savetxt

    def merge(self,indices,isort=None):
        """
        Merges elements of dataList.

        The merged dataArray is stored in the lowest indices. Others are removed.

        Parameters
        ----------
        indices : integer,'all'
            list of indices to merge
            'all' merges all elements into one.
        isort : integer
            argsort after merge along column eg isort='X', 'Y', or 0,1,2
            None is no sorting as default

        Notes
        -----
        Attributes are copied as lists in the merged dataArray.

        """
        if indices is 'all':
            indices=range(len(self))
        index=list(indices)
        index.sort(reverse=True)
        first=index.pop()
        self[first]=self[first].merge([self[i] for i in index],isort=isort)
        for this in index:
            self.__delitem__(this)

    def mergeAttribut(self, parName, limit=None, isort=None, func=np.mean):
        """
        Merges elements of dataList if attribute values are closer than limit (in place).

        If attribute is list the average is taken for comparison.
        For special needs create new parameter and merge along this.

        Parameters
        ----------
        parName : string
            name of a parameter
        limit : float
            The relative limit value.
            If limit is None limit is determined as standardeviation of sorted differences
            as limit=np.std(np.array(data.q[:-1])-np.array(data.q[1:]))/np.mean(np.array(self.q)
        isort : 'X', 'Y' or 0,1,2..., None, default None
            Column for isort.
            None is no sorting
        func : function or lambda, default np.mean
            a function to create a new value for parameter
            see extractAttribut
            stored as .parName+str(func.func_name)

        Examples
        --------
        ::

         i5=js.dL('exampleData/iqt_1hho.dat')
         i5.mergeAttribut('q',0.1)
         # use qmean instead of q or calc the new value
         print(  i5.qmean)


        """
        self.sort(key=parName)
        if limit is None:
            try:
                # relative standard deviation of the parameter differences as limit
                parval=getattr(self,parName)
                limit=np.std(np.diff(parval))/parval.mean
            except:
                raise TypeError('cannot determine limit; please specify')
        #define  a criterion for merging dataset
        def allwithinlimit(ml,limit):
            return abs(np.std(ml))<limit*np.mean(ml)
        mergelist=[0] #a first value to start
        while mergelist[-1]<(len(self)-1):
            # append if still within limits
            if allwithinlimit([getattr(self[ml],parName) for ml in mergelist+[mergelist[-1]+1]],limit):
                mergelist+=[mergelist[-1]+1]
            elif len(mergelist)==1:
                # only one element; no merge but parname should be a list as the others
                setattr(self[mergelist[-1]],parName,[getattr(self[mergelist[-1]],parName)])
                #next element for test in list
                mergelist=[mergelist[0]+1]
            else:
                #mergelist >1 so  merge and start next element
                self.merge(mergelist,isort=isort)
                mergelist=[mergelist[0]+1]
        # care about last element if it was a single one
        if len(mergelist)>1:
            self.merge(mergelist,isort=isort)
        else:
            setattr(self[mergelist[-1]],parName,[getattr(self[mergelist[-1]],parName)])
        #extract with func from the merged
        if func is not None:
            try:
                self.extractAttribut(parName,func=func,newParName=parName+str(func.func_name))
            except:
                self.extractAttribut(parName, func=func, newParName=parName + str(func.__name__))

    def extractAttribut(self, parName, func=None, newParName=None):
        """
        Extract a simpler attribute from a complex attribute in each element of dataList.

        eg. extract the mean value from a list in an attribute

        Parameters
        ----------
        parName : string
            name of the parameter to process
        func : function or lambda
            a function (eg lambda ) that creates a new content for the
            parameter from the original content
            eg lambda a:np.mean(a)*5.123
            the function gets the content of parameter whatever it is
        newParName :string
            if None old parameter is overwritten,
            otherwise this is the new parname

        """
        if newParName is None:
            for element in self:
                setattr(element,parName,func(getattr(element,parName)))
        else:
            for element in self:
                setattr(element,newParName,func(getattr(element,parName)))

    def bispline(self, func=None, invfunc=None, tx=None,ta=None,deg=[3,3],eps=None,addErr=False, **kwargs):
        """
        Weighted least-squares bivariate spline approximation for interpolation of Y at given attribute values for X values.

        Uses scipy.interpolate.LSQBivariateSpline
        eY values are used as weights (1/eY**2) if present.

        Parameters
        ----------
        kwargs :
            Keyword arguments
            The first keyword argument found as attribute is used for interpolation.
            E.g. conc=0.12 defines the attribute 'conc' to be interpolated to 0.12
            Special kwargs see below.
        X : array
            List of X values were to evaluate.
            If X not given the .X of first element are used as default.
        func : numpy ufunction or lambda
            Simple function to be used on Y values before interpolation.
            see dataArray.polyfit
        invfunc : numpy ufunction or lambda
            To invert func after extrapolation again.
        tx,ta : array like, None, int
            Strictly ordered 1-D sequences of knots coordinates for X and attribute.
            If None the X or attribute values are used.
            If integer<len(X or attribute) the respective number of equidistante points in the interval between min and max are used.
        deg : [int,int], optional
            Degrees of the bivariate spline for X and attribute. Default is 3.
            If single integer given this is used for both.
        eps : float, optional
            A threshold for determining the effective rank of an over-determined
            linear system of equations. `eps` should have a value between 0 and 1,
            the default is 1e-16.
        addErr : bool
            If errors are present spline the error colum and add it to the result.

        Returns
        -------
            dataArray

        Notes
        -----
         - The spline interpolation results in a good approximation if the data are narrow.
           Around peaks values are underestimated if the data are not dense enough as the
           flank values are included in the spline between the maxima. See Examples.
         - Without peaks there should be no artefacts.
         - To estimate new errors for the splined data use .setColimnIndex(iy=ii,iey=None) with ii as index of errors.
           Then spline the errors and add these as new column.
         - Interpolation can not be as good as fitting with a prior known
           model and use this for extrapolating.

        Examples
        --------
        ::

         import jscatter as js
         import numpy as np
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         fig = plt.figure()
         ax1 = fig.add_subplot(211, projection='3d')
         ax2 = fig.add_subplot(212, projection='3d')
         i5=js.dL([js.formel.gauss(np.r_[-50:50:5],mean,10) for mean in np.r_[-15:15.1:3]])
         i5b=i5.bispline(mean=np.r_[-15:15:1],X=np.r_[-25:25:1],tx=10,ta=5)
         fig.suptitle('Spline comparison with different spacing of data')
         ax1.set_title("Narrow spacing result in good interpolation")
         ax1.scatter3D(i5.X.flatten, np.repeat(i5.mean,[x.shape[0] for x in i5.X]), i5.Y.flatten,s=20,c='red')
         ax1.scatter3D(i5b.X.flatten,np.repeat(i5b.mean,[x.shape[0] for x in i5b.X]), i5b.Y.flatten,s=2)
         ax1.tricontour(i5b.X.flatten,np.repeat(i5b.mean,[x.shape[0] for x in i5b.X]), i5b.Y.flatten,s=2)
         i5=js.dL([js.formel.gauss(np.r_[-50:50:5],mean,10) for mean in np.r_[-15:15.1:15]])
         i5b=i5.bispline(mean=np.r_[-15:15:1],X=np.r_[-25:25:1])
         ax2.set_title("Wide spacing result in artefacts between peaks")
         ax2.scatter3D(i5.X.flatten, np.repeat(i5.mean,[x.shape[0] for x in i5.X]), i5.Y.flatten,s=20,c='red')
         ax2.scatter3D(i5b.X.flatten,np.repeat(i5b.mean,[x.shape[0] for x in i5b.X]), i5b.Y.flatten,s=2)
         ax2.tricontour(i5b.X.flatten,np.repeat(i5b.mean,[x.shape[0] for x in i5b.X]), i5b.Y.flatten,s=2)
         plt.show(block=False)

        """
        if 'X' in kwargs:
            X=np.atleast_1d(kwargs['X'])
        else:
            X=self[0].X
        if isinstance(deg,int):
            deg=[deg,deg]
        par=None
        for kw,val in kwargs.items():
            if kw is 'X':
                continue
            if kw in self.attr:
                par=kw
                newparval=np.atleast_1d(val)
                newparval.sort()
                break
        uniqueX=self.X.unique
        if isinstance(tx, int) and tx <uniqueX.shape[0]:
            tx=np.r_[uniqueX.min():uniqueX.max():tx*1j]
        if tx is None:
            tx=uniqueX
        uniquepar=getattr(self,par).unique
        if isinstance(ta, int) and ta <uniquepar.shape[0]:
            ta=np.r_[uniquepar.min():uniquepar.max():ta*1j]
        if ta is None:
            ta=uniquepar
        # create par coordinate P with shape of .X
        P=np.repeat(getattr(self,par),[x.shape[0] for x in self.X])
        if np.all(self.eY):
            w=1/self.eY.flatten**2  # error weight
        else:
            w=None
        Y=self.Y.flatten
        if func is not None:
            Y=func(Y)
        f = scipy.interpolate.LSQBivariateSpline(x=self.X.flatten,y=P,z=Y,tx=tx,ty=ta,
                                                 w=w,kx=deg[0],ky=deg[1],eps=eps)
        # get new values
        fY=f(X,newparval)
        if invfunc is not None:
            fY=invfunc(fY)
        if addErr and w is not None:
            ferr = scipy.interpolate.LSQBivariateSpline(x=self.X.flatten, y=P, z=self.eY.flatten, tx=tx, ty=ta,
                                                        kx=deg[0], ky=deg[1], eps=eps)
            eY=ferr(X,newparval)
        else:
            eY =np.zeros_like(fY)
        # prepare output dataList
        result=dataList()
        for p,fy,e in zip(newparval,fY.T,eY.T):
            if addErr and w is not None:
                result.append(np.c_[X,fy,e].T)
            else:
                result.append(np.c_[X, fy].T)
            setattr(result[-1],par,p)
        return result


    def interpolate(self, func=None, invfunc=None,deg=1, **kwargs):
        """
        Interpolates Y at given attribute values for X values.

        Uses twice a linear interpolation (first along X then along attribute).
        If X and attributes are equal to existing these datapoints are returned.

        Parameters
        ----------
        **kwargs :
            Keyword arguments as float or array-like
            the first keyword argument found as attribute is used for interpolation.
            E.g. conc=0.12 defines the attribute 'conc' to be interpolated to 0.12
            Special kwargs see below.
        X : array
            List of X values were to evaluate (linear interpolation).
            If X  < or > self.X the corresbonding min/max border is used.
            If X not given the .X of first element are used as default.
        func : function or lambda
            Function to be used on Y values before interpolation.
            See dataArray.polyfit.
        invfunc : function or lambda
            To invert func after extrapolation again.
        deg : integer, default =1
            Polynom degree for interpolation along attribute.
            Outliers result in Nan.

        Returns
        -------
            dataArray

        Notes
        -----
         - This interpolation results in a good approximation if the data are narrow.
           Around peaks values are underestimated if the data are not dense enough. See Examples.
         - To estimate new errors for the splined data use .setColumnIndex(iy=ii,iey=None) with ii as index of errors.
           Then spline the errors and add these as new column.
         - Interpolation can not be as good as fitting with a prior known
           model and use this for extrapolating.

        Examples
        --------
        ::

         import jscatter as js
         import numpy as np
         import matplotlib.pyplot as plt
         from mpl_toolkits.mplot3d import Axes3D
         fig = plt.figure()
         ax1 = fig.add_subplot(211, projection='3d')
         ax2 = fig.add_subplot(212, projection='3d')
         # try different kinds of polynaminal degree
         deg=2
         i5=js.dL([js.formel.gauss(np.r_[-50:50:5],mean,10) for mean in np.r_[-15:15.1:3]])
         i5b=i5.interpolate(mean=np.r_[-15:15:1],X=np.r_[-25:25:1],deg=deg)
         fig.suptitle('Interpolation comparison with different spacing of data')
         ax1.set_title("Narrow spacing result in good interpolation")
         ax1.scatter3D(i5.X.flatten, np.repeat(i5.mean,[x.shape[0] for x in i5.X]), i5.Y.flatten,s=20,c='red')
         ax1.scatter3D(i5b.X.flatten,np.repeat(i5b.mean,[x.shape[0] for x in i5b.X]), i5b.Y.flatten,s=2)
         ax1.tricontour(i5b.X.flatten,np.repeat(i5b.mean,[x.shape[0] for x in i5b.X]), i5b.Y.flatten,s=2)
         i5=js.dL([js.formel.gauss(np.r_[-50:50:5],mean,10) for mean in np.r_[-15:15.1:15]])
         i5b=i5.interpolate(mean=np.r_[-15:15:1],X=np.r_[-25:25:1],deg=deg)
         ax2.set_title("Wide spacing result in artefacts between peaks")
         ax2.scatter3D(i5.X.flatten, np.repeat(i5.mean,[x.shape[0] for x in i5.X]), i5.Y.flatten,s=20,c='red')
         ax2.scatter3D(i5b.X.flatten,np.repeat(i5b.mean,[x.shape[0] for x in i5b.X]), i5b.Y.flatten,s=2)
         ax2.tricontour(i5b.X.flatten,np.repeat(i5b.mean,[x.shape[0] for x in i5b.X]), i5b.Y.flatten,s=2)
         plt.show(block=False)

        """
        interp1d=scipy.interpolate.interp1d

        if 'X' in kwargs:
            X=np.atleast_1d(kwargs['X'])
            del kwargs['X']
        else:
            X=self[0].X
        for kw,val in kwargs.items():
            if kw in self.attr:
                par=kw
                newparval=np.atleast_1d(val)
                break
            raise ValueError('No parameter as given found in data. Check with .attr')
        # first interpolate to new X values
        if func is not None:
            YY = np.array([interp1d(ele.X, func(ele.Y), kind=deg)(X) for ele in self])
        else:
            YY = np.array([interp1d(ele.X,      ele.Y , kind=deg)(X) for ele in self])
        # attribute array
        parval=getattr(self,par).flatten
        # calc the poly coefficients for all YY and call it with newparval
        # outliers are handled above scipy 0.17.1 ; this will change later
        newY=interp1d(parval,YY.T,kind=deg)(newparval)
        if invfunc is not None:
            newY=invfunc(newY)
        result=dataList()
        for p,fy in zip(newparval,newY.T):
            result.append(np.c_[X, fy].T)
            setattr(result[-1],par,p)
        return result

    def polyfit(self,func=None,invfunc=None,xfunc=None,invxfunc=None,exfunc=None,**kwargs):
        """
        Inter/Extrapolated values along attribut for all given X values using a polyfit.

        To extrapolate along an attribute using twice a polyfit (first along X then along attribute).
        E.g. from a concentration series to extrapolate to concentration zero.

        Parameters
        ----------
        **kwargs :
            Keyword arguments
            The first keyword argument found as attribute is used for extrapolation
            e.g. q=0.01  attribute with values where to extrapolate to
            Special kwargs see below.
        X : arraylike
            list of X values were to evaluate
        funct : function or lambda
            Function to be used in Y values before extrapolating.
            See Notes.
        invfunc : function or lambda
            To invert function after extrapolation again.
        xfunct : function or lambda
            Function to be used for X values before interpolating along X.
        invxfunc : function or lambda
            To invert xfunction again.
        exfunc : function or lambda
            Weigth for extrapol along X
        degx,degy : integer default degx=0, degy=1
            polynom degree for extrapolation in x,y
            If degx=0 (default) no extrapolation for X is done and values are linear interpolated.

        Returns
        -------
            dataArray

        Notes
        -----
        funct is used to transfer the data to a simpler smoother or polynominal form.
         - Think about data describing diffusion like I~exp(-q**2*D*t) and we want to interpolate along attribute q.
           If funct is np.log we interpolate on a simpler parabolic q**2 and linear in t.
         - Same can be done with X axis thin in above case about subdiffusion t**a with a < 1.

        Examples
        --------
        Task: Extrapolate to zero q for 3 X values for an exp decaying function.
        Here first log(Y) is used (problem linearized), then linear extrapolate and and exp function used for the result.
        This is like lin extapolation of the exponent::

         i5.polyfit(q=0,X=[0,1,11],func=lambda y:np.log(y),invfunc=lambda y:np.exp(y),deg=1)

        concentration data with conc and extrapoleate to conc=0 ::

         data.polyfit(conc=0,X=data[0].X,deg=1)

        """
        if 'X' in kwargs:
            X=np.atleast_1d(kwargs['X'])
            del kwargs['X']
        else:
            X=self[0].X
        for kw in kwargs:
            if kw in self.attr:
                par=kw
                parval=np.atleast_1d(kwargs[kw])
                break
        else:
            raise ValueError('No parameter found in data check with .attr')
        degx=0
        degy=1
        if 'degx' in kwargs:
            degx=kwargs['degx']
        if 'degy' in kwargs:
            degy=kwargs['degy']
        if xfunc is None:
            xfunc=lambda y:y
            exfunc=None
        if exfunc is None:
            exfunc=lambda y:y
        if invxfunc is None:
            invxfunc=lambda y:y
        if func is None:
            func=lambda y:y
        if invfunc is None:
            invfunc=lambda y:y
        if degx>0:
            # interpolate to needed X values
            YY=np.array([ele.polyfit(X,deg=degx,function=xfunc,efunction=exfunc).Y for ele in self])
        else:
            YY=[np.interp(X,ele.X,ele.Y) for ele in self]
        #calc the poly coefficients for all YY
        poly=np.polyfit(np.array(getattr(self,par)).flatten(),func(invxfunc(YY)),deg=degy).T
        # and calc the values at parval
        pnn =np.array([np.poly1d(polyi)(parval) for polyi in poly]).T
        return dataList([np.c_[X,invfunc(fy)].T for fy in pnn])

    #: alternative name for polyfit
    extrapolate=polyfit

    def prune(self,*args,**kwargs):
        """
        Reduce number of values between upper and lower limits.

        Prune reduces a dataset to reduced number of data points in an interval
        between lower and upper by selection or by averaging including errors.

        Parameters
        ----------
        *args,**kwargs :
            arguments and keyword arguments see below
        lower : float
            lower bound min is min of data
        upper : float
            upper bound max is max of data
        number : int
            number of values in result
        kind : {'log','lin'} default 'lin'
            | type of the new point distrubution
            | 'log' closest values in log distribution with number points in [lower,upper]
            | 'lin' closest values in lin distribution with number points in [lower,upper]
            | if number==None all points between min,max are used
        type : {None,'mean','error','mean+error'} default 'mean'
            | how to determine the value for a point
            | None   original Y value of X closest to new X value
            | 'mean' mean values in interval between 2 X points;
            |        weight==None -> equal weight
            |        if weight!=None with weight=1/col[weight]**2
            |        weight column will get values according to error propagation
            | 'mean+std' calcs mean and adds error columns with standard deviation from intervals
            |        can be used if no errors are present
            |        for single values the error is interpolated from neighbouring values
            |        ! for less pruned data error may be bad defined if only a few points are averaged
        col : 'X','Y'....., or int, default 'X'
            column to prune along X,Y,Z or index of column
        weight : None, 'eX', 'eY' or int
            | column for weight as 1/err**2 in 'mean' calculation, None is equal weight
            | weight columne gets new error sqrt(1/sum_i(1/err_i**2))
            | if None or not existing equal weights are used
        keep : list of int
            list of indices to keep in any case

        Returns
        -------
        dataArray with values pruned to number of values

        Examples
        --------
        ::

         i5.prune(number=13,col='X',type='mean',weight='eY')
         i5.prune(number=13)


        Notes
        -----
        | Attention !!!!
        | dependent on the distribution of original data a lower number of points can be the result
        | eg think of noisy data between 4 and 5 and a lin distribution from 1 to 10 of 9 points
        | as there are no data between 5 and 10 these will all result in 5 and be set to 5 to be unique

        """
        out=dataList()
        for element in self:
            out.append(element.prune(*args,**kwargs))
        return out

    def modelValues(self,**kwargs):
        """
        Calculates modelValues of model after a fit.

        Model parameters are used from dataArray attributes or last fit parameters.
        Given arguments  overwrite parameters and attributes to simulate modelValues
        e.g. to extend X range.

        Parameters
        ----------
        **kwargs : parname=value
            Overwrite parname with value in the dataList attributes or fit results
            e.g. to extend the parameter range or simulate changed parameters.
        debug : internal usage documented for completes
              dictionary passed to model to allow calling model as model(**kwargs) for debugging

        Returns
        -------
        dataList of modelValues with parameters as attributes.

        Notes
        -----
        Example: extend time range ::

         data=js.dL('iqt_1hho.dat')
         diffusion=lambda A,D,t,wavevector: A*np.exp(-wavevector**2*D*t)
         data.fit(diffusion,{'D':[2],'amplitude':[1]},{},{'t':'X'})    # do fit
         # overwritte t to extend range
         newmodelvalues=data.modelValues(t=numpy.r_[0:100])   #with more t

        Example: 1-sigma interval for D ::

         data=js.dL('exampleData/iqt_1hho.dat')
         diffusion=lambda A,D,t,q: A*np.exp(-q**2*D*t)
         data.fit(diffusion,{'D':[0.1],'A':[1]},{},{'t':'X'})    # do fit
         # add errors of D for confidence limits
         upper=data.modelValues(D=data.D+data.D_err)
         lower=data.modelValues(D=data.D-data.D_err)
         data.showlastErrPlot()
         data.errPlot(upper,sy=0,li=[2,1,1])
         data.errPlot(lower,sy=0,li=[2,1,1])

        """
        imap= {'X':'ix','eX':'iex','Z':'iz','eZ':'iez'}
        if not hasattr(self,'model'):
            raise ValueError('First define a model to calculate model values!!')
        if 'default' in kwargs: # undocumented default values
            #a dictionary with parnames and values
            default=kwargs['default']
            del kwargs['default']
        else:
            default=None
        if 'debug' in kwargs:
            debug=True
            del kwargs['debug']
        else: debug=False
        mappedArgs={}                                              # all args to sent to model
        mappedNames=self._mapNames                                 # from calling fit
        co_argcount=self._code.co_argcount                         # number of arguments in model
        modelParameterNames=self._code.co_varnames[:co_argcount]   # from model definition
        # map the data names to model names
        for name in modelParameterNames:
            if name in mappedNames:
                pname=mappedNames[name]
            else:
                pname=name
            #and get the values
            pval=getattr(self,pname,None)
            if pval is not None:
                mappedArgs[name] = pval
            elif default is not None and name in default:
                mappedArgs[name]=default[name]
        # add the fixed parameters to the mappedArgs
        for key in self._fixpar:
            mappedArgs[key]=self._fixpar[key]
        # to override with given kwargs for fit changes or simulation of result
        for key in kwargs:
            mappedArgs[key]=kwargs[key]
        # create full dataArrays in dataList as return values
        values=dataList()
        columnIndex={'iy':-1,'iey':None} # last column for Y and no errors in simulated data
        # do calculation of model independently for self.X because of different length in X[i]
        # singleArgs contains the kwarguments for model
        singleArgs={}
        for i in range(len(self)):
            # xxArgs will have X,Z,eX and eZ values and appended Y values
            xxArgs=[]
            #shape the singleArgs and fill them with values
            for key,item in mappedArgs.items():
                if key in mappedNames and mappedNames[key] in ('X','Z','eX','eZ'):
                    try:
                        singleArgs[key]=item[i][self._xslice[i]]
                    except:                          # for new X from keywords equal for all sets
                        singleArgs[key]=item
                    xxArgs.append(singleArgs[key])
                    columnIndex[imap[mappedNames[key]]]=len(xxArgs)-1
                elif isinstance(item,(float,int)):   # single numbers
                    singleArgs[key]=item
                elif len(item)==1:                   # list with one element like independent parameter
                    singleArgs[key]=item[0]          # more for convenience to avoid  like [0]
                elif isinstance(item, (list, np.ndarray, atlist)):                        # lists
                    singleArgs[key]=item[i]
                else:
                    print(  'strange parameter found : ',key, item,len(item),isinstance(item,list),type(item))
                if isinstance(singleArgs[key], atlist):
                    singleArgs[key]=singleArgs[key].array
            for key in singleArgs:
                # soft limits increase chi2 in _errorfunction
                # here set hard limits to avoid breaking of limits
                if key in self._limits:
                    # set minimum hard border
                    if self._limits[key][2] is not None and np.any(singleArgs[key]<self._limits[key][2]):
                        singleArgs[key]=self._limits[key][2]
                    # set maximum hard border
                    if self._limits[key][3] is not None and np.any(singleArgs[key]>self._limits[key][3]):
                        singleArgs[key]=self._limits[key][3]
            # here we first do some fast checking to prevent simple errors and give a direct hint
            # some variable might be missing, so we check and try to tell which one(s)
            mname=self._code.co_name
            margcount=self._code.co_argcount
            try:
                if self.model.func_defaults is not None: margcount-=len(self.model.func_defaults)
            except:
                if self.model.__defaults__ is not None: margcount -= len(self.model.__defaults__)
            lenArgs=len(singleArgs)
            missingVar=[x for x in self._code.co_varnames[:margcount] if x not in set(singleArgs.keys())]
            if debug:
                return singleArgs
            try:
                # calc the model values
                fX=self.model(**singleArgs)
            except :
                print('%s takes exactly %i arguments (%i given) missing %s ' % (mname, margcount, lenArgs, missingVar))
                raise
            if isinstance(fX,int) and fX<0:
                # error in model
                return fX
            elif hasattr(fX,'_isdataArray') and fX.ndim>1:
                values.append(fX)
            else:
                xxArgs.append(np.asarray(fX))    # fX should be array
                values.append(np.vstack(xxArgs))
                values[-1].setColumnIndex(**columnIndex)
                values[-1].setattr(fX)                   # just in case there are attributes in return value fX
        #put used parameters to values and consider _mapNames
        for key,item in mappedArgs.items():
            if key in self._mapNames and self._mapNames[key] in ['X','Z','eX','eZ']:
                setattr(values,key,['@->'+self._mapNames[key]]*len(values))
            else:
                setattr(values,key,item)
        return values

    def _getError(self,modelValues):
        # and calc error  and put it together
        # check if output was ok
        if (isinstance(modelValues,int) and modelValues<0):
            #there was an error in model but we return something not to break the fit
            error = np.hstack([y[xslice]*1000 for y, xslice in  zip(self.Y, self._xslice)])
            evalOK=False
        elif not np.all(np.isfinite(modelValues.Y.flatten)):
            # we have nans or inf in the result
            error = np.hstack([y[xslice]*1000 for y, xslice in  zip(self.Y, self._xslice)])
            evalOK=False
        elif self._nozeroerror:
            err=[((val-y[xslice])/ey[xslice]) for val,y,ey,xslice in  zip(modelValues.Y,self.Y,self.eY,self._xslice)]
            error=np.hstack(err)
            evalOK=True
        else:
            err=[(val-y[xslice])              for val,y,xslice    in  zip(modelValues.Y,self.Y,self._xslice)]
            error=np.hstack(err)
            evalOK=True
        chi2=sum(error**2)/(len(error)-len(self._p))
        return error,chi2,evalOK

    def _errorfunction(self,*args,**kwargs):
        """
        Calculates the weighted error for least square fitting using model from fit
        as (val-y)/ey if ey is given, otherwise unweigthed with ey=1.

        If makeErrPlot is used a intermediate stepwise output is created
        as y value plot with residuals.

        """
        self.numberOfModelEvaluations+=1
        # _p contains the variable parameters from the fit algorithm
        self._p,args=args
        #distribute variable parameters to kwargs, check limits and calc modelValues
        i=0
        for name,par0 in self._freepar.items():
            l=len(np.atleast_1d(par0))
            kwargs[name]=self._p[i:i+l]
            i=i+l
        limitweigth,limits,hardlimits=self._checklimits(self._p)
        modelValues=self.modelValues(**kwargs)
        # error determination including check of proper model evaluation
        error,chi2,evalOK=self._getError(modelValues)
        self._lastchi2=chi2
        self._lenerror=len(error)
        self._len_p=len(self._p)
        #optional errplot if calculation longer than 2 seconds ago
        now=time.time()
        if hasattr(self,'_errplot') and self._lasterrortime<now-2 and evalOK:
            # last calculation time
            self._lasterrortime=now
            self.showlastErrPlot(modelValues=modelValues,kwargs=kwargs)
        #output to commandline all 0.1 s
        if self._lasterrortimecommandline<now-0.1:
            self._lasterrortimecommandline = now
            self._show_output(chi2,limitweigth,limits,hardlimits,kwargs)
        if self._fitmethod in ['leastsq']:
            # this is for scipy.optimize.leastsq
            return error * limitweigth
        else:
            # this returns chi2 for all algorithm in scipy.optimize.minimize and differential_evolution
            return chi2  # error*limitweigth

    def _checklimits(self,parameters):
        """
        Checks the parameters if limits are reached and increases limitweigth.

        Returns
        -------
        limitweigth,limits,hardlimits

        """
        # add _p to corresponding kwargs[name] values to reproduce change in fit algorithm
        i=0
        limitweigth=1
        limits=[]
        hardlimits=[]
        for name,par0 in self._freepar.items():
            l=len(np.atleast_1d(par0))
            par=parameters[i:i+l]
            # here determine upper and lower bound
            if name in self._limits:
                # soft limits just increase chi2 by a factor limitweight >1
                if self._limits[name][0] is not None and np.any(par<self._limits[name][0]): #set minimum border
                    # increase with distance to border and number of parameters above border
                    wff=sum(abs(par-self._limits[name][0])*(par<self._limits[name][0]))
                    limitweigth+=1+wff*10
                    limits.append(name)
                if self._limits[name][1] is not None and np.any(par>self._limits[name][1]): # set maximum border
                    wff=sum(abs(par-self._limits[name][1])*(par>self._limits[name][1]))
                    limitweigth+=1+wff*10
                    limits.append(name)
                #  hard limits are set in modelValues here only tracking for output and increase weight
                if self._limits[name][2] is not None and np.any(par<self._limits[name][2]): # set minimum hard border
                    wff=sum(abs(par-self._limits[name][2])*(par<self._limits[name][2]))
                    limitweigth+=10+wff*10
                    hardlimits.append(name)
                if self._limits[name][3] is not None and np.any(par>self._limits[name][3]): # set maximum hard border
                    wff=sum(abs(par-self._limits[name][3])*(par>self._limits[name][3]))
                    limitweigth+=10+wff*10
                    hardlimits.append(name)
            i+=l
        return limitweigth,limits,hardlimits

    def _show_output(self,chi2,limitweigth=1,limits=[],hardlimits=[],kwargs={}):
        if self._output is None or self._output==False:
            # suppress output
            return
        print(  'chi^2 = %.5g * %.1g (limit weight) after %i evaluations'
                    %(chi2,limitweigth,self.numberOfModelEvaluations))
        outlist=''.join(['%-8s= %s %s %s\n' % (
                            (item,'',value,'')                   if item not in limits+hardlimits else
                            ((item,CSIr,value,' !limited'+ CSIe) if item not in hardlimits else
                            (item,CSIy,value,' !hard limited'+ CSIe)))
                                    for item,value in sorted(kwargs.items())])
        outlist+='-----fixed-----\n'
        for name,values in sorted(self._fixpar.items()):
            try:
                outlist+='%-8s=['%name+''.join([' %.4G'%val for val in values])+']\n'
            except:
                outlist+='%-8s=[%.4G]\n' %(name, values)
        print( outlist,)
        return

    def setlimit(self,**kwargs):
        """
        Set upper and lower limits for parameters in least square fit.

        Parameters
        ----------
        parname : [value x 4] , list of 4 x (float/None), default None
            Use as setlimit(parname=(lowerlimit, upperlimit,lowerhardlimit, upperhardlimit))
            - lowerlimit, upperlimit : float, default None
              soft limit: chi2 increased with distance from limit, nonfloat resets limit
            - lowerhardlimit, upperhardlimit: hardlimit float, None
              values are set to border , chi2 is increased strongly

        Notes
        -----
        Penalty methods are a certain class of algorithms for solving constrained optimization problems.
        Here the penalty function increases chi2 by a factor chi*f_conststrain
        - no limit overrun : 1
        - softlimits :  + 1+abs(val-limit)*10 per limit
        - hardlimits :  +10+abs(val-limit)*10 per limit

        Examples
        -------- ::

          setlimit(D=(1,100),A=(0.2,0.8,0.0001))  to set lower=1 and upper=100
                                                  A with a hard limit to avoid zero
          setlimit(D=(None,100))                  to reset lower and set upper=100
          setlimit(D=(1,'thisisnotfloat','',))    to set lower=1 and reset upper

        """
        if 'reset' in kwargs or len(kwargs)==0:
            self._limits={}
            return
        for key in kwargs.iterkeys():
            limits=[None,None,None,None]
            try:
                limits[0]=float(kwargs[key][0])
            except:
                pass
            try:
                limits[1]=float(kwargs[key][1])
            except:
                pass
            try:
                limits[2]=float(kwargs[key][2])
            except:
                pass
            try:
                limits[3]=float(kwargs[key][3])
            except:
                pass
            self._limits[key]=limits

    @property
    def has_limit(self):
        """
        Return existing limits

        without limits returns None

        """
        if isinstance(self._limits,dict) and self._limits!={}:
            return self._limits
        return None

    def fit(self,model,freepar={},fixpar={},mapNames={},method='leastsq',xslice=slice(None),condition=None,output=True,**kw):
        """
        Least square fit of model that minimizes chi**2 (uses scipy.optimize.leastsq).

        - A least square fit of the .Y values dependent on X (, Z) and attributes (multidimensional fitting).
        - Data attributes are used automatically in model if they have the same name as a parameter.
        - Resulting parameter errors are 1-sigma errors, if the data errors are 1-sigma errors.
        - Results can be simulated with changed parameters in .modelValues or .showlastErrPlot.

        Parameters
        ----------
        model : function or lambda
            Model function, should accept arrays as input (use numpy ufunctions in model).
             -example:  diffusion=lambda A,D,t,wavevector:A * np.exp(-wavevector**2*D*t)
             - Return value should be dataArray (.Y is used) or only Y values.
             - Errors in model should return negative integer.
        freepar : dictionary
            Fit parameter names with startvalues.
             - {'D':2.56,..}             one common value for all
             - {'D':[1,2.3,4.5,...],..}  individual parameters for independent fit.
             - [..] is extended with missing values equal to last given value. [1] -> [1,1,1,1,1,1]
        fixpar : dictionary
            Fixed parameters, overwrites data attributes. (see freepar for syntax)
        mapNames :    dictionary
            Map parameter names from model to attribute names in data e.g.  {'t':'X','wavevector':'q',}
        method : default 'leastsq', 'differential_evolution', ‘BFGS’, ‘Nelder-Mead’  or from scipy.optimize.minimize
            Type of solver for minimization, for options see scipy.optimize. See last example for a comparison.
             - Only 'leastsq' and 'BFGS' return errors for the fit parameters.
             - 'leastsq' is fastest. 'leastsq' is a wrapper around MINPACK’s lmdif and lmder algorithms which are
                a modification of the Levenberg-Marquardt algorithm.
             - All use bounds set in setlimits to allow bounds as described there.
             - 'differential_evolution' uses automatic bounds as (x0/10**0.5,x0*10**0.5)
               if no explicit limits are set for a freepar. x0 is start value from freepar.
             - For some methods the Jacobian is required.
        xslice : slice object
            Use selected X values by slicing.
             - xslice=slice(2,-3,2)       To skip first 2,last 3 and take each second
        condition : function or lambda
            A lambda function to determine which datapoints to include.
             - The function should evaluate to boolean with dataArray as input
               and combines with xslice used on full set (first xslice then the condition is used)
             - local operation on numpy arrays as  "&"(and), "|"(or), "^"(xor)
                - lambda a:(a.X>1) & (a.Y<1)
                - lambda a:(a.X>1) & (a.X<100)
                - lambda a: a.X>a.q * a.X
        output : None,'last'
            -  !=None  returns best parameters and erros
            -  None   Returns string
            - 'last' returns lastfit
        debug : 1,2
            | debug modus returns:
            | 1 Free and fixed parameters but not mappedNAmes.
            | 2 Parameters in modelValues as dict to call model as model(**kwargs) with mappedNames.
            | >2 Prints parameters sent to model and returns the output of model without fitting.
        kw : additional keyword arguments
            Forwarded to minimizer as given in method.

        Returns
        -------
         - dependent on output parameter
         - Final results with errors is in .lastfit
         - Fitparameters are additional in dataList object as .parname and corresponding errors as .parname_err.

        Examples
        --------
        Basic examples with synthetic data. Usually data are loaded from a file.

        - An error plot with residuals can be created for intermediate output ::

           data=js.dL('exampleData/iqt_1hho.dat')
           diffusion=lambda t,wavevector,A,D,b:A*np.exp(-wavevector**2*D*t)+b
           data.setlimit(D=(0,2))               # set a limit for diffusion values
           data.makeErrPlot()                   # create errorplot which is updated
           data.fit(model=diffusion ,
                freepar={'D':0.1,               # one value for all (as a first try)
                         'A':[1,2,3]},          # extended to [1,2,3,3,3,3,...3] independent parameters
                fixpar={'b':0.} ,               # fixed parameters here, [1,2,3] possible
                mapNames= {'t':'X',             # maps time t of the model as .X column for the fit.
                           'wavevector':'q'},   # and map model parameter 'wavevector' to data attribute .q
                condition=lambda a:(a.Y>0.1) )  # set a condition

        - Fit sine to simulated data ::

           import jscatter as js
           import numpy as np
           x=np.r_[0:10:0.1]
           data=js.dA(np.c_[x,np.sin(x)+0.2*np.random.randn(len(x)),x*0+0.2].T)           # simulate data with error
           data.fit(lambda x,A,a,B:A*np.sin(a*x)+B,{'A':1.2,'a':1.2,'B':0},{},{'x':'X'})  # fit data
           data.showlastErrPlot()                                                         # show fit
           print(  data.A,data.A_err)                                                        # access A and error

        - Fit sine to simulated data using an attribute in data with same name ::

           x=np.r_[0:10:0.1]
           data=js.dA(np.c_[x,1.234*np.sin(x)+0.1*np.random.randn(len(x)),x*0+0.1].T)     # create data
           data.A=1.234                                                                   # add attribute
           data.makeErrPlot()                                                             # makes erroplot prior to fit
           data.fit(lambda x,A,a,B:A*np.sin(a*x)+B,{'a':1.2,'B':0},{},{'x':'X'})          # fit using .A

        - Fit sine to simulated data using an attribute in data with different name and fixed B ::

           x=np.r_[0:10:0.1]
           data=js.dA(np.c_[x,1.234*np.sin(x)+0.1*np.random.randn(len(x)),x*0+0.1].T)       # create data
           data.dd=1.234                                                                    # add attribute
           data.fit(lambda x,A,a,B:A*np.sin(a*x)+B,{'a':1.2,},{'B':0},{'x':'X','A':'dd'})   # fit data
           data.showlastErrPlot()                                                           # show fit

        - Fit sine to simulated dataList using an attribute in data with different name and fixed B from data.
          first one common parameter then as parameter list in []. ::

           x=np.r_[0:10:0.1]
           data=js.dL()
           ef=0.1  # increase this to increase error bars of final result
           for ff in [0.001,0.4,0.8,1.2,1.6]:                                                      # create data
               data.append( js.dA(np.c_[x,(1.234+ff)*np.sin(x+ff)+ef*ff*np.random.randn(len(x)),x*0+ef*ff].T) )
               data[-1].B=0.2*ff/2                                                                 # add attributes
           # fit with a single parameter for all data, obviously wrong result
           data.fit(lambda x,A,a,B,p:A*np.sin(a*x+p)+B,{'a':1.2,'p':0,'A':1.2},{},{'x':'X'})
           data.showlastErrPlot()                                                                 # show fit
           # now allowing multiple p,A,B as indicated by the list starting value
           data.fit(lambda x,A,a,B,p:A*np.sin(a*x+p)+B,{'a':1.2,'p':[0],'B':[0,0.1],'A':[1]},{},{'x':'X'})
           # plot p against A , just as demonstration
           p=js.grace()
           p.plot(data.A,data.p,data.p_err)

        - **2D fit** data with an X,Z grid data and Y values
          For 3D fit we calc Y values from X,Z coordinates (only for scalar Y data).
          For fitting we need data in X,Z,Y column format.
          ::

           import matplotlib.pyplot as plt
           from mpl_toolkits.mplot3d import Axes3D
           from matplotlib import cm
           #
           # create 3D data with X,Z axes and Y values as Y=f(X,Z)
           x,z=np.mgrid[-5:5:0.25,-5:5:0.25]
           xyz=js.dA(np.c_[x.flatten(),z.flatten(),0.3*np.sin(x*z/np.pi).flatten()+0.01*np.random.randn(len(x.flatten())),0.01*np.ones_like(x).flatten() ].T)
           # set columns where to find X,Y,Z )
           xyz.setColumnIndex(ix=0,iz=1,iy=2,iey=3)
           #
           ff=lambda x,z,a,b:a*np.sin(b*x*z)
           xyz.fit(ff,{'a':1,'b':1/3.},{},{'x':'X','z':'Z'})
           #
           fig = plt.figure()
           ax = fig.add_subplot(111, projection='3d')
           ax.scatter(xyz.X,xyz.Z,xyz.Y)
           ax.tricontour(xyz.lastfit.X,xyz.lastfit.Z,xyz.lastfit.Y, cmap=cm.coolwarm,linewidth=0, antialiased=False)
           plt.show(block=False)

        - Comparison of fit methods ::

           import numpy as np
           import jscatter as js
           diffusion=lambda A,D,t,elastic,wavevector=0:A*np.exp(-wavevector**2*D*t)+elastic

           i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
           i5.makeErrPlot(title='diffusion model residual plot')
           i5.fit(model=diffusion,freepar={'D':0.2,'A':1}, fixpar={'elastic':0.0},
                  mapNames= {'t':'X','wavevector':'q'},  condition=lambda a:a.X>0.01  )
           # 22 evaluations; error YES -> 'leastsq'
           #with D=[0.2]  130 evaluations

           i5.fit(model=diffusion,freepar={'D':0.2,'A':1}, fixpar={'elastic':0.0},
                  mapNames= {'t':'X','wavevector':'q'},  condition=lambda a:a.X>0.01 ,method='BFGS' )
           # 52 evaluations, error YES

           i5.fit(model=diffusion,freepar={'D':0.2,'A':1}, fixpar={'elastic':0.0},
                  mapNames= {'t':'X','wavevector':'q'},  condition=lambda a:a.X>0.01 ,method='differential_evolution' )
           # 498 evaluations, error NO ; needs >20000 evaluations using D=[0.2]; use only with low number of parameters

           i5.fit(model=diffusion,freepar={'D':0.2,'A':1}, fixpar={'elastic':0.0},
                  mapNames= {'t':'X','wavevector':'q'},  condition=lambda a:a.X>0.01 ,method='Powell' )
           # 121 evaluations; error NO

           i5.fit(model=diffusion,freepar={'D':0.2,'A':1}, fixpar={'elastic':0.0},
                  mapNames= {'t':'X','wavevector':'q'},  condition=lambda a:a.X>0.01 ,method='SLSQP' )
           # 37 evaluations, error NO

           i5.fit(model=diffusion,freepar={'D':0.2,'A':1}, fixpar={'elastic':0.0},
                  mapNames= {'t':'X','wavevector':'q'},  condition=lambda a:a.X>0.01 ,method='COBYLA' )
           # 308 evaluations, error NO


        Notes
        -----
        * The concept is to use data attributes as fixed parameters for the fit (multidimesional fit).
          This is realized by using data attribute with same name as fixed parameters if not given in freepar or fixpar.
        * Fit parameters can be set equal for all elements 'par':1 or independent 'par':[1]
          just by writing the start value as a single float or as a list of float.
          The same is for fixed parameters.
        * Change the fit is easy done by moving 'par':[1] between freepar and fixpar.
        * Limits for parameters can be set prior to the fit as .setlimit(D=[1,4,0,10]).
          The first two numbers (min,max) are softlimits (increase chi2) and
          second are hardlimits to avoid extreme values (hard set to these values if outside interval and increasing chi2).
        * If errors exist (.eY) and are not zero, weighted chi**2 is minimized.
          Without error or with single errors equal zero an unweighted chi**2 is minimized (equal weights).
        * The change of parameters can be simulated by .modelValues(D=3) which overides attributes and fit parameters.
        * .makeErrPlot creates an errorplot with residuals prior to the fit for intermediate output.
        * The last errPlot can be recreated after the fit with showlastErrPlot.
        * The simulated data can be shown in errPlot with .showlastErrPlot(D=3).
        * Each dataArray in a dataList can be fit individually (same model function) like this ::

           # see Examples for dataList creation
           for dat in datlist:
               dat.fit(model,freepar,fixpar,.....)

        **Additinal kwargs for 'leastsq'** ::

         all additional optional arguments passed to leastsq (see scipy.optimize.leastsq)
         col_deriv    default  0
         ftol         default  1.49012e-08
         xtol         default  1.49012e-08
         gtol         default  0.0
         maxfev       default  200*(N+1).
         epsfcn       default  0.0
         factor       default  100
         diag         default  None



        **Parameter result by name in lastfit** ::

         exda.D                    eg freepar 'D' with errors; same for fixpar but no error
                                   use exda.lastfit.attr to see attributes of model
         exda.lastfit[i].D         parameter D result of best fit
         exda.lastfit[i].D_err     parameter D error as 1-sigma error, if errors of data have also 1-sigma errors in .eY
         exda.lastfit.chi2         sum((y-model(x,best))**2)/dof;should be around 1 if  1-sigma errors in .eY
         exda.lastfit.cov          hessian**-1 * chi2
         exda.lastfit.dof          degrees of freedom   len(y)-len(best)
         exda.lastfit.func_name    name of used model
         exda.lastfit.func_code    where to find code of used model
         exda.lastfit.X            X values in fit
         exda.lastfit.Y            Y values in fit
         exda.lastfit.eY           Yerrors in fit

        If intermediate output is desired (calculation of modeValues in errorplot) use
        exda.makeErrPlot()             to create an output plot and parameter output inside

        How to construct a model:
         The model function gets .X (.Z, .eY, eX, eZ) as ndarray and parameters (from attributes)
         as scalar input. It should return an ndarray as output (as Y values) or dataArray (.Y is used).
         Therefore it is advised to use numpy ufunctions in the model because these use them automatically
         in the correct way. Instead of math.sin use numpy.sin, which is achieved by
         import numpy as np
         and use np.sin
         see   http://docs.scipy.org/doc/numpy/reference/ufuncs.html

        A bunch of models as templates can be found in formel.py, formfactor.py, stucturefactor.py.

        """
        # remove lastfit if existing
        if 'debug' in kw:
            debug=kw['debug']
        else: debug=False
        try:
            del self.lastfit  # delete a previous fit result
        except:pass

        # store all we need for fit with attributes
        self.model=model
        self.numberOfModelEvaluations=0
        try:
            self._code = self.model.func_code   # python2
        except:
            self._code = self.model.__code__    # python3
        argcount=self._code.co_argcount
        if len(set(protectedNames) & set(self._code.co_varnames[:argcount]))!=0:
            raise NameError(' model should not have a parameter name of :X, Y, Z, eX, eY, eZ')
        self._freepar=collections.OrderedDict(sorted(freepar.items(), key=lambda t: t[0]))
        self._mapNames=collections.OrderedDict(sorted(mapNames.items(), key=lambda t: t[0]))
        self._fixpar=collections.OrderedDict(sorted(fixpar.items(), key=lambda t: t[0]))
        self._lasterrortime=0         # to limit frequence for optional output in _errorfunction,0 so first is ploted
        self._lasterrortimecommandline = 0  # to limit frequence for output on commandline
        self._output=output
        # we need a list of slices to select values to be included for fit
        if isinstance(xslice,slice):
            xslice=[xslice]
        xslice.extend([xslice[-1]]*(len(self)-len(xslice)))  # extend to len(self) with last element
        self._xslice=xslice
        # overwite _xslice if a condition was given
        if condition is not None:
            for i in range(len(self)):
                #intersection of condition and full slice over data to use both
                cond=condition(self[i])
                if isinstance(cond,bool):
                    cond=np.full(len(self[i].X), cond, dtype=bool)
                self._xslice[i]=np.intersect1d(np.where(cond)[0],np.arange(len(self[i].X))[self._xslice[i]])
        # ensure length of parameter list =length self
        for key in self._freepar:
            if isinstance(self._freepar[key],list):
                self._freepar[key].extend([self._freepar[key][-1]]*(len(self)-len(self._freepar[key])))  # extend
        for key in self._fixpar:
            if isinstance(self._fixpar[key],list):
                self._fixpar[key].extend([self._fixpar[key][-1]]*(len(self)-len(self._fixpar[key])))  # extend

        # only with nonzero errors we cal in _errorfunction weighted chi**2
        if any([ey is None for ey in self.eY]):
            self._nozeroerror=False
        else:
            # test if Zero (is False) in eY
            self._nozeroerror=np.all([np.all(ey[xslice]) for ey, xslice in zip(self.eY, self._xslice)])
            if not self._nozeroerror:
                warnings.warn('Errors equal zero detected. Using non-weighted chi**2', UserWarning)

        if debug:
            if debug==1:
                return dict(self._freepar,**self._fixpar)
            elif debug==2:
                return self.modelValues(**dict(self._freepar,debug=2,**self._fixpar))
            else:
                # show parameter sent to modeValues and returns output of modelValues
                print(  'sent to modelValues from fit in  debug mode:')
                outlist=''.join(['%-8s= %s %s %s\n' % (item,'',value,'')
                                 for item,value in sorted(dict(self._freepar,**self._fixpar).items())])
                print(  outlist)
                return self.modelValues(**dict(self._freepar,**self._fixpar))

        # this is the fit
        print(   '^^^^^^^^^^^^^^ start fit ^^^^^^^^^^^^^^')
        startfittime=time.time()
        # list of free parameters for fit routine as 1d array
        freeParValues=np.r_[[sval for k,val in self._freepar.items() for sval in np.atleast_1d(val)]]
        if method in ['leastsq']:
            self._fitmethod = 'leastsq'
            res=scipy.optimize.leastsq(self._errorfunction,x0=freeParValues,args=(0),full_output=1,**kw)
            # prepare for proper storage
            (best,cov, info,  mesg,ier)=res
            dof=info['fvec'].size-len(best)-1  # degrees of freedom
            chi2=sum(info['fvec']**2)/dof
            try:
                cov=cov*chi2
                best_err=np.sqrt(cov.diagonal())
            except (TypeError,AttributeError):
                cov=None
                best_err=None
        elif method[:3]=='dif':
            self._fitmethod='differential_evolution'
            bounds=[]
            for name,values in self._freepar.items():
                if name in self._limits:
                    for val in np.atleast_1d(values):
                        bounds.append((self._limits[name][0],self._limits[name][1]))
                else:
                    for val in np.atleast_1d(values):
                        bounds.append((val/10**0.5,val*10**0.5))
            res=scipy.optimize.differential_evolution(func=self._errorfunction, bounds=bounds,args=(0,), **kw)
            ier=res.success
            mesg=res.message
            best=res.x
            dof = self._lenerror - self._len_p - 1  # degrees of freedom
            chi2=res.fun
            cov=None
            best_err=None
        else:
            self._fitmethod='minimize_'+method
            res=scipy.optimize.minimize(self._errorfunction, x0=freeParValues, args=(0), method=method,**kw)
            ier=res.success
            mesg=res.message
            best=res.x
            chi2=res.fun
            dof=self._lenerror-self._len_p-1  # degrees of freedom
            try:
                cov=res.hess_inv*chi2
                best_err=np.sqrt(cov.diagonal())
            except AttributeError:
                cov=None
                best_err=None

        if ier not in [True,1,2,3,4] : # NOT succesful fit
            print( CSIr+'Error '+str(mesg)+CSIe)
            print( CSIr+'last result : '+CSIe)
            i=0
            for name,value in self._freepar.items():
                l=len(np.ravel(value))
                print(  name,best[i:i+l])
                i+=l
            print(  CSIr+'fit NOT succesfull!!'+CSIe)
            raise notSuccesfullFitException(mesg)

        # -------------------------------------------
        # succesful fit -->
        #add fitted ParNames to self with correct name
        i=0
        resultpar={}
        for name,value in self._freepar.items():
            l=len(np.ravel(value))
            resultpar[name]=best[i:i+l]
            self.__setlistattr__(name,best[i:i+l])
            if best_err is not None: self.__setlistattr__(name+'_err',best_err[i:i+l])
            i+=l
        # write lastfit into attribute directly where modelValues uses the parameters set with __setlistattr__
        modelValues=self.modelValues(**resultpar)
        #  a negative integer indicates error was returned from model
        if isinstance(modelValues,int):
            print(  CSIr+'fit NOT succesfull!!'+CSIe)
            raise notSuccesfullFitException('model returns single integer. Error occured')
        self.__setlistattr__('lastfit',modelValues)
        # add results of freepar to lastfit with errors
        i=0
        for name,value in self._freepar.items():
            l=len(np.ravel(value))
            self.lastfit.__setlistattr__(name,best[i:i+l])
            if best_err is not None: self.lastfit.__setlistattr__(name+'_err',best_err[i:i+l])
            i+=l
        # add fixpar to lastfit without error
        for key,val in self._fixpar.items():
            self.lastfit.__setlistattr__(key,val)
        #update the errorplot if existing
        if hasattr(self,'_errplot'):
            self.showlastErrPlot(modelValues=modelValues)
        # put everything into lastfit
        self.lastfit.__setlistattr__('chi2',chi2)
        self.lastfit.__setlistattr__('dof',dof)
        try:
            # python2
            self.lastfit.__setlistattr__('func_code',str(self._code))
            self.lastfit.__setlistattr__('func_name',str(self.model.func_name))
        except:
            # python3
            self.lastfit.__setlistattr__('func_code', str(self._code))
            self.lastfit.__setlistattr__('func_name', str(self.model.__name__))
        #
        print(CSIg+'fit finished after %.3g s   --->>   result   --->>' %(time.time() - startfittime)+CSIe)
        limitweigth,limits,hardlimits=self._checklimits(best)
        self._show_output(chi2,1,limits,hardlimits,resultpar)
        print('degrees of freedom = ', dof)
        if cov is not None:
            # this ouput only if cov and errors are defined
            self.lastfit.__setlistattr__('cov', cov)
            covt=cov-cov.diagonal()
            dim=np.shape(covt)[0]
            imax=covt.argmax()
            covmax=covt.max()
            #freparnames as in freeparvaluess
            freeParNames=reduce(list.__add__,[[k]*len(np.atleast_1d(v)) for k,v in self._freepar.items()])
            message='nondiag covariance Matrix maximum '+'%.5g' %(covmax)+' between '+\
                 str(freeParNames[imax//dim])+' and '+str(freeParNames[imax%dim])+'\n'
            if self._nozeroerror:
                if covmax<0.3:
                    print(  CSIg+message+'         <0.3 seems to be OK'+CSIe)
                elif 0.3<covmax<.8:
                    print(  CSIy+message+'     >0.3 seems to be too large'+CSIe)
                elif 0.8<covmax:
                    print(  CSIr+message+'this is to big'+CSIe)
                # only with 1-sigma errors the chi2 should be close to one
                if  (chi2-1)>10:
                    print(  'a bad model or to small error estimates!')
                elif 1<(chi2-1)<10:
                    print(  'should be closer to 1  ;   Is this a good model; good errors?')
                elif  0.2<(chi2-1)<1:
                    print(  'looks quite good; satisfied or try again to get it closer 1?')
                elif  -0.2<(chi2-1)<0.2:
                    print(  'good!!! not to say its excellent')
                elif  -0.5<(chi2-1)<-0.2:
                    print(  ' seems to be overfitted,\n to much parameters or to large error estimates.')
                else:
                    print(   'overfitting!!!!\n to much parameters or to large error estimates')
            else:
                print(CSIy+'No Errors or zeros in Error!! Without proper error weight fit errors may not reflect 1-sigma errors!'+CSIe)
        try:
            if output[:4]=='last':
                return self.lastfit
            elif output is not None:
                return best,best_err
        except:pass
        print(  '_________fit succesfully converged. We are done here !!__________')

        return

    # placeholder for errPlot functions

    def makeNewErrPlot(self,**kwargs):
        """dummy"""
        pass
    def makeErrPlot(self,**kwargs):
        """dummy"""
        pass
    def detachErrPlot(self):
        """dummy"""
        pass
    def killErrPlot(self,**kwargs):
        """dummy"""
        pass
    def savelastErrPlot(self,  **kwargs):
        """dummy"""
        pass
    def errPlot(self,*args,**kwargs):
        """dummy"""
        pass
    def showlastErrPlot(self, **kwargs):
        """dummy"""
        pass
    def errPlotTitle(self,**kwargs):
        """dummy"""
        pass
##################################################################################

# dataList inlcuding errPlot functions

class dataList(dataListBase):

    def makeNewErrPlot(self,**kwargs):
        """
        Creates a NEW ErrPlot without destroying the last. See makeErrPlot for details.

        Parameters
        ----------
        **kwargs
            keyword arguments passed to makeErrPlot

        """
        self.detachErrPlot()
        self.makeErrPlot(**kwargs)

    def makeErrPlot(self,title=None,showfixpar=True,**kwargs):
        """
        Creates a GracePlot for intermediate output from fit with residuals.
        
        ErrPlot is updated only if consecutive steps need more than 2 seconds.
        
        Parameters
        ----------
        title : string
            title of plot
        residuals : string
            plot type of residuals
            'absolut' or 'a'  absolute residuals
            'relative' or 'r'  relative =res/y
        showfixpar : boolean (None,False,0 or True,Yes,1)
            show the fixed parameters in errplot
        yscale,xscale : 'n','l' for 'normal', 'logarithmic'
            y scale, log or normal (linear)
        fitlinecolor : int, [int,int,int]
            Color for fit lines (or line style as in plot).
            if not given same color as data.

        """
        yscale='n'
        xscale='n'
        yminmax=[None,None]
        xminmax=[None,None]

        if not (hasattr(self,'_errplot') and self._errplot.is_open()):
            # we need to make a new one
            self._errplot=openplot()
            if not hasattr(self,'_errplottype'):
                self._errplottype=None        # type of errplot set later
            self._errplottitle=''
        # do errplot layout
        if 'residuals' in  kwargs:
            if kwargs['residuals'][0]=='r':
                self._errplottype='relative'
            else:
                self._errplottype='absolute'
        if title is not None:
            self._errplottitle=str(title)
        self._errplot.Multi(2,1)
        self._errplot[0].Title(self._errplottitle)
        self._errplot[0].SetView(0.1,0.255,0.95,0.9)
        self._errplot[1].SetView(0.1,0.1,0.95,0.25)
        self._errplot[0].Yaxis(label='Y values')
        self._errplot[0].Xaxis(label='')
        self._errplot[1].Xaxis(label='X values')
        if 'fitlinecolor' in kwargs:
            self._errplot[0].fitlinecolor=kwargs['fitlinecolor']
            del kwargs['fitlinecolor']
        if 'yscale' in kwargs:
            if yscale[0]=='l':yminmax=[0.1,10]
            self._errplot[0].Yaxis(scale=kwargs['yscale'],min=yminmax[0],max=yminmax[1])
        if 'xscale' in kwargs:
            if xscale[0]=='l':xminmax=[0.1,10]
            self._errplot[0].Xaxis(scale=kwargs['xscale'],min=xminmax[0],max=xminmax[1])
            self._errplot[1].Xaxis(scale=kwargs['xscale'],min=xminmax[0],max=xminmax[1])
        if self._errplottype=='relative':
            self._errplot[1].Yaxis(label='residuals/Y')
        else:
            self._errplot[1].Yaxis(label='residuals')
        if showfixpar:
            self._errplotshowfixpar=True
        else:
            try:
                del self._errplotshowfixpar
            except:pass
        self._errplot[0].clear()
        self._errplot[1].clear()

    def detachErrPlot(self):
        """
        Detaches ErrPlot without killing it and returns a reference to it.


        """

        if hasattr(self,'_errplot'):
            errplot=self._errplot
            del self._errplot
            return errplot

    def errPlotTitle(self,title):
        self._errplot[0].Title(title)

    def killErrPlot(self,filename=None):
        """
        Kills ErrPlot

        If filename given the plot is saved.
        """
        if hasattr(self,'_errplot'):
            self.savelasterrplot(filename)
            self._errplot.Exit()
            del self._errplot

    def savelastErrPlot(self, filename, format='agr', size=(1012, 760), dpi=300, **kwargs):
        """
        Saves errplot to file with filename.
        """
        try:
            # self._errplot.is_open() gives True but is Disconnected if closed
            # so try this instead
            self._errplot._send('')
        except:
            self.showlastErrPlot(**kwargs)
        if filename is not None and isinstance(filename, str):
            self._errplot.Save(filename,format=format,size=size,dpi=dpi)

    def errPlot(self,*args,**kwargs):
        """
        Plot into an existing ErrPlot. See Graceplot.plot for details.

        """
        if (hasattr(self,'_errplot') and self._errplot.is_open()):
            self._errplot[0].plot(*args,**kwargs)
            self._errplot[0].legend()
        else:
            raise AttributeError('There is no errPlot to plot into')

    def showlastErrPlot(self, title=None, modelValues=None, **kwargs):
        """
        Shows last ErrPlot as created by makeErrPlot with last fit result.

        Same arguments as in makeErrPlot.

        Additional keyword arguments are passed as in modelValues and simulate changes in the parameters.
        Without parameters the last fit is retrieved.

        """
        self.makeErrPlot(title=title,**kwargs)
        if 'yscale' in kwargs:del kwargs['yscale']
        if 'xscale' in kwargs:del kwargs['xscale']
        if modelValues is None:
            # calculate modelValues if not given
            modelValues=self.modelValues(**kwargs)
        # generate some usefull output from fit parameters
        outlist=''
        for name in sorted(self._freepar):
            # here we need the names from modelValues
            values=np.atleast_1d(getattr(modelValues,name))   #modelValues.__getdatalistattr__(name)
            outlist+='%-8s=[' %name + ''.join([' %.4G'%val for val in values])+']\\n'
        if hasattr(self,'_errplotshowfixpar'):
            outlist+='-----fixed-----\\n'
            for name,values in sorted(self._fixpar.items()):
                try:
                    outlist+='%-8s=['%name+''.join([' %.4G'%val for val in values])+']\\n'
                except:
                    outlist+='%-8s=[%.4G]\\n' %(name, values)
        #plot the data that contribute to the fit
        for XYeY,xslice,c in zip(self,self._xslice,range(1,1+len(self.X))):
            if hasattr(XYeY,'eY'):
                self._errplot[0].Plot(XYeY.X[xslice],XYeY.Y[xslice],XYeY.eY[xslice],symbol=[-1,0.3,c],line=0,comment='d %s' %c)
            else:
                self._errplot[0].Plot(XYeY.X[xslice],XYeY.Y[xslice],                symbol=[-1,0.3,c],line=0,comment='d %s' %c)
        # plot modelValues and residuals
        residual=[]
        error=[]
        # if X axis is changed in kwargs we dont plot residuals
        showresiduals=not next((k for k,v in self._mapNames.items() if v == 'X')) in kwargs
        for mXX,mYY,XX,YY,eYY,xslice,c  in zip(modelValues.X,modelValues.Y,
                                               self.X,self.Y,self.eY,self._xslice,range(1,1+len(self.X))):
            if hasattr(self._errplot[0],'fitlinecolor'):
                if isinstance(self._errplot[0].fitlinecolor,int):
                    cc=[1,1,self._errplot[0].fitlinecolor]
                else:
                    cc=self._errplot[0].fitlinecolor
            else:
                cc=[1,1,c]
            self._errplot[0].Plot(mXX,mYY,symbol=0,line=cc,legend=outlist,comment='f %s' %c)
            outlist = ''  # only first get nonempty outlistif np.all(mXX==XX):
            if showresiduals:
                # residuals type
                residual.append(YY[xslice]-mYY)
                error.append(residual[-1])
                if self._errplottype=='relative':
                    residual[-1]=(residual[-1]/YY[xslice])
                self._errplot[1].Plot(XX[xslice],residual[-1],symbol=0,line=[1,1,c],legend=outlist,comment='r %s' %c)
                if self._nozeroerror:
                    error[-1]/= eYY[xslice]
        if not showresiduals:
            self._errplot[0].Subtitle(r'No residuals as X is changed for simulation.')
            return
        error=np.hstack(error)
        chi2=sum(error**2)/(len(error)-len(self._p))
        try:
            factor=5
            residual=np.array(residual)
            ymin=residual.mean()-residual.std()*factor
            ymax=residual.mean()+residual.std()*factor
            self._errplot[1].Yaxis(ymin=ymin,ymax=ymax,scale='n')
        except:
            pass
        self._errplot[0].Legend(charsize=0.7)
        if hasattr(self.model,'func_name'):
            modelname='Model '+str(self.model.func_name)
        elif hasattr(self.model,'__name__'):
            modelname='Model '+str(self.model.__name__) # python3
        else:
            modelname=''
        self._errplot[0].Subtitle(modelname+r' with chi\S2\N=%g (DOF = %i points - %i parameters)' %(chi2,self._lenerror,self._len_p))

##################################################################################
# this will generate automatic attributes
def gen_XYZ(cls,name,ixyz):
    """
    generate property with name name that returns column ixyz
    cls needs to be accessible as class[ixyz]

    Parameters
    ----------
    cls : class with column structure
    name : name of the property
    ixyz : index of column to return

    Returns
    -------
    array

    """
    def get(cls):
        if not hasattr(cls,ixyz):
            raise AttributeError('dataArray has no attribute ',name)
        if not isinstance(getattr(cls,ixyz),int):
            raise AttributeError('dataArray. '+ixyz,'needs to be integer.')
        if cls.ndim==1:
            return cls.view(np.ndarray)
        elif cls.ndim>1:
            return cls[getattr(cls,ixyz)].view(np.ndarray)
    def set(cls,val):
        if not hasattr(cls,ixyz):
            raise AttributeError('dataArray has no attribute ',name)
        if cls.ndim==1:
            cls[:]=val
        elif cls.ndim>1:
            cls[getattr(cls,ixyz),:]=val
    def delete(cls):
        try:
            delattr(cls,ixyz)
        except:pass

    docu="""this delivers attributs of dataArray class"""
    setattr(cls.__class__,name,property(get,set,delete,doc=docu))


class dataArrayBase(np.ndarray):


    def __new__(subtype, input=None,
                dtype=None,
                filename=None,
                block=None,
                index=0,
                usecols=None,
                skiplines=None,
                replace=None,
                ignore='#',
                delimiter=None,
                takeline=None,
                lines2parameter=None,
                XYeYeX=None):
        """
        dataArray (ndarray subclass) with attributes for fitting, plotting, filter.

        - A subclass of numpy ndarrays with attributes to add parameters describing the data.
        - Allows fitting, plotting, filtering, prune and more.
        - .X, .Y, .eY link to specified columns.
        - Numpy array functionality is preserved.
        - dataArray creation parameters (below) mainly determine how a file is read from file.

        Parameters
        ----------
        input : string, ndarray
            Object to create a dataArray from as numpy array, filename, list of strings, IOString.
        dtype : data type
            dtype of final dataArray, see numpy.ndarray
        index : int, default 0
            Index of the dataset in the given input to select one from multiple.
        block : string, list of integer
            String (as first word in line) that separates data blocks in ASCII text.
            If None is given start or end of block is chosen as data section with parameter section.
            If integers (i,j,k) slices the lines in file as lines[i:j:k]. See help below for details.
        XYeYeX : list integers, default=[0,1,2,None,None,None]
            Columns for X, Y, eY, eX, Z, eZ.
            Change later with eg. setColumnIndex(3,5,32).
            Values in dataArray can be changed by  dataArray.X=[list of length X ].
        usecols : list integers [0,1,4]
            Use only given columns and ignore others.
        ignore : string, default '#'
            Ignore lines starting with string e.g. '#'.
            For more complex lines to ignore use skiplines.
        replace : dictionary of strings eg. = {'old':'new','bad':'good'}
            Pairs in this dictionary are replaced prior to other actions.
            E.g. for replacement of semicolon by spaces or comma by points.
        skiplines : boolean function, list of string or single string
             Skip line if line meets condition. Function gets the list of words in a line.
             Examples:
              - lambda words: any(w in words for w in ['',' ','NAN',''*****])   #with exact match
              - lambda words: any(float(w)>3.1411 for w in words)
              - lambda words: len(words)==1
             If a list is given, the lambda function is generated automatically as in above example.
             If single string is given, it is tested if string is a substring of any word (  'abc' in '12 3abc4 56')
        delimiter : string
            Separator between data fields in a line, default any whitespace.
            E.g. '\\t' tabulator
        takeline : string
            takeline is a single string as optional first word in a line with data.
            E.g. PDB structures mark lines with atom positions with ATOM in first place.
            takeline='ATOM' delivers lines with atom positions.
        lines2parameter : list of integer
            List of lines numbers i which to prepend with 'line_i' to be found as attribute line_i.
            Used to mark lines with parameters without name.

        Returns
        -------
            dataArray

        Notes
        -----
        - Attributes to avoid (they are in the name space of numpy ndarrays):
          T,mean,max,min,... These names are substitute by appended '_' (underscore) if found in read data.
          Get a complete list by  "dir(np.array(0))".
        - Avoid attribute names including special math characters as " ** + - / & ".
          Any char that can be interpreted as a function (eg  datalist.up-down)
          will be interpreted from python as : updown=datalist.up operator(minus) down
          and result in: AttributeError.
          To get the values use getattr(dataList,'up-down') or avoid usage of these characters.
        - If an attribute 'columnname' exists with a string containing columnnames separated by semicolon
          the corresponding columns can be accessed in 2 ways ( columnname='wavevector; Iqt' ):
           - attribute with prepended underscore  '_'+'name' => data._Iqt
           - columnname string used as index                 => data['Iqt']
          From the names all char like "+-*/()[]()|§$%&#><°^, " are deleted.
          This is intended  for reading and not writing.

        **Data access/change** ::

           exa=js.dA('afile.dat')
           exa.columnname='t; iqt; e+iqt'  # if not given in read file
           exa.eY=exa.Y*0.05               # default for X, Y is column 0,1; see XYeYeX or .setColumnIndex ; read+write
           exa[-1]=exa[1]**4               # direct indexing of columns; read+write
           exa[-1,::2]=exa[1,::2]*4        # direct indexing of columns; read+write; each second is used (see numpy)
           eq1=exa[2]*exa[0]*4             # read+write
           iq2=exa._iqt*4                  # access by underscore name; only read
           eq3=exa._eiqt*exa._t*4          # read
           iq4=exa['iqt']*4                # access like dictionary; only read
           eq5=exa['eiqt']*exa['t']*4      # read
           aa=np.r_[[np.r_[1:100],np.r_[1:100]**2]] #load from numpy array
           daa=js.dA(aa)                            # with shape
           daa.Y=daa.Y*2                            # change Y values; same as daa[1]
           dbb=js.zeros((4,12))                     # empty dataArray
           dbb.X=np.r_[1:13]                        # set X
           dbb.Y=np.r_[1:13]**0.5                   # set Y
           dbb[2]=dbb.X*5
           dbb[3]=0.5                               # set 4th column
           dbb.a=0.2345
           dbb.setColumnIndex(ix=2,iy=1,iey=None)   # change column index for X,Y, end no eY

        Selecting  ::

           ndbb=dbb[:,dbb.X>20]            # only X>20
           ndbb=dbb[:,dbb.X>dbb.Y/dbb.a]   # only X>Y/a

        **Read/write** ::

           import jscatter as js
           #load data into dataArray from ASCII file, here load the third datablock from the file.
           daa=js.dA('./exampleData/iqt_1hho.dat',index=2)
           dbb=js.ones((4,12))
           dbb.ones=11111
           dbb.save('folder/ones.dat')
           dbb.save('folder/ones.dat.gz')  # gziped file

        **Rules for reading of ASCII files**

        """
        if isinstance(input, str):  # if a filename is given
            if os.path.isfile(input):
                input=_read(input, block=block, usecols=usecols, skiplines=skiplines, replace=replace, ignore=ignore,
                            delimiter=delimiter, takeline=takeline, lines2parameter=lines2parameter)
                if input==[]:
                    raise IOError('nothing read from ' + input)
            else:
                raise NameError('file does not exist :' + input)
        elif isinstance(input, dict) and 'val' in input: # output of _read
            input=[input]
            index=0
        elif input is None: #creates empty dataArray
            return zeros(0)
        elif all([isinstance(zz,str) for zz in input]) and len(input)>0:# a list with lines from a file
            # just interpret it in _read
            input=_read(input, block=block, usecols=usecols, skiplines=skiplines, replace=replace, ignore=ignore,
                        delimiter=delimiter, takeline=takeline, lines2parameter=lines2parameter)
        if hasattr(input, '_isdataArray'):   #for completness
            return input
        elif isinstance(input, np.ndarray):# create dataArray from numpy array
            if dtype is None:
                dtype = input.dtype
            else:
                dtype = np.dtype(dtype)
            # Input array is an already formed ndarray instance
            # We first cast to be our class type
            data = np.asanyarray(input, dtype=dtype).view(subtype)
            data.comment=[]
            #data.raw_data=[]
        # create dataArray from a given list like the output from _read; default
        elif isinstance(input, list):
            #file already read by _read so we need to search for internal links like @name
            input=_searchForLinks(input)
            # check dtype of original data
            if dtype is None:
                dtype = input[int(index)]['val'].dtype
            else:
                dtype = np.dtype(dtype)
            # now create the dataArray as subtype and create attributes from para
            data = np.asanyarray(input[int(index)]['val'], dtype=dtype).view(subtype)
            data.comment=input[int(index)]['com']
            data.setattr(input[int(index)]['para'])
            data.raw_data= input[index:index]
            data._orgcommmentline=input[int(index)]['_original_comline']
        else:
            raise Exception('nothing useful found to create dataarray')
        #set column indices and defines ._ix,._iy,._iey and X,Y,EY...
        if XYeYeX is None:
            XYeYeX =(0,1,2) # default values
        data.setColumnIndex(XYeYeX)
        # generate columnname if existent in comments
        data.getfromcomment('columnname')
        data._isdataArray=True
        return data
    # add docstring from _read
    __new__.__doc__ += _read.__doc__

    def __array_finalize__(self,obj):
        """
        finalyze our dataArray to have attributes and updated parameters

        here we look in __dict__ if we have new dynamical created attributes
        and inherit them to  slices or whatever
        remember ndarray has no __dict__
        """
        if obj is None: return
        # copy the columnIndices from obj
        self.setColumnIndex(obj)
        if hasattr(obj,'__dict__'):
            for attribut in obj.attr+['_orgcommentline','_isdataArray']:
                try:
                    if attribut not in protectedNames:
                        self.__dict__[attribut]=getattr(obj,attribut)
                except:
                    pass


    def __array_wrap__(self, out_arr, context=None):
        x=np.ndarray.__array_wrap__(self, out_arr, context)
        return x

    @property
    def name(self):
        """
        Attribute name, mainly the filename of read data files.
        """
        return getattr(self,'@name')

    def setColumnIndex(self,ix='',iy='',iey='',iex='',iz='',iez=''):
        """
        Set the column index where to find X,Y,Z and and errors eY, eX, eZ.....

        A list of all X in the dataArray is dataArray.X
        For array.ndim=1 -> ix=0 and others=None as default.

        Parameters
        ----------
        ix,iy,iey,iex,iz,iez : integer, None, default 0,1,2,None....
            | Set column index, where to find X, Y, eY.
            | Default from initialisation is ix,iy,iey,iex,iz,iez=0,1,2,None,None,None.
            | Usability wins iey=2!!
            | If first ix is dataArray the ColumnIndex is copied, others are ignored.
            | If first ix is list [0,1,3] these are used as [ix,iy,iey,iex,iz,iez].

        Notes
        -----
        | integer  column index as 0,1,2,-1 , should be in range
        | None     as not used eg iex=None -> no errors for x
        | anything else does not change

        """
        if hasattr(ix,'_isdataArray'):
            # copy the ColumnIndex from objekt in ix
            ix,iy,iey,iex,iz,iez=(getattr(ix,pIN)  if hasattr(ix,pIN) else None for pIN in protectedIndicesNames)
        elif isinstance(ix,(tuple,list)):
            # if a list is given as argument
            ix, iy, iey, iex, iz, iez =(list(ix)+['']*6)[:6]
        if self.ndim==1:
            #in this case icol<self.shape[0]
            ix,iy,iz,iex,iey,iez=0,None,None,None,None,None
        for icol,name,icolname in zip([ix,iy,iey,iex,iz,iez],
                                      protectedNames,
                                      protectedIndicesNames):
            if isinstance(icol,int):
                if icol < self.shape[0]:  # accept only if within number of columns
                    setattr(self,icolname,icol)
                    gen_XYZ(self,name,icolname)
                else:
                    try:
                        delattr(self,name)
                    except:
                        pass
            elif icol is None:
                try:
                    delattr(self,name)
                except:
                    pass

    def __deepcopy__(self, memo):
        cls = self.__class__
        # deepcopy of the ndarray
        result = cls(copy.deepcopy(self.array, memo) )
        #add to memo
        memo[id(self)] = result
        # copy attributes .attr has only the correct attributes and no private stuff
        for k in self.attr+protectedIndicesNames :
            try:
                setattr(result, k, copy.deepcopy(getattr(self,k), memo))
            except:pass
        #copy ColumnIndex
        result.setColumnIndex(self)
        return result

    def nakedcopy(self):
        """
        Deepcopy without attributes, thus only the data.

        """
        cls = self.__class__
        return cls(copy.deepcopy(self.array))

    def __getattribute__(self,attribute):
        return np.ndarray.__getattribute__(self,attribute)

    def __getattr__(self,attribute):
        """x.__getattr__('name') <==> x.name
        if operator char like + - * / in attribute name
        use getattr(dataArray,'attribute') to get the value
        """
        #----for _access
        if attribute not in protectedNames+protectedIndicesNames+['_isdataArray']:
            if attribute[0] is '_' and hasattr(self,'columnname') :
                columnnames=_deletechars(self.columnname,'+-*/()[]()|§$%&#><°^, ').split(';')
                if attribute[1:] in columnnames:
                    return self[columnnames.index(attribute[1:])].view(np.ndarray)
        #----
        return np.ndarray.__getattribute__(self,attribute)

    def setattr(self,objekt,prepend='',keyadd='_'):
        """
        Set (copy) attributes from objekt.

        Parameters
        ----------
        object : objekt or dictionary
            can be a dictionary of names:value pairs like {'name':[1,2,3,7,9]}
            if object is dataArray the attributesfrom  dataArray.attr are copied
        prepend : string, default ''
            Prepend this string to all attribute names.
        keyadd : char, default='_'
            if reserved attributes (T, mean, ..) are found the name is 'T'+keyadd

        """
        if hasattr(objekt,'_isdataArray'):
            for attribut in objekt.attr:
                try:
                    setattr(self,prepend+attribut,getattr(objekt,attribut))
                except AttributeError:
                    self.comment.append('mapped '+attribut+' to '+attribut+keyadd)
                    setattr(self,prepend+attribut+keyadd,getattr(objekt,attribut))
        elif type(objekt)==type({}):
            for key in objekt:
                try:
                    setattr(self,prepend+key,objekt[key])
                except AttributeError:
                    self.comment.append('mapped '+key+' to '+key+keyadd)
                    setattr(self,prepend+key+keyadd,objekt[key])

    def __getitem__(self, idx):
        if isinstance(idx, str):
            columnnames=_deletechars(self.columnname,'+-*/()[]()|§$%&#><°^, ').split(';')
            if idx in columnnames:
                idx=columnnames.index(idx)
        return super(dataArrayBase, self).__getitem__(idx)

    @property
    def array(self):
        """
        Strip of all attributes and return a simple ndarray.
        """
        return self.view(np.ndarray)

    @inheritDocstringFrom(np.ndarray)
    def argmin(self, axis=None, out=None):
        return self.array.argmin(axis=axis,out=out)

    @inheritDocstringFrom(np.ndarray)
    def argmax(self, axis=None, out=None):
        return self.array.argmax(axis=axis,out=out)

    def prune(self,lower=None,upper=None,number=None,kind='lin',col='X',weight='eY',keep=None,type='mean'):
        """
        Reduce number of values between upper and lower limits by selection or averaging.

        Reduces dataset to data points in number intervals between lower and upper
        by selection or by averaging including errors (see type).
        Dependent on the distribution of original data a lower number of points can be the result.

        Parameters
        ----------
        lower : float
            Lower bound min is min of data
        upper : float
            Upper bound max is max of data
        number : int
            Number of points in [lower,upper] resulting in number intervalls.
        kind : {'log','lin'} default 'lin'
            | Kind of the new point distrubution.
            | 'log' closest values in log distribution with number points in [lower,upper]
            | 'lin' closest values in lin distribution with number points in [lower,upper]
            | If number==None all points are used.
        type : {None,'mean','error','mean+error'} default 'mean'
            | How to determine the value for a point.
            | None   next original value closest to column col value
            | 'mean' mean values in interval between 2 points;
            |        weight==None -> equal weight
            |        If weight!=None with weight=1/col[weight]**2.
            |        Weight column will get values according to error propagation.
            | 'mean+std' calcs mean and adds error columns as standard deviation in intervals (no weight)
            |        Can be used if no errors are present to generate errors as std in intervals.
            |        For single values the error is interpolated from neighbouring values.
            |        ! For less pruned data error may be bad defined if only a few points are averaged
        col : 'X','Y'....., or int, default 'X'
            Column to prune along X,Y,Z or index of column.
        weight : None,'eX', 'eY' or int
            | Column for weight as 1/err**2 in 'mean' calculation, None is equal weight
            | weight columne gets new error sqrt(1/sum_i(1/err_i**2))
            | If None or not existing equal weights are used.
        keep : list of int
            list of indices to keep in any case

        Returns
        -------
        dataArray with values pruned to number-1 values.

        Examples
        --------
        ::

         self.prune(number=13,col='X',type='mean+',weight='eY')
         or
         self.prune(lower=0.1,number=13)

        Notes
        -----
        Attention !!!!
         Dependent on the distribution of original data a lower number of points can be the result
         eg think of noisy data between 4 and 5 and a lin distribution from 1 to 10 of 9 points
         as there are no data between 5 and 10 these will all result in 5 and be set to 5 to be unique.

        """
        #values to keep
        if keep is not None:
            keep=np.array([i in keep for i in range(len(self.X)) ],dtype=bool)
            temp=self[:,~keep].array
            keep=self[:,keep].array
        else:
            temp=self.array
        if number is not None and kind== 'all':
            kind='lin'
        if col in protectedNames:
            col=getattr(self,'_i'+col.lower())
        val=temp[int(col)]
        try:
            if   weight=='X': weight=self._ix
            elif weight=='Y': weight=self._iy
            elif weight=='Z': weight=self._iz
            elif weight=='eX':weight=self._iex
            elif weight=='eY':weight=self._iey
            elif weight=='eZ':weight=self._iez
            wval=1./temp[int(weight)]**2
        except:
            weight=None
            # then no weights err=1 as equal weight
            wval=np.ones_like(temp[int(col)])
        # determine min and max from values and use only these
        valmin=np.max([np.min(val),lower]) if lower is not None else np.min(val)
        valmax=np.min([np.max(val),upper]) if upper is not None else np.max(val)
        temp=temp[:,(val>=valmin) & (val<=valmax)]
        wval=wval[(val>=valmin) & (val<=valmax)]
        val=temp[int(col)]

        if number is None:
            # only keep, upper and lower important
            if keep is not None:
                temp=np.c_[keep,temp]
            temp=dataArray(temp)
            temp.setattr(self)
            temp.setColumnIndex(self)
            return temp
        elif kind[:3]=='log':
            # log distributed points
            pruneval=loglist(valmin,valmax,number+1)
        else:
            #lin distibuted points as default
            pruneval=np.r_[valmin:valmax:(number+1)*1j]
        if type[:4]=='mean':
            # out is one smaller than selected as we look at the intervals
            out=temp[:,:number]
            nn=self.shape[0]
            if type!='mean':
                out=np.r_[out,out*0]
            nonempty=np.ones(number,dtype=bool) # non empty intervals
            for i,low,upp in zip(range(number),pruneval[:-1],pruneval[1:]):
                #weighted average
                if i<number-1:
                    select=(low<=val) & (val<upp)
                else:
                    select=(low<=val) & (val<=upp)
                if not select.any():
                    nonempty[i]=False
                    continue
                out[:nn,i]=(temp[:,select]*wval[select]).sum(axis=1)/wval[select].sum()
                #error from errorpropagation for weight
                wv=wval[select]
                if weight is not None and len(wv)>1:
                    out[weight,i]=np.sqrt(1/(wv.sum()*(len(wv)-1)))
                if type!='mean':
                    # is more than 'mean' => error need to be calculated with weight and attached
                    if len(wv)>1:
                        out[nn:,i]=temp[:nn,select].std(axis=1)
            out=out[:,nonempty] # removes empty intervals
            if keep is not None:
                out=np.c_[keep,out]
            temp=dataArray(out)
            temp.setattr(self)
            temp.setColumnIndex(self)
            #find indices of error=0 which could make trouble. These come from non average as it was single number
            if type!='mean':
                #  interpolate from neighbours to get an error estimate
                # keep values might get the error of the border
                bzeros=(temp[nn,:]==0)
                for inn in range(nn,len(temp)):
                    temp[inn,bzeros]=np.interp(temp.X[bzeros],temp[col,~bzeros],temp[inn,~bzeros])
                #set attributes that errors can be found
                temp.setColumnIndex(iex=(getattr(self,'_ix')+nn if (hasattr(self,'X') and not hasattr(self,'eX')) else ''),
                                    iey=(getattr(self,'_iy')+nn if (hasattr(self,'Y') and not hasattr(self,'eY')) else ''),
                                    iez=(getattr(self,'_iz')+nn if (hasattr(self,'Z') and not hasattr(self,'eZ')) else ''))
            return temp

    def interpolate(self,X,left=None, right=None,deg=1):
        """
        Piecewise interpolated values of Y at position X=X returning dataArray.

        Parameters
        ----------
        X : array,float
             values to interpolate
        left : float
            Value to return for `X < X[0]`, default is `Y[0]`.
        right : float
            Value to return for `X > X[-1]`, defaults is `Y[-1]`.
        deg : integer, default =1
            Polynom degree for interpolation along attribute.
            For deg=1 values outside the data range are substituted by nearest value (see np.interp)
            For deg>1 a spline extrapolation scipy.interpolate.interp1d is used. Outliers result in Nan.

        Returns
        -------
            dataArray

        Notes
        -----
        | see numpy.interp
        | sorts automatically along X

        """
        if X is None:
            return self
        X=np.atleast_1d(X)
        xsort=self.X.argsort()
        if deg==1:
            # outliers are neareest in np.interp
            return dataArray(np.c_[X,np.interp(X,self.X[xsort],self.Y[xsort],left=left, right=right)].T )
        else:
            # outliers are handled above scipy 0.17.1 ; this will change later
            return dataArray(np.c_[X,scipy.interpolate.interp1d(self.X[xsort],self.Y[xsort],kind=deg)(X)].T )

    def interp(self,X,left=None, right=None):
        """
        Piecewise linear interpolated values of Y at position X returning only Y (faster).

        Parameters
        ----------
        X : array,float
             values to interpolate
        left : float
            Value to return for `X < X[0]`, default is `Y[0]`.
        right : float
            Value to return for `X > X[-1]`, defaults is `Y[-1]`

        Returns
        -------
            array

        Notes
        -----
        | see numpy.interp
        | sorts automatically along X

        """
        if X is None:
            return self.Y.array
        X=np.atleast_1d(X)
        xsort=self.X.argsort()
        return np.interp(X,self.X[xsort],self.Y[xsort],left=left, right=right)

    def interpAll(self,X=None,left=None,right=None):
        """
        Piecewise linear interpolated values of all columns  at new X values.

        Parameters
        ----------
        X : array like
             values where to interpolate
        left : float
            Value to return for `X < X[0]`, default is `Y[0]`.
        right : float
            Value to return for `X > X[-1]`, defaults is `Y[-1]`.

        Returns
        -------
            dataArray, here with X,Y,Z preserved and all attributes

        Notes
        -----
        | see numpy.interp
        | sorts automatically along X

        """
        if X is None:
            X=self.X
        X=np.atleast_1d(X)
        newself=zeros((self.shape[0],np.shape(X)[0]))
        xsort=self.X.argsort()
        columns=range(self.shape[0])
        columns.pop(self._ix)
        newself[self._ix]=X
        for i in columns:
            newself[i]=np.interp(X,self.X[xsort],self[i][xsort],left=left, right=right)
        newself.setattr(self)
        newself.setColumnIndex(self)
        return newself

    def polyfit(self,X=None,deg=1,function=None,efunction=None):
        """
        Interpolated values for Y at values X using a polyfit.

        Extrapolation is done by using a polynominal fit over all Y with weights eY only if eY is present.
        To get the correct result the output needs to be evaluated by the inverse of function.

        Parameters
        ----------
        X : arraylike
            X values where to calculate Y
            If None then X=self.X e.g. for smoothing/extrapolation.
        deg : int
            degree of polynom used for interpolation see numpy.polyfit
        function : function or lambda
            Used prior to polyfit as polyfit( function(Y) )
        efunction : function or lambda
            Used prior to polyfit for eY as weigths = efunction(eY)
            efunction should be build according to error propagation.

        Returns
        -------
            dataArray

        Notes
        -----
        Remember to reverse the function.!!!!!!!!!!

        """
        if X is None:
            X=self.X
        X=np.atleast_1d(X)
        if function is None:
            function=lambda y:y
            efunction=None
        if efunction is None:
            efunction=lambda ey:ey
        if hasattr(self,'eY'):
            poly=np.polyfit(x=self.X,y=function(self.Y),deg=deg,w=efunction(self.eY))
        else:
            poly=np.polyfit(self.X,function(self.Y),deg)
        return dataArray(np.c_[X,np.poly1d(poly)(X)].T )

    # use the fit routines from dataList to be used in dataArray
    def fit(self,model,freepar={},fixpar={},mapNames={},xslice=slice(None),condition=None,output=True,**kw):
        """
        Least square fit to model that minimizes chi**2 (uses scipy.optimize).

        See :py:meth:`dataList.fit`, but only first parameter is used if more than one given.

        """
        if not hasattr(self,'_asdataList'):
            self._asdataList=dataList(self)
        free={}
        fix={}
        # use only first value if a list is given
        for key, value in freepar.items():free[key]=(value if isinstance(value,(int,float)) else value[0])
        for key, value in fixpar.items() : fix[key]=(value if isinstance(value,(int,float)) else value[0])
        if 'debug' in kw:
            return self._asdataList.fit(model=model,freepar=free,fixpar=fix,mapNames=mapNames,xslice=xslice,condition=condition,output=output,**kw)
        self._asdataList.fit(model=model,freepar=free,fixpar=fix,mapNames=mapNames,xslice=xslice,condition=condition,output=output,**kw)
        self.lastfit=self._asdataList.lastfit[0]
        for attr in self._asdataList.lastfit.__dict__:
            if attr[0] != '_':
                temp=getattr(self._asdataList.lastfit,attr)
                if attr in free:
                    # is first element in a atlist
                    setattr(self.lastfit,attr,temp[0])
                    setattr(self,attr,temp[0])
                elif '_err' in attr and attr[:-4] in free:
                    setattr(self.lastfit, attr, temp[0])
                    setattr(self, attr, temp[0])
                elif attr in mapNames:
                    setattr(self.lastfit,attr,temp[0])
                elif attr in fix:
                    setattr(self.lastfit, attr, fix[attr])
                else:
                    setattr(self.lastfit,attr,temp)
        return

    @inheritDocstringFrom(dataList)
    def setlimit(self,*args,**kwargs):
        """
        Set upper and lower limits for parameters in least square fit.

        See :py:meth:`dataList.setlimit`

        """
        if not hasattr(self,'_asdataList'):
            self._asdataList=dataList(self)
        self._asdataList.setlimit(*args,**kwargs)

    @property
    @inheritDocstringFrom(dataList)
    def has_limit(self):
        """
        Return existing limits.

        See :py:meth:`dataList.has_limit`

        """
        return self._asdataList.has_limit

    @inheritDocstringFrom(dataList)
    def modelValues(self,*args,**kwargs):
        """
        Calculates modelValues of model after a fit

        See :py:meth:`dataList.modelValues`

        """
        if not hasattr(self,'_asdataList'):
            print(  'first do a fit!!')
        else:
            return self._asdataList.modelValues(*args,**kwargs)[0]

    def extract_comm(self,iname=0,deletechars='',replace={}):
        """
        Extracts not obvious attributes from comment and adds them to attributes.

        The iname_th word is selected as attribute and all numbers are taken.

        Parameters
        ----------
        deletechars : string
            chars to delete
        replace : dictionary of strings
            strings to replace {',':'.','as':'xx','r':'3.14',...}
        iname : integer
            which string to use as attr name; in example 3 for 'wavelength'

        Notes
        -----
        example :   w [nm] 632 +- 2,5 wavelength
        extract_comm(iname=3,replace={',':'.'})
        result .wavelength=[632, 2.5]

        """
        if isinstance(self.comment,str):
            self.comment= [self.comment]
        for line in self.comment:
            words=_deletechars(line,deletechars)
            for old,new in replace.items():
                words=words.replace(old,new)
            words=[_w2f(word) for word in words.split()]
            numbers=[word for word in words if type(word) in (float,int)]
            nonumber=[word for word in words if type(word) not in (float,int)]
            self.setattr({nonumber[iname]:numbers})

    def getfromcomment(self,attrname):
        """
        Extract a non number parameter from comment with attrname in front

        If multiple names start with parname first one is used.
        Used comment line is deleted from comments.

        Parameters
        ----------
        attrname : string
            name of the parameter in first place

        """
        for i,line in enumerate(self.comment):
            words=line.split()
            if len(words)>0 and words[0]==attrname:
                setattr(self,attrname,' '.join(words[1:]))
                del self.comment[i]
                return

    @property
    def attr(self):
        """
        Show data specific attribute names as sorted list of attribute names.

        """
        if hasattr(self,'__dict__'):
            attrlist=filter(lambda key:key[0]!='_' and
                                       key not in protectedNames + ['raw_data'], self.__dict__)
            return sorted(attrlist)
        else:
            return []

    def showattr(self,maxlength=None,exclude=['comment']):
        """
        Show data specific attributes with values as overview.

        Parameters
        ----------
        maxlength : int
            truncate string representation after maxlength char
        exclude : list of str
            list of attr names to exclude from result

        """
        for attr in self.attr:
            if attr not in exclude:
                #print(  '%25s = %s' %(attr,str(getattr(self,attr))[:maxlength]))
                values=getattr(self,attr)
                try:
                    valstr=shortprint( (values).split('\n'))
                    print(  '{:>24} = {:}'.format(attr, valstr[0]))
                    for vstr in valstr[1:]:
                        print(  '{:>25}  {:}'.format('', vstr))
                except:
                    print(  '%24s = %s' %(attr,str(values)[:maxlength]))

    def resumeAttrTxt(self,names=None,maxlength=None):
        """
        Resume attributes in text form.

        A list with the first element of each attr is converted to string.

        Parameters
        ----------
        names : iteratable
            names in attributes to use
        maxlength : integer
            max length of string

        Returns
        -------
        string

        """
        if names is None:
            names=self.attr
        ll=[]
        for name in names:
            if name=='comment' and len(getattr(self,name))>0:
                #only the first one in short
                ll.append(name+'='+_deletechars(getattr(self,name)[0],' ,.#*+-_"?§$%&/()=')[:10])
            else:
                par=getattr(self,name)
                try:
                    #only first element
                    ll.insert(0,'%s=%.3g' %(name,np.array(par).ravel()[0]))
                except:
                    pass
        text=' '.join(ll)
        return text[:min(len(text),maxlength)]

    def savetxt(self, name, fmt='%8.5e'):
        """
        Saves data in ASCII text file (optional gzipped).

        If name extension is '.gz' the file is compressed (gzip).

        Parameters
        ----------
        name : string, StrinIO
            Filename to write to or io.BytesIO.
        fmt : string
            Format specifier for float.

        Notes
        -----
        | format rules
        | datasets are separated by empty lines, parameters or comments

        | dataset consists of data table with optional parameters and comments
        | first two strings decide for a line
        | string + value     -> parameter as parametername + list of values
        | string + string    -> comment line
        | value  + value     -> data   (line of an array; in sequence without break)
        | single words       -> are appended to comments
        |
        | optional:
        | 1string+@string->  as parameter but links to other dataArray with name @string
        | (content of parameter with name 1string) stored in the same
        | file after this dataset identified by parameter @name=1string

        | internal parameters starting with underscore ('_') are ignored for writing, also X,Y,Z,eX,eY,eZ,
        | only ndarray content is stored; no dictionaries in parameters
        | @name is used as identifier or filename can be accessed as name

        | passed to savetext with example for ndarray part:
        | fmt : str or sequence of strs
        | A single format (%10.5f), a sequence of formats, or a
        | multi-format string, e.g. 'Iteration %d -- %10.5f', in which
        | case `delimiter` is ignored.

        """
        if hasattr(name,'writelines'):
            # write to IOstring
            file.writelines( _maketxt(self, name=name,fmt=fmt))
            return
        if os.path.splitext(name)[-1] == '.gz':
            _open = gzip.open
        else:  # normal file
            _open = open
        with _open(name,'wb') as f:
            f.writelines( _maketxt(self, name=name,fmt=fmt))
        return

    savetext=savetxt
    save=savetxt

    def __repr__(self):
        attr=self.attr[:6]
        try:
            attr.remove('comment')
        except:pass
        try:
            if isinstance(self.comment, list):
                comment=self.comment[:2]
            else:
                comment=[self.comment]
        except:
            comment=[]
        desc="""dataArray->(X,Y,....=\n%(data)s,
comment=%(comment)s)...,
attributes=%(attr)s ....,
shape=%(shape)s    """
        return desc % {'data': shortprint(self,49,3)+'.........',
                       'comment':[a[:70] for a in comment],
                       'attr':attr ,
                       'shape':np.shape(self)}

    @inheritDocstringFrom(np)
    def concatenate(self,others,axis=1,isort=None):
        """
        Concatenates the dataArray[s] others to self !!NOT IN PLACE

        and add all attributes from others

        Parameters
        ----------
        others : dataArray or dataList
            dataArray or list of dataArrays with same shape as self
        axis : integer
            axis along to concatenate  see numpy.concatenate
        isort : integer
            sort array along column isort =i

        Returns
        -------
        dataArray with merged attributes and isorted

        """
        if not isinstance(others,list):
            others=[others]
        data= dataArray(np.concatenate([self]+others,axis=axis))
        # copy attributes
        for one in [self]+others:
            for attribut in one.attr:
                if not hasattr(data,attribut):
                    data.__dict__[attribut]=[getattr(two,attribut) for two in [self]+others if hasattr(one,attribut)]
        if isort is not None:
            data.isort(col=isort)
        return data

    def addZeroColumns(self,n=1):
        """
        Copy with n new zero columns at the end !!NOT in place!!

        Parameters
        ----------
        n : int
            number of columns to append

        """
        newdA=dataArray(np.vstack((self,np.zeros((n,self.X.shape[0])))))
        newdA.setattr(self)
        newdA.setColumnIndex(self)
        return newdA

    def addColumn(self,n=1,values=0):
        """
        Copy with new columns at the end populated by values !!NOT in place!!

        Parameters
        ----------
        n : int
            number of columns to append
        values : float, list of float
            values to append in columns
            appended as [-n:]=values

        """
        newdA=self.addZeroColumns(n) # copy self with new columns
        newdA[-n:]=values
        newdA.setattr(self)
        newdA.setColumnIndex(self)
        return newdA

    def merge(self,others,axis=1,isort=None):
        """
        Merges dataArrays to self  !!NOT in place!!

        Parameters
        ----------
        axis : integer
            axis along to concatenate  see numpy.concatenate
        isort : integer
            sort array along column isort =i

        """
        return self.concatenate(others,axis,isort)

    def isort(self,col='X'):
        """
        Sort along a column  !!in place

        Parameters
        ----------
        col : 'X','Y','Z','eX','eY','eZ' or 0,1,2,...
            column to sort along

        """
        if col in protectedNames:
            col=getattr(self,'_i'+col.lower())
        self[:,:]=self[:,self[col].argsort()]

    def where(self,condition):
        """
        Copy with lines where condition is fulfilled.

        Parameters
        ----------
        condition : function
            function returning bool

        Examples
        --------
        ::

         data.where(lambda a:a.X>1)
         data.where(lambda a:(a.X**2>1) & (a.Y>0.05)  )

        """
        return self[:,condition(self)]

    @inheritDocstringFrom(dataListBase)
    def makeErrPlot(self,*args,**kwargs):
        pass

    @inheritDocstringFrom(dataListBase)
    def makeNewErrPlot(self,*args,**kwargs):
        pass

    @inheritDocstringFrom(dataListBase)
    def detachErrPlot(self,*args,**kwargs):
        pass

    @inheritDocstringFrom(dataListBase)
    def errPlot(self,*args,**kwargs):
        pass

    @inheritDocstringFrom(dataListBase)
    def savelastErrPlot(self,*args,**kwargs):
        pass

    @inheritDocstringFrom(dataListBase)
    def showlastErrPlot(self, *args, **kwargs):
        pass

    @inheritDocstringFrom(dataListBase)
    def killErrPlot(self,*args,**kwargs):
        pass

    @inheritDocstringFrom(dataListBase)
    def errPlottitle(self,*args,**kwargs):
        pass

# dataArray inlcuding errPlot functions

class dataArray(dataArrayBase):

    @inheritDocstringFrom(dataList)
    def makeErrPlot(self,*args,**kwargs):
        if not hasattr(self,'_asdataList'):
            self._asdataList=dataList(self)
        self._asdataList.makeErrPlot(*args,**kwargs)

    @inheritDocstringFrom(dataList)
    def makeNewErrPlot(self,*args,**kwargs):
        if not hasattr(self,'_asdataList'):
            self._asdataList=dataList(self)
        self._asdataList.makeNewErrPlot(*args,**kwargs)

    @inheritDocstringFrom(dataList)
    def detachErrPlot(self,*args,**kwargs):
        if not hasattr(self,'_asdataList'):
            self._asdataList=dataList(self)
        self._asdataList.detachErrPlot(*args,**kwargs)

    @inheritDocstringFrom(dataList)
    def errPlot(self,*args,**kwargs):
        if not hasattr(self,'_asdataList'):
            self._asdataList=dataList(self)
        self._asdataList.errPlot(*args,**kwargs)

    @inheritDocstringFrom(dataList)
    def savelastErrPlot(self,*args,**kwargs):
        if not hasattr(self,'_asdataList'):
            self._asdataList=dataList(self)
        self._asdataList.savelastErrPlot(*args,**kwargs)

    @inheritDocstringFrom(dataList)
    def showlastErrPlot(self, *args, **kwargs):
        if not hasattr(self,'_asdataList'):
            print(  'first do a fit!!')
        else:
            self._asdataList.showlastErrPlot(*args,**kwargs)

    @inheritDocstringFrom(dataList)
    def killErrPlot(self,*args,**kwargs):
        if not hasattr(self,'_asdataList'):
            print(  'first do a fit!!')
        else:
            self._asdataList.killErrPlot(*args,**kwargs)
    def errPlotTitle(self,*args,**kwargs):
        if not hasattr(self,'_asdataList'):
            print(  'first do a fit!!')
        else:
            self._asdataList.errPlotTitle(*args,**kwargs)

#############end dataArray main definitions###############################################

def zeros(*args,**kwargs):
    """
    dataArray filled with zeros.

    Parameters
    ----------
    shape : integer or tuple of integer
        Shape of the new array, e.g., (2, 3) or 2.

    Returns
    -------
        dataArray

    Examples
    --------
    ::

     js.zeros((3,20))

    """
    zero=np.zeros(*args,**kwargs)
    return dataArray(zero)

def ones(*args,**kwargs):
    """
    dataArray filled with ones.

    Parameters
    ----------
    shape : integer or tuple of integer
        Shape of the new array, e.g., (2, 3) or 2.

    Returns
    -------
        dataArray

    Examples
    --------
    ::

     js.ones((3,20))

    """
    one=np.ones(*args,**kwargs)
    return dataArray(one)

def fromFunction(function,X,*args,**kwargs):
    """
    evaluation of Y=function for all X and returns a dataArray with X,Y
    
    Parameters
    ----------
    function : function or lambda 
        function to evaluate with first argument as X[i]
        result is flattened (to be one dimensional)
    X : array N x M
        X array
        function is evaluated along first dimension (N)
        e.g np.linspace or np.logspace
    *args,**kwargs : arguments passed to function

    Returns
    -------
    dataArray with N x ndim(X)+ndim(function(X))
    
    Examples
    --------
    ::

     import jscatter as js
     result=js.fromFunction(lambda x,n:[1,x,x**(2*n),x**(3*n)],np.linspace(1,50),2)
     #
     X=(np.linspace(0,30).repeat(3).reshape(-1,3)*np.r_[1,2,3])
     result=js.fromFunction(lambda x:[1,x[0],x[1]**2,x[2]**3],X)
     #
     ff=lambda x,n,m:[1,x[0],x[1]**(2*n),x[2]**(3*m)]
     X=(np.linspace(0,30).repeat(3).reshape(-1,3)*np.r_[1,2,3])
     result1=js.fromFunction(ff,X,3,2)
     result2=js.fromFunction(ff,X,m=3,n=2)
     result1.showattr()
     result2.showattr()
        
    """
    res=[np.r_[x,np.asarray(function(x,*args,**kwargs)).flatten()] for x in X]
    result=dataArray(np.asarray(res).T)
    result.setColumnIndex(0,len(np.atleast_1d(X[0])))
    result.args=args
    for key in kwargs:
        setattr(result,key,kwargs[key])            
    if hasattr(function,'func_name'):
        result.function=str(function.func_name)
    elif hasattr(function,'__name__'):
        result.function=str(function.__name__)
    return result


# create two shortcuts
dL=dataList
dA=dataArray

# this generates the same interface for grace as in mplot
# unfortunatly both use the same names with small char at beginning
from .graceplot import GraceIsInstalled
if GraceIsInstalled:
    from .graceplot import GracePlot as openplot
    from .graceplot import GraceGraph
    openplot.Clear=openplot.clear
    openplot.Exit=openplot.exit
    openplot.Save=openplot.save
    openplot.Multi=openplot.multi
    GraceGraph.Plot=GraceGraph.plot
    GraceGraph.Title=GraceGraph.title
    GraceGraph.Subtitle=GraceGraph.subtitle
    GraceGraph.Yaxis=GraceGraph.yaxis
    GraceGraph.Xaxis=GraceGraph.xaxis
    GraceGraph.Clear=GraceGraph.clear
    GraceGraph.Legend=GraceGraph.legend

else:
    try:
        from . import mpl
        mpl.gf=20
        openplot=mpl.mplot
        print(  'use mpl')
    except:
        # use the base classes with errPlot only as dummy functions
        dataList=dataListBase
        dataArray=dataArrayBase
        print(  'No plot interface found')










