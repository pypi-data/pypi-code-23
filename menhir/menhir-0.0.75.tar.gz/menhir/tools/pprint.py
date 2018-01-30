"""Tool to print menhir's configuration and state dict.

This can be used to inspect what the configuration a previous tool
produces, or the next tool sees.

It can output in python pprint, json or yaml formats.
"""
from __future__ import absolute_import

import argparse
import logging
import pprint as pp
import sys

import json

from ..fileutils import yaml_dumper
from ..tool import Tool
from ..tool_utils import OK, FAIL


log = logging.getLogger(__name__)


def tool():
    return Pprint()


class Pprint(Tool):

    def dir_info(tool, path, info):
        return {
            'project_recognised': False,
            'can_run': True,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args):
        """Pprint the menhir config."""
        if args.format == 'pprint':
            pp.pprint(info, width=80)
        elif args.format == 'yaml':
            yaml = yaml_dumper()
            yaml.dump(info, sys.stdout)
        elif args.format == 'json':
            print(json.dumps(info, sort_keys=True, indent=4))
        else:
            log.error('Invalid output format: "%s', args.format)
            return FAIL
        return OK


def parser(**kwargs):
    """Configure arg parser for the tool options and arguments."""
    parser = argparse.ArgumentParser(
        description="Pretty print the menhir configuration.",
        **kwargs
    )
    parser.add_argument(
        "--format",
        default='yaml',
        choices=['json', 'pprint', 'yaml'],
        help="Output format.",
    )
    parser.add_argument('remainder', nargs=argparse.REMAINDER)
    return parser
