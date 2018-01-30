"""The setup_py tool provides functionality based on ``setup.py``.

The setup.py tool contributes iner-project dependencies by reading
relative ``file://...`` links in ``requirements.txt`` files.

The setup_py tool provides the ``sdist`` and ``lambda-package``
tasks.

lambda-package
--------------

The ``lambda-package`` task builds a ``package.zip`` file for upload
to AWS Lambda.  The tool is only run if there is a .lambda-package
file in the project directory.

"""
from __future__ import print_function  # NOQA

import argparse
import logging
import os
import re
import subprocess
import sys

from menhir.tool import DEPENDENCIES, PACKAGE, TEST, Tool
from menhir.tool_utils import (
    FAIL,
    NOTHING_TO_DO,
    OK,
    changed_state,
    has_self_or_dependent_changes,
    package_script,
    tool_env,
    working_dir
)
from menhir.utils import method, multi

DEP_PATTERN = re.compile('file:(.*)#egg=.*')

log = logging.getLogger(__name__)


def tool():
    return SetupPy()


class SetupPy(Tool):

    def name(arg):
        return "setup_py"

    def dir_info(tool, path, info):
        from os.path import exists, join
        has_setup_py = exists(join(path, 'setup.py'))
        return {
            'project_recognised': has_setup_py,
            'can_run': has_setup_py,
        }

    def dependencies(tool, path):
        from os.path import join, normpath
        log.debug('setup.py dependencies in %s', path)
        requirements_path = join(path, 'requirements.txt')
        if not os.path.isfile(requirements_path):
            return []

        try:
            requirements, dependency_links = read_requirements(
                requirements_path
            )
            return [
                normpath(join(path, DEP_PATTERN.match(l).group(1)))
                for l in dependency_links
                if l.startswith('file:')
            ]
        except Exception:
            print('Failed to infer dependencies in for setup_py %s' % path,
                  file=sys.stderr)
            raise

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args):
        """Execute a build phase."""
        changed = changed_state(info)
        if has_self_or_dependent_changes(changed):
            return task(path, info, args)
        return NOTHING_TO_DO

    def build_jobs(tool, info):
        return [DEPENDENCIES, TEST, PACKAGE]


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Invoke helpers that use setup.py",
        **kwargs
    )
    parsers = parser.add_subparsers(help="Tool phases", dest='phase')

    p = parsers.add_parser(
        'sdist',
        help='Run dist on project, and on local project requirements'
    )
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'lambda-package',
        help='Build a package.zip file for the setup.py project'
    )
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'test',
        help='Run tests for the setup.py project'
    )
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'install',
        help='Install the setup.py project'
    )
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    return parser


def read_requirements(path):
    with open(path, 'r') as f:
        return process_requirements(f)


def process_requirements(f):
    requirements = []
    dependency_links = []
    for line in f.read().split():
        if '#egg=' in line:
            package_name = line.rsplit('#egg=', 1).pop()
            requirements.append(package_name)
            dependency_links.append(line)
        else:
            requirements.append(line)
    return requirements, dependency_links


@multi
def task(path, info, args):
    log.info('Running %s in %s', args.phase, path)
    return args.phase


@method(task)
def default_task(path, info, args):
    """Unknown task, does nothing."""
    return NOTHING_TO_DO


@method(task, 'sdist')
def sdist(pdir, info, args):
    """Tar python project at path, including relative requirements."""
    import os.path as path
    import shutil
    import subprocess
    from os import mkdir, walk

    res = subprocess.call(["python", "setup.py", "sdist"], env=tool_env())
    if res:
        return FAIL

    dist_reqs = 'dist-requirements'
    if not path.exists(dist_reqs):
        mkdir(dist_reqs)

    reqs = "requirements.txt"
    if path.exists(reqs):
        with open(reqs) as f:
            for line in f.read().splitlines():
                match = DEP_PATTERN.match(line)
                if match:
                    dir = match.group(1)
                    with working_dir(dir):
                        log.debug('Running sdist for %s', dir)
                        res = subprocess.call(
                            ["python", "setup.py", "sdist"],
                            env=tool_env(),
                        )
                        if res:
                            return False
                    for root, dirs, files in walk(path.join(dir, 'dist')):
                        for f in files:
                            shutil.copyfile(
                                path.join(root, f),
                                path.join(dist_reqs, f))

    log.debug('Completed sdist in %s', pdir)
    return OK


@method(task, 'lambda-package')
def lambda_package(path, info, args):
    """Zip python project at path, including relative requirements.

    Only packages projects that contain a ``.lambda-package`` file.
    """
    import subprocess
    from os.path import exists
    from menhir.tool_utils import package_script

    marker = '.lambda-package'
    serverless = 'serverless.yml'
    if not (exists(marker) or exists(serverless)):
        print('Not a lambda project (no %s)' % marker)
        return NOTHING_TO_DO

    with package_script("/tools/setup_py/lambda-package.sh") as f:
        res = subprocess.call([f.name], env=tool_env())
        if res:
            return FAIL
    return OK


@method(task, 'safety')
def safety(path, info, args):
    """Run safety vulnerability checks."""
    with package_script("/tools/setup_py/safety.sh") as f:
        res = subprocess.call([f.name], env=tool_env())
        if res:
            return FAIL
    return OK


@method(task, 'test')
def test(path, info, args):
    """Run tests."""
    with package_script("/tools/setup_py/wrapper.sh") as f:
        res = subprocess.call(
            [f.name, 'python', 'setup.py', 'test'],
            env=tool_env(),
        )
    if res:
        return FAIL
    return OK


@method(task, 'install')
def install(path, info, args):
    """Run install."""
    with package_script("/tools/setup_py/wrapper.sh") as f:
        res = subprocess.call([f.name, 'pip', 'install', '.'], env=tool_env())
    if res:
        return FAIL
    return OK
