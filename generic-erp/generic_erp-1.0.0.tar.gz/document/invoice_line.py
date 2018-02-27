# -*- coding: utf-8 -*-


class InvoiceLine(object):

    def __init__(self, amount):
        self.amount = amount
        self.description = None
        self.tax = None
