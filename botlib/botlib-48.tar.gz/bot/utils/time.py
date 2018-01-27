# BOTLIB - the bot !!
#
# bot/utils/time.py
#
# Copyright 2017,2018 B.H.J Thate
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice don't have to be included.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.
#
# 9-1-2018 As the creator of this file, I disclaim all rights on this file. 
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" timed helper functions. """

import datetime
import os
import re
import time

class ENODATE(Exception):

    """ a time could not be detected. """
    
    pass

timere = re.compile(r'(\S+)\s+(\S+)\s+(\d+)\s+(\d+):(\d+):(\d+)\s+(\d+)')
bdmonths = ['Bo', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
monthint = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}

year_formats = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d-%m",
    "%m-%d",
]

def now():
    """ turn a datetime string of the current time. """
    return str(datetime.datetime.now())

def rtime():
    """ return a filestamp usable in a filename. """
    res =  str(datetime.datetime.now()).replace(" ", os.sep)
    return res

def spath(path):
    return os.sep.join(path.split(os.sep)[-3:])

def hms():
    """ return hour:minutes:seconds of toda=y. """
    return str(datetime.datetime.today()).split()[1].split(".")[0]

def day():
    """" return the current day. """
    return str(datetime.datetime.today()).split()[0]

def year():
    """ return the year we are living in. """
    return str(datetime.datetime.now().year)

def get_hour(daystr):
    """ get the hour from the string provided. """
    try:
        hmsre = re.search(r'(\d+):(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmsre.group(1)))
        hoursmin = hours  + int(hmsre.group(2)) * 60
        hms = hoursmin + int(hmsre.group(3))
    except AttributeError:
        pass
    except ValueError:
        pass
    try:
        hmre = re.search(r'(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmre.group(1)))
        hms = hours + int(hmre.group(2)) * 60
    except AttributeError:
        return 0
    except ValueError:
        return 0
    return hms

def get_time(txt):
    """ get time from a string containing day and/or hour. """
    try:
        target = get_day(txt)
    except ENODATE:
        target = to_day(day())
        hour = get_hour(txt)
        if hour:
            target += hour
    return target

def parse_time(txt):
    """" parse a string for a time mentioned. also parse for a diff in seconds. """
    seconds = 0
    target = 0
    txt = str(txt)
    for word in txt.split():
        if word.startswith("+"):
            seconds = int(word[1:])
            return time.time() + seconds
        if word.startswith("-"):
            seconds = int(word[1:])
            return time.time() - seconds
    if not target:
        try:
            target = to_time(txt)
        except ENODATE:
            target = to_day(day())
            hour = get_hour(txt)
            if hour:
                target += hour
    return target

def extract_time(daystr):
    """ use standard time timeformats to extract a time from a string. """
    for f in year_formats:
        try:
            res = time.mktime(time.strptime(daystr, f))
        except:
            res = None
        if res:
            return res

def to_day(daystring):
    """ try to detect a time in a string. """
    previous = ""
    line = ""
    daystr = str(daystring)
    for word in daystring.split():
        line = previous + " " + word
        previous = word
        try:
            res = extract_time(line.strip())
        except ValueError:
            res = None
        if res:
            return res
        line = ""

def to_time(daystr):
    """
         convert time/date string to a unix timestamp

         example: Wed, 10 Oct 2007 14:18:50 -0400 (EDT) 
         example: Thu, 17 May 2007 23:38:08 +0200 (CEST) 
         example: Tue, 09 Jan 2018 13:58:00 GMT
         example: 2016-08-29 16:34:23.837288
         example: Sat Jan 14 00:02:29 2017
         example: 2017-07-05t22:00:00+00:00
         example: Wed, 25 Apr 2012 10:14:11 +0200
         example: Wed, 10 Oct 2007 14:18:50 (edt) 
         example: 19 Oct 2007 22:17:14 
         example: Thu, 3 Aug 2006 15:30:07  
         example: Tue, 09 Oct 2012 07:07:32 BST 
         example: Fri Dec 22 01:23:54 


    """
    splitted = daystr.split()
    res = []
    for s in splitted:
        if "." in s:
            s = s.split(".")[0]
        res.append(s)
        if ':' in s:
            break
    daystr = " ".join(res)
    daystr = daystr.strip()
    res = 0
    try:
        res = time.mktime(time.strptime(daystr, "%a, %d %b %Y %H:%M:%S"))
    except:
        pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a, %d %b %Y %H:%M:%S %z (%Z)"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a, %d %b %Y %H:%M:%S %z"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d %b %Y %H:%M:%S"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a %b %d %H:%M:%S"))
        except:
            pass
        if res:
            daystr += " 2017"
            try:
                res = time.mktime(time.strptime(daystr, "%a %b %d %H:%M:%S %Y"))
            except:
                pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a, %d %b %Y %H:%M:%S %z"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%b %d %H:%M:%S"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a %b %d 2017 %H:%M:%S"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a %b %d %H:%M:%S %Y"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a %d %b %H:%M:%S %Y %z"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d %m %Y"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%d %H:%M:%S"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d-%m-%Y %H:%M:%S"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d-%m-%Y %H:%M"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%d %H:%M"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%d"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d-%m-%Y"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%dt%H:%M:%S+00:00"))
        except:
            pass
    if not res:
        raise ENODATE(daystr)
    return res

def file_time(timestamp):
    """ return a pseudo random time on today's start of the day. """
    return str(datetime.datetime.fromtimestamp(timestamp)).replace(" ", os.sep) + "." + str(random.randint(111111, 999999))

def to_date(*args, **kwargs):
    """ convert to date. """
    if not args:
        return None
    date = args[0]
    if not date:
        return None
    date = date.replace("_", ":")
    res = date.split()
    ddd = ""
    try:
        if "+" in res[3]:
            raise ValueError
        if "-" in res[3]:
            raise ValueError
        int(res[3])
        ddd = "{:4}-{:#02}-{:#02} {:6}".format(res[3], monthint[res[2]], int(res[1]), res[4])
    except (IndexError, KeyError, ValueError):
        try:
            if "+" in res[4]:
                raise ValueError
            if "-" in res[4]:
                raise ValueError
            int(res[4])
            ddd = "{:4}-{:#02}-{:02} {:6}".format(res[4], monthint[res[1]], int(res[2]), res[3])
        except (IndexError, KeyError, ValueError):
            try:
                ddd = "{:4}-{:#02}-{:02} {:6}".format(res[2], monthint[res[1]], int(res[0]), res[3])
            except (IndexError, KeyError):
                try:
                    ddd = "{:4}-{:#02}-{:02}".format(res[2], monthint[res[1]], int(res[0]))
                except (IndexError, KeyError):
                    try:
                        ddd = "{:4}-{:#02}".format(res[2], monthint[res[1]])
                    except (IndexError, KeyError):
                        try:
                            ddd = "{:4}".format(res[2])
                        except (IndexError, KeyError):
                            ddd = ""
    return ddd

def elapsed(seconds, short=True):
    """ return a string showing the elapsed days, hours, minutes, seconds. """
    txt = ""
    sub = str(seconds).split(".")[-1]
    nsec = float(seconds)
    year = 365*24*60*60
    week = 7*24*60*60
    day = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    days = int(nsec/day)
    nsec -= days*day
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    sec = nsec - minutes*minute
    if years:
        txt += "%sy" % years
    if weeks:
        days += weeks * 7
    if days:
        txt += "%sd" % days
    if years and short and txt:
        return txt
    if hours:
        txt += "%sh" % hours
    if days and short and txt:
        return txt
    if minutes:
        txt += "%sm" % minutes
    if hours and short and txt:
        return txt
    if sec == 0:
        txt += "0s"
    elif sec < 1 or not short:
        txt += "%.3fs" % sec
    else:
        txt += "%ss" % int(sec)
    txt = txt.strip()
    return txt

def today():
    """" return the day of a filename. """
    t = rtime().split(".")[0]
    ttime = time.strptime(t, "%Y-%m-%d/%H:%M:%S")
    result = time.mktime(ttime)
    return result

def get_day(daystring):
    """ get the day from the string provided. """
    day = 0
    try:
        ymdre = re.search(r'(\d+)-(\d+)-(\d+)', daystring)
        if ymdre:
            (year, month, day) = ymdre.groups()
    except:
        try:
            ymre = re.search(r'(\d+)-(\d+)', daystring)
            if ymre:
                (year, month) = ymre.groups()
                day = 1
        except:
            raise ENODATE(daystring)
    if not day:
        raise ENODATE(daystring)
    day = int(day)
    month = int(month)
    year = int(year)
    date = "%s %s %s" % (day, bdmonths[month], year)
    return time.mktime(time.strptime(date, "%d %b %Y"))

def days(obj):
    """ calculate the time passed since an object got logged. """
    t1 = time.time()
    try:
        t2 = dated(obj)
    except:
        t2 = time.ctime(time.time())
    t2 = to_time(t2)
    if t2:
        time_diff = float(t1 - t2)
        return elapsed(time_diff)

def dated(obj):
    """ fetch the date from an object. """
    try:
        res = obj._container.saved
    except:
        #print(obj)
        print(type(res))
    res = getattr(obj, "Date", res)
    res = getattr(obj, "saved", res)
    res = getattr(obj, "published", res)
    if not res:
        raise ENODATE(res)
    return res

def timed(obj):
    """ calculated the time of an object. """
    try:
        return fn_time(obj._container.path)
    except:
        try:
            return fn_time(rtime())
        except:
            pass
    try:
        d = dated(obj._container)
    except (AttributeError, ENODATE):
        try:
            d = dated(obj)
        except ENODATE:
            d = None
    if d:
        try:
            return to_time(d)
        except ENODATE:
            pass

def fn_time(daystr):
    """ determine the time used in a BL filename. """
    daystr = daystr.replace("_", ":")
    datestr = " ".join(daystr.split(os.sep)[-2:])
    datestr = datestr.split(".")[0]
    try:
        t = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
    except ValueError:
        t = 0
    return t

