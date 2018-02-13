#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Jared Webber
    jmw150530

:synopsis:
    Enums for the pipeline

:description:
    This module contains enums for the OS, Rigs, and Disciplines. Useful for resolving
    paths based upon formulas from the formula manager

:applications:
    Any applications that are required to run this script, i.e. Maya.

:see_also:
    Any other code that you have written that this module is similar to.

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#
import os
import platform
import sys
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#
# A enum class that gathers OS information.
def enum(**enums):
    return type('Enum', (), enums)

OSDrives = enum(WINDOWS='C:/', LINUX='//home/', MAC='//home/')

class BaseEnumOS(object):
    def __init__(self):
        self.os    = None
        self.drive = None
        self.eval_os()
        self.eval_drive()

    def eval_os(self):
        self.os = platform.system()

    def eval_drive(self):
        if self.os == 'Windows':
            self.drive = OSDrives.WINDOWS
        elif self.os == 'Linux':
            self.drive = OSDrives.LINUX
        elif self.os == 'Darwin':
            self.drive = OSDrives.MAC

class OSTypeEnum(object):
    def __init__(self):
        os_info    = BaseEnumOS()
        self.os    = os_info.os
        self.drive = os_info.drive


class BaseDiscType(object):
    def __init__(self, long, short):
        self.long  = long
        self.short = short

    def get_long(self):
        return self.long

    def get_short(self):
        return self.short

#Enum class for Disciplines
class DisciplineEnum(object):
    MODEL   = BaseDiscType('modeling', 'mdl')
    SURFACE = BaseDiscType('shading', 'surf')
    RIG     = BaseDiscType('rigging', 'rig')
    LAYOUT     = BaseDiscType('layout', 'lay')
    ANIMATION     = BaseDiscType('animation', 'ani')
    LIGHT     = BaseDiscType('lighting', 'lit')
    COMP    = BaseDiscType('compositing', 'comp')


# The rig types enum:
RigTypes = enum(ANI='ani_rig',
                CACHE='cache_rig',
                LAY='lay_rig',
                MODEL='model_rig',
                PREVIS='previs_rig',
                LIT='lit_rig')
# The disk types enum:
class DiskTypesEnum(object):
    CODE   = 'code'
    CONFIG = 'config'
    DATA   = 'data'
    RENDER = 'render'
    STORE  = 'store'
    WORK   = 'work'
    ALL    = [CODE, CONFIG, DATA, STORE, WORK]
    def get_all(self):
        return self.ALL



