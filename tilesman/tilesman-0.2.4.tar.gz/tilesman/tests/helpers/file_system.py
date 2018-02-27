import os
import shutil

def recursive_file_count(root_dir):
	'''
	Recursively counts how many files exist in 'root_dir' and all subdirectories
	'''

	return sum([len(files) for r, d, files in os.walk(root_dir)])

def recursive_dir_count(root_dir):
	'''
	Recursively counts how many directories exist in 'root_dir' and all subdirectories
	'''

	return sum([len(d) for r, d, files in os.walk(root_dir)])

def scan_dir(root_dir, include = 'dir'):
	'''
	Lists all files or directories exist in 'root_dir'. The distinction between what
	needs to be counted is made using the argument 'include'
	'''

	if include == 'dir':
		opt = 1
	elif include == 'file':
		opt = 2
	else:
		return []

	return [element for element in next(os.walk(root_dir))[opt]]

def create_dir(path):
	'''
	Creates a new directory as referenced by path
	'''

	os.mkdir(path)

def delete_dir(path):
	'''
	Deletes a directory referenced by path
	'''

	shutil.rmtree(path)
