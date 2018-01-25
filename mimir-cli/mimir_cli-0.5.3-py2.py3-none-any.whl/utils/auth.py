"""
authentication related helper functions
"""
import json
import os
import requests
from mimir_cli.utils.io import (
    mkdir
)
from mimir_cli.strings import (
    API_LOGIN_URL,
    MIMIR_DIR
)


def login_to_mimir(email, password):
    """logs into the platform api"""
    login_request = requests.post(
        API_LOGIN_URL,
        data={
            'email': email,
            'password': password
        }
    )
    data = json.loads(login_request.text)
    if data['success']:
        authentication_token = data['authToken']
        write_credentials(authentication_token)
    return data['success']


def logout_of_mimir():
    """logs out of mimir"""
    credentials_path = '{dir}.credentials'.format(dir=MIMIR_DIR)
    os.remove(credentials_path)
    return True


def read_credentials():
    """reads the user credentials from the mimir directory"""
    mkdir(MIMIR_DIR)
    credentials_path = '{dir}.credentials'.format(dir=MIMIR_DIR)
    if os.path.isfile(credentials_path):
        mimir_credentials_file = open(credentials_path, 'r')
        credentials = json.loads(mimir_credentials_file.read())
        mimir_credentials_file.close()
        return credentials
    return False


def write_credentials(auth_token):
    """writes the user credentials to the mimir directory"""
    mkdir(MIMIR_DIR)
    credentials_path = '{dir}.credentials'.format(dir=MIMIR_DIR)
    credentials = json.dumps({'authToken': auth_token})
    with open(credentials_path, 'w') as mimir_credentials_file:
        mimir_credentials_file.write(credentials)
