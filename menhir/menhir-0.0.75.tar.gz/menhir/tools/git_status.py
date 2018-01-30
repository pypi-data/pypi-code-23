"""Add git status information.

The :command:`git_status` tool adds a list of changed files into the
menhir state dict.  This is used by th command:`multiproject` tool to
determine which projects, dependents and dependees have been changed.

"""
import argparse
import logging

from menhir import gitutils
from menhir.tool import Tool
from menhir.tool_utils import OK

log = logging.getLogger(__name__)


def tool():
    return GitStatus()


class GitStatus(Tool):

    def name(tool):
        return 'git_status'

    def dir_info(tool, path, info):
        from menhir import gitutils
        has_git = gitutils.find_root()
        return {
            'project_recognised': has_git,
            'can_run': has_git,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        """Arg parser for the tool options and arguments."""
        return parser(**kwargs)

    def execute_tool(tool, path, info, args):
        """Add git status information."""
        git_root = gitutils.find_root()
        files = changed_files(git_root, args.from_commit)
        info['git_status'] = files
        info['git_status']['root'] = git_root
        return OK


def parser(**kwargs):
    """Arg parser for the tool options and arguments."""
    parser = argparse.ArgumentParser(
        description="""GitStatus command to add git status.
Adds changed information to project infos.
        """,
        **kwargs
    )
    parser.add_argument(
        "--from-commit",
        help="""
Run task on projects that depend on files changed since the
specified commit.  This can be specified as a single commit,
e.g. 3f8e5bb, 3f8e5bb^, head^.
"""
    )

    parser.add_argument(
        "--dirty",
        help="""
Run task on projects that depend on dirty (uncommited) files.
"""
    )
    parser.add_argument('remainder', nargs=argparse.REMAINDER)
    return parser


def changed_files(git_root, from_commit):
    """Return the files that have been changed.

    If from_commit is not None, or an implicit from_commit is found
    from CIRCLE_COMPARE_URL, or CIRCLE_SHA1, then return files changed
    since that commit.

    If there are uncommitted files, return them, return the last
    commit's files.
    """
    from menhir.gitutils import (
        files_changed_since,
        head_commit,
        repo,
        uncommited_files,
    )
    git_repo = repo(git_root)

    from_commit = with_implicit_from_commit(from_commit) or \
        str(head_commit(git_repo)) + "^"

    uncommited = uncommited_files(git_repo)['all']

    files = files_changed_since(git_repo, from_commit)

    return {
        'from_commit': from_commit,
        'changed': files,
        'uncommited': uncommited,
    }


def with_implicit_from_commit(from_commit):
    """Return any implicit from commit specification.

    Returns the first of the following that is not nil:

    * ``from_commit``
    * the start of the CIRCLE_COMPARE_URL range
    * the commit prior to CIRCLE_SHA1
    """
    import os

    if from_commit:
        return from_commit

    compare_url = os.getenv('CIRCLE_COMPARE_URL')
    if compare_url:
        log.debug('Deriving commit range from %s', compare_url)
        commit_range = compare_url.rsplit('/', 1)[1]
        return commit_range.split('..')[0]

    if os.getenv('CIRCLE_SHA1'):
        sha = os.getenv('CIRCLE_SHA1')
        return sha+"^"


# def git_config():
#     from os.path import relpath
#     from menhir import gitutils
#     git_root = gitutils.find_root()
#     return {
#         'git_root': git_root,
#         'git_prefix': relpath(git_root),
#     }
