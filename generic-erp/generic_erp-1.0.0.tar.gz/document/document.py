# - coding: utf-8 -*-
class Document(object):
    """
    Contiene la logica que deberia contener cualquier documento con importes: Facturas, Pagos, etc.
    """
    def __init__(self, partner):
        self.partner = partner
