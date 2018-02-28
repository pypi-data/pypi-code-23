# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import str
from builtins import object
import inspect
import os.path
from pathlib import Path
import gettext
from ._File import File

_ = gettext.gettext


class Template(File):

    def __init__(self,*args,**kwargs):
        File.__init__(self,*args,**kwargs)
        self.logger = logging.getLogger(__name__)


class TemplateManager(ObjectManager):
    schema = "schemas/TemplateManager.json"
    extensions = ['*']

    def __init__(self,*args,**kwargs):
        ObjectManager.__init__(self,Template,*args,**kwargs)
        self.logger = logging.getLogger(__name__)
