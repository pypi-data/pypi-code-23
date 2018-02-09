'''
importer.py

a class which auto imports all modules provided
'''
from subprocess import check_output

def ImportHandler(modules):
    '''
    DESCRIPTION
        ImportHandler tries to import a module and if fails tries to install
        it using pip then imports it

    VARIABLES
        modules
            This variable is expected to be a list of module names

    RETURN
        The return value is a string to be executed using exec()
        Correct use of ImportHandler is:
            exec(ImportHandler(["sys"]))
    '''
    exec_string = ""
    for i in modules:
        try:
            exec("import %s"%i)
        except:
            if i in knowns:
                i = knowns[i]
            check_output("pip install --user %s"%i, shell=True).decode()
            print("Installing %s..."%i)
        exec_string += "import %s\n"%i
    return(exec_string)

knowns = {'win32api':'pypiwin32',
          'win32con':'pypiwin32',
          'win32gui':'pypiwin32',
          'win32ui' :'pypiwin32'}
