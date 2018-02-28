#!/usr/bin/env python3
import os, sys, logging
from pics2word import *
from LogGen import set_up_logging

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
\t-v\t - Verbosity, for debugging purposes. Set how much the program talks with "talk", "info" or "quiet". Defaults to "quiet".

Commands may be passed as command-value pairs in any order.
All commands are optional and the defaults will be used if no commands are given.

Example: pics2word -P \"C:\\\\Pictures\\\" -T Report -Td n -f table\n'''
    print(message)

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
    myargs = getopts(sys.argv)
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
