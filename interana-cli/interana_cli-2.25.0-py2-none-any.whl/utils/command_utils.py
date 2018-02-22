# Copyright 2017 Interana, Inc.
'''
Utility functions to be used by commands
'''

import argparse
import ast
import datetime
import json
import os

# Completer uses API to get latest version. Using this to show examples in help
DATA_SOURCE_TYPES = ['aws', 'azure_blob', 'file_system', 'kafka', 'http_listener', 'remote_fs']

PIPELINE_LIST_COLUMNS = [
    (lambda r: r['pipeline_id'], 'ID'),
    (lambda r: r['name'], 'Name'),
    (lambda r: r['table_name'], 'Table'),
    (lambda r: r['data_source_type'], 'Data Source'),
    (lambda r: r['data_source_parameters']['file_pattern'] if 'file_pattern' in r['data_source_parameters'] else '',
     'File Pattern'),
]


def IngestInputDate(v):
    '''
    Custom argparse type for date input validation for pipeline and job commands
    '''
    # Continuous jobs may have start date values as integers
    try:
        int_v = int(v)
        if int_v < 1:
            raise argparse.ArgumentTypeError('Start day integer value must be greater than zero')
        return v
    except ValueError:
        pass
    if v in ['today', 'tomorrow', 'yesterday']:
        return v
    # return empty if false, parsed date if true
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S'):
        try:
            datetime.datetime.strptime(v, fmt)
            return v
        except:
            pass
    raise argparse.ArgumentTypeError("Date must be 'today', 'tomorrow', "
                                     "'yesterday' or of format '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S'")


def parse_ingest_input_date(ingest_input_date):
    '''
    Translates valid IngestInputDate formats to a datetime object. Returns None if date could not
    be parsed.
    '''
    parsed_date = None
    # Non date string cases
    if ingest_input_date.isdigit():
        parsed_date = datetime.date.today() - datetime.timedelta(days=int(ingest_input_date))
    elif ingest_input_date.lower() == 'today':
        parsed_date = datetime.date.today()
    elif ingest_input_date.lower() == 'yesterday':
        parsed_date = datetime.date.today() - datetime.timedelta(days=1)
    elif ingest_input_date.lower() == 'tomorrow':
        parsed_date = datetime.date.today() + datetime.timedelta(days=1)
    # Date strings
    if not parsed_date:
        for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S'):
            try:
                parsed_date = datetime.datetime.strptime(ingest_input_date, fmt)
                break
            except:
                pass

    return parsed_date


def print_example_config(command_name, example_config):
    print '-------- Sample {} Config --------\n'.format(command_name)
    print example_config


def user_confirm(question, default=False):
    '''
    Prompt user for confirmation. Returns True if user enters 'y' for yes, and False if user enters
    'n'. Can set default value, when user hits enter without entering any input. This default value
    has a default of 'n'
    '''
    user_confirmed = False
    while True:
        resp = raw_input(question).strip()
        if resp.lower() == 'y':
            user_confirmed = True
            break
        elif resp.lower() == 'n':
            break
        elif resp.lower() == '':
            user_confirmed = default
            break
        else:
            print "Invalid response. Please try again."
    return user_confirmed


def parse_config_file(config_file_path):
    '''
    Given a path to a config file, parse the config file or raise an Exception
    '''
    if not os.path.isfile(config_file_path):
        raise Exception('"{}" is not a file'.format(config_file_path))
    parsed_config = None
    with open(config_file_path, 'rb') as config_fh:
        config_text = config_fh.read()
        try:
            parsed_config = ast.literal_eval(config_text)
        except ValueError:
            try:
                parsed_config = json.loads(config_text)
            except ValueError:
                raise Exception('Could not load configuration from file.')
    return parsed_config
