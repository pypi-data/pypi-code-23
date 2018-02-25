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

import re

from Drawing import Drawing
import layer_system
import color_system

class Executor():
    def __init__(self):
        self.Creator = None
        #----
        self.create_data_fields()
        
    def create_data_fields(self):
        self.commandlist = []
        
    #----------------------------------------------

    def asign_Creator(self, Creator):
        self.Creator = Creator

    #----------------------------------------------

    def get_commands_report(self):
        if self.commandlist:
            report = 'Waiting to execute command list:\n'
            for command in self.commandlist:\
                report += "'%s' at %s\n" %(command[0], command[1])
            return report
        else:
            return 'Empty command list - nothing to report'

    #----------------------------------------------
    
    def DoCommand(self, command, point = [0,0, 0,0]):
        print "DoCommand - '%s'......" %command
        #-----steel section ---------------
        re_text = re.compile('\s*steel section\s*(.+)\s*') # steel section IPE / steel section IPE 120
        if re_text.search(command):
            sectname = re_text.findall(command)[0]
            print 'Drawing steel section %s at %s' %(sectname, point)
            self.Creator.draw_steel_section(sectname, point)
        #-----steel bolt ---------------
        re_text = re.compile('\s*steel bolt\s*(.+)\s*') # steel bolt M12
        if re_text.search(command):
            BoltDim = re_text.findall(command)[0]
            print 'Drawing bolt %s at %s' %(BoltDim, point)
            self.Creator.draw_steel_bolt(BoltDim, point)
        print '  .....done'

    def ExecuteAll(self):
        for command in self.commandlist:
            self.DoCommand(command[0], command[1])
            command[2].dxf.color = color_system.dead_command[0] 


# Test if main
if __name__ == "__main__":
    from environment import*
    DRAWING.open_file()
    SCANER.load_data_to_model()
    #---
    print EXECUTOR.get_commands_report()
    EXECUTOR.ExecuteAll()
    #EXECUTOR.DoCommand('steel section IPE 200')
    DRAWING.save()