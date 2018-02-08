# -*- coding: utf-8 -*-
import json
import os.path
from typing import List

import click
from logzero import logger
import requests

from chaosiq import __version__
from chaosiq.config import initialize_config, load_config, \
    CHAOISQ_CONFIG_PATH, get_token, save_config, set_token, set_config_key
from chaosiq.exceptions import ChaosIQException, ConfigurationMissingError

__all__ = ["cli"]


###############################################################################
# chaosiq CLI
###############################################################################
@click.group()
@click.option('--config-file', default=CHAOISQ_CONFIG_PATH,
              show_default=True, help='chaosiq configuration file path.')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx: click.Context, config_file: str=CHAOISQ_CONFIG_PATH):
    """
    The chaosiq command adds ChaosIQ features to the open-source chaostoolkit
    package.

    \b
    In order to benefit from thos features, you must have registered with
    ChaosIQ to get an access token. You should set that token in the
    configuration file with `chaosiq login`.
    \b
    Once you have configured chaosiq, simply use the chaostoolkit commands
    as usual, the chaosiq package will extend them by talking to the ChaosIQ
    services.
    """
    subcommand = ctx.invoked_subcommand
    ctx.obj = {}
    ctx.obj["config_file"] = config_file

    if subcommand == "config":
        return

    if not os.path.exists(config_file):
        click.echo(
            "You are missing a configuration file, creating '{c}'".format(
                c=config_file))
        initialize_config(config_file)

    try:
        ctx.obj["config"] = load_config(config_file)
        if subcommand != "login":
            ctx.obj["token"] = get_token(ctx.obj["config"])
    except ChaosIQException as err:
        raise click.ClickException(str(err))


@cli.command()
@click.pass_context
def login(ctx: click.Context):
    """
    Login with the chaosiq services.
    """
    email = click.prompt(click.style("Email", fg='green'), type=str)
    token = click.prompt(
        click.style("Token", fg='green'), type=str, hide_input=True)

    config = ctx.obj["config"]
    config_file = ctx.obj["config_file"]
    set_token(email, token, config)
    save_config(config, config_path=config_file)
    click.echo(
        "Credentials saved in configuration '{c}'".format(c=config_file))


@cli.command()
@click.option('--force', is_flag=True, help='Force the operation.')
@click.option('--key', help='Dotted key to set in the config.')
@click.option('--value', help='Value for a key.')
@click.argument("operation", type=click.Choice(["init", "set"]), nargs=1)
@click.pass_context
def config(ctx: click.Context, operation: str=None, key: str=None,
           value: str=None, force: bool=False):
    """
    Manage your chaosiq configuration.

    \b
    The following operations are supported:
    - init: to create a new default configuration (overriding the existing one)
    - set: to set a key in the configuration

    \b
    When setting a key, it can be dotted. In that case it is translated into
    nested keys inside the configuration. The value is always set to the last
    segment of the key.
    """
    config_file = ctx.obj["config_file"]
    if operation == "init":
        initialize_config(config_file, force)
        click.echo("The configuration was created at: {c}".format(
            c=config_file))
        return

    try:
        config = load_config(config_file)
    except ConfigurationMissingError as err:
        raise click.ClickException(str(err))

    if operation == "set":
        config = load_config(config_file)
        set_config_key(config, key, value)
        save_config(config, config_path=config_file)
