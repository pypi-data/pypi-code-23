# License: MIT (expat)
#
# This script is heavily inspired by android-localization-helper
# by Jordan Jozwiak.
# 
# Copyright (c) 2018 Julien Lepiller <julien@lepiller.eu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#####

import xml.etree.ElementTree as ET
import os

# http://effbot.org/zone/element-pi.htm
# Allows to parse comments
class AndroidParser(ET.TreeBuilder):
    def __init__(self):
        ET.TreeBuilder.__init__(self)
    
    def comment(self, data):
        self.start(ET.Comment, {})
        self.data(data)
        self.end(ET.Comment)

# in-place prettyprint formatter
# http://effbot.org/zone/element-lib.htm#prettyprint
def indent(elem, level=0):
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

class entry(object):
    """Represents an entry in the strings file."""
    def __init__(self, type, id, orig, dst, comment=None):
        self.type = type
        self.id = id
        self.orig = orig
        self.dst = dst
        self.comment = comment

    def __str__(self):
        return "<entry type:" + self.type + ", id: "+self.id+", original: \"" + str(self.orig) + "\", translation: \"" + str(self.dst) + "\", comment: \"" + comment + "\">"

class parser(object):
    """Parse a strings.xml file"""
    def __init__(self, file):
        self.file = file
        if(os.path.isfile(file)):
            self.content = ET.parse(file, parser=ET.XMLParser(target=AndroidParser()))
            self.keyvalues = self.getKeyValues()
        else:
            raise Exception('File not found')

    def getKeys(self):
        root = self.content.getroot()
        keys = []
        comment = ''
        for child in root:
            # ignore strings that can't be translated
            if child.get('translatable', default='true') == 'false':
                continue
            # ignore providers
            if (child.get('name').startswith('provider.')):
                continue
            keys.append((child.tag, child.get('name')))
        return keys

    def getKeyValues(self):
        root = self.content.getroot()
        values = []
        comment = None
        for child in root:
            # ignore strings that can't be translated
            if child.get('translatable', default='true') == 'false':
                continue
            if not isinstance(child.tag, str):
                comment = child.text
                continue
            # ignore providers
            if (child.get('name').startswith('provider.')):
                continue
            value = []
            if(child.tag == "string"):
                value = child.text
            else:
                for c in child:
                    value.append(c.text)
            values.append(
                entry(child.tag, child.get('name'), value, '', comment))
            if comment != None:
                comment = None
        return values

    def getById(self, id):
        for k in self.keyvalues:
            if k.id == id:
                return k
        return entry('string', id, '', '')

    def set(self, keyvalues):
        self.keyvalues = keyvalues

    def save(self):
        root = ET.Element('resources')
        tree = ET.ElementTree(root)
        for data in self.keyvalues:
            if data.comment != None:
                c = ET.Comment(data.comment)
                root.append(c)
            v = ET.SubElement(root, data.type)
            v.set('name', data.id)
            if data.type == "string-array":
                for val in data.orig:
                    item = ET.SubElement(v, 'item')
                    item.text = val
            else:
                v.text = data.orig
        indent(root)
        tree.write(self.file, "UTF-8")
