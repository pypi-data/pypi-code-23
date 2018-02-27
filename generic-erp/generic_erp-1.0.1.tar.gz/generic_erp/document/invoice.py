# -*- coding: utf-8 -*-
from generic_erp.document.document import Document
INVOICE_TYPES = [
    'invoice',
    'refund',
    'debit_note'
]


class Invoice(Document):

    def __init__(self, partner, invoice_type):
        super(Invoice, self).__init__(partner)
        self.date = None
        self.taxed_amount = None
        self.untaxed_amount = None
        self.exempt_amount = None
        self.invoice_lines = []
        self._invoice_type = invoice_type

    def get_total_amount(self):
        """ Devuelve el total de la factura basandose en los otros importes """
        try:
            total_amount = self.taxed_amount + self.untaxed_amount + self.exempt_amount

        except TypeError:
            raise AttributeError("Falta especificar algun importe en la factura")

        return total_amount

    @property
    def invoice_type(self):
        return self._invoice_type

    @invoice_type.setter
    def invoice_type(self, value):
        if value not in INVOICE_TYPES:
            raise AttributeError("El tipo de comprobante no es valido")
