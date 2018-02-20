# Copyright (C) 2007-2018 Gaetan Delannay

# This file is part of Appy.

# Appy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Appy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Appy. If not, see <http://www.gnu.org/licenses/>.

# ------------------------------------------------------------------------------
import time
from appy.shared.utils import Traceback

# Some POD-specific constants --------------------------------------------------
XHTML_HEADINGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
XHTML_LISTS = ('ol', 'ul')
# "para" is a meta-tag representing p, div or blockquote
XHTML_PARA_TAGS = XHTML_HEADINGS + ('p', 'div', 'blockquote', 'para')
XHTML_INNER_TAGS = ('b', 'i', 'u', 'em', 'span')
XHTML_UNSTYLABLE_TAGS = ('li', 'a')
XHTML_META_TAGS = {'p': 'para', 'div': 'para', 'blockquote': 'para'}

# ------------------------------------------------------------------------------
class PodError(Exception):
    @staticmethod
    def dumpTraceback(buffer, tb, removeFirstLine):
        # If this error came from an exception raised by pod (p_removeFirstLine
        # is True), the text of the error may be very long, so we avoid having
        # it as error cause + in the first line of the traceback.
        linesToRemove = removeFirstLine and 3 or 2
        i = 0
        for tLine in tb.splitlines():
            i += 1
            if i > linesToRemove:
                buffer.write('<text:p>')
                try:
                    buffer.dumpContent(tLine)
                except UnicodeDecodeError:
                    buffer.dumpContent(tLine.decode('utf-8'))
                buffer.write('</text:p>')

    @staticmethod
    def dump(buffer, message, withinElement=None, removeFirstLine=False,
             dumpTb=True):
        '''Dumps the error p_message in p_buffer or in r_ if p_buffer is None'''
        if withinElement:
            buffer.write('<%s>' % withinElement.OD.elem)
            for subTag in withinElement.subTags:
                buffer.write('<%s>' % subTag.elem)
        buffer.write('<office:annotation><dc:creator>POD</dc:creator>' \
          '<dc:date>%s</dc:date><text:p>' % time.strftime('%Y-%m-%dT%H:%M:%S'))
        buffer.dumpContent(message)
        buffer.write('</text:p>')
        if dumpTb:
            # We don't dump the traceback if it is an expression error (it is
            # already included in the error message).
            PodError.dumpTraceback(buffer, Traceback.get(), removeFirstLine)
        buffer.write('</office:annotation>')
        if withinElement:
            subTags = withinElement.subTags[:]
            subTags.reverse()
            for subTag in subTags:
                buffer.write('</%s>' % subTag.elem)
            buffer.write('</%s>' % withinElement.OD.elem)
# ------------------------------------------------------------------------------
