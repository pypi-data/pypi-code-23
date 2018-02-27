# -*- coding: utf-8 -*-
from abc import ABCMeta


class Vat:

    __metaclass__ = ABCMeta

    def __init__(self, number, vat_type):
        self.number = number
        self.vat_type = vat_type

    @staticmethod
    def validate_number():
        raise NotImplemented("Funcion no implementada para este tipo de documento")
