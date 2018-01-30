"""The git tool provides tasks for working with a git reopsitory.

The ``install-hooks`` task installs local git hooks.  Hooks are
assumed to be in a top-level ``git-hooks`` directory.  This can be
configured with the ``.git.hook-dir`` configuration value.

The ``with-stashed-changes`` task runs whatever command it it is
passed with all unstaged commits stashed.

"""
import argparse
import logging
import stat

from menhir.tool import CHECKOUT, Tool
from menhir.tool_utils import OK, FAIL
from menhir.utils import multi, method

log = logging.getLogger(__name__)

RWXR_XR_X = (
    stat.S_IRUSR |
    stat.S_IWUSR |
    stat.S_IXUSR |
    stat.S_IRGRP |
    stat.S_IXGRP |
    stat.S_IROTH |
    stat.S_IXOTH
)


def tool():
    return Git()


class Git(Tool):

    def dir_info(tool, path, info):
        from os.path import isdir, join
        path = join(path, '.git')
        has_git = isdir(path)
        return {
            'project_recognised': has_git,
            'can_run': has_git,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args):
        """Execute git task."""
        return task(path, info, args)

    def build_jobs(tool, info):
        return [CHECKOUT]


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="git utilities",
        **kwargs
    )
    parsers = parser.add_subparsers(help="git tasks", dest='phase')

    p = parsers.add_parser(
        'install-hooks',
        help='Install local git hooks'
    )
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'with-stashed-changes',
        help='Execute a command with all unstaged changes stashed'
    )
    p.add_argument('cmd', nargs='*', help='command to execute')
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    return parser


@multi
def task(path, info, args):
    """Execute a task."""
    return args.phase


@method(task, 'install-hooks')
def install_hooks(path, info, args):
    """Install local git hooks from a project directory."""
    from os import chmod, listdir
    from os.path import isdir, isfile, join, normpath
    from shutil import copy

    log.debug('git install-hooks')
    hook_dir_name = info.get('git', {}).get('hook-dir', "git-hooks")
    hook_dir = join(path, hook_dir_name)
    if not isdir(hook_dir):
        log.error('No git hooks directory %s', normpath(hook_dir))
        return FAIL

    target_dir = join(path, ".git", "hooks")
    for f in listdir(hook_dir):
        log.debug('Found potential hook file %s', f)
        src = join(hook_dir, f)
        if isfile(src):
            log.debug('Install git hook %s', f)
            target = join(target_dir, f)
            copy(src, target)
            chmod(target, RWXR_XR_X)

    return OK


@method(task, 'with-stashed-changes')
def with_stashed_changes(path, info, args):
    from menhir import gitutils
    from menhir.tool_utils import call

    repo = gitutils.repo()
    with gitutils.staged_as_committed(repo):
        with gitutils.stashed_changes(repo):
            return call(args.cmd)
