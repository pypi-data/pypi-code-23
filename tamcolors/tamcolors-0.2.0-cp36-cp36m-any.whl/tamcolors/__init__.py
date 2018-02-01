#tamcolors AKA Tammy Colors
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

__version__ = "1.0.0"

"""simple terminal color manager

colors:
    *None          -1
    *black          0
    *blue           1
    *green          2
    *aqua           3
    *red            4
    *purple         5
    *yellow         6
    *white          7
    *gray           8
    *light blue     9
    *light green   10
    *light aqua    11
    *light red     12
    *light purple  13
    *light yellow  14
    *bright white  15
    
--------------------------------------------------------------------
from tamcolors import*

colorToTextSetter(True)
clearJumperSetter(50)

def main():
    print("milk")
    printc("index", (4,11), "101", (15, None), bypassCTT = True)
    printc("kitty", "cat", ("light aqua", -1), sameColor = True)
    print("USA")
    inputc(">>> ",(11, -1))
    clear()
    print("hi")
    input(">>> ")

main()
--------------------------------------------------------------------"""

#Version 1.0.0:

#   -iowin & ioother-
#   *Made printc
#   *Made inputc
#   *Made clear
#   *Made adoSpaceTF
#   *Made setAdoClear

#   -buffermanager-
#   *Made textBuffer
#       *Made new
#       *Made fill
#       *Made place
#       *Made printt
#       *Made drawOn

__all__ = ["printc",
           "inputc",
           "clear",
           "colorToTextSetter",
           "colorToTextList",
           "clearJumperSetter",
           "colorOutPuts",
           "textBuffer",
           "__version__"]

from sys import platform
try:
    from tamcolors.iowin import*
except:
    from tamcolors.iodarwin import*
    
from tamcolors.buffermanager import*




