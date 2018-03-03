"""git support
"""

# pylint: disable=C0103
#                          Invalid name for type variable

# test like this:
# cd test/src
# git init
# git add *
# git commit -a -m 'initial release'
# git tag 1.1
# cd ..
# git clone src clone
import os.path
import re
import sumolib.system
import sumolib.utils

__version__="3.3" #VERSION#

assert __version__==sumolib.system.__version__
assert __version__==sumolib.utils.__version__

# -----------------------------------------------
# Repo class
# -----------------------------------------------

def assert_git():
    """ensure that git exists."""
    sumolib.system.test_program("git")

class Repo(object):
    """represent a git repository."""
    # pylint: disable=R0902
    #                          Too many instance attributes
    rx_repo=re.compile(r'^\s*Push\s+URL:\s*(.*)$')
    rx_tag=re.compile(r'^(.*)\s+([0-9]+):([a-z0-9]+)$')
    def _find_remote(self, patcher):
        """find and contact the remote repository.

        Note that "git remote show origin" tries to contact the remote
        repository and fails if the repository cannot be reached.
        """
        assert_git()
        try:
            (reply,_)= sumolib.system.system(\
                             "git -C %s remote show origin" % self.directory,
                             True, False,
                             self.verbose, self.dry_run)
        except IOError, _:
            # remote repo could not be contacted.
            return
        for line in reply.splitlines():
            line= line.strip()
            # look for "Push" url:
            m= self.rx_repo.search(line)
            if m is not None:
                repo= m.group(1)
                if patcher is not None:
                    repo= patcher.apply(repo)
                return repo
        return
    def _local_changes(self, matcher):
        """returns True if there are uncomitted changes.

        Does basically "git status". All lines that match the matcher
        object are ignored. The matcher parameter may be <None>.
        """
        assert_git()
        cmd= "git -C %s status --porcelain" % self.directory
        (reply,_)= sumolib.system.system(cmd, True, False,
                                         self.verbose, self.dry_run)
        changes= False
        for line in reply.splitlines():
            line= line.rstrip()
            if line.startswith("?? "):
                # ignore unknown files
                continue
            line= line[3:]
            if matcher is not None:
                # ignore if line matches:
                if matcher.search(line):
                    continue
            # any line remaining means that there were changes:
            changes= True
            break
        return changes
    def _local_patches(self):
        """returns True when there are unpushed patches.

        """
        if self.remote_url is None:
            raise AssertionError("cannot compute local patches without "
                                 "a reachable remote repository.")
        assert_git()
        cmd= "git -C %s log origin..HEAD" % self.directory
        (reply,_)= sumolib.system.system(cmd,
                                         True, False,
                                         self.verbose, self.dry_run)

        changes= False
        for line in reply.splitlines():
            line= line.strip()
            if line.startswith("commit"):
                changes= True
                break
        return changes
    def _current_revision(self):
        """returns the revision of the working copy.

        This returns the shortened hash key, the hash key has 7 characters in
        this case.

        Note that a tag at the top has itself a revision hash key, so if a tag
        is on top this will return the hash key of the tag, not of the newest
        patch.
        """
        assert_git()
        (reply,_)= sumolib.system.system(\
                "git -C %s rev-parse --short HEAD" % self.directory,
                True, False,
                self.verbose, self.dry_run)
        # for uncomitted changes, the revision ends with a "+":
        return reply.splitlines()[0].strip()
    def _tag_on_top(self):
        """returns True when a tag identifies the working copy.

        Returns the found tag or None if no tag on top was found.
        """
        curr_rev= self.current_revision
        assert_git()
        cmd= "git -C %s tag --points-at %s" % (self.directory, curr_rev)
        (reply,_)= sumolib.system.system(cmd, True, False,
                                         self.verbose, self.dry_run)
        tags= []
        for line in reply.splitlines():
            line= line.strip()
            if line: # if line is not empty:
                # there may be more than one tag:
                tags.append(line)
        if not tags:
            # no tags found:
            return
        # return the first tag of the sorted list:
        tags.sort()
        return tags[0]
    def _hint(self, name):
        """return the value of hint "name"."""
        return self.hints.get(name)
    def __init__(self, directory, hints, verbose, dry_run):
        """initialize.

        Hints must be a dictionary. This gives hints how the directory should
        be scanned. Currently we know these keys in the dictionary:

        "ignore changes": sumolib.utils.RegexpMatcher
            All local changes in files that match the RegexpMatcher object are
            ignored. By this we can get the remote repository and tag from a
            directory although there are uncomitted changes. A common
            application is to ignore changes in file "configure/RELEASE".
        "dir patcher": sumolib.utils.RegexpPatcher
            This patcher is applied to the directory that is stored in the
            object.
        "url patcher": sumolib.utils.RegexpPatcher
            This patcher is applied to the URL that is stored in the object.
        "force local": bool
            If this is True, the returns repository object does not contain a
            remote repoistory url even if there was one.
        """
        self.hints= dict(hints) # shallow copy
        patcher= self._hint("dir patcher")
        if patcher is not None:
            directory= patcher.apply(directory)
        self.directory= directory
        self.verbose= verbose
        self.dry_run= dry_run
        self.local_changes= None
        self.remote_url= None
        self.local_patches= None
        self.tag_on_top= None
        self.current_revision= None
        if self.directory is None:
            return
        self.current_revision= self._current_revision()
        self.local_changes= \
                self._local_changes(self._hint("ignore changes"))
        self.remote_url= self._find_remote(self._hint("url patcher"))
        if self.remote_url is not None:
            self.local_patches= self._local_patches()
        if self._hint("force local"):
            self.remote_url= None
        self.tag_on_top= self._tag_on_top() # uses self._current_revision
    def __str__(self):
        """return a human readable representation."""
        lines= [ "git repo",
                 "dir: %s" % repr(self.directory),
                 "current revision: %s" % repr(self.current_revision),
                 "local_changes: %s" % repr(self.local_changes),
                 "remote url: %s" % repr(self.remote_url),
                 "local patches: %s" % repr(self.local_patches),
                 "tag on top: %s" % repr(self.tag_on_top) ]
        return "\n".join(lines)
    @staticmethod
    def name():
        """return the repo type name."""
        # pylint: disable=R0201
        #                          Method could be a function
        return "git"
    @staticmethod
    def distributed_repo():
        """True for distributed version controls systems, False otherwise."""
        return True
    def get_tag_on_top(self):
        """return the "tag on top" property."""
        return self.tag_on_top
    def get_remote_url(self):
        """return the "remote_url" property, this may be None."""
        return self.remote_url
    def get_revision(self):
        """return the current revision."""
        return self.current_revision
    @classmethod
    def scan_dir(cls, directory, hints, verbose, dry_run):
        """return a Repo object if a git repo was found.

        This function returns <None> if no working repo was found.

        If bool(hints["write check"]) is True, return <None> if the repository
        directory is not writable.

        For parameter "hints" see comment at __init__.
        """
        # pylint: disable=R0201
        #                          Method could be a function
        repodir= os.path.join(directory,".git")
        if not os.path.exists(repodir):
            return
        if hints.get("write check"):
            if not os.access(repodir, os.W_OK):
                return
        obj= cls(directory, hints, verbose, dry_run)
        return obj
    def source_spec(self):
        """return a complete source specification (for SourceSpec class).
        """
        if self.directory is None:
            raise AssertionError("cannot create source_spec from "
                                 "empty object")
        if self.local_changes:
            raise AssertionError("cannot create spec from repo '%s' with "
                                 "unrecorded changes" % self.directory)
        d= {"type":"git"}
        if self.tag_on_top is not None:
            d["tag"]= self.tag_on_top
        else:
            d["rev"]= self.current_revision

        if self.remote_url is None:
            d["url"]= self.directory
        elif self.local_patches:
            d["url"]= self.directory
        else:
            d["url"]= self.remote_url
        return d
    @staticmethod
    def checkout(spec, destdir, _, verbose, dry_run):
        """spec must be a dictionary with "url" and "tag" (optional).
        """
        url= spec.get("url")
        if url is None:
            raise ValueError("spec '%s' has no url" % repr(spec))
        assert_git()
        cmd= "git clone -q %s %s" % (url, destdir)
        tag= spec.get("tag")
        rev= spec.get("rev")
        if tag and rev:
            raise ValueError("you cannot specify both, tag '%s' and "
                             "revision '%s'" % (tag,rev))
        sumolib.system.system(cmd, False, False, verbose, dry_run)
        # the following to avoid warning if we use "git push" in this
        # repository:
        cmd="git -C %s config push.default simple" % destdir
        sumolib.system.system(cmd, False, False,
                              verbose,
                              dry_run)
        if (tag is None) and (rev is None):
            return
        if tag is not None:
            cmd="git checkout %s" % tag
        elif rev is not None:
            cmd="git checkout %s" % rev
        else:
            cmd="git checkout master"
        cmd+=" -q"
        cwd= sumolib.utils.changedir(destdir)
        try:
            sumolib.system.system(cmd, False, False, verbose, dry_run)
        finally:
            sumolib.utils.changedir(cwd)
    def commit(self, logmessage):
        """commit changes."""
        if not logmessage:
            m_param=""
        else:
            m_param="-m '%s'" % logmessage
        assert_git()
        cmd="git -C %s commit -a -q %s" % (self.directory, m_param)
        sumolib.system.system(cmd,
                              False, False,
                              self.verbose, self.dry_run)
        self.local_changes= False
    def push(self):
        """push all changes."""
        if self.remote_url is None:
            raise AssertionError("cannot push local patches without "
                                 "a reachable remote repository.")
        assert_git()
        cmd="git -C %s push -q %s" % (self.directory, self.remote_url)
        sumolib.system.system(cmd,
                              True, False,
                              self.verbose, self.dry_run)
    def pull_merge(self):
        """pull changes and try to merge."""
        if self.remote_url is None:
            raise AssertionError("cannot pull patches without "
                                 "a reachable remote repository.")
        assert_git()
        cmd="git -C %s fetch %s -q" % (self.directory, self.remote_url)
        sumolib.system.system(cmd,
                              True, False,
                              self.verbose, self.dry_run)

        cmd="git -C %s merge FETCH_HEAD -q" % self.directory

        (_,_,rc)= sumolib.system.system_rc(cmd,
                                           True, False,
                                           self.verbose, self.dry_run)
        if rc:
            msg="error, 'git pull' failed"
            raise IOError(msg)

# git fetch <remote> -q   --> works!
