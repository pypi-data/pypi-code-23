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

#------------- regular expresion for  2x[6]-IPE120-2500-S355
#=================================+====0  2    4      6   8

re_text = re.compile('\A\s*(\d*)(x*)\[(\d+)\](-*)([a-zA-Z0-9_, ]*)(-*)(\d*)(-*)(.*)\s*\Z')
                  
def has_correct_format(text):
    if re_text.search(text):
        return True
    else:
        return False

def is_maintext(text):
    if has_correct_format(text):
        data = data_get(text)
        if data['Length']:
            return True
        else:
            return False
    else:
        return False

def data_get(text):
    if has_correct_format(text):
        data = re_text.findall(text)[0]
        #---
        Number = data[0]
        if Number == '': Number = 0
        else: Number = int(Number)
        #---
        Mark = data[2]
        #---
        Sect = data[4]
        if Sect == '': Sect = None
        #---
        #---
        Length = data[6]
        if Length == '': Length = None
        else: Length = float(Length)
        #---
        Grade = data[8]
        if Grade == '': Grade = None
        #---
        return {'Number':Number, 'Mark':Mark, 'Sect':Sect, 'Length':Length, 'Grade':Grade}
    else:
        return None

def data_change(text, newNumber=None, newMark=None, newSect=None):
    if has_correct_format(text):
        #--------geting data----------------
        data = data_get(text)
        #---------changing data---------------
        Mark = data['Mark']
        if newMark: Mark = newMark
        #---
        Sect = data['Sect']
        if newSect and Sect : Sect = newSect
        #------------Back to string------------
        if not Sect : Sect = ''
        #------changing text----------
        changedtext = re_text.sub(r'\1\2[%s]\4%s\6\7\8\9'%(Mark, Sect), text)
        return changedtext
       
# Test if main        
if __name__ == "__main__":
    text = '2x[6]-IPE 100-2500-S355'
    print re_text.findall(text)    
    
    print has_correct_format('2x[6]-IPE-2500-S355')
    
    print data_get('2x[6]-IPE 350-2500-S355')
    print data_get('2x[6]-IPE-2500')
    print data_get('2x[6]-IPE')
    print data_get('2x[6]')
    
    print data_change('1x[6]-hjhj-2500-ST22', newNumber=0, newMark='1', newSect='HEB 50')
