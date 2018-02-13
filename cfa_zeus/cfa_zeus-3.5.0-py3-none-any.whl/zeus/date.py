# -----------------------------------------------------------------
# zeus: date.py
#
# zeus date manipulation module
#
# Copyright (C) 2016-2018, Christophe Fauchard
# -----------------------------------------------------------------

"""
Submodule: zeus.date

Dates manipulation

Copyright (C) 2016-2018, Christophe Fauchard
"""

import os
import datetime


class Date():

    """
    Date class with iso and custom format methods
    """

    def __init__(self):
        self.update()

    def update(self):
        """
        update datetime object with current time
        """
        self.value = datetime.datetime.now()

    def date_time_iso(self):
        """
        Format datetime object according to iso8601 normalization
        with time
        """
        return (self.value.strftime('%Y-%m-%dT%H:%M:%S'))

    def date_iso(self):
        """
        Format datetime object according to iso8601 normalization
        without time
        """
        return (self.value.strftime('%Y-%m-%d'))

    def format(self, format_string):

        """
        Format datetime object according to format_string parameter
        """
        return (self.value.strftime(format_string))

    def path_date_tree(self, path):
        """
        return a string with path parameter as prefix and directory
        YYYY/MM/DD
        """
        return (os.path.join(path,
                             self.value.strftime('%Y'),
                             self.value.strftime('%m'),
                             self.value.strftime('%d')))

    def print(self):
        """
        update datetime object and print with date_time_iso function
        """
        self.update()
        print(self.date_time_iso(), "", end='')
