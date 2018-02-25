# -*- coding: utf-8 -*-
# tatorter
# Copyright (C) 2018  Daniel Llin Ferrero
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
Created on 05.02.2018

@author: DLF
'''
from fuzzywuzzy import fuzz
import os

class Episode(object):
    def __init__(self, **kwargs):
        self._attribs = []
        for key, val in kwargs.items():
            setattr(self, key, val)
            self._attribs.append(key)
        for must_have in ["episode_index","title","location","broadcaster"]:
            assert must_have in self._attribs
    @property
    def as_dict(self):
        result = {}
        for attrib in self._attribs:
            result[attrib] = getattr(self, attrib)
        return result
    def match(self, file_name):
        file_name = os.path.splitext(os.path.basename(file_name))[0].lower()
        title = self.title.lower()
        broadcaster = self.broadcaster.lower()
        value = fuzz.partial_ratio(title, file_name)
        #max 100
        if broadcaster in file_name:
            value +=10
        #max 110
        if str(self.episode_index) in file_name:
            value += 5 * len(str(self.episode_index))
        #max 130
        value = int(100 * value / 130)
        return value  
        
    
class Matcher(object):
    def __init__(self, file_name, episodes):
        self.match_list = []
        for episode in episodes:
            value = episode.match(file_name)
            self.match_list.append((value, episode))
        self.match_list.sort(key=lambda e:e[0], reverse=True)
    