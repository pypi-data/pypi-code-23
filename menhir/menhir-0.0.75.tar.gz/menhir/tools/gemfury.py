"""The gemfury tool provides ``publish`` command.

The ``publish`` task takes a file and pushes it to gemfury.

Configuration is under the ``gemfury`` key.

The ``org`` key contains the user or organisation name to publish artifacts to
on GemFury.

"""
import argparse
import logging

import requests

from menhir.tool import Tool
from menhir.tool_utils import (
    OK,
    FAIL,
    NOTHING_TO_DO,
)
from menhir.utils import multi, method

log = logging.getLogger(__name__)


def tool():
    return GemFury()


class GemFury(Tool):

    def name(arg):
        return "gemfury"

    def dir_info(tool, path, info):
        from os.path import exists, join
        path = join(path, '.gemfury')
        recognised = info.get('gemfury') or exists(path)
        return {
            'project_recognised': recognised,
            'can_run': recognised,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build phase."""
        return NOTHING_TO_DO


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Commands to interact with gemfury.",
        **kwargs
    )
    parsers = parser.add_subparsers(help="GemFury commands", dest='phase')
    p = parsers.add_parser(
        'publish',
        help='Publish a release to GemFury'
    )
    p.add_argument(
        '--org',
        help="Specify the GemFury user or organisation name to publish to")
    p.add_argument(
        '--token',
        help="Specify the GemFury token to use for publishing")
    p.add_argument(
        '--package',
        help="path to package to publish")
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    return parser


@multi
def task(phase_name, path, info, args):
    return phase_name


@method(task)
def task_default(phase_name, path, info, args):
    return NOTHING_TO_DO


@method(task, 'publish')
def gemfury_build(phase_name, path, info, args):
    log.info('Running gemfury publish in %s', path)

    gemfury = info.get('gemfury', {})
    token = args.token or gemfury.get('token')
    org = args.org or gemfury.get('org')
    package = args.package or gemfury.get('package')

    if not token:
        log.error('No gemfury token specified')
        return FAIL

    url = "https://{}@push.fury.io/{}/".format(
        token,
        org,
    )
    with open(package) as f:
        res = requests.post(url, files=dict(package=f))

    res.raise_for_status()

    return OK
