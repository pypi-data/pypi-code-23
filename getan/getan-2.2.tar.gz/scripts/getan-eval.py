#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2013, 2014 by Björn Ricks <bjoern.ricks@intevation.de>
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.

import codecs
import locale
import sys

from datetime import date, datetime, timedelta
from optparse import OptionParser

from getan.template import render


def main():
    parser = OptionParser()
    parser.add_option("-d", "--database", dest="database",
                      help="getan database",  metavar="DATABASE")
    parser.add_option("-t", "--template", dest="template", metavar="TEMPLATE",
                      help="name of getan template")
    parser.add_option("-u", "--user", dest="user", help="name of user")
    parser.add_option("-p", "--project", dest="project",
                      help="key of output project")
    parser.add_option("-w", "--week", type="int", dest="week",
                      help="week of year")
    parser.add_option("-y", "--year", type="int", dest="year", help="year")
    parser.add_option("-c", "--lastweek", dest="lastweek",
                      help="entries of last working week",
                      action="store_true")
    parser.add_option("-m", "--empty", dest="empty",
                      help="show projects without an entries",
                      action="store_true")
    parser.add_option("--encoding", dest="encoding",
                      help="encoding of output", metavar="ENCODING")

    (options, args) = parser.parse_args()

    if options.lastweek:
        week = (datetime.now() - timedelta(7)).isocalendar()[1]
        year = int(date.today().strftime("%Y"))
    else:
        year = options.year
        week = options.week

    template_name = options.template or "wochenbericht"

    if not options.encoding:
        encoding = locale.getdefaultlocale()[1] or "utf-8"

    Writer = codecs.getwriter(encoding)
    sys.stdout = Writer(sys.stdout)

    user = None
    if options.user:
        user = options.user.decode(encoding)

    print render(database=options.database, user=user,
                 template=template_name, year=year, week=week,
                 project=options.project, empty_projects=options.empty)


if __name__ == '__main__':
    main()

# vim:set ts=4 sw=4 si et sta sts=4 :
