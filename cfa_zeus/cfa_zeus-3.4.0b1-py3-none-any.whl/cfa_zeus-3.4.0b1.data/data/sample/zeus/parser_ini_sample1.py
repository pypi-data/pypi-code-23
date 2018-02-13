#!/usr/bin/env python3
# coding: utf8
#-----------------------------------------------------------------
# zeus: parser_ini_sample.py
#
# process launcher
#
# Copyright (C) 2016, Christophe Fauchard
#-----------------------------------------------------------------

import argparse
import sys
import zeus

#
# Parse command line arguments
# The option formatter_class=argparse.RawTextHelpFormatter allow
# help fields to be multi lines 
#
args_parser = argparse.ArgumentParser(description = "Sample for parsing ini config files", 
formatter_class=argparse.RawTextHelpFormatter)
args_parser.add_argument("--version", action = 'version', version = '%(prog)s ' + zeus.__version__)
args_parser.add_argument("ini_file",  help = "ini file")
args = args_parser.parse_args()

print("version zeus: " + zeus.__version__)
print("Running tests for parser.py...")

print("testing class ConfigParser...")

try:
	parser = zeus.parser.ConfigParser(args.ini_file)

	print("parsing of " + args.ini_file + " done")
	print(parser)

except zeus.exception.FileNotFoundException as error:
	print("Class ConfigParser not passed, File not found: " + error.filename)
else:
	print("Class ConfigParser passed")

	
