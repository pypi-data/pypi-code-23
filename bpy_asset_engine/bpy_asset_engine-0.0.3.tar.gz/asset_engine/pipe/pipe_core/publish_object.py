#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Jared Webber
    jmw150530

:synopsis:
    Contains Object Publishing information

:description:
    The classes in this module contain variables with the proper formula name and
    Rig Enum identifier to retrieve and publish those objects from a path of disk
    resolved from PipeContext

:applications:
    Maya

:see_also:
    Any other code that you have written that this module is similar to.

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Built-in
from ..pipe_core import pipe_enums

# Third party

# Internal

# External

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#




class ModelRig(object):
    MODEL_RIG = 'as_rig_pub_official_file'
    RIG_TYPE = pipe_enums.RigTypes.MODEL
    def __init__(self):
        pass

class LayRig(object):
    LAY_RIG = 'as_rig_pub_official_file'
    RIG_TYPE = pipe_enums.RigTypes.LAY
    def __init__(self):
        pass

class AnimRig(object):
    ANIM_RIG = 'as_rig_pub_official_file'
    RIG_TYPE = pipe_enums.RigTypes.ANI
    def __init__(self):
        pass

