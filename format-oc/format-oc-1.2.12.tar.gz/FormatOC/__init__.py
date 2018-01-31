# coding=utf-8
""" FormatOC Package

Exports several classes used to represent documents and their nodes
"""

__author__		= "Chris Nasr"
__copyright__	= "OuroborosCoding"
__license__		= "Apache"
__version__		= "1.2.0"
__maintainer__	= "Chris Nasr"
__email__		= "ouroboroscode@gmail.com"

# Import python core modules
import abc
import datetime
from decimal import Decimal, InvalidOperation as DecimalInvalid
import hashlib
import re
import sys

# Import local modules
import JSON

## Hash Field
#
# Holds a regex to match dynamic hash elements
#
# @var _sre.SRE_Pattern
_hashField		= re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_]*$')

## Special Fields
#
# Holds a regex to match special hash elements
#
# @var _sre.SRE_Pattern
_specialSyntax	= r'[a-z0-9_-]+'
_specialName	= re.compile(r'^' + _specialSyntax + r'$')
_specialKey		= re.compile(r'^__(' + _specialSyntax + r')__$')
_specialSet		= '__%s__'

## Standard Field
#
# Holds a regex to match any standard named fields. These are limited in order
# to ease the ability to plugin additional data stores
#
# @var _sre.SRE_Pattern
_standardField	= re.compile(r'^_?[a-zA-Z][a-zA-Z0-9_]*$')

## Type to regex
#
# Holds a hash of type values to the regular expression used to validate them
#
# @var dict
_typeToRegex	= {
	'base64':	re.compile(r'^(?:[A-Za-z0-9+/]{4})+(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'),
	'date':		re.compile(r'^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$'),
	'datetime':	re.compile(r'^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01]) (?:[01]\d|2[0-3])(?::[0-5]\d){2}$'),
	'int':		re.compile(r'^(?:0|[+-]?[1-9]\d*|0x[0-9a-f]+|0[0-7]+)$'),
	'ip':		re.compile(r'^(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])){2}\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])$'),
	'md5':		re.compile(r'^[a-fA-F0-9]{32}$'),
	'price':	re.compile(r'^-?(?:[1-9]\d+|\d)(?:\.\d{1,2})?$'),
	'time':		re.compile(r'^(?:[01]\d|2[0-3])(?::[0-5]\d){2}$'),
	'uuid':		re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}$')
}

# There is no way to access the real type of compiled regular expressions or md5
#	hashes so unfortunately we have to do this ugly hack
_REGEX_TYPE	= type(_typeToRegex['date'])
_MD5_TYPE	= type(hashlib.md5('hack'))

## Node Interface
#
# All Node instances must be built off of this one
#
# @name _NodeInterface
# @extends object
class _NodeInterface(object):
	__metaclass__	= abc.ABCMeta

	## representation (__repr__)
	#
	# Returns a string representation of the instance
	#
	# @name __repr__
	# @param _BasicNode self			A pointer to the current instance
	# @return str
	def __repr__(self):
		return str(self.toDict())

	## Clean
	#
	# As validation allows for strings representing non-string values, it is
	# useful to be able to "clean" a value and turn it into the value it was
	# representing, making sure that data in data stores is real and not
	# representitive
	#
	# @name clean
	# @abstract
	# @param _BasicNode self			A pointer to the current instance
	# @param mixed value				The value to clean
	# @return mixed
	@abc.abstractmethod
	def clean(self, value):
		pass

	## To Dictionary
	#
	# Returns the basic node as a dictionary in the same format as is used in
	# constructing it
	#
	# @name toDict
	# @abstract
	# @param _BasicNode self			A pointer to the current instance
	# @return dict
	@abc.abstractmethod
	def toDict(self):
		pass

	## To JSON
	#
	# Returns a JSON string representation of the instance
	#
	# @name toJSON
	# @param _BasicNode self			A pointer to the current instance
	# @return str
	def toJSON(self):
		return JSON.encode(self.toDict())

	## From File
	#
	# Loads a JSON file and creates a Tree instance from it
	#
	# @name fromFile
	# @static
	# @throws ValueError
	# @param object cls					The class associated with the call
	# @param str filename				The name of the file to load
	# @param bool override				Used for special override sequences
	# @return dict
	@classmethod
	def fromFile(cls, filename, override=False):

		# Load the file
		oFile	= open(filename)

		# Convert it to a dictionary
		dDetails	= JSON.decodef(oFile)

		# Call fromDicts and return it
		return cls(dDetails)

	## Valid
	#
	# Checks if a value is valid based on the instance's values
	#
	# @name valid
	# @abstract
	# @param _BasicNode self			A pointer to the current instance
	# @param mixed value				The value to validate
	# @return bool
	@abc.abstractmethod
	def valid(self, value):
		pass

## Basic Node
#
# Represents shared functionality amongst Nodes and Parents
#
# @name _BasicNode
# @extends _NodeInterface
class _BasicNode(_NodeInterface):

	## Constructor
	#
	# Initialises the instance
	#
	# @name __init__
	# @param _BasicNode self			A pointer to the new instance
	# @param dict details				Details describing the type of values allowed for the node
	# @return _BasicNode
	def __init__(self, details):

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details in ' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + ' must be a dict')

		# Init the variables used to identify the last falure in validation
		self.validation_fail_name	= ''
		self.validation_fail_value	= None

		# Init the optional flag, assume all nodes are necessary
		self._optional	= False

		# If the details contains an optional flag
		if '__optional__' in details:

			# If it's a valid bool, store it
			if isinstance(details['__optional__'], bool):
				self._optional	= details['__optional__']

			# Else, write a warning to stderr
			else:
				sys.stderr.write('"' + str(details['__optional__']) + '" is not a valid value for __optional__, assuming false')

			# Remove it from details
			del details['__optional__']

		# Init the special dict
		self._special	= {}

		# If there are any other special fields in the details
		for k in details.keys():

			# If key is special
			oMatch	= _specialKey.match(k)
			if oMatch:

				# Store it with the other specials then remove it
				self._special[oMatch.group(1)]	= details[k]
				del details[k]

	def special(self, name, value=None, default=None):
		"""Special

		Getter/Setter method for special values associated with nodes that are
		not fields

		To retrieve a value or values, pass only the name or names, to set a
		single special value, pass a name and value

		Args:
			name (str): The name of the value to either set or get
			value (mixed): The value to set
				Must be something that can be converted directly to JSON
			default (mixed): The default value
				Returned if the special field doesn't exist

		Returns:
			On getting, the value of the special field is returned. On setting,
			nothing is returned

		Raises:
			TypeError: If the name is not a valid string
			ValueError: If the name is invalid, or if setting and the value can
				not be converted to JSON
		"""

		# Check the name is a string
		if not isinstance(name, basestring):
			raise TypeError('name must be a string')

		# Check the name is valid
		if not _specialName.match(name):
			raise ValueError('special name must match "%s"' % _specialSyntax)

		# If the value is not set, this is a getter
		if value is None:

			# Return the value or the default
			try:				return self._special[name]
			except KeyError:	return default

		# Else, this is a setter
		else:

			# Can the value safely be turned into JSON
			try:
				JSON.encode(value)
			except TypeError:
				raise ValueError('value can not be encoded to JSON')

			# Save it
			self._special[name]	= value

	## To Dictionary
	#
	# Returns the basic node as a dictionary in the same format as is used in
	# constructing it
	#
	# @name toDict
	# @param _BasicNode self			A pointer to the current instance
	# @return dict
	def toDict(self):

		# Create the dict we will return
		dRet	= {}

		# If the optional flag is set
		if self._optional:
			dRet['__optional__']	= True

		# Add all the special fields found
		for k in self._special.keys():
			dRet[_specialSet % k]	= self._special[k]

		# Return
		return dRet

## Array Node
#
# Represents a node which is actually an array containing lists of another node
#
# @name ArrayNode
# @extends object
class ArrayNode(_BasicNode):

	## Valid Array
	#
	# Holds a list of valid values used to represent arrays types
	#
	# @name _VALID_ARRAY
	# @var str[]
	# @static
	_VALID_ARRAY	= ['unique', 'duplicates']

	## Constructor
	#
	# Initialises the instance
	#
	# @name __init__
	# @param ArrayNode self				A pointer to the new instance
	# @param dict details				Details describing the type of values allowed for the node
	# @return ArrayNode
	def __init__(self, details):

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details')

		# If the array config is not found
		if '__array__' not in details:
			raise KeyError('__array__')

		# If the value is not a dict
		if not isinstance(details['__array__'], dict):
			details['__array__']	= {
				"type":		details['__array__']
			}

		# If the type is missing
		if not 'type' in details['__array__']:
			self._type	= 'unique'
			sys.stderr.write('"type" of array is missing, assuming \'unique\'')

		# Or if the type is invalid
		elif details['__array__']['type'] not in self._VALID_ARRAY:
			self._type	= 'unique'
			sys.stderr.write('"' + str(details['__array__']['type']) + '" is not a valid type for __array__, assuming \'unique\'')

		# Else, store it
		else:
			self._type	= details['__array__']['type']

		# Init the value types
		self._minimum	= None
		self._maximum	= None

		# If there's a minimum or maximum present
		if 'minimum' in details['__array__'] \
			or 'maximum' in details['__array__']:
			self.minmax(
				('minimum' in details['__array__'] and details['__array__']['minimum'] or None),
				('maximum' in details['__array__'] and details['__array__']['maximum'] or None)
			)

		# If there's an optional flag somewhere in the mix
		if '__optional__' in details:
			sOptional	= details['__optional__']
			del details['__optional__']
		elif 'optional' in details['__array__']:
			sOptional	= details['__array__']['optional']
		else:
			sOptional	= None

		# Remove it from details
		del details['__array__']

		# Create the node that defines the array details
		if '__type__' in details:
			self._node	= Node(details)
		else:
			self._node	= Parent(details)

		# If we had an optional flag, add it for the parent constructor
		if sOptional:
			details['__optional__']	= sOptional

		# Call the parent constructor
		super(ArrayNode, self).__init__(details)

	## Min/Max
	#
	# Sets the minimum and/or maximum number of items for the Array
	#
	# @name __minmax
	# @raises ValueError
	# @param ArrayNode self				A pointer to the current instance
	# @param uint minimum				The minimum value
	# @param uint maximum				The maximum value
	# @return None
	def minmax(self, minimum=None, maximum=None):

		# If the minimum is set
		if minimum != None:

			# If the value is not a valid int or long
			if not isinstance(minimum, (int, long)):

				# If it's a valid representation of an integer
				if isinstance(minimum, basestring) \
					and _typeToRegex['int'].match(minimum):

					# Convert it
					minimum	= int(minimum, 0)

				# Else, raise an error
				else:
					raise ValueError('minimum')

			# If it's below zero
			if minimum < 0:
				raise ValueError('minimum')

			# Store the minimum
			self._minimum	= minumum

		# If the maximum is set
		if maximum != None:

			# If the value is not a valid int or long
			if not isinstance(maximum, (int, long)):

				# If it's a valid representation of an integer
				if isinstance(maximum, basestring) \
					and _typeToRegex['int'].match(maximum):

					# Convert it
					maximum	= int(maximum, 0)

				# Else, raise an error
				else:
					raise ValueError('minimum')

			# It's below zero
			if maximum < 0:
				raise ValueError('maximum')

			# If we also have a minimum and the max is somehow below it
			if self._minimum \
				and maximum < self._minimum:
				raise ValueError('maximum')

			# Store the maximum
			self._maximum	= maximum

	## Clean
	#
	# Goes through each of the values in the list, cleans it, stores it, and
	# returns a new list
	#
	# @name clean
	# @param ArrayNode self			A pointer to the current instance
	# @param list value				The value to validate
	# @return list
	def clean(self, value):

		# If the value is not a list
		if not isinstance(value, list):
			raise ValueError('value')

		# Recurse and return it
		return [self._node.clean(m) for m in value]

	## To Dictionary
	#
	# Returns the Array as a dictionary in the same format as is used in
	# constructing it
	#
	# @name toDict
	# @param ArrayNode self				A pointer to the current instance
	# @return dict
	def toDict(self):

		# Init the dictionary we will return
		dRet	= {}

		# If either a min or a max is set
		if self._minimum or self._maximum:

			# Set the array element as it's own dict
			dRet['__array__']	= {
				"type":	self._type
			}

			# If there is a minimum
			if self._minimum:
				dRet['__array__']['minimum']	= self._minimum

			# If there is a maximum
			if self._maximum:
				dRet['__array__']['maximum']	= self._maximum

		# Else, just add the type as the array element
		else:
			dRet['__array__']	= self._type

		# Get the parents dict and add it to the return
		dRet.update(super(ArrayNode,self).toDict())

		# Get the nodes dict and also add it to the return
		dRet.update(self._node.toDict())

		# Return
		return dRet

	## Valid
	#
	# Checks if a value is valid based on the instance's values
	#
	# @name valid
	# @param ArrayNode self				A pointer to the current instance
	# @param mixed value				The value to validate
	# @return bool
	def valid(self, value):

		# If the value isn't a list
		if not isinstance(value, list):
			self.validation_fail_value	= str(value)
			return False

		# Keep track of duplicates
		if self._type == 'unique':
			lItems	= []

		# Go through each item in the list
		for i in xrange(len(value)):

			# If the element isn't valid, return false
			if not self._node.valid(value[i]):
				self.validation_fail_name	= '[' + str(i) + ']' + self._node.validation_fail_name
				self.validation_fail_value	= self._node.validation_fail_value
				return False

			# If we need to check for duplicates
			if self._type == 'unique':

				# Try to get an existing item
				try:

					# If it is found, we have a duplicate
					iIndex	= lItems.index(value[i])

					# Add the error to the list
					self.validation_fail_name	= '[' + str(i) + ']'
					self.validation_fail_value	= 'duplicate of [' + str(iIndex) + ']'
					return False

				# If a Value Error is thrown, there is no duplicate, add the
				# 	value to the list and continue
				except ValueError:
					lItems.append(value[i])

		# Return ok
		return True

## Hash Node
#
# Handles objects similar to parents except where they keys are dynamic instead
# of static
#
# @name HashNode
# @extends _BasicNode
class HashNode(_BasicNode):

	## Constructor
	#
	# Initialises the instance
	#
	# @name __init__
	# @param HashNode self				A pointer to the new instance
	# @param dict details				Details describing the type of values allowed for the node
	# @return HashNode
	def __init__(self, details):

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details')

		# If the hash config is not found
		if '__hash__' not in details:
			raise KeyError('__hash__')

		# If there's an optional flag somewhere in the mix
		if '__optional__' in details:
			sOptional	= details['__optional__']
			del details['__optional__']
		else:
			sOptional	= None

		# Remove it from details
		del details['__hash__']

		# Create the node that defines the value part of the hash
		#	Does it have an array?
		if '__array__' in details:
			self._node	= ArrayNode(details)

		# Else does it have a type?
		elif '__type__' in details:
			self._node	= Node(details)

		# Else it's a Parent of a Parent
		else:
			self._node	= Parent(details)

		# If we had an optional flag, add it for the parent constructor
		if sOptional:
			details['__optional__']	= sOptional

		# Call the parent constructor
		super(HashNode, self).__init__(details)

	## Clean
	#
	# Makes sure both the key and value are properly stored in their correct
	# representation
	#
	# @name clean
	# @param HashNode self				A pointer to the current instance
	# @param mixed value				The value to clean
	# @return mixed
	def clean(self, value):

		# If the value is not a dict
		if not isinstance(value, dict):
			raise ValueError('value')

		# Recurse and return it
		return {str(k):self._node.clean(v) for k,v in value.iteritems()}

	## To Dictionary
	#
	# Returns the basic node as a dictionary in the same format as is used in
	# constructing it
	#
	# @name toDict
	# @param HashNode self				A pointer to the current instance
	# @return dict
	def toDict(self):

		# Init the dictionary we will return
		dRet	= {}

		# Add the hash flag
		dRet['__hash__']	= True

		# Get the parents dict and add it to the return
		dRet.update(super(HashNode,self).toDict())

		# Get the nodes dict and also add it to the return
		dRet.update(self._node.toDict())

		# Return
		return dRet

	## Valid
	#
	# Checks if a value is valid based on the instance's values
	#
	# @name valid
	# @param HashNode self				A pointer to the current instance
	# @param mixed value				The value to validate
	# @return bool
	def valid(self, value):

		# If the value isn't a dictionary
		if not isinstance(value, dict):
			self.validation_fail_value	= str(value)
			return False

		# Go through each key and value
		for k,v in value.iteritems():

			# If the key isn't valid
			if _hashField.match(str(k)) == None:
				self.validation_fail_name	= '.' + k
				self.validation_fail_value	= 'invalid key'
				return False

			# Check the value
			if not self._node.valid(v):
				self.validation_fail_name	= '.' + k + self._node.validation_fail_name
				self.validation_fail_value	= self._node.validation_fail_value
				return False

		# Keys and values have no issues
		return True

## Node
#
# Represents a single node of data, an immutable type like an int or a string
#
# @name Node
# @extends _BasicNode
class Node(_BasicNode):

	## Valid Types
	#
	# Holds a list of valid values used to represent Node types
	#
	# @name _VALID_TYPES
	# @var str[]
	# @static
	_VALID_TYPES	= ['any', 'base64', 'bool', 'date', 'datetime', 'decimal',
						'float', 'int', 'ip', 'json', 'md5', 'price', 'string',
						'time', 'timestamp', 'uint', 'uuid']

	## Compare IPs
	#
	# Compares two IPs and returns a status based on which is greater
	# If first is less than second: -1
	# If first is equal to second: 0
	# If first is greater than second: 1
	#
	# @name __compare_ips
	# @param string first				A string representing an IP address
	# @param string second				A string representing an IP address
	# @return int						-1, 0, 1
	@staticmethod
	def __compare_ips(first, second):

		# If the two IPs are the same, return 0
		if first == second:
			return 0

		# Create lists from the split of each IP, store them as ints
		lFirst	= [int(i) for i in first.split('.')]
		lSecond	= [int(i) for i in second.split('.')]

		# Go through each part from left to right until we find the
		# 	difference
		for i in [0, 1, 2, 3]:

			# If the part of x is greater than the part of y
			if lFirst[i] > lSecond[i]:
				return 1

			# Else if the part of x is less than the part of y
			elif lFirst[i] < lSecond[i]:
				return -1

	## Constructor
	#
	# Initialises the instance
	#
	# @name __init__
	# @raises KeyError, ValueError
	# @param Node self					A pointer to the new instance
	# @param dict details				Details describing the type of values allowed for this Node
	# @return Node
	def __init__(self, details):

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details')

		# If the type is not found or is invalid
		if '__type__' not in details or details['__type__'] not in self._VALID_TYPES:
			raise KeyError('__type__')

		# Store the type and remove it from the details
		self._type	= details['__type__']
		del details['__type__']

		# Init the value types
		self._regex		= None
		self._options	= None
		self._minimum	= None
		self._maximum	= None

		# If there's a regex string available
		if '__regex__' in details:
			self.__regex(details['__regex__'])
			del details['__regex__']

		# Else if there's a list of options
		elif '__options__' in details:
			self.__options(details['__options__'])
			del details['__options__']

		# Else
		else:

			# If there's a min or max
			bMin	= ('__minimum__' in details and True or False)
			bMax	= ('__maximum__' in details and True or False)

			if bMin or bMax:
				self.__minmax(
					(bMin and details['__minimum__'] or None),
					(bMax and details['__maximum__'] or None)
				)

			if bMin: del details['__minimum__']
			if bMax: del details['__maximum__']

		# Call the parent constructor
		super(Node, self).__init__(details)

	## Min/Max
	#
	# Sets the minimum and/or maximum values for the Node
	#
	# @name __minmax
	# @raises ValueError
	# @param Node self					A pointer to the current instance
	# @param mixed minimum				The minimum value
	# @param mixed maximum				The maximum value
	# @return None
	def __minmax(self, minimum=None, maximum=None):

		# If the minimum is set
		if minimum != None:

			# If the current type is a date, datetime, ip, or time
			if self._type in ['date', 'datetime', 'ip', 'time']:

				# Make sure the value is valid for the type
				if not isinstance(minimum, basestring) \
					or not _typeToRegex[self._type].match(minimum):
					raise ValueError('__minimum__')

			# Else if the type is an int (unsigned, timestamp), or a string in
			# 	which the min/max are lengths
			elif self._type in ['base64', 'int', 'string', 'timestamp', 'uint']:

				# If the value is not a valid int or long
				if not isinstance(minimum, (int, long)):

					# If it's a valid representation of an integer
					if isinstance(minimum, basestring) \
						and _typeToRegex['int'].match(minimum):

						# Convert it
						minimum	= int(minimum, 0)

					# Else, raise an error
					else:
						raise ValueError('__minimum__')

					# If the type is meant to be unsigned
					if self._type in ['base64', 'string', 'timestamp', 'uint']:

						# And it's below zero
						if minimum < 0:
							raise ValueError('__minimum__')

			# Else if the type is decimal
			elif self._type in ['decimal', 'price']:

				# Store it if it's valid, else throw a ValueError
				try:
					minimum	= Decimal(minimum)
				except ValueError:
					raise ValueError('__minimum__')

			# Else if the type is float
			elif self._type in ['float']:

				# Store it if it's valid, else throw a ValueError
				try:
					minimum	= float(minimum)
				except ValueError:
					raise ValueError('__minimum__')

			# Else we can't have a minimum
			else:
				sys.stderr.write('can not set __minimum__ for ' + self._type)
				return

			# Store the minimum
			self._minimum	= minimum

		# If the maximum is set
		if maximum != None:

			# If the current type is a date, datetime, ip, or time
			if self._type in ['date', 'datetime', 'ip', 'time']:

				# Make sure the value is valid for the type
				if not isinstance(maximum, basestring) \
					or not _typeToRegex[self._type].match(maximum):
					raise ValueError('__maximum__')

			# Else if the type is an int (unsigned, timestamp), or a string in
			# 	which the min/max are lengths
			elif self._type in ['base64', 'int', 'string', 'timestamp', 'uint']:

				# If the value is not a valid int or long
				if not isinstance(maximum, (int, long)):

					# If it's a valid representation of an integer
					if isinstance(maximum, basestring) \
						and _typeToRegex['int'].match(maximum):

						# Convert it
						maximum	= int(maximum, 0)

					# Else, raise an error
					else:
						raise ValueError('__minimum__')

					# If the type is meant to be unsigned
					if self._type in ['base64', 'string', 'timestamp', 'uint']:

						# And it's below zero
						if maximum < 0:
							raise ValueError('__maximum__')

			# Else if the type is decimal
			elif self._type in ['decimal', 'price']:

				# Store it if it's valid, else throw a ValueError
				try:
					maximum	= Decimal(maximum)
				except ValueError:
					raise ValueError('__maximum__')

			# Else if the type is float
			elif self._type in ['float']:

				# Store it if it's valid, else throw a ValueError
				try:
					minimum	= float(minimum)
				except ValueError:
					raise ValueError('__maximum__')

			# Else we can't have a maximum
			else:
				sys.stderr.write('can not set __maximum__ for ' + self._type)
				return

			# If we also have a minimum
			if self._minimum is not None:

				# If the type is an IP
				if self._type == 'ip':

					# If the min is above the max, we have a problem
					if self.__compare_ips(self._minimum, maximum) == 1:
						raise ValueError('__maximum__')

				# Else any other data type
				else:

					# If the min is above the max, we have a problem
					if self._minimum > maximum:
						raise ValueError('__maximum__')

			# Store the maximum
			self._maximum	= maximum

	## Options
	#
	# Sets the list of acceptable values for the Node
	#
	# @name __options
	# @raises ValueError
	# @param Node self					A pointer to the current instance
	# @param list options				A list of valid values
	# @return None
	def __options(self, options):

		# If the options are not a list
		if not isinstance(options, (list, tuple)):
			raise ValueError('__options__')

		# If the type is not one that can have options
		if self._type not in ['any', 'base64', 'date', 'datetime', 'decimal', \
								'float', 'int', 'ip', 'md5', 'price', 'string', \
								'time', 'timestamp', 'uint', 'uuid']:
			sys.stderr.write('can not set __options__ for ' + self._type)
			return

		# Init the list of options to be saved
		lOpts	= []

		# Go through each item and make sure it's unique and valid
		for i in xrange(len(options)):

			# Convert the value based on the type
			# 	If it's decimal
			if self._type in ['decimal', 'price']:

				try:
					options[i]	= Decimal(options[i])
				except ValueError:
					raise ValueError('options[' + str(i) + ']')

			# Else if it's a float
			elif self._type == 'float':

				try:
					options[i]	= float(options[i])
				except ValueError:
					raise ValueError('options[' + str(i) + ']')

			# Else if it's an integer
			elif self._type in ['int', 'timestamp', 'uint']:

				# If we don't already have an int
				if not isinstance(options[i], (int, long)):

					# And we don't have a string
					if not isinstance(options[i], basestring):
						raise ValueError('options[' + str(i) + ']')

					try:
						options[i]	= int(options[i], 0)
					except ValueError:
						raise ValueError('__options__[' + str(i) + ']')

				# If the type is unsigned and negative, raise an error
				if self._type in ['timestamp', 'uint'] and options[i] < 0:
					raise ValueError('options[' + str(i) + ']')

			# Else if the type is a string one that we can validate
			elif self._type in ['base64', 'date', 'datetime', 'ip', 'md5', 'time']:

				# If the value is not a string or doesn't match its regex, raise
				# 	an error
				if not isinstance(options[i], basestring) \
					or not _typeToRegex[self._type].match(options[i]):
					raise ValueError('__options__[' + str(i) + ']')

			# Else if the type is a string
			elif self._type == 'string':

				# If the value is not a string
				if not isinstance(options[i], basestring):

					# If the value can't be turned into a string
					try:
						options[i]	= str(options[i])
					except ValueError:
						raise ValueError('__options__[' + str(i) + ']')

			# If it's already in the list, raise an error
			if options[i] in lOpts:
				sys.stderr.write('__options__[' + str(i) + '] is a duplicate')

			# Store the option
			else:
				lOpts.append(options[i])

		# Store the list of options
		self._options	= lOpts

	## Regex
	#
	# Sets the regular expression used to validate the Node
	#
	# @name __regex
	# @raises ValueError
	# @param Node self					A pointer to the current instance
	# @param str regex					A standard regular expression string
	# @return None
	def __regex(self, regex):

		# If the type is not a string
		if self._type not in ['decimal', 'int', 'price', 'string', 'timestamp', 'uint']:
			sys.stderr.write('can not set __regex__ for ' + self._type)
			return

		# If it's not a valid string or regex
		if not isinstance(regex, (basestring, _REGEX_TYPE)):
			raise ValueError('__regex__')

		# Store the regex
		self._regex	= regex

	## Clean
	#
	# Cleans and returns the new value
	#
	# @name clean
	# @param Node self				A pointer to the current instance
	# @param mixed value			The value to validate
	# @return mixed
	def clean(self, value):

		# If it's an ANY, there is no reasonable expectation that we know what
		#	the value should be, so we return it as is
		if self._type == 'any':
			pass

		# Else if it's a basic string type
		elif self._type in ['base64', 'ip', 'string', 'uuid']:

			# And not already a string
			if not isinstance(value, basestring):
				value	= str(value)

		# Else if it's a BOOL just check if the value flags as positive
		elif self._type == 'bool':

			# If it's specifically a string, it needs to match a specific
			#	pattern to be true
			if isinstance(value, basestring):
				value	= (value in ('true', 'True', 'TRUE', 't', 'T', 'yes', 'Yes', 'YES', 'y', 'Y', 'x', '1') and True or False);

			# Else
			else:
				value	= (value and True or False)

		# Else if it's a date type
		elif self._type == 'date':

			# If it's a python type, use strftime on it
			if isinstance(value, (datetime.date, datetime.datetime)):
				value	= value.strftime('%Y-%m-%d')

			# Else if it's already a string
			elif isinstance(value, basestring):
				pass

			# Else convert it to a string
			else:
				value	= str(value)

		# Else if it's a datetime type
		elif self._type == 'datetime':

			# If it's a python type, use strftime on it
			if isinstance(value, datetime.datetime):
				value	= value.strftime('%Y-%m-%d %H:%M:%S')
			elif isinstance(value, datetime.date):
				value	= '%s 00:00:00' % value.strftime('%Y-%m-%d')

			# Else if it's already a string
			elif isinstance(value, basestring):
				pass

			# Else convert it to a string
			else:
				value	= str(value)

		# Else if it's a decimal
		elif self._type == 'decimal':
			value	= Decimal(value)

		# Else if it's a float
		elif self._type == 'float':
			value	= float(value)

		# Else if it's an int type
		elif self._type in ['int', 'timestamp', 'uint']:
			value	= int(value)

		# Else if it's a JSON type
		elif self._type == 'json':

			# If it's already a string
			if isinstance(value, basestring):
				pass

			# Else, encode it
			else:
				value	= JSON.encode(value)

		# Else if it's an md5 type
		elif self._type == 'md5':

			# If it's a python type, get the hexadecimal digest
			if isinstance(value, _MD5_TYPE):
				value	= value.hexdigest()

			# Else if it's a string
			elif isinstance(value, basestring):
				pass

			# Else, try to convert it to a string
			else:
				value	= str(value)

		# Else if it's a price type
		elif self._type == 'price':
			value	= "{0:f}".format(Decimal(value).quantize(Decimal('1.00')))

		# Else if it's a time type
		elif self._type == 'time':

			# If it's a python type, use strftime on it
			if isinstance(value, (datetime.time, datetime.datetime)):
				value	= value.strftime('%H:%M:%S')

			# Else if it's already a string
			elif isinstance(value, basestring):
				pass

			# Else convert it to a string
			else:
				value	= str(value)

		# Else we probably forgot to add a new type
		else:
			raise Exception('%s has not been added to .clean()' % self._type)

		# Return the cleaned value
		return value

	## To Dictionary
	#
	# Returns the Node as a dictionary in the same format as is used in
	# constructing it
	#
	# @name toDict
	# @param Node self					A pointer to the current instance
	# @return dict
	def toDict(self):

		# Init the dictionary we will return
		dRet	= {
			"__type__":	self._type
		}

		# If there is a regex associated, add it
		if self._regex:
			dRet['__regex__']	= str(self._regex)

		# Else if there were options associated, add them
		elif self._options:
			dRet['__options__']	= self._options

		# Else check for min and max and add if either are found
		else:
			if self._minimum:
				dRet['__minimum__']	= self._minimum
			if self._maximum:
				dRet['__maximum__']	= self._maximum

		# Get the parents dict and add it to the return
		dRet.update(super(Node,self).toDict())

		# Return
		return dRet

	## Valid
	#
	# Checks if a value is valid based on the instance's values
	#
	# @name valid
	# @param Node self					A pointer to the current instance
	# @param mixed value				The value to validate
	# @return bool
	def valid(self, value):

		# If we are validating an ANY field, immediately return true
		if self._type == 'any':

			# If there's a list of options
			if self._options:

				# Returns based on the option's existance
				if value not in self._options:
					self.validation_fail_value	= 'not in options'
					return False
				else:
					return True

			# Else, just return True
			return True

		# If we are validating a DATE, DATETIME, IP or TIME data point
		elif self._type in ['base64', 'date', 'datetime', 'ip', 'md5', 'time', 'uuid']:

			# If it's a date or datetime type and the value is a python type
			if self._type in ['date', 'datetime']	\
				and isinstance(value, (datetime.date, datetime.datetime)):
				return True

			# If it's a time type and the value is a python type
			elif self._type == 'time' \
				and isinstance(value, (datetime.time, datetime.datetime)):
				return True

			# Else if the type is md5 and the value is a python type
			elif self._type == 'md5' \
				and isinstance(value, _MD5_TYPE):
				return True

			# If the value is not a string
			if not isinstance(value, basestring):
				self.validation_fail_value	= 'not a string'
				return False

			# If there's no match
			if not _typeToRegex[self._type].match(value):
				self.validation_fail_value	= 'failed regex (internal)'
				return False

			# Else if there's a list of options
			elif self._options:

				# Returns based on the option's existance
				if value not in self._options:
					self.validation_fail_value	= 'not in options'
					return False
				else:
					return True

		# Else if we are validating some sort of integer
		elif self._type in ['int', 'timestamp', 'uint']:

			# If the type is a bool, fail immediately
			if type(value) == bool:
				self.validation_fail_value	= 'is a bool'
				return False

			# If it's not an int
			if not isinstance(value, (int, long)):

				# And it's a valid representation of an int
				if isinstance(value, basestring) \
					and _typeToRegex['int'].match(value):

					# Convert the value to an int
					value	= int(value, 0)

				# Else, return false
				else:
					self.validation_fail_value	= 'not an integer'
					return False

			# If it's not signed
			if self._type in ['timestamp', 'uint']:

				# If the value is below 0
				if value < 0:
					self.validation_fail_value	= 'signed'
					return False

			# If there is a regex
			if self._regex:

				# And it doesn't match the regex
				if re.match(self._regex, str(value)) == None:
					self.validation_fail_value	= 'failed regex (custom)'
					return False

			# If there's a list of options
			if self._options:

				# Returns based on the option's existance
				if value not in self._options:
					self.validation_fail_value	= 'not in options'
					return False
				else:
					return True

		# Else if we are validating a bool
		elif self._type == 'bool':

			# If it's already a bool
			if isinstance(value, bool):
				return True

			# If it's an int or long at 0 or 1
			if isinstance(value, (int, long)) and value in [0, 1, 1L]:
				return True

			# Else if it's a string
			elif isinstance(value, basestring):

				# If it's t, T, 1, f, F, or 0
				if value in ['true', 'True', 'TRUE', 't', 'T', '1', 'false', 'False', 'FALSE', 'f', 'F', '0']:
					return True
				else:
					self.validation_fail_value	= 'not a valid string representation of a bool'
					return False

			# Else it's no valid type
			else:
				self.validation_fail_value	= 'not valid bool replacement'
				return False

		# Else if we are validating a decimal value
		elif self._type == 'decimal':

			# If the type is a bool, fail immediately
			if type(value) == bool:
				self.validation_fail_value	= 'is a bool'
				return False

			# If we fail to convert the value
			try:
				value	= Decimal(value)
			except (DecimalInvalid, TypeError, ValueError):
				self.validation_fail_value	= 'can not be converted to decimal'
				return False

			# If there is a regex
			if self._regex:

				# And it doesn't match the regex
				if re.match(self._regex, str(value)) == None:
					self.validation_fail_value	= 'failed regex (custom)'
					return False

			# Else if there's a list of options
			elif self._options:

				# Returns based on the option's existance
				if value not in self._options:
					self.validation_fail_value	= 'not in options'
					return False
				else:
					return True

		# Else if we are validating a floating point value
		elif self._type == 'float':

			# If the type is a bool, fail immediately
			if type(value) == bool:
				self.validation_fail_value	= 'is a bool'
				return False

			# If we fail to convert the value
			try:
				value	= float(value)
			except (ValueError, TypeError):
				self.validation_fail_value	= 'can not be converted to float'
				return False

			# If there's a list of options
			if self._options:

				# Returns based on the option's existance
				if value not in self._options:
					self.validation_fail_value	= 'not in options'
					return False
				else:
					return True

		# Else if we are validating a JSON string
		elif self._type == 'json':

			# If it's already a string
			if isinstance(value, basestring):

				# Try to decode it
				try:
					value	= JSON.decode(value)
					return True
				except ValueError:
					self.validation_fail_value	= 'Can not be decoded from JSON'
					return False

			# Else
			else:

				# Try to encode it
				try:
					value= JSON.encode(value)
					return True
				except (ValueError, TypeError):
					self.validation_fail_value	= 'Can not be encoded to JSON'
					return False

		# Else if we are validating a price value
		elif self._type == 'price':

			# If the type is a bool, fail immediately
			if type(value) == bool:
				self.validation_fail_value	= 'is a bool'
				return False

			# If it's not a floating point value
			if not isinstance(value, Decimal):

				# But it is a valid string representing a price, or a float
				if isinstance(value, (basestring, float)) \
					and _typeToRegex['price'].match(str(value)):

					# Convert it to a decimal
					value	= Decimal(value).quantize(Decimal('1.00'))

				# Else if it's an int
				elif isinstance(value, int):

					# Convert it to decimal
					value	= Decimal(str(value) + '.00')

				# Else whatever it is is no good
				else:
					return False

			# Else
			else:

				# If the exponent is longer than 2
				if abs(value.as_tuple().exponent) > 2:
					return False

			# If there is a regex
			if self._regex:

				# And it doesn't match the regex
				if re.match(self._regex, str(value)) == None:
					self.validation_fail_value	= 'failed regex (custom)'
					return False

			# Else if there's a list of options
			elif self._options:

				# Returns based on the option's existance
				if value not in self._options:
					self.validation_fail_value	= 'not in options'
					return False
				else:
					return True

		# Else if we are validating a string value
		elif self._type == 'string':

			# If the value is not some form of string
			if not isinstance(value, basestring):
				self.validation_fail_value	= 'is not a string'
				return False

			# If we have a regex
			if self._regex:

				# If it doesn't match the regex
				if re.match(self._regex, value) == None:
					self.validation_fail_value	= 'failed regex (custom)'
					return False

			# If there's a list of options
			elif self._options:

				# Returns based on the option's existance
				if value not in self._options:
					self.validation_fail_value	= 'not in options'
					return False
				else:
					return True

			# Else
			else:

				# If there's a minimum length and we don't reach it
				if self._minimum and len(value) < self._minimum:
					self.validation_fail_value	= 'not long enough'
					return False

				# If there's a maximum length and we surpass it
				if self._maximum and len(value) > self._maximum:
					self.validation_fail_value	= 'too long'
					return False

			# Return ok
			return True

		# If there is a minimum value (for non bools and strings)
		if self._minimum:

			# If we are checking an IP
			if self._type == 'ip':

				# If the IP is less than the minimum
				if self.__compare_ips(value, self._minimum) == -1:
					self.validation_fail_value	= 'did not meet minimum'
					return False

			# Else
			else:

				# If the value is less than the minimum
				if value < self._minimum:
					self.validation_fail_value	= 'did not meet minimum'
					return False

		# If there is a maximum value (for non bools and strings)
		if self._maximum:

			# If we are checking an IP
			if self._type == 'ip':

				# If the IP is greater than the maximum
				if self.__compare_ips(value, self._maximum) == 1:
					self.validation_fail_value	= 'exceeds maximum'
					return False

			# Else
			else:

				# If the value is greater than the maximum
				if value > self._maximum:
					self.validation_fail_value	= 'exceeds maximum'
					return False

		# Value has no issues
		return True

## Options Node
#
# Represents a list of options available to a single hash key
#
# @name OptionsNode
# @extends _NodeInterface
class OptionsNode(_NodeInterface):

	## Constructor
	#
	# Initialises the instance of options for the hash key
	#
	# @name __init__
	# @raises TypeError
	# @param OptionsNode self			A pointer to the new instance
	# @param list details				The list of notes associated with the key
	# @return OptionsNode
	def __init__(self, details):

		# If details is not a dict instance
		if not isinstance(details, list):
			raise ValueError('details in ' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + ' must be a list')

		# Init the variables used to identify the last falure in validation
		self.validation_fail_name	= ''
		self.validation_fail_value	= None

		# Init the optional flag, assume all nodes are optional until we find one that isn't
		self._optional	= True

		# Init the internal list
		self._nodes	= []

		# Go through each element in the list
		for i in xrange(len(details)):

			# If the element is not a dict instance
			if not isinstance(details[i], dict):
				raise ValueError('details[' + str(i)  + '] in ' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + ' must be a dict')

			# Does it have an array?
			if '__array__' in details[i]:
				self._nodes.append(ArrayNode(details[i]))

			# Else does it have a type?
			elif '__type__' in details[i]:
				self._nodes.append(Node(details[i]))

			# Else it's a Parent of a Parent
			else:
				self._nodes.append(Parent(details[i]))

			# If the element is not optional, then the entire object can't be optional
			if not self._nodes[-1]._optional:
				self._optional = False

	## Clean
	#
	# Uses the valid method to check which type the value is, and then calls
	# the correct version of clean on that node
	#
	# @name clean
	# @raises ValueError
	# @param OptionsNode self			A pointer to the current instance
	# @param mixed value				The value to clean
	# @return mixed
	def clean(self, value):

		# Go through each of the nodes
		for i in xrange(len(self._nodes)):

			# If it's valid
			if self._nodes[i].valid(value):

				# Use it's clean
				return self._nodes[i].clean(value)

		# Something went wrong
		raise ValueError('value', value)

	## To Dictionary
	#
	# Returns the basic node as a list of dictionary elements in the same format
	# as is used in constructing it
	#
	# @name toDict
	# @param OptionsNode self			A pointer to the current instance
	# @return list
	def toDict(self):
		return [d.toDict() for d in self._nodes]

	## To JSON
	#
	# Returns a JSON string representation of the instance
	#
	# @name toJSON
	# @param OptionsNode self			A pointer to the current instance
	# @return str
	def toJSON(self):
		return JSON.encode(self.toDict())

	## Valid
	#
	# Checks if a value is valid based on the instance's values
	#
	# @name valid
	# @param OptionsNode self			A pointer to the current instance
	# @param mixed value				The value to validate
	# @return bool
	def valid(self, value):

		# Go through each of the nodes
		for i in xrange(len(self._nodes)):

			# If it's valid
			if self._nodes[i].valid(value):

				# Return OK
				return True

		# Not valid for anything
		self.validation_fail_name	= ''
		self.validation_fail_value	= 'no valid option'
		return False

## Parent
#
# Represents a hash of values what can themselves represent Parents of Nodes
#
# @name Parent
# @extends _BasicNode
class Parent(_BasicNode):

	## contains (__contains__)
	#
	# Returns whether a specific key exists in the parent
	#
	# @name __contains__
	# @param Parent self				A pointer to the current instance
	# @param str key					The key to check the existence of
	# @return bool
	def __contains__(self, key):
		return key in self._nodes

	## get item (__getitem__)
	#
	# Returns a specific key from the parent
	#
	# @name __getitem__
	# @param Parent self				A pointer to the current instance
	# @param str key					The key to get
	# @return _BasicNode
	def __getitem__(self, key):
		if key in self._nodes:	return self._nodes[key]
		else:					raise KeyError(key)

	## Constructor
	#
	# Initialises the instance by storing the record locally
	#
	# @name __init__
	# @raises ValueError
	# @param Parent self				A pointer to the new instance
	# @param dict details				Details describing the type of values allowed for this Parent
	# @return Parent
	def __init__(self, details):

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details in ' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + ' must be a dict')

		# Init the nodes and requires dicts
		self._nodes		= {}
		self._requires	= {}

		# Go through the keys in the details
		for k in details.keys():

			# If key is standard
			if _standardField.match(k):

				# If the key points to a list
				if isinstance(details[k], list):

					# Create a list of options for the key
					self._nodes[k]	= OptionsNode(details[k])

				# Else if the key points to a dictionary
				elif isinstance(details[k], dict):

					# Is it a dynamic hash
					if '__hash__' in details[k]:
						self._nodes[k]	= HashNode(details[k])

					# Else if it have an array?
					elif '__array__' in details[k]:
						self._nodes[k]	= ArrayNode(details[k])

					# Else does it have a type?
					elif '__type__' in details[k]:
						self._nodes[k]	= Node(details[k])

					# Else it's a Parent of a Parent
					else:
						self._nodes[k]	= Parent(details[k])

				# Else if the key points to a string
				elif isinstance(details[k], basestring):

					# Create a simple node with the type as the string
					self._nodes[k]	= Node({"__type__":details[k]})

				# Else raise an error
				else:
					raise TypeError('details[' + str(k) + ']')

				# Remove the key from the details
				del details[k]

		# If there's a require hash available
		if '__require__' in details:
			self.__require(details['__require__'])
			del details['__require__']

		# Call the parent constructor with whatever details are left
		super(Parent, self).__init__(details)


	## iterator (__iter__)
	#
	# Returns an iterator to the parent's keys
	#
	# @name __iter__
	# @param Parent self				A pointer to the current instance
	# @return dictionary-itemiterator
	def __iter__(self):
		return self._nodes.iterkeys()

	## Require
	#
	# Sets the require rules used to validate the Parent
	#
	# @name __require
	# @raises ValueError
	# @param Parent self				A pointer to the current instance
	# @param dict require				A dictionary expressing requirements of fields
	# @return None
	def __require(self, require):

		# If it's not a valid dict
		if not isinstance(require, dict):
			raise ValueError('__require__')

		# Go through each key and make sure it goes with a field
		for k,v in require.iteritems():

			# If the field doesn't exist
			if k not in self._nodes:
				raise ValueError('__require__[' + str(k) + ']')

			# If the value is a string
			if isinstance(v, basestring):
				v	= [v]

			# Else if it's not a list type
			elif not isinstance(v, (tuple,list)):
				raise ValueError('__require__[' + str(k) + ']')

			# Make sure each required field also exists
			for s in v:
				if s not in self._nodes:
					raise ValueError('__require__[' + str(k) + ']:' + str(v))

			# If it's all good
			self._requires[k]	= v

	## Clean
	#
	# Goes through each of the values in the dict, cleans it, stores it, and
	# returns a new dict
	#
	# @name clean
	# @param Parent self			A pointer to the current instance
	# @param dict value				The value to validate
	# @return dict
	def clean(self, value):

		# If the value is not a dict
		if not isinstance(value, dict):
			raise ValueError('value')

		# Init the return value
		dRet	= {}

		# Go through each value and clean it using the associated node
		for k in value.keys():
			try:
				dRet[k]	= self._nodes[k].clean(value[k])
			except KeyError:
				raise ValueError('%s is not a valid node in the parent' % k)

		# Return the cleaned values
		return dRet

	## Get
	#
	# Returns the node of a specific key from the parent
	#
	# @name get
	# @param Parent self				A pointer to the current instance
	# @param str key					The key to get
	# @param mixed default				Value to return if the key does not exist
	# @return _BasicNode
	def get(self, key, default=None):
		if key in self._nodes:	return self._nodes[key]
		else:					return default

	## Has Key
	#
	# Returns whether a specific key exists in the parent
	#
	# @name has_key
	# @param Parent self				A pointer to the current instance
	# @param str key					The key to check the existence of
	# @return bool
	def has_key(self, key):
		return key in self._nodes

	## Iterate Keys
	#
	# Returns an iterator to the parent's keys
	#
	# @name __iter__
	# @param Parent self				A pointer to the current instance
	# @return dictionary-keyiterator
	def iterkeys(self):
		return self._nodes.iterkeys()

	## Keys
	#
	# Returns a list of the node names in the parent
	#
	# @name keys
	# @param Parent self				A pointer to the current instance
	# @return list
	def keys(self):
		return self._nodes.keys()

	## To Dictionary
	#
	# Returns the Node as a dictionary in the same format as is used in
	# constructing it
	#
	# @name toDict
	# @param Node self					A pointer to the current instance
	# @return dict
	def toDict(self):

		# Get the parents dict as the starting point of our return
		dRet	= super(Parent,self).toDict()

		# Go through each field and add it to the return
		for k,v in self._nodes.iteritems():
			dRet[k]	= v.toDict()

		# Return
		return dRet

	## Valid
	#
	# Checks if the passed dict has the right values for this Parent
	#
	# @name valid
	# @param Parent self				A pointer to the current instance
	# @param dict value				The value to validate
	# @return bool
	def valid(self, value):

		# If the value isn't a dictionary
		if not isinstance(value, dict):
			self.validation_fail_value	= str(value)
			return False

		# Go through each node in the instance
		for k in self._nodes:

			# If we are missing a node
			if k not in value:

				# If the value is not optional
				if not self._nodes[k]._optional:
					self.validation_fail_name	= '.' + k + self._nodes[k].validation_fail_name
					self.validation_fail_value	= 'missing'
					return False

				# Else, just continue
				else:
					continue

			# If the element isn't valid, return false
			if not self._nodes[k].valid(value[k]):
				self.validation_fail_name	= '.' + k + self._nodes[k].validation_fail_name
				self.validation_fail_value	= self._nodes[k].validation_fail_value
				return False

			# If the element requires others
			if k in self._requires:

				# Go through each required field
				for f in self._requires[k]:

					# If the field doesn't exist in the value
					if f not in value or value[f] in ('0000-00-00','',None):
						self.validation_fail_name	= '.' + k + self._nodes[k].validation_fail_name
						self.validation_fail_value	= 'requires \'' + str(f) + '\' to also be set'
						return False

		# Return OK
		return True

	## View Keys
	#
	# Returns a view associated with the parent's keys
	#
	# @name viewkeys
	# @param Parent self				A pointer to the current instance
	# @return dict_keys
	def viewkeys(self):
		return self._nodes.viewkeys()

## Tree
#
# Represents the master parent of a record, holds special data to represent how
# the entire tree is stored
#
# @name Tree
# @extends Parent
class Tree(Parent):

	## Constructor
	#
	# Initialises the instance by storing the record locally
	#
	# @name __init__
	# @raises KeyError, ValueError
	# @param Tree self					A pointer to the new instance
	# @param dict details				Details describing the type of values allowed for this Parent
	# @return Tree
	def __init__(self, details):

		# If details is not a dict instance
		if not isinstance(details, dict):
			raise ValueError('details in ' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + ' must be a dict')

		# If the name is not set
		if '__name__' not in details:
			raise KeyError('__name__')

		# If the name is not valid
		if not _standardField.match(details['__name__']):
			raise ValueError('__name__')

		# Store the name then delete it
		self._name	= details['__name__']
		del details['__name__']

		# If for some reason the array flag is set, remove it
		if '__array__' in details:
			del details['__array__']

		# Call the parent constructor
		super(Tree, self).__init__(details)

	## To Dictionary
	#
	# Returns the Node as a dictionary in the same format as is used in
	# constructing it
	#
	# @name toDict
	# @param Node self					A pointer to the current instance
	# @return dict
	def toDict(self):

		# Init the dictionary we will return
		dRet	= {
			"__name__":	self._name
		}

		# Get the parents dict and add it to the return
		dRet.update(super(Tree,self).toDict())

		# Return
		return dRet

	## Valid
	#
	# Checks if the passed dict has the right values for this Parent
	#
	# @name valid
	# @param Parent self				A pointer to the current instance
	# @param dict value				The value to validate
	# @return bool
	def valid(self, value):

		# Call the parent valid method
		bValid	= super(Tree, self).valid(value)

		# If we failed
		if not bValid:
			self.validation_fail_name	= self._name + self.validation_fail_name

		# Return
		return bValid


