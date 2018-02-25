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

import os
import random

import ezdxf

from strupy.pill import SectionBase, u

from geo import Point, Line, Polyline, Bar_shape, pline_from_dxfpline, dim_round
import x_dxf_test_path
import text_syntax_profile
import rcbar_prop
import schedule_format_profile
import tolerance
import color_system

class Profile():
    def __init__(self, maintext=None):
        self.element = None
        self.maintext = maintext
        self.deptexts = []
        self.delete_mark = False
    
    #----------------------------------------------
    
    def add_deptext(self, text_entity):
        if text_syntax_profile.has_correct_format(text_entity.dxf.text):
            self.deptexts.append(text_entity)

    #----------------------------------------------
    
    def refresh(self):
        self.data_set()
        
    #----------------------------------------------

    def data_set(self, newMark=None, newSect=None):
        if newMark == None: newMark = self.Mark
        if newSect == None: newSect = self.Sect
        #---
        text_entity_to_change = self.deptexts + [self.maintext]
        #---
        for dxftxt in text_entity_to_change:
            new_dxftxt_string = text_syntax_profile.data_change(    dxftxt.dxf.text,
                                                                    newNumber=None, 
                                                                    newMark=newMark, 
                                                                    newSect=newSect)
            dxftxt.dxf.text = new_dxftxt_string     
    
    #----------------------------------------------
    
    @property
    def maintext_string(self):
        return self.maintext.dxf.text
        
    @property
    def maintext_data(self):
        return text_syntax_profile.data_get(self.maintext_string)

    @property
    def deptexts_list(self):
        return [deptexts.dxf.text for deptexts in self.deptexts]

    @property
    def Sect(self):
        Sect = self.maintext_data['Sect']
        return Sect
        
    @property
    def Grade(self):
        if not self.maintext_data['Grade']:
            return 'S235'
        else:
            return self.maintext_data['Grade']

    @property
    def Mark(self):
        return self.maintext_data['Mark']

    def Mark_set(self,newMark=None):
        self.data_set(newMark = newMark)

    @property
    def Number(self):
        #--from maintext
        number_from_maintext = self.maintext_data['Number']
        #--from deptexts
        countable_deptexts = []
        for text in self.deptexts:
            if text.dxf.color not in color_system.annot_uncountable:
                countable_deptexts.append(text.dxf.text)
        number_list = [text_syntax_profile.data_get(text)['Number'] for text in countable_deptexts]
        number_from_deptexts = sum(number_list)
        #--total number    
        number_total = number_from_deptexts + number_from_maintext
        return number_total
    
    @property
    def Length(self):
        return self.maintext_data['Length']

    @property
    def Total_Length(self):
        return self.Length * self.Number

    @property
    def Mass(self):
        try:
            mass_per_length = SectionBase.get_sectionparameters(self.Sect)['mass'].asUnit(u.kg / u.m).asNumber() # in [kg / m]
        except:
            mass_per_length = 0
        mass = self.Length / 1000.0 * mass_per_length
        mass = round(mass, 2)
        return mass
    
    @property
    def Total_Mass(self):
        mass = self.Mass * self.Number
        mass = round(mass, 2)
        return mass

    #----------------------------------------------
    
    @property
    def location_point(self):
        coord = self.maintext.dxf.insert
        return Point([coord[0], coord[1]])
        
    #----------------------------------------------
        
    def __str__(self):
        if self.maintext:
            return 'profile' + self.maintext_string + str(self.deptexts)
        else:
            return 'bar' + ' with no maintext '

    #----------------------------------------------
    
    @property
    def schedule_record(self):
        return schedule_format_profile.record(self)
        
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

    profile = STEEL_MODEL.profilelist[1]
    
    for i in STEEL_MODEL.profilelist:
        print '-------------'
        print i.maintext_string
        print i.Length
        print i.deptexts_list