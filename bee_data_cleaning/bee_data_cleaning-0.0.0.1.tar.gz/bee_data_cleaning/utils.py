import pytz
from math import ceil
from datetime import datetime


def diff_month(d1, d2):
    """
    Returns the difference in months between 'd1' and 'd2'
    :param d1: datetime
        The initial datetime
    :param d2: datetime
        The final datetime
    :return: int
        the number of months between the dates
    """
    return ceil(abs((d1.year - d2.year) * 12 + d1.month - d2.month))


def to_dt(d1):
    return pytz.UTC.localize(datetime.strptime(str(d1[:19]), "%Y-%m-%d %H:%M:%S"))
