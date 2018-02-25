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

from strupy.pill import SectionBase

from ConcreteModel import ConcreteModel
from Drawing import Drawing
from Scaner import Scaner
import color_system
import text_syntax_bar
import text_syntax_profile
import text_syntax_screw
import text_syntax_element

class Checker():
    def __init__(self):
        self.ConcreteModel = None
        self.SteelModel = None
        self.Drawing = None
        self.pen = None
        self.layer = 'DS_TMPCHECK'
        
    #----------------------------------------------
    
    def asign_ConcreteModel(self, ConcreteModel):
        self.ConcreteModel = ConcreteModel

    def asign_SteelModel(self, SteelModel):
        self.SteelModel = SteelModel

    def asign_Drawing(self, Drawing):
        self.Drawing = Drawing
        self.pen = self.Drawing.pen
        
    #----------------------------------------------
    
    def check_concrete(self, dosave = False):
        print '********* Checking dxf for concrete model ***************'
        self.delete_all_marks()
        #---
        isCorrect = []
        isCorrect.append(self.bar_with_no_ctext())
        isCorrect.append(self.ctext_with_no_bar())
        isCorrect.append(self.ctext_with_wrong_format())
        isCorrect.append(self.ctext_not_linked())
        #---
        isCorrect.append(self.elemet_text_with_wrong_format())
        isCorrect.append(self.elemet_text_with_no_frame())
        if dosave:
            self.pen.save()
        #---
        check_result = all(isCorrect)
        if check_result:
            print '>>>any problem detected<<<'

        else:
            print '>>>!!some problem detected!!<<<'
        print '*******************************************'
        return check_result

    def check_steel(self, dosave = False):
        print '********* Checking dxf for steel model ***************'
        self.delete_all_marks()
        #---
        isCorrect = []
        isCorrect.append(self.stext_with_wrong_format())
        isCorrect.append(self.stext_with_not_recognized_section())
        isCorrect.append(self.stext_not_linked())
        #---
        isCorrect.append(self.elemet_text_with_wrong_format())
        isCorrect.append(self.elemet_text_with_no_frame())
        if dosave:
            self.pen.save()
        #---
        check_result = all(isCorrect)
        if check_result:
            print '>>>any problem detected<<<'

        else:
            print '>>>!!some problem detected!!<<<'
        print '*******************************************'
        return check_result
            
    #-----------------concrete checks-----------------------------
    
    def bar_with_no_ctext(self):
        isCorrect = True
        print '---bar_with_no_ctext---'
        for bar in self.ConcreteModel.barlist:
            if not bar.maintext:
                if bar.dxf_pline_entity.dxf.color not in color_system.dead_bar:
                    p = bar.pline.get_coord_list()[0]
                    self.pen.set_current_layer(self.layer)
                    self.pen.addText('no ctext for bar!!!', p, height=200, color = 'red')
                    self.pen.addLine([0.0, 0.0], p, color = 'red')
                    print '  found at %s' %p
                    isCorrect = False
        print '   ...done'
        return isCorrect

    def ctext_with_no_bar(self):
        isCorrect = True
        print '---ctext_with_no_bar---'
        texts_in_bars = [bar.maintext for bar in self.ConcreteModel.barlist]
        for text in self.Drawing.DS_CTEXTS:
            if not text in texts_in_bars:
                if text.dxf.color not in (color_system.annot_countable + color_system.annot_uncountable):
                    p = list(text.dxf.insert[:2])
                    self.pen.set_current_layer(self.layer)
                    self.pen.addText('no bar for ctext!!!', p, height=200, color = 'red')
                    self.pen.addLine([0.0, 0.0], p, color = 'red')
                    print '  found at %s' %p
                    isCorrect = False
        print '   ...done'
        return isCorrect
        
    def ctext_with_wrong_format(self):
        isCorrect = True
        print '---ctext with wrong format---'
        for text in self.Drawing.DS_CTEXTS:
            if not text_syntax_bar.has_correct_format(text.dxf.text):
                p = list(text.dxf.insert[:2])
                self.pen.set_current_layer(self.layer)
                self.pen.addText('ctext with wrong format!!!', p, height=200, color = 'red')
                self.pen.addLine([0.0, 0.0], p, color = 'red')
                print '  found at %s' %p
                isCorrect = False
        print '   ...done'
        return isCorrect

    def ctext_not_linked(self):
        isCorrect = True
        print '---ctext_not_linked---'
        #--main texts
        texts_in_bars = [bar.maintext for bar in self.ConcreteModel.barlist]
        #-- deptexts
        for bar in self.ConcreteModel.barlist:
            texts_in_bars += bar.deptexts
        for text in self.Drawing.DS_CTEXTS:
            if not text in texts_in_bars:
                p = list(text.dxf.insert[:2])
                self.pen.set_current_layer(self.layer)
                self.pen.addText('ctext not linked to any bar!!!', p, height=200, color = 'red')
                self.pen.addLine([0.0, 0.0], p, color = 'red')
                #---seting mark as 0
                text_string = text.dxf.text
                text_string = text_syntax_bar.data_change(text_string, newMark='0')
                text.dxf.text = text_string
                
                print '  found at %s' %p
                isCorrect = False
        print '   ...done'
        return isCorrect

    #-----------------steel checks-----------------------------

    def stext_with_wrong_format(self):
        isCorrect = True
        print '---stext with wrong format---'
        for text in self.Drawing.DS_STEXTS:
            if not (text_syntax_profile.has_correct_format(text.dxf.text) or text_syntax_screw.has_correct_format(text.dxf.text)) :
                p = list(text.dxf.insert[:2])
                self.pen.set_current_layer(self.layer)
                self.pen.addText('stext with wrong format!!!', p, height=200, color = 'red')
                self.pen.addLine([0.0, 0.0], p, color = 'red')
                print '  found %s at %s' %(text.dxf.text, p)
                isCorrect = False
        print '   ...done'

        return isCorrect

    def stext_with_not_recognized_section(self):
        isCorrect = True
        print '---stext with not recognized section---'
        sections_in_base = SectionBase.get_database_sectionlist()
        for text in self.Drawing.DS_STEXTS:
            if text_syntax_profile.has_correct_format(text.dxf.text) and text_syntax_profile.is_maintext(text.dxf.text):
                sect = text_syntax_profile.data_get(text.dxf.text)['Sect']
                if not sect in sections_in_base:
                    p = list(text.dxf.insert[:2])
                    self.pen.set_current_layer(self.layer)
                    self.pen.addText('stext with not recognized section!!!', p, height=200, color = 'blue')
                    self.pen.addLine([0.0, 0.0], p, color = 'blue')
                    print '  found %s at %s' %(sect,p)
                    isCorrect = False
        print '   ...done'
        return isCorrect

    def stext_not_linked(self):
        isCorrect = True
        print '---stext_not_linked---'
        #--main texts
        linked_texts = []
        linked_texts += [profile.maintext for profile in self.SteelModel.profilelist] # in profiles
        linked_texts += [screw.maintext for screw in self.SteelModel.screwlist] # in screws
        #-- deptexts
        for profile in self.SteelModel.profilelist: # in profiles
            linked_texts += profile.deptexts
        for screw in self.SteelModel.screwlist: # in screws
            linked_texts += screw.deptexts
        for text in self.Drawing.DS_STEXTS:
            if not text in linked_texts:
                p = list(text.dxf.insert[:2])
                self.pen.set_current_layer(self.layer)
                self.pen.addText('stext not linked to any profile!!!', p, height=200, color = 'green')
                self.pen.addLine([0.0, 0.0], p, color = 'green')
                #---seting mark as 0 i profile
                if text_syntax_profile.has_correct_format(text.dxf.text):
                    text_string = text.dxf.text
                    text_string = text_syntax_profile.data_change(text_string, newMark='0')
                    text.dxf.text = text_string
                print '  found at %s' %p
                isCorrect = False
        print '   ...done'
        return isCorrect
        

    #-----------------element checks-----------------------------

    def elemet_text_with_wrong_format(self):
        isCorrect = True
        print '---elemet_text_with_wrong_format---'
        for text in self.Drawing.DS_ELEMENT_TEXT:
            if not text_syntax_element.has_correct_format(text.dxf.text):
                p = list(text.dxf.insert[:2])
                self.pen.set_current_layer(self.layer)
                self.pen.addText('elemet_text_with_wrong_format!!!', p, height=200, color = 'red')
                self.pen.addLine([0.0, 0.0], p, color = 'red')
                print '  found at %s' %p
                isCorrect = False
        print '   ...done'
        return isCorrect

    def elemet_text_with_no_frame(self):
        isCorrect = True
        print '---elemet_text_with_no_frame---'
        texts_in_elements = [elemet.dxf_text_entity for elemet in self.ConcreteModel.elementlist]
        for text in self.Drawing.DS_ELEMENT_TEXT:
            if not text in texts_in_elements:
                p = list(text.dxf.insert[:2])
                self.pen.set_current_layer(self.layer)
                self.pen.addText('elemet_text_with_no_frame!!!', p, height=200, color = 'red')
                self.pen.addLine([0.0, 0.0], p, color = 'red')
                print '  found at %s' %p
                isCorrect = False
        print '   ...done'
        return isCorrect

    #----------------------------------------------
    
    def show_concrete_depenance(self):
        print '---show_concrete_depenance---'
        #---
        self.delete_all_marks()
        #---
        self.pen.set_current_layer(self.layer)
        self.pen.set_origin()
        #---
        for bar in self.ConcreteModel.barlist:
            if bar.maintext:
                maintext_point = list(bar.maintext.dxf.insert[:2])
                for text in bar.deptexts:
                    text_point = list(text.dxf.insert[:2])
                    self.pen.addLine(maintext_point, text_point, color = 'blue')
        #---
        print '   ...done'

    def show_steel_depenance(self):
        print '---show_steel_depenance---'
        #---
        self.delete_all_marks()
        #---
        self.pen.set_current_layer(self.layer)
        self.pen.set_origin()
        #---profils
        for profile in self.SteelModel.profilelist:
            if profile.maintext:
                maintext_point = list(profile.maintext.dxf.insert[:2])
                for text in profile.deptexts:
                    text_point = list(text.dxf.insert[:2])
                    self.pen.addLine(maintext_point, text_point, color =  33)
        for screw in self.SteelModel.screwlist:
            if screw.maintext:
                maintext_point = list(screw.maintext.dxf.insert[:2])
                for text in screw.deptexts:
                    text_point = list(text.dxf.insert[:2])
                    self.pen.addLine(maintext_point, text_point, color = 222)
        #---
        print '   ...done'
                
    #----------------------------------------------
    
    def delete_all_marks(self):
        print '---deleting all warnings marks---'
        to_delete_list = []
        for entity in self.pen.msp:
            if entity.dxf.layer == 'DS_TMPCHECK':
                to_delete_list.append(entity) 
        self.pen.delete_entity(to_delete_list)
        print '   ...done'

# Test if main
if __name__ == "__main__":
    from environment import*
    DRAWING.open_file()
    SCANER.load_data_to_model()
    #print CHECKER.check_concrete()
    print CHECKER.check_steel()
    #CHECKER.show_steel_depenance()
    CHECKER.pen.save()