# Copyright (c) 2017 Daniel Knüttel                                           #
#                                                                             #
# This file is part of licor.                                                 #
#                                                                             #
# licor is free software: you can redistribute it and/or modify               #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# licor is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with licor.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
#                                                                             #


import docopt, datetime, sys
from .work import work_all, work_this_path
from .templates import get_template_meta, format_template, get_templates_available
from .comment import uncomment_line_based, uncomment_multiline_line_oriented, uncomment_multiline_block_oriented
import os, sys
from .io import insert_header, check_file_perm

usage = '''\

Insert license/copyright/warranty disclaimer to source files.

Usage:
       licor list-db [<path>] [options]
       licor list-all [<path>] [options]
       licor list-path [<path>] [options]
       licor list-templates [options]
       licor print-templ <format> [options]
       licor insert-header <format> [<path>] [options]

Options:
       --comment-start=<comment-start>                 Comment start token to use [default: //]
       --comment-stop=<comment-stop>                   Comment stop token to use [default: */]
       --border=<border>                               Border character for some fancy stuff [default: *]
       -f --fancy                                      Use more fancy comments 
       --after-comment=<after-comment>                 A string to seperate border and content (defaults to one blank)
       -c --confirm                                    Wait for user confirmation before modifying files
       --format=<format>                               Use a special comment format [default: block]
       --license=<license>                             Use this license template [default: GPLv3]
       --single-file                                   Use single-file templates
       --copyright                                     Use templates containing copyright information
       -a <author> --author=<author>                   Set the author (required for --copyright)
       -p <project> --project=<project>                Set the project (required unless --single-file is specified)
       -e <ending> --file-ending=<ending>              Search for files ending with this ending [default: c]
       -i --ignore-db                                  Ignore the database of processed files
       --ignore-paths=<paths>                          Ignore all paths with one of `<paths>` in it (comma-seperated) [default: .git]
       --pad-to=<pad-to>                               Pad comment blocks to this width [default: 0]
'''


db_filename = ".licor.list"
def get_ignored(path):
	try:
		with open(os.path.join(path, db_filename)) as f:
			return f.read().split("\n")
	except:
		return []

def write_ignored(path, ignored):
	with open(os.path.join(path, db_filename), "w") as f:
		f.write("\n".join([i for i in ignored if i]))

def get_confirmation(text):
	while(True):
		print(text, " ", end = "")
		res = input("(y/n) ")
		if(res in ("Y", "y")):
			return True
		if(res in ("n", "N")):
			return False
		print("please enter Y or N")

def get_path_confirmation(path):
	return not get_confirmation("use " + path)


def raw_insert_into_db(db_path, path):
	ignored = get_ignored(db_path)
	if(not path in ignored):
		ignored.append(path)
	write_ignored(db_path, ignored)



def list_this_path(path, file_ending, ignore_db = False):
	if(ignore_db):
		ignore_files = get_ignored(path)
	else:
		ignore_files = []
	work_this_path(path, file_ending, [print], ignore_files = ignore_files)

def list_all(path, file_ending, ignore_paths, ignore_db = False):
	if(not ignore_db):
		ignore_files = get_ignored(path)
	else:
		ignore_files = []
	work_all(path, file_ending, [print], ignore_paths = ignore_paths, ignore_files = ignore_files)

def list_db(path):
	with open(os.path.join(path, db_filename)) as f:
		print(f.read())

def print_uncommented_line_based(license_name, modifiers, data, 
		comment_start, fancy = False, after_comment = " ", pad_to = 0):
	data = format_template(license_name, data, modifiers)
	print(uncomment_line_based(data, comment_start, fancy = fancy, 
				after_comment = after_comment, pad_to = pad_to))

def print_uncommented_block_based(license_name, modifiers, data, 
		comment_start, comment_stop, method = "line", border = "*", fancy = False, after_comment = " ", pad_to = 0):
	data = format_template(license_name, data, modifiers)

	if(method == "block"):
		print(uncomment_multiline_block_oriented(data,
				comment_start, comment_stop,
				after_comment = after_comment,
				fancy = fancy, border = border,
				pad_to = pad_to))
	else:
		print(uncomment_multiline_line_oriented(data,
				comment_start, comment_stop,
				after_comment = after_comment,
				fancy = fancy, border = border,
				pad_to = pad_to))

def print_template_options():
	meta = get_templates_available()
	for template_name, data in meta.items():
		print(template_name)
		for modifier in data["modifiers"]:
			print("\t\t", modifier)



def insert_templates_all(path, file_ending, ignore_paths, license_name, modifiers, data, 
		comment_start, comment_stop, format_, method = "line", border = "*",
		fancy = False, after_comment = " ", pad_to = 0,
		ignore_db = False, confirm = False):
	if(not ignore_db):
		ignore_files = get_ignored(path)
	else:
		ignore_files = []


	# check for file permissions
	try:
		work_all(path, file_ending, [check_file_perm], ignore_paths = ignore_paths, ignore_files = ignore_files)
	except Exception as e:
		print(e)
		sys.exit(1)


	callbacks = []

	data = format_template(license_name, data, modifiers)
	if(format_ == "line"):
		text = uncomment_line_based(data, comment_start, fancy = fancy, 
				after_comment = after_comment, pad_to = pad_to)
	else:
		if(method == "block"):
			text = uncomment_multiline_block_oriented(data,
					comment_start, comment_stop,
					after_comment = after_comment,
					fancy = fancy, border = border,
					pad_to = pad_to)
		else:
			text = uncomment_multiline_line_oriented(data,
					comment_start, comment_stop,
					after_comment = after_comment,
					fancy = fancy, border = border,
					pad_to = pad_to)
	text += "\n\n"
	if(confirm):
		callbacks.append(get_path_confirmation)

	callbacks.append(lambda x: insert_header(x, text))

	if(not ignore_db):
		callbacks.append(lambda x: raw_insert_into_db(path, x))

	work_all(path, file_ending, callbacks, ignore_paths = ignore_paths, ignore_files = ignore_files)

	
def main():
	args = docopt.docopt(usage, sys.argv[1:])

	if(args["list-db"]):
		path = args["<path>"]
		if(not path):
			path = "."
		try:
			list_db(path)
		except Exception as e:
			print(e)
			sys.exit(1)

	if(args["list-path"]):
		path = args["<path>"]
		if(not path):
			path = "."
		ending = args["--file-ending"]
		ignore_db = args["--ignore-db"]

		list_this_path(path, ending, ignore_db = ignore_db)

	if(args["list-all"]):
		path = args["<path>"]
		if(not path):
			path = "."
		ending = args["--file-ending"]
		ignore_paths = args["--ignore-paths"].split(",")
		ignore_db = args["--ignore-db"]

		list_all(path, ending, ignore_paths, ignore_db = ignore_db)

	if(args["print-templ"]):
		form = args["<format>"]
		license_name = args["--license"]
		modifiers = []
		if(args["--single-file"]):
			modifiers.append("single-file")
		if(args["--copyright"]):
			modifiers.append("copyright")

		data = {}
		if(args["--author"]):
			data["author"] = args["--author"]
		if(args["--project"]):
			data["project"] = args["--project"]
		data["year"] = str(datetime.datetime.now().year)

		after_comment = " "
		if(args["--after-comment"]):
			after_comment = args["--after-comment"]

		try:
			pad_to = int(args["--pad-to"])
		except:
			print("Failed to convert {} to int".format(args["--pad-to"]))
			sys.exit(1)

		if(form == "line"):
			print_uncommented_line_based(license_name, modifiers, data, args["--comment-start"],
					fancy = args["--fancy"], after_comment = after_comment,
					pad_to = pad_to)
		elif(form == "block"):
			method = args["--format"]
			if(not method):
				method = "line"

			print_uncommented_block_based(license_name, modifiers, data,
					args["--comment-start"], args["--comment-stop"],
					border = args["--border"],
					fancy = args["--fancy"], after_comment = after_comment,
					method = method,  pad_to = pad_to)
		else:
			print("Unknown format ({}). Use line or block.".format(form))
		
	if(args["list-templates"]):
		print_template_options()

	if(args["insert-header"]):
		form = args["<format>"]
		license_name = args["--license"]
		modifiers = []
		if(args["--single-file"]):
			modifiers.append("single-file")
		if(args["--copyright"]):
			modifiers.append("copyright")

		data = {}
		if(args["--author"]):
			data["author"] = args["--author"]
		if(args["--project"]):
			data["project"] = args["--project"]
		data["year"] = str(datetime.datetime.now().year)

		after_comment = " "
		if(args["--after-comment"]):
			after_comment = args["--after-comment"]

		try:
			pad_to = int(args["--pad-to"])
		except:
			print("Failed to convert {} to int".format(args["--pad-to"]))
			sys.exit(1)
		method = args["--format"]
		if(not method):
			method = "line"

		path = args["<path>"]
		if(not path):
			path = "."
		ignore_paths = args["--ignore-paths"].split(",")
		ignore_db = args["--ignore-db"]
		insert_templates_all(path, args["--file-ending"], ignore_paths, license_name,
				modifiers, data, args["--comment-start"], args["--comment-stop"],
				form, method = method, border = args["--border"], fancy = args["--fancy"],
				after_comment = after_comment, pad_to = pad_to, ignore_db = args["--ignore-db"],
				confirm = args["--confirm"])
