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

#------------- regular expresion for '5#12-[5]-200DG' ----------
re_text = re.compile('\A\s*(\d*)#(\d+)-\[(\d+)\](-*)(\d*)(\D*)\s*\Z')
                  
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
        if Number == '': Number = 0
        else: Number = int(Number)
        #---
        Type = '#'
        #---
        Size = int(data[1])
        #---
        Mark = data[2]
        #---
        Centre = data[4]
        if Centre == '': Centre = None
        else: Centre = int(Centre)   
        #---
        Location = data[5]
        #---
        Total_Number = Number
        if len(Location):
            Total_Number *= len(Location)
        #---
        return {    'Number':Number, 'Type':Type, 'Size':Size, 'Mark':Mark, 
                    'Centre':Centre, 'Location':Location, 'Total_Number':Total_Number}
    else:
        return None

def data_change(text, newNumber=None, newType=None, newSize=None, newMark=None):
    if has_correct_format(text):
        #--------geting data----------------
        data = data_get(text)
        #---------changing data---------------
        Number = data['Number']
        if newNumber: Number = newNumber
        #---
        Type = data['Type']
        if newType: Type = newType
        #---
        Size = data['Size']
        if newSize: Size = newSize
        #---
        Mark = data['Mark']
        if newMark: Mark = newMark
        #------------Back to string------------
        if Number == 0: Number = ''
        #------changing text----------
        changedtext = re_text.sub(r'%s%s%s-[%s]\4\5\6'%(Number, Type, Size, Mark), text)
        return changedtext
        
        
# Test if main        
if __name__ == "__main__":
    
    for text in [   '#12-[5]',
                    '5#12-[5]',
                    '#12-[5]-DG',
                    '5#12-[5]-200',
                    '#12-[5]-200',
                    '5#12-[5]-200DGD',
                    '5#12-[5]-200DMG',
                    '5@12-[5]-200DG'    ]:
        print '-----------------------------'
        print text
        print data_get(text)
    
    print data_change('60#12-[5]', newNumber=None, newType=None, newSize=20, newMark='6')
    
    #T1 = '10#12-[5]'
    #pT1 = re.compile('\A\s*(\d*)#(\d+)-\[(\d+)\]\s*\Z')
    #print pT1.search(T1).group()
    
    #T2 = '5#12-[5]-200DG'
    #pT2 = re.compile('\A\s*(\d*)#(\d+)-\[(\d+)\]-(\d*)(\D*)\s*\Z')
    #print pT2.search(T2).group()
    #print pT2.sub(r'\1#\2-[\3]-\4\5', T2)

    #NUMBER = 50
    #MARK = 10
    #print pT2.sub(r'%s#\2-[%s]-\4\5'%(NUMBER, MARK), T2)        
    
    #print 't333333'
    #T3 = '5#12-[5]-200DG'
    #T3 = '5#12-[5]'
    #pT3 = re.compile('\A\s*(\d*)#(\d+)-\[(\d+)\](-*)(\d*)(\D*)\s*\Z')
    #print pT3.findall(T3)
    #print pT3.search(T3)
    
    #text = '5#12-[5]-200DG'
    #print has_correct_format(text)
    #print data_get(text)