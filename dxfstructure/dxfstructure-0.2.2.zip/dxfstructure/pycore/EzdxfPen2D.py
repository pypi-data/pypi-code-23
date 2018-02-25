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

import ezdxf

import strupy.units as u
from strupy.x_graphic.BaseCreator2D import BaseCreator2D
    
class EzdxfPen2D(BaseCreator2D):
    def __init__(self):
        BaseCreator2D.__init__(self)
        self.unit = 1.0 * u.mm
        self.scene = None
        self.msp = None
        self.currentlayer = None
    
    def assign_Ezdxf(self, Ezdxf = None):
        if Ezdxf == None:
            testdxfpath = os.path.dirname(os.path.abspath(__file__))
            testdxfpath = os.path.join(testdxfpath, 'EzdxfPen2Dtest.dxf')
            dwg = ezdxf.new('R2000')
            dwg.saveas(testdxfpath)
            Ezdxf = ezdxf.readfile(testdxfpath)
        self.scene = Ezdxf
        self.msp = self.scene.modelspace()
    
    def dxfcolorcode(self, color):
        colordict = {'black': 250, 'red' : 1, 'blue' : 5, 'green' : 3, 'yellow' : 2, 'white' : 7}
        if type(color) is str:
            return colordict[color]
        if type(color) is int:
            return color
    
    def open_file(self, path=None):
        if path == None:
            dxfpath = x_dxf_test_path.test_path
        else:
            dxfpath = path
        self.filepath = dxfpath
        self.dwg = ezdxf.readfile(dxfpath)
        #---
        self.load_data()

    def save(self):
        self.scene.save()
        print 'Saved to %s' %self.scene.filename

    def dimtopixels(self, dim):
        if type(dim) is list:
            if type(dim[0]) == type(self.origin[0]) :
                dim = [dim[0] + self.origin[0], dim[1] + self.origin[1]]
            elif type(self.origin[0]) == type(u.mm):
                dim = [ dim[0] + self.origin[0].asUnit(self.unit).asNumber(), 
                        dim[1] + self.origin[1].asUnit(self.unit).asNumber()    ]
            elif type(dim[0]) == type(u.mm):
                dim = [ dim[0].asUnit(self.unit).asNumber() + self.origin[0], 
                        dim[1].asUnit(self.unit).asNumber() + self.origin[1]    ]                
            pixels = []
            for i in dim :
                pixels.append((i / self.unit).asNumber())
        else:
            pixels = (dim / self.unit).asNumber()
        return pixels
    
    #----------base draw method replacement--------------
    
    def addLine(self, p1, p2, color='white'):
        p1 = self.dimtopixels(p1)
        p2 = self.dimtopixels(p2)
        addedline = self.msp.add_line(p1, p2)
        addedline.dxf.color = self.dxfcolorcode(color)
        if self.currentlayer:
            addedline.dxf.layer = self.currentlayer
        
    def addText(self, text, p, color='white', height=20):
        p = self.dimtopixels(p)    
        addedtext = self.msp.add_text(text)
        addedtext.set_pos(p, align='LEFT')
        addedtext.dxf.height = height
        addedtext.dxf.color = self.dxfcolorcode(color)
        if self.currentlayer:
            addedtext.dxf.layer = self.currentlayer
        
        
    def addCircle(self, p, r, color='white'):
        p = self.dimtopixels(p) 
        r = self.dimtopixels(r)
        addedcircle = self.msp.add_circle(p, r)
        addedcircle.dxf.color = self.dxfcolorcode(color)
        if self.currentlayer:
            addedcircle.dxf.layer = self.currentlayer
        
    def addMtext(self, text, p, color='white', height=20):
        p = self.dimtopixels(p)  
        addedmtext = self.msp.add_mtext(text.replace('\n', '\\P'))
        addedmtext.set_location(p)
        addedmtext.dxf.char_height = height
        addedmtext.dxf.color = self.dxfcolorcode(color)
        if self.currentlayer:
            addedmtext.dxf.layer = self.currentlayer
            
    #--------method specialisation to make white color as default----------------
    
    def addPolyline(self, plist, color='white'):
        BaseCreator2D.addPolyline(self, plist, color)

    def addRegpoly(self, p, r, side_num, color = 'white'):
        BaseCreator2D.addRegpoly(self, p, r, side_num, color)
    
    #---------------------------------------------
    
    def delete_entity(self, entity):
        if type(entity) is list:
            for i in entity:
                self.msp.delete_entity(i)
        else:
            self.msp.delete_entity(entity)
    
    #---------------------------------------------
    
    def layer_add(self, name='none', linetype='CONTINOUS', color='blue', line_weight=530):
        if not self.scene.layers.has_entry(name):
            color = self.dxfcolorcode(color)
            self.scene.layers.new(name = name, dxfattribs={'linetype': linetype, 'color': color,  'line_weight': line_weight})
            print '%s layer created' %name
        else:
            print '%s layer already exist!!' %name
    
    def set_current_layer(self, layer):
        self.currentlayer = layer
        
        
# Test if main
if __name__ == "__main__":
    pen = EzdxfPen2D()
    pen.assign_Ezdxf()
    
    p1 = [550.0*u.mm, -100.0*u.mm]
    p2 = [400.0, -200.0]
    pen.addLine(p1, p2, color='blue')
    pen.addText('Ala ma dfdkotat', p1, height=10, color='red')
    pen.addCircle(p1, 40*u.mm, color='blue')
    pen.addCircle(p1, 10.0, color=20)
    #pen.addCircle([0*u.mm, 0*u.mm], 40*u.mm)
    
    from strupy.steel.SteelSection import SteelSection
    sec = SteelSection()
    
    sec.draw_contour(pen, 0)
    pen.set_origin([20.0, 2000.0])
    sec.draw_contour(pen, 0)
    #pen.addMtext(u'asasasa \\P aasas', p1, height=10, color='red')
    pen.addMtext('-------\n 1.2345\n123.457\n 12.345\n  12345\n 1234.5\n-------', p1, height=10, color='red')
    pen.save()
    #Mtect formating
    #http://www.cadforum.cz/cadforum_en/text-formatting-codes-in-mtext-objects-tip8640