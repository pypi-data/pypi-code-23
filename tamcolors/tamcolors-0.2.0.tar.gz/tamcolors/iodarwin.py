#iodarwin - Part of tamcolors
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

from sys import stdout
from tamcolors.similarities import*

colorNameToString = {"black"        : '0'  ,
                     "blue"         : '4'  ,
                     "green"        : '28' ,
                     "aqua"         : '32' ,
                     "red"          : '1'  , 
                     "purple"       : '89' ,
                     "yellow"       : '100',
                     "white"        : '7'  ,
                     "gray"         : '8'  ,
                     "light blue"   : '21' ,
                     "light green"  : '46' ,
                     "light aqua"   : '45' ,
                     "light red"    : '196' ,
                     "light purple" : '200' ,
                     "light yellow" : '184' ,
                     "bright white" : '255' }

NumberToString = {-1 : '',
                  0  : '0',
                  1  : '4',
                  2  : '28',
                  3  : '32',
                  4  : '1',
                  5  : '89',
                  6  : '100',
                  7  : '7',
                  8  : '8',
                  9  : '21',
                  10 : '46',
                  11 : '45',
                  12 : '196',
                  13 : '200',
                  14 : '184',
                  15 : '255'}

StringToNumber = {''    : 16,
                  '0'   : 0,
                  '4'   : 1,
                  '28'  : 2,
                  '32'  : 3,
                  '1'   : 4,
                  '89'  : 5,
                  '100' : 6,
                  '7'   : 7,
                  '8'   : 8,
                  '21'  : 9,
                  '46'  : 10,
                  '45'  : 11,
                  '196' : 12,
                  '200' : 13,
                  '184' : 14,
                  '255' : 15}

colorOutPuts = ["<_io.TextIOWrapper name='<stdout>' mode='w' encoding='UTF-8'>"]

def _getSingleColor(singleColor):
    if singleColor == None:
        return ''
    elif type(singleColor) == str:
        return colorNameToString[singleColor.lower()]
    elif type(singleColor) == int:
        return NumberToString[singleColor]

    return str(singleColor)

def _getColorToText(value, background):
    return value.replace(' ', colorToTextList[StringToNumber[background]])

def _getUColor(foreground, background):
    if foreground != '' and background != '':
        return u"\u001b[38;5;" + foreground + ";48;5;" + background + "m"
    elif foreground != '':
        return u"\u001b[38;5;" + foreground + "m"
    elif background != '':
        return u"\u001b[48;5;" + background + "m"
    else:
        return u"\u001b[0m"

def _printc(value, foreground, background, bypassCTT):
    if str(stdout) in colorOutPuts:
        foreground = _getSingleColor(foreground)
        background = _getSingleColor(background)
        setColor = _getUColor(foreground, background)
        stdout.write(setColor)
        stdout.write(str(value))
        stdout.write("\u001b[0m")
        stdout.write("\u001b[0m")
    else: 
        if bypassCTT:
            stdout.write(str(value))
        else:
            background = _getSingleColor(background)
            stdout.write(_getColorToText(str(value), background))
        

def printc(*value, sameColor = False, sep = ' ', end = '\n', bypassCTT = False):
    if sameColor:
        for v in range(len(value) - 1):
            if v != 0:
                _printc(sep, value[-1][0], value[-1][1], bypassCTT)#sep
                
            _printc(value[v], value[-1][0], value[-1][1], bypassCTT)#value
        try:
            if end[-1] == '\n':
                _printc(end[:-1], value[-1][0], value[-1][1], bypassCTT)#end
                print()
            else:
                _printc(end, value[-1][0], value[-1][1], bypassCTT)
        except:
            pass
    else: 
        for v in range(0, len(value), 2):
            if v != 0:
                _printc(sep, value[v - 1][0], value[v - 1][1], bypassCTT)#sep
                    
            _printc(value[v], value[v + 1][0], value[v + 1][1], bypassCTT)#value
        try:
            if end[-1] == '\n':
                _printc(end[:-1], value[-1][0], value[-1][1], bypassCTT)#end
                print()
            else:
                _printc(end, value[-1][0], value[-1][1], bypassCTT)
        except:
            pass

def inputc(value, color, bypassCTT = False):
    if str(stdout) in colorOutPuts:
        foreground = _getSingleColor(color[0])
        background = _getSingleColor(color[1])
        setColor = _getUColor(foreground, background)
        stdout.write(setColor)

        ui = input(str(value))

        stdout.write("\u001b[0m")
        stdout.write("\u001b[0m")

    else:      
        if bypassCTT:
            ui = input(str(value))
        else:
            background = _getSingleColor(background)
            ui = input(_getColorToText(str(value), background))

    return ui

def clear():
    if str(stdout) in colorOutPuts:
        print("\n"*50, end = '')
    else:
        print("\n"*clearJumper, end = '')

def colorToTextSetter(position = False):
    global colorToText
    colorToText = position

def clearJumperSetter(jumpCount = 0):
    global clearJumper
    clearJumper = jumpCount   
