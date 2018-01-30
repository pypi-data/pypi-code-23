"""The build tool invokes build phases according to a configuration."""
import argparse
import logging

from menhir.tool import Tool
from menhir.tool_utils import (
    FAIL,
    NOTHING_TO_DO,
    OK,
    package_script,
    tool_env,
)

log = logging.getLogger(__name__)


def tool():
    return Build()


class Build(Tool):

    def dir_info(tool, path, info):
        return {
            'project_recognised': True,
            'can_run': True,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build phase."""
        import subprocess

        log.info('build: %s %s %s', path, info, args)
        if (
                'changed' not in info or
                info['changed'].get('self') or
                info['changed'].get('dependents')
        ):
            log.info('Running build in %s', path)
            project_name = info['project-name']
            env = tool_env()
            env['MENHIR_PROJECT'] = project_name
            with package_script("/tools/build/test.sh") as f:
                res = subprocess.call([f.name] + args.args, env=env)
                if res:
                    return FAIL
                return OK
        else:
            return NOTHING_TO_DO


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Invoke build based tests",
        **kwargs
    )
    parser.add_argument('args', nargs='*', help='build arguments')
    return parser
