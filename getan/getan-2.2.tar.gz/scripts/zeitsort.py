#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# zeitsort
# --------
# (c) 2008 by Sascha L. Teichmann <sascha.teichmann@intevation.de>
#
# Simple script which sorts lines of zeiterfassung.txt files by date.
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#

import sys
import re

from datetime import date

DATE = re.compile("(\d\d)\.(\d\d)\.(\d\d\d\d)")

def date_cmp(a, b):
    ma = DATE.search(a)
    mb = DATE.search(b)
    if not ma and not mb: return cmp(a, b)
    if ma and not mb: return -1
    if not ma and mb: return +1
    da = date(int(ma.group(3)), int(ma.group(2)), int(ma.group(1)))
    db = date(int(mb.group(3)), int(mb.group(2)), int(mb.group(1)))
    return cmp(da, db)

def main():
    all = []
    while True:
        line = sys.stdin.readline()
        if not line: break
        if not DATE.search(line):
            # handle multi lines
            if not all: all.append(line)
            else:       all[-1] += line
        else:
            all.append(line)
    all.sort(date_cmp)
    sys.stdout.write(''.join(all))
    sys.stdout.flush()

if __name__ == '__main__':
    main()

# vim:set ts=4 sw=4 si et sta sts=4 fenc=utf8:
