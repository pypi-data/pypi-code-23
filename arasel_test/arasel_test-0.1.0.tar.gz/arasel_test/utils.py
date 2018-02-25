import numpy

def longest_dates_interval(dates):
    """Returns longest interval in consecutive dates"""

    if len(dates) == 0:
        raise ValueError("Empty list of dates")

    elif len(dates) == 1:
        return numpy.nan

    sorted_dates = sorted(dates)
    longest_interval = 0
    for first_date, second_date in zip(sorted_dates, sorted_dates[1:]):
        current_interval = (second_date - first_date).days
        longest_interval = max(longest_interval, current_interval)

    return longest_interval
