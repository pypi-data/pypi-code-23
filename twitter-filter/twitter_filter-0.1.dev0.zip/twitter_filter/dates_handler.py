# -*- coding: utf-8 -*-
"""

This module is responsible for handling dates-related operations
like generating a range of dates and extracting date info from date files.

"""

from datetime import timedelta, datetime

from twitter_filter.file_util import FileUtil
from pandas.tseries.offsets import CustomBusinessHour

from twitter_filter.exceptions_wrapper import ErrorWrapper


# This is the dates handling class.
class DatesHandler(object):
    """ This class implements every date-related functionality.

    This class gets the dates range and extracts date info from files.

    Attributes:
    ----------
    start_date : datetime
        The operation starting date.
    end_date : datetime
        The operation ending date.

    """
    def __init__(self, start_date, end_date):
        """
        Initializer for DatesHandler class.


        Parameters
        ----------
        start_date : datetime
            The start date.
        end_date : datetime
            The end date.

        """
        self.start_date = start_date
        self.end_date = end_date

    def date_range(self):
        """
        This function gets a range of dates between the start_date and end_date attributes.


        Parameters
        ----------

        Yields
        -------
        list
            The range of datetime items.

        """
        try:
            for n in range(int((self.end_date - self.start_date).days) + 1):
                yield self.start_date + timedelta(n)
        except Exception as e:
            print(ErrorWrapper(e).handle())

    @staticmethod
    def extract_date_info(read_file_path, hours_write_file_path, week_days_write_file_path):
        """
        This function extracts the hour and the week day from date input file.
        It stores the results in output files whose paths are function arguments.


        Parameters
        ----------
        read_file_path : str
            The date data file path.

        hours_write_file_path : str
            The desired hours only data file path.

        week_days_write_file_path : str
            The desired week days only data file path.

        Returns
        -------

        """
        try:
            lines = FileUtil.file_reader(read_file_path)
            hours = []
            week_days = []
            for line in lines:
                parts = line.split(" ")
                week_day = parts[0]
                time = parts[3]
                hour = time.split(":")[0]
                hours.append(hour)
                week_days.append(week_day)
            FileUtil.write_to_file(hours_write_file_path, hours)
            FileUtil.write_to_file(week_days_write_file_path, week_days)
        except Exception as e:
            print(ErrorWrapper(e).handle())


    @staticmethod
    def create_bussiness_hour(start='00:00', end='23:00', week_mask='Mon Tue Wed Thu Fri'):
        """
        This function creates custom business hour for using in date ranges creation.

        Parameters
        ----------
        start : str
            The business hours start.

        end : str
            The business hours end.
        week_mask : str
            The mask that specify work weekdays.

        Returns
        -------
        object
            The business hour object.

        """
        bhour = CustomBusinessHour(start='08:00', end='23:00', weekmask=week_mask)