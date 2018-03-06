import os

import click

from .. import config as c
from ..utils import make_request, save_token


@click.command('signup', short_help='Signup with cassiny.io')
def signup():
    """
    Signup user.

    Save the token inside `~/.cassiny`
    """
    click.secho("Register your Cassiny.io credentials", bold=True)

    email = click.prompt('Your email')
    password = click.prompt('Your password', hide_input=True)
    first_name = click.prompt('Your name')
    last_name = click.prompt('Your surname')

    data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name
    }

    make_request('/api/auth/signup', method='POST', data=data, token=False)

    click.secho("Thanks for sign-up!", fg='green', bold=True)


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
        '/api/auth/login', method='POST', data=data, token=False
    )
    save_token(response.json())
    click.secho("Logged in :)", fg='green', bold=True)


@click.command('logout', short_help='logout from Cassiny.io')
def logout():
    """Logout and remove the token."""
    if os.path.exists(c.FOLDER):
        with open(c.FOLDER, 'wb') as f:
            f.write(b"{}")
    click.secho("Logged out :)", fg='green', bold=True)
