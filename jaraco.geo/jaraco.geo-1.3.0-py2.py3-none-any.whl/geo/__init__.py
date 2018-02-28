# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re

import six
from six.moves import filter

from jaraco.collections import dict_map


def split_sign(value):
	"""
	>>> split_sign(-5)
	(-1, 5)
	>>> split_sign(5)
	(1, 5)
	"""
	sign = [1, -1][value < 0]
	return sign, value * sign


def sign_string(sign):
	return ['', '-'][sign < 0]


def test_encoding():
	"""
	In some of the early implementations, I ran into encoding problems
	so I include this as a sanity check of encoding various characters
	used in DMS objects.

	>>> test_encoding()
	"""
	sample1 = ''' 38\u00b055'14.46"N'''
	assert sample1[3] == '\u00b0'
	sample2 = ''' 38°55'14.46"N'''
	assert sample2 == sample1


class DMS(object):
	"""
	DMS - Degrees Minutes Seconds
	A class for parsing and manipulating polar coordinates in degrees,
	either as DMS or as decimal degrees (DD)

	>>> lat = DMS('-34.383333333')
	>>> float(lat) == -34.383333333
	True
	>>> value, sign = lat.DMS
	>>> value[0]
	34
	>>> value[1]
	23

	Test to make sure we can recognize a DD with no leading zero
	>>> dms, sign = DMS('.616667').DMS
	>>> dms[1] == 37
	True

	Test a location taken from Google Earth
	>>> dms = DMS(''' 38\u00b055'14.46"N''')

	If you're using a degree symbol, you need to be sure it's
	properly encoded.  This will depend on what your file or
	shell encoding are.
	>>> dms = DMS(''' 38°55'14.46"N''')

	DMS can also be instantiated from a float.
	>>> dms = DMS(35.4)

	"""
	pattern_definitions = [
		# This pattern matches the DMS string that assumes little formatting.
		#  The numbers are bunched together, and it is assumed that the minutes
		#  and seconds are two digits each.
		"""
		(-)?			# optional negative sign
		(?P<deg>\d+)	# number of degrees (saved as 'deg')
		(?P<min>\d{2})	# number of minutes (saved as 'min')
		(?P<sec>\d{2})	# number of seconds (saved as 'sec')
		\s*				# optional whitespace
		([NSEW])?		# optional directional specifier
		$				# end of string
		""",
		# This pattern attempts to match all other possible specifications of
		#  DMS entry.
		u"""
		(-)?			# optional negative sign
		(?P<deg>\d+		# number of degrees (saved as 'deg')
			(\.\d+)?	# optional fractional number of degrees (not saved separately)
			|			# OR
			\.\d+		# fractional number of degrees with implicit 0 degrees
		)				# all saved as 'deg'
		\s*				# optional whitespace
		(?:(°|deg))?	# optionally a degrees symbol or the word 'deg' (not saved)
		(?:				# begin optional minutes and seconds
			\s*?			# optional whitespace (matched minimally)
			[,]?			# optional comma or space (as a delimiter)
			\s*				# optional whitespace
			(?P<min>\d+)	# number of minutes (saved as 'min')
			\s*				# optional whitespace
			(?:('|min))?	# optionally a minutes symbol or the word 'min' (not saved)
			\s*?			# optional whitespace (matched minimally)
			[,]?			# optional comma or space (as a delimiter)
			(?:			# begin optional seconds
				\s*				# optional whitespace
				(?P<sec>\d+		# number of seconds
					(?:\.\d+)?	# optional fractional number of seconds (not saved separately)
				)				# (all saved as 'sec')
				\s*				# optional whitespace
				(?:("|sec))?	# optionally a minutes symbol or the word 'sec' (not saved)
			)?				# end optional seconds
		)?				# end optional minutes and seconds
		\s*				# optional whitespace
		([NSEW])?		# optional directional specifier
		$				# end of string
		"""
	]
	patterns = [
		re.compile(defn, re.IGNORECASE | re.VERBOSE)
		for defn in pattern_definitions]

	def __init__(self, dms_string=None):
		if dms_string is not None:
			self.DMS = six.text_type(dms_string).strip()

	def __float__(self):
		return self.dd

	def __unicode__(self):
		value, sign = self.DMS
		sign = sign_string(sign)
		return u'''{0:s}{1:d}° {2:d}' {3:f}"'''.format(sign, *value)

	@staticmethod
	def dd_to_dms(dd):
		"""
		Convert from degrees in decimal to degrees, minutes, seconds.

		>>> DMS.dd_to_dms(35.2)
		((35, 12, 1.0231815394945443e-11), 1)

		>>> DMS.dd_to_dms(-273.9)
		((273, 54, -8.185452315956354e-11), -1)

		>>> DMS.dd_to_dms(-273.90236461982337)
		((273, 54, 8.512631364042136), -1)
		"""
		sign, dd = split_sign(dd)

		def int_round(v):
			return int(round(v, 2))
		deg = int_round(dd)
		fracMin = (dd - deg) * 60
		min = int_round(fracMin)
		sec = (fracMin - min) * 60
		return (deg, min, sec), sign

	@staticmethod
	def dms_to_dd(dms):
		"""
		Convert DMS string to DD

		>>> DMS.dms_to_dd('334259')
		33.71638888888889
		>>> DMS.dms_to_dd('35deg 42min 20sec E')
		35.705555555555556
		"""
		matches = [pattern.match(dms) for pattern in DMS.patterns]
		matches = filter(None, matches)
		try:
			best_match = next(matches)
		except StopIteration:
			raise ValueError(u'String %s did not match any DMS pattern' % dms)
		return DMS._get_dd_from_match(best_match)

	def set_DMS(self, dms_string):
		self.dd = self.dms_to_dd(dms_string)

	def get_DMS(self):
		return self.dd_to_dms(self.dd)

	DMS = property(get_DMS, set_DMS)

	@staticmethod
	def _get_dd_from_match(dms_match):
		# get the negative sign
		is_negative = bool(dms_match.group(1))
		# get SW direction
		is_south_or_west = (
			bool(dms_match.groups()[-1]) and
			dms_match.groups()[-1].lower() in ('s', 'w')
		)
		d = dms_match.groupdict()
		# set min & sec to zero if they weren't matched
		if d['min'] is None:
			d['min'] = 0
		if d['sec'] is None:
			d['sec'] = 0
		# get the DMS and convert each to float
		d = dict_map(float, d)
		# convert the result to decimal format
		result = d['deg'] + d['min'] / 60 + d['sec'] / 3600
		if is_negative ^ is_south_or_west:
			result = -result
		# validate the result
		if not (
			0 <= d['deg'] < 360 and
			0 <= d['min'] < 60 and
			0 <= d['sec'] < 60 and
			result >= -180):
				fmt = """DMS not given in valid range ({deg:f}°{min:f}'{sec:f}")."""
				msg = fmt.format(**d)
				raise ValueError(msg)
		return result
