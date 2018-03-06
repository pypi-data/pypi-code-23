from datetime import date
import math

class DateTimeUtils:
    '''
    Calculates a week range from the Sunday before the given @day to the next
    Saturday.

    @param day: a date object of the day to calculate from, defaults to today
    @return: a list of date objects
    '''
    def get_sunday_to_saturday(self, day = date.today()):
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        today_name = day.strftime("%A")
        today_offset = days.index(today_name)

        sunday = day.toordinal() - today_offset

        dates = []
        dates.append(date.fromordinal(sunday))
        for i in range(1, 7):
            dates.append(date.fromordinal(sunday + i))

        return dates


    '''
    Converts minutes to hours, rounding up to the given resolution.

    @param mins: the number of minutes to convert
    @param resolution: where to round to, default 0.25 (quarter hour/15 minutes)
    @return: the converted number of hours
    '''
    def convert_to_hours(self, mins, resolution = 0.25):
        hours = mins / 60

        # Round up to the nearest resolution
        return math.ceil(hours / resolution) * resolution


    '''
    Converts a string in the format YYYY-MM-DD to a datetime.date object.

    @param string: the date in the format YYYY-MM-DD
    @return: a date object
    '''
    def date_string_to_date_object(self, string):
        date_parts = list(map(int, string.split('-')))
        return date(date_parts[0], date_parts[1], date_parts[2])
