#!/usr/bin/env python3
import os, sys
from .pics2word import *

# Method to parse command line arguements into command-value pairs
def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts

def main():
    Doc = pics2word()
    myargs = getopts(sys.argv)
    if '-h' in myargs:
        Doc.help()
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
