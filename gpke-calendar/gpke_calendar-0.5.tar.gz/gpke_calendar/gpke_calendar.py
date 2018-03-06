import json
from datetime import date, datetime

import os

import sys

from pip._vendor import requests
from workdays import workday

SCRIPT_DIR = os.path.dirname(__file__)
DATA_DIR = "data"
excludes = ["Gründonnerstag", "Augsburger Friedensfest"]

def get_next_date(start: date, offset=0):
    holidays = get_holiday_list(start.year-1)
    holidays.extend(get_holiday_list(start.year))
    holidays.extend(get_holiday_list(start.year + 1))
    return workday(start, days=offset, holidays=set(holidays))


def get_holiday_list(year):
    if not date:
        raise Exception("no date")
    rel_path = get_filename(year)
    abs_file_path = os.path.join(SCRIPT_DIR, rel_path)

    with open(abs_file_path) as json_file:
        hollyday_data = json.load(json_file)
        dates = [datetime.strptime(ve.get('datum'), '%Y-%m-%d').date() for k, v in hollyday_data.items() for ke, ve in v.items() if ke not in excludes]
        return sorted(set(dates))


def get_filename(year):
    return "{}/{}.json".format(DATA_DIR, year)


def download_json():
    for year in range(2006, 2020):
        r = requests.get('https://feiertage-api.de/api/?jahr={}'.format(year))
        json_str = json.dumps(r.json())

        with open(get_filename(year), 'w') as f:
            f.write(json_str)


if __name__ == '__main__':
    print(get_next_date(datetime.strptime(sys.argv[1], '%d.%m.%Y').date(), int(sys.argv[2])))
