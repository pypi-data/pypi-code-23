import subprocess
import tempfile
import errno
from urlparse import urlparse
from program import *


def formaturl(url, format="default"):
    url = "%s" % url
    m = re.match(regex_aos_url, url)
    if m:
        if format == "http":
            url = 'http://%s/%s/%s/%s/%s' % (m.group(2), m.group(4), m.group(5), m.group(6), m.group(7))
        else:
            url = 'https://%s/%s/%s/%s/%s' % (m.group(2), m.group(4), m.group(5), m.group(6), m.group(7))
    else:
        m = re.match(regex_git_url, url)
        if m:
            if format == "ssh":
                url = 'ssh://%s%s/%s.git' % (m.group(2) or 'git@', m.group(6), m.group(7))
            elif format == "http":
                url = 'http://%s%s/%s' % (
                m.group(2) if (m.group(2) and (m.group(5) or m.group(3) != 'git')) else '', m.group(6), m.group(7))
            elif format == "https":
                url = 'https://%s%s/%s%s' % (
                m.group(2) if (m.group(2) and (m.group(5) or m.group(3) != 'git')) else '', m.group(6), m.group(7),
                m.group(8))
        else:
            m = re.match(regex_hg_url, url)
            if m:
                if format == "ssh":
                    url = 'ssh://%s/%s' % (m.group(2), m.group(3))
                elif format == "http":
                    url = 'http://%s/%s' % (m.group(2), m.group(3))
                elif format == "https":
                    url = 'https://%s/%s' % (m.group(2), m.group(3))
    return url


# Handling for multiple version controls
scms = {}


def scm(name):
    def _scm(cls):
        scms[name] = cls()
        return cls

    return _scm


# pylint: disable=no-self-argument, no-method-argument, no-member, no-self-use, unused-argument
@scm('git')
@staticclass
class Git(object):
    name = 'git'
    ignore_file = os.path.join('.git', 'info', 'exclude')

    def isurl(url):
        m_url = re.match(regex_url_ref, url.strip().replace('\\', '/'))
        if m_url and not re.match(regex_build_url, m_url.group(1)) and not re.match(regex_aos_url, m_url.group(1)):
            return re.match(regex_git_url, m_url.group(1))
        else:
            return False

    def init(path=None):
        popen([git_cmd, 'init'] + ([path] if path else []) + ([] if very_verbose else ['-q']))

    def cleanup():
        info("Cleaning up Git index")
        if os.path.exists(os.path.join('.git', 'logs')):
            rmtree_readonly(os.path.join('.git', 'logs'))

    def clone(url, name=None, depth=None, protocol=None):
        popen([git_cmd, 'clone', formaturl(url, protocol), name] + (['--depth', depth] if depth else []) + ['-v'])

    def add(dest):
        info("Adding reference " + dest)
        try:
            popen([git_cmd, 'add', dest] + (['-v'] if very_verbose else []))
        except ProcessException:
            pass

    def remove(dest):
        info("Removing reference " + dest)
        try:
            popen([git_cmd, 'rm', '-f', dest] + ([] if very_verbose else ['-q']))
        except ProcessException:
            pass

    def commit(msg=None):
        popen([git_cmd, 'commit', '-a'] + (['-m', msg] if msg else []) + (
        ['-v'] if very_verbose else ([] if verbose else ['-q'])))

    def publish(all_refs=None):
        if all_refs:
            popen([git_cmd, 'push', '--all'] + (['-v'] if very_verbose else ([] if verbose else ['-q'])))
        else:
            remote = Git.getremote()
            branch = Git.getbranch()
            if remote and branch:
                popen([git_cmd, 'push', remote, branch] + (['-v'] if very_verbose else ([] if verbose else ['-q'])))
            else:
                err = "Unable to publish outgoing changes for \"%s\" in \"%s\".\n" % (
                os.path.basename(os.getcwd()), os.getcwd())
                if not remote:
                    error(err + "The local repository is not associated with a remote one.", 1)
                if not branch:
                    error(err + "Working set is not on a branch.", 1)

    def fetch():
        info("Fetching revisions from remote repository to \"%s\"" % os.path.basename(os.getcwd()))
        popen([git_cmd, 'fetch', '--all', '--tags'] + (['-v'] if very_verbose else ([] if verbose else ['-q'])))

    def discard(clean_files=False):
        info("Discarding local changes in \"%s\"" % os.path.basename(os.getcwd()))
        pquery([git_cmd, 'reset', 'HEAD'] + ([] if very_verbose else ['-q']))  # unmarks files for commit
        pquery([git_cmd, 'checkout', '.'] + ([] if very_verbose else ['-q']))  # undo  modified files
        pquery([git_cmd, 'clean', '-fd'] + (['-x'] if clean_files else []) + (
        ['-q'] if very_verbose else ['-q']))  # cleans up untracked files and folders

    def merge(dest):
        info("Merging \"%s\" with \"%s\"" % (os.path.basename(os.getcwd()), dest))
        popen([git_cmd, 'merge', dest] + (['-v'] if very_verbose else ([] if verbose else ['-q'])))

    def checkout(rev, clean=False):
        if not rev:
            return
        info("Checkout \"%s\" in %s" % (rev, os.path.basename(os.getcwd())))
        branch = None
        refs = Git.getrefs(rev)
        for ref in refs:  # re-associate with a local or remote branch (rev is the same)
            m = re.match(r'^(.*?)\/(.*?)$', ref)
            if m and m.group(2) != "HEAD":  # matches origin/<branch> and isn't HEAD ref
                if not os.path.exists(os.path.join('.git', 'refs', 'heads', m.group(
                        2))):  # okay only if local branch with that name doesn't exist (git will checkout the origin/<branch> in that case)
                    branch = m.group(2)
            elif ref != "HEAD":
                branch = ref  # matches local branch and isn't HEAD ref

            if branch:
                info("Revision \"%s\" matches a branch \"%s\" reference. Re-associating with branch" % (rev, branch))
                popen([git_cmd, 'checkout', branch] + ([] if very_verbose else ['-q']))
                break

        if not branch:
            popen([git_cmd, 'checkout', rev] + (['-f'] if clean else []) + ([] if very_verbose else ['-q']))

    def update(rev=None, clean=False, clean_files=False, is_local=False):
        if not is_local:
            Git.fetch()
        if clean:
            Git.discard(clean_files)
        if rev:
            Git.checkout(rev, clean)
        else:
            remote = Git.getremote()
            branch = Git.getbranch()
            if remote and branch:
                try:
                    Git.merge('%s/%s' % (remote, branch))
                except ProcessException:
                    pass
            else:
                err = "Unable to update \"%s\" in \"%s\"." % (os.path.basename(os.getcwd()), os.getcwd())
                if not remote:
                    info(err + " The local repository is not associated with a remote one.")
                if not branch:
                    info(err + " Working set is not on a branch.")

    def status():
        return pquery([git_cmd, 'status', '-s'] + (['-v'] if very_verbose else []))

    def dirty():
        return pquery([git_cmd, 'status', '-uno', '--porcelain'])

    def untracked():
        return pquery([git_cmd, 'ls-files', '--others', '--exclude-standard']).splitlines()

    def outgoing():
        # Get default remote
        remote = Git.getremote()
        if not remote:
            return -1
        # Get current branch
        branch = Git.getbranch()
        if not branch:
            # Default to "master" in detached mode
            branch = "master"
        try:
            # Check if remote branch exists
            if not pquery([git_cmd, 'rev-parse', '%s/%s' % (remote, branch)]):
                return 1
        except ProcessException:
            return 1
        # Check for outgoing commits for the same remote branch
        return 1 if pquery([git_cmd, 'log', '%s/%s..%s' % (remote, branch, branch)]) else 0

    # Checks whether current working tree is detached
    def isdetached():
        return True if Git.getbranch() == "" else False

    # Finds default remote
    def getremote():
        remote = None
        remotes = Git.getremotes('push')
        for r in remotes:
            remote = r[0]
            # Prefer origin which is Git's default remote when cloning
            if r[0] == "origin":
                break
        return remote

    # Finds all associated remotes for the specified remote type
    def getremotes(rtype='fetch'):
        result = []
        remotes = pquery([git_cmd, 'remote', '-v']).strip().splitlines()
        for remote in remotes:
            remote = re.split(r'\s', remote)
            t = re.sub('[()]', '', remote[2])
            if not rtype or rtype == t:
                result.append([remote[0], remote[1], t])
        return result

    def seturl(url):
        info("Setting url to \"%s\" in %s" % (url, os.getcwd()))
        return pquery([git_cmd, 'remote', 'set-url', 'origin', url]).strip()

    def geturl():
        url = ""
        remotes = Git.getremotes()
        for remote in remotes:
            url = remote[1]
            if remote[0] == "origin":  # Prefer origin URL
                break
        return formaturl(url)

    def getrev():
        return pquery([git_cmd, 'rev-parse', 'HEAD']).strip()

    # Gets current branch or returns empty string if detached
    def getbranch(rev='HEAD'):
        try:
            branch = pquery([git_cmd, 'rev-parse', '--symbolic-full-name', '--abbrev-ref', rev]).strip()
        except ProcessException:
            branch = "master"
        return branch if branch != "HEAD" else ""

    # Finds refs (local or remote branches). Will match rev if specified
    def getrefs(rev=None, ret_rev=False):
        result = []
        lines = pquery([git_cmd, 'show-ref']).strip().splitlines()
        for line in lines:
            m = re.match(r'^(.+)\s+(.+)$', line)
            if m and (not rev or m.group(1).startswith(rev)):
                if re.match(r'refs\/(heads|remotes)\/', m.group(2)):  # exclude tags
                    result.append(m.group(1) if ret_rev else re.sub(r'refs\/(heads|remotes)\/', '', m.group(2)))
        return result

    # Finds branches a rev belongs to
    def revbranches(rev):
        branches = []
        lines = pquery([git_cmd, 'branch', '-a', '--contains'] + ([rev] if rev else [])).strip().splitlines()
        for line in lines:
            if re.match(r'^\*?\s+\((.+)\)$', line):
                continue
            line = re.sub(r'\s+', '', line)
            branches.append(line)
        return branches

    def ignores():
        try:
            ignore_file_parent_directory = os.path.dirname(Git.ignore_file)
            if not os.path.exists(ignore_file_parent_directory):
                os.mkdir(ignore_file_parent_directory)

            with open(Git.ignore_file, 'w') as f:
                f.write('\n'.join(ignores) + '\n')
        except IOError:
            error("Unable to write ignore file in \"%s\"" % os.path.join(os.getcwd(), Git.ignore_file), 1)

    def ignore(dest):
        try:
            with open(Git.ignore_file) as f:
                exists = dest in f.read().splitlines()
        except IOError:
            exists = False

        if not exists:
            try:
                ignore_file_parent_directory = os.path.dirname(Git.ignore_file)
                if not os.path.exists(ignore_file_parent_directory):
                    os.mkdir(ignore_file_parent_directory)

                with open(Git.ignore_file, 'a') as f:
                    f.write(dest.replace("\\", "/") + '\n')
            except IOError:
                error("Unable to write ignore file in \"%s\"" % os.path.join(os.getcwd(), Git.ignore_file), 1)

    def unignore(dest):
        try:
            with open(Git.ignore_file) as f:
                lines = f.read().splitlines()
        except IOError:
            lines = []

        if dest in lines:
            lines.remove(dest)
            try:
                ignore_file_parent_directory = os.path.dirname(Git.ignore_file)
                if not os.path.exists(ignore_file_parent_directory):
                    os.mkdir(ignore_file_parent_directory)

                with open(Git.ignore_file, 'w') as f:
                    f.write('\n'.join(lines) + '\n')
            except IOError:
                error("Unable to write ignore file in \"%s\"" % os.path.join(os.getcwd(), Git.ignore_file), 1)


# Repository object
class Repo(object):
    is_local = False
    is_build = False
    name = None
    path = None
    url = None
    rev = None
    scm = None
    libs = []
    codes = []
    cache = None

    @classmethod
    def fromurl(cls, url, path=None):
        repo = cls()
        m_local = re.match(regex_local_ref, url.strip().replace('\\', '/'))
        m_repo_url = re.match(regex_url_ref, url.strip().replace('\\', '/'))
        m_bld_url = re.match(regex_build_url, url.strip().replace('\\', '/'))
        if m_local:
            repo.name = os.path.basename(path or m_local.group(1))
            repo.path = os.path.abspath(path or os.path.join(os.getcwd(), m_local.group(1)))
            repo.url = m_local.group(1)
            repo.rev = m_local.group(2)
            repo.is_local = True
        elif m_bld_url:
            repo.name = os.path.basename(path or m_bld_url.group(7))
            repo.path = os.path.abspath(path or os.path.join(os.getcwd(), repo.name))
            repo.url = m_bld_url.group(1) + '/builds'
            repo.rev = m_bld_url.group(8)
            repo.is_build = True
        elif m_repo_url:
            repo.name = os.path.basename(path or m_repo_url.group(2)[:-4])
            if repo.name == OS_NAME:
                repo.path = os.path.abspath(os.path.join(Global().get_path(), repo.name))
                Global().set_cfg(AOS_SDK_PATH, repo.path.replace(os.path.sep, '/'))
            else:
                pd = Program(os.getcwd())
                repo.path = os.path.abspath(path or os.path.join(pd.get_cfg(REMOTE_PATH), repo.name))
            repo.url = formaturl(m_repo_url.group(1))
            repo.rev = m_repo_url.group(3)
            if repo.rev and repo.rev != 'master' and not re.match(r'^([a-fA-F0-9]{6,40})$', repo.rev):
                error('Invalid revision (%s)' % repo.rev, -1)
        else:
            error('Invalid repository (%s)' % url.strip(), -1)

        cache_cfg = Global().get_cfg('CACHE', '')
        if cache_repositories and cache_cfg and cache_cfg != 'none' and cache_cfg != 'off' and cache_cfg != 'disabled':
            loc = cache_cfg if (cache_cfg and cache_cfg != 'on' and cache_cfg != 'enabled') else None
            repo.cache = loc or os.path.join(tempfile.gettempdir(), 'aos-repo-cache')

        return repo

    @classmethod
    def fromlib(cls, lib=None):
        with open(lib) as f:
            ref = f.read(200)

        m_local = re.match(regex_local_ref, ref.strip().replace('\\', '/'))
        m_repo_url = re.match(regex_url_ref, ref.strip().replace('\\', '/'))
        m_bld_url = re.match(regex_build_url, ref.strip().replace('\\', '/'))
        if not (m_local or m_bld_url or m_repo_url):
            warning(
                "File \"%s\" in \"%s\" uses a non-standard .comp or .codes file extension, which is not compatible with the aos build tools.\n" % (
                os.path.basename(lib), os.path.split(lib)[0]))
            return False
        else:
            return cls.fromurl(ref, lib[:lib.rfind('.')])

    @classmethod
    def fromcode(cls, code=None):
        with open(code) as f:
            ref = f.read(200)

        m_local = re.match(regex_local_ref, ref.strip().replace('\\', '/'))
        m_repo_url = re.match(regex_url_ref, ref.strip().replace('\\', '/'))
        m_bld_url = re.match(regex_build_url, ref.strip().replace('\\', '/'))
        if not (m_local or m_bld_url or m_repo_url):
            warning(
                "File \"%s\" in \"%s\" uses a non-standard .lib file extension, which is not compatible with the aos build tools.\n" % (
                os.path.basename(code), os.path.split(code)[0]))
            return False
        else:
            return cls.fromurl(ref, code[:code.rfind('.')])

    @classmethod
    def fromrepo(cls, path=None):
        repo = cls()
        if path is None:
            path = Repo.findparent(os.getcwd())
            if path is None:
                error(
                    "Could not find aos program in current path \"%s\".\n"
                    "You can fix this by calling \"aos new .\" or \"aos config root .\" in the root of your program." % os.getcwd())

        repo.path = os.path.abspath(path)
        repo.name = os.path.basename(repo.path)

        cache_cfg = Global().get_cfg('CACHE', '')
        if cache_repositories and cache_cfg and cache_cfg != 'none' and cache_cfg != 'off' and cache_cfg != 'disabled':
            loc = cache_cfg if (cache_cfg and cache_cfg != 'on' and cache_cfg != 'enabled') else None
            repo.cache = loc or os.path.join(tempfile.gettempdir(), 'aos-repo-cache')

        repo.sync()

        if repo.scm is None:
            info(
                "Program \"%s\" in \"%s\" does not use source control management.\n"
                "To fix this you should use \"aos new .\" in the root of your program." % (repo.name, repo.path))

        return repo

    @classmethod
    def isrepo(cls, path=None):
        for name, _ in scms.items():
            if os.path.isdir(os.path.join(path, '.' + name)):
                return True

        return False

    @classmethod
    def findparent(cls, path=None):
        path = os.path.abspath(path or os.getcwd())

        while cd(path):
            if os.path.isfile(os.path.join(path, Cfg.file)) or Repo.isrepo(path):
                return path

            tpath = path
            path = os.path.split(path)[0]
            if tpath == path:
                break

        return None

    @classmethod
    def pathtype(cls, path=None):
        path = os.path.abspath(path or os.getcwd())
        pd = Program(path)
        # depth = 0
        # while cd(path):
        #     tpath = path
        #     path = Repo.findparent(path)
        #     if path:
        #         depth += 1
        #         path = os.path.split(path)[0]
        #         if tpath == path:       # Reached root.
        #             break
        #     else:
        #         break

        return pd.get_cfg(PATH_TYPE) if pd.get_cfg(PATH_TYPE) else "directory"

    @classmethod
    def revtype(cls, rev, ret_rev=False):
        if rev is None or len(rev) == 0:
            return 'latest' + (' revision in the current branch' if ret_rev else '')
        elif re.match(r'^([a-fA-F0-9]{6,40})$', rev) or re.match(r'^([0-9]+)$', rev):
            return 'rev' + (' #' + rev[0:12] if ret_rev else '')
        else:
            return 'branch' + (' ' + rev if ret_rev else '')

    @classmethod
    def isurl(cls, url):
        m = re.match(regex_url_ref, url.strip().replace('\\', '/'))
        return True if m else False

    @property
    def lib(self):
        return self.path + '.' + ('bld' if self.is_build else 'component')

    @property
    def code(self):
        return self.path + '.' + ('bld' if self.is_build else 'codes')

    @property
    def fullurl(self):
        if self.url:
            return (self.url.rstrip('/') + '/' +
                    (('' if self.is_build else '#') +
                     self.rev if self.rev else ''))

    def sync(self):
        self.url = None
        self.rev = None
        if os.path.isdir(self.path):
            try:
                self.scm = self.getscm()
                if self.scm and self.scm.name == 'bld':
                    self.is_build = True
            except ProcessException:
                pass

            try:
                self.url = self.geturl()
                if not self.url:
                    self.is_local = True
                    ppath = self.findparent(os.path.split(self.path)[0])
                    self.url = relpath(ppath, self.path).replace("\\", "/") if ppath else os.path.basename(self.path)
            except ProcessException:
                pass

            try:
                self.rev = self.getrev()
            except ProcessException:
                pass

            try:
                self.libs = list(self.getlibs())
            except ProcessException:
                pass

            try:
                self.codes = list(self.getcodes())
            except ProcessException:
                pass

    def getscm(self):
        for name, scm in scms.items():
            if os.path.isdir(os.path.join(self.path, '.' + name)):
                return scm

    # Pass backend SCM commands and parameters if SCM exists
    def __wrap_scm(self, method):
        def __scm_call(*args, **kwargs):
            if self.scm and hasattr(self.scm, method) and callable(getattr(self.scm, method)):
                with cd(self.path):
                    return getattr(self.scm, method)(*args, **kwargs)

        return __scm_call

    def __getattr__(self, attr):
        if attr in ['geturl', 'getrev', 'add', 'remove', 'ignores', 'ignore', 'unignore',
                    'status', 'dirty', 'commit', 'outgoing', 'publish', 'checkout', 'update',
                    'isdetached']:
            wrapper = self.__wrap_scm(attr)
            self.__dict__[attr] = wrapper
            return wrapper
        else:
            raise AttributeError("Repo instance doesn't have attribute '%s'" % attr)

    def remove(self, dest, *args, **kwargs):
        if os.path.isfile(dest):
            try:
                os.remove(dest)
            except OSError:
                pass
        return self.scm.remove(dest, *args, **kwargs)

    def clone(self, url, path, rev=None, depth=None, protocol=None, **kwargs):
        # Sorted so repositories that match urls are attempted first
        sorted_scms = [(scm.isurl(url), scm) for scm in scms.values()]
        sorted_scms = filter(lambda (m, _): m, sorted_scms)

        for _, scm in sorted_scms:
            main = True
            cache = self.get_cache(url)

            # Try to clone with cache ref first
            if cache and not os.path.isdir(path):
                info("Found matching cached repository in \"%s\"" % cache)
                try:
                    if os.path.split(path)[0] and not os.path.isdir(os.path.split(path)[0]):
                        os.makedirs(os.path.split(path)[0])

                    info("Carbon copy from \"%s\" to \"%s\"" % (cache, path))
                    shutil.copytree(cache, path)

                    with cd(path):
                        scm.seturl(formaturl(url, protocol))
                        scm.cleanup()
                        info("Update cached copy from remote repository")
                        scm.update(rev, True)
                        main = False
                except (ProcessException, IOError):
                    info("Discarding cached repository")
                    if os.path.isdir(path):
                        rmtree_readonly(path)

            # Main clone routine if the clone with cache ref failed (might occur if cache ref is dirty)
            if main:
                try:
                    scm.clone(url, path, depth=depth, protocol=protocol, **kwargs)
                except ProcessException:
                    if os.path.isdir(path):
                        rmtree_readonly(path)
                    continue

            self.scm = scm
            self.url = url
            self.path = os.path.abspath(path)
            self.ignores()
            self.set_cache(url)
            return True

        return False

    def getlibs(self):
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files[:] = [f for f in files if not f.startswith('.')]

            for f in files:
                if f.endswith('.component'):
                    repo = Repo.fromlib(os.path.join(root, f))
                    if repo:
                        yield repo
                    if f[:f.rfind('.')] in dirs:
                        dirs.remove(f[:f.rfind('.')])

    def getcodes(self):
        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            files[:] = [f for f in files if not f.startswith('.')]

            for f in files:
                if f.endswith('.codes'):
                    repo = Repo.fromcode(os.path.join(root, f))
                    if repo:
                        yield repo
                    if f[:f.rfind('.')] in dirs:
                        dirs.remove(f[:f.rfind('.')])

    def write(self):
        if os.path.isfile(self.lib):
            with open(self.lib) as f:
                lib_repo = Repo.fromurl(f.read().strip())
                if (formaturl(lib_repo.url, 'https') == formaturl(self.url,
                                                                  'https')  # match URLs in common format (https)
                        and (
                                lib_repo.rev == self.rev  # match revs, even if rev is None (valid for repos with no revisions)
                                or (lib_repo.rev and self.rev
                                    and lib_repo.rev == self.rev[
                                                        0:len(lib_repo.rev)]))):  # match long and short rev formats
                    # print self.name, 'unmodified'
                    return

        ref = (formaturl(self.url, 'https').rstrip('/') + '/' +
               (('' if self.is_build else '#') +
                self.rev if self.rev else ''))
        action("Update reference \"%s\" -> \"%s\"" % (
        relpath(cwd_root, self.path) if cwd_root != self.path else self.name, ref))
        with open(self.lib, 'wb') as f:
            f.write(ref + '\n')

    def write_codes(self):
        if os.path.isfile(self.code):
            with open(self.code) as f:
                lib_repo = Repo.fromurl(f.read().strip())
                if (formaturl(lib_repo.url, 'ssh') == formaturl(self.url, 'ssh')  # match URLs in common format (ssh)
                        and (
                                lib_repo.rev == self.rev  # match revs, even if rev is None (valid for repos with no revisions)
                                or (lib_repo.rev and self.rev
                                    and lib_repo.rev == self.rev[
                                                        0:len(lib_repo.rev)]))):  # match long and short rev formats
                    # print self.name, 'unmodified'
                    return

        ref = (formaturl(self.url, 'ssh').rstrip('/') + '/' +
               (('' if self.is_build else '#') +
                self.rev if self.rev else ''))
        action("Update reference \"%s\" -> \"%s\"" % (
        relpath(cwd_root, self.path) if cwd_root != self.path else self.name, ref))
        with open(self.code, 'wb') as f:
            f.write(ref + '\n')

    def rm_untracked(self):
        untracked = self.scm.untracked()
        for f in untracked:
            if re.match(r'(.+)\.(lib|bld)$', f) and os.path.isfile(f):
                action("Remove untracked library reference \"%s\"" % f)
                os.remove(f)

    def get_cache(self, url):
        up = urlparse(formaturl(url, 'https'))
        if self.cache and up and up.netloc and os.path.isdir(
                os.path.join(self.cache, up.netloc, re.sub(r'^/', '', up.path))):
            return os.path.join(self.cache, up.netloc, re.sub(r'^/', '', up.path))

    def set_cache(self, url):
        up = urlparse(formaturl(url, 'https'))
        if self.cache and up and up.netloc and os.path.isdir(self.path):
            try:
                cpath = os.path.join(self.cache, up.netloc, re.sub(r'^/', '', up.path))
                if not os.path.isdir(cpath):
                    os.makedirs(cpath)

                scm_dir = '.' + self.scm.name
                if os.path.isdir(os.path.join(cpath, scm_dir)):
                    rmtree_readonly(os.path.join(cpath, scm_dir))
                shutil.copytree(os.path.join(self.path, scm_dir), os.path.join(cpath, scm_dir))
            except Exception:
                warning("Unable to cache \"%s\" to \"%s\"" % (self.path, cpath))
        return False

    def can_update(self, clean, clean_deps):
        err = None
        if (self.is_local or self.url is None) and not clean_deps:
            err = (
                    "Preserving local library \"%s\" in \"%s\".\nPlease publish this library to a remote URL to be able to restore it at any time."
                    "You can use --ignore switch to ignore all local libraries and update only the published ones.\n"
                    "You can also use --clean-deps switch to remove all local libraries. WARNING: This action cannot be undone." % (
                    self.name, self.path))
        elif not clean and self.dirty():
            err = (
                    "Uncommitted changes in \"%s\" in \"%s\".\nPlease discard or stash them first and then retry update.\n"
                    "You can also use --clean switch to discard all uncommitted changes. WARNING: This action cannot be undone." % (
                    self.name, self.path))
        elif not clean_deps and self.outgoing():
            err = (
                    "Unpublished changes in \"%s\" in \"%s\".\nPlease publish them first using the \"publish\" command.\n"
                    "You can also use --clean-deps to discard all local commits and replace the library with the one included in this revision. WARNING: This action cannot be undone." % (
                    self.name, self.path))

        return (False, err) if err else (True, "OK")

    def check_repo(self, show_warning=None):
        err = None
        if not os.path.isdir(self.path):
            err = (
                    "Library reference \"%s\" points to non-existing library in \"%s\"\n"
                    "You can use \"aos deploy\" to import the missing libraries.\n"
                    "You can also use \"aos sync\" to synchronize and remove all invalid library references." % (
                    os.path.basename(self.lib), self.path))
        elif not self.isrepo(self.path):
            err = (
                    "Library reference \"%s\" points to a folder \"%s\", which is not a valid repository.\n"
                    "You can remove the conflicting folder manually and use \"aos deploy\" to import the missing libraries\n"
                    "You can also remove library reference \"%s\" and use \"aos sync\" again." % (
                    os.path.basename(self.lib), self.path, self.lib))

        if err:
            if show_warning:
                warning(err)
            else:
                error(err, 1)
            return False
        return True
