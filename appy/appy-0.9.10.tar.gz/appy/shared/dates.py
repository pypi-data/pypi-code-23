'''Date-related classes and functions'''

# Copyright (C) 2007-2018 Gaetan Delannay

# This file is part of Appy.

# Appy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Appy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Appy. If not, see <http://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------------
try:
    from DateTime import DateTime
except ImportError:
    pass # Zope is required

# ------------------------------------------------------------------------------
def toUTC(d):
    '''When manipulating DateTime instances, like p_d, errors can raise when
       performing operations on dates that are not in Universal time, during
       months when changing from/to summer/winter hour. This function returns
       p_d set to UTC.'''
    return DateTime('%d/%d/%d UTC' % (d.year(), d.month(), d.day()))

# ------------------------------------------------------------------------------
class DayIterator:
    '''Class allowing to iterate over a range of days'''

    def __init__(self, startDay, endDay, back=False):
        self.start = toUTC(startDay)
        self.end = toUTC(endDay)
        # If p_back is True, the iterator will allow to browse days from end to
        # start.
        self.back = back
        self.finished = False
        # Store where we are within [start, end] (or [end, start] if back)
        if not back:
            self.current = self.start
        else:
            self.current = self.end

    def __iter__(self): return self
    def __next__(self):
        '''Returns the next day'''
        if self.finished:
            raise StopIteration
        res = self.current
        # Get the next day, forward
        if not self.back:
            if self.current >= self.end:
                self.finished = True
            else:
                self.current += 1
        # Get the next day, backward
        else:
            if self.current <= self.start:
                self.finished = True
            else:
                self.current -= 1
        return res
    next = __next__ # Python2-3 compliance

# ------------------------------------------------------------------------------
def getLastDayOfMonth(date):
    '''Returns a DateTime object representing the last day of date.month()'''
    day = 31
    month = date.month()
    year = date.year()
    found = False
    while not found:
        try:
            res = DateTime('%d/%d/%d 12:00' % (year, month, day))
            found = True
        except DateTime.DateError, de:
            day -= 1
    return res

def getDayInterval(date):
    '''Returns a tuple (startOfDay, endOfDay) representing the whole day into
       which p_date occurs.'''
    day = date.strftime('%Y/%m/%d')
    return DateTime('%s 00:00' % day), DateTime('%s 23:59' % day)
# ------------------------------------------------------------------------------
