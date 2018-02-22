"""
This module provides classes that can be used to handle date/time/datetime
objects with the JSON api. All adapters inherite from the coresponding 
datetime class and add the ``from_dict`` staticmethod and the ``to_dict`` 
method.
"""

import datetime


class ConversionException(Exception): 
	pass

class DateAdapter(datetime.date):
	"""
	Subclass of datetime.date.
	"""
	def __new__(cls, *args, **kwargs):
		return datetime.date.__new__(cls, *args, **kwargs)

	@staticmethod
	def from_dict(dct):
		if(not "__type__" in dct):
			raise ConversionException("missing __type__")
		if(dct["__type__"] != "date"):
			raise ConversionException("wrong type: {}".format(dct["__type__"]))
		
		my_dct = {"year": 0, "month": 1, "day": 1}
		my_dct.update(dct)

		return DateAdapter(my_dct["year"], my_dct["month"], my_dct["day"])

	def to_dict(self):
		return {"__type__": "date", 
			"year": self.year,
			"month": self.month,
			"day": self.day}
	@staticmethod
	def copy(self, date):
		"""
		Copy a date instance and construct a new DateAdapter.
		"""
		return DateAdapter(date.year, date.month, date.day)

class DatetimeAdapter(datetime.datetime):
	"""
	Subclass of datetime.datetime.
	"""
	def __new__(cls, *args, **kwargs):
		return datetime.datetime.__new__(cls, *args, **kwargs)

	@staticmethod
	def from_dict(dct):
		if(not "__type__" in dct):
			raise ConversionException("missing __type__")
		if(dct["__type__"] != "datetime"):
			raise ConversionException("wrong type: {}".format(dct["__type__"]))
		
		my_dct = {"year": 0, "month": 1, "day": 1,
			"hour": 0, "minute": 0, "second": 0,
			"microsecond": 0, "utcoffset": 0}
		my_dct.update(dct)

		return DatetimeAdapter(my_dct["year"], 
				my_dct["month"], 
				my_dct["day"],
				my_dct["hour"], 
				my_dct["minute"], 
				my_dct["second"], 
				my_dct["microsecond"],
				datetime.timezone(
					datetime.timedelta(
						minutes = my_dct["utcoffset"]
						)
					)
				)


	def to_dict(self):
		return {"__type__": "datetime", 
			"year": self.year,
			"month": self.month,
			"day": self.day,
			"hour": self.hour,
			"minute": self.minute,
			"second": self.second,
			"microsecond": self.microsecond,
			"utcoffset": self.tzinfo.utcoffset(None).seconds // 60 if self.tzinfo else 0
			}
	@staticmethod
	def copy(self, datetime):
		"""
		Copy a datetime instance and create a new DatetimeAdapter.
		"""
		return DatetimeAdapter(datetime.year,
				datetime.month,
				datetime.day,
				datetime.hour,
				datetime.minute,
				datetime.second,
				datetime.microsecond,
				datetime.tzinfo)

class TimeAdapter(datetime.time):
	"""
	Subclass of datetime.time.
	"""
	def __new__(cls, *args, **kwargs):
		return datetime.time.__new__(cls, *args, **kwargs)

	@staticmethod
	def from_dict(dct):
		if(not "__type__" in dct):
			raise ConversionException("missing __type__")
		if(dct["__type__"] != "time"):
			raise ConversionException("wrong type: {}".format(dct["__type__"]))
		
		my_dct = {"hour": 0, "minute": 0, "second": 0, "microsecond": 0, "utcoffset": 0}
		my_dct.update(dct)

		return TimeAdapter(my_dct["hour"], 
				my_dct["minute"], 
				my_dct["second"], 
				my_dct["microsecond"],
				datetime.timezone(
					datetime.timedelta(
						minutes = my_dct["utcoffset"]
						)
					)
				)

	def to_dict(self):
		return {"__type__": "time", 
			"hour": self.hour,
			"minute": self.minute,
			"second": self.second,
			"microsecond": self.microsecond,
			"utcoffset": self.tzinfo.utcoffset(None).seconds // 60 if self.tzinfo else 0
			}

	@staticmethod
	def copy(self, time):
		"""
		Copy a time instance and create a new TimeAdapter.
		"""
		return TimeAdapter(time.hour,
				time.minute,
				time.second,
				time.microsecond,
				time.tzinfo)
