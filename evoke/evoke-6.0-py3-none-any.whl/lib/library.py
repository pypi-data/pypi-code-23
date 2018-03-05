"""
evoke library routines

a library of robust general routines mainly for handling conversions

def elapsed(seconds)         converts time in seconds into hours:mins:secs   

def process_time():          returns time elapsed since system started, in a display format

def httpDate(self, when=None, rfc='1123'): generates rfc standard dates strings for http 

def turnaround(start,end):   calculates turnaround, in working days, ie ignoring weekends
                             accepts dates in any format  
def asItems(text):
def counted(items,start=1):  converts list of items into list of (count,item) pairs
def safeint(num):            converts to int, regardless
def sn(ok):                  converts boolean value to +1 or -1

def limit(v,lo,hi):          limits v to between lo and hi

def percent(a,b):            returns string repr of a as a percentage of b (to nearest full percent)

def page(req,pagesize=50):   for paging: returns limit parameter for self.list()

def idf(t):                  fixes t into an id which wont break html - not foolproof

def url_safe(text):          fixes url for http

def csv_format(s):           cleans syntax problems for csv output

def sql_list(val):          converts single value or list or tuple into sql format list for 'is in' etc.

(Ian Howie Mackenzie 2/11/2005 onwards. Email enhancements by Chris J Hurst)
"""

from time import time, gmtime
import datetime
from .DATE import DATE
import urllib.request, urllib.parse, urllib.error, re

###################### time ###################


def httpDate(when=None, rfc='1123'):
    """ (copied as is from MoinMoin request.py)
    Returns http date string, according to rfc2068

    See http://www.cse.ohio-state.edu/cgi-bin/rfc/rfc2068.html#sec-3.3

    A http 1.1 server should use only rfc1123 date, but cookie's
    "expires" field should use the older obsolete rfc850 date.

    Note: we can not use strftime() because that honors the locale
    and rfc2822 requires english day and month names.

    We can not use email.Utils.formatdate because it formats the
    zone as '-0000' instead of 'GMT', and creates only rfc1123
    dates. This is a modified version of email.Utils.formatdate
    from Python 2.4.

    @param when: seconds from epoch, as returned by time.time()
    @param rfc: conform to rfc ('1123' or '850')
    @rtype: string
    @return: http date conforming to rfc1123 or rfc850
    """
    if when is None:
        when = time()
    now = gmtime(when)
    month = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
        'Nov', 'Dec'
    ][now.tm_mon - 1]
    if rfc == '1123':
        day = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][now.tm_wday]
        date = '%02d %s %04d' % (now.tm_mday, month, now.tm_year)
    elif rfc == '850':
        day = [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
            "Sunday"
        ][now.tm_wday]
        date = '%02d-%s-%s' % (now.tm_mday, month, str(now.tm_year)[-2:])
    else:
        raise ValueError("Invalid rfc value: %s" % rfc)
    return '%s, %s %02d:%02d:%02d GMT' % (day, date, now.tm_hour, now.tm_min,
                                          now.tm_sec)


def elapsed(seconds, format=""):
    """converts time in seconds into days hours mins secs 
    format, if given, can be "d:h:m:s", or "h:m:s", or "m:s", otherwise long format is used
    ( adapted from zope ApplicationManager.py )
    """
    s = safeint(seconds)
    d = 0
    h = 0
    if (not format) or format.startswith("d:"):
        d = int(s / 86400)
        s = s - (d * 86400)
    if (not format) or ("h:" in format):
        h = int(s / 3600)
        s = s - (h * 3600)
    m = int(s / 60)
    s = s - (m * 60)
    if format:
        if d:
            return ('%d:%02d:%02d:%02d' % (d, h, m, s))
        if h:
            return ('%d:%02d:%02d' % (h, m, s))
        return ('%d:%02d' % (m, s))
    else:  # long format
        d = d and ('%d day%s' % (d, (d != 1 and 's' or ''))) or ''
        h = h and ('%d hour%s' % (h, (h != 1 and 's' or ''))) or ''
        m = m and ('%d min' % m) or ''
        s = '%d sec' % s
        return ('%s %s %s %s' % (d, h, m, s)).strip()


def process_time():
    s = int(time()) - process_start
    return elapsed(s)


process_start = int(time())


def turnaround(start, end):
    """calculates turnaround, in working days, ie ignoring weekends
       accepts dates in any format
    """
    start = DATE(start).datetime.date()
    end = DATE(end).datetime.date()
    t = end - start
    s = start.weekday()
    e = end.weekday()
    d = (7 - s) + e
    return int((((t.days - d) * 5) // 7) + d - 1)


###################### number conversion ###################


def asItems(text):
    try:
        n = int(text)
        if n == 0:
            return ''
        return repr(n)
    except:
        return ''


def counted(items, start=1):
    "converts list of items into list of (count,item) pairs"
    n = start
    z = []
    for i in items:
        z.append((n, i))
        n += 1
    return z


def safeint(num):
    """converts to int, regardless
  """
    try:
        v = int(num)
    except:
        v = 0
    return v


def safefloat(num):
    """converts to float, regardless
  """
    try:
        v = float(num)
    except:
        v = 0.0
    return v


def sn(ok):
    """converts boolean value to +1 or -1
  """
    if ok: return 1
    else: return -1


# number utilities ##################


def limit(v, lo, hi):
    "limits v to between lo and hi"
    return min(hi, max(lo, v))


# number formatting ############


def percent(a, b):
    "returns string repr of a as a percentage of b (to nearest full percent)"
    return '%d%%' % (0.5 + float(a) * 100 / float(b))


################# list utilities ###############


def prev(p, seq):
    "expects current object 'p', and sequence of objects 'seq' - returns previous object"
    try:
        i = seq.index(p)
        if i:
            return seq[i - 1]
        else:
            return None
    except:
        return None


def next(p, seq):
    "expects current object 'p', and sequence of objects 'seq' - returns next object"
    try:
        return seq[seq.index(p) + 1]
    except:
        return None


################### paging ####################


def page(req, pagesize=50):
    "returns limit parameter for self.list(): requires req.pagenext, and provides req.pagenext and req.pagesize"
    offset = safeint(req.pagenext)
    req.pagenext = offset + pagesize  #next page
    req.pagesize = pagesize  #for use in form, to determine whether there is more to show
    return '%s,%s' % (offset, pagesize)


################### text formatting ##################

def delf(text):
    """remove carriage-returns and single line-feeds from text
       - leaves double line-feeds (paragraph breaks)
       - also removes trailing spaces
       - source must be a string
    """
    # remove trailing spaces
    lines=[line.rstrip() for line in text.split('\n')]
    cleantext='\n'.join(lines)
    # remove carriage returns and single line feeds
    return cleantext.replace('\r','').replace('\n\n','\r').replace('\n',' ').replace('\r','\n\n')


################### html formatting ###################


def idf(t):
    "fixes t into an id which wont break html - not foolproof"
    return t.replace(' ', '').replace('(', '').replace(')', '')


################### http formatting ###################

#def url_safe(text):
#  return urllib.quote(text)


def url_safe(text):
    return urllib.parse.quote_plus(text, safe="/")


################### CSV formattingr ###################
# O/S - THIS SHOULD BE SOMEWHERE ELSE.... a reporting library?


def csv_format(s):
    """
    cleans syntax problems for csv output
  """
    s = s.replace('"', "'")
    s = s.replace("\n", " ")
    s = s.replace("\x00D", "")
    return '"%s"' % s


################# SQL formatting ###################


def sql_list(val):
    "converts list or tuple into sql format list for 'is in' etc."
    return len(val) == 1 and '(%s)' % repr(val[0]) or tuple(val)


################ filename formatting ###############


def safe_filename(text):
    "not foolproof"
    return text.replace(' ', '_').replace("'", "").replace('"', '').replace(
        '/', '-').replace('?', '').replace('!', '')


def test():
    pass


if __name__ == '__main__': test()
