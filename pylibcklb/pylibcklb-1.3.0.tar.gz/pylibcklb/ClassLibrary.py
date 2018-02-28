## Class library file for my classes 
#
# @file		    ClassLibrary.py
# @author	    Tobias Ecklebe tobias.ecklebe@outlook.de
# @date		    05.11.2017
# @version	    0.3.0
# @note		    This file includes classes as libary that i think are great for different projects.\n\n
#               To use this file:  from pylibcklb import ClassLibrary as CL\n
#               To use a function: CL.SomeClass()\n\n        
#
# @pre          The library was developed with python 3.6 64 bit
#
# @bug          No bugs at the moment.
#
# @warning      No warning at the moment.
#
# @copyright    pylibcklb package
#               Copyright (C) 2017  Tobias Ecklebe
#
#               This program is free software: you can redistribute it and/or modify
#               it under the terms of the GNU Lesser General Public License as published by
#               the Free Software Foundation, either version 3 of the License, or
#               (at your option) any later version.
#
#               This program is distributed in the hope that it will be useful,
#               but WITHOUT ANY WARRANTY; without even the implied warranty of
#               MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#               GNU Lesser General Public License for more details.
#
#               You should have received a copy of the GNU Lesser General Public License
#               along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from abc import ABCMeta, abstractmethod
import os
import sys
import traceback

## Documentation for a class that handles the debug prints at the console
#  @param object Inherit from object
class cDebug(object):

    LEVEL_ZERO              = 0
    LEVEL_DEVELOPMENT       = 1
    LEVEL_FUNCTIONENTRY     = 2
    LEVEL_All               = 3

    ## Documentation of the constructor
    #  @param self The object pointer.
    #  @param Level Level of debug
    def __init__(self, Level = None):
        if Level is not None:
            self.Level = Level
        else:
            self.Level = self.LEVEL_ZERO

    ## Documentation of the destructor 
    #  @param self The object pointer.
    def __del__(self): 
        self.Level = self.LEVEL_ZERO

    ## Documentation of a method to get the current code line 
    #  @param self The object pointer.
    def get_codeline(self):
        stack = traceback.extract_stack()
        filename, codeline, funcName, text = stack[-4]
        return codeline

    ## Documentation of a method to print by correct debug level an string at the console
    #  @param self The object pointer.
    #  @param Level Level of debug
    #  @param String2Print String to print on the console
    def Print(self, Level, String2Print):
        if self.Level >= Level:
            print('Line ' + str(self.get_codeline()) + ' ' + str(String2Print))
   
    ## Documentation of a method to print by correct debug level an string at the console
    #  @note code comes original from: https://stackoverflow.com/a/36228241
    #  @param self The object pointer.
    def get_function_name(self):
        stack = traceback.extract_stack()
        filename, codeline, funcName, text = stack[-4]
        filename2, codeline2, funcName2, text2 = stack[-5]
        filename = os.path.basename(filename)
        return (filename + ' Line ' + str(codeline) + ' ' + funcName + '() called from function in line ' + str(codeline2) + ' ' + funcName2 + '()')

    ## Documentation of a method to print the current funtion name and the code line out on the console
    #  @param self The object pointer.
    #  @param Level Level of debug
    def PrintFunctionName(self, Level):
        if self.Level >= Level:
            print(str(self.get_function_name()))    

## Documentation for a class that defines things of the observer pattern to inherit
#  @param object Inherit from object
class cObservable(object):
    
    # Documentation of reasons for notification
    CALLBACK_REASON_INIT_NOTIFICATION   = 0
    CALLBACK_REASON_ERROR               = 1
    CALLBACK_REASON_WARNING             = 2
    CALLBACK_REASON_INFORMATION         = 3
    CALLBACK_REASON_QUESTION            = 4

    ## Documentation of the constructor
    #  @param self The object pointer.
    def __init__(self):
        self.observers = []
        self.error_message                  = 'NO_ERROR'
        self.error_detailed_message         = ''
        self.error_informative_message      = 'NO_ERROR_INFORMATIVE'

        self.warning_message                = 'NO_WARNING'
        self.warning_detailed_message       = ''
        self.warning_informative_message    = 'NO_WARNING_INFORMATIVE'

        self.information_message            = 'NO_INFORMATION'
        self.information_detailed_message   = ''
        self.information_informative_message= 'NO_INFORMATION_INFORMATIVE'

        self.question_message               = 'NO_QUESTION'
        self.question_detailed_message      = ''
        self.question_informative_message   = 'NO_QUESTION_INFORMATIVE'
 
    ## Documentation of the destructor 
    #  @param self The object pointer.
    def __del__(self): 
        self.unregister_all()

    ## Documentation of a method to get the error message
    # @param self The object pointer
    def Get_ERROR_MESSAGE(self):
        return self.error_message

    ## Documentation of a method to get the detailed error message
    # @param self The object pointer
    def Get_ERROR_DETAILED_MESSAGE(self):
        return self.error_detailed_message

    ## Documentation of a method to get the informative error message
    # @param self The object pointer
    def Get_ERROR_INFORMATIVE_MESSAGE(self):
        return self.error_informative_message

    ## Documentation of a method to get the warning message
    # @param self The object pointer
    def Get_WARNING_MESSAGE(self):
        return self.warning_message

    ## Documentation of a method to get the detailed warning message
    # @param self The object pointer
    def Get_WARNING_DETAILED_MESSAGE(self):
        return self.warning_detailed_message

    ## Documentation of a method to get the informative warning message
    # @param self The object pointer
    def Get_WARNING_INFORMATIVE_MESSAGE(self):
        return self.warning_informative_message

    ## Documentation of a method to get the information message
    # @param self The object pointer
    def Get_INFORMATION_MESSAGE(self):
        return self.information_message

    ## Documentation of a method to get the detailed information message
    # @param self The object pointer
    def Get_INFORMATION_DETAILED_MESSAGE(self):
        return self.information_detailed_message

    ## Documentation of a method to get the informative information message
    # @param self The object pointer
    def Get_INFORMATION_INFORMATIVE_MESSAGE(self):
        return self.information_informative_message

    ## Documentation of a method to get the question message
    # @param self The object pointer
    def Get_QUESTION_MESSAGE(self):
        return self.question_message

    ## Documentation of a method to get the detailed question message
    # @param self The object pointer
    def Get_QUESTION_DETAILED_MESSAGE(self):
        return self.question_detailed_message

    ## Documentation of a method to get the informative question message
    # @param self The object pointer
    def Get_QUESTION_INFORMATIVE_MESSAGE(self):
        return self.question_informative_message

    ## Documentation of a method to register observer 
    # @param self The object pointer
    # @param observer The observer pointer
    def register(self, observer):
        if not observer in self.observers:
            self.observers.append(observer)
 
    ## Documentation of a method to unregister observer 
    # @param self The object pointer
    # @param observer The observer pointer
    def unregister(self, observer):
        if observer in self.observers:
            print(observer.InstanceName, 'unregistered')  
            self.observers.remove(observer)
 
    ## Documentation of a method to unregister all listed observer
    # @param self The object pointer
    def unregister_all(self):
        if self.observers:
            for observer in self.observers:
                print(observer.InstanceName, 'unregistered')  
            del self.observers[:]

    ## Documentation of a method to notify all listed observer.
    # The following code explaines the example usage:
    # @code
    #   # Can be called easily with a pre defined reason as parameter
    #   self.notify_observers(ModelABC.CALLBACK_REASON_INIT_NOTIFICATION)
    # @endcode
    # @param self The object pointer
    # @param reason Reason why all observer be notified 
    def notify_observers(self, reason=CALLBACK_REASON_INIT_NOTIFICATION):
        for observer in self.observers:
            observer.callback(self, reason)
 
## Documentation for a class that defines things of the observer pattern to inherit
#  @param object Inherit from object
class cObserver(object):
    __metaclass__ = ABCMeta

    @abstractmethod

    ## Documentation of the constructor
    #  @param self The object pointer.
    def __init__(self):
        self.model = None

    ## Documentation of a abstract method to get a callback.
    # The following code explaines the example usage:
    # @code
    #   def callback(self, obj, reason):
    #       if type(obj) is ModelABC:
    #           if reason == ModelABC.CALLBACK_REASON_INIT_NOTIFICATION:
    #               # Update the plot 
    #               self.UpdatePlot()
    #       if type(obj) is ModelXYZ:
    #           # Update the plot no matter which reason is given
    #           self.UpdatePlot()
    # @endcode
    # @param self The object pointer
    # @param obj Check who triggered the callback
    # @param reason Check the reason why is was called
    def callback(self, obj, reason):
        pass

    ## Documentation of a method to store the model for function calls. 
    # That hurts the seperation of model and view of the observer pattern
    # @param self The object pointer
    # @param model The pointer the data model
    def AddModel(self, model):
        self.model = model

       
