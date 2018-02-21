#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  include.py
#
#  Based on code Copyright 2015 Christopher MacMackin <cmacmackin@gmail.com>
#
#  Copyright 2018 Christopher Jefferson <chris@bubblescope.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


from __future__ import print_function
import re
import os.path
from codecs import open
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
import importlib
from six import string_types

INC_SYNTAX = re.compile(r'\{!([A-Z])\s*(.+?)\s*!\}')


class MarkdownSwiss(Extension):
    def __init__(self, configs={}):
        self.config = {
            'base_path': ['.', 'Default location from which to evaluate ' \
                'relative paths for the include statement.'],
            'encoding': ['utf-8', 'Encoding of the files used by the include ' \
                'statement.']
        }
        for key, value in configs.items():
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add(
            'include', IncludePreprocessor(md,self.getConfigs()),'_begin'
        )

class IncludePreprocessor(Preprocessor):
    def funcF(self, m):
        filename = m.group(2)
        if not os.path.isabs(filename):
            filename = os.path.normpath(
                os.path.join(self.base_path,filename)
            )
        try:
            with open(filename, 'r', encoding=self.encoding) as r:
                text = [x.rstrip() for x in r.readlines()]
        except Exception as e:
            print('Warning: could not find file {}. Ignoring '
                'include statement. Error: {}'.format(filename, e))
            return ""
        return text

    def funcE(self, m):
        code = m.group(2)
        return eval(code)

    def funcI(self, m):
        lib = m.group(2)
        globals()[lib] = importlib.import_module(lib)
        return ""

    def funcX(self, m):
        code = m.group(2)
        exec(code)
        return ""

    '''
    This provides an "include" function for Markdown, similar to that found in
    LaTeX (also the C pre-processor and Fortran). The syntax is {!filename!},
    which will be replaced by the contents of filename. Any such statements in
    filename will also be replaced. This replacement is done prior to any other
    Markdown processing. All file-names are evaluated relative to the location
    from which Markdown is being called.
    '''
    def __init__(self, md, config):
        super(IncludePreprocessor, self).__init__(md)
        self.base_path = config['base_path']
        self.encoding = config['encoding']
        self.options = {
            'F' : self.funcF,
            'E' : self.funcE,
            'I' : self.funcI
        }

    def run(self, lines):
        done = False
        while not done:
            for line in lines:
                loc = lines.index(line)
                m = INC_SYNTAX.search(line)

                if m:
                    command = m.group(1)
                    text = self.options[command](m)
                    if isinstance(text, string_types):
                        text = [text]
                    line_split = INC_SYNTAX.split(lines[loc], maxsplit = 1)
                    if len(text) == 0: text.append('')
                    text[0] = line_split[0] + text[0]
                    text[-1] = text[-1] + line_split[-1]
                    lines = lines[:loc] + text + lines[loc+1:]
                    break
            else:
                done = True
        return lines


def makeExtension(*args,**kwargs):
    return MarkdownSwiss(kwargs)
