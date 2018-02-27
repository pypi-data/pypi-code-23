# -*- coding: utf-8 -*-


class Tax(object):

    def __init__(self, amount):
        self.amount = amount
        self.taxable_base = None
        self.aliquot = None
