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

from Drawing import Drawing
import layer_system


from strupy.pill import SectionBase, u
from strupy.steel.BoltClip import BoltClip
BoltClip = BoltClip()

class Creator():
    def __init__(self):
        self.Drawing = None
        self.pen = None

    def asign_Drawing(self, Drawing):
        self.Drawing = Drawing
        self.pen = self.Drawing.pen
    
    def inject_DS_system(self):
        self._create_layer_system()

    def _create_layer_system(self):
        for layername in layer_system.layer_name_list:
            #---
            color = layer_system.color_for_layer(layername)
            width = layer_system.width_for_layer(layername)
            lintype = layer_system.linetype_for_layer(layername)
            line_weight = layer_system.width_for_layer(layername)
            #----
            self.pen.layer_add(name=layername, linetype=lintype, color=color, line_weight = line_weight)
    
    #-----------
    
    def draw_steel_section(self, name='IPE 330', insertpoint=[1000.0,1000.0]):
        self.Drawing.pen.set_origin(insertpoint)
        if name in SectionBase.get_database_sectionlist():
            self.draw_steel_section_type_one(name, insertpoint)
        elif name in SectionBase.get_database_sectiontypes():
            self.draw_steel_section_type_range(name, insertpoint)
        else:
            self.pen.addText(name + ' - not recognized!!', [0.0, 0.0], height=25)
            
    def draw_steel_section_type_one(self, sectname='IPE 330', insertpoint=[1000.0,1000.0]):
        print 'draw_steel_section one'
        self.Drawing.pen.set_origin(insertpoint)
        if sectname in SectionBase.get_database_sectionlist():
            SectionBase.draw_sectiongeometry(self.pen, sectname, annotation=0)
            self.pen.addText(sectname, [0.0, 0.0], height=25)
        else:
            self.pen.addText(sectname + ' - not recognized!!', [0.0, 0.0], height=25)

    def draw_steel_section_type_range(self, type='IPE', insertpoint=[1000.0,1000.0]):
        print 'draw_steel_section range'
        self.Drawing.pen.set_origin(insertpoint)
        if type in SectionBase.get_database_sectiontypes():
            for sectname in SectionBase.get_database_sectionlistwithtype(type):
                self.draw_steel_section(sectname, insertpoint)
                width = SectionBase.get_sectionparameters(sectname)['b'].asUnit(u.mm).asNumber()
                insertpoint[0] += width + 100
        else:
            self.pen.addText(type + ' - not recognized!!', [0.0, 0.0], height=25)
    
    #-----------
    
    def draw_steel_bolt(self, Dim='M12', insertpoint=[1000.0,1000.0]):
        print 'draw_steel_bolt'
        self.Drawing.pen.set_origin(insertpoint)
        #---
        if Dim in BoltClip.get_AvailableBoltDim():
            BoltClip.set_BoltDim(Dim)
            BoltClip.draw(self.pen, annotation=False, axes=True)
            self.pen.addText(Dim, [20.0, -15.0], height=10)
        else:
            self.pen.addText(type + ' bolt dim not recognized!!', [0.0, 0.0], height=25)        
    

# Test if main
if __name__ == "__main__":
    from environment import*
    DRAWING.open_file()
    #---
    #CREATOR.draw_steel_section(sectname='HE 140 B', insertpoint=[2000.0,2000.0])
    #CREATOR.draw_steel_section(sectname='IPNass 260', insertpoint=[3000.0,3000.0])
    #CREATOR.draw_steel_section_type_range()
    #CREATOR.draw_xxx()
    #CREATOR.DoCommand('draw_xxx')
    CREATOR.Drawing.save()