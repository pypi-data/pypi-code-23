#!python
"""Example script
escher.py-cli --config-file="experiment.yaml" --starting-index=0 --extra-arguments-etc
"""
from functools import reduce
from os import getcwd, environ
from pprint import pformat
import click
import re
from termcolor import colored as c

from click import Abort
import escher_cli
from escher_cli import helpers, script_runner
from subprocess import check_call


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--debug', is_flag=True)
def escher(debug):
    """Escher-cli is a command line tool for your ML training."""
    # todo: use decorator pattern to share common parameters
    # link: https://github.com/pallets/click/issues/108
    if debug:  # set debug flag in helpers
        helpers.set_debug()
    helpers.debug("debug mode is ON.")


@escher.command(context_settings=dict(ignore_unknown_options=True))
def init():
    """initialize the project with an .escher runcom file, similar to `.babelrc` or `.bashrc`"""
    from shutil import copyfile
    from os import getcwd, path
    # todo: add error handling
    # add iterative guide for {name}, {author(s)} etc
    script_path = path.dirname(__file__)
    target_path = path.join(getcwd(), ".escher")
    if path.exists(target_path):
        print(f"{c('✘', 'red')}project file already exist! check .escher")
        # raise Error if --ignore-error
    else:
        copyfile(path.join(script_path, "./default-scripts/default.escher"), target_path)
        print(f"{c('✔', 'green')} project file has been created: .escher")


@escher.command(context_settings=dict(ignore_unknown_options=True))
@click.pass_context
# @escher.py.argument()
@click.option('--worker', '-w', default='local', type=str)
@click.argument('script', default="default", type=str)
@click.option('--work-directory', default=getcwd(), type=str)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def run(ctx, worker, script, work_directory, args):
    """escher run <your script name>
    Some of the default cloud bindings are:
    - aws-nvidia.launch.sh
    """
    # todo: add error catching to make error look nicer
    try:
        return script_runner.run(worker, script, work_directory, args)
    except Exception as e:
        print(e);
