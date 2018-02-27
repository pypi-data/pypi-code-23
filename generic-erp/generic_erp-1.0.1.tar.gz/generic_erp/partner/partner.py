# -*- coding: utf-8 -*-


class Partner(object):
    """
    Contiene los datos de un partner
    :param vat: Vat(), documento del partner
    :param name: Nombre del partner
    """
    def __init__(self, name, vat):
        self.name = name
        self.vat = vat

    def validate_vat(self):
        self.vat.validate_number()
