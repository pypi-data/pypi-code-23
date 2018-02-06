#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x4eb79462

# Compiled with Coconut version 1.3.1-post_dev17 [Dead Parrot]

# Coconut Header: -------------------------------------------------------------

import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_NamedTuple, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_pipe, _coconut_star_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: -----------------------------------------------------------

# Copyright Arne Bachmann
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Standard modules
import codecs  # line 5
import collections  # line 5
import fnmatch  # line 5
import json  # line 5
import logging  # line 5
import mimetypes  # line 5
import os  # line 5
import shutil  # line 5
sys = _coconut_sys  # line 5
import time  # line 5
try:  # line 6
    from typing import Any  # only required for mypy  # line 7
    from typing import Dict  # only required for mypy  # line 7
    from typing import FrozenSet  # only required for mypy  # line 7
    from typing import IO  # only required for mypy  # line 7
    from typing import Iterator  # only required for mypy  # line 7
    from typing import List  # only required for mypy  # line 7
    from typing import Set  # only required for mypy  # line 7
    from typing import Tuple  # only required for mypy  # line 7
    from typing import Type  # only required for mypy  # line 7
    from typing import Union  # only required for mypy  # line 7
except:  # typing not available (prior Python 3.5)  # line 8
    pass  # typing not available (prior Python 3.5)  # line 8
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # line 9
try:  # line 10
    from sos import version  # line 11
    from sos.utility import *  # line 12
except:  # line 13
    import version  # line 14
    from utility import *  # line 15

# External dependencies
import configr  # optional dependency  # line 18
#from enforce import runtime_validation  # https://github.com/RussBaz/enforce  TODO doesn't work for "data" types


# Constants
MARKER = r"/###/"  # line 23
APPNAME = "Subversion Offline Solution V%s (C) Arne Bachmann" % version.__release_version__  # type: str  # line 24
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": False, "texttype": [], "bintype": [], "ignoreDirs": [".*", "__pycache__"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout", "_FOSSIL_", "*.sos.zip"], "ignoresWhitelist": []})  # line 25
termWidth = getTermWidth() - 1  # uses curses or returns conservative default of 80  # line 26


# Functions
def loadConfig() -> 'configr.Configr':  # Accessor when using defaults only  # line 30
    ''' Simplifies loading user-global config from file system or returning application defaults. '''  # line 31
    config = configr.Configr("sos", defaults=defaults)  # type: configr.Configr  # defaults are used if key is not configured, but won't be saved  # line 32
    f, g = config.loadSettings(clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # latter for testing only  # line 33
    if f is None:  # line 34
        debug("Encountered a problem while loading the user configuration: %r" % g)  # line 34
    return config  # line 35

@_coconut_tco  # line 37
def saveConfig(config: 'configr.Configr') -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[Exception]]':  # line 37
    return _coconut_tail_call(config.saveSettings, clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # saves global config, not local one  # line 38

def usage(short: 'bool'=False):  # line 40
    printo("{marker} {appname}{version}".format(marker=MARKER, appname=APPNAME, version="" if not short else " (PyPI: %s)" % version.__version__))  # line 41
    if not short:  # line 42
        printo("""

Usage: {cmd} <command> [<argument>] [<option1>, ...]        When operating in offline mode, or command is one of "help", "offline", "version"
       {cmd} --sos <sos command and arguments>              When operating in offline mode, forced passthrough to SOS
       {cmd} --vcs <underlying vcs command and arguments>   When operating in offline mode, forced passthrough to traditional VCS
       {cmd} <underlying vcs command and arguments>         When operating in online mode, automatic passthrough to traditional VCS

  Repository handling:
    offline [<name>]                                      Start working offline, creating a branch (named <name>), default name depending on VCS
      --compress                                            Compress versioned files (same as `sos config set compress on && sos offline`)
      --track                                               Setup SVN-style mode: users add/remove tracking patterns per branch
      --picky                                               Setup Git-style mode: users pick files for each operation
      --strict                                              Always compare entire file contents
    online                                                Finish working offline
    dump [<path>/]<name[.sos.zip]>                        Dump entire repository into an archive file

  Working with branches:
    branch [<name>]                                       Create a new branch from current file tree and switch to it
      --last                                                Use last revision, not current file tree, but keep file tree unchanged
      --stay                                                Don't switch to new branch, continue on current one
    destroy [<branch>]                                    Remove (current or specified) branch entirely
    switch [<branch>][/<revision>]                        Continue work on another branch
      --meta                                                Only switch file tracking patterns for current branch, don't update any files
    update [<branch>][/<revision>]                        Integrate work from another branch
      --add | --rm | --ask                                  Only add new files / only remove vanished files / Ask what to do. Default: add and remove
      --add-lines | --rm-lines | --ask-lines                Only add inserted lines / only remove deleted lines / Ask what to do. Default: add and remove
      --add-chars | --rm-chars | --ask-chars                Only add new characters / only remove vanished characters / Ask what to do. Default: add and remove
      --eol                                                 Use EOL style from the integrated file instead. Default: EOL style of current file

  Working with files:
    changes [<branch>][/<revision>]                       List changed paths vs. last or specified revision
    commit [<message>]                                    Create a new revision from current state file tree, with an optional commit message
      --tag                                               Memorizes commit message as a tag that can be used instead of numeric revisions
    diff [<branch>][/<revision>]                          List changes in file tree (or `--from` specified revision) vs. last (or specified) revision
      --to=branch/revision                                Take "to" revision as target to compare against (instead of current file tree state)
    ls [<folder path>] [--patterns|--tags]                List file tree and mark changes and tracking status

  Defining file patterns:
    add <file pattern>                                    Add a tracking pattern to current branch (file pattern)
    rm <file pattern>                                     Remove a tracking pattern. Only useful after "offline --track" or "offline --picky"
    mv <oldpattern> <newPattern>                          Rename, move, or move and rename tracked files according to tracked file patterns
      --soft                                                Don't move or rename files, only the tracking pattern

  More commands:
    help, --help                                          Show this usage information
    log                                                   List commits of current branch
      --changes                                             Also list file differences
      --diff                                                Also show textual version differences
    status [-v]                                           List branches and display repository status
    version                                               Display version and package information

  User configuration:
    config [set/unset/show/add/rm] [<param> [<value>]]    Configure user-global defaults.
                                                          Flags (1/0, on/off, true/false, yes/no):
                                                            strict, track, picky, compress
                                                          Lists (semicolon-separated when set; single values for add/rm):
                                                            texttype, bintype, ignores, ignoreDirs, ignoresWhitelist, ignoreDirsWhitelist
                                                          Supported texts:
                                                            defaultbranch (has a dynamic default value, depending on VCS discovered)
    config show|list flags|lists|texts                    Enumerates all configurable settings for specified type
    config show <key>                                     Displays only single value

  Arguments:
    [<branch>][/<revision>]      Revision string. Branch is optional (defaulting to current branch) and may be a label or number >= 0
                                 Revision is an optional integer and may be negative to reference from the latest commits (-1 is most recent revision), or a tag name

  Common options:
    --force                      Executes potentially harmful operations. SOS will tell you when it needs you to confirm an operation with "--force"
                                   for offline: ignore being already offline, start from scratch (same as 'sos online --force && sos offline')
                                   for online: ignore uncommitted branches, just go online and remove existing offline repository
                                   for commit, switch, update, add: ignore uncommitted changes before executing command
    --strict                     Always perform full content comparison, don't rely only on file size and timestamp
                                   for offline command: memorize strict mode setting in repository
                                   for changes, diff, commit, switch, update, delete: perform operation in strict mode, regardless of repository setting
    --progress                   Display file names during file tree traversal, and show compression advantage, if enabled
    --only   <tracked pattern>   Restrict operation to specified pattern(s). Available for "changes", "commit", "diff", "switch", and "update"
    --except <tracked pattern>   Avoid operation for specified pattern(s). Available for "changes", "commit", "diff", "switch", and "update"
    --{cmd}                      When executing {CMD} not being offline, pass arguments to {CMD} instead (e.g. {cmd} --{cmd} config set key value.)
    --log                        Enable logging details
    --verbose                    Enable verbose output, including show compression ratios""".format(appname=APPNAME, cmd="sos", CMD="SOS"))  # line 121
    Exit(code=0)  # line 122

# Main data class
#@runtime_validation
class Metadata:  # line 126
    ''' This class doesn't represent the entire repository state in memory,
      but serves as a container for different repo operations,
      using only parts of its attributes at any point in time. Use with care.
  '''  # line 130

    def __init__(_, path: 'str'):  # line 132
        ''' Create empty container object for various repository operations, and import configuration. '''  # line 133
        _.root = path  # type: str  # line 134
        _.tags = []  # type: List[str]  # list of known (unique) tags  # line 135
        _.branch = None  # type: _coconut.typing.Optional[int]  # current branch number  # line 136
        _.branches = {}  # type: Dict[int, BranchInfo]  # branch number zero represents the initial state at branching  # line 137
        _.repoConf = {}  # type: Dict[str, Any]  # line 138
        _.track = None  # type: bool  # TODO set defaults here?  # line 139
        _.picky = None  # type: bool  # TODO set defaults here?  # line 139
        _.strict = None  # type: bool  # TODO set defaults here?  # line 139
        _.compress = None  # type: bool  # TODO set defaults here?  # line 139
        _.loadBranches()  # loads above values from repository, or uses application defaults  # line 140

        _.commits = {}  # type: Dict[int, CommitInfo]  # consecutive numbers per branch, starting at 0  # line 142
        _.paths = {}  # type: Dict[str, PathInfo]  # utf-8 encoded relative, normalized file system paths  # line 143
        _.commit = None  # type: _coconut.typing.Optional[int]  # current revision number  # line 144

        _.c = configr.Configr(data=_.repoConf, defaults=loadConfig())  # type: configr.Configr  # load global configuration with defaults behind the local configuration  # line 146

    def isTextType(_, filename: 'str') -> 'bool':  # line 148
        return (((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(mimetypes.guess_type(filename)[0])).startswith("text/") or any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.texttype])) and not any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.bintype])  # line 148

    def listChanges(_, changes: 'ChangeSet'):  # line 150
        if len(changes.additions) > 0:  # line 151
            printo(ajoin("ADD ", sorted(changes.additions.keys()), "\n"))  # line 151
        if len(changes.deletions) > 0:  # line 152
            printo(ajoin("DEL ", sorted(changes.deletions.keys()), "\n"))  # line 152
        if len(changes.modifications) > 0:  # line 153
            printo(ajoin("MOD ", sorted(changes.modifications.keys()), "\n"))  # line 153

    def loadBranches(_):  # line 155
        ''' Load list of branches and current branch info from metadata file. '''  # line 156
        try:  # fails if not yet created (on initial branch/commit)  # line 157
            branches = None  # type: List[Tuple]  # line 158
            with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "r", encoding=UTF8) as fd:  # line 159
                repo, branches, config = json.load(fd)  # line 160
            _.tags = repo["tags"]  # list of commit messages to treat as globally unique tags  # line 161
            _.branch = repo["branch"]  # current branch integer  # line 162
            _.track, _.picky, _.strict, _.compress, _.version = [repo[r] for r in ["track", "picky", "strict", "compress", "version"]]  # line 163
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 164
            _.repoConf = config  # line 165
        except Exception as E:  # if not found, create metadata folder  # line 166
            _.branches = {}  # line 167
            _.track, _.picky, _.strict, _.compress, _.version = [defaults[k] for k in ["track", "picky", "strict", "compress"]] + [version.__version__]  # line 168
            warn("Couldn't read branches metadata: %r" % E)  # TODO when going offline, this message is not needed  # line 169

    def saveBranches(_, also: 'Dict[str, Any]'={}):  # line 171
        ''' Save list of branches and current branch info to metadata file. '''  # line 172
        with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "w", encoding=UTF8) as fd:  # line 173
            store = {"version": _.version, "tags": _.tags, "branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}  # type: Dict[str, Any]  # line 174
            store.update(also)  # allows overriding certain values at certain points in time  # line 175
            json.dump((store, list(_.branches.values()), _.repoConf), fd, ensure_ascii=False)  # stores using unicode codepoints, fd knows how to encode them  # line 176

    def getRevisionByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 178
        ''' Convenience accessor for named revisions (using commit message as name as a convention). '''  # line 179
        if name == "":  # line 180
            return -1  # line 180
        try:  # attempt to parse integer string  # line 181
            return int(name)  # attempt to parse integer string  # line 181
        except ValueError:  # line 182
            pass  # line 182
        found = [number for number, commit in _.commits.items() if name == commit.message]  # find any revision by commit message (usually used for tags)  # HINT allows finding any message, not only tagged ones  # line 183
        return found[0] if found else None  # line 184

    def getBranchByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 186
        ''' Convenience accessor for named branches. '''  # line 187
        if name == "":  # current  # line 188
            return _.branch  # current  # line 188
        try:  # attempt to parse integer string  # line 189
            return int(name)  # attempt to parse integer string  # line 189
        except ValueError:  # line 190
            pass  # line 190
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 191
        return found[0] if found else None  # line 192

    def loadBranch(_, branch: 'int'):  # line 194
        ''' Load all commit information from a branch meta data file. '''  # line 195
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "r", encoding=UTF8) as fd:  # line 196
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 197
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 198
        _.branch = branch  # line 199

    def saveBranch(_, branch: 'int'):  # line 201
        ''' Save all commit information to a branch meta data file. '''  # line 202
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "w", encoding=UTF8) as fd:  # line 203
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 204

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'):  # line 206
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 211
        debug("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 212
        tracked = [t for t in _.branches[_.branch].tracked]  # copy  # line 213
        os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 214
        _.loadBranch(_.branch)  # line 215
        revision = max(_.commits)  # type: int  # line 216
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 217
        for path, pinfo in _.paths.items():  # line 218
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 219
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 220
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 221
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 222
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].inSync, tracked)  # save branch info, before storing repo state at caller  # line 223

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 225
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 230
        simpleMode = not (_.track or _.picky)  # line 231
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # in case of initial branch creation  # line 232
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 233
        _.paths = {}  # type: Dict[str, PathInfo]  # line 234
        if simpleMode:  # branches from file system state  # line 235
            changes = _.findChanges(branch, 0, progress=simpleMode)  # type: ChangeSet  # creates revision folder and versioned files  # line 236
            _.listChanges(changes)  # line 237
            _.paths.update(changes.additions.items())  # line 238
        else:  # tracking or picky mode: branch from latest revision  # line 239
            os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 240
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 241
                _.loadBranch(_.branch)  # line 242
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 243
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 244
                for path, pinfo in _.paths.items():  # line 245
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 246
        ts = int(time.time() * 1000)  # line 247
        _.commits = {0: CommitInfo(0, ts, ("Branched on %s" % strftime(ts) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 248
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 249
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 250
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked)  # save branch info, in case it is needed  # line 251

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 253
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 254
        shutil.rmtree(encode(os.path.join(_.root, metaFolder, "b%d" % branch)))  # line 255
        binfo = _.branches[branch]  # line 256
        del _.branches[branch]  # line 257
        _.branch = max(_.branches)  # line 258
        _.saveBranches()  # line 259
        _.commits.clear()  # line 260
        return binfo  # line 261

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 263
        ''' Load all file information from a commit meta data. '''  # line 264
        with codecs.open(encode(branchFolder(branch, revision, base=_.root, file=metaFile)), "r", encoding=UTF8) as fd:  # line 265
            _.paths = json.load(fd)  # line 266
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 267
        _.branch = branch  # line 268

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 270
        ''' Save all file information to a commit meta data file. '''  # line 271
        target = branchFolder(branch, revision, base=_.root)  # type: str  # line 272
        try:  # line 273
            os.makedirs(encode(target))  # line 273
        except:  # line 274
            pass  # line 274
        with codecs.open(encode(os.path.join(target, metaFile)), "w", encoding=UTF8) as fd:  # line 275
            json.dump(_.paths, fd, ensure_ascii=False)  # line 276

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'ChangeSet':  # line 278
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        The function returns the state of file tree *differences*, unless "inverse" is True -> then return original data
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes
        progress: Show file names during processing
    '''  # line 287
        write = branch is not None and revision is not None  # line 288
        if write:  # line 289
            try:  # line 290
                os.makedirs(encode(branchFolder(branch, revision, base=_.root)))  # line 290
            except FileExistsError:  # HINT "try" only necessary for testing hash collisions  # line 291
                pass  # HINT "try" only necessary for testing hash collisions  # line 291
        changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 292
        counter = Counter(-1)  # type: Counter  # line 293
        timer = time.time()  # type: float  # line 293
        hashed = None  # type: _coconut.typing.Optional[str]  # line 294
        written = None  # type: int  # line 294
        compressed = 0  # type: int  # line 294
        original = 0  # type: int  # line 294
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 295
        for path, pinfo in _.paths.items():  # line 296
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 297
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 300
        for path, dirnames, filenames in os.walk(_.root):  # line 301
            path = decode(path)  # line 302
            dirnames[:] = [decode(d) for d in dirnames]  # line 303
            filenames[:] = [decode(f) for f in filenames]  # line 304
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 305
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 306
            dirnames.sort()  # line 307
            filenames.sort()  # line 307
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 308
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 309
            if dontConsider:  # line 310
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 311
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 312
                filename = relPath + SLASH + file  # line 313
                filepath = os.path.join(path, file)  # line 314
                stat = os.stat(encode(filepath))  # line 315
                size, mtime, newtime = stat.st_size, int(stat.st_mtime * 1000), time.time()  # line 316
                if progress and newtime - timer > .1:  # line 317
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", PROGRESS_MARKER[int(counter.inc() % 4)], filename)  # line 318
                    printo(outstring + " " * max(0, termWidth - len(outstring)), nl="")  # line 319
                    timer = newtime  # line 319
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 320
                    nameHash = hashStr(filename)  # line 321
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=nameHash) if write else None) if size > 0 else (None, 0)  # line 322
                    changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 323
                    compressed += written  # line 324
                    original += size  # line 324
                    continue  # with next file  # line 325
                last = _.paths[filename]  # filename is known - check for modifications  # line 326
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 327
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if size > 0 else (None, 0)  # line 328
                    changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 329
                    continue  # line 329
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and hashFile(filepath, _.compress)[0] != last.hash):  # detected a modification  # line 330
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 331
                    changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 332
                else:  # with next file  # line 333
                    continue  # with next file  # line 333
                compressed += written  # line 334
                original += last.size if inverse else size  # line 334
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 335
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 335
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 336
            for file in names:  # line 337
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 338
                    continue  # don't mark ignored files as deleted  # line 338
                pth = path + SLASH + file  # type: str  # line 339
                changes.deletions[pth] = _.paths[pth]  # line 340
        if progress:  # forces new line  # line 341
            printo("\rChecking finished.%s" % ((" Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else "").ljust(termWidth))  # forces new line  # line 341
        else:  # line 342
            debug("Finished detecting changes.%s" % ((" Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else ""))  # line 342
        return changes  # line 343

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 345
        ''' Returns nothing, just updates _.paths in place. '''  # line 346
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 347

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 349
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 350
        _.loadCommit(branch, 0)  # load initial paths  # line 351
        if incrementally:  # line 352
            yield _.paths  # line 352
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 353
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 353
        for rev in range(1, revision + 1):  # line 354
            m.loadCommit(branch, rev)  # line 355
            for p, info in m.paths.items():  # line 356
                if info.size == None:  # line 357
                    del _.paths[p]  # line 357
                else:  # line 358
                    _.paths[p] = info  # line 358
            if incrementally:  # line 359
                yield _.paths  # line 359
        yield None  # for the default case - not incrementally  # line 360

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 362
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 365
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 366
            return (_.branch, -1)  # no branch/revision specified  # line 366
        argument = argument.strip()  # line 367
        if argument.startswith(SLASH):  # current branch  # line 368
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 368
        if argument.endswith(SLASH):  # line 369
            try:  # line 370
                return (_.getBranchByName(argument[:-1]), -1)  # line 370
            except ValueError:  # line 371
                Exit("Unknown branch label '%s'" % argument)  # line 371
        if SLASH in argument:  # line 372
            b, r = argument.split(SLASH)[:2]  # line 373
            try:  # line 374
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 374
            except ValueError:  # line 375
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 375
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 376
        if branch not in _.branches:  # line 377
            branch = None  # line 377
        try:  # either branch name/number or reverse/absolute revision number  # line 378
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 378
        except:  # line 379
            Exit("Unknown branch label or wrong number format")  # line 379
        Exit("This should never happen. Please create a issue report")  # line 380
        return (None, None)  # line 380

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 382
        while True:  # find latest revision that contained the file physically  # line 383
            source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 384
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 385
                break  # line 385
            revision -= 1  # line 386
            if revision < 0:  # line 387
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 387
        return revision, source  # line 388

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 390
        ''' Copy versioned file to other branch/revision. '''  # line 391
        target = branchFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 392
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 393
        shutil.copy2(encode(source), encode(target))  # line 394

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 396
        ''' Return file contents, or copy contents into file path provided. '''  # line 397
        source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 398
        try:  # line 399
            with openIt(source, "r", _.compress) as fd:  # line 400
                if toFile is None:  # read bytes into memory and return  # line 401
                    return fd.read()  # read bytes into memory and return  # line 401
                with open(encode(toFile), "wb") as to:  # line 402
                    while True:  # line 403
                        buffer = fd.read(bufSize)  # line 404
                        to.write(buffer)  # line 405
                        if len(buffer) < bufSize:  # line 406
                            break  # line 406
                    return None  # line 407
        except Exception as E:  # line 408
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 408
        return None  # line 409

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 411
        ''' Recreate file for given revision, or return contents if path is None. '''  # line 412
        if relPath is None:  # just return contents  # line 413
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 413
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 414
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 415
            try:  # line 416
                os.makedirs(encode(os.path.dirname(target)))  # line 416
            except:  # line 417
                pass  # line 417
        if pinfo.size == 0:  # line 418
            with open(encode(target), "wb"):  # line 419
                pass  # line 419
            try:  # update access/modification timestamps on file system  # line 420
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 420
            except Exception as E:  # line 421
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 421
            return None  # line 422
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 423
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 425
            while True:  # line 426
                buffer = fd.read(bufSize)  # line 427
                to.write(buffer)  # line 428
                if len(buffer) < bufSize:  # line 429
                    break  # line 429
        try:  # update access/modification timestamps on file system  # line 430
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 430
        except Exception as E:  # line 431
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 431
        return None  # line 432

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None) -> 'FrozenSet[str]':  # line 434
        ''' Returns list of tracking patterns for provided branch or current branch. '''  # line 435
        return _coconut.frozenset() if not _.track and not _.picky else frozenset(_.branches[_.branch if branch is None else branch].tracked)  # line 436


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 440
    ''' Initial command to start working offline. '''  # line 441
    if os.path.exists(encode(metaFolder)):  # line 442
        if '--force' not in options:  # line 443
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 443
        try:  # line 444
            for entry in os.listdir(metaFolder):  # line 445
                resource = metaFolder + os.sep + entry  # line 446
                if os.path.isdir(resource):  # line 447
                    shutil.rmtree(encode(resource))  # line 447
                else:  # line 448
                    os.unlink(encode(resource))  # line 448
        except:  # line 449
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 449
    m = Metadata(os.getcwd())  # type: Metadata  # line 450
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 451
        m.compress = True  # plain file copies instead of compressed ones  # line 451
    if '--picky' in options or m.c.picky:  # Git-like  # line 452
        m.picky = True  # Git-like  # line 452
    elif '--track' in options or m.c.track:  # Svn-like  # line 453
        m.track = True  # Svn-like  # line 453
    if '--strict' in options or m.c.strict:  # always hash contents  # line 454
        m.strict = True  # always hash contents  # line 454
    debug("Preparing offline repository...")  # line 455
    m.createBranch(0, (defaults["defaultbranch"] if argument is None else argument), initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 456
    m.branch = 0  # line 457
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 458
    info("Offline repository prepared. Use 'sos online' to finish offline work")  # line 459

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 461
    ''' Finish working offline. '''  # line 462
    force = '--force' in options  # type: bool  # line 463
    m = Metadata(os.getcwd())  # line 464
    m.loadBranches()  # line 465
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 466
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 466
    strict = '--strict' in options or m.strict  # type: bool  # line 467
    if options.count("--force") < 2:  # line 468
        changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track and not m.picky else m.getTrackingPatterns(), progress='--progress' in options)  # type: ChangeSet  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 469
        if modified(changes):  # line 470
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 470
    try:  # line 471
        shutil.rmtree(encode(metaFolder))  # line 471
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 471
    except Exception as E:  # line 472
        Exit("Error removing offline repository: %r" % E)  # line 472

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 474
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 475
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 476
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 477
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 478
    m = Metadata(os.getcwd())  # type: Metadata  # line 479
    m.loadBranch(m.branch)  # line 480
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 481
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 481
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 482
    debug("Branching to %sbranch b%02d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 483
    if last:  # line 484
        m.duplicateBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  # branch from branch's last revision  # line 485
    else:  # from file tree state  # line 486
        m.createBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  # branch from current file tree  # line 487
    if not stay:  # line 488
        m.branch = branch  # line 489
        m.saveBranches()  # line 490
    info("%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 491

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 493
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 494
    m = Metadata(os.getcwd())  # type: Metadata  # line 495
    branch = None  # type: _coconut.typing.Optional[int]  # line 495
    revision = None  # type: _coconut.typing.Optional[int]  # line 495
    strict = '--strict' in options or m.strict  # type: bool  # line 496
    branch, revision = m.parseRevisionString(argument)  # line 497
    if branch not in m.branches:  # line 498
        Exit("Unknown branch")  # line 498
    m.loadBranch(branch)  # knows commits  # line 499
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 500
    if revision < 0 or revision > max(m.commits):  # line 501
        Exit("Unknown revision r%02d" % revision)  # line 501
    info(MARKER + " Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 502
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 503
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 504
    m.listChanges(changes)  # line 505
    return changes  # for unit tests only TODO remove  # line 506

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 508
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 509
    m = Metadata(os.getcwd())  # type: Metadata  # line 510
    branch = None  # type: _coconut.typing.Optional[int]  # line 510
    revision = None  # type: _coconut.typing.Optional[int]  # line 510
    strict = '--strict' in options or m.strict  # type: bool  # line 511
    _from = {None: option.split("--from=")[1] for option in options if option.startswith("--from=")}.get(None, None)  # type: _coconut.typing.Optional[str]  # line 512
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 513
    if branch not in m.branches:  # line 514
        Exit("Unknown branch")  # line 514
    m.loadBranch(branch)  # knows commits  # line 515
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 516
    if revision < 0 or revision > max(m.commits):  # line 517
        Exit("Unknown revision r%02d" % revision)  # line 517
    info(MARKER + " Differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 518
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 519
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 520
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 521
    if modified(onlyBinaryModifications):  # line 522
        debug(MARKER + " File changes")  # line 522
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 523

    if changes.modifications:  # line 525
        debug("%s%s Textual modifications" % ("\n" if modified(onlyBinaryModifications) else "", MARKER))  # line 525
    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 526
        content = None  # type: _coconut.typing.Optional[bytes]  # line 527
        if pinfo.size == 0:  # empty file contents  # line 528
            content = b""  # empty file contents  # line 528
        else:  # versioned file  # line 529
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 529
            assert content is not None  # versioned file  # line 529
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 530
        blocks = merge(filename=abspath, into=content, diffOnly=True)  # type: List[MergeBlock]  # only determine change blocks  # line 531
        printo("DIF %s%s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else ""))  # line 532
        for block in blocks:  # line 533
            if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:  # line 534
                pass  # TODO print some previous and following lines - which aren't accessible here anymore  # line 535
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 536
                for no, line in enumerate(block.lines):  # line 537
                    printo("+++ %04d |%s|" % (no + block.line, line))  # line 538
            elif block.tipe == MergeBlockType.REMOVE:  # line 539
                for no, line in enumerate(block.lines):  # line 540
                    printo("--- %04d |%s|" % (no + block.line, line))  # line 541
            elif block.tipe == MergeBlockType.REPLACE:  # TODO for MODIFY also show intra-line change ranges (TODO remove if that code was also removed)  # line 542
                for no, line in enumerate(block.replaces.lines):  # line 543
                    printo("- | %04d |%s|" % (no + block.replaces.line, line))  # line 544
                for no, line in enumerate(block.lines):  # line 545
                    printo("+ | %04d |%s|" % (no + block.line, line))  # line 546
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 550
    ''' Create new revision from file tree changes vs. last commit. '''  # line 551
    m = Metadata(os.getcwd())  # type: Metadata  # line 552
    if argument is not None and argument in m.tags:  # line 553
        Exit("Illegal commit message. It was already used as a tag name")  # line 553
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 554
    if m.picky and not trackingPatterns:  # line 555
        Exit("No file patterns staged for commit in picky mode")  # line 555
    changes = None  # type: ChangeSet  # line 556
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but abort if no changes  # line 557
    info((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 558
    m.paths = changes.additions  # line 559
    m.paths.update(changes.modifications)  # update pathset to changeset only  # line 560
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changes.deletions.items()})  # line 561
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 562
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 563
    m.saveBranch(m.branch)  # line 564
    m.loadBranches()  # TODO is it necessary to load again?  # line 565
    if m.picky:  # remove tracked patterns  # line 566
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 566
    else:  # track or simple mode: set branch dirty  # line 567
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 567
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 568
        m.tags.append(argument)  # memorize unique tag  # line 568
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 568
    m.saveBranches()  # line 569
    info("Created new revision r%02d%s (+%02d/-%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))  # TODO show compression factor  # line 570

def status(options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 572
    ''' Show branches and current repository state. '''  # line 573
    m = Metadata(os.getcwd())  # type: Metadata  # line 574
    current = m.branch  # type: int  # line 575
    strict = '--strict' in options or m.strict  # type: bool  # line 576
    info(MARKER + " Offline repository status")  # line 577
    info("SOS installation:    %s" % os.path.abspath(os.path.dirname(__file__)))  # line 578
    info("Current SOS version: %s" % version.__version__)  # line 579
    info("At creation version: %s" % m.version)  # line 580
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 581
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 582
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 583
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 584
    m.loadBranch(m.branch)  # line 585
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 508  # line 586
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps, progress=True)  # type: ChangeSet  # line 587
    printo("File tree %s" % ("has changes vs. last revision of current branch" if modified(changes) else "is unchanged"))  # line 588
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 589
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 590
        m.loadBranch(branch.number)  # knows commit history  # line 591
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 592
    if m.track or m.picky and len(m.branches[m.branch].tracked) > 0:  # line 593
        info("\nTracked file patterns:")  # line 594
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 595

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str]]':  # line 597
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags. '''  # line 602
    m = Metadata(os.getcwd())  # type: Metadata  # line 603
    force = '--force' in options  # type: bool  # line 604
    strict = '--strict' in options or m.strict  # type: bool  # line 605
    if argument is not None:  # line 606
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 607
        if branch is None:  # line 608
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 608
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 609

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 612
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 613
    changes = m.findChanges(m.branch if commit else None, max(m.commits) + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 614
    if check and modified(changes) and not force:  # line 615
        m.listChanges(changes)  # line 616
        if not commit:  # line 617
            Exit("File tree contains changes. Use --force to proceed")  # line 617
    elif commit and not force:  #  and not check  # line 618
        Exit("Nothing to commit")  #  and not check  # line 618

    if argument is not None:  # branch/revision specified  # line 620
        m.loadBranch(branch)  # knows commits of target branch  # line 621
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 622
        if revision < 0 or revision > max(m.commits):  # line 623
            Exit("Unknown revision r%02d" % revision)  # line 623
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch))  # line 624
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns)  # line 625

def switch(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 627
    ''' Continue work on another branch, replacing file tree changes. '''  # line 628
    changes = None  # type: ChangeSet  # line 629
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options)  # line 630
    info(MARKER + " Switching to branch %sb%02d/r%02d" % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 631

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 634
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked)  # line 635
    else:  # full file switch  # line 636
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 637
        changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 638
        if not modified(changes):  # line 639
            info("No changes to current file tree")  # line 640
        else:  # integration required  # line 641
            for path, pinfo in changes.deletions.items():  # line 642
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 643
                printo("ADD " + path)  # line 644
            for path, pinfo in changes.additions.items():  # line 645
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 646
                printo("DEL " + path)  # line 647
            for path, pinfo in changes.modifications.items():  # line 648
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 649
                printo("MOD " + path)  # line 650
    m.branch = branch  # line 651
    m.saveBranches()  # store switched path info  # line 652
    info("Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 653

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 655
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 659
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 660
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 661
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 662
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 663
    m = Metadata(os.getcwd())  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 664
    changes = None  # type: ChangeSet  # line 665
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 666
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 667
    debug("Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 668

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 671
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 672
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingUnion), dontConsider=excps, progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 673
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 674
        if trackingUnion != trackingPatterns:  # nothing added  # line 675
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 676
        else:  # line 677
            info("Nothing to update")  # but write back updated branch info below  # line 678
    else:  # integration required  # line 679
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 680
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 681
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 681
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 682
        for path, pinfo in changes.additions.items():  # line 683
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 684
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 684
            if mrg.value & MergeOperation.REMOVE.value:  # line 685
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 685
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 686
        for path, pinfo in changes.modifications.items():  # line 687
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 688
            binary = not m.isTextType(path)  # type: bool  # line 689
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 690
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 691
                printo(("MOD " if not binary else "BIN ") + path)  # line 692
                while True:  # line 693
                    printo(into)  # TODO print mtime, size differences?  # line 694
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 695
                    if op in ("it" if binary else "itm"):  # line 696
                        break  # line 696
            if op == "t":  # line 697
                printo("THR " + path)  # blockwise copy of contents  # line 698
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 698
            elif op == "m":  # line 699
                current = None  # type: bytes  # line 700
                with open(encode(into), "rb") as fd:  # TODO slurps file  # line 701
                    current = fd.read()  # TODO slurps file  # line 701
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 702
                if current == file:  # line 703
                    debug("No difference to versioned file")  # line 703
                elif file is not None:  # if None, error message was already logged  # line 704
                    contents = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # type: bytes  # line 705
                    if contents != current:  # line 706
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 707
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 707
                    else:  # TODO but update timestamp?  # line 708
                        debug("No change")  # TODO but update timestamp?  # line 708
            else:  # mine or wrong input  # line 709
                printo("MNE " + path)  # nothing to do! same as skip  # line 710
    info("Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 711
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 712
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 713
    m.saveBranches()  # line 714

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 716
    ''' Remove a branch entirely. '''  # line 717
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options)  # line 718
    if len(m.branches) == 1:  # line 719
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 719
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 720
    if branch is None or branch not in m.branches:  # line 721
        Exit("Cannot delete unknown branch %r" % branch)  # line 721
    debug("Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 722
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 723
    info("Branch b%02d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 724

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 726
    ''' Add a tracked files pattern to current branch's tracked files. '''  # line 727
    force = '--force' in options  # type: bool  # line 728
    m = Metadata(os.getcwd())  # type: Metadata  # line 729
    if not m.track and not m.picky:  # line 730
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 730
    if pattern in m.branches[m.branch].tracked:  # line 731
        Exit("Pattern '%s' already tracked" % pattern)  # line 731
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 732
        Exit("The pattern folder doesn't exist. Use --force to add it anyway")  # line 732
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 733
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 734
    m.branches[m.branch].tracked.append(pattern)  # line 735
    m.saveBranches()  # line 736
    info("Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 737

def remove(relPath: 'str', pattern: 'str'):  # line 739
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 740
    m = Metadata(os.getcwd())  # type: Metadata  # line 741
    if not m.track and not m.picky:  # line 742
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 742
    if pattern not in m.branches[m.branch].tracked:  # line 743
        suggestion = _coconut.set()  # type: Set[str]  # line 744
        for pat in m.branches[m.branch].tracked:  # line 745
            if fnmatch.fnmatch(pattern, pat):  # line 746
                suggestion.add(pat)  # line 746
        if suggestion:  # TODO use same wording as in move  # line 747
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 747
        Exit("Tracked pattern '%s' not found" % pattern)  # line 748
    m.branches[m.branch].tracked.remove(pattern)  # line 749
    m.saveBranches()  # line 750
    info("Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 751

def ls(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 753
    ''' List specified directory, augmenting with repository metadata. '''  # line 754
    folder = "." if argument is None else argument  # type: str  # line 755
    m = Metadata(os.getcwd())  # type: Metadata  # line 756
    info("Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 757
    relPath = os.path.relpath(folder, m.root).replace(os.sep, SLASH)  # type: str  # line 758
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 759
    if '--tags' in options:  # line 760
        printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 761
        return  # line 762
    if '--patterns' in options:  # line 763
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 764
        if out:  # line 765
            printo(out)  # line 765
        return  # line 766
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 767
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 768
        ignore = None  # type: _coconut.typing.Optional[str]  # line 769
        for ig in m.c.ignores:  # line 770
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 771
                ignore = ig  # remember first match  # line 771
                break  # remember first match  # line 771
        if ig:  # line 772
            for wl in m.c.ignoresWhitelist:  # line 773
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 774
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 774
                    break  # found a white list entry for ignored file, undo ignoring it  # line 774
        matches = []  # type: List[str]  # line 775
        if not ignore:  # line 776
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 777
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 778
                    matches.append(os.path.basename(pattern))  # line 778
        matches.sort(key=lambda element: len(element))  # line 779
        printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "..."), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 780

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 782
    ''' List previous commits on current branch. '''  # line 783
    m = Metadata(os.getcwd())  # type: Metadata  # line 784
    m.loadBranch(m.branch)  # knows commit history  # line 785
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + " Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 786
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 787
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, max(m.commits))  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 788
    maxWidth = max([wcswidth((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) for commit in m.commits.values()])  # type: int  # line 789
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 790
    for no in range(max(m.commits) + 1):  # line 791
        commit = m.commits[no]  # type: CommitInfo  # line 792
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 793
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # side-effect: updates m.paths  # line 794
        _add = news - olds  # type: FrozenSet[str]  # line 795
        _del = olds - news  # type: FrozenSet[str]  # line 796
        _mod = frozenset([_ for _, info in nxts.items() if _ in m.paths and m.paths[_].size != info.size and (m.paths[_].hash != info.hash if m.strict else m.paths[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 797
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 798
        printo("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT) |%s|%s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)).ljust(maxWidth), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 799
        if '--changes' in options:  # line 800
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}))  # line 800
        if '--diff' in options:  # TODO needs to extract code from diff first to be reused here  # line 801
            pass  # TODO needs to extract code from diff first to be reused here  # line 801
        olds = news  # line 802

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 804
    ''' Exported entire repository as archive for easy transfer. '''  # line 805
    force = '--force' in options  # type: bool  # line 806
    progress = '--progress' in options  # type: bool  # line 807
    import zipfile  # TODO display compression ratio (if any)  # line 808
    try:  # line 809
        import zlib  # line 809
        compression = zipfile.ZIP_DEFLATED  # line 809
    except:  # line 810
        compression = zipfile.ZIP_STORED  # line 810

    if argument is None:  # line 812
        Exit("Argument missing (target filename)")  # line 812
    argument = argument if "." in argument else argument + ".sos.zip"  # line 813
    if os.path.exists(encode(argument)) and not force:  # line 814
        Exit("Target archive already exists. Use 'sos dump <arget> --force' to override")  # line 814
    with zipfile.ZipFile(argument, "w", compression) as fd:  # line 815
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 816
        counter = Counter(-1)  # type: Counter  # line 817
        timer = time.time()  # type: float  # line 817
        totalsize = 0  # type: int  # line 818
        start_time = time.time()  # type: float  # line 819
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 820
            dirpath = decode(dirpath)  # line 821
            dirnames[:] = [decode(d) for d in dirnames]  # line 822
            filenames[:] = [decode(f) for f in filenames]  # line 823
            for filename in filenames:  # line 824
                newtime = time.time()  # type: float  # TODO alternatively count bytes and use a threshold there  # line 825
                abspath = os.path.join(dirpath, filename)  # type: str  # line 826
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 827
                totalsize += os.stat(encode(abspath)).st_size  # line 828
                if progress and newtime - timer > .1:  # line 829
                    printo(("\rDumping %s@%6.2f MiB/s %s" % (PROGRESS_MARKER[int(counter.inc() % 4)], totalsize / (MEBI * (time.time() - start_time)), filename)).ljust(termwidth), nl="")  # line 829
                    timer = newtime  # line 829
                fd.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 830
    printo("\rDone dumping entire repository.".ljust(termwidth), nl="")  # clean line  # line 831

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 833
    command, key, value = (arguments + [None] * 2)[:3]  # line 834
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 835
        Exit("Unknown config command")  # line 835
    local = "--local" in options  # type: bool  # line 836
    m = Metadata(os.getcwd())  # type: Metadata  # loads layerd configuration as well. TODO warning if repo not exists  # line 837
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 838
    if command == "set":  # line 839
        if None in (key, value):  # line 840
            Exit("Key or value not specified")  # line 840
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 841
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 841
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 842
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 842
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 843
    elif command == "unset":  # line 844
        if key is None:  # line 845
            Exit("No key specified")  # line 845
        if key not in c.keys():  # line 846
            Exit("Unknown key")  # line 846
        del c[key]  # line 847
    elif command == "add":  # line 848
        if None in (key, value):  # line 849
            Exit("Key or value not specified")  # line 849
        if key not in CONFIGURABLE_LISTS:  # line 850
            Exit("Unsupported key %r" % key)  # line 850
        if key not in c.keys():  # add list  # line 851
            c[key] = [value]  # add list  # line 851
        elif value in c[key]:  # line 852
            Exit("Value already contained, nothing to do")  # line 852
        if ";" in value:  # line 853
            c[key].append(removePath(key, value))  # line 853
        else:  # line 854
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 854
    elif command == "rm":  # line 855
        if None in (key, value):  # line 856
            Exit("Key or value not specified")  # line 856
        if key not in c.keys():  # line 857
            Exit("Unknown key %r" % key)  # line 857
        if value not in c[key]:  # line 858
            Exit("Unknown value %r" % value)  # line 858
        c[key].remove(value)  # line 859
    else:  # Show or list  # line 860
        if key == "flags":  # list valid configuration items  # line 861
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 861
        elif key == "lists":  # line 862
            printo(", ".join(CONFIGURABLE_LISTS))  # line 862
        elif key == "texts":  # line 863
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 863
        else:  # line 864
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 865
            c = m.c  # always use full configuration chain  # line 866
            try:  # attempt single key  # line 867
                assert key is not None  # line 868
                c[key]  # line 868
                l = key in c.keys()  # type: bool  # line 869
                g = key in c.__defaults.keys()  # type: bool  # line 869
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 870
            except:  # normal value listing  # line 871
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 872
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 873
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 874
                for k, vt in sorted(vals.items()):  # line 875
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 875
                if len(c.keys()) == 0:  # line 876
                    info("No local configuration stored")  # line 876
                if len(c.__defaults.keys()) == 0:  # line 877
                    info("No global configuration stored")  # line 877
        return  # in case of list, no need to store anything  # line 878
    if local:  # saves changes of repoConfig  # line 879
        m.repoConf = c.__map  # saves changes of repoConfig  # line 879
        m.saveBranches()  # saves changes of repoConfig  # line 879
        Exit("OK", code=0)  # saves changes of repoConfig  # line 879
    else:  # global config  # line 880
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 881
        if f is None:  # line 882
            error("Error saving user configuration: %r" % h)  # line 882
        else:  # line 883
            Exit("OK", code=0)  # line 883

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[]):  # line 885
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique. '''  # line 886
    force = '--force' in options  # type: bool  # line 887
    soft = '--soft' in options  # type: bool  # line 888
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 889
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 889
    m = Metadata(os.getcwd())  # type: Metadata  # line 890
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 891
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 892
    if not matching and not force:  # line 893
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 893
    if not m.track and not m.picky:  # line 894
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 894
    if pattern not in m.branches[m.branch].tracked:  # line 895
        for tracked in (t for t in m.branches[m.branch].tracked if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 896
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 897
            if alternative:  # line 898
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 898
        if not (force or soft):  # line 899
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 899
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 900
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 901
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 902
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 906
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 907
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 907
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 908
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 909
    if len({st[1] for st in matches}) != len(matches):  # line 910
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 910
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 911
    if os.path.exists(encode(newRelPath)):  # line 912
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 913
        if exists and not (force or soft):  # line 914
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 914
    else:  # line 915
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 915
    if not soft:  # perform actual renaming  # line 916
        for (source, target) in matches:  # line 917
            try:  # line 918
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 918
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 919
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 919
    m.branches[m.branch].tracked[m.branches[m.branch].tracked.index(pattern)] = newPattern  # line 920
    m.saveBranches()  # line 921

def parse(root: 'str', cwd: 'str'):  # line 923
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm. '''  # line 924
    debug("Parsing command-line arguments...")  # line 925
    try:  # line 926
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 927
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: Union[List[str], str, None]  # line 928
        if len(arguments) == 0:  # line 929
            arguments = [None]  # line 929
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 930
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 931
        debug("Processing command %r with arguments %r and options %r." % (("" if command is None else command), arguments if arguments else "", options))  # line 932
        if command[:1] in "amr":  # line 933
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 933
        if command[:1] == "m":  # line 934
            if len(arguments) < 2:  # line 935
                Exit("Need a second file pattern argument as target for move/rename command")  # line 935
            newRelPath, newPattern = relativize(root, os.path.join(cwd, options[0]))  # line 936
        if command[:1] == "a":  # line 937
            add(relPath, pattern, options)  # line 937
        elif command[:1] == "b":  # line 938
            branch(arguments[0], options)  # line 938
        elif command[:2] == "ch":  # line 939
            changes(arguments[0], options, onlys, excps)  # line 939
        elif command[:3] == "com":  # line 940
            commit(arguments[0], options, onlys, excps)  # line 940
        elif command[:2] == "ci":  # line 941
            commit(arguments[0], options, onlys, excps)  # line 941
        elif command[:3] == 'con':  # line 942
            config(arguments, options)  # line 942
        elif command[:2] == "de":  # line 943
            delete(arguments[0], options)  # line 943
        elif command[:2] == "di":  # line 944
            diff(arguments[0], options, onlys, excps)  # line 944
        elif command[:2] == "du":  # line 945
            dump(arguments[0], options)  # line 945
        elif command[:1] == "h":  # line 946
            usage()  # line 946
        elif command[:2] == "lo":  # line 947
            log(options)  # line 947
        elif command[:2] == "li":  # TODO handle absolute paths as well, also for Windows? think through  # line 948
            ls(relativize(root, cwd if not arguments else os.path.join(cwd, arguments[0]))[1], options)  # TODO handle absolute paths as well, also for Windows? think through  # line 948
        elif command[:2] == "ls":  # TODO avoid and/or normalize root super paths (..)  # line 949
            ls(relativize(root, cwd if not arguments else os.path.join(cwd, arguments[0]))[1], options)  # TODO avoid and/or normalize root super paths (..)  # line 949
        elif command[:1] == "m":  # line 950
            move(relPath, pattern, newRelPath, newPattern, options[1:])  # line 950
        elif command[:2] == "of":  # line 951
            offline(arguments[0], options)  # line 951
        elif command[:2] == "on":  # line 952
            online(options)  # line 952
        elif command[:1] == "r":  # line 953
            remove(relPath, pattern)  # line 953
        elif command[:2] == "st":  # line 954
            status(options, onlys, excps)  # line 954
        elif command[:2] == "sw":  # line 955
            switch(arguments[0], options, onlys, excps)  # line 955
        elif command[:1] == "u":  # line 956
            update(arguments[0], options, onlys, excps)  # line 956
        elif command[:1] == "v":  # line 957
            usage(short=True)  # line 957
        else:  # line 958
            Exit("Unknown command '%s'" % command)  # line 958
        Exit(code=0)  # line 959
    except (Exception, RuntimeError) as E:  # line 960
        printo(str(E))  # line 961
        import traceback  # line 962
        traceback.print_exc()  # line 963
        traceback.print_stack()  # line 964
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing.")  # line 965

def main():  # line 967
    global debug, info, warn, error  # line 968
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 969
    _log = Logger(logging.getLogger(__name__))  # line 970
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 970
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 971
        sys.argv.remove(option)  # clean up program arguments  # line 971
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 972
        usage()  # line 972
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 973
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 974
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 975
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 976
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in ["h", "v"]:  # in offline mode or just going offline TODO what about git config?  # line 977
        cwd = os.getcwd()  # line 978
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 979
        parse(root, cwd)  # line 980
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 981
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 982
        import subprocess  # only required in this section  # line 983
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 984
        inp = ""  # type: str  # line 985
        while True:  # line 986
            so, se = process.communicate(input=inp)  # line 987
            if process.returncode is not None:  # line 988
                break  # line 988
            inp = sys.stdin.read()  # line 989
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 990
            if root is None:  # line 991
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 991
            m = Metadata(root)  # type: Metadata  # line 992
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 993
            m.saveBranches()  # line 994
    else:  # line 995
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 995


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 999
level = logging.DEBUG if verbose else logging.INFO  # line 1000
force_sos = '--sos' in sys.argv  # type: bool  # line 1001
force_vcs = '--vcs' in sys.argv  # type: bool  # line 1002
_log = Logger(logging.getLogger(__name__))  # line 1003
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1003
if __name__ == '__main__':  # line 1004
    main()  # line 1004
