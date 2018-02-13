#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Jared Webber
    jmw150530

:synopsis:
    Creates PipeObjects - ProjectObject and AssetObject

:description:
    This module creates ProjectObjects and AssetObjects with kwargs that are resolved
    from formulas using the formula manager and type_object module. It includes logic to
    set the values of the keys for ProjectObjects and AssetObjects

:applications:
    Any applications that are required to run this script, i.e. Maya.

:see_also:
    Any other code that you have written that this module is similar to.

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Built-in
# Third party

# Internal

# External
from ..pipe_core.pipe_context import PipeContext, PathContext
from ..pipe_core.publish_object import ModelRig, AnimRig
from ..pipe_core import type_object as TO


#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class PipeObject(object):
    """
    This Class defines a Pipeline Object.
    """
    def __init__(self, **kwargs):
        """
        Stores the values of XML keys that are generated via the Project class
        :param kwargs:
        """
        self._id            = kwargs.setdefault('_id', None)
        self.name           = kwargs.setdefault('name', None)
        self.path = kwargs.setdefault('path', None)

class ProjectObject(PipeObject):
    """
    This Class defines a Project Object.
    """
    def __init__(self, **kwargs):
        """
        Stores the values of XML keys that are generated via the Project class
        :param kwargs:
        """
        super(self.__class__, self).__init__(**kwargs)
        PipeObject.__init__(self, **kwargs)
        self.modified_date  = kwargs.setdefault('modified_date', None)
        self.modified_by    = kwargs.setdefault('modified_by', None)
        self.description    = kwargs.setdefault('description', None)
        self.created_by     = kwargs.setdefault('created_by', None)
        self.creation_date  = kwargs.setdefault('creation_date', None)

class EpisodeObject(PipeObject):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        PipeObject.__init__(self, **kwargs)

class AssetTypeObject(PipeObject):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        PipeObject.__init__(self, **kwargs)


class AssetObject(PipeObject):
    """
    This class defines an Asset Object
    """
    def __init__(self, **kwargs):
        """
        Stores the values of XML keys generated via the Asset Class
        :param kwargs:
        """
        super(self.__class__, self).__init__(**kwargs)
        PipeObject.__init__(self, **kwargs)
        self.modified_date  = kwargs.setdefault('modified_date', None)
        self.modified_by    = kwargs.setdefault('modified_by', None)
        self.description    = kwargs.setdefault('description', None)
        self.created_by     = kwargs.setdefault('created_by', None)
        self.creation_date  = kwargs.setdefault('creation_date', None)
        self.style          = kwargs.setdefault('style', None)
        self.type           = kwargs.setdefault('type', None)
        self.version        = kwargs.setdefault('version', None)
        self.components     = []

    # def get_ani_rig_official(self):
    #     ani_rig = AnimRig.ANIM_RIG
    #     rig_type = ModelRig.RIG_TYPE
    #     context = PipeContext.eval_path(ani_rig, **rig_type)
    #
    #
    # def get_model_rig_official(self):
    #     model_rig = ModelRig.MODEL_RIG
    #     rig_type = AnimRig.RIG_TYPE
    #     context = PipeContext.eval_path(model_rig, **rig_type)


class ComponentObject(AssetObject):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        AssetObject.__init__(self, **kwargs)
        self.descriptor     = kwargs.setdefault('descriptor', None)
        self.version        = None


class SequenceObject(PipeObject):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        PipeObject.__init__(self, **kwargs)


class ShotObject(PipeObject):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        PipeObject.__init__(self, **kwargs)