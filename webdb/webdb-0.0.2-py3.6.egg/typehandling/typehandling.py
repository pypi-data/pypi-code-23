"""
Provides functions for converting types that are returned by the 
backend (for instance pymysql) to types that can be sent to the
client. 
"""
from .date_and_time import DateAdapter, TimeAdapter, DatetimeAdapter, ConversionException
from datetime import date, time, datetime



conversions_dict = {"date": DateAdapter.from_dict,
			"time": TimeAdapter.from_dict,
			"datetime": DatetimeAdapter.from_dict}

def handle_type(value):
	"""
	Handle types coming from the client, convert the values
	in an appropiate manner and return them.

	raises ConversionException on failure.
	"""
	if(isinstance(value, (str, int, float, bool, bytes))):
		return value
	if(isinstance(value, dict)):
		if(not "__type__" in value):
			raise ConversionException("missing __type__")
		if(not value["__type__"] in conversions_dict):
			raise ConversionException("unknow type: {}".format(value["__type__"]))
		return conversions_dict[value["__type__"]](value)
	raise ConversionException("Unsupported type: {}".format(type(value)))


def handle_types(dct):
	"""
	Handles all types in a dict. Uses ``handle_type`` internally.
	"""
	return {k: handle_type(v) for k,v in dct.items()}


def reverse_handle_type(value):
	"""
	Handles types coming from a client.
	"""
	if(isinstance(value, (str, int, float, bool, bytes))):
		return value
	if(isinstance(value, datetime)):
		return DatetimeAdapter.copy(value)
	if(isinstance(value, time)):
		return TimeAdapter.copy(value)
	if(isinstance(value, date)):
		return DateAdapter.copy(value)

