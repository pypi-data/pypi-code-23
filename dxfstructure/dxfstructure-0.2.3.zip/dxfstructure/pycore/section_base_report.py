'''
--------------------------------------------------------------------------
Copyright (C) 2017-2018 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2018-02-24
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

from tabulate import tabulate
from strupy.pill import SectionBase, u
import strupy.steel.database_sections.sectiontypes as sectiontypes

SectionBase.set_speedmode(1)

available_groups_ids = []
available_groups_ids.append(10) #Single I-beam
available_groups_ids.append(20) #Single channel
available_groups_ids.append(30) #Single Angel
available_groups_ids.append(40) #Rectangular bar
available_groups_ids.append(41) #Round bar
available_groups_ids.append(50) #Flat bar
available_groups_ids.append(60) #Round hollow tube
available_groups_ids.append(61) #Hexagonal hollow tube
available_groups_ids.append(62) #Rectangular hollow tube
available_groups_ids.append(70) #Structural tee
available_groups_ids.append(71) #Tee cut from I-beam

available_groups_names = [sectiontypes.sectiongroups[i] for i in available_groups_ids]

def group_name_id(group_name = 'Single I-beam'):
    return dict (zip(available_groups_names, available_groups_ids))[group_name]

def type_for_group(group_id=10):
    types = sectiontypes.figuregrouplist[group_id]
    #----deleting same nod needed types
    types_to_delete  = ['PRS'] 
    types_to_delete += ['UAPP', 'UUAP', 'UUPN'] #! for now - must be corected in strupy single channel
    types_to_delete += ['CAIP', 'CAEP']
    types = types.difference(set(types_to_delete))
    #---
    return types

def report_group(group_id=10):
    groupname = SectionBase.get_database_sectiongroups()[group_id]
    #---
    title = '++++++++++++++++++++++++++++++++++++++++\n'
    title += '++++++++++++++++++++++++++++++++++++++++\n'
    title +=  groupname + '\n'
    #----
    reportstring = title
    for typ in type_for_group(group_id):
        reportstring += report_type(typ) + '\n'
    return reportstring

def report_type(typ='IPE'):
    title = '--------------------------------------\n'
    title = 'Section type %s\n'%typ
    title +=  SectionBase.get_database_sectiontypesdescription()[typ] + '\n'
    #----
    table = [['name', 'b [mm]', 'h [mm]', 'A [cm2]', 'Wx [cm3]', 'Wy [cm3]']]
    table.append(['---', '---', '---', '---', '---', '---'])
    #---
    sectrecords = []
    for sectname in SectionBase.get_database_sectionlistwithtype(typ):
        sectparam = SectionBase.get_sectionparameters(sectname)
        b = round(sectparam['b'].asUnit(u.mm).asNumber(), 1)
        h = round(sectparam['h'].asUnit(u.mm).asNumber(), 1)
        Wy = round(sectparam['Wy'].asUnit(u.cm**3).asNumber(), 2)
        Wz = round(sectparam['Wz'].asUnit(u.cm**3).asNumber(), 2)
        A = round(sectparam['Ax'].asUnit(u.cm**2).asNumber(), 2)
        sectrecords.append([sectname, b, h, A, Wy, Wy])
    sectrecords.sort(key=lambda i: i[2], reverse = False)
    #---
    table = table + sectrecords
    #---
    tablestring = tabulate(table, numalign="right") 
    return '\n' + title + tablestring

def report():
    reportstring = ''
    for group in available_groups_ids:
        reportstring += report_group(group)
    return reportstring
    
# Test if main        
if __name__ == "__main__":
    #print report_type()
    print report_group()
    #print type_for_group()
    #print report()