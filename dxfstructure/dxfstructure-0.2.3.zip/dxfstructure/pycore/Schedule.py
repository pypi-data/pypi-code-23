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

from geo import Point
import schedule_format_bar
import schedule_format_profile
import schedule_format_screw

from tabulate import tabulate

class Schedule():
    def __init__(self):
        self.ConcreteModel = None
        self.SteelModel = None
        self.Drawing = None
        self.pen = None
        self.layer_concrete = 'DS_SCHEDULECONCRETE'
        self.layer_steel = 'DS_SCHEDULESTEEL'

    #----------------------------------------------
        
    def asign_ConcreteModel(self, ConcreteModel):
        self.ConcreteModel = ConcreteModel

    def asign_SteelModel(self, SteelModel):
        self.SteelModel = SteelModel

    def asign_Drawing(self, Drawing):
        self.Drawing = Drawing
        self.pen = self.Drawing.pen
    
    #----------------------------------------------    
    
    @property
    def main_bar_schedule_text(self):
        title = schedule_format_bar.title()
        header = schedule_format_bar.header()
        records = self.ConcreteModel.schedule_record
        summary = schedule_format_bar.summary()
        #---
        schedule = header + records
        main_schedule_text = tabulate(schedule, numalign="right")  
        main_schedule_text += '\n' + summary + ' %s [kg]'%(self.ConcreteModel.Mass)   
        main_schedule_text = title + '\n' + main_schedule_text
        return str(main_schedule_text)

    @property
    def main_profile_schedule_text(self):
        title = schedule_format_profile.title()
        header = schedule_format_profile.header()
        records = self.SteelModel.schedule_record_profiles
        summary = schedule_format_profile.summary()
        #---
        schedule = header + records
        main_schedule_text = tabulate(schedule, numalign="right")  
        main_schedule_text += '\n' + summary + ' %s [kg]'%(self.SteelModel.Mass)  
        main_schedule_text = title + '\n' + main_schedule_text 
        return str(main_schedule_text)

    @property
    def main_screw_schedule_text(self):
        title = schedule_format_screw.title()
        header = schedule_format_screw.header()
        records = self.SteelModel.schedule_record_screws
        #---
        schedule = header + records
        main_schedule_text = tabulate(schedule, numalign="right")
        main_schedule_text = title + '\n' + main_schedule_text
        return str(main_schedule_text)

    #----------------------------------------------
        
    def draw_concrete_schedule_in_drawing (self):
        print '****** drawing concrete bar schedule in drawing ************'
        self.pen.set_origin()
        self.delete_existing_schedule_from_drawing(self.layer_concrete)
        #---
        self.pen.set_current_layer(self.layer_concrete)
        #---main schedule
        inserpoint = [0.0, 0.0]
        main_schedule_text = self.main_bar_schedule_text
        main_schedule_text = '{\Fcdm;%s}'%main_schedule_text #defining font
        self.pen.addMtext(main_schedule_text, inserpoint, height = 150, color = 'yellow')
        #---shape schedule
        inserpoint = [25000.0, 0.0]
        self.pen.set_origin(inserpoint)
        for bar in self.ConcreteModel.unicat_bars_sorted_numered:
            if bar.maintext:
                if not bar.is_straight():
                    bar.draw(self.pen)
                    self.pen.move_origin(0, -(bar.shape.sizexy[1] + 1100))
        p1 = [-200.0, 200.0]
        p2 = [2800.0, self.pen.origin[1]]
        self.pen.set_origin(inserpoint)
        print '   ...done'
        print '***************************************************'    

    def draw_steel_schedule_in_drawing (self):
        print '****** drawing steel profile schedule in drawing ************'
        self.pen.set_origin()
        self.delete_existing_schedule_from_drawing(self.layer_steel)
        #---
        self.pen.set_current_layer(self.layer_steel)
        #---main schedule profiles
        inserpoint = [-22000.0, 0.0]
        main_schedule_text = self.main_profile_schedule_text
        main_schedule_text = '{\Fcdm;%s}'%main_schedule_text #defining font
        self.pen.addMtext(main_schedule_text, inserpoint, height = 150, color = 'yellow')
        #---main schedule screws
        inserpoint = [-40000.0, 0.0]
        main_schedule_text = self.main_screw_schedule_text
        main_schedule_text = '{\Fcdm;%s}'%main_schedule_text #defining font
        self.pen.addMtext(main_schedule_text, inserpoint, height = 150, color = 'yellow')
        print '   ...done'
        print '***************************************************'  
    
    def delete_existing_schedule_from_drawing(self, layer):
        to_delete_list = []
        for entity in self.pen.msp:
            if entity.dxf.layer == layer:
                to_delete_list.append(entity) 
        self.pen.delete_entity(to_delete_list)

# Test if main
if __name__ == "__main__":
    #---
    from environment import*
    DRAWING.open_file()
    SCANER.load_data_to_model()
    
    CONCRETE_MODEL.selftest()
    STEEL_MODEL.selftest()
    
    print SCHEDULE.main_bar_schedule_text
    print SCHEDULE.main_profile_schedule_text
    print SCHEDULE.main_screw_schedule_text
    
    SCHEDULE.draw_concrete_schedule_in_drawing()
    SCHEDULE.draw_steel_schedule_in_drawing()
    
    SCHEDULE.pen.save()