#!/usr/bin/env python
from dateutil import parser
import datetime
import yaml


with open("Config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)


def xrange(x):
    return iter(range(x))

def get_dates(from_date, to_date, day_list=[0,1,2,3,4,5,6]):
    tmp_list = list()
    date_list = list()
    ## Creates a list of all the dates falling between the from_date and to_date range
    for x in xrange((to_date - from_date).days +1 ):
        tmp_list.append(from_date + datetime.timedelta(days=x))
    for date_record in tmp_list:
        if date_record.weekday() in day_list:
            date_list.append(date_record)

    return date_list

from_date,to_date,duration = cfg['dates']['fromdate'],cfg['dates']['todate'],cfg['dates']['weekdaydeparture']
departuredates = get_dates(from_date, to_date, day_list=([int(x)-1 for x in cfg['dates']['weekdaydeparture']]))
returndates = get_dates(from_date, to_date, day_list=([int(x)-1 for x in cfg['dates']['weekdayreturn']]))

print('Fetched config data..')

