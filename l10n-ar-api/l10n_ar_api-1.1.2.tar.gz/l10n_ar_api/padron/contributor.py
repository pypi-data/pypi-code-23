# -*- coding: utf-8 -*-
import config
import json
import urllib2

class Contributor:
    
    def __init__(self):
        self.name = None
        self.document_type = None
        self.document_number = None
        self.street = None
        self.postal_code = None
        self.city = None
        self.state_code = None
        
    
    def set_partner_data(self, document_number=None):
        """ 
        Completa los datos del contribuyente con los datos del API Rest de AFIP
        :param document_number: Numero de documento con el cual se consultara
        """
        
        if document_number: self.document_number = document_number 
        
        if self.document_number:
            data = self.get_partner_data(self.document_number).get('data')
            fiscal_location = None
            
            if data:

                self.name = data.get('nombre')
                fiscal_location = data.get('domicilioFiscal')
            
            if fiscal_location:
                self.postal_code = fiscal_location.get('codPostal')      
                self.city = fiscal_location.get('localidad')
                self.street = fiscal_location.get('direccion')           
                self.state_code = fiscal_location.get('idProvincia')
        
    @classmethod
    def is_valid_cuit(cls, cuit):
        """
        :param cuit: Cuit a validar
        :return: Falso si no es valido
        """
        
        try:
            int(cuit)
        except ValueError:
            return False
        
        cuit = str(cuit)
        
        if len(cuit) != 11:
            return False
        
        l=[5,4,3,2,7,6,5,4,3,2]

        var1=0
        for i in range(10):
            var1=var1+int(cuit[i])*l[i]
        var3=11-var1%11

        if var3==11: var3=0
        if var3==10: var3=9
        if var3 == int(cuit[10]):

            return True

        return False
    
    @classmethod
    def get_partner_data(cls, document_number, url=None):
        """
        Obtiene los datos del API Rest de AFIP
        :param document_number: Cuit a consultar
        :param url: Url de donde se realizara la consulta
        :raises: ValueError si la url es invalida o no se puede obtener un JSON.
        :returns: JSON con la respuesta para ese contribuyente.
        """
        
        url = url+str(document_number) if url else config.URL_PADRON+str(document_number)
        try:
            res = json.load(urllib2.urlopen(url))
        except ValueError:
            raise
        
        return res
        
        