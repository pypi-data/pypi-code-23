# -*- coding: utf8 -*-
import base64
import hashlib
import json
import logging
import os
import random
import socket
import sys

import click
import requests
from pandas.io.json import json_normalize
from requests import HTTPError
from terminaltables import PorcelainTable
from six.moves.urllib import parse
from .utilities.tables import format_json_data, dict_to_csv


def print_as_json(result):
    click.echo(json.dumps(result))


def print_as_bad_json(result):
    click.echo(result)


def create_validate_length(min_length, max_length):
    def validate_length(ctx, option, value):
        if value is None:
            return value

        if len(value) > max_length:
            raise click.BadParameter("needs to be shorter than %s characters" % max_length)

        if len(value) < min_length:
            raise click.BadParameter("needs to be longer than %s characters" % min_length)

        return value

    return validate_length


def build_auth0_url(auth0):
    return '{}.auth0.com'.format(auth0)


def add_to_data_if_not_none(data, val, key):
    if val is not None:
        data[key] = val


def get_data_and_remove(kwargs, key):
    key = key.lower()
    result = kwargs.get(key)

    if key in kwargs:
        del kwargs[key]

    return result


def base64url(b):
    return bytearray(base64.b64encode(b).decode('ascii').replace('=', '').replace('+', '-').replace('/', '_'), 'ascii')


def sha256(s):
    h = hashlib.sha256()
    h.update(s)
    return h.digest()


def urljoin(*args):
    base = args[0]
    for u in args[1:]:
        base = parse.urljoin(base, u)

    return base


class LocalWebServer(object):
    ports = [27017, 41589, 55130, 6617, 1566, 17404, 44288, 6948, 15950, 48216, 3318, 34449, 22082, 22845, 37862, 59304]

    def __init__(self):
        self.app = self.create_app()
        self.code = None
        self.srv = None

        self.disable_logging()
        self.start_server()

    def close(self):
        if self.srv is not None:
            self.srv.server_close()

    @classmethod
    def disable_logging(cls):
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

    def create_app(self):
        from flask import Flask, request, redirect
        app = Flask(__name__)

        @app.route('/console/auth/init')
        def auth_init():
            self.code = request.args.get('code')
            return redirect("/console/auth/finish")

        @app.route('/console/auth/finish')
        def auth_finish():
            self.srv.shutdown_signal = True
            return "You can go now back to the console"

        return app

    def run(self):
        self.srv.serve_forever()

    @property
    def redirect_uri(self):
        return 'http://localhost:%s/console/auth/init' % self.srv.port

    def start_server(self):
        from werkzeug.serving import make_server

        ports = self.ports[:]
        random.shuffle(ports)

        for port in ports:
            try:
                self.srv = make_server('127.0.0.1', port, self.app)
                break
            except (OSError, socket.error):
                continue

        if self.srv is None:
            click.echo("can't create local server for authentication, consider using the --disable-webserver flag")


def wait_for_input():
    if sys.version_info >= (3, 0):
        code = input('Enter the token ')
    else:
        # noinspection PyUnresolvedReferences
        code = raw_input('Enter the token ')

    return code


def auth0_oauth_token(auth0_url, code, verifier, client_id, redirect_uri):
    params = {
        'code': code,
        'code_verifier': verifier,
        'client_id': client_id,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }

    r = requests.post('https://{}/oauth/token'.format(auth0_url), json=params)

    r.raise_for_status()

    return r.json()


# noinspection PyUnusedLocal
def pixy_flow(ctx):
    import webbrowser

    verifier = base64url(os.urandom(32))
    verifier_challenge = base64url(sha256(verifier))
    verifier_challenge = verifier_challenge.decode('ascii')

    verifier = verifier.decode('ascii')

    def get_authorize_url():
        host = ctx.host if 'missinglink.ai' in ctx.host else '{host}.firebaseapp.com'.format(host=ctx.host)

        current_redirect_uri = app.redirect_uri if ctx.local_web_server else '{host}/console/auth/init'.format(
            host=host)

        query = {
            'response_type': 'code',
            'scope': 'openid offline_access user_external_id org orgs email picture name given_name user_metadata',
            'client_id': ctx.client_id,
            'redirect_uri': current_redirect_uri,
            'code_challenge': verifier_challenge,
            'code_challenge_method': 'S256'
        }

        return 'https://{}/authorize?{}'.format(build_auth0_url(ctx.auth0), parse.urlencode(query)), current_redirect_uri

    app = LocalWebServer() if ctx.local_web_server else None

    authorize_url, redirect_uri = get_authorize_url()

    if ctx.local_web_server and not webbrowser.open(authorize_url):
        app.close()
        ctx.local_web_server = False
        authorize_url, redirect_uri = get_authorize_url()

    if ctx.local_web_server:
        msg = "If the browser doesn't open enter this URL manually\n{authorize_url}\n"
    else:
        msg = "Enter the following URL in your machine browser\n{authorize_url}\n"

    click.echo(msg.format(authorize_url=authorize_url))

    if ctx.local_web_server:
        app.run()
        code = app.code
    else:
        code = wait_for_input()

    try:
        data = auth0_oauth_token(build_auth0_url(ctx.auth0), code, verifier, ctx.client_id, redirect_uri)
    except HTTPError:
        click.echo("Failed to init authorized (did you enter the current token?).", err=True)
        exit(1)
        return

    click.echo("Success!, you sre authorized to use the command line.")

    return data['access_token'], data['refresh_token'], data['id_token']


def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def output_result(ctx, result, fields=None, formatters=None, write_row_index=False):
    if result is None:
        return

    format_tables = ctx.obj.output_format == 'tables'
    format_csv = ctx.obj.output_format == 'csv'

    result = format_json_data(result, formatters)

    def normal_name(name):
        return name.replace('_', ' ').title()

    if format_csv:
        df = json_normalize(result)
        df = df.rename(normal_name, axis='columns')

        df.to_csv(sys.stdout, columns=map(normal_name, fields), index=write_row_index)
    elif format_tables:
        table_data = list(dict_to_csv(result, fields))

        click.echo(PorcelainTable(table_data).table)
    elif hasattr(ctx.obj, 'bad_json_format'):
        print_as_bad_json(result)
    else:
        print_as_json(result)
