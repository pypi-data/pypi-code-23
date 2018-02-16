#!/usr/bin/env python
# encoding: utf-8

"""
utf8file.py

Created by Hywel Thomas on 2010-11-25.
Copyright (c) 2010 Hywel Thomas. All rights reserved.
"""

import codecs
import os
from conversionutil import convert_to_unicode


class UTF8File(object):
    def __init__(self,
                 filename,
                 mode='r'):
        self.filename = filename
        self.file = None
        self.mode = mode
        self.open()

    def reset(self):
        self.open()

    def write(self,
              string_to_write):
        self.file.write(convert_to_unicode(u'%s' % string_to_write))

    def writeln(self,
                string_to_write):
        self.write(u'{string}{newline}'.format(string=string_to_write,
                                               newline=os.linesep))

    def readline(self):
        line = self.file.readline()
        return line.rstrip()

    def read(self):
        self.reset()
        whole_file = self.file.read()
        self.close()
        return whole_file

    @property
    def contents(self):
        return self.read()

    def open(self):
        self.file = codecs.open(filename=self.filename,
                                encoding='UTF-8',
                                mode=self.mode)

    def close(self):
        self.file.close()


def file_contents(filename):
    return UTF8File(filename).contents()


if __name__ == '__main__':
    # TODO: Convert to unittests
    x = UTF8File('UTF8Test.txt', 'w')
    x.write(u'â')
    x.close()
    x = UTF8File('UTF8Test.txt', 'a')
    x.writeln(u'âêîôûŷŵÂÊÎÔÛŴŶ')
    x.writeln(u'line2')
    x.writeln(u'[§2]')
    x.close()
    x = UTF8File('UTF8Test.txt', 'r')
    print 'read this -->', x.readline(), '<--'
    for line in x.file:
        print line
    x.close()

    print "whole file:*%s*" % x.contents()
