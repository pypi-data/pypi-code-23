# -*- coding: utf8 -*-
import logging

import requests
from requests import HTTPError
from six.moves.urllib import parse

from .eprint import eprint
from .config import get_prefix_section, Config

BASE_URL_PATH = '_ah/api/missinglink/v1/'


def __urljoin(*args):
    base = args[0]
    for u in args[1:]:
        base = parse.urljoin(base, u)

    return base


def __api_call(config, url, http_method, data):
    id_token = config.id_token

    for _ in range(3):
        headers = {'Authorization': 'Bearer {}'.format(id_token)}
        r = http_method(url, headers=headers, json=data)

        if r.status_code == 401:
            try:
                id_token = update_token(config)
                continue
            except HTTPError:
                eprint('Authorization failed, try running "mali auth init" again')
                exit(1)

        r.raise_for_status()

        return r.json()

    eprint('failed to refresh the token, rerun auth init again')
    exit(1)


# noinspection PyUnusedLocal
def handle_api(ctx_or_config, http_method, method_url, data=None, retry=None):
    config = ctx_or_config if isinstance(ctx_or_config, Config) else ctx_or_config.config

    if config.id_token is None:
        eprint('Please run: "mali auth init" to setup authorization')
        exit(1)

    url = __urljoin(config.api_host, BASE_URL_PATH, method_url)

    def api_call_with_retry(current_config, current_url, current_http_method, current_data):
        return retry.call(__api_call, current_config, current_url, current_http_method, current_data)

    f = __api_call if retry is None else api_call_with_retry

    try:
        return f(config, url, http_method, data)
    except requests.exceptions.HTTPError as ex:
        try:
            error_message = ex.response.json().get('error', {}).get('message')
        except ValueError:
            error_message = None

        if error_message is None:
            error_message = str(ex)

        eprint('\n' + error_message)
        exit(1)


def build_auth0_url(auth0):
    return '{}.auth0.com'.format(auth0)


def _should_retry_auth0(exception):
    logging.debug('got retry exception (auth0) %s', exception)

    error_codes_to_retries = [
        429,  # Too many requests
    ]

    return isinstance(exception, requests.exceptions.HTTPError) and exception.response.status_code in error_codes_to_retries


def update_token(config):
    from retrying import retry

    @retry(retry_on_exception=_should_retry_auth0)
    def with_retry():
        r = requests.post('https://{}/delegation'.format(build_auth0_url(config.auth0)), json={
            'client_id': config.client_id,
            'grant_type': "urn:ietf:params:oauth:grant-type:jwt-bearer",
            'scope': 'openid offline_access user_external_id org orgs email picture name given_name user_metadata',
            'refresh_token': config.refresh_token,
        })

        r.raise_for_status()

        data = r.json()

        config.set(get_prefix_section(config.config_prefix, 'token'), 'id_token', data['id_token'])
        config.save()

        return data['id_token']

    return with_retry()


def default_api_retry(stop_max_attempt_number=None):
    from retrying import Retrying

    def retry_if_retry_possible_error(exception):
        logging.debug('got retry exception (api) %s', exception)

        return True

    return Retrying(
        retry_on_exception=retry_if_retry_possible_error,
        wait_exponential_multiplier=50,
        wait_exponential_max=5000,
        stop_max_attempt_number=stop_max_attempt_number)
