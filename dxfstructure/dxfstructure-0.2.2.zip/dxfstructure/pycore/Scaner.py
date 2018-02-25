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

import uuid
import ezdxf
import os

from Bar import Bar
from Profile import Profile
from Screw import Screw
from Element import Element
from Drawing import Drawing
from ConcreteModel import ConcreteModel

from geo import Point, Line, Polyline, Rectangle,  pline_from_dxfpline
import text_syntax_element
import text_syntax_profile
import text_syntax_screw
import color_system

class Scaner():
    def __init__(self):
        self.ConcreteModel = None
        self.SteelModel = None
        self.Drawing = None
        self.Executor = None
        self.pen = None
     
    #---------------------------------------------- 
        
    def asign_ConcreteModel(self, ConcreteModel):
        self.ConcreteModel = ConcreteModel

    def asign_SteelModel(self, SteelModel):
        self.SteelModel = SteelModel

    def asign_Drawing(self, Drawing):
        self.Drawing = Drawing
        self.pen = self.Drawing.pen

    def asign_Executor(self, Executor):
        self.Executor = Executor

    #----------------------------------------------
    
    def load_data_to_model(self):
        print '********* Loading data to model ***************'
        self.search_bars()
        self.search_maintext_for_bars()
        self.search_rangeplines_for_bars()
        self.search_maintext_for_bars_with_ref()
        #---
        self.search_profiles()
        self.search_screws()
        #---
        self.search_elements()
        self.search_elements_text()
        #---
        self.assign_bar_to_element()
        self.assign_profile_to_element()
        self.assign_screw_to_element()
        #---
        self.clr_deps_if_request()
        self.assign_id_if_deplines_for_concrete_model()
        self.assign_id_if_deplines_for_steel_model()
        self.delete_deplines()
        #---
        self.search_deptext_for_bars()
        self.search_deptext_for_profiles()
        self.search_deptext_for_screws()
        self.refresh_id()
        #--
        self.push_command_to_executor()
        print '***********************************************'

    #----------------------------------------------
    
    def search_bars(self):
        print '---searching bars---'
        for i in self.Drawing.DS_BARS:
            if i.dxf.color not in color_system.dead_bar:
                self.ConcreteModel.add_bar(Bar(i))
        print '   %s bars found' %self.ConcreteModel.get_bar_number()
        print '   ....done'
    
    def search_maintext_for_bars(self):
        print '---searching maintext---'
        for bar in self.ConcreteModel.barlist:
            #--getting closest text from bar
            tdists = []
            for txt in self.Drawing.DS_CTEXTS:
                dxfinsert = txt.dxf.insert
                textp = Point([dxfinsert[0], dxfinsert[1]])
                txtdist = bar.pline.distance(textp)
                if txt.dxf.color in color_system.annot_countable + color_system.annot_uncountable:
                    txtdist = float('inf')
                tdists.append(txtdist)
            mintdist = min(tdists)
            mintdistindex = tdists.index(mintdist)
            t_entity = self.Drawing.DS_CTEXTS[mintdistindex] #dxf text entity we looking for
            maxdist = 1.0 * t_entity.dxf.height
            #---if found text is closest than it height from bar then assign it to bar
            if mintdist < maxdist:
                if t_entity.dxf.color not in color_system.annot_countable + color_system.annot_uncountable:
                    bar.maintext = t_entity
        print '   ....done'
        
    def search_maintext_for_bars_with_ref(self):
        print '---searching maintext for bars with ref---'
        for ref in self.Drawing.DS_CTEXTREFS:
            #--geting closest text from refs
            ref_pline = pline_from_dxfpline(ref)
            tdists = []
            for txt in self.Drawing.DS_CTEXTS:
                dxfinsert = txt.dxf.insert
                textp = Point([dxfinsert[0], dxfinsert[1]])
                txtdist = ref_pline.distance(textp)
                tdists.append(txtdist)
            mintdist = min(tdists)
            mintdistindex = tdists.index(mintdist)
            t_entity = self.Drawing.DS_CTEXTS[mintdistindex] #dxf text entity we looking for
            maxdist = 0.8 * t_entity.dxf.height
            #---if found text is closest than it height from ref pline then assign it to bar
            if mintdist > maxdist:
                t_entity = None
            if t_entity:
                ref_pline_coords = ref_pline.get_coord_list()
                startpoint = Point(ref_pline_coords[0])
                endpoint = Point(ref_pline_coords[-1])
                for bar in self.ConcreteModel.barlist:
                    start_dist = bar.pline.distance(startpoint)
                    end_dist = bar.pline.distance(endpoint)
                    maxdist = 0.01*t_entity.dxf.height
                    if min(start_dist, end_dist) < maxdist:
                        bar.maintext = t_entity
        print '   ....done'
        
    def search_rangeplines_for_bars(self):
        print '---searching rangeplines---'
        for bar in self.ConcreteModel.barlist:
            for dxfpline in self.Drawing.DS_RANGEPLINES:
                pline = pline_from_dxfpline(dxfpline)
                bar_pline_intersection = pline.intersection(bar.pline)
                if bar_pline_intersection:
                    for circle in self.Drawing.DS_RANGECIRCELS:
                        circlecenter = Point(circle.dxf.center)
                        if bar_pline_intersection[0].intersection(circlecenter):
                            bar.rangepline = pline_from_dxfpline(dxfpline)
        print '   ....done'
    
    #------------------------------------------
    def search_profiles(self):
        print '---searching profiles---'
        for txt in self.Drawing.DS_STEXTS:
            txt_string = txt.dxf.text
            if text_syntax_profile.is_maintext(txt_string):
                #print txt_string
                self.SteelModel.add_profile(Profile(txt))
        print '   %s profiles found' %self.SteelModel.get_profile_number()
        print '   ....done'    

    def search_screws(self):
        print '---searching screws---'
        for txt in self.Drawing.DS_STEXTS:
            txt_string = txt.dxf.text
            if text_syntax_screw.has_correct_format(txt_string):
                if txt.dxf.color not in color_system.annot_uncountable:
                    self.SteelModel.add_screw(Screw(txt))
        print '   %s screws found' %self.SteelModel.get_screw_number()
        print '   ....done'   
    
    #------------------------------------------
    
    def search_elements(self):
        print '---searching elements---'
        for i in self.Drawing.DS_ELEMENT_FRAME:
            ielement = Element(i)
            self.ConcreteModel.add_element(ielement)
            self.SteelModel.add_element(ielement)
        print '   %s element found' %self.ConcreteModel.get_element_number()
        print '   ....done'

    def search_elements_text(self):
        print '---searching elements_name---'
        for element in self.ConcreteModel.elementlist:
            for txt in self.Drawing.DS_ELEMENT_TEXT:
                if element.rectangle.has_inside(Point(txt.dxf.insert)):
                    if text_syntax_element.has_correct_format(txt.dxf.text):
                        element.dxf_text_entity = txt
        print '   ....done'

    def assign_bar_to_element(self):
        print '---assign_bar_to_element---'
        for bar in self.ConcreteModel.barlist:
            for element in self.ConcreteModel.elementlist:
                if element.rectangle:
                    if element.rectangle.has_inside(bar.pline):
                        element.add_bar(bar)
                        bar.element = element
        #--creating freebar element
        if None in [bar.element for bar in  self.ConcreteModel.barlist]:
            freebar_element = Element()
            freebar_element.clear_data()
            freebar_element_name = 'FreeBars'
            freebar_element.name = freebar_element_name
            freebar_element.quantity = 1.0
            print '   (additional FreeBars element created)'
            self.SteelModel.add_element(freebar_element)
            self.ConcreteModel.add_element(freebar_element)
            for bar in self.ConcreteModel.barlist:
                if not bar.element:
                    freebar_element.add_bar(bar)
                    bar.element = freebar_element            
        print '   ....done'


    def assign_profile_to_element(self):
        print '---assign_profiles_to_element---'
        for profile in self.SteelModel.profilelist:
            for element in self.SteelModel.elementlist:
                if element.rectangle:
                    if element.rectangle.has_inside(profile.location_point):
                        element.add_profile(profile)
                        profile.element = element
        #--creating freeprofile element
        if None in [profile.element for profile in  self.SteelModel.profilelist]:
            freeprofile_element = Element()
            freeprofile_element.clear_data()
            freeprofile_element_name = 'FreeProfiles'
            freeprofile_element.name = freeprofile_element_name
            freeprofile_element.quantity = 1.0
            print '   (additional FreeProfiles element created)'
            self.SteelModel.add_element(freeprofile_element)
            self.ConcreteModel.add_element(freeprofile_element)
            for profile in self.SteelModel.profilelist:
                if not profile.element:
                    freeprofile_element.add_profile(profile)
                    profile.element = freeprofile_element            
        print '   ....done'

    def assign_screw_to_element(self):
        print '---assign_screwss_to_element---'
        for screw in self.SteelModel.screwlist:
            for element in self.SteelModel.elementlist:
                if element.rectangle:
                    if element.rectangle.has_inside(screw.location_point):
                        element.add_screw(screw)
                        screw.element = element
        #--creating freescrew element
        if None in [screw.element for screw in  self.SteelModel.screwlist]:
            freescrew_element = Element()
            freescrew_element.clear_data()
            freescrew_element_name = 'FreeScrews'
            freescrew_element.name = freescrew_element_name
            freescrew_element.quantity = 1.0
            print '   (additional FreeScrews element created)'
            self.SteelModel.add_element(freescrew_element)
            self.ConcreteModel.add_element(freescrew_element)
            for screw in self.SteelModel.screwlist:
                if not screw.element:
                    freescrew_element.add_screw(screw)
                    screw.element = freescrew_element            
        print '   ....done'

    #------------------------------------------

    def clr_deps_if_request(self):
        print '---clr_deps_if_request---'
        #-----------CTEXTS
        for text in self.Drawing.DS_CTEXTS:
            if 'clr' in text.dxf.text:
                text.dxf.text = text.dxf.text.replace('clr', '')
                self.Drawing.entity_id_set_random(text)
        #-----------
        for text in self.Drawing.DS_STEXTS:
            if 'clr' in text.dxf.text:
                text.dxf.text = text.dxf.text.replace('clr', '')
                self.Drawing.entity_id_set_random(text)
        print '   ....done'
        
    def assign_id_if_deplines_for_concrete_model(self):
        print '---assign_id_if_deplines for concrete model---'
        for bar in self.ConcreteModel.barlist:
            if bar.maintext:
                maintext_id = self.Drawing.entity_id_get(bar.maintext)
                bar_maintext_point = list(bar.maintext.dxf.insert[:2])
                bar_maintext_point = Point(bar_maintext_point)
                for line in self.Drawing.DS_DEPLINES:
                    line_start_point = list(line.dxf.start[:2])
                    line_start_point = Point(line_start_point)
                    line_end_point = list(line.dxf.end[:2])
                    line_end_point = Point(line_end_point)
                    inter_start = bar_maintext_point.intersection(line_start_point)
                    inter_end = bar_maintext_point.intersection(line_end_point)
                    pick_point = None
                    if inter_start : pick_point = line_end_point
                    if inter_end : pick_point = line_start_point
                    if pick_point :
                        for text in self.Drawing.DS_CTEXTS:
                            ptext = list(text.dxf.insert[:2])
                            ptext = Point(ptext)
                            if pick_point.intersection(ptext):
                                self.Drawing.entity_id_set(text, maintext_id)
        print '   ....done'

    def assign_id_if_deplines_for_steel_model(self):
        print '---assign_id_if_deplines for steel model---'
        #for profile in self.SteelModel.profilelist:
        for profile in self.SteelModel.profilelist + self.SteelModel.screwlist:
            if profile.maintext:
                maintext_id = self.Drawing.entity_id_get(profile.maintext)
                profile_maintext_point = list(profile.maintext.dxf.insert[:2])
                profile_maintext_point = Point(profile_maintext_point)
                for line in self.Drawing.DS_DEPLINES:
                    line_start_point = list(line.dxf.start[:2])
                    line_start_point = Point(line_start_point)
                    line_end_point = list(line.dxf.end[:2])
                    line_end_point = Point(line_end_point)
                    inter_start = profile_maintext_point.intersection(line_start_point)
                    inter_end = profile_maintext_point.intersection(line_end_point)
                    pick_point = None
                    if inter_start : pick_point = line_end_point
                    if inter_end : pick_point = line_start_point
                    if pick_point :
                        for text in self.Drawing.DS_STEXTS:
                            if not text_syntax_profile.is_maintext(text.dxf.text):
                                ptext = list(text.dxf.insert[:2])
                                ptext = Point(ptext)
                                if pick_point.intersection(ptext):
                                    self.Drawing.entity_id_set(text, maintext_id)
        print '   ....done'

    def delete_deplines(self):
        print '---delete_deplines---'
        to_delete_list = []
        for entity in self.pen.msp:
            if entity.dxf.layer == 'DS_DEPLINE':
                to_delete_list.append(entity) 
        self.pen.delete_entity(to_delete_list)
        print '   ....done'

    def search_deptext_for_bars(self):
        print '---search_deptext_for_bars---'
        maintexts = []
        for bar in self.ConcreteModel.barlist:
            if bar.maintext:
                maintexts.append(bar.maintext)
        for bar in self.ConcreteModel.barlist:
            if bar.maintext:
                bar_maintext_id = self.Drawing.entity_id_get(bar.maintext)
                for text in self.Drawing.DS_CTEXTS:
                    if self.Drawing.entity_id_get(text) == bar_maintext_id:
                        if not text in maintexts:
                            bar.deptexts.append(text)
        print '   ....done'

    def search_deptext_for_profiles(self):
        print '---search_deptext_for_profiles---'
        maintexts = []
        for profile in self.SteelModel.profilelist:
            if profile.maintext:
                maintexts.append(profile.maintext)
        for profile in self.SteelModel.profilelist:
            if profile.maintext:
                profile_maintext_id = self.Drawing.entity_id_get(profile.maintext)
                for text in self.Drawing.DS_STEXTS:
                    if self.Drawing.entity_id_get(text) == profile_maintext_id:
                        if not text in maintexts:
                            if text_syntax_profile.has_correct_format(text.dxf.text) :
                                profile.add_deptext(text)
                                if text.dxf.color not in color_system.annot_uncountable:
                                    text.dxf.color = color_system.annot_countable[0]
        print '   ....done'

    def search_deptext_for_screws(self):
        print '---search_deptext_for_screws---'
        maintexts = []
        for screw in self.SteelModel.screwlist:
            if screw.maintext:
                maintexts.append(screw.maintext)
        for screw in self.SteelModel.screwlist:
            if screw.maintext:
                screw_maintext_id = self.Drawing.entity_id_get(screw.maintext)
                for text in self.Drawing.DS_STEXTS:
                    if self.Drawing.entity_id_get(text) == screw_maintext_id:
                        if not text in maintexts:
                            if text_syntax_screw.has_correct_format(text.dxf.text):
                                screw.deptexts.append(text)
                                if not text.dxf.color in color_system.annot_uncountable:
                                    text.dxf.color = color_system.annot_countable[0]
        print '   ....done'

    def refresh_id(self):
        print '---refresch_id---'
        #---concrete model
        for bar in self.ConcreteModel.barlist:
            if bar.maintext:
                new_id = self.Drawing.entity_id_set_random(bar.maintext)
                for text in bar.deptexts:
                    self.Drawing.entity_id_set(text, new_id)
        #---steel model profiles
        for profile in self.SteelModel.profilelist:
            if profile.maintext:
                new_id = self.Drawing.entity_id_set_random(profile.maintext)
                for text in profile.deptexts:
                    self.Drawing.entity_id_set(text, new_id)
        #---steel model screws
        for screw in self.SteelModel.screwlist:
            if screw.maintext:
                new_id = self.Drawing.entity_id_set_random(screw.maintext)
                for text in screw.deptexts:
                    self.Drawing.entity_id_set(text, new_id)
        print '   ....done'
    
    #----------------------------------------------
    
    def push_command_to_executor(self):
        print '---pushing command to executor---'
        for command in self.Drawing.DS_COMMAND:
            command_text = command.dxf.text
            command_point = [command.dxf.insert[0], command.dxf.insert[1]]
            if command.dxf.color not in color_system.dead_command:
                self.Executor.commandlist.append([command_text, command_point, command])
        print '   ....done'

# Test if main
if __name__ == "__main__":
    
    from environment import*
    #---
    DRAWING.open_file()
    #---
    SCANER.load_data_to_model()
    #---
    #SCANER.pen.save()
    
    print CONCRETE_MODEL.elementlist[0]
    
    print '_________________________'
    
    for element in CONCRETE_MODEL.elementlist:
        print element.maintext_string
        print element.name

    #for bar in CONCRETE_MODEL.barlist:
    #    print bar.element