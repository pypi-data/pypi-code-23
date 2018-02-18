# -*- coding: utf-8 -*-

"""
Realization of the RESTAPI for healthyhouse
"""
import requests

class Healthyhouse(object):
    '''
    This class implements the healthyhouse web restful api
    '''

    def __init__(self, token, server):
        self.rm_auth_headers = \
            {'Authorization': 'Token {}'.format(token)}
        self.server = server

    def set_results(self, results):
        """
        results dict should have structure like this:
        [
            {
               "id": 12120,
               "concentration": 45,
               "uncertainty": 23
            },
            {
               "id": 11495,
               "concentration": 78,
               "uncertainty": 6
            }
        ]
        """
        return requests.post(
                '{}/api/v1/dosimeters/set-results/'.format(self.server),
                headers = self.rm_auth_headers,
                json = results
        )

    def get_report(self, order_number):
        '''
        Retrieves a report.
        To access encoded content, look in response.text
        To access binary content (which could e.g. get dumped directly to a file) look in response.content
        '''
        return requests.get(
                '{}/api/v1/orders/generate_reports_pdf/?order_number={}'.format(self.server, order_number),
                headers = self.rm_auth_headers
        )

    def get_invoice(self, order_number):
        '''
        Retrieves an invoice.
        To access encoded content, look in response.text
        To access binary content (which could e.g. get dumped directly to a file) look in response.content
        '''
        return requests.get(
                '{server}/api/v1/orders/generate_invoices_pdf/?order_number={order_number}'.format(server = self.server, order_number = order_number),
                headers = self.rm_auth_headers
        )

    def import_order(
            self,
            country=None,          # String 'dk'
            currency=None,         # String 'DKK'
            date_placed=None,      # String (Y-%m-%d %H:%M)
            email=None,            # String
            first_name=None,       # String
            last_name=None,        # String
            line1=None,            # 'address'
            partner_code=None,     # 'partner_0001'
            partner_name=None,     # 'Bolius'
            partner_order_id=None, # '12345'
            phone_number=None,     # '+45123456' Remember country code
            postcode=None,         # '1234'
            product=None,          # 'integer, eg. 1' What is this?
            quantity=None,         # Integer
            serial_numbers=None,   # List of strings
            shipping_code=None,    # String
            shipping_excl_tax=None,# integer
            shipping_id=None,      # String
            shipping_incl_tax=None,# float
            shipping_method=None,  # What to use here?
            state=None,            # String
            status=None,           # String e.g. created or issued
            total_excl_tax=None,   # float
            total_incl_tax=None    # float
        ):
        '''
        Inserts an order into radonmeters system
        '''
        body = {k:v for k, v in locals().items() if v is not None and v is not self}
        return requests.post(
            '{}/api/v1/data-import/orders/'.format(self.server),
            headers=self.rm_auth_headers,
            data=body
        )
