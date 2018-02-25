#!/usr/bin/python3
# -*- encoding: utf-8 -*-
"""
Voor gebruik van de webservice is aparte autorisatie vereist. 
Deze autorisatie wordt verleend na ontvangst van een getekend contract. 
Dit contract is op te vragen via nsr.api@ns.nl.
"""

import requests
import sys
import time
import os
import logging
import xmltodict

from .trains import Trains

class prijzen(Trains):
    """
        class for fetching and parsing NS train pricing data
    """

    def getData(self, fromST=None, toST=None, viaST="", dateTime=""):
        try:
            if fromST is None or toST is None:
                raise Exception("You must provide a From and To station")    
            
            #fetch the elements from the NS API
            url = "http://webservices.ns.nl/ns-api-prijzen-v3?from={}&to={}&via={}&dateTime={}".format(fromST,toST,viaST,dateTime)

            root = self.goFetch(url)
            
            return xmltodict.parse(root, dict_constructor=dict)
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) + " | " + str(fname) + " | " + str(exc_tb.tb_lineno))  