__author__ = 'Nick'

import os
import json

def _get_dropbox_location(account_type='personal'):
    """
    Returns a string of the filepath of the Dropbox for this user

    :param account_type: str, 'business' or 'personal'
    """
    info_path = _get_dropbox_info_path()
    info_dict = _get_dictionary_from_path_to_json(info_path)
    return _get_dropbox_path_from_dictionary(info_dict, account_type)

def _get_dropbox_info_path():
    """
    Returns filepath of Dropbox file info.json
    """
    path = _create_dropbox_info_path('APPDATA')
    if path:
        return path
    return _create_dropbox_info_path('LOCALAPPDATA')

def _create_dropbox_info_path(appdata_str):
    r"""
    Looks up the environment variable given by appdata_str and combines with \Dropbox\info.json

    Then checks if the info.json exists at that path, and if so returns the filepath, otherwise
    returns False
    """
    path = os.path.join(os.environ[appdata_str], r'Dropbox\info.json')
    if os.path.exists(path):
        return path
    return False

def _get_dictionary_from_path_to_json(info_path):
    """
    Loads a json file and returns as a dictionary
    """
    with open(info_path, 'r') as f:
        text = f.read()

    return json.loads(text)

def _get_dropbox_path_from_dictionary(info_dict, account_type):
    """
    Returns the 'path' value under the account_type dictionary within the main dictionary
    """
    return info_dict[account_type]['path']


filepath = _get_dropbox_location()

if __name__ == '__main__':
    print(filepath)