import os

import click

from .. import config as c
from ..utils import make_request, save_token


@click.command('login', short_help='login with cassiny.io')
def login():
    """
    Login user.

    Save the token inside `~/.cassiny`
    """
    click.secho("Enter your Cassiny.io credentials", bold=True)

    email = click.prompt('Email')
    password = click.prompt('Password', hide_input=True)

    data = {"email": email, "password": password}

    response = make_request(
        '/auth/login', method='POST', data=data, token=False
    )

    save_token(response.headers)
    click.secho("Logged in :)", fg='green', bold=True)


@click.command('logout', short_help='Logout from Cassiny.io')
def logout():
    """Logout and remove the token."""
    if os.path.exists(c.FOLDER):
        with open(c.FOLDER, 'wb') as f:
            f.write(b"{}")
    click.secho("Logged out :)", fg='green', bold=True)
