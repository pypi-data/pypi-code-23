import argparse
import datetime
import functools
import sys

from .colorcalendar import show_calendar, month_list
from colorline import cprint

eprint = functools.partial(cprint, color='r', bcolor='g', mode='highlight')

parser = argparse.ArgumentParser(description='A colorful calendar')
parser.add_argument('--date', help='ISO format: 2018-2-11', default=datetime.date.today().isoformat(), dest='date')
parser.add_argument('-b', '--background', help='background color', dest='bg')
parser.add_argument('-f', '--foreground', help='foreground color', dest='fg')

args = parser.parse_args()

thirty_list = [4, 6, 9, 11]

def check_date(year, month, day):
    if year <= 1900 or year >= 2100:
        raise ValueError('Year must be in [1900, 2100]')
    elif month < 1 or month > 12:
        raise ValueError('Month must be in [1, 12]')
    elif day < 1 or day > 31:
        raise ValueError('Day must be in [1, 31]')

    leap_year = True if year % 4 == 0 else False
    if month == 2:
        if day > 29:
            raise ValueError("There's only 28 days in {}".format(month_list[month - 1]))
        elif not leap_year and day == 29:
            raise ValueError('Year {} is not a leap year'.format(year))
    elif month in thirty_list and day > 30:
        raise ValueError("There's only 30 days in {}".format(month_list[month - 1]))

def main():
    try:
        year, month, day = [int(x) for x in args.date.split('-')]
    except ValueError:
        #Date must be integer, must be format year-mo-da
        eprint('Invalid date, please refer to the ISO format: 2018-2-11')
        parser.print_help()
    else:
        try:
            check_date(year, month, day)
        except ValueError as error:
            eprint(error)
            parser.print_help()
            sys.exit(-1)

    print(year, month, day)
