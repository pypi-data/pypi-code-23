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

from PyQt4 import QtGui

import x_dxf_test_path
from EzdxfPen2D import EzdxfPen2D

_APP_ID = 'DXF_STRUCTURE'

class Drawing():

    def __init__(self):
        print "DS_drawing init"
        self.filepath = None
        self.dwg = None
        self.pen = EzdxfPen2D()
        self.name = 'Not named'
        #---
        self.create_data_fields()

    #----------------------------------------------
    
    def create_data_fields(self):
        self.DS_BARS = []
        self.DS_STEXTS = []
        self.DS_CTEXTS = []
        self.DS_CTEXTREFS = []
        self.DS_DEPLINES = []
        self.DS_RANGEPLINES = []
        self.DS_RANGECIRCELS = []
        self.DS_ELEMENT_FRAME = []
        self.DS_ELEMENT_TEXT = []
        self.DS_COMMAND = []
        self.DS_DATA = []

    #----------------------------------------------

    def open_file(self, path=None):
        if path == None:
            dxfpath = x_dxf_test_path.test_path
        else:
            dxfpath = path
        self.filepath = dxfpath
        self.dwg = ezdxf.readfile(dxfpath)
        self.pen.assign_Ezdxf(self.dwg)
        #---
        self.load_data()

    def save(self):
        try:
            print '---saveing---'
            self.pen.save()
            print '   ...done'
        except IOError:
            QtGui.QMessageBox.information(None, 'Info', 'It look like the file is open! Close file and try again!')        
            print '   ...not saved'

    def reload_file(self):
        self.open_file(self.filepath)

    #----------------------------------------------
        
    def load_data(self):
        print '***** Loading neeed DXF data from file *******'
        self.get_BARS()
        self.get_STEXTS()
        self.get_CTEXTS()
        self.get_CTEXTREFS()
        self.get_DEPLINES()
        self.get_RANGEPLINES()
        self.get_RANGECIRCELS()   
        self.get_ELEMENT_FRAME()     
        self.get_ELEMENT_TEXT()
        self.get_COMMAND()
        self.xdata_create_APP_ID_entry()
        self.set_id_for_ctexts()
        self.set_id_for_stexts()
        print '***********************************************'
                
    def get_BARS(self):
        print '---geting bars---'
        BARS = []
        for e in self.dwg.modelspace():
            if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'DS_CBAR':
                BARS.append(e)
        print '   %s found'%len(BARS)        
        print '   ...done'
        self.DS_BARS = BARS
        return BARS

    def get_CTEXTS(self):
        print '----geting ctext----'
        CTEXTS = []
        for e in self.dwg.modelspace():
            if e.dxftype() == 'TEXT' and e.dxf.layer == 'DS_CTEXT':
                CTEXTS.append(e)
        print '   %s found'%len(CTEXTS) 
        print '   ...done'
        self.DS_CTEXTS = CTEXTS
        return CTEXTS

    def get_CTEXTREFS(self):
        print '----geting CTEXTREFS----'
        CTEXTREFS = []
        for e in self.dwg.modelspace():
            if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'DS_CTEXT':
                CTEXTREFS.append(e)
        print '   %s found'%len(CTEXTREFS) 
        print '   ...done'
        self.DS_CTEXTREFS= CTEXTREFS
        return CTEXTREFS
        
    def get_STEXTS(self):
        print '----geting stext----'
        STEXTS = []
        for e in self.dwg.modelspace():
            if e.dxftype() == 'TEXT' and e.dxf.layer == 'DS_STEXT':
                STEXTS.append(e)
        print '   %s found'%len(STEXTS) 
        print '   ...done'
        self.DS_STEXTS = STEXTS
        return STEXTS

    def get_DEPLINES(self):        
        print '----geting deplines----'
        DEPLINES = []
        for e in self.dwg.modelspace():
            if e.dxftype() == 'LINE' and e.dxf.layer == 'DS_DEPLINE':
                DEPLINES.append(e)
        print '   %s found'%len(DEPLINES) 
        print '   ...done'
        self.DS_DEPLINES = DEPLINES
        return DEPLINES
        
    def get_RANGEPLINES(self):        
        print '----geting RANGEPLINES----'
        RANGEPLINES = []
        for e in self.dwg.modelspace():
            if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'DS_RANGE':
                RANGEPLINES.append(e)
        print '   %s found'%len(RANGEPLINES) 
        print '   ...done'
        self.DS_RANGEPLINES = RANGEPLINES
        return RANGEPLINES 

    def get_RANGECIRCELS(self):        
        print '----geting RANGECIRCELS----'
        RANGECIRCELS = []
        for e in self.dwg.modelspace():
            if e.dxftype() == 'CIRCLE' and e.dxf.layer == 'DS_RANGE':
                RANGECIRCELS.append(e)
        print '   %s found'%len(RANGECIRCELS) 
        print '   ...done'
        self.DS_RANGECIRCELS = RANGECIRCELS
        return RANGECIRCELS
    
    def get_ELEMENT_FRAME(self):        
        print '----geting ELEMENT_FRAME----'
        ELEMENT_FRAME = []
        for e in self.dwg.modelspace():
            if e.dxftype() == 'LWPOLYLINE' and e.dxf.layer == 'DS_ELEMENT':
                ELEMENT_FRAME.append(e)
        print '   %s found'%len(ELEMENT_FRAME) 
        print '   ...done'
        self.DS_ELEMENT_FRAME = ELEMENT_FRAME
        return ELEMENT_FRAME

    def get_ELEMENT_TEXT(self):        
        print '----geting ELEMENT_TEXT----'
        ELEMENT_TEXT = []
        for e in self.dwg.modelspace():
            if e.dxftype() == 'TEXT' and e.dxf.layer == 'DS_ELEMENT':
                ELEMENT_TEXT.append(e)
        print '   %s found'%len(ELEMENT_TEXT) 
        print '   ...done'
        self.DS_ELEMENT_TEXT = ELEMENT_TEXT
        return ELEMENT_TEXT

    def get_COMMAND(self):        
        print '----geting COMMAND----'
        COMMAND = []
        for e in self.dwg.modelspace():
            if e.dxftype() == 'TEXT' and e.dxf.layer == 'DS_COMMAND':
                COMMAND.append(e)
        print '   %s found'%len(COMMAND)
        print '   ...done'
        self.DS_COMMAND = COMMAND
        return COMMAND

    #----------------------------------------------
        
    def xdata_create_APP_ID_entry(self):
        if not self.dwg.appids.has_entry(_APP_ID):
            self.dwg.appids.new(_APP_ID)
            print "APP_ID entry '%s' created" %_APP_ID
        else:
            print "APP_ID entry '%s' already exist" %_APP_ID

    def idstring_make_one(self):
        return uuid.uuid1().hex[:20].upper()

    def entity_id_get(self, entity):   
        if not entity.tags.has_xdata(_APP_ID):
            random_id = self.idstring_make_one()
            entity.tags.new_xdata(_APP_ID, [(1000, random_id)])
        return entity.tags.get_xdata(_APP_ID).find_first(1000)
            
    def entity_id_set(self, entity, id):
        if not entity.tags.has_xdata(_APP_ID):
            entity.tags.new_xdata(_APP_ID, [(1000, id)])
        else:
            entity.tags.get_xdata(_APP_ID).update(1000, id)

    def entity_id_set_random(self, entity):   
        random_id = self.idstring_make_one()  
        if not entity.tags.has_xdata(_APP_ID):
            self.entity_id_get(entity)
        else:
            random_id = self.idstring_make_one()
            self.entity_id_set(entity, random_id)
        return entity.tags.get_xdata(_APP_ID).find_first(1000)
            
    def set_id_for_ctexts(self):
        print '----setting id for ctexts----'
        for entity in self.DS_CTEXTS:
            self.entity_id_get(entity)
        print '   ...done'

    def set_id_for_stexts(self):
        print '----setting id for stexts----'
        for entity in self.DS_STEXTS:
            self.entity_id_get(entity)
        print '   ...done'

    #----------------------------------------------

# Test if main
if __name__ == "__main__":
    from environment import*
    DRAWING.open_file()
    '''
    DRAWING.set_id_for_ctexts()
    for i in DRAWING.DS_CTEXTS:
        print DRAWING.entity_id_get(i)
    DRAWING.save()
    example_entity=DRAWING.DS_CTEXTS[0]
    print DRAWING.entity_id_get(example_entity)
    DRAWING.entity_id_set(example_entity, 'dupa444')
    print DRAWING.entity_id_get(example_entity)
    for i in DRAWING.dwg.modelspace():
        pass
        #print i, i.dxf.layer
    pass
    '''