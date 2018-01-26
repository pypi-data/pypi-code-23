# coding=utf-8
"""
Runs all linters
"""
import click

import epab.utils

from ._flake8 import flake8
from ._isort import isort
from ._pep8 import pep8
from ._pylint import pylint
from ._safety import safety


@epab.utils.run_once
def _lint(ctx: click.Context, amend: bool):
    epab.utils.info('Running all linters')
    ctx.invoke(pep8, amend=amend)
    ctx.invoke(isort, amend=amend)
    ctx.invoke(flake8)
    ctx.invoke(pylint)
    ctx.invoke(safety)


@click.command()
@click.pass_context
@click.option('-a', '--amend', is_flag=True, help='Amend last commit with changes')
def lint(ctx: click.Context, amend: bool):
    """
    Runs all linters

    Args:
        ctx: click context
        amend: whether or not to commit results
    """
    _lint(ctx, amend)
