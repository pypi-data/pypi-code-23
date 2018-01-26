#!/usr/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.
#

import sys, argparse
from .bdwb import BDwb as Workbench

def main():
    parser = argparse.ArgumentParser(description='Available options')
    parser.add_argument('batchfile', metavar='INSTRUCTION_FILE', nargs='?',
                        default=None,
                        help='A file that contains workbench commands for '
                             'non-interactive processing.')
    parser.add_argument('--initapp', action='store_true', default=False, dest='init',
                        help='Initialize the current directory with skeletal code '
                        'and directroy structure for developing a catalog entry '
                        'for BlueData\'s EPIC platform.')
    parser.add_argument('-i', '--instruction', metavar='INSTRUCTION',
                        action='store', dest='instr', default=None,
                        help='A single instruction to execute. This will exit '
                        'as soon as the given instructions is executed.')
    parser.add_argument('--baseimg', choices=['centos6', 'rhel6', 'centos7', 'rhel7', 'ubuntu16'],
                        default=None, dest='baseimg', action='store',
                        help='Copy all the files related to building docker '
                        'image that can be used as a base for apps on BlueData '
                        'EPIC. The files are copied to the current directory.')
    parser.add_argument('-v', '--version', action='store_true', dest='version',
                        help='Prints the SDK version on the console and exits.')

    args = parser.parse_args()

    if (args.instr != None) and (args.batchfile != None):
        parser.error("-i/--instruction and batchfile are mutually exclusive options.")
        sys.exit(1)

    instruction=''
    if args.version == True:
        instruction = 'workbench version'
    elif args.init == True:
        instruction = 'workbench initapp'
    elif args.baseimg != None:
        instruction = 'baseimg init --os %s' % (args.baseimg)
    else:
        instruction=args.instr

    Workbench(instr=instruction, batchfile=args.batchfile).cmdloop()
