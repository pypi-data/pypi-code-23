import os
from os.path import exists, isdir
import subprocess
import logging
from collections import OrderedDict
from datetime import datetime


logging.basicConfig(level=logging.INFO)


class GitRepoNotClean(BaseException):
    pass


class GitCommitNotAvailable(BaseException):
    pass


class GitRemotesAmbiguous(BaseException):
    pass


class EnforceStateError(BaseException):
    pass


def _maintain_curdir(func):
    """ Decorator that guarantees that a function does not change the current working directory. """
    def wrapper(*args, **kwargs):
        cwd = os.getcwd()
        result = func(*args, **kwargs)
        os.chdir(cwd)
        return result
    return wrapper


def get_subprocess_stdout(*args, **kwargs):
    proc = subprocess.Popen(*args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
    out = proc.communicate()[0]
    return out


def get_subprocess_stdout_return_code(*args, **kwargs):
    proc = subprocess.Popen(*args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
    out = proc.communicate()[0]
    return_code = proc.returncode
    return out, return_code


@_maintain_curdir
def is_git_workdir_clean(path):
    """ Return True if the git repository at the specified path is clean, False otherwise """
    os.chdir(path)
    status = get_subprocess_stdout(['git', 'status', '--porcelain'])
    return status == ""


@_maintain_curdir
def get_git_revision_hash(path):
    os.chdir(path)
    return get_subprocess_stdout(['git', 'rev-parse', 'HEAD']).strip()


@_maintain_curdir
def get_git_revision_message(path, revision_hash):
    os.chdir(path)
    return get_subprocess_stdout(['git', 'show', '-s', '--format=%B', revision_hash]).strip()


@_maintain_curdir
def get_git_revision_message_summary(path, revision_hash):
    os.chdir(path)
    return get_subprocess_stdout(['git', 'show', '-s', '--format=%s', revision_hash]).strip()


@_maintain_curdir
def does_commit_exist(path, revision_hash):
    os.chdir(path)
    out = get_subprocess_stdout(['git', 'rev-parse', '--quiet', '--verify', '{}^{{commit}}'.format(revision_hash)]).strip()
    return not out == ""


@_maintain_curdir
def get_git_remote_and_url(path, default_remote="origin"):
    os.chdir(path)
    remote_listings = get_subprocess_stdout(['git', 'remote']).strip().split('\n')
    if len(remote_listings) == 1:
        remote_name = remote_listings[0]
    else:
        if default_remote in remote_listings:
            remote_name = default_remote
        else:
            raise GitRemotesAmbiguous("{} has multiple remotes, none are default {}".format(path, default_remote))

    remote_listings = get_subprocess_stdout(['git', 'remote', '-v']).strip().split('\n')
    for listing in remote_listings:
        name, url, direction = listing.split()
        if name == remote_name and "fetch" in direction:
            return remote_name, url
    assert False  # should never get here


@_maintain_curdir
def checkout_git_commit(path, commit_hash, remote_name):
    if not is_git_workdir_clean(path):
        raise GitRepoNotClean("{} has uncommitted changes.  Cannot checkout commit.".format(path))
    original_hash = get_git_revision_hash(path)
    if original_hash == commit_hash:
        return
    os.chdir(path)

    if not does_commit_exist(path, commit_hash):
        get_subprocess_stdout(['git', 'fetch', '--prune', remote_name])

    # Attempt to stay on master branch if possible, since that is the most common use case
    #   not worth trying to stay on other branches, but master is nice to maintain rather than detached HEAD
    remote_master = remote_name + "/master"
    if does_commit_exist(path, remote_master) and does_commit_exist(path, 'master'):
        # check if desired commit is in history of <remote>/master
        out, return_code = get_subprocess_stdout_return_code(['git', 'rev-list', '{}/master..{}'.format(remote_name, commit_hash)])
        if return_code:
            raise GitCommitNotAvailable("{} does not have commit {:8}".format(path, commit_hash))
        if out == "":
            # commit is in history of <remote>/master
            get_subprocess_stdout(['git', 'checkout', 'master'])
            get_subprocess_stdout(['git', 'reset', '--hard', commit_hash])
        else:
            get_subprocess_stdout(['git', 'checkout', commit_hash])
    else:
        get_subprocess_stdout(['git', 'checkout', commit_hash])

    if commit_hash != get_git_revision_hash(path):
        raise GitCommitNotAvailable("{} does not have commit {:8}".format(path, commit_hash))

    logging.info(" Repo {}:".format(path))
    logging.info("    Was at {}".format(original_hash))
    logging.info("    Now at {}".format(commit_hash))


@_maintain_curdir
def clone_git_repo(path, url, remote_name='origin'):
    parent_path = os.path.dirname(path)
    basename = os.path.basename(path)
    try:
        os.mkdir(parent_path)
    except OSError as e:
        if not e.errno == os.errno.EEXIST:
            raise e
    os.chdir(parent_path)
    logging.info(" Cloning {} from {} ...".format(path, url))
    result = get_subprocess_stdout(['git', 'clone', '--origin', remote_name, url, basename])
    if "fatal" in result:
        return False
    logging.info(" Cloned {} from {}".format(path, url))
    return True


def find_git_repos(dirpath, max_depth=None, ignore=None, select=None):
    """
    Find all git repositories under the given directory.

    :param dirpath:  path of directory to search (absolute or relative)
    :param max_depth: number of levels, starting with dirpath, to search (0 --> [], 1 --> [dirpath], ...)
                      if max_depth=None, no limit to depth of search
    :param ignore: list of directory names (or relative paths) to ignore at any level of search
    :param select: list of directory names to use *only* on the first level of search
    :return: list of pathnames of git repositories
    """
    if max_depth == 0:
        return []

    if ignore is None:
        ignore = []

    repos = []
    subpaths = []
    is_repo = False

    for name in os.listdir(dirpath):
        subpath = os.path.join(dirpath, name)
        if name in ignore or subpath in ignore:
            continue
        if select is not None and name not in select and subpath not in select:
            continue
        if os.path.isdir(subpath):
            if name == ".git":
                is_repo = True
                break
            else:
                subpaths.append(subpath)

    if is_repo:
        repos.append(dirpath)
    else:
        max_depth = None if max_depth is None else max_depth - 1
        for subpath in subpaths:
            subpath_repos = find_git_repos(subpath, max_depth=max_depth, ignore=ignore, select=None)
            repos.extend(subpath_repos)
    return repos


def capture_single_repo_state(repo_path, default_remote='origin'):
    if not is_git_workdir_clean(repo_path):
        raise GitRepoNotClean("{} has uncommitted changes.  State cannot be captured.".format(repo_path))
    commit = get_git_revision_hash(repo_path)
    message = get_git_revision_message_summary(repo_path, commit)
    remote, url = get_git_remote_and_url(repo_path, default_remote=default_remote)
    state_dict = OrderedDict()
    state_dict["commit"] = commit
    state_dict["message"] = message
    state_dict["remote"] = remote
    state_dict["url"] = url
    return state_dict


def capture_state(dirpath, version=None, description=None, max_depth=5, ignore=None, select=None):
    """
    Creates a state dict reflecting the current state of all repos in the specified directory.

    Will raise a GitRepoNotClean exception if any repo has uncommitted work.

    Returns dictionary of the following format:

    { "version": "x.xx.xx",
      "description":  "that demo we did that one time",
      "repos": {
        "folder1/folder2": {
          "remote": "origin",
          "url": "example.com/myrepo.git"
          "commit": "358a5c7e8a39ded530e4a762c4e66c99dced4d6f",
          "message": "this was a great commit"
        },
        ...
      }
    }

    :param dirpath:  path of directory to search (absolute or relative)
    :param version:  version number to record in the state dict
    :param description:  optional description to record in the state dict
    :param max_depth: number of levels, starting with dirpath, to search (0 --> [], 1 --> [dirpath], ...)
                      if max_depth=None, no limit to depth of search (could take a very long time)
    :param ignore: list of directory names (or relative paths) to ignore at any level of search
    :param select: list of directory names to use *only* on the first level of search
    :return: dictionary
    """
    repos = find_git_repos(dirpath, max_depth=max_depth, ignore=ignore, select=select)
    repos.sort()

    repo_dict = OrderedDict()
    for repo in repos:
        key = repo.partition(dirpath)[2].strip('/')  # portion of repo path below dirname, no leading or trailing '/'
        repo_dict[key] = capture_single_repo_state(repo)

    result = OrderedDict()
    if version is not None:
        result["version"] = version
    if description is not None:
        result['description'] = description
    result["date"] = str(datetime.now().date())
    result["base_directory"] = os.path.abspath(dirpath)
    result["repos"] = repo_dict
    return result


def verify_state_can_apply(dirname, state):

    if "repos" not in state.keys():
        logging.error('Bad state file: "repos" must be top-level key')
        return False

    repo_dict = state["repos"]

    # collect errors if any path is a file, or is a non-empty directory that is not a git repo,
    #   or is a git repo with the wrong URL
    errors = []
    for path in repo_dict.keys():
        fullpath = os.path.abspath(os.path.join(dirname, path))
        if exists(fullpath):
            if not isdir(fullpath):
                errors.append("{} is not a directory".format(fullpath))
                continue
            if os.listdir(fullpath):
                if not exists(os.path.join(fullpath, ".git")):
                    errors.append("{} is not a git repository".format(fullpath))
                    continue
                defined_remote = repo_dict[path]["remote"]
                defined_url = repo_dict[path]["url"]

                try:
                    remote_name, url = get_git_remote_and_url(fullpath, default_remote=defined_remote)
                except GitRemotesAmbiguous:
                    errors.append("{} does not have the specified remote repository {}".format(path, defined_remote))
                    continue
                except Exception as e:
                    errors.append("{} had a problem.  Is it a git repo?  Are you SURE??\n  Exception: {}".format(path, e.message))
                    continue

                if url.lower() != defined_url.lower():
                    errors.append("{} has the wrong url for remote {}:".format(path, remote_name))
                    errors.append("  Expected: {}".format(defined_url))
                    errors.append("  Found:    {}".format(url))
                    continue

                if not is_git_workdir_clean(fullpath):
                    errors.append("{} has uncommitted changes.".format(path))
                    continue

    for error in errors:
        logging.error(error)

    return len(errors) == 0


def enforce_state(dirname, state):
    """
    Checks out all commits specified by the given base directory and state dict.

    Will fail if any required repository has uncommitted work.

    State dict must be a dictionary of this format:

    { "version": "x.xx.xx",
      "description":  "that demo we did that one time",
      "repos": {
        "folder1/folder2": {
          "remote": "origin",
          "url": "example.com/myrepo.git"
          "commit": "358a5c7e8a39ded530e4a762c4e66c99dced4d6f",
          "message": "this was a great commit"
        },
        ...
      }
    }

    """

    if not verify_state_can_apply(dirname, state):
        raise EnforceStateError("Could not enforce state")
    else:
        errors = []
        for path in state["repos"].keys():
            path_dict = state["repos"][path]
            fullpath = os.path.abspath(os.path.join(dirname, path))

            defined_remote = path_dict["remote"]
            defined_url = path_dict["url"]

            if not exists(fullpath):
                success = clone_git_repo(fullpath, path_dict["url"], remote_name=path_dict["remote"])
                if not success:
                    errors.append("Could not clone repo {} at url {}".format(path, path_dict["url"]))
                    continue

                try:
                    remote_name, url = get_git_remote_and_url(fullpath, default_remote=defined_remote)
                except GitRemotesAmbiguous as _:
                    errors.append("{} does not have the specified remote ({})".format(path, defined_remote))
                    continue
                if remote_name != defined_remote:
                    errors.append("{} cloned incorrectly -- remote should be {}".format(path, defined_remote))
                    continue
                if url.lower() != defined_url.lower():
                    errors.append("{} cloned incorrectly -- URL should be {}".format(path, defined_url))
                    continue

            try:
                remote_name, _ = get_git_remote_and_url(fullpath, default_remote=defined_remote)
                checkout_git_commit(fullpath, path_dict["commit"], remote_name)
            except (GitCommitNotAvailable, GitRepoNotClean) as e:
                errors.append(e.message)
                continue

        for error in errors:
            logging.error(error)

        if errors:
            raise EnforceStateError("Could not enforce state")


def split_with_bash_space_escapes(s):
    """ Splits a string by spaces but keeps together substrings separated by a backslash-escaped space """
    i = s.split().__iter__()
    output = []
    item = ""
    while True:
        try:
            item += i.next()
            if item.endswith('\\'):
                item = item.rstrip('\\') + ' '
            else:
                output.append(item)
                item = ""
        except StopIteration as _:
            break
    return output
