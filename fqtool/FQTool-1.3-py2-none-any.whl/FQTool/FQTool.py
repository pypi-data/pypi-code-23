#!/usr/bin/env python3

## @file FQTool.py
## @brief Some code lines to merge the two parsers.

# Import the necessary functions
from src.ArgParser import create_parser
from src.FQParser import process_read

# Parse the command line flags and put them into a dictionary
# NOTE: I accept a list of input files, so user can insert every filenames he wants 
args = vars(create_parser().parse_args()) 
for i in range(0, len(args["filenames"])):
	# Open the files in read-only mode once at a time
	with open(args["filenames"][i], "r") as read_stream:
		count_lines = 0
		# We need to get the second and the fourth lines per read, we work using modules to find them
		for line in read_stream:
			count_lines += 1
			if count_lines % 4 == 2:
				read = line.rstrip()
			if count_lines % 4 == 0:
				phread = line.rstrip()
				# Call a function to find the best part of the read satisfying the required features, print it after the computation 
				res = process_read(read, phread, args["function"], args["accuracy"] , args["quality"], args["length"])
				# Print the result
				if (res != None):
					print(res)
				else:
					print("Could not find a part of the read that satisfied your requirements.")
