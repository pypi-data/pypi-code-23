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

from tabulate import tabulate

language = 'PL'

def title():
    if language == 'EN':
        title =      'SCREW SCHEDULE'
    if language == 'PL':
        title =      'ZESTAWIENIE SRUB'
    return title


def header():
    if language == 'EN':
        header_1 =      ['Element',  'Screw',  'Length',   'Grade',  'Number',   'Number of screws',    'Total']
        header_2 =      [  '  ',     'type',     '  ',       ' ',  'of elements',   'in element',       'number']
        header_3 =      [  '  ',      '  ',      '[mm]',      ' ',      '   ',            '   ',           '   ']
    if language == 'PL':
        header_1 =      ['Element',   'Typ',     'Dlugosc',   'Klasa',  'Ilosc',   'Ilosc srub',    'Laczna']
        header_2 =      [  '  ',     'sruby',     'sruby',    'sruby',  'elementow',   'w elemencie',  'ilosc']
        header_3 =      [  '  ',      '  ',      '[mm]',      ' ',      '   ',           '  ',         '  ']
    return [header_1, header_2, header_3]

def breake_mark():
    return [len(header()[0]) * ['---']]

def record(screw):
    #---
    Member = screw.element.name
    #---
    Screwtype = screw.Screwtype
    #---
    Length = screw.Length
    if not Length: Length = '-'
    #---
    Grade = screw.Grade
    if not Grade: Grade = '-'
    #---
    Number_of_members = screw.element.quantity
    #---
    Number_of_profiles_in_element = screw.Number
    #---
    Total_number = screw.Number * screw.element.quantity 
    #---
    record =[ Member, Screwtype, Length, Grade, Number_of_members, Number_of_profiles_in_element, Total_number] 
    return [record]

# Test if main        
if __name__ == "__main__":
    from environment import*
    DRAWING.open_file()
    SCANER.load_data_to_model()
    print tabulate(header(), numalign="right")  
    screw = STEEL_MODEL.screwlist[2]
    print tabulate(record(screw), numalign="right") 
    #print tabulate(header() + record(profile), numalign="right") 