# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 13:25:32 2018

@author: jaredmt
"""


'''=========imports========='''
from .jtmain import getpythonfolder
import __main__
from .jtstring import strfind




'''****global variables*****'''

excludes_list=['fractions','numpy','openpyxl','requests','pandas','sympy',
               'matplotlib','tkinter','pyodbc','inspect']
stateList=['normal','normal']




'''=================dialog functions================='''
def user_browse_for_file():
    'opens dialog for user to browse and select file'
    from tkinter import filedialog,Tk
    file_name = filedialog.askopenfilename()
    return file_name

def user_browse_for_folder():
    from tkinter import filedialog,Tk
    folder_name=filedialog.askdirectory()
    return folder_name

'''==============make exe files============='''
'''
go to scripts folder in cmd and type:
    pyinstaller --onefile --noconsole "file path/name"
    note that this will be a simple command prompt program
    and it will likely save in the scripts folder
    for recursion error:
        open myfile.spec and put the following at the top:
            # -*- mode: python -*-
            import sys
            sys.setrecursionlimit(5000)
        now go back to command prompt and type the following:
            pyinstaller --onefile --noconsole myfile.spec
 note that pandas module does not compile correctly. must modify .spec
 refer to Simpletkinter.spec (documents/python) for how to modify
 for excludes: go to spec file and add modules to exclude=['module1','module2']
 or it may be easier to use command prompt option:
 pyinstaller --onefile --noconsole --exclude-module module1 --exclude-module module2 myscript.py
 (excludes will be useful for jt functions since jt uses many other modules)
 --note: the exclude option doesn't work if the module has been imported
 ---it does work if "import module1" is within a function but never called
 --alternative is to edit the excludes list in the .spec file
 

to add an icon after EXE is made:
    use Resource Hacker. to make the .ico use easypicture2icon
    
'''



'''********functions **********'''
def createSpec(programName,
               exclude_list=True,datas_list=[],
               hiddenimports_list=[],overwrite=False,icon="KasonLogo.ico"):
    '''generates spec file. requires user inputs
    
    '''
    import os
    if exclude_list==True:
        exclude_list=getexcludesForMainScript()
    
    #autocorrect program name
    if '.py' in programName: programName=programName.replace('.py','')

    
    
    #section 1
    specText=(
'''# -*- mode: python -*-

import sys
sys.setrecursionlimit(5000)

block_cipher = None
''')
    
    if 'pandas' not in exclude_list:
        specText+='''def get_pandas_path():
    import pandas
    pandas_path = pandas.__path__[0]
    return pandas_path
    
'''
    
    #add lists:
    specText+=(
            'exclude_list='+str(exclude_list)+"\n"+
            'programName="'+str(programName)+'"\n'+
            'datas_list='+str(datas_list)+"\n"+
            'hiddenimports_list='+str(hiddenimports_list)+"\n"
            )
    
    
    #section 2
    specText+=(
            '''
a = Analysis([programName+'.py'],
             pathex=['C:\\Program Files (x86)\\Python36-32\\Scripts'],
             binaries=[],
             datas=datas_list,
             hiddenimports=hiddenimports_list,
             hookspath=[],
             runtime_hooks=[],
             excludes=exclude_list,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)'''+"\n")
    
    if 'pandas' not in exclude_list:
        specText+='''
dict_tree = Tree(get_pandas_path(), prefix='pandas', excludes=["*.pyc"])
a.datas += dict_tree
a.binaries = filter(lambda x: 'pandas' not in x[0], a.binaries)'''
    
    
    
    #final section:
    specText+=('''
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=programName,
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False''')
    if icon==None:    
        specText+=" )"
    else:
        specText+=",\n          icon='"+icon+"')\n"
    
    
    #print(specText)
    #now generate the spec file:
    scriptsDir=getpythonfolder()+"\\Scripts"
    specFile=scriptsDir+"\\"+programName+".spec"
    if os.path.exists(specFile)==False or overwrite:#create file
        f=open(specFile,'w')
        f.write(specText)
    else:
        print("spec file already exists. you may choose overwrite option")




'''====================GUI notes and tkinter================'''
'''
I am using PAGE which is a tkinter based GUI builder
it is really only good for initially getting the code started. after that
it is easier to edit the GUI through an IDE.
PAGE instructions:
    -set the IDE in preferences. I typed in "spyder3"
    -set up the new GUI the way you want it to look then save it
    -Gen_python->Generate Support Module
    -Gen_python->Generate Python GUI
    -save everything
    -Gen_python->load project into IDE or just close page and open the .py file
    -using spyder: make sure to use a dedicated console
for example refer to TestGUI
callbacks: 
    error: 1 argument received 2: this means the function needs to have self
    as the first argument. example:
        def samplefunc(self,arg1): do this
    command: call a function with no inputs and do not put () at the end. ex:
        self.but39.configure(command=self.printToLabel)
    do NOT put:
        self.but39.configure(command=self.printToLabel())
tkinter examples....

#Notebook (switch frames using tabs)
main=Tk()
nb=Notebook(main,height=50,width=100)
nb.grid(row=1,column=1)
f1=Frame(nb)
nb.add(f1)
nb.tab(0,text="tab1",underline="-1")
f2=Frame(nb)
nb.add(f2)
nb.tab(1,text="tab2",underline="-1")
main.mainloop()

f=Frame(main)
f.grid(row=0,column=0)
f.grid_remove()#hides this frame and anything inside it
f.grid()#brings back the frame and everything inside it

Canvas:
-examples: GUI_Canvas_DrawLine and GUI_Canvas_DrawFree,GUI_Canvas_MoveWidget
-Canvas allows you to draw but also to move widgets freely
-you can add widgets in the canvas and allow those widgets to be dragged around

Adding Images to Labels:
pic=encodeImage(file_name)#note it is better to copy and paste this string 
#then store as a variable. this way the program doesn't require an external image
render=PhotoImage(data=pic)
lbl=Label(image=render)

Adding Images to banner icon:
pic=encodeImage(file_name)
render=PhotoImage(data=pic)
main.tk.call('wm','iconphoto',main._w,render)
'''
def EntryTable(master,hor=1,vert=1,ht=10,wd=30):
    '''this widget creates a table of Entry Boxes
    these Entry Boxes are rows/columns of entry boxes
    cframe,cells=EntryTable(master,hor=2,vert=3)
    cframe.grid(column=0,row=0)#sets grid for cells frame
    cells[0][0].insert(0,"text")#insert text on first cell
    cells[1][2].insert(0,"text2")#insert text on last cell
    '''
    from tkinter import Entry,Frame
    f=Frame(master)
    ent=[[[]]*vert for k in range(hor)]
    for i in range(hor):
        for j in range(vert):
            ent[i][j]=Entry(f)
            ent[i][j].grid(column=i,row=j,ipadx=wd,ipady=ht)
            #ent[i][j].insert(0,"entry"+str(j)+str(i))
    return f,ent

def encodeImage(file_name):
    '''
    encodeImage(file_name)
    file_name=path and file name (as string)
    this string can be copied to a variable and later used with PhotoImage
    to render the image inside a GUI without calling an external image file
    the image must be a GIF for this to work
    see ScreenPartNumberProgram1.py for example
    '''
    import base64
    with open(file_name, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string

#this function automatically disables print...
def JTPhotoImage(file_name,pythonDir=getpythonfolder(),debugmode=False):
    '''my version of PhotoImage
    this version is compatible with pyinstaller
    (hopefully)
    render=JTPhotoImage('example.gif')
    the image must be a .gif file
    
    note that this assumes the python folder is in program files
    if it is anywhere else then you need to add the python directory
    example:
    mydir = r"C:\Python36-32"
    render=JTPhotoImage(file_name="picture.gif",pythonDir=mydir)
    
    this file works by creating a module in the Lib folder. 
    the module name is based on the main file name. for example:
    your main file name is mymain.py
    created module name: mymainImages.py
    all variable names within here are the imagenames
    
    for this function to work you must add the created module to hidden imports
    
    to add: generate .spec file (if not yet created) and include hidden import
    
    '''
    import os
    import sys
    from tkinter import PhotoImage
    
    #debug mode: (allow printing only if true)
    yesprint=sys.stdout#used to enable printing
    noprint=open(os.devnull,'w')#used to disable printing
    #sys.stdout=yesprint#default
    if debugmode==False: sys.stdout=noprint#printing disabled
    
    #get info from file_name (image file):
    if ".gif" not in file_name:
        raise Exception("JT error: must be a gif")
    imagename=os.path.basename(file_name).replace(".gif","")
    imagefilepath=os.path.dirname(file_name).replace("/","\\")
    if imagefilepath=='':#if user doesn't include
        imagefilepath=os.getcwd()
    imagefile=imagefilepath+"\\"+os.path.basename(file_name)
    print("imagename: "+imagename)
    print("imagefile: "+imagefile)
    
    #directory for image module (in Lib folder)
    fullDir=sys.argv[0].replace("/","\\")#this prints .exe path and filename
    LibDir=pythonDir+"\\Lib"
    
    newModuleFile=fullDir[:fullDir.find(".")]+".py"#force .py at the end
    newModuleFile=os.path.basename(newModuleFile)
    print("newModuleFile1: "+newModuleFile)
    newModuleFile=newModuleFile.replace(".py","Images.py")
    print("newModuleFile2: "+newModuleFile)
    newModuleName=os.path.basename(newModuleFile).replace(".py","")
    newModuleFile=LibDir+"\\"+newModuleFile
    print("fullDir: "+fullDir)
    print("LibDir: "+LibDir)
    print("newModuleFile: "+newModuleFile)
    print("newModuleName: "+newModuleName)
    print("starting render process...\n")
    
    #render image:
    try:
        '''first try to import. this is only being used within IDE's
        it is better not to import within the EXE'''
        #exec("import "+newModuleName)#check if module is created. this doesn't work
        #import renderImageTest2Images#this worked
        #__import__(newModuleName)#doesn't work on exe
        #print("1a: imported module "+newModuleName+" successfully")
        try:
            exec("import "+newModuleName)
            print("imported (needed inside IDE)")
        except:
            print("couldn't import (not necessary for exe)")
            
        try:
            print("attempting to retreive image bytes")
            pic=getattr(eval(newModuleName),imagename)#check if image bytes are saved
            print("2a: successfuly retreived image string "+imagename)
        except:#no img bytes, add new image variable
            print("did not retreive image bytes. checking module file")
            f1=open(newModuleFile,'r')
            check=f1.read()
            f1.close()
            if "\n"+imagename+"=" in check:#allow var creation only once
                print('module and var already exists')
            else:
                print('2b: module found, creating new image var...')
                f=open(newModuleFile,'a+')#open in append mode
                ei=encodeImage(imagefile)
                addvar = "\n"+imagename+"="+str(ei)+"\n"
                f.write(addvar)
                f.close()
                pic=ei
                print("added image string "+imagename)
        print('2c: attempting to render')
        render = PhotoImage(data=pic)#fails here
        print("rendered "+imagename+" successfully")
    except:
        if os.path.exists(newModuleFile)==False:#create new module if it doesn't exist
            print("1b: nothing to import. creating module...")
            f=open(newModuleFile,'w')
            ei=encodeImage(imagefile)
            addvar="\n"+imagename+"="+str(ei)+"\n"
            f.write(addvar)
            f.close()
            pic=ei
            print("created image string "+imagename)
            render=PhotoImage(data=pic)
            print("rendered "+imagename+" successfully")
        else:#if module exists and ended up here then couldn't get image var
            print("1c: file exists, error rendering")
    
    if fullDir[-3:]==".py":#create spec file if running from IDE
        mainFile=os.path.basename(fullDir)
        mainFile=mainFile.replace(".py","")
        createSpec(mainFile,hiddenimports_list=[newModuleName])
        
    sys.stdout=yesprint#reenable printing
    return render

def TKcenterwindow(root):#center window on startup
    '''centers window in tkinter
    note: if any frames are hidden or shown 
    then you must use root.geometry("")
    in order to make the GUI update size
    use swCreateBlankProject.py as reference'''
    from tkinter import Tk
    def cw():
        ws = root.winfo_screenwidth() # width of the screen
        hs = root.winfo_screenheight() # height of the screen
        w=root.winfo_width()#width of GUI
        h=root.winfo_height()#height of GUI
        x = (ws/2) - (w/2)#calculate x coordinate for GUI
        y = (hs*.25) - (h/2)#calculate y coordinate for GUI
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    root.after(50,cw)


def TKaddonzoom(root,zoomfunc=None,normfunc=None):
    '''this function does something when window is maximized
    and does something else when window is unmaximized
    example:
    def onMaximizeFunc():
        do something
    def onUnmaximizeFunc():
        do something else
    TKaddonzoom(main,onMaximizeFunc,onUnmaximizeFunc)
    '''
    def onzoomed(event):#to do when window is maximized or unmaximized
        global stateList
        stateList.append(root.state())
        if len(stateList)>10: stateList=stateList[-2:]#manage size
        
        #if no widget was populated and window state changed:
        if str(event.widget)=='.' and stateList[-2]!=stateList[-1]:
            if stateList[-1]=='zoomed':#when user maximizes window
                if zoomfunc!=None:
                    zoomfunc()
                #print("maximized")
            elif stateList[-2]=='zoomed':#when user unmaximizes window
                #unmaximize events
                if normfunc!=None:
                    normfunc()
                #print("minimized")
    root.bind("<Configure>",onzoomed)#bind function to change of window state/size
    
def TKgrid_configColRange(root,cols=[]):
    '''configures range of columns. adding weight of 1
    input could be a list, range or integer 
    integer will be taken as a range'''
    if type(cols)==type(1): cols=range(cols)
    for i in cols: root.grid_columnconfigure(i,weight=1)

def TKshowFrameKeepCurrentGeometry(root,widget):
    '''displays the frame and anything on that frame
    while keeping the window the same size as before adding the frame
    this is typically used to add hidden features to a window
    which are only shown after increasing the size of the window
    example:
    main.after(30,TKshowFrameKeepCurrentGeometry,main,frame1)'''
    from tkinter import Tk,Frame
    def LCGwait():
        w=root.winfo_width()
        h=root.winfo_height()
        x=root.winfo_x()
        y=root.winfo_y()
        def LCGwaitAgain():
            root.geometry("%dx%d+%d+%d" % (w,h,x,y))
        root.after(20,LCGwaitAgain)#time set geometry
        widget.grid()
    root.after(30,LCGwait)#time to update current widgets
    
def TKdisplayGifAsIcon(root,image):
    '''adds image to window icon in GUI. image must be a gif'''
    from tkinter import Tk
    render=JTPhotoImage(image)
    root.tk.call('wm','iconphoto',root._w,render)


def getjtimports():
    '''gets dict of modules and submodules
    with 'jmt' in the name that have been imported
    returns {modulename:moduleobject}'''
    global submodules
    import sys
    from inspect import getmembers,isfunction
    submodfuncs={}
    #current_module = sys.modules[__name__]
    sysmod=sys.modules
    #sysmod=[sysmod.keys(),sysmod.values()]
    jmtsubmods={k:v for k,v in sysmod.items() if 'jmt' in k}
    jmtsubmodslist=list(sysmod.keys())#not needed
    return jmtsubmods

def getjtfuncs():
    '''gets dict of submodules:functions list
    submodules is string and functions list is a list of all 
    functions within the submodule'''
    from inspect import getmembers,isfunction
    jmtsubmods=getjtimports()
    jmtfuncs={}
    for i,j in jmtsubmods.items():
        jmtfuncs[i]=[k for k,v in getmembers(j,isfunction)]
    return jmtfuncs

def getFuncText(mod,func):
    '''returns list of imports used within function
    input mod and function as string
    example:
    getImportsInFunc('jmt.jttkinter','gettfuncs')'''
    import sys
    import __main__
    filepath=sys.modules[mod].__file__
    f=open(filepath)
    txt=f.read()
    f.close()
    loc=txt.find(func)
    txtfunc=txt[loc:]
    nl =strfind("\n",txtfunc)
    t=strfind("    ",txtfunc)
    loc2=[v for v in nl if v+1 not in t]
    if len(loc2)>0: txtfunc=txtfunc[:loc2[0]]
    return txtfunc
    

def inspectMainScriptForModules():
    '''this function will read the main function file for modules
    it will then return a list of modules found which are typically
    excluded from createSpec exclude list'''
    import sys
    from inspect import getmembers,isfunction
    #getmembers(jmt.jttkinter, isfunction)
    global excludes_list
    mainScript=sys.argv[0]
    f=open(mainScript)
    txt=f.read()
    f.close()
    modules_found=[v for v in excludes_list if v in txt]
    jmtfuncs=getjtfuncs()#dict of {submodule:functionslist}
    
    #get list of functions used in main script:
    funcsUsed={}#these are the functions being used in main script
    for submods,jtflist in jmtfuncs.items():
        for jtfunc in jtflist:#do something with functions list
            if jtfunc in txt:#jt function was found within main script
                #add to end of list if it exists. otherwise create list
                try: funcsUsed[submods]+=[jtfunc]
                except: funcsUsed[submods]=[jtfunc]
                
    #check function for excludes_list:
    for FUmods,FUfuncs in funcsUsed.items():
        for FUfunc in FUfuncs:
            #print(FUmods+": "+FUfunc)#for debugging
            txtfunc=getFuncText(FUmods,FUfunc)#get full text of func
            #now add excludes modules to mods found if found within jt func
            modules_found+=[v for v in excludes_list if v in txtfunc]
            #if jt subfuncs are used, add to funcsUsed[FUmods] list
            funcsUsed[FUmods]+=[v for v in jmtfuncs[FUmods] if v in txtfunc and 
                      v not in funcsUsed[FUmods]]
    modules_found=list(set(modules_found))#remove duplicates
    modules_found.sort()
    return modules_found

def getexcludesForMainScript():
    '''this module gets the excludes list but removes
    anything from the list that the main script is using'''
    global excludes_list
    modsfound=inspectMainScriptForModules()
    newExcludes=[v for v in excludes_list if v not in modsfound]
    return newExcludes
    
    
