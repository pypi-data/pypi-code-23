# -*- coding: utf-8 -*-

class Validator(object):
    @staticmethod
    def validate_non_none(arg):
        if arg is None:
            raise ValueError()

    @staticmethod
    def validate_path(path):
        if path[0] is not '/':
            raise Exception('All the paths should start with "/"')