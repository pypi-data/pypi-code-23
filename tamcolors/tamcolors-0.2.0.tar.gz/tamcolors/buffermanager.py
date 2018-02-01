#buffermanager - Part of tamcolors
#Copyright (C) 2018  Charles McMarrow
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from copy import copy, deepcopy

try:
    from tamcolors.iowin import*
except:
    from tamcolors.iodarwin import*

class textBuffer:
    def __init__(self, value, color, w, h):
        self.new(value, color, w, h)

    def new(self, value, color, w, h):
        role = [[value, color[0], color[1]] for c in range(w)]
        self.buffer = [deepcopy(role) for r in range(h)]
        
   
    def fill(self, value = "NC", foreground = "NC", background = "NC"):
        for role in self.buffer:
            for c in role:
                if value != "NC":
                    c[0] = copy(value)
                if foreground != "NC":
                    c[1] = copy(foreground)
                if background != "NC":
                    c[2] = copy(background)
        
    def place(self, x, y, value = "NC", foreground = "NC", background = "NC"):
        try:
            if value == "NC":   
                if foreground != "NC":
                    self.buffer[y][x][1] = foreground
                if background != "NC":
                    self.buffer[y][x][2] = background
            else:
                for num, v in enumerate(value):
                    self.buffer[y][x + num][0] = v
                    if foreground != "NC":
                        self.buffer[y][x + num][1] = foreground
                    if background != "NC":
                        self.buffer[y][x + num][2] = background           
        except:
            pass
        
    def printt(self):
        for role in self.buffer:
            chunk = ""
            foreground = "NC"
            background = "NC"
            for c in role:  #Group up text with same colors
                if foreground == "NC" and background == "NC":
                    chunk = c[0]
                    foreground = c[1]
                    background = c[2]
                elif foreground == c[1] and background == c[2]:
                    chunk += c[0]
                else:
                    printc(chunk,(background, foreground), end = '')
                    chunk = c[0]
                    foreground = c[1]
                    background = c[2]
                    
            printc(chunk,(background, foreground))  #end of line
                  
    def drawOn(self, buffer2, x, y):
        for numy, role in enumerate(buffer2.buffer):
            for numx, data in enumerate(role):
                try:
                    self.buffer[y + numy][x + numx] = copy(data)
                except:
                    pass
    
