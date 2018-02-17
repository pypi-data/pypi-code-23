# -*- coding: utf-8 -*-

"""Console script for healthyhouse_api."""

import argparse
from marshmallow import Schema, fields, validates, ValidationError, pre_load
import os
import healthyhouse_api as hh_api
import pandas as pd

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
Import lab results from csv file.
csv file should have the following structure:

id,concentration,uncertainty
12120,42,22
11495,43,13
11620,44,14
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
    
    
    data = Inputvalidation().load(vars(parser.parse_args()))
    
    HH = hh_api.Healthyhouse(data['token'], server=data['server'])
    df = pd.read_csv(data['infile'])
    dct = df.to_dict(orient='records')
    print('Inserting {count} rows...'.format(count=len(df)))
    res = HH.set_results(
        [{k: int(v) for k, v in d.items()} for d in dct]
    )
    if res.status_code != 200:
        print('Error code: {}'.format(res.status_code) )
        print(res.text)
    else:
        print('Done')
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
