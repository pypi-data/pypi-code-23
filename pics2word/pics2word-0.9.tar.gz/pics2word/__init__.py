#!/usr/bin/env python3
import os, sys, logging, pickle
from .pics2word import *
from .LogGen import set_up_logging

logger = logging.getLogger(__name__)

def help():
    message = '''Usage: pics2word [-command] [value]
Options:
\t-h\t- Pass "help" to print this help message to the terminal. \n\t\t  Pass the name of a command below without the '-' for more informatio about that command. <UNDER CONSTRUCTION>
\t-P\t- Pass an alternative path to be used. i.e. \"C:\\\\Pictures\\\". Defaults to current directory.
\t-f\t- format pictures. pass either "normal" or "table". Defaults to normal. 
\t-T\t- Override the default title. Defaults to PhotoDoc_<current date> (See Td, below).
\t-Td\t- Choose to append the title with the current date. Options: \"y\" or \"n\". Defaults to \"y\".
\t-pw\t- Set the width of imported pictures in inches. Defaults to 4 inches
\t-ph\t- Set the height of imported pictures in inches. Defaults to 4 inches
\t-tw\t- Set the number of columns used in table format. Note: table format must be enabled! Defaults to 2.
\t-v\t- Verbosity, for debugging purposes. Set how much the program talks with "talk", "info" or "quiet". Defaults to "quiet".
\t-m\t- Module. Allows the creation of templates. Pass -m "report" to load the arguments saved in that module. 
\t\t  If the module name does not exist then one will be created under the passed name using the proceeding arguments as saved values.
\t\t  Note that when loading the template, arguments passed AFTER overwrite the template values but do not save permanently.

Commands may be passed as command-value pairs in any order.
All commands are optional and the defaults will be used if no commands are given.

Example: pics2word -P \"C:\\\\Pictures\\\" -T Report -Td n -f table\n'''
    print(message)

def remDictKey(d, key):
    '''Returns a new dictionary with a key-value pair removed'''
    new_d = d.copy()
    new_d.pop(key)
    return new_d

# Method to parse command line arguements into command-value pairs
def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            logging.debug("Adding %s as a value to %s command." % (argv[1], argv[0]))
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts

def main():
    #Arglist passed as immutable for key to dict 
    set_up_logging(tuple(sys.argv))
    IniArgs = getopts(sys.argv)
    # Load / save arg template
    if '-m' in IniArgs: 
        mod = IniArgs['-m']
        try:
            logger.info("Found module %s. Loading arg list." % mod)
            myargs = pickle.load(open(mod+".p", "rb"))
        except:
            # Assumes the file does not exist so sets one up
            logger.info("Module %s not found. creating module called %s" % (mod,mod))
            myargs = remDictKey(IniArgs, '-m') # dont resave save function
            pickle.dump(myargs, open(mod+".p", "wb"))
    else:
        myargs = IniArgs

    Doc = pics2word()  
    if '-h' in myargs:
        help()
    if '-P' in myargs:
        # Override the default path
        Doc.SetPath(myargs['-P'])
    if '-f' in myargs:
        # Set as table or default
        Doc.SetFormat(format=myargs['-f'])
    if '-T' in myargs:
        # Set a title to override the default
        Doc.SetTitle(title=myargs['-T'],date=myargs['-Td'])
    if '-pw' in myargs:
        # Override the default picture width
        Doc.SetPicWidth(float(myargs['-pw']))
    if '-ph' in myargs:
        # Override the default picture height
        Doc.SetPicHeight(float(myargs['-ph'])) 
    if '-tw' in myargs:
        if Doc.format[0] != 't' :
            raise ValueError("Must enable table format to format table width!")
        else:
            Doc.SetTableWidth(int(myargs['-tw']))
    
    # after all optional parameters have been changed and not asked for help, then write document.
    if '-h' not in myargs:
        Doc.WriteDoc()

if __name__ == '__main__':
    main()
