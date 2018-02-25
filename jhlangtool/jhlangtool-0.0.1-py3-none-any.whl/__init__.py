import sys
from subprocess import Popen, PIPE
from . import FromExcelToJson, FromJsonToExcel

def process_args(l):
	argsdict = {}
	lower = False
	for i in range(0, len(l), 2):
		if lower == True:
			i -= 1
		command = l[i]
		if command == '-v' or command == '--verbose':
			argsdict['verbose'] = True
			lower = True
			continue
		try:
			value = l[i+1]
		except IndexError:
			break
		if command[0] != '-':
			print("Invalid arguments")
			quit()
		if command == '-i' or command == '--input':
			argsdict['input'] = value
		elif command == '-o' or command == '--output':
			argsdict['output'] = value
		elif command == '-f' or command == '--filename':
			argsdict['filename'] = value
		else:
			print("Invalid arguments")
			quit()
	return argsdict

def main():
	args = sys.argv[1:]
	if len(args) == 0:
		print(
		"""
		Error: no arguments provided
		
		To convert from JSON to excel, do:
		jhlangtool toexcel -i <path to root language directory> [-o <path to output directory>] [--filename <name of excel file>] [-v]
	
		To covert from Excel to JSON, do:
		jhlangtool tojson -i <path to excel file> [-o <path where to generate JSON>] [-v]
		
		Please note that toexcel and tojson have to be the first argument
		"""
		)
		quit()
	programargs = ['python']
	dict = process_args(args[1:])
	if args[0].lower() == 'toexcel':
		FromJsonToExcel.GenerateExcelFile(arguments=dict)
	if args[0].lower() == 'tojson':
		FromExcelToJson.GenerateJSON(arguments=dict)

if __name__ == "__main__":
	main()
		