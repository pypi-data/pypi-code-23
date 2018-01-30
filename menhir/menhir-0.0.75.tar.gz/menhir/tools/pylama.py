"""Tool that invokes the given command.

If the given command is given with a relative path, then this is
interpreted as a project local, and the failure is determined by the
``--if-no-op`` flag.

"""
import argparse
import logging
import subprocess
from os.path import exists, join

from menhir.tool import LINT, Tool
from menhir.tool_utils import (
    FAIL,
    NOTHING_TO_DO,
    OK,
    changed_state,
    has_self_or_dependent_changes,
    tool_env,
)

log = logging.getLogger(__name__)


def tool():
    return Pylama()


class Pylama(Tool):

    def dir_info(tool, path, info):
        has_setup_py = exists(join(path, 'setup.py'))
        return {
            'project_recognised': has_setup_py,
            'can_run': has_setup_py,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        """Arg parser for the tool options and arguments."""
        return parser(**kwargs)

    def execute_tool(tool, path, info, args):
        """Pylamaute the script tool."""
        cmd = ['pylama']
        changed = changed_state(info)
        log.info('Running "%s" in %s', " ".join(cmd), path)
        if not has_self_or_dependent_changes(changed):
            return NOTHING_TO_DO

        env = tool_env()
        if changed is None:
            env['MENHIR_ALL'] = "1"
        else:
            if changed.get('self'):
                env['MENHIR_CHANGED_SELF'] = "1"
            if changed.get('dependents'):
                env['MENHIR_CHANGED_DEPENDENTS'] = "1"
            if changed.get('dependees'):
                env['MENHIR_CHANGED_DEPENDEES'] = "1"

        result = subprocess.call(cmd, env=env)
        log.debug('Pylama result: %s', result)
        if result:
            return FAIL
        return OK

    def build_jobs(tool, info):
        return [LINT]


def parser(**kwargs):
    """Arg parser for the tool options and arguments."""
    parser = argparse.ArgumentParser(
        description="Run pylama.",
        **kwargs
    )

    parser.add_argument(
        'command_args',
        nargs=argparse.REMAINDER,
        help='command arguments'
    )
    return parser
