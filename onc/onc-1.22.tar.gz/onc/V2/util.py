#------------------------------------------------------------------------------
# Name:        util
# Purpose:     This is a collection of utility functions used the ONC library
#
# Author:      ryanross
#
# Created:     31/10/2016
# Copyright:   (c) Ocean Networks Canada 2016-2018
# Licence:     None
# Requires:    requests library - [Python Install]\scripts\pip install requests
#------------------------------------------------------------------------------

import sys

import requests
import json
from xml.etree.ElementTree import fromstring, ElementTree
import math
from datetime import datetime
import os.path
import sys
from datetime import datetime
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from dateutil.relativedelta import *

datetimeFormat = '%Y-%m-%dT%H:%M:%S.%f' 
 
'''
Method to print an error message from an ONC web service call to the console.
'''
def printErrorMesasge(response,
                      parameters,
                      showUrl=False,
                      showValue=False):
    
    if(response.status_code == 400):
        if showUrl:print('Error Executing: {}'.format(response.url))
        payload = json.loads(str(response.content))
        if len(payload) >= 1:
            for e in payload['errors']:
                msg = e['errorMessage']
                parm = e['parameter']
                 
                matching = [p for p in parm.split(',') if p in parameters.keys()]
                if len(matching) >=1: 
                    for p in matching:print("  '{}' for {} - value: '{}'".format(msg,p,parameters[p]))
                else: 
                    print("  '{}' for {}".format(msg,parm))
                
                if showValue:
                    for p in parm.split(','):
                        parmValue = parameters[p]
                        print("  {} for {} - value: '{}'".format(msg,p,parmValue))
            return payload
    else:
        msg = 'Error {} - {}'.format(response.status_code,response.reason)
        print (msg)
        return msg

'''
Method to print a count with a name to the console.
'''
def printCount(count,
               name):
    
    if(count != 1):
        print('  {} {}'.format(count,name))

'''
Method to print a time duration of a web service call to the console.
'''
def printResponseTime(end,
                      start):
    
    delta = end - start
    execTime = delta.seconds + delta.microseconds/1E6
    print('Web Service Response Time: {} seconds'.format(execTime))

'''
Method to convert a time value in seconds to a string in the format Hours:Minutes:Seconds.
'''
def getHMS(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "{}:{}:{}".format(int(h),int(m),round(s,2))

'''
Method to print a time value in seconds as string in the format Hours:Minutes:Seconds to the console.
'''
def printHMS(seconds):
    print(getHMS(seconds))
 
'''
Method to return a string representation of a size in bytes.
'''
def convertSize(size):
    
   if (size == 0):
       return '0 KB'
   sizeUnits = ("B","KB","MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size,1024)))
   p = math.pow(1024,i)
   s = round(size/p,2)
   return '%s %s' % (s,sizeUnits[i])

'''
Method to return a size in bytes from a string representation of a file size
'''
def toBytes(str):
    
    iBytes = None
    if str:
        sizeUnits = ("B","KB","MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        sSize = str.split(' ')[0]
        if isNumber(sSize):
            iSize = float(sSize)    
        else:
            return None
        
        sName = str.split(' ')[1]
        if (sName in sizeUnits):
            indx = sizeUnits.index(sName)
            p = math.pow(1024,indx)
            iBytes = int(p*iSize)
        else:
            print("Unable to convert to bytes - '{}' is an unknown size unit.".format(sName))
        
    return iBytes

'''
Method to return a time in seconds from a string representing a time
'''
def toSeconds(str):
    seconds = None
    if str:
        timeUnits = ("s","min","h")
        sSize = str.split(' ')[0]
        if isNumber(sSize):
            iSize = float(sSize)    
        else:
            return None
        
        sName = str.split(' ')[1]
        if (sName in timeUnits):
            indx = timeUnits.index(sName)
            p = math.pow(60,indx)
            seconds = int(p*iSize)
        else:
            print("Unable to convert to seconds - '{}' is an unknown time unit.".format(sName))
    
    return seconds

'''
Method to print a message to the console without a line break. This allows for writing subsequent messages to the same line, such as Downloading.....
'''
def printWithEnd(message,
                 separator=None):
    
    print message,

'''
Method to read JSON from a file and return it as an object.
'''
def readJSONFile(filename):
    
    j = None
    with open(filename) as f:
        j = json.loads(f.read())
    
    return j

'''
Method to write an object as JSON to a file.
''' 
def writeJSONFile (filename,
                   obj,
                   sort=False):
    
    s = json.dumps(obj,sort_keys=sort,indent=4, separators=(',',': '))
    with open(filename, "w") as f:
        f.write(s)

'''
Method to return the string representation of an object.
'''
def toString(obj):
    return str(obj)

'''
Method to determine if an object is a valid number.
'''
def isNumber(obj):
    try:
        float(obj)
        return True
    except ValueError:
        return False 

def daterangeByDay(startDate, endDate):
    dtStart =  datetime(startDate.year, startDate.month, startDate.day)
    dtEnd = dtStart + timedelta(days=1)
    yield {'begin':startDate.strftime(datetimeFormat)[:-3]+'Z','end':dtEnd.strftime(datetimeFormat)[:-3]+'Z'}
    
    while True:
        dtStart = dtEnd
        dtEnd = dtStart + relativedelta(days=1)
        if (dtEnd > endDate):
            yield {'begin':dtStart.strftime(datetimeFormat)[:-3]+'Z','end':endDate.strftime(datetimeFormat)[:-3]+'Z'}
            break
        else:
            yield {'begin':dtStart.strftime(datetimeFormat)[:-3]+'Z','end':dtEnd.strftime(datetimeFormat)[:-3]+'Z'}

def daterangeByWeek(startDate, endDate, dayOfWeek=0): #0 - Monday, 6 - Sunday
    dayDelta = startDate.weekday() - dayOfWeek
    newStart = startDate - timedelta(days=dayDelta)
    
    dtStart =  datetime(newStart.year, newStart.month, newStart.day)
    dtEnd = dtStart + relativedelta(weeks=1)
    yield {'begin':startDate.strftime(datetimeFormat)[:-3]+'Z','end':dtEnd.strftime(datetimeFormat)[:-3]+'Z'}
    
    while True:
        dtStart = dtEnd
        dtEnd = dtStart + relativedelta(weeks=1)
        if (dtEnd > endDate):
            yield {'begin':dtStart.strftime(datetimeFormat)[:-3]+'Z','end':endDate.strftime(datetimeFormat)[:-3]+'Z'}
            break
        else:
            yield {'begin':dtStart.strftime(datetimeFormat)[:-3]+'Z','end':dtEnd.strftime(datetimeFormat)[:-3]+'Z'}

def daterangeByMonth(startDate, endDate):
    dtStart =  datetime(startDate.year, startDate.month, 1)
    dtEnd = dtStart + relativedelta(months=1)
    yield {'begin':startDate.strftime(datetimeFormat)[:-3]+'Z','end':dtEnd.strftime(datetimeFormat)[:-3]+'Z'}
    
    while True:
        dtStart = dtEnd
        dtEnd = dtStart + relativedelta(months=1)
        if (dtEnd > endDate):
            yield {'begin':dtStart.strftime(datetimeFormat)[:-3]+'Z','end':endDate.strftime(datetimeFormat)[:-3]+'Z'}
            break
        else:
            yield {'begin':dtStart.strftime(datetimeFormat)[:-3]+'Z','end':dtEnd.strftime(datetimeFormat)[:-3]+'Z'}

def daterangeByYear(startDate, endDate):
    dtStart =  datetime(startDate.year, 1, 1)
    dtEnd = dtStart + relativedelta(years=1)
    yield {'begin':startDate.strftime(datetimeFormat)[:-3]+'Z','end':dtEnd.strftime(datetimeFormat)[:-3]+'Z'}
    
    while True:
        dtStart = dtEnd
        dtEnd = dtStart + relativedelta(years=1)
        if (dtEnd > endDate):
            yield {'begin':dtStart.strftime(datetimeFormat)[:-3]+'Z','end':endDate.strftime(datetimeFormat)[:-3]+'Z'}
            break
        else:
            yield {'begin':dtStart.strftime(datetimeFormat)[:-3]+'Z','end':dtEnd.strftime(datetimeFormat)[:-3]+'Z'}
