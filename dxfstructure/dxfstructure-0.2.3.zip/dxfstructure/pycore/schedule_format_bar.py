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

from tabulate import tabulate

language = 'PL'

def title():
    if language == 'EN':
        title =      'BAR SCHEDULE'
    if language == 'PL':
        title =      'ZESTAWIENIE PRETOW ZBROJENIOWYCH'
    return title

def header():
    if language == 'EN':
        header_1 =      ['Element',  'Bar',   'Steel',      'Bar',      'Bar',         'Bar',       'Number',   'Number of bars',    'Total',     'Total',   'Total']
        header_2 =      [      '',   'mark',  'type',    'diameter',    'length',     'mass',   'of elements',   'in element',    'number',    'length',    'mass']
        header_3 =      [   '   ',    '   ',   '   ',      '   ',       '[mm]',        '[kg]',      '   ',            '   ',           '   ',      '[m]',      '[kg]']
    if language == 'PL':
        header_1 =      ['Element',  'Poz.',   'Typ',      'Sred.',      'Dl.',         'Masa',       'Ilosc',   'Pretow',     'Laczna',     'Laczna',   'Laczna']
        header_2 =      [      '',    'nr',   'stali',     'preta',     'preta',       'preta',       'elem.',   'w elem.',    'ilosc',      'dl.',       'masa']
        header_3 =      [   '   ',    '   ',   '   ',      '   ',       '[mm]',        '[kg]',         '   ',     '   ',        '   ',       '[m]',      '[kg]']
    return [header_1, header_2, header_3]

def breake_mark():
    return [len(header()[0]) * ['---']]

def record(bar):
    #---
    Member = bar.element.name
    #---
    Bar_mark = bar.Mark
    #---
    Steel_type = bar.Grade
    #---
    Bar_diameter = bar.Size
    #---
    Bar_length = bar.Length
    #---
    Bar_mass = bar.Mass
    #---
    Number_of_members = bar.element.quantity
    #---
    Number_of_bars_in_element = bar.Total_Number
    #---
    Total_number = bar.Total_Number * bar.element.quantity 
    #---
    Total_length = bar.Total_Number * bar.element.quantity * bar.Length / 1000.0
    Total_length = round(Total_length, 2)
    #---
    Total_mass = bar.Total_Mass * bar.element.quantity
    #---
    record =[ Member,   Bar_mark,   Steel_type,   Bar_diameter,   Bar_length,  Bar_mass, Number_of_members,  Number_of_bars_in_element,   Total_number,  Total_length, Total_mass] 
    return [record]

def summary():
    if language == 'EN':
        sumary =      'TOTAL MASS FOR DRAWING :'
    if language == 'PL':
        sumary =      'CALKOWITA MASA DLA RYSUNKU :'
    return sumary

# Test if main        
if __name__ == "__main__":
    from environment import*
    DRAWING.open_file()
    SCANER.load_data_to_model()
    print tabulate(header(), numalign="right")  
    bar = CONCRETE_MODEL.barlist[0]
    print tabulate(bar_record(bar), numalign="right") 
    print tabulate(header() + bar_record(bar), numalign="right") 