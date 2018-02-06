import hashlib
import logging
import re
import tempfile
import uuid
from os import path, remove
from shutil import copyfile

from six.moves.urllib import parse


class GitError(Exception):
    pass


class GitExpando(object):
    pass


def _append_commit_link(remote_template):
    x = parse.urlparse(remote_template)
    if x.hostname is not None:
        remote_template += '/commit/{}' if x.hostname.lower() == 'github.com' else '/commits/{}'
    return remote_template


def __remote_to_template(remote_url):
    remote_template = remote_url
    if '@' in remote_template:
        remote_template = 'https://' + (remote_url.split('@')[1].strip()).replace(':', '/')
    remote_template = remote_template if not remote_url.lower().endswith('.git') else remote_template[:-4]
    return _append_commit_link(remote_template)


def __fill_repo(repo, res=GitExpando()):
    res.repo = repo
    res.git_version = repo.git.version()
    res.remote_name = None
    res.remote_url = None
    res.has_head = repo.head.is_valid()
    res._remote_template = None
    if len(repo.remotes) > 0:
        remote = list(repo.remotes)[0]
        res.remote_name = remote.name
        res.remote_url = remote.url
        res._remote_template = __remote_to_template(remote.url)
    res.branch = repo.active_branch
    res.head_sha = res.repo.head.object.hexsha if res.has_head else None

    res.head_sha_url = res._remote_template.format(res.head_sha) if res._remote_template else res.head_sha
    res.is_clean = repo.git.status(porcelain=True).strip() == ''
    return res


def _export_commit(commit):
    return {'author': commit.author.name,
            'email': commit.author.email,
            'date': commit.authored_datetime.isoformat()}


def import_git():
    try:
        import git
        return git
    except ImportError:
        logging.warning('Failed to import git')
    raise GitError('Failed to import git')


def get_repo(path_='.', repo=None):
    git = import_git()
    try:
        repo = repo or git.Repo(path_, search_parent_directories=True)
        response = __fill_repo(repo)
        response.export_commit = _export_commit
        response.refresh = lambda: __fill_repo(repo, response)
        return response
    except git.exc.InvalidGitRepositoryError:
        logging.warning('path is not tracked')
        raise GitError('path is not tracked')


class GitRepoSyncer(object):
    @classmethod
    def _sanitize_branch_name(cls, name):
        return re.sub(r'[^a-zA-Z0-9]', "_", name)

    @classmethod
    def try_ex_path(cls, git, repo_path):
        if path.isdir(repo_path):
            try:
                repo = git.Repo(repo_path)
                return repo
            except Exception as ex:
                logging.warning("Failed to init shadow repo at {}, got {}".format(repo_path, str(ex)))
                remove(repo_path)
        return None

    @classmethod
    def _validate_shadow_or_clone(cls, repo_path, shadow_url):

        git = import_git()
        repo = cls.try_ex_path(git, repo_path) or git.Repo.clone_from(shadow_url, repo_path)
        for remote in repo.remotes:
            if remote.name == 'origin' and remote.url != shadow_url:
                raise GitError("Shadow repository at {} has remote other than {} shadow_url configured: {}".format(repo_path, shadow_url, remote.url))

        repo.git.reset(hard=True)
        return repo

    @classmethod
    def clone_shadow_repo(cls, shadow_url, fixed_clone_path=None):
        repo_id = 'missinglink_{}'.format(hashlib.sha256(shadow_url.encode('utf-8')).hexdigest())
        temp_path = fixed_clone_path or path.join(tempfile.gettempdir(), repo_id)
        logging.debug("Clone {} to {}".format(shadow_url, temp_path))
        return cls._validate_shadow_or_clone(temp_path, shadow_url)

    @classmethod
    def _checkout(cls, repo, branch=None):
        if branch in repo.branches:
            repo.git.checkout(branch)
        else:
            repo.git.checkout(b=branch)

    @classmethod
    def _get_changed_files(cls, repo):
        changes = repo.git.status(porcelain=True).strip()
        if len(changes) == 0:
            return []
        files = list(map(lambda x: x.split(' ')[-1].strip(), repo.git.status(porcelain=True).strip().split('\n')))
        return files

    # @classmethod
    # def _is_clean(cls, repo):
    #     return repo.git.status(porcelain=True).strip() == ''

    @classmethod
    def _sync_uncommitted_changes(cls, src, shadow):
        changed_files = cls._get_changed_files(src)
        for file in changed_files:
            src_file = path.join(src.working_dir, file)
            shadow_file = path.join(shadow.working_dir, file)
            if path.exists(src_file):  # the file is present, copy it...
                copyfile(src_file, shadow_file)
            elif path.exists(shadow_file):  # the file is deleted - delete it
                remove(shadow_file)
        if len(changed_files) > 0:
            shadow.git.add('.')
            shadow.index.commit('ML AI: Synced file(s) from {}.Files: \n{}'.format(src.working_dir, '\n'.join(changed_files)))

    @classmethod
    def _merge_to_new_branch(cls, src, shadow, branch_name):

        cls._checkout(shadow, 'dev_null')
        shadow.git.fetch('origin')
        shadow.git.fetch('src')
        cls._checkout(shadow, branch_name)
        if src.head.is_valid():
            shadow.git.merge('src/{}'.format(src.active_branch))
            return True
        return False

    @classmethod
    def _push_to_shadow_remote(cls, shadow):
        if not shadow.head.is_valid():
            shadow.git.commit(m='empty commit', allow_empty=True)
        shadow.remotes['origin'].push('{}:{}'.format(shadow.active_branch, shadow.active_branch))

    @classmethod
    def merge_src_to_shadow(cls, src, shadow, br_tag=None):
        git = import_git()
        if git.Remote(src, 'src') not in shadow.remotes:
            shadow.create_remote('src', src.git_dir)
        br_tag = br_tag or uuid.uuid4().hex[0:5]

        br_name = '{}_{}'.format(br_tag, src.active_branch)
        br_name = 'xp/' + cls._sanitize_branch_name(br_name)
        cls._merge_to_new_branch(src, shadow, br_name)
        cls._sync_uncommitted_changes(src, shadow)
        cls._push_to_shadow_remote(shadow)
        cls._checkout(shadow, 'dev_null')
        return br_name
