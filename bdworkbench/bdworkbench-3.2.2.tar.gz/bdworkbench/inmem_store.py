#!/usr/bin/env python
#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function

from collections import OrderedDict
from utils import isDebug

ENTRY_DICT = 'entrydict'
DELIVERABLE_DICT = 'deliverableDict'
SIMPLESETUP_DICT = 'simeplsetupdict'

DEFAULT_DELIVERABLE_DICT = {}
DEFAULT_SIMPLESETUP_DICT = {
                            "autogen": {
                                    'name'   : '',
                                    'package': '',
                                    'configapi': '',
                                    'append' : OrderedDict(),
                                    'execute': [],
                                    'replace': [],
                                    'addfile': OrderedDict(),
                                    'perms'  : OrderedDict(),
                                    'services': OrderedDict(),
                                    'sourcefiles': []
                                }
                            }
DEFAULT_ENTRY_DICT = {
                        "services": [{
                                      "id": "ssh",
                                      "label": { "name": "SSH" },
                                      "endpoint" : {
                                        "port" : "22",
                                        "is_dashboard" : False
                                      }
                                }]
                     }

class InmemStore(object):
    """
    """

    def __init__(self):
        """
        """
        self.inmem = self._default_inmem()

    def _default_inmem(self):
        return {
                ENTRY_DICT       : DEFAULT_ENTRY_DICT,
                DELIVERABLE_DICT : DEFAULT_DELIVERABLE_DICT,
                SIMPLESETUP_DICT : DEFAULT_SIMPLESETUP_DICT
               }

    def clear(self, opDict="ALL"):
        """

        """
        if opDict == "ALL":
            self.inmem = self._default_inmem()
        elif opDict == ENTRY_DICT:
            self.inmem[opDict] = DEFAULT_ENTRY_DICT
        elif opDict == SIMPLESETUP_DICT:
            self.inmem[opDict] = DEFAULT_SIMPLESETUP_DICT
        elif opDict == DELIVERABLE_DICT:
            self.inmem[opDict] = DEFAULT_DELIVERABLE_DICT

        if isDebug():
            print("DEBUG: INMEM CLEAR -", opDict)

    def getDict(self, opDict):
        """

        """
        return self.inmem[opDict]

    def setDict(self, opDict, value):
        """

        """
        self.inmem[opDict] = value
        if isDebug():
            print("DEBUG: INMEM SET - OP: %s VAL: %s" % (opDict, self.inmem[opDict]))

    def addField(self, opDict, key, value):
        """
        Adds the {key, value} pair to 'opDict' replacing any previous definition.
        """
        self.inmem[opDict][key] = value
        if isDebug():
            print("DEBUG: INMEM ADD - OP: %s KEY: %s VAL: %s" %
                        (opDict, key, self.inmem[opDict][key]))

    def appendValue(self, opDict, key, value):
        """
        Appends the new value to an already existing key in 'opDict'. If the key
        doesn't exist, a new key is added with its value as the list containing the
        input value as the single element.
        """
        if self.inmem[opDict].has_key(key):
            values = self.inmem[opDict][key]
            if value not in values:
                self.inmem[opDict][key].append(value)
        else:
            self.addField(opDict, key, [value])

        if isDebug():
            print("DEBUG: INMEM APPEND - OP: %s KEY: %s VAL: %s" %
                        (opDict, key, self.inmem[opDict][key]))
