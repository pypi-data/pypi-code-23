# -*- coding: utf-8 -*-

"""Console script for healthyhouse_api."""

import argparse
from marshmallow import Schema, fields, validates, ValidationError, pre_load
import os
import healthyhouse_api as hh_api
import pandas as pd
import collections
from itertools import chain

class Inputvalidation(Schema):
    '''
    Example usage of validator with filename validation excluded:
    data, errors = Job(exclude=('filename',)).load({'infile':'./somefile.csv','server':'https://xyz.com', 'token': '1234'})
    '''
    infile = fields.String( required = True)
    server = fields.String( required = True)
    token = fields.String( required = True)
    
    @validates('infile')
    def validate_filename(self, value):
        if not os.path.isfile(value):
            raise ValidationError('Supplied filename {} does not point to a fileresource'.format(value))

def main():

    desc = """
Import orders from csv file.
csv file should have the following structure:

country,currency,date_placed,email,first_name,last_name,line1,state,phone_number,postcode,serial_numbers
dk,DKK,2018-01-31 00:00,foobar@gmail.com,John,Doe,"Noway 4, st. mf.",København,"+4522345129",1874,12734;12730;12724
dk,DKK,2018-02-31 00:00,info@aasdert.com,Jan,Karlsen,"wayway 4,",Silkeborg,"+4512345678",8700,12744;12745;12746;12747
dk,DKK,2018-01-01 00:00,asdf@gmail.com,fname,name2,"hayway 4,",Horsens,"+4512345678",8700,22744;22745;22746
"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-i', '--infile',
                        help='csv file containing lab results to be ingested',
                        default="")
    parser.add_argument('-s', '--server',
                        help='URL for running instance of healthyhouse.',
                        default = None)
    parser.add_argument('-t', '--token',
                        help='Token for using the webservices',
                        default = None)
    
    
    data, errors = Inputvalidation().load(vars(parser.parse_args()))
    if errors:
        print(errors)
        return 1

    HH = hh_api.Healthyhouse(data['token'], server=data['server'])
    df = pd.read_csv(data['infile'],dtype={'phone_number':str})
    defaults = collections.OrderedDict(product='1')
    for row in df.itertuples(index=False):
        defaults.update(row._asdict())
        defaults['serial_numbers'] = [str(v) for v in defaults['serial_numbers'].split(';')]
        defaults['quantity'] = len(defaults['serial_numbers'])
        res = HH.import_order(**defaults)
        if res.status_code != 200:
            print('Error code: {}'.format(res.status_code) )
            print(res.text)
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
