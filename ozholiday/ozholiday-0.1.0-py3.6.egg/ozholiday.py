# -*- coding: utf-8 -*-

"""Get the public holiday date from data.gov.au, and parse it to build the function"""
from datetime import date, datetime
from urllib import request
import json


API_URL = "https://data.gov.au/api/3/action/datastore_search?resource_id=31eec35e-1de6-4f04-9703-9be1d43d405b"
INFO_URL = "https://data.gov.au/dataset/australian-holidays-machine-readable-dataset"


def _build_list():
    """Return the list of holidays"""
    with request.urlopen(API_URL) as f:
        data = f.read().decode('utf-8')
    
    json_obj = json.loads(data)
    return json_obj['result']['records']
        

def _get_holiday_info(given_date):
    """The function to get the holiday details
    """

    holidays = _build_list()
    min_date = min(holidays, key=lambda x:x['_id'])['Date']
    max_date = max(holidays, key=lambda x:x['_id'])['Date']

    if not isinstance(given_date, (str, date, datetime)):
        raise "please give yyyymmdd format, or an `date` or an `datetime`"
    
    if isinstance(given_date, (date, datetime)):
        s = given_date.strftime("%Y%m%d")
    else:
        s = given_date

    # Check if the data outside range
    if s < min_date or s > max_date:
        raise ValueError("The date {d} is not in current list published by data.gov.au, \
                           \n Check here {url}".format(d=s, url=INFO_URL))

    holiday = [x for x in holidays if x['Date'] == s]
    if holiday:
        return holiday[0]
    else:
        return None

def isholiday(given_date, detail=False):
    """Return True or False if deatil is False, otherwise return the detail of holiday
    
    """
    result = _get_holiday_info(given_date)
    if not result:
        return False
    else:
        if not detail:
            return True
        else:
            return result


