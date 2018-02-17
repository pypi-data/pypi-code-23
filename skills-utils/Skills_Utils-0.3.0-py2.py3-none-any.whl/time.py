"""Time utilities"""
from datetime import date
import math


def quarter_to_daterange(quarter):
    """Convert a quarter in arbitrary filename-ready format (e.g. 2015Q1)
    into start and end datetimes"""
    assert len(quarter) == 6
    year = int(quarter[0:4])
    quarter = quarter[5]
    MONTH_DAY = {
        '1': ((1, 1), (3, 31)),
        '2': ((4, 1), (6, 30)),
        '3': ((7, 1), (9, 30)),
        '4': ((10, 1), (12, 31))
    }
    md = MONTH_DAY[quarter]
    start_md, end_md = md
    return (
        date(year, *start_md),
        date(year, *end_md)
    )


def datetime_to_year_quarter(dt):
    """
    Args:
        dt: a datetime
    Returns:
        tuple of the datetime's year and quarter
    """
    year = dt.year
    quarter = int(math.ceil(float(dt.month)/3))
    return (year, quarter)


def datetime_to_quarter(dt):
    """
    Args:
        dt: a datetime
    Returns:
        the datetime's quarter in string format (2015Q1)
    """
    year, quarter = datetime_to_year_quarter(dt)
    return '{}Q{}'.format(year, quarter)


def overlaps(start_one, end_one, start_two, end_two):
    return start_one <= end_two and start_two <= end_one
