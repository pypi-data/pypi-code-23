#!/usr/bin/env python

'''
 Mulator - An extensible {ARM} {e,si}mulator
 Copyright 2011-2012  Pat Pannuto <pat.pannuto@gmail.com>
 Copyright 2017  Andrew Lukefahr <lukefahr@indiana.edu>

 This file is part of Mulator.

 Mulator is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Mulator is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Mulator.  If not, see <http://www.gnu.org/licenses/>.
'''

from inspect import getframeinfo, stack
import multiprocessing
import os
import sys

try:
    import threading
except ImportError:
    print("ERROR: Your Python doesn't support threads")
    raise
try:    
    import queue 
except ImportError:
    import Queue as queue

try:
    import PyMulatorC as PyMulatorC
except ImportError:
    print("ERROR:  Couldn't find PyMulatorC module?")
    raise


'''
 This is public PyMulator class.  PyMulatorC should not be called directly.

 This provides a gdb-like interface into Mulator callable from within python.
 All communication to/from Mulator is in gdb-compatable strings

 To use this class, you will need to provide a dictionary (or equivalent) of 
 the register and memory contents. See __init__ for more details. 

 PyMulator currently accepts the following commands:
    - stepi:  read the current pc register, find the instruction in memory, 
                execute it, and update the register/memory contents accordingly
    - quit:  stops the currently executing Mulator                
 
'''
class PyMulator(object):
    
    class PyMulatorError(Exception): 
        pass

    '''
     Example of how a regfile could work
    '''
    class RegFile:
        def __init__(this): print ("WARNING: dummy RegFile")
        def __getitem__(this,key):
            print ('RegRd ' + str(key))
            if key == 'pc': return 0+4 # ARM PC is wierd
            return 0
        def __setitem__(this,key,val):            
            print ('RegWr ' + str(key))
   
    '''
     Example of how a memory could work
    '''
    class Memory:
        def __init__(this): print ("WARNING: dummy Memory")
        def __getitem__(this,key):
            addr = key[0]
            size = key[1]
            print ('MemRd uint' + str(size) + '_t ' + hex(addr))
            return 0x4011
        def __setitem__(this,key,val):            
            print ('MemWr ' + str(key))
 

    def __init__(this, registers, memory, debug=False):
        '''
        Create a PyMulator module

        @registers: dictionary-like structure to allow access via 
        the ['regName'] operator
        i.e. registers['pc'] = 0x100, x = registers['r2'] 

        @memory: dictionary-like structure to allow access via 
        the [ (memAddr,size) ] operator
        i.e. memory[ (0x100,32) ] = 0xdeadbeef, memory[ (0x20,8) ] = 0x55

        @debug: enable debugging output from this module
        '''

        this.ONEYEAR = 264 * 24 * 60 * 60
        
        this.debug = debug

        this.registers = registers if registers else RegFile()
        this.memory = memory if memory else Memory()

        #
        # The GIL causes some issues with Mulator
        # Speciflcally, when we call Python->C we acquire the GIL
        # and then Pthon->C->Python still has the GIL.  
        # If that blocks, it will never release the GIL
        # and nobody can make forward progress. 
        # To solve this, the Mulator work is forked into a seperate 
        # single-threaded process, so nobody cares about who owns the GIL
        #
        #
        this.mulator_req_queue = multiprocessing.Queue()
        this.mulator_resp_queue = multiprocessing.Queue()
        this.mulator_thread = multiprocessing.Process(
                target=this._mulator_process, \
                args=(this.mulator_req_queue, this.mulator_resp_queue))
        this.mulator_thread.daemon = True
        this.mulator_thread.start()                                
    
    def stepi(this):
        '''
        Single steps using Mulator
        '''
        this._process_cmd('stepi')
    
    def quit(this):
        this._process_cmd('quit')
    
    def _process_cmd(this, cmd):
        '''
         sends an arbirary command to Mulator, processes
         any subsequent requests for regs/memory
         and returns when the command is finished

         @cmd: string form of a gdb-like command 
        '''
        this._dprintf('Issueing cmd: ' + str(cmd))
        this.mulator_req_queue.put(cmd)
        
        #wait for a message
        msg = this.mulator_resp_queue.get()
        while not msg.startswith('DONE: ' + cmd):

            # Mulator wants some other data
            # go get it, and respond back
            resp = this._get_data(msg)

            this._dprintf('servicing req: ' + str(msg))
            this._dprintf('with resp: ' + str(resp))
            this.mulator_req_queue.put(resp)

            # get the next one                
            msg = this.mulator_resp_queue.get()
       
        assert( this.mulator_resp_queue.empty())
        assert( this.mulator_req_queue.empty())

        this._dprintf(cmd + ' complete, returning')

    def _get_data(this, gdb_str):
        '''
        
        Parses gdb-formatted strings from Mulator
        grabs Python data, and returns a gdb-formatted 
        string of that data

        @gdb_str: a gdb-like string of the requested data

        '''
        #this._dprintf('Input: ' + gdb_str)

        cmds = gdb_str.split()
        result = None

        # register read
        if 'info' == cmds[0]:
            assert( len(cmds) > 1) 

            if 'register' in cmds[1]:
                assert(len(cmds) > 2)

                this._dprintf('Reading Register: ' + cmds[2])

                reg = cmds[2]

                reg_val = this.registers[reg]

                result = reg + ' ' + hex(reg_val)

        # register write
        elif cmds[0].startswith('p'):
            assert( len(cmds) > 3)
            this._dprintf('Writing Register: ' + cmds[1])

            reg = cmds[1].strip('$')
            # 2 is equal sign
            val = int(cmds[3],16)
            
            this.registers[reg] = val 

            result = '$0 = ' + hex(val)

        # memory read
        elif cmds[0].startswith('x/'):
            assert( len(cmds) > 1)
            this._dprintf('Reading Memory: ' + cmds[1])

            addr = int(cmds[1],16)

            if '/1xw' in cmds[0]: # word
                val = this.memory[(addr,32)]
            elif '/1xh' in cmds[0]: # halfword
                val = this.memory[(addr,16)]
            elif '/1xb' in cmds[0]: # word
                val = this.memory[(addr,8)]
            else: 
                raise Exception("Bad Memory Read")

            result = hex(addr) + ': ' + hex(val)

        #memory write 
        elif 'set' == cmds[0]:
            assert(len(cmds) > 4 )
            this._dprintf('Writing Memory: ' + cmds[2])

            addr = int(cmds[2],16)

            if cmds[1] == '{uint32_t}':
                size = 32
            elif cmds[1] == '{uint16_t}':
                size = 16
            elif cmds[1] == '{uint8_t}':
                size = 8
            else: raise Exception("Bad Memory Write")

            val = int(cmds[4],16)

            this.memory[(addr,size)] = val 

            result = ""
            
        #this._dprintf('Output: ' + str(result))
        return result
    

    def _mulator_process(this, reqQ, respQ):
        '''
        Seperate Process that handles all interfacing with Mulator
        so we don't have to worry about the GIL

        This should only communicate with the rest of the class 
        via the queues

        @reqQ: a request queue containing requests from the main process
        
        @respQ:  a response queue where this process places results

        '''
        # register our callback function
        PyMulatorC.register_callback(this._mulator_callback)
       
        msg = reqQ.get()
        while not msg.startswith('quit'):
            
            PyMulatorC.call_to_mulator(msg)

            respQ.put('DONE: ' + msg)

            msg = reqQ.get()

        this._dprintf('Quitting\n') 
        respQ.put('DONE: ' + msg)

    
    def _mulator_callback(this,gdb_req):
        '''
        Part of the _mulator_process callstack

        Callback by Mulator to request additional data from the system
        accessably through Python (namely registers and memory)

        @gdb_req:  a gdb-like string of a request from Mulator

        @return: a gdb-like string of a response to Mulator

        '''
        
        this._dprintf("Adding to queue:" + str(gdb_req))
        this.mulator_resp_queue.put(gdb_req)
        gdb_resp = this.mulator_req_queue.get()
        this._dprintf("received resp:" + str(gdb_resp))

        return gdb_resp

    def _dprintf(this, out):
        '''
         A simple debug function with formatting similar to Mulator

         @out: the message to be printed
        '''
        if (this.debug == True):
            caller = getframeinfo(stack()[1][0])
            #keep similar formatting as Mulator
            print "222  %s:%d : %s" %  \
                (os.path.basename(caller.filename), caller.lineno, out)



