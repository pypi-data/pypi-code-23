#!/usr/bin/env python3
# coding=utf-8

"""
@version:0.1
@author: ysicing
@file: /finit.py
@time: 18-1-23 上午12:19
"""

import os
import click


@click.group()
def cli():
    """A simple cmd line tool"""


@click.command(help='create new project')
def new():
    click.echo("add record. {}".format(os.getcwd()))


cli.add_command(new)


