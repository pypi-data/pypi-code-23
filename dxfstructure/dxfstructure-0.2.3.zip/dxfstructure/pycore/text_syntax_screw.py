'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1 date 2017-08-10
This file is part of DxfStructure (structural engineering dxf drawing system).
http://struthon.org/

DxfStructure is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

DxfStructure is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

import re


#------------- regular expresion for  5xM16x250-8.8
#                            5   x    M16  x   250 -     8.8
#                            0          2       4         6
re_text = re.compile('\A\s*(\d*)(x*)([A-Z0-9_ ]+)(x*)(\d*)(-*)([a-zA-Z0-9_. ]*)\s*\Z')
                  
def has_correct_format(text):
    if re_text.search(text):
        return True
    else:
        return False

def data_get(text):
    if has_correct_format(text):
        data = re_text.findall(text)[0]
        #---
        Number = data[0]
        if Number == '': Number = 1
        else: Number = int(Number)
        #---
        Screwtype = data[2]
        if Screwtype == '': Screwtype = None
        #---
        #---
        Length = data[4]
        if Length == '': Length = None
        else: Length = float(Length)
        #---
        Grade = data[6]
        if Grade == '': Grade = None
        #---
        return {'Number':Number, 'Screwtype':Screwtype, 'Length':Length, 'Grade':Grade}
    else:
        return None
       
# Test if main        
if __name__ == "__main__":
    text = '3xM16x250-8.8'
    print re_text.findall(text)
    print has_correct_format('2x[6]-HE 100 A-1140-S355')
    print data_get('3xHILTI HAS M16x200-8.8')
    print data_get('3xHILTI HAS M16-8.8')
    print data_get('dfdgsg')
