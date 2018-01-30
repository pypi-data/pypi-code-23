"""The codecov tool uplods coverage data to ``codecov.io``."""
import argparse
import logging
from os.path import exists, join

from menhir.tool import TEST, Tool
from menhir.tool_utils import (
    NOTHING_TO_DO,
    OK,
    changed_state,
    has_self_or_dependent_changes,
    tool_env,
)

log = logging.getLogger(__name__)


def tool():
    return Codecov()


class Codecov(Tool):
    def name(arg):
        return "codecov"

    def dir_info(tool, path, info):
        setup_path = join(path, 'setup.cfg')
        path = join(path, '.coverage')
        return {
            'project_recognised': exists(setup_path),
            'can_run': exists(path),
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build phase."""
        import re
        from os import getenv
        from os.path import exists, join
        from menhir.tool_utils import call, package_script

        if not getenv('CODECOV_TOKEN'):
            return NOTHING_TO_DO

        log.info('Try Running codecov in %s', path)

        changed = changed_state(info)

        if has_self_or_dependent_changes(changed):
            log.info('Running codecov in %s', path)

            if not exists(join(path, '.coverage')):
                log.debug('No .coverage in %s', path)
                return OK

            env = tool_env()
            env['MENHIR_PROJECT'] = info['project-name']
            env['MENHIR_CODECOV_FLAGS'] \
                = re.sub(r'\W', "_", info['project-name'])
            env['CODECOV_TOKEN'] = getenv('CODECOV_TOKEN')

            with package_script("/tools/codecov/upload.sh") as f:
                return call([f.name], env=env,)
        else:
            log.info('not running codecov in %s', path)
            return OK

    def build_jobs(tool, info):
        return [TEST]


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Push coverage metrics to codecov.io",
        **kwargs
    )
    parser.add_argument('remainder', nargs=argparse.REMAINDER)
    return parser
