import calendar
from datetime import timedelta, datetime, date


def month_bound_from_date(d):
    """Get first and last date in date's month."""
    return d.replace(day=1), d.replace(day=calendar.monthrange(d.year, d.month)[1])


def month_bound_from_month_number(year, month):
    """Get first and last date in (year, month)."""
    return month_bound_from_date(date(year, month, 1))


def week_bound_from_date(d):
    """Get first and last date in date's week. First day is Monday."""
    first_day = d - timedelta(days=d.weekday())
    last_day = first_day + timedelta(days=6)
    return first_day, last_day


def week_bound_from_week_number(week_year, week):
    """Get first and last date in isoweeknum. First day is Monday."""
    first_day = datetime.strptime(str(week_year) + str(week) + '1', '%G%V%w')
    return week_bound_from_date(first_day)


def diff_week(minuend, subtrahend):
    """Get two dates' week diff."""
    monday1, _ = week_bound_from_date(minuend)
    monday2, _ = week_bound_from_date(subtrahend)

    return int((monday1 - monday2).days / 7)


def diff_month(minuend, subtrahend):
    """Get two dates' month diff."""
    return (minuend.year - subtrahend.year) * 12 + minuend.month - subtrahend.month


def month_weekdays(d, weekday):
    """
    Get all weekday in a month which the date in.
    Use month_*days for simple.

    :param d: date, will return all weekday in this date's month
    :param weekday: 0-Monday, 1-Tuesday, 2-Wednesday, 3-Thursday, 4-Friday, 5-Saturday, 6-Sunday.
    :return: a date Generator
    """
    month_first_day, _ = month_bound_from_date(d)
    days_ahead = weekday - month_first_day.weekday()
    if days_ahead < 0:
        days_ahead += 7
    next_day = month_first_day + timedelta(days=days_ahead)

    while next_day.month == d.month:
        yield next_day
        next_day += timedelta(days=7)


def month_mondays(d):
    return month_weekdays(d, 0)


def month_tuesdays(d):
    return month_weekdays(d, 1)


def month_wednesdays(d):
    return month_weekdays(d, 2)


def month_thursdays(d):
    return month_weekdays(d, 3)


def month_fridays(d):
    return month_weekdays(d, 4)


def month_saturdays(d):
    return month_weekdays(d, 5)


def month_sundays(d):
    return month_weekdays(d, 6)


def daterange(start, end):
    """range version for date. NOTE: As built-in range, this not include the end."""
    d = start
    delta = timedelta(days=1)
    while d < end:
        yield d
        d += delta
