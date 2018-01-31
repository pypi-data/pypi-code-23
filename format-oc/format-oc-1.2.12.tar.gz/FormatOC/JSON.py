# coding=utf-8
""" JSON

Extra module to help convert to and from JSON with complicated types like
datetime and decimal
"""

__author__		= "Chris Nasr"
__copyright__	= "OuroborosCoding"
__license__		= "Apache"
__version__		= "1.0.0"
__maintainer__	= "Chris Nasr"
__email__		= "ouroboroscode@gmail.com"

# Import python core modules
import json
from datetime import datetime
from decimal import Decimal

# Byteify
def _byteify(input):
	"""Byteify

	Turns unicode strings into utf-8

	Args:
		o (mixed): The object or string to byteify

	Return:
		mixed
	"""

	# If we were passed a dictionary
	if isinstance(input, dict):
		return {_byteify(key):_byteify(value) for key,value in input.iteritems()}

	# Else if we were passed a list
	elif isinstance(input, list):
		return [_byteify(element) for element in input]

	# Else if we have a unicode string
	elif isinstance(input, unicode):
		return input.encode('utf-8')

	# Else, return as is
	else:
		return input

# Encode
def encode(o):
	"""Encode

	Handles encoding objects/values into JSON, returns the JSON as a string

	Args:
		o (mixed): The object or value to encode

	Returns:
		str
	"""
	return json.dumps(o, cls=CEncoder)

# EncodeF
def encodef(o, f):
	"""EncodeF

	Handles encoding objects/values into JSON and stores them in the given file

	Args:
		o (mixed): The object or value to encode
		f (fp): An open file pointer which can be written to

	Returns:
		None
	"""
	return json.dump(o, f, cls=CEncoder)

# Decode
def decode(s):
	"""Decode

	Handles decoding JSON, as a string, into objects/values

	Args:
		s (str): The JSON to decode

	Returns:
		mixed
	"""
	oJSON	= json.loads(s, parse_float=Decimal, encoding='utf-8')
	return _byteify(oJSON)

# DecodeF
def decodef(f):
	"""DecodeF

	Handles decoding JSON, from a file, into objects/values

	Args:
		f (fp): An open file pointer that can be read

	Returns:
		mixed
	"""
	oJSON	= json.load(f, parse_float=Decimal, encoding='utf-8')
	return _byteify(oJSON)

# Encoder
class CEncoder(json.JSONEncoder):
	"""Encode

	Handles encoding types the default JSON encoder can't handle

	Extends: json.JSONEncoder
	"""

	# Default
	def default(self, obj):
		"""Default

		Called when the regular Encoder can't figure out what to do with the type

		Args:
			self (CEncoder): A pointer to the current instance
			obj (mixed): An unknown object that needs to be encoded

		Returns:
			str: A valid JSON string representing the object
		"""

		# If we have a datetime object
		if isinstance(obj, datetime):
			return obj.strftime('%Y-%m-%d %H:%M:%S')

		# Else if we have a decimal object
		elif isinstance(obj, Decimal):
			return '{0:f}'.format(obj)

		# Bubble back up to the parent default
		return json.JSONEncoder.default(self, obj)
