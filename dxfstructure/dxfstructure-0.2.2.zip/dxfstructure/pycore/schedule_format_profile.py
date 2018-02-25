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
from strupy.pill import SectionBase

language = 'PL'

def title():
    if language == 'EN':
        title =      'FROFILE SCHEDULE'
    if language == 'PL':
        title =      'ZESTAWIENIE PROFILI'
    return title

def header():
    if language == 'EN':
        header_1 =      ['Element',  'Bar',   'Steel',      'Profile',     'Profile',   'Profile',       'Number',   'Number of Profiles',    'Total',     'Total',   'Total']
        header_2 =      [      '',   'mark',  'type',          '',         'length',     'mass',       'of elements',   'in element',         'number',    'length',    'mass']
        header_3 =      [   '   ',    '   ',   '   ',      '   ',       '[mm]',        '[kg]',      '   ',            '   ',           '   ',      '[m]',      '[kg]']
    if language == 'PL':
        header_1 =      ['Element',  'Poz.',   'Typ',      'Profil',      'Dl.',         'Masa',       'Ilosc',   'Profili',     'Laczna',     'Laczna',   'Laczna']
        header_2 =      [      '',    'nr',   'stali',        '',       'profilu',     'profilu',      'elem.',   'w elem.',      'ilosc',      'dl.',       'masa']
        header_3 =      [   '   ',    '   ',   '   ',      '   ',       '[mm]',        '[kg]',         '   ',     '   ',        '   ',       '[m]',      '[kg]']
    return [header_1, header_2, header_3]

def breake_mark():
    return [len(header()[0]) * ['---']]

def record(profile):
    #---
    Member = profile.element.name
    #---
    Profile_mark = profile.Mark
    #---
    Steel_type = profile.Grade
    #---
    Profile_sect = profile.Sect
    if not Profile_sect in SectionBase.get_database_sectionlist():
        Profile_sect += '(!-not reconized-!)'
    #---
    Profile_length = profile.Length
    #---
    Profile_mass = profile.Mass
    #---
    Number_of_members = profile.element.quantity
    #---
    Number_of_profiles_in_element = profile.Number
    #---
    Total_number = profile.Number * profile.element.quantity 
    #---
    Total_length = profile.Number * profile.element.quantity * profile.Length / 1000.0
    Total_length = round(Total_length, 2)
    #---
    Total_mass = profile.Total_Mass * profile.element.quantity
    #---
    record =[ Member,   Profile_mark,   Steel_type,   Profile_sect,   Profile_length,  Profile_mass, Number_of_members,  Number_of_profiles_in_element,   Total_number,  Total_length, Total_mass] 
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
    profile = STEEL_MODEL.profilelist[0]
    print tabulate(record(profile), numalign="right") 
    print tabulate(header() + record(profile), numalign="right") 