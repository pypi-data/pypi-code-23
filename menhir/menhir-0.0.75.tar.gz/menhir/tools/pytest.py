"""The pytest tool invokes pytest based tests."""
import argparse
import logging

from menhir.tool import TEST, Tool
from menhir.tool_utils import (
    FAIL,
    NOTHING_TO_DO,
    OK,
    changed_state,
    has_self_or_dependent_changes,
    package_script,
    tool_env,
)

log = logging.getLogger(__name__)


def tool():
    return PyTest()


class PyTest(Tool):

    def dir_info(tool, path, info):
        from os.path import exists, join
        has_pytest = None
        path = join(path, 'setup.cfg')
        if exists(path):
            with open(path, "r") as file:
                data = file.read()
                has_pytest = 'pytest' in data
        return {
            'project_recognised': has_pytest,
            'can_run': has_pytest,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build phase."""
        import subprocess

        log.info('pytest: %s %s %s', path, info, args)

        changed = changed_state(info)

        if has_self_or_dependent_changes(changed):
            log.info('Running pytest in %s', path)
            project_name = info['project-name']
            env = tool_env()
            env['MENHIR_PROJECT'] = project_name
            with package_script("/tools/pytest/test.sh") as f:
                res = subprocess.call([f.name] + args.args, env=env)
                if res:
                    return FAIL
                return OK
        else:
            return NOTHING_TO_DO

    def build_jobs(tool, info):
        return [TEST]


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Invoke pytest based tests",
        **kwargs
    )
    parser.add_argument('args', nargs='*', help='pytest arguments')
    return parser
