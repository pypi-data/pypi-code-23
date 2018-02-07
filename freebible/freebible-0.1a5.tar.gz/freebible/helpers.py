# -*- coding: utf-8 -*-

'''
Common bible processing functions
Latest version can be found at https://github.com/neocl/freebible

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2018, Le Tuan Anh <tuananh.ke@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

########################################################################

import logging

from chirptext import TextReport

from freebible.data import KOUGO_PATH
from freebible.parsers.kougo import parse_kougo
from freebible.data import WEB_VERSES, WEB_BOOKS, WEB_ABBRS
from freebible.parsers.web import parse_web, read_abbr


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------

def read_kougo():
    ''' Read Japanese Colloquial Bible (口語訳) '''
    return parse_kougo(KOUGO_PATH)


def read_web():
    ''' Read World English Bible '''
    return parse_web(WEB_VERSES, WEB_BOOKS, WEB_ABBRS)


def bookmap():
    ''' return World English Bible standard books mapping information (i.e. book names) '''
    return read_abbr(WEB_ABBRS)


class Bibles(object):

    def __init__(self):
        self.__kougo = None
        self.__web = None

    @property
    def kougo(self):
        ''' Singleton Kougo '''
        if not self.__kougo:
            self.__kougo = read_kougo()
        return self.__kougo

    @property
    def web(self):
        ''' Singleton WEB '''
        if not self.__web:
            self.__web = read_web()
        return self.__web

    def printlines(self, lines, output=None):
        if output:
            for line in lines:
                output.write(line)
                output.write('\n')

    def quote(self, book_key, cid=None, vid=None, output=None):
        quotes = [b.quote(book_key, cid, vid) for b in (self.kougo, self.web)]
        self.printlines(quotes, output=output)
        return quotes

    def print(self, book_key, cid=None, vid=None):
        ''' Quote bibles to standard output '''
        return self.quote(book_key, cid=cid, vid=vid, output=TextReport())


bibles = Bibles()
