'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2017-08-10
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

import os
import random

from geo import Point
import text_syntax_screw
import schedule_format_screw
import color_system

class Screw():
    def __init__(self, maintext=None):
        self.element = None
        self.maintext = maintext
        self.deptexts = []
        self.delete_mark = False

    #----------------------------------------------
    
    def refresh(self):
        self.data_set()
        
    #----------------------------------------------

    def data_set(self):
        #---
        text_entity_to_change = self.deptexts
        #---
        for dxftxt in text_entity_to_change:
            dxftxt.dxf.text = self.maintext_string
            #dxftxt.dxf.color = color_system.annot_uncountable #!!!!!!!!!!!!!!
    
    #----------------------------------------------
    
    @property
    def maintext_string(self):
        return self.maintext.dxf.text
        
    @property
    def maintext_data(self):
        return text_syntax_screw.data_get(self.maintext_string)

    @property
    def deptexts_list(self):
        return [deptexts.dxf.text for deptexts in self.deptexts]

    @property
    def Screwtype(self):
        Screwtype = self.maintext_data['Screwtype']
        return Screwtype
        
    @property
    def Grade(self):
        return self.maintext_data['Grade']

    @property
    def Number(self):
        return self.maintext_data['Number']

    @property
    def Length(self):
        return self.maintext_data['Length']

    #----------------------------------------------
    
    @property
    def location_point(self):
        coord = self.maintext.dxf.insert
        return Point([coord[0], coord[1]])
        
    #----------------------------------------------
        
    def __str__(self):
        if self.maintext:
            return 'screw ' + self.maintext_string + str(self.deptexts)
    
    #----------------------------------------------
    
    @property
    def schedule_record(self):
        return schedule_format_screw.record(self)
        
    #----------------------------------------------
    
 
# Test if main
if __name__ == "__main__":
    
    from environment import*
    #---
    DRAWING.open_file()
    #---
    SCANER.load_data_to_model()
    #---
    CONCRETE_MODEL.selftest()
    CONCRETE_MODEL.procces_data()
       
    print '=================================='

    screw = STEEL_MODEL.screwlist[2]
    
    for i in STEEL_MODEL.screwlist:
        print i