from datetime import date, datetime, timedelta
class DateIterator(object):
	'''
	This iterable makes it easy to walk between two dates, based on an
	interval specified in days.  In each iteration, the iterator yields
	a tuple giving the starting and ending date for that interval.

	Dates are input as Datetime.date or datetime.datetime objects, and 
	are output as datetime.date objects.

	To iterate over every day between two dates, provide the first and
	last day, and set the increment_by_days keyword argument to 1
	'''

	CHRONOLOGICAL = 1
	STATIONARY = 0
	REVERSE_CHRONOLOGICAL = -1

	def __init__(self, start, end, increment_by_days=1):

		# Register variables
		self.start = start
		self.end = end
		self.increment = increment_by_days 

		# ensure that start and end are date-like
		are_start_end_date_like = all([
			hasattr(start, 'year'),
			hasattr(start, 'month'),
			hasattr(start, 'day'),
			hasattr(end, 'year'),
			hasattr(end, 'month'),
			hasattr(end, 'day')
		])

		if not are_start_end_date_like:
			raise ValueError(
				'<start> and <end> should be like datetime.date '
				'or datetime.datetime.'
			)

		# what direction is this iterator moving in?
		if self.increment > 0:
			self.direction = self.CHRONOLOGICAL
		elif self.increment < 0:
			self.direction = self.REVERSE_CHRONOLOGICAL
		elif self.increment == 0:
			self.direction = self.STATIONARY

		# this is the difference between the first day and last day
		# within one date increment.  It is correctly 0 if increment
		# is either -1, 0, or 1.  
		# Generally 1 less than increment in magnitude
		self.span = self.direction * (abs(increment_by_days) - 1)

		# make sure that increment will move from start towards end
		if self.start > self.end and self.direction >= 0:
			raise ValueError(
				'If start date is after end date, the '
				'increment parameter should be positive.'
			)
		elif self.start < self.end and self.direction <=0:
			raise ValueError(
				'If start date is before end date, the '
				'increment parameter should be negative.'
			)

		self.pointer = start


	def __iter__(self):

		# the iterator is a fresh copy of this.
		# this means that one can instantiate multiple iterators from the
		# same DateIterator instance concurrently
		return self.__class__(self.start, self.end, self.increment)


	def next(self):

		# If we are alread passed the end date, stop iterating
		if self.pointer > self.end and self.direction >= 0:
			raise StopIteration
		elif self.pointer < self.end and self.direction <= 0:
			raise StopIteration

		# Determine the starting and ending dates for this subinterval
		interval_start = self.pointer
		interval_end = self.pointer + timedelta(self.span)

		# If interval end falls outside the range, truncate it
		if interval_end > self.end and self.direction >= 0:
			interval_end = self.end
		elif interval_end < self.end and self.direction <= 0:
			interval_end = self.end

		# Update the internal pointer
		self.pointer += timedelta(self.increment)

		# Return the subinterval
		return interval_start, interval_end


class DateBinner(object):

	DATE_FORMAT = '%Y/%m/%d'

	def __init__(self, start, end, increment_by_days=7):
		self.start = start
		self.end = end
		self.increment_by_days = increment_by_days

		self.date_keys = self.get_date_keys(start, end, increment_by_days)


	def get_date_keys(self, start, end, increment_by_days):

		# We'll accumulate a list of tuples consisting of <k, start, end>
		# where k is a string (a key) that represents the time interval
		# from start to end (which are dates, inclusive).
		# This will help map an arbitrary date onto the string representing
		# the interval in which that date falls
		date_keys = []

		# Make a date iterator to yield the desired interval endpoints
		date_iterator = DateIterator(start, end, increment_by_days)

		# Use the iterator and accumulate all of the key-interval 
		# assignments
		for interval_start, interval_end in date_iterator:
			start_str = interval_start.strftime(self.DATE_FORMAT)
			end_str = interval_end.strftime(self.DATE_FORMAT)
			key = '%s-%s' % (start_str, end_str)
			date_keys.append((key, interval_start, interval_end))

		return date_keys


	def get_date_key(self, datelike):
		''' 
		Returns a string, representing date range into which <datelike> 
		falls.  <datelike> should be a date or datetime object.  
		'''
		if isinstance(datelike, datetime):
			datelike = datelike.date()
		for key, start, end in self.date_keys:
			if datelike >= start and datelike <= end:
				return key 
		return None
