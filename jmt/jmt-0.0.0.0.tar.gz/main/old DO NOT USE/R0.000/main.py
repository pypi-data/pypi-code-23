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
    if not pathsFound: pathsFound=[]
    if type(searchPath)==type([]):
        #allow user to search multiple directories with searchPath as list
        for i in searchPath: 
            pathsFound+=searchForFolder(i,folderName,deep,contains,None)
        pathsFound=list(set(pathsFound))#remove duplicates
        pathsFound.sort()#sort in alphabetical order
        return pathsFound
    elif os.path.exists(searchPath)==False:
        print('warning: searchPath '+searchPath+' does not exist')
        return []
    if os.path.basename(folderName)!='':
        folderName=os.path.basename(folderName)
    #print(searchPath)
    try:
        subFolders=next(os.walk(searchPath))[1]
    except: 
        print("warning: could not search path " +searchPath)
        return []
    if searchPath[-1]!="\\":
        prefix = searchPath+"\\"
    else: prefix=searchPath
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
    if type(searchPath)==type([]):
        #allow user to search multiple directories with searchPath as list
        filesFound=[]
        for i in searchPath: 
            filesFound+=searchForFile(i,fileName,deep,contains,filesFound)
        filesFound=list(set(filesFound))#remove duplicates
        filesFound.sort()#sort in alphabetical order
        return filesFound
    elif os.path.exists(searchPath)==False:
        print('warning: searchPath '+searchPath+' does not exist')
        return []
    if not filesFound: filesFound=[]
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

def getpythonfolder():
    '''finds python directory
    by searching through program files (x86) then program files
    '''
    import os
    env=dict(os.environ)#entire list of main directories
    #get all folders in dict with keys containing 'PROGRAMFILE' and '86'
    prgmfl = [value for key, value in env.items() if ('PROGRAMFILE' in key and 
              '86' in key)]
    if prgmfl==[]:#if program files (x86) doesn't exist, use program files
        prgmfl = [value for key, value in env.items() if ('PROGRAMFILE' in key)]
    prgmfl = os.path.commonpath(prgmfl)#common path=program file (x86)
    findpy=next(os.walk(prgmfl))[1]#generate list of immediate subdirectories
    #search for folder containing 'python'
    pyfolder=[val for val in findpy if 'python' in val.lower()]
    #if no folder exists then try program files (not x86)
    if pyfolder==[]:
        prgmfl=[value for key, value in env.items() if ('PROGRAMFILE' in 
                key and '86' not in key)]
        if prgmfl==[]:#no program files folder, failed to find python folder
            print("python folder not found")
            return ''
        else:#programs folder found
            prgmfl = os.path.commonpath(prgmfl)#get common path (program files)
        findpy=next(os.walk(prgmfl))[1]#get sub directories
        #search 'python' again
        pyfolder=[val for val in findpy if 'python' in val.lower()]
    if pyfolder==[]:#still can't find python folder
        print("python folder not found in either Progam Files folders")
        return ''
    pyfolder=pyfolder[0]#use first folder found (should only be one anyway)
    pydir=prgmfl+"\\"+pyfolder
    return pydir

def getpythonfolder2():
    '''find python directory by searching typical installation folder locations
    '''
    import os
    env=os.environ
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
    return pyfolder[0]