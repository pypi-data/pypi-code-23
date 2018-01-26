#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2008, 2009, 2010 by
#   Sascha L. Teichmann <sascha.teichmann@intevation.de>
#   Ingo Weinzierl <ingo.weinzierl@intevation.de>
# (c) 2017 by Intevation GmbH
# Authors:
#  * Sascha L. Teichmann <sascha.teichmann@intevation.de>
#  * Ingo Weinzierl <ingo.weinzierl@intevation.de>
#  * Bernhard Reiter <bernhard.reiter@intevation.de>
#
# This is Free Software licensed unter the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.

import locale
import re

from datetime import datetime, timedelta


class Project(object):

    def __init__(self, backend, id, key, desc, total):
        self.backend = backend
        self.id = id
        self.key = key
        self.desc = desc
        self._entries = None
        self.total = total
        self.start = None
        self.stop = None

    def year(self):
        total = 0
        now = datetime.now()
        for entry in self.entries:
            start = entry.start
            if start.year == now.year:
                total += (entry.end - start).seconds
        return total

    def month(self):
        total = 0
        now = datetime.now()
        for entry in self.entries:
            start = entry.start
            if start.month == now.month and start.year == now.year:
                total += (entry.end - start).seconds
        return total

    def week(self):
        total = 0
        now = datetime.now()
        tweek = now.strftime('%W')
        for entry in self.entries:
            start = entry.start
            if start.strftime('%W') == tweek and start.year == now.year:
                total += (entry.end - start).seconds
        return total

    def day(self):
        total = 0
        now = datetime.now()
        for entry in self.entries:
            start = entry.start
            if start.month == now.month and start.year == now.year \
                    and start.day == now.day:
                total += (entry.end - start).seconds
        return total

    def load_entries(self, year=None, week=None):
        self._entries = self.backend.load_entries(self.id, year, week)

    @property
    def entries(self):
        if self._entries is None:
            self.load_entries()
        return self._entries

    def get_total_duration(self):
        dur = timedelta(0)
        for entry in self.entries:
            dur += entry.get_duration()
        return dur


class Entry(object):

    WORKPACKAGE = re.compile("^\[([^\s\]]+)(\s|\])")

    def __init__(self, id, project_id, start, end, desc):
        self.id = id
        self.project_id = project_id
        self.start = start
        self.end = end
        self.desc = desc
        self.workpackage = "-"

        # we add this attribute for use in jinja2 templates,
        # as filters like sort() or groupby() work only on attributes
        # and sorting or grouping by day is common for reporting
        self.startisoday = start.date().isoformat()

        # carefully handle non unicode string
        # urwid seems to have some issue with plain str
        if self.desc and not isinstance(self.desc, unicode):
            self.desc = unicode(self.desc, locale.getpreferredencoding())

        c = self.desc
        if c:
            m = self.WORKPACKAGE.match(c)
            if m:
                self.workpackage = m.group(1)
                c = c[m.end():].strip()
            c = c.replace('\x1b', '')
        self.comment = c

    def get_workpackage(self):
        return self.workpackage

    def get_duration(self):
        return (self.end - self.start)

    def get_comment(self):
        return self.comment

    def __str__(self):
        return ("[%s | %s | %s | %s | %s]" %
                (self.id, self.project_id, self.start, self.end, self.desc))

# vim:set ts=4 sw=4 si et sta sts=4 fenc=utf8:
