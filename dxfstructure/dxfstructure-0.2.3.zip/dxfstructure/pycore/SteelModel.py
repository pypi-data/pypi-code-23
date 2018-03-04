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
along with Fooprofil; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

from Profile import Profile
from Element import Element
from Screw import Screw
import schedule_format_profile
import schedule_format_screw
import tolerance

class SteelModel():
    def __init__(self):
        self.create_data_fields() 
        
    #----------------------------------------------
    
    def create_data_fields(self):
        self.profilelist = []
        self.screwlist = []
        self.elementlist = [] 
        
    #----------------------------------------------
    
    def add_profile(self, profile=Profile()):
        self.profilelist.append(profile)

    def add_screw(self, screw=Screw()):
        self.screwlist.append(screw)
        
    def add_element(self, element=Element()):
        self.elementlist.append(element)
        
    #----------------------------------------------
    
    def get_profile_number(self):
        return len(self.profilelist)

    def get_screw_number(self):
        return len(self.screwlist)

    def print_profilelist_info(self):
        print '++++++++++++++profilelist_info+++++++++++++++++++++'
        print 'There is %s profils' %len(self.profilelist)
        for profil in self.profilelist:
            print 'profil no. %s - %s x %s in %s' %(profil.Number, profil.pline, profil.Total_Number, profil.element)
    
    def get_element_number(self):
        return len(self.elementlist)

    def print_element_list_info(self):
        print '++++++++++++++element_list_info+++++++++++++++++++++'
        print 'There is %s elements' %len(self.elementlist)
        for element in self.elementlist:
            print 'element %s - with %s profils inside' %(element.name, element.get_profile_number())

    #----------------------------------------------

    def selftest(self):
        print '(Steel model self test start)'
        
        print '(Steel model self test end)'


    def purge_profile_in_model(self): # it delete profil if it.delete_mark is True
        for profilelist in [self.profilelist] + [element.profilelist for element in self.elementlist]:
            for i in range(len(profilelist)):
                if profilelist[i].delete_mark:
                    profilelist[i] = None
            while None in profilelist:
                profilelist.remove(None)
        
    #----------------------------------------------     
        
    def procces_data(self):
        print '********* Procces_data in steel model ***************'
        self.refresh_profils()
        self.refresh_screws()
        print '***********************************************'       

    def refresh_profils(self):
        print '---refresh_profils---'
        for profil in self.profilelist:
            profil.refresh()
        print '   ...done'

    def refresh_screws(self):
        print '---refresh_screws---'
        for screw in self.screwlist:
            screw.refresh()
        print '   ...done'

    #----------------------------------------------
    
    def renumerate(self):
        print '---renumering---'
        #--sorting with profile mass as key
        self.profilelist.sort(key=lambda profile: profile.Mass, reverse = True)
        #--renumbering profiles in sorted profilelist 
        no = 1
        for profile in self.profilelist:
            profile.data_set(newMark=str(no))
            no += 1
        print '   ...done'

    #----------------------------------------------
    
    @property
    def schedule_record_profiles(self):
        record = []
        for element in self.elementlist:
            if element.schedule_record_profiles:
                record += schedule_format_profile.breake_mark()
                record += element.schedule_record_profiles
        return record

    @property
    def schedule_record_screws(self):
        record = []
        for element in self.elementlist:
            if element.schedule_record_screws:
                record += schedule_format_screw.breake_mark()
                record += element.schedule_record_screws
        return record
    
    @property
    def Mass(self):
        mass = sum(element.Total_Mass_profiles for element in self.elementlist)
        mass = round(mass, 1)
        return mass

# Test if main
if __name__ == "__main__":   
    from environment import*
    DRAWING.open_file()
    SCANER.load_data_to_model()

    STEEL_MODEL.selftest()
    STEEL_MODEL.procces_data()
    
    STEEL_MODEL.renumerate()
    
    DRAWING.save()