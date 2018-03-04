'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2017-06-01
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

#-----regular expresion for 'Element Bk1 x 2' ------

re_text = re.compile('\s*Element (.*) x (\d+)\s*')
                  
def has_correct_format(text):
    if re_text.search(text):
        return True
    else:
        return False

def data_get(text):
    if has_correct_format(text):
        data = re_text.findall(text)[0]
        #---
        Name = data[0] 
        Number = float(data[1])
        #---
        return { 'Number':Number, 'Name':Name }
    else:
        return None

# Test if main        
if __name__ == "__main__":
    test_text = 'Element Bk-5 x s'
    print has_correct_format(test_text)
    print data_get(test_text)