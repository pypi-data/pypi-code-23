# Copyright 2017 Interana, Inc.
import os
from stat import S_IREAD, S_IWRITE

import json
from os.path import expanduser

RC_FILE = expanduser("~") + '/.interanarc'


def get_config():

    rcconfig = {}

    try:
        with open(RC_FILE, 'r') as f:
            rcconfig = json.load(f)
    except:
        pass

    return rcconfig


def get_credentials(instance):

    try:
        rcconfig = get_config()[instance]
    except:
        if not os.getenv('INTERANA_HOSTNAME') and os.getenv('INTERANA_API_TOKEN'):
            raise Exception("No such instance!")

    config = {}
    config['hostname'] = os.getenv('INTERANA_HOSTNAME') or rcconfig.get('hostname')
    config['api_token'] = os.getenv('INTERANA_API_TOKEN') or rcconfig.get('api_token')

    cust_id = os.getenv('INTERANA_CUSTOMER_ID') or rcconfig.get('customer_id')
    if cust_id:
        config['customer_id'] = cust_id

    return config


def write_rcconfig(hostname, api_token, instance, customer_id=None):
    '''
    customer_id should be included only for service accounts.
    '''
    config = get_config()
    config[instance] = {}
    config[instance]['hostname'] = hostname
    config[instance]['api_token'] = api_token
    if customer_id:
        config[instance]['customer_id'] = customer_id

    if os.path.exists(RC_FILE):
        os.chmod(RC_FILE, S_IREAD | S_IWRITE)

    with open(RC_FILE, 'w') as f:
        json.dump(config, f, indent=4)

    os.chmod(RC_FILE, S_IREAD)
