# tools.py

import os
import re
import io
import xmltodict
import json
import yaml
import pprint
import ConfigParser

""" config file format constants """
FMT_INI = 1
FMT_DELIMITED = 2
FMT_XML = 3
FMT_JSON = 4
FMT_YAML = 5

def determine_file_extension_based_on_format(format_specifier):
	""" returns file extension string """
	if format_specifier == FMT_INI:
		return 'ini'
	if format_specifier == FMT_DELIMITED:
		return ''
	if format_specifier == FMT_XML:
		return 'xml'
	if format_specifier == FMT_JSON:
		return 'json'
	if format_specifier == FMT_YAML:
		return 'yml'
	raise ValueError('invalid format specifier: {}'.format(format_specifier))

class CfgPy(object):

	"""
	 The CfgPy object exposes the methods
	 used to return a cfg dict.
	"""

	def __init__(self, format_specifier, confdir, filepaths=None):
		"""
		 args to object ctor
		 1. fmtspec (format specifier) constant (integer)   
		 2. confdir (directory containing config files)
		 3. filepaths - optional list of filepaths

		 When filepaths not None and not empty,
		 use explicit loading instead of implicit.

		 With explicit loading (e.g. from filepaths), 
		 the 'confdir' argument is ignored.

		 Implicit loading tries to load using three layers:
		 1. default
		 2. environment type (value of PY_ENV environment variable)
		 3. local

		 When using implicit loading, we look in confdir
		 to find default.<ext>, <envtype>.<ext>, local.<ext>
		 where <ext> is determined by the format.

		 Format-specific implicit file extensions:

		 1. FMT_INI .ini 
		 2. FMT_XML .xml 
		 3. FMT_JSON .json 
		 4. FMT_YAML .yml 
		 5. FMT_DELIMITED none, i.e. use <filename> not <filename>.<ext>

		 If you wish to use different file extensions, you must
		 use explit rather than implicit loading. That is, 
		 specify the list of filepaths explicitly via the
		 'filepaths' argument.

		 SPECIAL NOTE CONCERNING XML.

		 Xml requires an outermost enclosing tag (element).
		 Being an element, it must have an element name.
		 When config files are read, they're converted to Python dicts.
		 Dicts are recursive key/value structures.
		 When a file that's loaded later contains a key that matches
		 a key in the cfg dictionary loaded from an earlier file, the 
		 new value replaces the earlier one.
		 This means that when multiple xml loaded sequentially,
		 if the outermost element has the same name the entire contents
		 of the earlier file will be replaced with the contents of the
		 file loaded more recently. 

		 SPECIAL NOTE CONCERNING DELIMITED FILES 

		 Delimited files are a special case.
		 Explicit mode must be used; implicit mode is not supported.
		 And combining settings from multiple delimited files is not supported.
		 That means the 'filepaths' list should contain exactly one filepath
		 when using FMT_DELIMITED.

		"""

		""" should validate this """
		self.format = format_specifier
		""" validated by attempts to load files from here? """
		self.confdir = confdir
		if not isinstance(filepaths, list):
			filepaths = [filepaths]
		self.filepaths = filepaths
		self.file_extension = determine_file_extension_based_on_format(format_specifier)
		self.delimited_file_column_names = None
		self.field_delimiter = None
		self.cfg_dict = {}
		self.cfg_list = []
		self.load()

	def set_field_delimiter(self, field_delimiter):

		"""
		 use this method when using FMT_DELIMITED
		 to specify the field separator, i.e. the delimiter
		"""
		self.field_delimiter = field_delimiter

	def set_delimiter(self, field_delimiter):

		self.set_field_delimiter(field_delimiter)

	def set_file_extension(self, ext):

		self.file_extension = ext

	def set_delimited_file_column_names(self, column_names):
		""" 
		takes a list of column_names 
		when column names are provided, then if number of 
		column names matches the number of columns when
		lines are split on delimiter, load returns
		a list of dictionaries such that the keys are
		the column names. 
		when column names are not provided or number of
		column names doesn't match number of columns,
		load returns a list of tuples.
		"""

		self.delimited_file_column_names = column_names

	def read_element(self, element_path):
		"""
		takes a tuple of keys
		returns node found in cfg_dict
		found by traversing cfg_dict by successive 
		application of keys from element_path
		"""

		# doesn't support DELIMITED, only dict-based formats
		if self.format == FMT_DELIMITED:
			return None

		node = self.cfg_dict
		for key in element_path:
			node = node[key]
		return node

	def get_element(self, element_path):

		return self.read_element(element_path)

	def read_value(self, element_path):

		return self.read_element(element_path)

	def get_value(self, element_path):

		return self.read_element(element_path)

	def load_using_delimited_format_explicitly(self):

		comment_pattern = re.compile(r'^[\t ]*#')
		for filepath in self.filepaths:
			with open(filepath) as fh:
				for line in fh.readlines():
					# skip comments 
					if comment_pattern.match(line):
						continue
					fields = line.split(self.field_delimiter)
					if not self.delimited_file_column_names or not len(self.delimited_file_column_names) == len(fields):
						self.cfg_list.append(tuple(fields))
						continue
					row_dict = {}
					for i, _ in enumerate(self.delimited_file_column_names):
						colname = self.delimited_file_column_names[i] 
						row_dict[colname] = fields[i]
					self.cfg_list.append(row_dict)

		return self.cfg_list

	def load_using_ini_format_explicitly(self):

		self.cfg_dict = {}
		cp = ConfigParser.ConfigParser()
		for filepath in self.filepaths:
			""" with explicit loading, let file not found raise exception """
			cp.read(filepath)
			ordered_dict = cp._sections
			self.cfg_dict.update(json.loads(json.dumps(ordered_dict)))

		return self.cfg_dict

	def load_using_ini_format_implicitly(self):

		self.cfg_dict = {}
		cp = ConfigParser.ConfigParser()
		default_filepath = "{}/{}.{}".format(self.confdir, 
			'default', self.file_extension)

		try:
			cp.read(default_filepath)
			ordered_dict = cp._sections
			self.cfg_dict.update(json.loads(json.dumps(ordered_dict)))
		except Exception, e:
			pass

		if "PY_ENV" in os.environ:
			env_filepath = "{}/{}.{}".format(self.confdir,
				os.environ['PY_ENV'], self.file_extension)
			try:
				cp.read(env_filepath)
				ordered_dict = cp._sections
				self.cfg_dict.update(json.loads(json.dumps(ordered_dict)))
			except Exception, e:
				pass

		local_filepath = "{}/{}.{}".format(self.confdir,
			'local', self.file_extension)

		try:
			cp.read(local_filepath)
			ordered_dict = cp._sections
			self.cfg_dict.update(json.loads(json.dumps(ordered_dict)))
		except Exception, e:
			pass

		return self.cfg_dict

	def load_using_xml_format_explicitly(self):

		self.cfg_dict = {}
		for filepath in self.filepaths:
			""" with explicit loading, let file not found raise exception """
			with io.open(filepath, 'r') as fh:
				slurpee = fh.read().encode('utf-8')
				ordered_dict = xmltodict.parse(slurpee)
				file_dict = json.loads(json.dumps(ordered_dict))
			self.cfg_dict.update(file_dict)

		return self.cfg_dict

	def load_using_xml_format_implicitly(self):

		self.cfg_dict = {}
		default_filepath = "{}/{}.{}".format(self.confdir, 
			'default', self.file_extension)

		try:
			with io.open(default_filepath, 'r') as fh:
				slurpee = fh.read().encode('utf-8')
				ordered_dict = xmltodict.parse(slurpee)
				default_dict = json.loads(json.dumps(ordered_dict))
			self.cfg_dict.update(default_dict)
		except Exception, e:
			pass

		if "PY_ENV" in os.environ:
			env_filepath = "{}/{}.{}".format(self.confdir,
				os.environ['PY_ENV'], self.file_extension)
			try:
				with io.open(env_filepath, 'r') as fh:
					slurpee = fh.read().encode('utf-8')
					ordered_dict = xmltodict.parse(slurpee)
					env_dict = json.loads(json.dumps(ordered_dict))
				self.cfg_dict.update(env_dict)
			except Exception, e:
				pass

		local_filepath = "{}/{}.{}".format(self.confdir,
			'local', self.file_extension)

		try:
			with io.open(local_filepath, 'r') as fh:
				slurpee = fh.read().encode('utf-8')
				ordered_dict = xmltodict.parse(slurpee)
				local_dict = json.loads(json.dumps(ordered_dict))
			self.cfg_dict.update(local_dict)
		except Exception, e:
			pass

		return self.cfg_dict

	def load_using_json_format_explicitly(self):

		self.cfg_dict = {}
		for filepath in self.filepaths:
			""" with explicit loading, let file not found raise exception """
			with io.open(filepath, 'r') as fh:
				file_dict = json.load(fh)
			self.cfg_dict.update(file_dict)

		return self.cfg_dict

	def load_using_json_format_implicitly(self):

		self.cfg_dict = {}
		default_filepath = "{}/{}.{}".format(self.confdir, 
			'default', self.file_extension)

		try:
			with io.open(default_filepath, 'r') as fh:
				default_dict = json.load(fh)
			self.cfg_dict.update(default_dict)
		except Exception, e:
			pass

		if "PY_ENV" in os.environ:
			env_filepath = "{}/{}.{}".format(self.confdir,
				os.environ['PY_ENV'], self.file_extension)
			try:
				with io.open(env_filepath, 'r') as fh:
					env_dict = json.load(fh)
				self.cfg_dict.update(env_dict)
			except Exception, e:
				pass

		local_filepath = "{}/{}.{}".format(self.confdir,
			'local', self.file_extension)

		try:
			with io.open(local_filepath, 'r') as fh:
				local_dict = json.load(fh)
			self.cfg_dict.update(local_dict)
		except Exception, e:
			pass

		return self.cfg_dict

	def load_using_yaml_format_explicitly(self):

		self.cfg_dict = {}
		for filepath in self.filepaths:
			""" with explicit loading, let file not found raise exception """
			with io.open(filepath, 'r') as fh:
				file_dict = yaml.load(fh)
			self.cfg_dict.update(file_dict)

		return self.cfg_dict

	def load_using_yaml_format_implicitly(self):

		self.cfg_dict = {}
		default_filepath = "{}/{}.{}".format(self.confdir, 
			'default', self.file_extension)

		try:
			with io.open(default_filepath, 'r') as fh:
				default_dict = yaml.load(fh)
			self.cfg_dict.update(default_dict)
		except Exception, e:
			pass

		if "PY_ENV" in os.environ:
			env_filepath = "{}/{}.{}".format(self.confdir,
				os.environ['PY_ENV'], self.file_extension)
			try:
				with io.open(env_filepath, 'r') as fh:
					env_dict = yaml.load(fh)
				self.cfg_dict.update(env_dict)
			except Exception, e:
				pass

		local_filepath = "{}/{}.{}".format(self.confdir,
			'local', self.file_extension)

		try:
			with io.open(local_filepath, 'r') as fh:
				local_dict = yaml.load(fh)
			self.cfg_dict.update(local_dict)
		except Exception, e:
			pass

		return self.cfg_dict

	def load(self):

		"""
		this is a glorified switch/case
		"""
		if self.format == FMT_INI:
			if self.filepaths:
				return self.load_using_ini_format_explicitly()
			return self.load_using_ini_format_implicitly()

		elif self.format == FMT_DELIMITED:
			if self.filepaths:
				return self.load_using_delimited_format_explicitly()
			raise ValueError('Implicit mode is not supported with FMT_DELIMITED')

		elif self.format == FMT_XML:
			if self.filepaths:
				return self.load_using_xml_format_explicitly()
			return self.load_using_xml_format_implicitly()

		elif self.format == FMT_JSON:
			if self.filepaths:
				return self.load_using_json_format_explicitly()
			return self.load_using_json_format_implicitly()

		elif self.format == FMT_YAML:
			if self.filepaths:
				return self.load_using_yaml_format_explicitly()
			return self.load_using_yaml_format_implicitly()

		else:
			raise ValueError('invalid config format: {}'.format(self.format))

		return None

	def get_config(self):

		return self.cfg_dict

class Cfg(CfgPy):

	def __init__(self, format_specifier, confdir, filepaths=None):

		CfgPy.__init__(self, format_specifier, confdir, filepaths)

		
if __name__ == "__main__":

	pp = pprint.PrettyPrinter(indent=4)

	"""
	# verify json implicit loading
	json_implicit_config_object = CfgPy(FMT_JSON, '.', None)

	json_implicit_config = json_implicit_config_object.load()
	pp.pprint(json_implicit_config)

	# verify json explicit loading 
	json_explicit_config_object = CfgPy(
		FMT_JSON, 
		'.', 
		['./one.json','./two.json', './three.json']
		)

	json_explicit_config = json_explicit_config_object.load()
	pp.pprint(json_explicit_config)

	# verify yaml implicit loading 
	yaml_implicit_config_object = CfgPy(FMT_YAML, '.', None)

	yaml_implicit_config = yaml_implicit_config_object.load()
	pp.pprint(yaml_implicit_config)

	# verify yaml explicit loading
	yaml_explicit_config_object = CfgPy(
		FMT_YAML, 
		'.', 
		['./one.yml','./two.yml', './three.yml']
		)

	yaml_explicit_config = yaml_explicit_config_object.load()
	pp.pprint(yaml_explicit_config)

	# verify xml implicit loading
	xml_implicit_config_object = CfgPy(FMT_XML, '.', None)

	xml_implicit_config = xml_implicit_config_object.load()
	pp.pprint(xml_implicit_config)

	# verify xml explicit loading 
	xml_explicit_config_object = CfgPy(
		FMT_XML, 
		'.', 
		['./one.xml','./two.xml', './three.xml']
		)

	xml_explicit_config = xml_explicit_config_object.load()
	pp.pprint(xml_explicit_config)

	# verify ini implicit loading
	ini_implicit_config_object = CfgPy(FMT_INI, '.', None)

	ini_implicit_config = ini_implicit_config_object.load()
	pp.pprint(ini_implicit_config)

	# verify ini explicit loading 
	ini_explicit_config_object = CfgPy(
		FMT_INI, 
		'.', 
		['./one.ini','./two.ini', './three.ini']
		)

	ini_explicit_config = ini_explicit_config_object.load()
	pp.pprint(ini_explicit_config)


	# verify delimtxt implicit loading
	delimtxt_implicit_config_object = CfgPy(FMT_DELIMITED, '.', None)

	delimtxt_implicit_config = delimtxt_implicit_config_object.load()
	pp.pprint(delimtxt_implicit_config)


	# verify delimtxt explicit loading 
	delimtxt_explicit_config_object = CfgPy(
		FMT_DELIMITED, 
		'.', 
		['./one']
		)
	delimtxt_explicit_config_object.set_delimiter(':')
	delimtxt_explicit_config_object.set_delimited_file_column_names(['host','port','db','user','password'])
	delimtxt_explicit_config = delimtxt_explicit_config_object.load()
	pp.pprint(delimtxt_explicit_config)
	"""

	delimtxt_explicit_config_object = CfgPy(
		FMT_DELIMITED, 
		'.',
		['./two']
		)
	delimtxt_explicit_config_object.set_delimiter(' ')
	delimtxt_explicit_config_object.set_delimited_file_column_names(['host','port','db','user','password'])
	delimtxt_explicit_config = delimtxt_explicit_config_object.load()
	pp.pprint(delimtxt_explicit_config)
