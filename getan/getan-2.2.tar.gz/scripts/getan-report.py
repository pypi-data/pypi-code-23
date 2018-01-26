#!/usr/bin/env python3
"""
write a daily report accessing a database from
http://hg.intevation.de/getan 1.1dev3.
"""
# hastily done, written to learn the getan database format and its manipulation
# Free Software under GNU GPL v>=3
# 20130109 bernhard@intevation.de
# 20140103 bernhard@intevation.de:
#   started from 2013/getan-writeout-timesorted.py
#   ported to python3. Removed the dependency for functions from worklog.py.
#   the timesorted variant can be uncommented in the code for now
# 20140109 bernhard@intevation.de:
#   Total time output format improved.
# 20140120 bernhard@intevation.de:
#   added command line options, requires argparse module now (e.g. Python>=3.2)
# 20141104 bernhard@intevation.de:
#   migration to argparse complete, added -t option
# TODO:
#  * use python v>=3.2 variants in the code where noted.

import argparse
import datetime
import logging
import sqlite3

factor = {'privat': 0}

l = logging
l.basicConfig(level=logging.INFO,
              # l.basicConfig(level=logging.DEBUG,
              format='%(message)s')
#                    format='%(asctime)s %(levelname)s %(message)s')


def hhhmm_from_timedelta(td):
    """Return a string '-HHH:MM' from the timedelta parameter.

    Accounts for way the integer division works for negative numbers:
        -2 // 60 == -1
        -2 % 60 == 58
    by first working on the positive number and then adding the minus
    to the string.

    For python >=3.1. Successor of hhmm_from_timedelta() from
    http://intevation.de/cgi-bin/viewcvs-misc.cgi/worklog.py/ .
    """
    total_minutes = abs(round(td.days * 24 * 60 + td.seconds / 60))
    # variant for Python v>3.2:
    # total_minutes = abs(round(td/datetime.timedelta(minutes=1)))

    hours = total_minutes // 60
    minutes = total_minutes % 60

    h_string = "{}".format(hours)

    if(td.days < 0):
        h_string = "-" + h_string

    return "{:>3s}:{:02d}".format(h_string, minutes)


def self_test():
    """Run some simple tests on hhhmm_from_timedelta().

    e.g. run like
        python3 -c 'from getan_report_20140103 import *; self_test()'
    """
    l.info(hhhmm_from_timedelta(datetime.timedelta(minutes=1)))
    l.info(hhhmm_from_timedelta(datetime.timedelta(minutes=-2)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-t", action='store_true',
                        help="timesorted output and default reportday to today")
    parser.add_argument("dbfilename")
    parser.add_argument("reportday", nargs='?',
                        help="day to report  yyyy-mm-dd")

    args = parser.parse_args()
    l.debug(args)

    if args.reportday:
        try:
            report_range_start = \
                datetime.datetime.strptime(args.reportday, "%Y-%m-%d")
        except ValueError:
            report_range_start = \
                datetime.datetime.strptime(args.reportday, "%Y%m%d")

    elif args.t:
        # start with today 00:00
        report_range_start = datetime.datetime.combine(
            datetime.date.today(), datetime.time())
    else:
        # start with yesterday 00:00
        report_range_start = datetime.datetime.combine(
            datetime.date.today() - datetime.timedelta(days=1),
            datetime.time())
    report_range_end = report_range_start + datetime.timedelta(days=1)

    l.info("Opening sqlite3 database '%s'" % args.dbfilename)
    conn = sqlite3.connect(
        args.dbfilename,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    c = conn.cursor()

    tasks = {}
    task_total = {}

    c.execute('select * from projects')
    for t in c:
        l.debug(t)
        tasks[t[0]] = t[2]
        task_total[t[0]] = datetime.timedelta()

# from getan 1.0 20130103
# CREATE TABLE entries (
#    id          INTEGER PRIMARY KEY AUTOINCREMENT,
#    project_id  INTEGER REFERENCES projects(id),
#    start_time  TIMESTAMP NOT NULL,
#    stop_time   TIMESTAMP NOT NULL,
#    description VARCHAR(256),
#
#    CHECK (strftime('%s', start_time) <= strftime('%s', stop_time))
# );

    total_time = datetime.timedelta()

    if args.t:
        c.execute('select * from entries order by start_time')
    else:
        c.execute('select * from entries order by project_id')
    for e in c:
        l.debug(e)
        # let us ignore microseconds
        start_time = e[2].replace(microsecond = 0)
        stop_time = e[3].replace(microsecond = 0)
        length = stop_time - start_time

        desc = tasks[e[1]]

        if start_time >= report_range_start and start_time < report_range_end:
            if args.t:
                print("{0:%Y-%m-%d %H:%M}-\n"
                      "{1:%Y-%m-%d %H:%M} {4}  {2}: {3}\n".
                      format(start_time, stop_time, desc, e[4],
                             hhhmm_from_timedelta(length)))
            else:
                print("{0} {2}: {3} {4}".
                      format(start_time, stop_time, desc, e[4],
                             hhhmm_from_timedelta(length)))
            if desc in factor:
                # python3.1 does not allow timedelta division.
                # TODO: Make python3.1 save or update to python3.2.
                # l.info("applying factor %f to entry %s" % (factor[desc], e))
                # length = (length * int(factor[desc]*1000))/1000
                # Until python3.2 we only honor a factor of zero:
                if factor[desc] == 0:
                    length = datetime.timedelta(0)
                    l.info("not counting {}".format(e))
                else:
                    l.info("ignoring factor {}".factor[desc])
            total_time += length
            task_total[e[1]] += length

    print("(" + hhhmm_from_timedelta(total_time).strip() + ")")
    for t in tasks:
        if task_total[t] != datetime.timedelta(0):
            print("\t" + tasks[t], hhhmm_from_timedelta(task_total[t]))

    c.close()

if __name__ == "__main__":
    main()
