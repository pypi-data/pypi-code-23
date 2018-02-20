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
import appy
import os.path

# ------------------------------------------------------------------------------
appyPath = os.path.realpath(os.path.dirname(appy.__file__))
od = 'application/vnd.oasis.opendocument'
ms = 'application/vnd.openxmlformats-officedocument'
ms2 = 'application/vnd.ms'

mimeTypes = {'odt': '%s.text' % od,
             'ods': '%s.spreadsheet' % od,
             'doc': 'application/msword',
             'rtf': 'text/rtf',
             'pdf': 'application/pdf'
             }
mimeTypesExts = {
    '%s.text' % od:        'odt',
    '%s.spreadsheet' % od: 'ods',
    'application/msword':  'doc',
    'text/rtf':            'rtf',
    'application/pdf':     'pdf',
    'image/png':           'png',
    'image/jpeg':          'jpg',
    'image/pjpeg':         'jpg',
    'image/gif':           'gif',
    '%s.wordprocessingml.document' % ms: 'docx',
    '%s.spreadsheetml.sheet' % ms: 'xlsx',
    '%s.presentationml.presentation' % ms: 'pptx',
    '%s-excel' % ms2:      'xls',
    '%s-powerpoint' % ms2: 'ppt',
    '%s-word.document.macroEnabled.12' % ms2: 'docm',
    '%s-excel.sheet.macroEnabled.12' % ms2: 'xlsm',
    '%s-powerpoint.presentation.macroEnabled.12' % ms2: 'pptm'
}

# ------------------------------------------------------------------------------
class UnmarshalledFile:
    '''Used for producing file objects from a marshalled Python object.'''
    def __init__(self):
        self.name = '' # The name of the file on disk
        self.mimeType = None # The MIME type of the file
        self.content = '' # The binary content of the file or a file object
        self.size = 0 # The length of the file in bytes.

class UnicodeBuffer:
    '''With StringIO class, I have tons of encoding problems. So I define a
       similar class here, that uses an internal unicode buffer.'''
    def __init__(self):
        self.buffer = []
    def write(self, s):
        if s == None: return
        if isinstance(s, unicode):
            self.buffer.append(s)
        elif isinstance(s, str):
            self.buffer.append(s.decode('utf-8'))
        else:
            self.buffer.append(unicode(s))
    def getValue(self):
        return u''.join(self.buffer)
# ------------------------------------------------------------------------------
