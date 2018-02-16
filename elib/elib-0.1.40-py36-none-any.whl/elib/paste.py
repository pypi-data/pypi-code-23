# coding=utf-8
"""
Creates a snippet at glot.io for text sharing
"""

import json
import typing
from collections import namedtuple

import requests
from elib.custom_logging._custom_logging import get_elib_logger

LOGGER = get_elib_logger()

BASE_URL = 'https://snippets.glot.io/snippets'

PasteContent = namedtuple('PasteContent', 'filename content')


class PasteError(requests.HTTPError):
    """Raised on paste error"""
    pass


def create_new_paste(title, files: typing.List[PasteContent], public: bool = False, language='lua'):
    """
    Creates a paste on Glot

    :param title: name of the paste
    :param files: list of PasteContent
    :param public: whether or not paste is public
    :param language: syntax highlighting
    :return: URL of the newly created paste
    """
    headers = {
        'Content-type': 'application/json',
    }
    data = {
        'language': language,
        'title': title,
        'public': public,
        'files': [
            {
                'name': file.filename,
                'content': file.content
            } for file in files
        ],
    }
    req = requests.post(BASE_URL, json=data, headers=headers)
    if req.ok:
        resp = json.loads(req.text)
        url = resp['url'].replace('https://snippets.glot.io', 'https://glot.io')
        return url
    else:
        raise PasteError(f'failed to post content; reason: {req.reason}')
