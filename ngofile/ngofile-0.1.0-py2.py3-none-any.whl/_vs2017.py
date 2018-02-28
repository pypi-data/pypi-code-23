# *- coding: utf-8 -*-
""" utilities, prototypes and classes of serializers

_schemas.py - created on 02/01/2018
author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import unicode_literals

import logging
import uuid
from builtins import object
from builtins import str
from xml.etree import ElementTree as ET

from ngomodel import Parser
from ngomodel import register_parser
from ngomodel import register_serializer
from ngomodel import root_namespace
from ngomodel import take_arrays
from ngomodel._jinja2 import Jinja2Serializer


@register_parser
class Vs2017Parser(Parser):
    id = 'vs2017'
    objectClass = "ngoproject._project.NgoProject"
    extensions = ['.pyproj']

    def __init__(self, *args, **kwargs):
        Parser.__init__(self, *args, **kwargs)
        self.logger = logging.getLogger(__name__)

    @take_arrays(1)
    def loads(self, stream, **kwargs):
        from ._project import Project
        from ._environment import PythonEnvironment
        root = ET.parse(stream)
        nsmap = root_namespace(root)[1:-1]
        guid = root.find('.//{%s}ProjectGuid' % nsmap).text
        startupfile = root.find('.//{%s}StartupFile' % nsmap).text
        currentInterpreter = root.find(
            './/{%s}InterpreterId' % nsmap).text.split('|')[1]

        prj = Project(vsGuid=guid)
        pythonEnvs = {}
        for n in root.findall('.//{%s}Interpreter' % nsmap):
            id = n.find('{%s}Id' % nsmap).text
            description = n.find('{%s}Description' % nsmap).text
            path = n.find('{%s}InterpreterPath' % nsmap).text
            version = n.find('{%s}Version' % nsmap).text
            archi = n.find('{%s}Architecture' % nsmap).text
            pathEnvironmentVariable = n.find(
                '{%s}PathEnvironmentVariable' % nsmap).text
            pythonEnvs[Id] = PythonEnvironment(
                path=path,
                name=Id,
                description=description,
                version=version,
                archi=archi)
        prj.pythonEnvs = pythonEnvs
        return prj


@register_serializer
class Vs2017Serializer(Jinja2Serializer):
    id = 'vs2017'
    objectClass = "ngoproject._project.NgoProject"
    extensions = ['.pyproj']
    template = "file.pyproj"

    def __init__(self, *args, **kwargs):
        Jinja2Serializer.__init__(self, self.template, *args, **kwargs)
        self.logger = logging.getLogger(__name__)

    @take_arrays(1)
    def dumps(self, data, **kwargs):
        incs = data['fileDataManager'].list_files()
        srcs = data['fileSrcManager'].list_files(
        ) + data['fileTestManager'].list_files()
        dirs = set([p.parent for p in srcs + incs])
        data.update({'incs': incs, 'srcs': srcs, 'dirs': dirs})
        if 'vsGuid' not in data:
            data['vsGuid'] = uuid.uuid1()
        return Jinja2Serializer.dumps(self, data, **kwargs)
