# coding: utf-8

import sys
import os
import time
import re
import datetime

class pyarrot():
    def __init__(self, programDescription=[]):
        # Define option strings of "mode selector".
        self.modeArgStr = '-mode'
        
        # Define option value of batch mode.
        # If you set the argument that " -mode=batch"
        #    PyArrot will execute as batch mode.
        self.modeArgStr_batch = 'batch'
        
        # Define option strings of "function selector".
        self.commandArgStr = '-command'

        # 開始時に表示するプログラム説明
        self.programDescription = programDescription
        
        # Function list
        self.functionStacker = []
        
        # Delay time for PyArrot message.
        # to fix the problems that differ in order between message of PyArrot and logger output of your Script.
        # maybe this cause of some delay of logger output
        self.command_delay = 0.1
    
    def inputDate(self, message='', defaultValue='', batchArgStr='', date_format='%Y/%m/%d'):
        '''
        @param message
        @param defaultValue
        @param batchArgStr
        @param date_format '%Y/%m/%d'
        @return Inputed date object.
        
        1, Show message that request a formatted date strings.
        2, Return Date object.
        '''
        target_date = None
        while target_date==None:
            try:
                inputted_str = self.inputValue(message, defaultValue, batchArgStr)
            except Exception as e:
                print("input error: %s" % e)
                continue
            
            try:
                target_date = datetime.datetime.strptime(inputted_str, date_format)
            except Exception as e:
                print("date format error: %s" % e)
            
        return target_date
    
    def selectFile(self, message='', target_dir='', defaultValue='', batchArgStr='', reject_pattern='^_', all_choice=False):
        '''
        @param message
        @param target_dir
        @param defaultValue
        @param batchArgStr
        @param reject_pattern
        @param all_choice
        @return filename strings
        
        1, View file-list of target_dir.
        2, View a message that ask to the file-number in file-list.
        3, Return selected filename strings.
        '''
        
        filelist = []
        for f in os.listdir(target_dir):
            if not re.match(r"%s" % reject_pattern, f):
                filelist.append(f)
        
        print("----------choose.----------")
        i = 0
        if all_choice:
            print("%d. %s" % (i,"all"))
            i = i+1
        for e in filelist:
            print("%d. %s" % (i,e))
            i = i+1
        print("-----------------------------")
        
        target_file = ''
        while target_file=='':
            try:
                file_no = int(self.inputValue(message, defaultValue, batchArgStr))
                if all_choice:
                    if file_no == 0:
                        return filelist
                    file_no = file_no -1
                if len(filelist) > file_no:
                    target_file = filelist[file_no]
            except:
                pass
        
        if all_choice:
            return [target_file]
        else:
            return target_file

    def inputValue(self, message='', defaultValue='', batchArgStr=''):
        '''
        @param message
        @param defaultValue
        @param batchArgStr
        @return value
        
        If in Interactive mode, Return value that inputted by prompt.
        If in Batch mode, Return value that commandline Arg.
        
        1, Show message that request to input a value.
        2, Return the inputed value.
        '''

        if self.isBatchMode():
            val = self.getArgValue(batchArgStr)
        else:
            time.sleep(self.command_delay)
            val = input(message)
        
        if len(val) > 0:
            return val
        else:
            return defaultValue

    def addFunction(self, triggerWord, description, stackfunction):
        '''
        @param triggerWord
        @param description
        @param stackfunction
        
        Define The function for bach/Interactive mode.
        '''
        self.functionStacker.append({'trigger':triggerWord, 'description':description, 'function':stackfunction})

    def start(self):
        '''
        Start function.
        '''

        # Add default function.
        self.addFunction('h', 'Help.', self.showHelp)
        self.addFunction('q', 'Quit.', self.quit)

        # 引数に'-h'が指定されていた場合、コマンド一覧を表示して終了
        if self.existArg('-h'):
            self.showHelp()
            sys.exit()

        # バッチモードだった場合はバッチモードで、プロンプトモードだった場合はプロンプトモードで起動
        if self.isBatchMode():
            self.startBatchMode()
        else:
            self.startInteractiveMode()

        return 0

    def isBatchMode(self):
        '''
        @return boolean
        
        Check Args to get program mode.
        '''
        
        mode = self.getArgValue(self.modeArgStr)

        # return true, if option has '-mode=batch'
        if mode==self.modeArgStr_batch:
            return True
        else:
            return False

    def showHelp(self):
        '''
        View help message.
        '''
        print('Input following command([command] Description.) to execute the function.')
        for eachFunction in self.functionStacker:
            print(' [' + eachFunction['trigger'] + '] ' + eachFunction['description'])

    def quit(self):
        '''
        End function.
        '''
        print("Bye.")
        sys.exit()

    def startInteractiveMode(self):
        '''
        Start Interactive mode.
        '''
        
        # To prevent miss order to output messages.
        time.sleep(self.command_delay)

        print('######################################################################')
        for eachLine in self.programDescription:
            print('### ' + eachLine)
        print("### Start Datetime: {0:%Y/%m/%d %H:%M:%S}".format(datetime.datetime.now()))
        print('######################################################################')

        # Show command help as default.
        self.showHelp()

        # Loop of Interactive prompt.
        try:
            while 1:
                time.sleep(self.command_delay)
                command = input("[{0:%H:%M:%S}] > ".format(datetime.datetime.now()))

                for eachFunction in self.functionStacker:
                    if eachFunction['trigger'].lower() == command.lower():
                        eachFunction['function']()
                        break
        except KeyboardInterrupt:
            print("Quit by user command(CTRL-C).")
        except Exception as e:
            print("Unknown Error(%s)." % e)

    def startBatchMode(self):
        """
        Start Batch mode.
        Execute the function that received an argument as "-command=FUNCTION-CODE".
        """

        command = self.getArgValue(self.commandArgStr)
        if command!='':
            for eachFunction in self.functionStacker:
                if eachFunction['trigger'].lower() == command.lower():
                    eachFunction['function']()
                    break
        return 0
    
    def getArgValue(self, key):
        """
        @param key Is argument key strings
        @return argument value
        
        Return the values which separate '='.
        If no '=' return ''.
        """
        val = ''
        if len(sys.argv) > 1:
            for each_arg in sys.argv:
                if each_arg.split("=")[0] == key:
                    val = each_arg.split("=")[1]
        return val
    
    def existArg(self, key):
        """
        @param key Is argument key strings
        @return boolean
        
        If Args have key value, return True.
        """
        if len(sys.argv) > 1:
            for each_arg in sys.argv:
                if each_arg == key:
                    return True
        return False