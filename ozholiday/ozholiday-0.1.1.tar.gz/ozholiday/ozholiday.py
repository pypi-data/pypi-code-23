# -*- coding: utf-8 -*-

"""Get the public holiday date from data.gov.au, and parse it to build the function"""
from datetime import date, datetime
from urllib import request
import json
import logging
import os


API_URL = "https://data.gov.au/api/3/action/datastore_search?resource_id=31eec35e-1de6-4f04-9703-9be1d43d405b"
INFO_URL = "https://data.gov.au/dataset/australian-holidays-machine-readable-dataset"

HOMEFOLDER = os.environ.get('HOME',None) or os.environ.get('USERPROFILE', None) or './'
CACHE_FILE = os.path.join(HOMEFOLDER, '.ozholiday.json')


def _days_to_now(filename):
    """Calculate the days to now for a existing file
    """
    ts = os.path.getmtime(filename)
    today = datetime.today()
    time_delta = today - datetime.fromtimestamp(ts)
    return time_delta.days

def _build_list():
    """Get the file from cache or from web
    """
    if not os.path.isfile(CACHE_FILE) or _days_to_now(CACHE_FILE) > 180:
        obj_json = _build_list_from_web()
        try:
            os.remove(CACHE_FILE)
        except:
            pass

        with open(CACHE_FILE,'w') as fp:
            logging.info("Writting to cache file")
            json.dump(obj_json, fp)
    else:
        # file exist and less than half year
        with open(CACHE_FILE,'r') as fp:
            obj_json = json.load(fp)

    return obj_json


def _build_list_from_web():
    """Return the list of holidays"""
    with request.urlopen(API_URL) as f:
        logging.info("Getting file from web ...")
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


