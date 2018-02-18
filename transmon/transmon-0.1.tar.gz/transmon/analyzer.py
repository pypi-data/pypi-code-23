#   Copyright (c) 2018 Julien Lepiller <julien@lepiller.eu>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
####
import os
import polib
from androidstringslib import android

class Analyzer(object):
    def __init__(self):
        return

    def analyze(self, path):
        raise Exception('Not implemented')

class AndroidAnalyzer(Analyzer):
    def __init__(self):
        Analyzer.__init__(self)

    def analyze(self, path):
        respath = path + '/app/src/main/res'
        dirs = os.listdir(respath)
        dirs = [(respath + "/" + x) for x in dirs if 'strings.xml' in os.listdir(respath + "/" + x)]
        res = {}
        for p in dirs:
            if p.endswith('values'):
                continue
            an = android(respath + '/values/strings.xml', p + '/strings.xml')
            translated = 0
            number = len(an)
            for entry in an:
                if entry.dst != '':
                    translated = translated + 1
            res[p[-2:]] = (translated, number)
        return res
