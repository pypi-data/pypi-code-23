import json
import sys
from urllib.parse import urljoin

import click
import requests
from requests.exceptions import ConnectionError

from cassiny import config


def make_request(
    url,
    method,
    params=None,
    headers=None,
    data=None,
    token=True,
    files=None
):
    """Make a request to Cassiny.io."""
    url = urljoin(config.BASE_URI, url)

    request_headers = {}

    if data:
        request_headers['content-type'] = 'application/json'
        data = json.dumps(data)

    if files:
        data = files

    if headers:
        request_headers.update(headers)

    if token is True:
        request_headers['Authorization'] = 'Bearer {}'.format(get_token())

    try:
        response = requests.request(
            method,
            url,
            params=params,
            headers=request_headers,
            data=data
        )
    except ConnectionError as e:
        print("Impossible to connect!")
        raise
    else:
        if response.ok:
            return response
        else:
            try:
                print(response.json()['error'])
                sys.exit(1)
            except json.JSONDecodeError:
                print("😞....something went really bad!")
                sys.exit(1)


def get_token():
    """Get the token."""
    try:
        with open(config.FOLDER, 'rb') as f:
            data = json.loads(f.read())
            return data['token']
    except (KeyError, FileNotFoundError):
        click.secho(
            "You need to call `cassiny login` before running this command.", fg='red', bold=True)
        sys.exit(1)


def save_token(payload):
    """Save the token."""
    token = payload['token']
    with open(config.FOLDER, 'wb') as f:
        f.write(json.dumps({"token": token}).encode('utf-8'))
