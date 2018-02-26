# coding=utf-8
"""
Manages the local Git repo
"""
import os
import sys
import typing

import git
from git.exc import GitCommandError

from .custom_logging import get_logger

LOGGER = get_logger('ELIB')


# pylint: disable=too-many-public-methods
class Repo:
    """
    Wrapper for git.Repo
    """

    def __init__(self):
        self.repo = git.Repo()
        self.stashed = False

    def get_current_branch(self) -> str:
        """
        Returns: current branch as a string
        """
        return self.repo.active_branch.name

    def tag(self, tag: str, overwrite: bool = False):
        """
        Tags the repo

        Args:
            tag: tag as a string
            overwrite: replace existing tag
        """
        LOGGER.debug(f'tagging repo: {tag}')

        try:
            self.repo.create_tag(tag)
        except GitCommandError as exc:
            if 'already exists' in exc.stderr and overwrite:
                self.remove_tag(tag)
                self.repo.create_tag(tag)
            else:
                raise

    def remove_tag(self, *tag: str):
        """
        Deletes a tag from the repo

        Args:
            tag: tag to remove
        """
        LOGGER.debug(f'removing tag: {tag}')

        self.repo.delete_tag(*tag)

    def get_latest_tag(self) -> typing.Optional[str]:
        """
        Returns: latest tag on the repo in the form TAG[-DISTANCE+[DIRTY]]
        """
        tags = list(self.repo.tags)
        if not tags:
            return None
        return tags.pop().name

    def latest_commit(self) -> git.Commit:
        """

        Returns: latest commit

        """
        return self.repo.head.commit

    def is_on_tag(self) -> bool:
        """
        :return: True if latest commit is tagged
        """
        if self.get_current_tag():
            return True

        return False

    def get_current_tag(self) -> typing.Optional[str]:
        """
        :return: tag name if current commit is on tag, else None
        """
        tags = list(self.repo.tags)
        if not tags:
            return None
        for tag in tags:
            if tag.commit == self.latest_commit():
                return tag.name

        return None

    def stash(self, stash_name: str):
        """
        Creates a stash

        Args:
            stash_name: name of the stash for easier later referencing
        """
        if self.stashed:
            LOGGER.error('already stashed')
        else:
            if not self.index_is_empty():
                LOGGER.error('cannot stash; index is not empty')
                sys.exit(-1)
            if self.untracked_files():
                LOGGER.error('cannot stash; there are untracked files')
                sys.exit(-1)
            if self.changed_files():
                LOGGER.debug('stashing changes')
                self.repo.git.stash('push', '-u', '-k', '-m', f'"{stash_name}"')
                self.stashed = True
            else:
                LOGGER.debug('no changes to stash')

    def unstash(self):
        """
        Pops the last stash if EPAB made a stash before
        """
        if not self.stashed:
            LOGGER.error('no stash')
        else:
            LOGGER.debug('popping stash')
            self.repo.git.stash('pop')
            self.stashed = False

    @staticmethod
    def ensure():
        """
        Makes sure the current working directory is a Git repository.
        """
        LOGGER.debug('checking repository')
        if not os.path.exists('.git'):
            LOGGER.error('this command is meant to be ran in a Git repository.')
            sys.exit(-1)
        LOGGER.debug('repository check succeeded')

    def last_commit_msg(self) -> str:
        """
        Returns: latest commit comment
        """
        return self.latest_commit().message.rstrip()

    def untracked_files(self) -> typing.List[str]:
        """

        Returns: list of untracked files

        """
        return self.repo.untracked_files

    def status(self):
        """

        Returns: Git status

        """
        return self.repo.git.status()

    def list_staged_files(self) -> typing.List[str]:
        """

        Returns: list of staged files

        """
        return [x.a_path for x in self.repo.index.diff('HEAD')]

    def index_is_empty(self) -> bool:
        """

        Returns: True if index is empty (no staged changes)

        """
        return len(self.repo.index.diff(self.repo.head.commit)) == 0

    def changed_files(self) -> typing.List[str]:
        """

        Returns: list of changed files

        """
        return [x.a_path for x in self.repo.index.diff(None)]

    def reset_index(self):
        """
        Resets changes in the index (working tree untouched)
        """
        LOGGER.debug('resetting changes')
        self.repo.index.reset()

    def stage_all(self):
        """
        Stages all changed and untracked files
        """
        LOGGER.debug('staging all files')
        self.repo.git.add(A=True)

    def stage_modified(self):
        """
        Stages modified files only (no untracked)
        """
        LOGGER.debug('staging modified files')
        self.repo.git.add(u=True)

    def stage_subset(self, *files_to_add: str):
        """
        Stages a subset of files
        Args:
            *files_to_add: files to stage
        """
        LOGGER.debug(f'staging files: {files_to_add}')
        self.repo.git.add(*files_to_add, A=True)
        # self.repo.index.add(files_to_add)

    @staticmethod
    def _add_skip_ci_to_commit_msg(message: str):
        first_line_index = message.find('\n')
        if first_line_index == -1:
            return message + ' [skip ci]'
        return message[:first_line_index] + ' [skip ci]' + message[first_line_index:]

    @staticmethod
    def _sanitize_files_to_add(
            files_to_add: typing.Optional[typing.Union[typing.List[str], str]] = None
    ) -> typing.Optional[typing.List[str]]:

        if not files_to_add:
            return None

        if files_to_add and isinstance(files_to_add, str):
            return [files_to_add]

        return files_to_add

    def commit(
            self,
            message: str,
            files_to_add: typing.Optional[typing.Union[typing.List[str], str]] = None,
            allow_empty: bool = False,
    ):
        """
        Commits changes to the repo

        Args:
            message: first line of the message
            files_to_add: optional list of files to commit
            allow_empty: allow dummy commit
        """

        files_to_add = self._sanitize_files_to_add(files_to_add)

        if not message:
            LOGGER.error('empty commit message')
            sys.exit(1)

        if os.getenv('APPVEYOR'):
            message = self._add_skip_ci_to_commit_msg(message)

            LOGGER.debug(f'committing with message: {message}')

        if files_to_add is None:
            self.stage_all()
        else:
            self.reset_index()
            self.stage_subset(*files_to_add)

        if self.index_is_empty() and not allow_empty:
            LOGGER.error('empty commit')
            sys.exit(-1)

        self.repo.index.commit(message=message)

    def _sanitize_amend_commit_message(
            self,
            append_to_msg: typing.Optional[str] = None,
            new_message: typing.Optional[str] = None,
            previous_message: str = None,
    ) -> str:
        message = None
        if new_message:
            message = new_message
        if append_to_msg:
            last_commit_msg = previous_message or self.repo.head.commit.message
            last_commit_msg = last_commit_msg.rstrip()
            if append_to_msg not in last_commit_msg:
                if '\n\n' not in last_commit_msg:
                    last_commit_msg = f'{last_commit_msg}\n'
                message = '\n'.join((last_commit_msg, append_to_msg))
            else:
                message = last_commit_msg
        if message is None:
            LOGGER.error('missing either "new_message" or "append_to_msg"')
            sys.exit(-1)
        return message

    def amend_commit(
            self,
            append_to_msg: typing.Optional[str] = None,
            new_message: typing.Optional[str] = None,
            files_to_add: typing.Optional[typing.Union[typing.List[str], str]] = None,
    ):
        """
        Amends last commit

        Args:
            append_to_msg: string to append to previous message
            new_message: new commit message
            files_to_add: optional list of files to commit
        """

        files_to_add = self._sanitize_files_to_add(files_to_add)

        if new_message and append_to_msg:
            LOGGER.error('cannot use "new_message" and "append_to_msg" together')
            sys.exit(-1)

        message = self._sanitize_amend_commit_message(append_to_msg, new_message)

        if os.getenv('APPVEYOR'):
            message = f'{message} [skip ci]'

        LOGGER.debug(f'amending commit with new message: {message}')
        latest_tag = self.get_current_tag()
        if latest_tag:
            LOGGER.debug(f'removing tag: {latest_tag}')
            self.remove_tag(latest_tag)

        LOGGER.debug('going back one commit')
        branch = self.repo.head.reference
        try:
            branch.commit = self.repo.head.commit.parents[0]
        except IndexError:
            LOGGER.error('cannot amend the first commit')
            sys.exit(-1)
        if files_to_add:
            self.stage_subset(*files_to_add)
        else:
            self.stage_all()
        self.repo.index.commit(message, skip_hooks=True)
        if latest_tag:
            LOGGER.debug(f'resetting tag: {latest_tag}')
            self.tag(latest_tag)

    def merge(self, ref_name: str):
        """
        Merges two refs

        Args:
            ref_name: ref to merge in the current one
        """
        if self.is_dirty():
            LOGGER.error(f'repository is dirty; cannot merge "{ref_name}"')
            sys.exit(-1)
        LOGGER.debug(f'merging {ref_name} into {self.get_current_branch()}')
        self.repo.git.merge(ref_name)

    def push(self):
        """
        Pushes all refs (branches and tags) to origin
        """
        LOGGER.debug('pushing repo to origin')
        self.repo.git.push()
        self.push_tags()

    def push_tags(self):
        """
        Pushes tags to origin
        """
        LOGGER.debug('pushing tags to origin')
        self.repo.git.push('--tags')

    def list_branches(self) -> typing.List[str]:
        """
        Returns: branches names as a list of string
        """
        return [head.name for head in self.repo.heads]

    def get_sha(self) -> str:
        """
        Returns: SHA of the latest commit
        """
        return self.repo.head.commit.hexsha

    def _validate_branch_name(self, branch_name: str):
        try:
            self.repo.git.check_ref_format('--branch', branch_name)
        except git.exc.GitCommandError:  # pylint: disable=no-member
            LOGGER.error(f'invalid branch name: {branch_name}')
            sys.exit(1)

    def checkout(self, reference: str):
        """
        Checks out a reference.

        If the index is dirty, or if the repository contains untracked files, the function will fail.

        Args:
            reference: reference to check out as a string

        """
        if not self.index_is_empty():
            LOGGER.error('index contains change; cannot checkout')
            print(self.status())
            sys.exit(-1)
        if self.is_dirty(untracked=True):
            LOGGER.error(f'repository is dirty; cannot checkout "{reference}"')
            print(self.status())
            sys.exit(-1)
        LOGGER.debug(f'checking out: {reference}')
        for head in self.repo.heads:
            if head.name == reference:
                self.repo.head.reference = head
                self.repo.head.reset(index=True, working_tree=True)
                break
        else:
            LOGGER.error(f'unknown reference: {reference}')
            sys.exit(-1)

    def create_branch(self, branch_name: str):
        """
        Creates a new branch

        Args:
            branch_name: name of the branch

        """
        LOGGER.debug(f'creating branch: {branch_name}')
        self._validate_branch_name(branch_name)
        if branch_name in self.list_branches():
            LOGGER.error('branch already exists')
            sys.exit(1)
        new_branch = self.repo.create_head(branch_name)
        new_branch.commit = self.repo.head.commit

    def create_branch_and_checkout(self, branch_name: str):
        """
        Creates a new branch if it doesn't exist

        Args:
            branch_name: branch name
        """
        self.create_branch(branch_name)
        self.checkout(branch_name)

    def is_dirty(self, untracked=False) -> bool:
        """
        Checks if the current repository contains uncommitted or untracked changes

        Returns: true if the repository is clean
        """
        result = False
        if not self.index_is_empty():
            LOGGER.error('index is not empty')
            result = True
        changed_files = self.changed_files()
        if bool(changed_files):
            LOGGER.error(f'repo has {len(changed_files)} modified files: {changed_files}')
            result = True
        if untracked:
            result = result or self.untracked_files()
        return result
