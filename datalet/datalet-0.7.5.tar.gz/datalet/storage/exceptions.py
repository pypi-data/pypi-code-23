#!/usr/bin/env python
# -*- coding: utf-8  -*-

class StorageExistsError(Exception):

	def __init__(self, location):
		self.location = location


class StorageNotFoundError(Exception):

	def __init__(self, location):
		self.location = location



class UnmatchExtensionError(Exception):
    
    def __init__(self, location):
        self.location = location


class ForeignRelationExistsError(Exception):

    def __init__(self, location):
        self.location = location


class ArgumentsAbsenceError(Exception):

	def __init__(self, message):
		self.message = message