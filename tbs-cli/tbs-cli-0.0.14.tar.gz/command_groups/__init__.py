import os
import json
import click
import tbs_client
import inspect
from pathlib import Path
from tbscli.decorators import (instantiate_context,
                               print_result)
from tbscli.CONSTANTS import CLICK_CONTEXT_SETTINGS


@click.command(help="Login to 3Blades", context_settings=CLICK_CONTEXT_SETTINGS)
@click.option("--username", "-u", help="3Blades account username")
@click.option("--password", "-p", help="3Blades account password")
@instantiate_context
@print_result
def login(ctx, *args, **kwargs):
    home_dir = os.getenv("HOME")
    config_file = Path(home_dir, ".threeblades.config")
    if config_file.exists():
        click.echo(".threeblades.config file already exists in $HOME directory. "
                   "Using that to login.")
        with config_file.open() as conf:
            line = conf.read()
            conf_json = json.loads(line)
            if "token" in conf_json and "namespace" in conf_json:
                ctx.obj['token'] = conf_json['token']
                ctx.obj['namespace'] = conf_json['namespace']
            else:
                click.echo("A .threeblades.config file exists, but is invalid. "
                           "Please delete it and try logging in again.")
    else:
        username = kwargs.get("username") or click.prompt("Username", type=str)
        password = kwargs.get("password") or click.prompt("Password", type=str, hide_input=True)
        auth_api = tbs_client.AuthApi()
        jwt_data = tbs_client.JWTData(username=username,
                                      password=password)
        response = auth_api.auth_jwt_token_auth(jwt_data=jwt_data)

        if response.token:
            config = {'token': response.token,
                      'namespace': username}

            ctx.obj['token'] = response.token
            ctx.obj['namespace'] = username
            with open(config_file, "w") as tok_file:
                tok_file.write(json.dumps(config))

            return f"User '{username}' successfully logged in."
        else:
            return "Something went wrong with login :/"


def istbscommand(obj):
    return (inspect.isclass(obj)
            and issubclass(obj, ThreeBladesBaseCommand)
            and obj != ThreeBladesBaseCommand)


class ThreeBladesBaseCommand(click.Command):
    def __init__(self, name, params=list, api_class=None, help=""):
        super(ThreeBladesBaseCommand, self).__init__(name=name,
                                                     params=params,
                                                     help=help,
                                                     context_settings=CLICK_CONTEXT_SETTINGS,
                                                     callback=self._full_command)
        self.context = {}
        home_dir = os.getenv("HOME")
        config_file = Path(home_dir, ".threeblades.config")
        if config_file.exists():
            with config_file.open() as conf_file:
                line = conf_file.read()
                conf_json = json.loads(line)
                self.context['token'] = conf_json['token']
                self.context['namespace'] = conf_json.get('namespace')
        tbs_client.configuration.api_key['Authorization'] = self.context.get('token')
        tbs_client.configuration.api_key_prefix['Authorization'] = 'Bearer'
        self.api_client = api_class()

    def _cmd(self, *args, **kwargs):
        raise NotImplementedError("All subclasses of ThreeBladesBaseCommand must "
                                  "define the _cmd method.")

    def _validate_params(self, *args, **kwargs):
        return args, kwargs

    def _full_command(self, *args, **kwargs):
        new_args, new_kwargs = self._validate_params(*args, **kwargs)
        self._cmd(*new_args, **new_kwargs)

    def invoke(self, ctx):
        if self.callback is not None:
            return ctx.invoke(self.callback, **ctx.params)
