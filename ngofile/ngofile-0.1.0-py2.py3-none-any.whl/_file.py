# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 11:06:57 2012

@author: Cédric ROMAN
"""
from __future__ import unicode_literals

import logging
import re
from builtins import object
from builtins import str

from ngomodel import ClassWithSchema
from ngomodel import ObjectManager


class File(ClassWithSchema):
    """ file object where can be extrated protected areas """
    schemaPath = "D:/code/python-ngoproject/src/ngoproject/schemas/File.json"

    def get_protected_areas(self):
        """ returns a dictionnary of the protected areas of a source code
    
        { region_id : user_source_code}
        sourcecode : string containing source code
        """
        if not self.path:
            raise Exception(
                'path needs to be set before getting protected areas')
        regex = r'PROTECTED REGION ID\((?P<canonical>[\w\.]+)\) ENABLED START @\*/\s*?# Insert here user code\n(?P<usercode>.*?)\n\s*# End of user code\s*#/\*@ PROTECTED REGION END @\*/'
        reg = re.compile(regex, re.DOTALL | re.MULTILINE | re.UNICODE)
        f = self.path.open("r")
        code = f.read()
        return {cn: uc for (cn, uc) in reg.findall(sourcecode)}


class FileManager(ObjectManager):
    """ main file manager """
    extensions = ["*"]

    def __init__(self, *args, **kwargs):
        ObjectManager.__init__(self, File, *args, **kwargs)


class FileSrcManager(FileManager):
    """ source files manager """
    extensions = [".py", ".cpp", ".h"]
    excludes = ["tests", "templates"]

    def __init__(self, *args, **kwargs):
        FileManager.__init__(self, *args, **kwargs)


class FileDataManager(FileManager):
    """ data files manager """
    extensions = [".json", ".yaml", ".ngo", ".mtm"]
    includes = ["templates/*"]
    excludes = [".*", "dist", "build", "docs"]

    def __init__(self, *args, **kwargs):
        FileManager.__init__(self, *args, **kwargs)
        self.logger = logging.getLogger(__name__)


class FileTestManager(FileManager):
    """ test files manager """
    includes = ["test_*.py", "test_*.cpp"]
    extensions = [".py", ".cpp", ".h"]

    def __init__(self, *args, **kwargs):
        FileManager.__init__(self, *args, **kwargs)
