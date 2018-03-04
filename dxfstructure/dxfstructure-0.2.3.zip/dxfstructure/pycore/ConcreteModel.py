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

from Bar import Bar
from Element import Element
import schedule_format_bar
import text_syntax_bar
import tolerance

class ConcreteModel():
    def __init__(self):
        self.create_data_fields() 
        
    #----------------------------------------------
    
    def create_data_fields(self):
        self.barlist = []
        self.elementlist = [] 
        
    #----------------------------------------------
    
    def add_bar(self, bar=Bar()):
        self.barlist.append(bar)

    def add_element(self, element=Element()):
        self.elementlist.append(element)
        
    #----------------------------------------------
    
    def get_bar_number(self):
        return len(self.barlist)

    def print_bar_list_info(self):
        print '++++++++++++++bar_list_info+++++++++++++++++++++'
        print 'There is %s bars' %len(self.barlist)
        for bar in self.barlist:
            print 'bar no. %s - %s x %s in %s' %(bar.Number, bar.pline, bar.Total_Number, bar.element)
    
    def get_element_number(self):
        return len(self.elementlist)

    def print_element_list_info(self):
        print '++++++++++++++element_list_info+++++++++++++++++++++'
        print 'There is %s elements' %len(self.elementlist)
        for element in self.elementlist:
            print 'element %s - with %s bars inside' %(element.name, element.get_bar_number())

    #----------------------------------------------

    def selftest(self):
        print '(Conctere model self test start)'
        self.delete_bars_with_no_maintext()
        self.delete_bars_with_wrong_text_format()
        print '(Conctere model self test end)'   

    def delete_bars_with_no_maintext(self):
        print '---delete_bars_with_no_maintext---'
        for bar in self.barlist:
            if not bar.maintext:
                bar.delete_mark = True
                print 'bar with no text - removing from concrete model'
        #--purge barlist
        self.purge_bar_in_model()
        print '   ...done'

    def delete_bars_with_wrong_text_format(self):
        print '---delete_bars_with_wrong_text_format---'
        for bar in self.barlist:
            if not text_syntax_bar.has_correct_format(bar.maintext_string):
                bar.delete_mark = True
                print 'bar with wrong text format (%s) - removing from concrete model' %bar.maintext_string
        #--purge barlist
        self.purge_bar_in_model()
        print '   ...done'

    
    def purge_bar_in_model(self): # it delete bar if it.delete_mark is True
        for barlist in [self.barlist] + [element.barlist for element in self.elementlist]:
            for i in range(len(barlist)):
                if barlist[i].delete_mark:
                    barlist[i] = None
            while None in barlist:
                barlist.remove(None)
        
    #----------------------------------------------     
        
    def procces_data(self):
        print '********* Procces_data in model ***************'
        self.refresh_bars()
        print '***********************************************'       

    def refresh_bars(self):
        print '---refresh_bars---'
        for bar in self.barlist:
            bar.refresh()
        print '   ...done'

    #----------------------------------------------
    
    @property
    def unicat_bars_sorted_numered(self):
        unicates_list = []
        tmpbarlist = []
        tmpbarlist[:] = self.barlist[:]
        while tmpbarlist:
            unicates_list.append(tmpbarlist[0])
            this_unicat = tmpbarlist[0]
            for i in range(len(tmpbarlist)):
                if tmpbarlist[i].is_the_same_as(this_unicat):
                    tmpbarlist[i] = None
            while None in tmpbarlist:
                tmpbarlist.remove(None)
        #sorting unicates_list
        unicates_list.sort(key=lambda bar: bar.Length, reverse = True)
        #numering
        no = 1
        for unicat in unicates_list:
            unicat.Mark_set(no)
            no += 1
        #---
        return unicates_list
    
    def renumerate(self):
        print '---renumering---'
        unicates_list = self.unicat_bars_sorted_numered
        for unicat in unicates_list:
            for bar in self.barlist:
                if bar.is_the_same_as(unicat):
                    bar.Mark_set(unicat.Mark)
        print '   ...done'

    def find_quite_similare_number(self):
        print '---find_quite_similare_number---'
        unicats = self.unicat_bars_sorted_numered
        typenumber = len(self.unicat_bars_sorted_numered)
        similarlist = []
        for i in range(typenumber):
            for j in range(i,typenumber):
                if i != j:
                    ibar = unicats[i]
                    jbar = unicats[j]
                    if ibar.is_the_same_as(jbar, tolerance = tolerance.similare_bar_dim_tolerance):
                        similarlist.append([ibar.Mark, jbar.Mark]) 
        print '   ...done'
        return similarlist 

    #----------------------------------------------
    
    @property
    def schedule_record(self):
        record = []
        for element in self.elementlist:
            if element.schedule_record_bars:
                record += schedule_format_bar.breake_mark()
                record += element.schedule_record_bars
        return record
    
    @property
    def Mass(self):
        mass = sum(element.Total_Mass_bars for element in self.elementlist)
        mass = round(mass, 1)
        return mass

# Test if main
if __name__ == "__main__":   
    from environment import*
    DRAWING.open_file()
    SCANER.load_data_to_model()
    CONCRETE_MODEL.selftest()
    CONCRETE_MODEL.procces_data()
    print CONCRETE_MODEL.unicat_bars_sorted_numered
    CONCRETE_MODEL.renumerate()
    print CONCRETE_MODEL.find_quite_similare_number()