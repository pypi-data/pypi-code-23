import os
import json
import click
from functools import update_wrapper
from pathlib import Path


def instantiate_context(func):
    home_dir = os.getenv("HOME")
    config_file = Path(home_dir, ".threeblades.config")

    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        if ctx.obj is None:
            ctx.obj = {}
        if config_file.exists():
            with config_file.open() as conf_file:
                line = conf_file.read()
                conf_json = json.loads(line)
                ctx.obj['token'] = conf_json['token']
                ctx.obj['namespace'] = conf_json.get('namespace')
        return ctx.invoke(func, ctx, *args, **kwargs)
    return update_wrapper(new_func, func)


def print_result(func):
    # This decorator is stupid simple for now, but it will be helpful in the future
    # When we begin printing output in different formats based on user settings
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        click.echo(result)
    return wrapper
