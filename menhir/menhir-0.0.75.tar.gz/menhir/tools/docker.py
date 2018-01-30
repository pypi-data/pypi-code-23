"""The docker tool provides ``build``, ``push`` and ``publish`` commands.

The `build` tasks build the dockerfile and tags the resulting image with the
project's name.
"""
import argparse
import logging
import os
from functools import reduce
from os.path import exists, join

from menhir.project import branch, image
from menhir.tool import DEPLOY, Tool
from menhir.tool_utils import (
    FAIL,
    NOTHING_TO_DO,
    OK,
    argv_to_dict,
    call,
    changed_state,
    has_self_or_dependent_changes,
    package_script,
    run_if,
    slugify,
    tool_env,
)
from menhir.utils import method, multi

log = logging.getLogger(__name__)


def tool():
    return Docker()


class Docker(Tool):

    def name(arg):
        return "docker"

    def dir_info(tool, path, info):
        path = join(path, 'Dockerfile')
        has_dockerfile = exists(path)
        return {
            'project_recognised': has_dockerfile,
            'can_run': has_dockerfile,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build phase."""

        phase_name = args.phase

        dockerfile = 'Dockerfile'

        if not exists(dockerfile):
            log.debug(
                'No Dockerfile %(dockerfile)s',
                {'dockerfile': dockerfile})
            return NOTHING_TO_DO

        changed = changed_state(info)
        run_flag = has_self_or_dependent_changes(changed)

        if phase_name in {'build', 'push', 'publish'}:
            with run_if(run_flag, phase_name, path) as flag:
                if flag:
                    return task(phase_name, path, info, args)
                return OK
        else:
            return NOTHING_TO_DO

    def build_jobs(tool, info):
        return [DEPLOY]


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Commands to build and push docker images.",
        **kwargs
    )
    parsers = parser.add_subparsers(help="Docker commands", dest='phase')
    p = parsers.add_parser(
        'build',
        help='Build a docker image from a Dockerfile'
    )
    p.add_argument(
        '--build-arg', dest='build_args', action='append',
        help="Specify a build argument for the docker build")
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'push',
        help='Push a docker image to a remote repository'
    )
    p.add_argument(
        '--arg', dest='args', action='append',
        help="Specify an argument for the encryption settings")
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'publish',
        help='Build and push a docker image to a remote repository'
    )
    p.add_argument(
        '--arg', dest='args', action='append',
        help="Specify an argument for the encryption settings")
    p.add_argument(
        '--build-arg', dest='build_args', action='append',
        help="Specify a build argument for the docker build")
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    return parser


@multi
def task(phase_name, path, info, args):
    return phase_name


@method(task)
def task_default(phase_name, path, info, args):
    return NOTHING_TO_DO


@method(task)
def task_publish(phase_name, path, info, args):
    res = task('build', path, info, args)
    if res != OK:
        return res
    return task('push', path, info, args)


@method(task, 'build')
def docker_build(phase_name, path, info, args):
    log.info('Running docker-build in %s', path)

    project_name = info['project-name']

    env = tool_env()

    env_names = [
        v for v in info.get('docker', {}).get('env', [])
        if v in os.environ
    ]

    for v in env_names:
        env[v] = os.environ[v]

    env_args = reduce(
        lambda v, a: v + ['--build-arg', '{}={}'.format(a, os.environ[a])],
        env_names,
        []
    )

    build_args = reduce(
        lambda v, a: v + ['--build-arg', a],
        args.build_args or [],
        [])

    # docker build -t "${MENHIR_TAG}" "$@" .
    argv = (
        ['docker', 'build', '-t', project_name] + build_args + env_args + ['.']
    )
    print(argv)
    return call(argv, env=env)


@method(task, 'push')
def docker_push(phase_name, path, info, args):
    log.info('Running docker-push in %s', path)

    arg_names = info.get('docker', {}).get('args', [])
    arg_values = args.args or []

    arg_dict = argv_to_dict(arg_names, arg_values)
    if arg_dict is None:
        log.error('Expected --arg for each of %s', arg_names)
        return FAIL

    project_name = info['project-name']
    current_branch = branch()
    tag = project_name
    sha_tag = image(info, path)
    if not sha_tag:
        log.error('No remote repository configured to push to.')
        return FAIL

    sha_tag = sha_tag % arg_dict
    branch_tag = "%s:%s" % (
        sha_tag.split(':')[0],
        slugify(current_branch, length=40),
    )
    branch_tag = branch_tag % arg_dict

    env = tool_env()
    env['MENHIR_TAG'] = tag
    env['MENHIR_BRANCH_TAG'] = branch_tag
    env['MENHIR_SHA_TAG'] = sha_tag

    with package_script("/tools/docker/docker-push.sh") as f:
        return call([f.name], env=env,)
