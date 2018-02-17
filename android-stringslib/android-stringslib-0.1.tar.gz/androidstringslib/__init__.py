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

from .parser import entry, parser

class android(list):
    def __init__(self, origin, destination):
        list.__init__(self)
        self.origin = parser(origin)
        self.destination = parser(destination)
        keys = self.origin.getKeyValues()
        for k in keys:
            trans = self.destination.getById(k.id)
            txt = trans.orig
            if trans.type != k.type:
                txt = ''
            comm = None
            if k.comment != None:
                comm = k.comment
            if trans.comment != None:
                comm = trans.comment
            self.append(entry(k.type, k.id, k.orig, txt, comm))

    def save(self):
        keyvalues = []
        for k in self:
            keyvalues.append(entry(k.type, k.id, k.dst, '', k.comment))
        self.destination.set(keyvalues)
        self.destination.save()

