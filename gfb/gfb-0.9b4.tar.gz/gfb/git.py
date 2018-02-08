import sys
import os
import io
import typing
import locale
import re
import github
import urllib
import configparser
import subprocess
from gfb import userinput
from datetime import datetime
from github import Github


class GitError(Exception):
    def __init__(self, message):
        super().__init__(self)
        self.message = message


class AuthenticationError(GitError):
    """ github authentication error """
    def __init__(self, message):
        super().__init__(message)


class BadRepoError(GitError):
    """ bad or missing repository error """
    def __init__(self, message):
        super().__init__(message)


class NotInLocalRepo(GitError):
    def __init__(self, message):
        super().__init__(message)


class Credentials:
    """ github credentials and repo information """

    def __init__(self, remote_repo: str,
                 username: str = "",
                 password: str = "",
                 api_key: str = ""):

        self.repo = remote_repo
        self.username = username
        self.password = password
        self.api_key = api_key

    def __str__(self):
        value = "Repo: " + self.repo
        if self.username and self.password:
            value += "("+self.username+","+self.password+")"
        if self.api_key:
            value += "(key: " + self.api_key + ")"
        return value


class BranchFinder:
    """ find a branch in a remote repository """

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.github = None
        self.repo = None

    def __auth(self):
        """ authenticate against github """
        if self.credentials.api_key:
            self.github = Github(self.credentials.api_key)
        else:
            self.github = Github(self.credentials.username,
                                 self.credentials.password)

        try:
            self.github.get_user().name
            self.repo = self.github.get_repo(self.credentials.repo)
            self.repo.full_name
        except github.BadCredentialsException as bc:
            raise AuthenticationError("{0}".format(bc))
        except github.UnknownObjectException as uo:
            raise BadRepoError("{0}".format(uo))

    def find_branch(self, regex_string: str = "") -> typing.List[str]:
        """ locate branch that matches regex """
        if not self.repo:
            self.__auth()

        regex = re.compile(regex_string)
        matches = [br.name for br in self.repo.get_branches() if
                   regex.match(br.name)]
        return matches


class LocalRepoFinder:
    """ locate the local repo in which we're running """

    def __init__(self, cwd: str):
        self.starting_dir = cwd
        self.repo_dir = None
        self.repo_name = None

    def local_repo_name(self) -> str:
        """ return the name of the repo in cwd """
        if not self.find_local_repo_dir():
            raise NotInLocalRepo("no local repo found")
        git_config = "/".join([self.repo_dir, 'config'])
        if not os.path.exists(git_config):
            raise BadRepoError("{0} is not a git repo".format(git_config))
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read(git_config)
        repo_name = self.get_repo_name(cfg_parser)
        if not repo_name:
            raise NotInLocalRepo("unable to find local repo name")
        self.repo_name = repo_name
        return repo_name

    def get_repo_name(self, git_config: configparser.ConfigParser) -> str:
        """ extract the full git repo name from the config file """
        if not git_config.has_section('remote "origin"'):
            return None
        if not git_config.has_option('remote "origin"', 'url'):
            return None
        url = git_config['remote "origin"']['url']
        return self.__get_repo_name(url)

    def find_local_repo_dir(self) -> bool:
        """ scan upwards from cwd to find local git repo """
        path = self.starting_dir
        path_parts = path.split('/')
        while True:
            dirs = [d for d in os.scandir(path)
                    if d.is_dir() and d.name == '.git']
            if len(dirs) == 1:
                git_dir = dirs[0]
                self.repo_dir = '/'.join(path_parts + [git_dir.name])
                return True
            else:
                path_parts.pop()
                if len(path_parts) == 0:
                    self.repo_dir = None
                    return False
                elif len(path_parts) == 1:
                    path = '/'
                else:
                    path = '/'.join(path_parts)

    def __get_repo_name(self, url: str) -> str:
        """ extract repo name from remote url """
        git_url = urllib.parse.urlparse(url)
        if git_url.scheme.startswith('http'):
            path = git_url.path
            return path[1:path.index('.')]
        elif url.startswith('git@github.com'):
            path = url.split(':')[1]
            start_idx = 1 if path[0] == '/' else 0
            return path[start_idx:path.index('.')]
        return None


class BranchSelector:
    """ allow the user to operate on matching branches """

    def __init__(self, branches: [str], local_repo=True):
        super().__init__()
        self.branches = branches
        self.ask_checkout = local_repo

    def choose_branch(self) -> str:
        """
        present the list of branch selections, returning
        the users's selection
       """
        if len(self.branches) == 0:
            print("\nNo results found\n")
            return None
        for idx, branch in enumerate(self.branches):
            print("{:>4}. {}".format(idx+1, branch))

        if not self.ask_checkout:
            return None

        prompt = "Enter the branch number to checkout or 'X' to exit: "
        while True:
            response = userinput.prompt(prompt=prompt)
            if response.lower() == 'x':
                return None
            try:
                idx = int(response)
                if idx < 1 or idx > len(self.branches):
                    raise ValueError('input out of range')
            except ValueError as ve:
                pass
            else:
                return self.branches[idx-1]

    def checkout_branch(self, branch_name: str):
        """ checkout the passed in branch """
        stash_name = "gfb-{0}".format(datetime.today().isoformat())
        push_cmd = ['git', 'stash', 'push', '-u', '-m', stash_name]
        result = subprocess.run(push_cmd)
        self._success_or_exit(result)
        remote = "origin/{0}".format(branch_name)
        checkout_cmd = ['git', 'checkout', '-b',  branch_name, remote]
        if self._is_branch_local(branch_name):
            checkout_cmd = ['git', 'checkout', branch_name]
        result = subprocess.run(checkout_cmd)
        self._success_or_exit(result)

    def _is_branch_local(self, branch: str) -> bool:
        """ checks if the passed in branch needs fetching """
        cmd = ['git', 'branch', '--list', branch]
        result = subprocess.run(cmd, stdout=subprocess.PIPE,
                                encoding=locale.getpreferredencoding())
        self._success_or_exit(result)
        lines = io.StringIO(result.stdout).readlines()
        return len(([l.strip() for l in lines])) == 1

    def _success_or_exit(self, result: subprocess.CompletedProcess):
        """ exit if the subprocess return code is non-zero """
        if result.returncode != 0:
            print(result.stderr)
            sys.exit(result.returncode)
