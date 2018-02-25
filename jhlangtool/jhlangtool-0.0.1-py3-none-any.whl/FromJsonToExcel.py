#! /usr/bin/env python

import xlsxwriter
import json
from os import listdir, getcwd
from os.path import basename, join
import argparse
import logging

def GenerateExcelFile(arguments=None):
	parser = argparse.ArgumentParser(description="This will generate an excel file that lists all values for all JSON-files in directories.")
	parser.add_argument('-i', '--input', 
	help="The path to a root directory, which contains the language directories, which contain the JSON files.")
	parser.add_argument('-f', '--filename', help="The output filename (default output.xlsx)", nargs='?', default='output.xlsx')
	parser.add_argument('-o', '--output', default=getcwd(), help="Where to save the excel file (default is current working directory)")
	parser.add_argument('-v', '--verbose', default=getcwd(), help="Outputs current processing file (verbose output)")
	if arguments == None:
		arguments = parser.parse_args()
		arguments = vars(arguments)

	try:
		inputDirs = arguments["input"]
		if inputDirs == None:
			raise KeyError
	except KeyError:
		print("\n --ERROR-- ")
		print("Input directory not specified. Run 'jhlangtool toexcel -i <path to root language directory>'")
		print("\n")
		parser.print_help()
		quit()
	try:
		outputDirs = arguments["output"]
	except KeyError:
		outputDirs = getcwd()
	try:
		file_name = arguments["filename"]
		if file_name[-5:] != '.xlsx':
			file_name = file_name+'.xlsx'
		excel_file = join(outputDirs, file_name)
	except KeyError:
		excel_file = join(outputDirs, 'output.xlsx')
	if len(basename(outputDirs)) > 5 and outputDirs[-5:] == '.xlsx':
		excel_file = outputDirs
	try:
		arguments["verbose"]
		logging.basicConfig(level=logging.INFO, format='%(message)s')
	except KeyError:
		pass
	wb = xlsxwriter.Workbook(excel_file)
	language_row_format = wb.add_format()
	language_row_format.set_bg_color('#c5efcd')
	language_row_format.set_bold()
	key_col_format = wb.add_format()
	key_col_format.set_bg_color('#cbe7ff')
	counter = 0
	col = 1

	start_row = 0


	def dictionary_breaker(d, ws, scol, title):  # dodati jezik i ispitati da li je jednak "en" da se unese u
		nonlocal start_row
		for k in d:

			if type(d[k]) == dict:
				find_key_row(worksheet, title + '/' + str(k))
				dictionary_breaker(d[k], ws, col, title + '/' + str(k))
			else:
				write_into_worksheet(worksheet, title + '/' + str(k), col, d[k])


	def find_key_row(worksheet, key):
		nonlocal worksheet_keys
		nonlocal start_row

		try:
			index = list(worksheet_keys.keys()).index(key)
		except ValueError:
			index = start_row
			start_row += 1
			worksheet_keys[key] = index
			worksheet.write(index, 0, key)

		return worksheet_keys[key]


	def write_into_worksheet(worksheet, key, col, value):
		index = find_key_row(worksheet, key)
		worksheet.write(index, col, value)


	for file in listdir(join(inputDirs, 'en')):
		counter += 1
		start_row = 2
		worksheet_name = basename(file)[:-5]
		worksheet = wb.add_worksheet(worksheet_name[:30] + str(counter)[:0])
		worksheet.write(0, 0, basename(file))
		worksheet_keys = {}
		logging.info("Processing {}".format(file))
		col = 1

		for language in listdir(inputDirs):
			json_files = join(inputDirs, language)

			worksheet.write(0, col, language)
			#start_row += 1
			file2 = json_files + '/' + file
			# file2 = json_files + '/' + 'audits.json'
			# content = pandas.read_json(file2, typ=pandas.Series, encoding='utf-8')
			content = []
			try:
				with open(file2, encoding='utf-8') as data_file:
					content = json.loads(data_file.read())
				for key in content:
					value = content[key]
					if type(value) == dict:
						find_key_row(worksheet, key)
						dictionary_breaker(value, worksheet, col, key)
					else:
						write_into_worksheet(worksheet, key, col, value)
			except FileNotFoundError:
				pass

			col += 1
			worksheet.set_column(firstcol=1, lastcol=col, width=18)
			worksheet.set_column(firstcol=0, lastcol=0, width=30)
			worksheet.set_row(0,  cell_format=language_row_format)

	print("File saving to", excel_file)
	wb.close()

if __name__ == '__main__':
	GenerateExcelFile()
