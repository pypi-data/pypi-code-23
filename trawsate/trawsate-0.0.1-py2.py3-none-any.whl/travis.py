# -*- coding: utf-8 -*-
from typing import Any, List, Dict, Tuple, Optional
import logging
import urllib.parse
import requests

AccessKeyPair = Any

_BASE = 'https://api.travis-ci.org'

logger = logging.getLogger(__name__)


class TravisError(Exception):
    """
    Represents any error received from Travis (not connection or timeout
    errors).
    """

    def __init__(self, response: requests.Response):
        """
        Initialise a new error.

        :param response: The response received from Travis.
        """
        self._response = response

    def __str__(self) -> str:
        return f'{self.__class__.__name__}({self._response.status_code})'


def create_session(token: str) -> requests.Session:
    """
    Initialise a new context for interacting with the Travis API.

    :param token: The access token to authorise requests with.
    :return: The created requests session.
    """
    session = requests.session()
    session.headers.update({
        'Travis-API-Version': '3',  # requests complains if not str
        'Authorization': f'token {token}'
    })
    return session


def update_env_var(session: requests.Session, current: Dict, value: str) \
        -> None:
    """
    Change the value of an existing environment variable.

    :param session: The session to use to interact with the Travis API.
    :param current: The current variable's dict, retrieved from the env_var
                    endpoint.
    :param value: The new value to assign.
    :raises TravisError: If the variable could not be updated.
    """
    endpoint = f"{_BASE}{current['@href']}"
    response = session.patch(endpoint, json={
        'env_var.value': value
    })
    if not response.ok:
        raise TravisError(response)


def create_env_var(session: requests.Session, slug: str, name: str,
                   value: str, public: bool = False) -> None:
    """
    Add a new environment variable.

    :param session: The session to use to interact with the Travis API.
    :param slug: The "<username>/<repo_name>" of the GitHub repository in
                 Travis.
    :param name: The name of the environment variable.
    :param value: The value to assign.
    :param public: Whether the value should be public; defaults to false.
    :raises TravisError: If the variable could not be created.
    """
    endpoint = f'{_BASE}/repo/{urllib.parse.quote_plus(slug)}/env_vars'
    response = session.post(endpoint, json={
        'env_var.name': name,
        'env_var.value': value,
        'env_var.public': public
    })
    if not response.ok:
        raise TravisError(response)


def _find_aws_access_key_variables(env_vars: List[Dict]) \
        -> Tuple[Optional[Dict], Optional[Dict]]:
    """
    Scans for AWS credentials in Travis environment variables.

    :param env_vars: A list of environment variables for a repository.
    :return: A pair containing the access key and secret respectively. If a
             value is not found, its corresponding element will be set to None.
    """
    id_ = None
    secret = None
    for var in env_vars:
        if var['name'] == 'AWS_ACCESS_KEY_ID':
            id_ = var
        elif var['name'] == 'AWS_SECRET_ACCESS_KEY':
            secret = var

        if id_ is not None and secret is not None:
            return id_, secret

    return id_, secret


def update_access_key(repo_slug: str, access_key: AccessKeyPair,
                      session: requests.Session) -> None:
    """
    Set a repository's environment variables to use a particular AWS access
    key pair.

    :param repo_slug: The "<username>/<repo_name>" of the GitHub repository in
                      Travis.
    :param access_key: The AWS access key pair to user.
    :param session: The session, created with `create_session()`, to use to
                    interact with the Travis API.
    :raises TravisError: If a request fails. The repository may be left in an
                         inconsistent state (e.g. with the ID updated but not
                         the secret).
    """

    def set_var(name: str, value: str, current: Optional[Dict]) -> None:
        if current is None:
            create_env_var(session, repo_slug, name, value)
        else:
            update_env_var(session, current, value)

    response = session.get(f'{_BASE}/repo/{urllib.parse.quote_plus(repo_slug)}'
                           f'/env_vars')
    if not response.ok:
        raise TravisError(response)
    id_, secret = _find_aws_access_key_variables(response.json()['env_vars'])

    set_var('AWS_ACCESS_KEY_ID', access_key.id, id_)
    set_var('AWS_SECRET_ACCESS_KEY', access_key.secret, secret)
