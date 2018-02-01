#iowin - Part of tamcolors
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

from os import system
from sys import stdout

from tamcolors.similarities import*
from tamcolors import _tamcolors

colorNameToNumber = {"black"        :  0,
                     "blue"         :  1,
                     "green"        :  2,
                     "aqua"         :  3,
                     "red"          :  4,
                     "purple"       :  5,
                     "yellow"       :  6,
                     "white"        :  7,
                     "gray"         :  8,
                     "light blue"   :  9,
                     "light green"  : 10,
                     "light aqua"   : 11,
                     "light red"    : 12,
                     "light purple" : 13,
                     "light yellow" : 14,
                     "bright white" : 15}

colorOutPuts = ["<_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>"]

def _getSingleColor(singleColor):
    if type(singleColor) == str:
        return colorNameToNumber[singleColor.lower()]
    elif singleColor == None:
        return -1
    return singleColor

def _getColorToText(value, background):
    if colorToText and str(stdout) not in colorOutPuts:
        return str(value).replace(" ", colorToTextList[_getSingleColor(background)])
    return value

def _printc(value, foreground, background, bypassCTT):
    _tamcolors._setColor(_getSingleColor(foreground), _getSingleColor(background))
    if bypassCTT:
        print(value, end ='', flush = True)
    else:
        print(_getColorToText(value, background), end ='', flush = True)
        
    _tamcolors._goToDefault()

def printc(*value, sameColor = False, sep = ' ', end = '\n', bypassCTT = False):
    _printc("",-1, -1, bypassCTT)
    if sameColor:
        for v in range(len(value) - 1):
            if v != 0:
                _printc(sep, value[-1][0], value[-1][1], bypassCTT)#sep
                
            _printc(value[v], value[-1][0], value[-1][1], bypassCTT)#value

        _printc(end, value[-1][0], value[-1][1], bypassCTT)#end
    else: 
        for v in range(0, len(value), 2):
            if v != 0:
                _printc(sep, value[v - 1][0], value[v - 1][1], bypassCTT)#sep
                    
            _printc(value[v], value[v + 1][0], value[v + 1][1], bypassCTT)#value

        _printc(end, value[-1][0], value[-1][1], bypassCTT)#end

def inputc(value, color, bypassCTT = False):
    _tamcolors._setColor(_getSingleColor(color[0]), _getSingleColor(color[1]))
    if bypassCTT:
        userInput = input(value)
    else:
        userInput = input(_getColorToText(value, color[0]))
    _tamcolors._goToDefault()
    return userInput

def clear():
    if str(stdout) in colorOutPuts:
        system("cls")
    else:
        print("\n"*clearJumper, end = '')

def colorToTextSetter(position = False):
    global colorToText
    colorToText = position

def clearJumperSetter(jumpCount = 0):
    global clearJumper
    clearJumper = jumpCount


