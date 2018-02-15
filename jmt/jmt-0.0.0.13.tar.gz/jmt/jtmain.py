"""
Created on Sun Jan 28 13:18:57 2018

@author: jaredmt

@description: any general function of no category goes here
"""

def isimported(module_name):
    '''this might be my way of cleaning up imports that are not needed
    note: this function is probably not needed. my understanding is that
    python only imports each module once unless you use reload'''
    import sys
    if module_name in sys.modules:
        return True
    else:
        return False

def ceil(a):
    'rounds up'
    if (a==int(a)):
        return int(a)
    else:
        return int(a+1)
    
def num2frac(a):
    '''returns estimated fraction as string
    example: num2frac(.13131313)
    13/99'''
    from fractions import Fraction

    return str(Fraction(a).limit_denominator())

def str2func(str1,*args):
    '''args = all user inputs
    example:
        strtofunc('mxnlist',2,3)#output [[[], [], []], [[], [], []]]
    '''
    return globals()[str1](*args)
'''similar to str2func is built-in eval function:
    eval("5+2",globals())#output 7
    x=2
    eval("5+x",globals())#output 7
    eval("num2frac(5/8)",globals())#output '5/8'
    note that THIS IS A SECURITY RISK since the user has ability
    to do anything including importing os/sys to mess up the computer
    the way around it is to change the string around first rather than
    input direct to eval. i.e. eval(int(input()))
    other similiar functions are locals(),exec,compile
    
    security ideas:
        -don't allow string inputs that include: import,__,eval,exec,compile,etc
        -find which module the function is from and don't allow os,sys,etc
    
    '''
def checkEval(str1):
    'checks string for potentially malicious inputs for eval function'
    str1=str(str1)
    excludes = ['import','__','os','sys','eval','exec','compile','open','write','\n','\t']
    for i in range(len(excludes)):
        if excludes[i] in str1:
            return False
    return True

def error(msg):
    'raises an Exception with the msg string as output'
    raise Exception("jt error: "+str(msg))
    
'''================read/write files==============='''
'''
filename="readwritethisfile.txt"
fr=open(filename,"r")
fcurrent = fr.read()#current text file
fw=open(filename,"w")
fw.write(fcurrent+"\nhere is new text")
fa=open(filename,"a")#append text in file
fa.write("this text will be at the end")

fr.close()
fw.close()
fa.close()
'''

'''==============website functions================'''
'''
get HTML from a website:
from requests import get
f=get("http://www.bbc.com/news/world-asia-42435798")
urltext = f.text#actual website text
'''

'''=============kivy (cross-platform including android)=============='''
'''
kivy has its own language (.kv files) but you can import .py files and run those
sentdex youtube channel shows how to make buttons,text,textbox, draw,
navigate different windows, import .py files
maybe kivy can be used to make a general python calculator which includes sympy
numpy and many other python core items. it could be the android version of
ti-89

'''

def searchForFolder(searchPath,folderName,deep=float('inf'),
                    contains=True,pathsFound=None):
    '''looks within searchPath and subfolders to find folderName
    this will search all subfolders and list all folders with folderName
    if contains is true then it will search any foldername that contains
    folderName
    deep=how many folders deep to search
    example
    searchForFolder(path,"R0")#returns folders and subfolders containing R0
    searchForFolder(path,"R0",1)#only returns immediate subfolders containing R0
    searchForFolder(path,"R1",contains=False)#only returns exact match for R1
    '''
    import os
    #cannot use [] as default because .append will save the list
    if not pathsFound: pathsFound=[]
    
    #allow user to search multiple directories with searchPath as list
    if type(searchPath)==type([]):
        for i in searchPath: 
            pathsFound+=searchForFolder(i,folderName,deep,contains,pathsFound)
        pathsFound=list(set(pathsFound))#remove duplicates
        pathsFound.sort()#sort in alphabetical order
        return pathsFound
    elif os.path.exists(searchPath)==False:
        #if path doesn't exist, don't bother searching it
        print('warning: searchPath '+searchPath+' does not exist')
        return []
    
    #allow user to search multiple key words:
    if type(folderName)==type([]):
        for fn in folderName:
            pathsFound+=searchForFolder(searchPath,fn,deep,contains,pathsFound)
        pathsFound=list(set(pathsFound))#remove duplicates
        pathsFound.sort()#sort in alphabetical order
        
        return pathsFound
    
    #shorten folderName. only need folder name, not full path
    if os.path.basename(folderName)!='':
        folderName=os.path.basename(folderName)
    #attempt to get list of subfolders:
    try:
        subFolders=next(os.walk(searchPath))[1]
    except: 
        #sometimes it recognizes folders that don't appear to be there
        #i'm not sure how to fix this
        print("warning: could not search path " +searchPath)
        return []
    #prefix must end with \. some paths such as C:\ folder already have \
    if searchPath[-1]!="\\":
        prefix = searchPath+"\\"
    else: prefix=searchPath
    
    #now find the search paths
    if subFolders!=[] and deep>0:
        if contains:#return all resutls containing folderName
            for n in subFolders:
                if folderName.lower() in n.lower(): pathsFound.append(prefix+n)
        elif folderName in subFolders:#only get exact match
            pathsFound.append(prefix+folderName)
        #now search subfolders:
        for v in subFolders: 
            pathsFound=searchForFolder(prefix+v,folderName,deep-1,contains,pathsFound)
    return pathsFound



def searchForFile(searchPath,fileName,deep=float('inf'),
                  contains=True,filesFound=None):
    '''
    this function searches thru searchPath to find fileName
    contains=False#this will search exact name
    deep=how many folders deep to search
    example
    searchForFile(path,"R0")#returns files containing R0 from all subfolders
    searchForFile(path,"R0",1)#only returns files containing R0 from path
    searchForFile(path,"R1",contains=False)#only returns exact match for R1
    '''
    import os
    if not filesFound: filesFound=[]
    
    if type(searchPath)==type([]):
        #allow user to search multiple directories with searchPath as list
        for i in searchPath: 
            filesFound+=searchForFile(i,fileName,deep,contains,filesFound)
        filesFound=list(set(filesFound))#remove duplicates
        filesFound.sort()#sort in alphabetical order
        return filesFound
    elif os.path.exists(searchPath)==False:
        print('warning: searchPath '+searchPath+' does not exist')
        return []
    
    #allow user to search multiple filenames:
    if type(fileName)==type([]):
        for fN in fileName:
            filesFound+=searchForFile(searchPath,fN,deep,contains,filesFound)
        filesFound=list(set(filesFound))
        filesFound.sort()
        return filesFound
    
    
    if os.path.basename(fileName)!='':
        fileName=os.path.basename(fileName)
    try:
        subFolders,files=next(os.walk(searchPath))[1:]
    except:
        print('warning: could not search '+searchPath)
        return []
    prefix=searchPath+"\\"
    if contains:#return all results containing fileName
        for n in files:
            #print(n)
            if fileName.lower() in n.lower(): filesFound.append(prefix+n)
    elif fileName in files:
        filesFound.append(prefix+fileName)
    if subFolders!=[] and deep>0:
        #now search subfolders:
        for v in subFolders:
            filesFound=searchForFile(prefix+v,fileName,deep-1,contains,filesFound)
    return filesFound

def getpythonfolder(debugmode=False):
    '''find python directory by searching typical installation folder locations
    '''
    import os
    import sys
    debugon=sys.stdout
    debugoff=open(os.devnull,'w')
    if debugmode==False: sys.stdout=debugoff
    env=os.environ
    
    #first attempt to find python folder using PATH:
    p=env['PATH'].split(";")
    py=[v for v in p if 'python' in v.lower()]
    try: py=os.path.commonpath(py)
    except: print("failed to get common path")
    if py!=[] and type(py)==type("") and 'python' in py.lower():
        return py
    
    #if PATH didn't work, then search in common directories:
    prgmfl=[val for key, val in env.items() if ('PROGRAMFILES' in key and
            'COMMON' not in key)]
    homedrive = [env['HOMEDRIVE']+"\\"]
    systemdrive=[env['SYSTEMDRIVE']+"\\"]
    #add all to list and remove duplicates
    allsearchpaths=list(set(prgmfl+homedrive+systemdrive))
    allsearchpaths.sort()#search in alphabetical order (easier for debugging)
    pyfolder=searchForFolder(allsearchpaths,'python',1)
    
    #put preference on which folder:
    #for now just returning first result
    sys.stdout=debugon#turn printing back on
    return pyfolder[0]


def createPath(path):
    '''creates full path if it doesn't exist.'''
    import os
    path=path.replace("/","\\")
    if path[-1]=="\\": path=path[:-1]
    if os.path.isdir(path):
        print("path exists")
        return
    basename=os.path.basename(path)
    if basename=='':
        print("cannot create path. drive doesn't exist")
        return
    p=os.path.dirname(path)#parent folder
    #print("parent: "+p)
    if os.path.isdir(p)==False:
        createPath(p)
        #print("created path")
    try: os.mkdir(path)
    except: print("couldn't make: "+path)