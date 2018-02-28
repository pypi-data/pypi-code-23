# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 11:06:57 2012

@author: cedric
"""
from __future__ import unicode_literals

import logging
from builtins import object
from builtins import str

from ngomodel import ClassWithSchema
from ngomodel import ObjectManager


class Person(ClassWithSchema):
    schemaPath = "schemas/Person.json"


class PersonManager(ObjectManager):
    schemaPath = "schemas/PersonManager.json"
    extensions = ['.ngopl']

    def __init__(self, *args, **kwargs):
        ObjectManager.__init__(self, Person, *args, **kwargs)
        self.logger = logging.getLogger(__name__)
