#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xa55bf91a

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
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": False, "texttype": [], "bintype": [], "ignoreDirs": [".*", "__pycache__"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout", "_FOSSIL_"], "ignoresWhitelist": []})  # line 25
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
    print("{marker} {appname}{version}".format(marker=MARKER, appname=APPNAME, version="" if not short else " (PyPI: %s)" % version.__version__))  # line 41
    if not short:  # line 42
        print("""

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
            print(ajoin("ADD ", sorted(changes.additions.keys()), "\n"))  # line 151
        if len(changes.deletions) > 0:  # line 152
            print(ajoin("DEL ", sorted(changes.deletions.keys()), "\n"))  # line 152
        if len(changes.modifications) > 0:  # line 153
            print(ajoin("MOD ", sorted(changes.modifications.keys()), "\n"))  # line 153

    def loadBranches(_):  # line 155
        ''' Load list of branches and current branch info from metadata file. '''  # line 156
        try:  # fails if not yet created (on initial branch/commit)  # line 157
            branches = None  # type: List[Tuple]  # line 158
            with codecs.open(os.path.join(_.root, metaFolder, metaFile), "r", encoding=UTF8) as fd:  # line 159
                repo, branches, config = json.load(fd)  # line 160
            _.tags = repo["tags"]  # list of commit messages to treat as globally unique tags  # line 161
            _.branch = repo["branch"]  # current branch integer  # line 162
            _.track, _.picky, _.strict, _.compress, _.version = [repo[r] for r in ["track", "picky", "strict", "compress", "version"]]  # line 163
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 164
            _.repoConf = config  # line 165
        except Exception as E:  # if not found, create metadata folder  # line 166
            _.branches = {}  # line 167
            _.track, _.picky, _.strict, _.compress, _.version = [defaults[k] for k in ["track", "picky", "strict", "compress"]] + [version.__version__]  # line 168
            warn("Couldn't read branches metadata: %r" % E)  # line 169

    def saveBranches(_, also: 'Dict[str, Any]'={}):  # line 171
        ''' Save list of branches and current branch info to metadata file. '''  # line 172
        with codecs.open(os.path.join(_.root, metaFolder, metaFile), "w", encoding=UTF8) as fd:  # line 173
            store = {"version": _.version, "tags": _.tags, "branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}  # type: Dict[str, Any]  # line 174
            store.update(also)  # allows overriding certain values at certain points in time  # line 175
            json.dump((store, list(_.branches.values()), _.repoConf), fd, ensure_ascii=False)  # line 176

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
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "r", encoding=UTF8) as fd:  # line 196
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 197
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 198
        _.branch = branch  # line 199

    def saveBranch(_, branch: 'int'):  # line 201
        ''' Save all commit information to a branch meta data file. '''  # line 202
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "w", encoding=UTF8) as fd:  # line 203
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 204

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'):  # line 206
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 211
        debug("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 212
        tracked = [t for t in _.branches[_.branch].tracked]  # copy  # line 213
        os.makedirs(branchFolder(branch, 0, base=_.root))  # line 214
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
            os.makedirs(branchFolder(branch, 0, base=_.root))  # line 240
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
        shutil.rmtree(os.path.join(_.root, metaFolder, "b%d" % branch))  # line 255
        binfo = _.branches[branch]  # line 256
        del _.branches[branch]  # line 257
        _.branch = max(_.branches)  # line 258
        _.saveBranches()  # line 259
        _.commits.clear()  # line 260
        return binfo  # line 261

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 263
        ''' Load all file information from a commit meta data. '''  # line 264
        with codecs.open(branchFolder(branch, revision, base=_.root, file=metaFile), "r", encoding=UTF8) as fd:  # line 265
            _.paths = json.load(fd)  # line 266
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 267
        _.branch = branch  # line 268

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 270
        ''' Save all file information to a commit meta data file. '''  # line 271
        target = branchFolder(branch, revision, base=_.root)  # line 272
        try:  # line 273
            os.makedirs(target)  # line 273
        except:  # line 274
            pass  # line 274
        with codecs.open(os.path.join(target, metaFile), "w", encoding=UTF8) as fd:  # line 275
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
                os.makedirs(branchFolder(branch, revision, base=_.root))  # line 290
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
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 302
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 303
            dirnames.sort()  # line 304
            filenames.sort()  # line 304
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 305
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 306
            if dontConsider:  # line 307
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 308
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 309
                filename = relPath + SLASH + file  # line 310
                filepath = os.path.join(path, file)  # line 311
                stat = os.stat(filepath)  # line 312
                size, mtime, newtime = stat.st_size, int(stat.st_mtime * 1000), time.time()  # line 313
                if progress and newtime - timer > .1:  # line 314
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", PROGRESS_MARKER[int(counter.inc() % 4)], filename)  # line 315
                    sys.stdout.write(outstring + " " * max(0, termWidth - len(outstring)))  # TODO could write to new line instead of carriage return (still true?)  # line 316
                    sys.stdout.flush()  # TODO could write to new line instead of carriage return (still true?)  # line 316
                    timer = newtime  # TODO could write to new line instead of carriage return (still true?)  # line 316
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 317
                    nameHash = hashStr(filename)  # line 318
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=nameHash) if write else None) if size > 0 else (None, 0)  # line 319
                    changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 320
                    compressed += written  # line 321
                    original += size  # line 321
                    continue  # line 322
                last = _.paths[filename]  # filename is known - check for modifications  # line 323
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 324
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if size > 0 else (None, 0)  # line 325
                    changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 326
                    continue  # line 326
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and hashFile(filepath, _.compress)[0] != last.hash):  # detected a modification  # line 327
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 328
                    changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 329
                else:  # line 330
                    continue  # line 330
                compressed += written  # line 331
                original += last.size if inverse else size  # line 331
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 332
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 332
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 333
            for file in names:  # line 334
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 335
                    continue  # don't mark ignored files as deleted  # line 335
                pth = path + SLASH + file  # type: str  # line 336
                changes.deletions[pth] = _.paths[pth]  # line 337
        if progress:  # force new line  # line 338
            print("\rPreparation finished.%s" % (" Compression advantage %s" % ("is %.1f%%" % (original * 100. / compressed - 100.) if compressed > 0 else "cannot be computed") if _.compress else "").ljust(termWidth), file=sys.stdout)  # force new line  # line 338
        else:  # line 339
            debug("Finished detecting changes.%s" % (" Compression advantage %s" % ("is %.1f%%" % (original * 100. / compressed - 100.) if compressed > 0 else "cannot be computed") if _.compress else ""))  # line 339
        return changes  # line 340

    def integrateChangeset(_, changes: 'ChangeSet', clear=False):  # line 342
        ''' In-memory update from a changeset, marking deleted files with size=None. Use clear = True to start on an empty path set. '''  # line 343
        if clear:  # line 344
            _.paths.clear()  # line 344
        else:  # line 345
            rm = [p for p, info in _.paths.items() if info.size is None]  # remove files deleted in earlier change sets (revisions)  # line 346
            for old in rm:  # remove previously removed entries completely  # line 347
                del _.paths[old]  # remove previously removed entries completely  # line 347
        for d, info in changes.deletions.items():  # mark now removed entries as deleted  # line 348
            _.paths[d] = PathInfo(info.nameHash, None, info.mtime, None)  # mark now removed entries as deleted  # line 348
        _.paths.update(changes.additions)  # line 349
        _.paths.update(changes.modifications)  # line 350

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 352
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once  # line 353

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[ChangeSet]]':  # line 355
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 356
        _.loadCommit(branch, 0)  # load initial paths  # line 357
        if incrementally:  # line 358
            yield diffPathSets({}, _.paths)  # line 358
        n = Metadata(_.root)  # type: Metadata  # next changes  # line 359
        for revision in range(1, revision + 1):  # line 360
            n.loadCommit(branch, revision)  # line 361
            changes = diffPathSets(_.paths, n.paths)  # type: ChangeSet  # line 362
            _.integrateChangeset(changes)  # line 363
            if incrementally:  # line 364
                yield changes  # line 364
        yield None  # for the default case - not incrementally  # line 365

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 367
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 370
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 371
            return (_.branch, -1)  # no branch/revision specified  # line 371
        argument = argument.strip()  # line 372
        if argument.startswith(SLASH):  # current branch  # line 373
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 373
        if argument.endswith(SLASH):  # line 374
            try:  # line 375
                return (_.getBranchByName(argument[:-1]), -1)  # line 375
            except ValueError:  # line 376
                Exit("Unknown branch label '%s'" % argument)  # line 376
        if SLASH in argument:  # line 377
            b, r = argument.split(SLASH)[:2]  # line 378
            try:  # line 379
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 379
            except ValueError:  # line 380
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 380
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 381
        if branch not in _.branches:  # line 382
            branch = None  # line 382
        try:  # either branch name/number or reverse/absolute revision number  # line 383
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 383
        except:  # line 384
            Exit("Unknown branch label or wrong number format")  # line 384
        Exit("This should never happen. Please create a issue report")  # line 385
        return (None, None)  # line 385

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 387
        while True:  # find latest revision that contained the file physically  # line 388
            source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 389
            if os.path.exists(source) and os.path.isfile(source):  # line 390
                break  # line 390
            revision -= 1  # line 391
            if revision < 0:  # line 392
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 392
        return revision, source  # line 393

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 395
        ''' Copy versioned file to other branch/revision. '''  # line 396
        target = branchFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 397
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 398
        shutil.copy2(source, target)  # line 399

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 401
        ''' Return file contents, or copy contents into file path provided. '''  # line 402
        source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 403
        try:  # line 404
            with openIt(source, "r", _.compress) as fd:  # line 405
                if toFile is None:  # read bytes into memory and return  # line 406
                    return fd.read()  # read bytes into memory and return  # line 406
                with open(toFile, "wb") as to:  # line 407
                    while True:  # line 408
                        buffer = fd.read(bufSize)  # line 409
                        to.write(buffer)  # line 410
                        if len(buffer) < bufSize:  # line 411
                            break  # line 411
                    return None  # line 412
        except Exception as E:  # line 413
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 413
        return None  # line 414

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 416
        ''' Recreate file for given revision, or return contents if path is None. '''  # line 417
        if relPath is None:  # just return contents  # line 418
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 418
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 419
        if ensurePath:  #  and not os.path.exists(os.path.dirname(target)):  # line 420
            try:  # line 421
                os.makedirs(os.path.dirname(target))  # line 421
            except:  # line 422
                pass  # line 422
        if pinfo.size == 0:  # line 423
            with open(target, "wb"):  # line 424
                pass  # line 424
            try:  # update access/modification timestamps on file system  # line 425
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 425
            except Exception as E:  # line 426
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 426
            return None  # line 427
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 428
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(target, "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 430
            while True:  # line 431
                buffer = fd.read(bufSize)  # line 432
                to.write(buffer)  # line 433
                if len(buffer) < bufSize:  # line 434
                    break  # line 434
        try:  # update access/modification timestamps on file system  # line 435
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 435
        except Exception as E:  # line 436
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 436
        return None  # line 437

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None) -> 'FrozenSet[str]':  # line 439
        ''' Returns list of tracking patterns for provided branch or current branch. '''  # line 440
        return _coconut.frozenset() if not _.track and not _.picky else frozenset(_.branches[_.branch if branch is None else branch].tracked)  # line 441


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 445
    ''' Initial command to start working offline. '''  # line 446
    if os.path.exists(metaFolder):  # line 447
        if '--force' not in options:  # line 448
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 448
        try:  # line 449
            for entry in os.listdir(metaFolder):  # line 450
                resource = metaFolder + os.sep + entry  # line 451
                if os.path.isdir(resource):  # line 452
                    shutil.rmtree(resource)  # line 452
                else:  # line 453
                    os.unlink(resource)  # line 453
        except:  # line 454
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 454
    m = Metadata(os.getcwd())  # type: Metadata  # line 455
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 456
        m.compress = True  # plain file copies instead of compressed ones  # line 456
    if '--picky' in options or m.c.picky:  # Git-like  # line 457
        m.picky = True  # Git-like  # line 457
    elif '--track' in options or m.c.track:  # Svn-like  # line 458
        m.track = True  # Svn-like  # line 458
    if '--strict' in options or m.c.strict:  # always hash contents  # line 459
        m.strict = True  # always hash contents  # line 459
    debug("Preparing offline repository...")  # line 460
    m.createBranch(0, (defaults["defaultbranch"] if argument is None else argument), initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 461
    m.branch = 0  # line 462
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 463
    info("Offline repository prepared. Use 'sos online' to finish offline work")  # line 464

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 466
    ''' Finish working offline. '''  # line 467
    force = '--force' in options  # type: bool  # line 468
    m = Metadata(os.getcwd())  # line 469
    m.loadBranches()  # line 470
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 471
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 471
    strict = '--strict' in options or m.strict  # type: bool  # line 472
    if options.count("--force") < 2:  # line 473
        changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track and not m.picky else m.getTrackingPatterns(), progress='--progress' in options)  # type: ChangeSet  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 474
        if modified(changes):  # line 475
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 475
    try:  # line 476
        shutil.rmtree(metaFolder)  # line 476
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 476
    except Exception as E:  # line 477
        Exit("Error removing offline repository: %r" % E)  # line 477

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 479
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 480
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 481
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 482
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 483
    m = Metadata(os.getcwd())  # type: Metadata  # line 484
    m.loadBranch(m.branch)  # line 485
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 486
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 486
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 487
    debug("Branching to %sbranch b%02d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 488
    if last:  # line 489
        m.duplicateBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  # branch from branch's last revision  # line 490
    else:  # from file tree state  # line 491
        m.createBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  # branch from current file tree  # line 492
    if not stay:  # line 493
        m.branch = branch  # line 494
        m.saveBranches()  # line 495
    info("%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 496

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 498
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 499
    m = Metadata(os.getcwd())  # type: Metadata  # line 500
    branch = None  # type: _coconut.typing.Optional[int]  # line 500
    revision = None  # type: _coconut.typing.Optional[int]  # line 500
    strict = '--strict' in options or m.strict  # type: bool  # line 501
    branch, revision = m.parseRevisionString(argument)  # line 502
    if branch not in m.branches:  # line 503
        Exit("Unknown branch")  # line 503
    m.loadBranch(branch)  # knows commits  # line 504
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 505
    if revision < 0 or revision > max(m.commits):  # line 506
        Exit("Unknown revision r%02d" % revision)  # line 506
    info(MARKER + " Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 507
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 508
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 509
    m.listChanges(changes)  # line 510
    return changes  # for unit tests only  # line 511

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 513
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 514
    m = Metadata(os.getcwd())  # type: Metadata  # line 515
    branch = None  # type: _coconut.typing.Optional[int]  # line 515
    revision = None  # type: _coconut.typing.Optional[int]  # line 515
    strict = '--strict' in options or m.strict  # type: bool  # line 516
    _from = {None: option.split("--from=")[1] for option in options if option.startswith("--from=")}.get(None, None)  # type: _coconut.typing.Optional[str]  # line 517
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 518
    if branch not in m.branches:  # line 519
        Exit("Unknown branch")  # line 519
    m.loadBranch(branch)  # knows commits  # line 520
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 521
    if revision < 0 or revision > max(m.commits):  # line 522
        Exit("Unknown revision r%02d" % revision)  # line 522
    info(MARKER + " Differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 523
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 524
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 525
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 526
    if modified(onlyBinaryModifications):  # line 527
        debug(MARKER + " File changes")  # line 527
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 528

    if changes.modifications:  # line 530
        debug("%s%s Textual modifications" % ("\n" if modified(onlyBinaryModifications) else "", MARKER))  # line 530
    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 531
        content = None  # type: _coconut.typing.Optional[bytes]  # line 532
        if pinfo.size == 0:  # empty file contents  # line 533
            content = b""  # empty file contents  # line 533
        else:  # versioned file  # line 534
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 534
            assert content is not None  # versioned file  # line 534
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 535
        blocks = merge(filename=abspath, into=content, diffOnly=True)  # type: List[MergeBlock]  # only determine change blocks  # line 536
        print("DIF %s%s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else ""))  # line 537
        for block in blocks:  # line 538
            if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:  # line 539
                pass  # TODO print some previous and following lines - which aren't accessible here anymore  # line 540
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 541
                for no, line in enumerate(block.lines):  # line 542
                    print("+++ %04d |%s|" % (no + block.line, line))  # line 543
            elif block.tipe == MergeBlockType.REMOVE:  # line 544
                for no, line in enumerate(block.lines):  # line 545
                    print("--- %04d |%s|" % (no + block.line, line))  # line 546
            elif block.tipe == MergeBlockType.REPLACE:  # TODO for MODIFY also show intra-line change ranges (TODO remove if that code was also removed)  # line 547
                for no, line in enumerate(block.replaces.lines):  # line 548
                    print("- | %04d |%s|" % (no + block.replaces.line, line))  # line 549
                for no, line in enumerate(block.lines):  # line 550
                    print("+ | %04d |%s|" % (no + block.line, line))  # line 551
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 555
    ''' Create new revision from file tree changes vs. last commit. '''  # line 556
    m = Metadata(os.getcwd())  # type: Metadata  # line 557
    if argument is not None and argument in m.tags:  # line 558
        Exit("Illegal commit message. It was already used as a tag name")  # line 558
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 559
    if m.picky and not trackingPatterns:  # line 560
        Exit("No file patterns staged for commit in picky mode")  # line 560
    changes = None  # type: ChangeSet  # line 561
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but abort if no changes  # line 562
    info((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 563
    m.integrateChangeset(changes, clear=True)  # update pathset to changeset only  # line 564
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 565
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 566
    m.saveBranch(m.branch)  # line 567
    m.loadBranches()  # TODO is it necessary to load again?  # line 568
    if m.picky:  # line 569
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 570
    else:  # track or simple mode  # line 571
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # set branch dirty  # line 572
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 573
        m.tags.append(argument)  # memorize unique tag  # line 573
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 573
    m.saveBranches()  # line 574
    info("Created new revision r%02d%s (+%02d/-%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))  # TODO show compression factor  # line 575

def status(options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 577
    ''' Show branches and current repository state. '''  # line 578
    m = Metadata(os.getcwd())  # type: Metadata  # line 579
    current = m.branch  # type: int  # line 580
    strict = '--strict' in options or m.strict  # type: bool  # line 581
    info(MARKER + " Offline repository status")  # line 582
    info("Repository version:  %s" % m.version)  # line 583
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 584
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 585
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 586
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 587
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps, progress=True)  # type: ChangeSet  # line 588
    print("File tree %s" % ("has changes vs. last revision of current branch" if modified(changes) else "is unchanged"))  # line 589
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 590
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 591
        m.loadBranch(branch.number)  # knows commit history  # line 592
        print("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 593
    if m.track or m.picky and len(m.branches[m.branch].tracked) > 0:  # line 594
        info("\nTracked file patterns:")  # line 595
        print(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 596

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str]]':  # line 598
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags. '''  # line 603
    m = Metadata(os.getcwd())  # type: Metadata  # line 604
    force = '--force' in options  # type: bool  # line 605
    strict = '--strict' in options or m.strict  # type: bool  # line 606
    if argument is not None:  # line 607
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 608
        if branch is None:  # line 609
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 609
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 610

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 613
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 614
    changes = m.findChanges(m.branch if commit else None, max(m.commits) + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 615
    if check and modified(changes) and not force:  # line 616
        m.listChanges(changes)  # line 617
        if not commit:  # line 618
            Exit("File tree contains changes. Use --force to proceed")  # line 618
    elif commit and not force:  #  and not check  # line 619
        Exit("Nothing to commit")  #  and not check  # line 619

    if argument is not None:  # branch/revision specified  # line 621
        m.loadBranch(branch)  # knows commits of target branch  # line 622
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 623
        if revision < 0 or revision > max(m.commits):  # line 624
            Exit("Unknown revision r%02d" % revision)  # line 624
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch))  # line 625
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns)  # line 626

def switch(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 628
    ''' Continue work on another branch, replacing file tree changes. '''  # line 629
    changes = None  # type: ChangeSet  # line 630
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options)  # line 631
    info(MARKER + " Switching to branch %sb%02d/r%02d" % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 632

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 635
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked)  # line 636
    else:  # full file switch  # line 637
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 638
        changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 639
        if not modified(changes):  # line 640
            info("No changes to current file tree")  # line 641
        else:  # integration required  # line 642
            for path, pinfo in changes.deletions.items():  # line 643
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 644
                print("ADD " + path)  # line 645
            for path, pinfo in changes.additions.items():  # line 646
                os.unlink(os.path.join(m.root, path.replace(SLASH, os.sep)))  # is added in current file tree: remove from branch to reach target  # line 647
                print("DEL " + path)  # line 648
            for path, pinfo in changes.modifications.items():  # line 649
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 650
                print("MOD " + path)  # line 651
    m.branch = branch  # line 652
    m.saveBranches()  # store switched path info  # line 653
    info("Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 654

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 656
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 660
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 661
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 662
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 663
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 664
    m = Metadata(os.getcwd())  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 665
    changes = None  # type: ChangeSet  # line 666
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 667
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 668
    debug("Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 669

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 672
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 673
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingUnion), dontConsider=excps, progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 674
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 675
        if trackingUnion != trackingPatterns:  # nothing added  # line 676
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 677
        else:  # line 678
            info("Nothing to update")  # but write back updated branch info below  # line 679
    else:  # integration required  # line 680
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 681
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 682
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 682
            print("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 683
        for path, pinfo in changes.additions.items():  # line 684
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 685
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 685
            if mrg.value & MergeOperation.REMOVE.value:  # line 686
                os.unlink(m.root + os.sep + path.replace(SLASH, os.sep))  # line 686
            print("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 687
        for path, pinfo in changes.modifications.items():  # line 688
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 689
            binary = not m.isTextType(path)  # type: bool  # line 690
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 691
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 692
                print(("MOD " if not binary else "BIN ") + path)  # line 693
                while True:  # line 694
                    print(into)  # TODO print mtime, size differences?  # line 695
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 696
                    if op in ("it" if binary else "itm"):  # line 697
                        break  # line 697
            if op == "t":  # line 698
                print("THR " + path)  # blockwise copy of contents  # line 699
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 699
            elif op == "m":  # line 700
                current = None  # type: bytes  # line 701
                with open(into, "rb") as fd:  # TODO slurps file  # line 702
                    current = fd.read()  # TODO slurps file  # line 702
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 703
                if current == file:  # line 704
                    debug("No difference to versioned file")  # line 704
                elif file is not None:  # if None, error message was already logged  # line 705
                    contents = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # type: bytes  # line 706
                    if contents != current:  # line 707
                        with open(path, "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 708
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 708
                    else:  # TODO but update timestamp?  # line 709
                        debug("No change")  # TODO but update timestamp?  # line 709
            else:  # mine or wrong input  # line 710
                print("MNE " + path)  # nothing to do! same as skip  # line 711
    info("Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 712
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 713
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 714
    m.saveBranches()  # line 715

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 717
    ''' Remove a branch entirely. '''  # line 718
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options)  # line 719
    if len(m.branches) == 1:  # line 720
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 720
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 721
    if branch is None or branch not in m.branches:  # line 722
        Exit("Cannot delete unknown branch %r" % branch)  # line 722
    debug("Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 723
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 724
    info("Branch b%02d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 725

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 727
    ''' Add a tracked files pattern to current branch's tracked files. '''  # line 728
    force = '--force' in options  # type: bool  # line 729
    m = Metadata(os.getcwd())  # type: Metadata  # line 730
    if not m.track and not m.picky:  # line 731
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 731
    if pattern in m.branches[m.branch].tracked:  # line 732
        Exit("Pattern '%s' already tracked" % pattern)  # line 732
    if not force and not os.path.exists(relPath.replace(SLASH, os.sep)):  # line 733
        Exit("The pattern folder doesn't exist. Use --force to add it anyway")  # line 733
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 734
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 735
    m.branches[m.branch].tracked.append(pattern)  # line 736
    m.saveBranches()  # line 737
    info("Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 738

def remove(relPath: 'str', pattern: 'str'):  # line 740
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 741
    m = Metadata(os.getcwd())  # type: Metadata  # line 742
    if not m.track and not m.picky:  # line 743
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 743
    if pattern not in m.branches[m.branch].tracked:  # line 744
        suggestion = _coconut.set()  # type: Set[str]  # line 745
        for pat in m.branches[m.branch].tracked:  # line 746
            if fnmatch.fnmatch(pattern, pat):  # line 747
                suggestion.add(pat)  # line 747
        if suggestion:  # TODO use same wording as in move  # line 748
            print("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 748
        Exit("Tracked pattern '%s' not found" % pattern)  # line 749
    m.branches[m.branch].tracked.remove(pattern)  # line 750
    m.saveBranches()  # line 751
    info("Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 752

def ls(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 754
    ''' List specified directory, augmenting with repository metadata. '''  # line 755
    folder = "." if argument is None else argument  # type: str  # line 756
    m = Metadata(os.getcwd())  # type: Metadata  # line 757
    info("Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 758
    relPath = os.path.relpath(folder, m.root).replace(os.sep, SLASH)  # type: str  # line 759
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 760
    if '--tags' in options:  # line 761
        print(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 762
        return  # line 763
    if '--patterns' in options:  # line 764
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 765
        if out:  # line 766
            print(out)  # line 766
        return  # line 767
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 768
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 769
        ignore = None  # type: _coconut.typing.Optional[str]  # line 770
        for ig in m.c.ignores:  # line 771
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 772
                ignore = ig  # remember first match  # line 772
                break  # remember first match  # line 772
        if ig:  # line 773
            for wl in m.c.ignoresWhitelist:  # line 774
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 775
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 775
                    break  # found a white list entry for ignored file, undo ignoring it  # line 775
        matches = []  # type: List[str]  # line 776
        if not ignore:  # line 777
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 778
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 779
                    matches.append(os.path.basename(pattern))  # line 779
        matches.sort(key=lambda element: len(element))  # line 780
        print("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "..."), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 781

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 783
    ''' List previous commits on current branch. '''  # line 784
    m = Metadata(os.getcwd())  # type: Metadata  # line 785
    m.loadBranch(m.branch)  # knows commit history  # line 786
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + " Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 787
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 788
    changeset = m.computeSequentialPathSetIterator(m.branch, max(m.commits))  # line 789
    maxWidth = max([wcswidth((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) for commit in m.commits.values()])  # type: int  # line 790
    for no in range(max(m.commits) + 1):  # line 791
        commit = m.commits[no]  # type: CommitInfo  # line 792
        changes = next(changeset)  # type: ChangeSet  # side-effect: updates m.paths  # line 793
        newTextFiles = len([file for file in changes.additions.keys() if m.isTextType(file)])  # type: int  # line 794
        print("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT/%05.1f%%) |%s|%s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(changes.additions), len(changes.deletions), len(changes.modifications), newTextFiles, 0. if len(changes.additions) == 0 else newTextFiles * 100. / len(changes.additions), ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)).ljust(maxWidth), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 795
        if '--changes' in options:  # line 796
            m.listChanges(changes)  # line 796
        if '--diff' in options:  # TODO needs to extract code from diff first to be reused here  # line 797
            pass  # TODO needs to extract code from diff first to be reused here  # line 797

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 799
    ''' Exported entire repository as archive for easy transfer. '''  # line 800
    force = '--force' in options  # type: bool  # line 801
    progress = '--progress' in options  # type: bool  # line 802
    import zipfile  # TODO display compression ratio (if any)  # line 803
    try:  # line 804
        import zlib  # line 804
        compression = zipfile.ZIP_DEFLATED  # line 804
    except:  # line 805
        compression = zipfile.ZIP_STORED  # line 805

    if argument is None:  # line 807
        Exit("Argument missing (target filename)")  # line 807
    argument = argument if "." in argument else argument + ".sos.zip"  # line 808
    if os.path.exists(argument) and not force:  # line 809
        Exit("Target archive already exists. Use 'sos dump <arget> --force' to override")  # line 809
    with zipfile.ZipFile(argument, "w", compression) as fd:  # line 810
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 811
        counter = Counter(-1)  # type: Counter  # line 812
        timer = time.time()  # type: float  # line 812
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 813
            for filename in filenames:  # line 814
                newtime = time.time()  # type: float  # TODO alternatively count bytes and use a threshold there  # line 815
                if progress and newtime - timer > .1:  # line 816
                    sys.stdout.write("Dumping %s %s\r" % (PROGRESS_MARKER[int(counter.inc() % 4)], filename))  # line 816
                    sys.stdout.flush()  # line 816
                    timer = newtime  # line 816
                abspath = os.path.join(dirpath, filename)  # type: str  # line 817
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 818
                fd.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 819

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 821
    command, key, value = (arguments + [None] * 3)[:3]  # line 822
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 823
        Exit("Unknown config command")  # line 823
    local = "--local" in options  # type: bool  # line 824
    m = Metadata(os.getcwd())  # type: Metadata  # loads layerd configuration as well. TODO warning if repo not exists  # line 825
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 826
    if command == "set":  # line 827
        if None in (key, value):  # line 828
            Exit("Key or value not specified")  # line 828
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 829
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 829
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 830
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 830
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (value.strip() if key not in CONFIGURABLE_LISTS else safeSplit(value, ";"))  # TODO sanitize texts?  # line 831
    elif command == "unset":  # line 832
        if key is None:  # line 833
            Exit("No key specified")  # line 833
        if key not in c.keys():  # line 834
            Exit("Unknown key")  # line 834
        del c[key]  # line 835
    elif command == "add":  # line 836
        if None in (key, value):  # line 837
            Exit("Key or value not specified")  # line 837
        if key not in CONFIGURABLE_LISTS:  # line 838
            Exit("Unsupported key %r" % key)  # line 838
        if key not in c.keys():  # add list  # line 839
            c[key] = [value]  # add list  # line 839
        elif value in c[key]:  # line 840
            Exit("Value already contained, nothing to do")  # line 840
        c[key].append(value)  # line 841
    elif command == "rm":  # line 842
        if None in (key, value):  # line 843
            Exit("Key or value not specified")  # line 843
        if key not in c.keys():  # line 844
            Exit("Unknown key %r" % key)  # line 844
        if value not in c[key]:  # line 845
            Exit("Unknown value %r" % value)  # line 845
        c[key].remove(value)  # line 846
    else:  # Show or list  # line 847
        if key == "flags":  # list valid configuration items  # line 848
            print(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 848
        elif key == "lists":  # line 849
            print(", ".join(CONFIGURABLE_LISTS))  # line 849
        elif key == "texts":  # line 850
            print(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 850
        else:  # line 851
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 852
            c = m.c  # always use full configuration chain  # line 853
            try:  # attempt single key  # line 854
                assert key is not None  # line 855
                c[key]  # line 855
                l = key in c.keys()  # type: bool  # line 856
                g = key in c.__defaults.keys()  # type: bool  # line 856
                print("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 857
            except:  # normal value listing  # line 858
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 859
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 860
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 861
                for k, vt in sorted(vals.items()):  # line 862
                    print("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 862
                if len(c.keys()) == 0:  # line 863
                    info("No local configuration stored")  # line 863
                if len(c.__defaults.keys()) == 0:  # line 864
                    info("No global configuration stored")  # line 864
        return  # in case of list, no need to store anything  # line 865
    if local:  # saves changes of repoConfig  # line 866
        m.repoConf = c.__map  # saves changes of repoConfig  # line 866
        m.saveBranches()  # saves changes of repoConfig  # line 866
        Exit("OK", code=0)  # saves changes of repoConfig  # line 866
    else:  # global config  # line 867
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 868
        if f is None:  # line 869
            error("Error saving user configuration: %r" % h)  # line 869
        else:  # line 870
            Exit("OK", code=0)  # line 870

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[]):  # line 872
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique. '''  # line 873
    force = '--force' in options  # type: bool  # line 874
    soft = '--soft' in options  # type: bool  # line 875
    if not os.path.exists(relPath.replace(SLASH, os.sep)) and not force:  # line 876
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 876
    m = Metadata(os.getcwd())  # type: Metadata  # line 877
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(relPath.replace(SLASH, os.sep)) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 878
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 879
    if not matching and not force:  # line 880
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 880
    if not m.track and not m.picky:  # line 881
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 881
    if pattern not in m.branches[m.branch].tracked:  # line 882
        for tracked in (t for t in m.branches[m.branch].tracked if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 883
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 884
            if alternative:  # line 885
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 885
        if not (force or soft):  # line 886
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 886
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 887
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 888
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 889
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 893
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 894
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 894
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 895
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 896
    if len({st[1] for st in matches}) != len(matches):  # line 897
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 897
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 898
    if os.path.exists(newRelPath):  # line 899
        exists = [filename[1] for filename in matches if os.path.exists(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep))]  # type: _coconut.typing.Sequence[str]  # line 900
        if exists and not (force or soft):  # line 901
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 901
    else:  # line 902
        os.makedirs(os.path.abspath(newRelPath.replace(SLASH, os.sep)))  # line 902
    if not soft:  # perform actual renaming  # line 903
        for (source, target) in matches:  # line 904
            try:  # line 905
                shutil.move(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep)), os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep)))  # line 905
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 906
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 906
    m.branches[m.branch].tracked[m.branches[m.branch].tracked.index(pattern)] = newPattern  # line 907
    m.saveBranches()  # line 908

def parse(root: 'str', cwd: 'str'):  # line 910
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm. '''  # line 911
    debug("Parsing command-line arguments...")  # line 912
    try:  # line 913
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 914
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # line 915
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 916
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 917
        debug("Processing command %r with arguments %r and options %r." % (("" if command is None else command), arguments if arguments else "", options))  # line 918
        if command[:1] in "amr":  # line 919
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 919
        if command[:1] == "m":  # line 920
            if len(arguments) < 2:  # line 921
                Exit("Need a second file pattern argument as target for move/rename command")  # line 921
            newRelPath, newPattern = relativize(root, os.path.join(cwd, options[0]))  # line 922
        if command[:1] == "a":  # line 923
            add(relPath, pattern, options)  # line 923
        elif command[:1] == "b":  # line 924
            branch(arguments[0], options)  # line 924
        elif command[:2] == "ch":  # line 925
            changes(arguments[0], options, onlys, excps)  # line 925
        elif command[:3] == "com":  # line 926
            commit(arguments[0], options, onlys, excps)  # line 926
        elif command[:2] == "ci":  # line 927
            commit(arguments[0], options, onlys, excps)  # line 927
        elif command[:3] == 'con':  # line 928
            config(arguments, options)  # line 928
        elif command[:2] == "de":  # line 929
            delete(arguments[0], options)  # line 929
        elif command[:2] == "di":  # line 930
            diff(arguments[0], options, onlys, excps)  # line 930
        elif command[:2] == "du":  # line 931
            dump(arguments[0], options)  # line 931
        elif command[:1] == "h":  # line 932
            usage()  # line 932
        elif command[:2] == "lo":  # line 933
            log(options)  # line 933
        elif command[:2] == "li":  # TODO handle absolute paths as well, also for Windows? think through  # line 934
            ls(relativize(root, cwd if not arguments else os.path.join(cwd, arguments[0]))[1], options)  # TODO handle absolute paths as well, also for Windows? think through  # line 934
        elif command[:2] == "ls":  # TODO avoid and/or normalize root super paths (..)  # line 935
            ls(relativize(root, cwd if not arguments else os.path.join(cwd, arguments[0]))[1], options)  # TODO avoid and/or normalize root super paths (..)  # line 935
        elif command[:1] == "m":  # line 936
            move(relPath, pattern, newRelPath, newPattern, options[1:])  # line 936
        elif command[:2] == "of":  # line 937
            offline(arguments[0], options)  # line 937
        elif command[:2] == "on":  # line 938
            online(options)  # line 938
        elif command[:1] == "r":  # line 939
            remove(relPath, pattern)  # line 939
        elif command[:2] == "st":  # line 940
            status(options, onlys, excps)  # line 940
        elif command[:2] == "sw":  # line 941
            switch(arguments[0], options, onlys, excps)  # line 941
        elif command[:1] == "u":  # line 942
            update(arguments[0], options, onlys, excps)  # line 942
        elif command[:1] == "v":  # line 943
            usage(short=True)  # line 943
        else:  # line 944
            Exit("Unknown command '%s'" % command)  # line 944
        Exit(code=0)  # line 945
    except (Exception, RuntimeError) as E:  # line 946
        print(str(E))  # line 947
        import traceback  # line 948
        traceback.print_exc()  # line 949
        traceback.print_stack()  # line 950
        try:  # line 951
            traceback.print_last()  # line 951
        except:  # line 952
            pass  # line 952
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing.")  # line 953

def main():  # line 955
    global debug, info, warn, error  # line 956
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 957
    _log = Logger(logging.getLogger(__name__))  # line 958
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 958
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 959
        sys.argv.remove(option)  # clean up program arguments  # line 959
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 960
        usage()  # line 960
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 961
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 962
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 963
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 964
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in ["h", "v"]:  # in offline mode or just going offline TODO what about git config?  # line 965
        cwd = os.getcwd()  # line 966
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 967
        parse(root, cwd)  # line 968
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 969
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 970
        import subprocess  # only required in this section  # line 971
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 972
        inp = ""  # type: str  # line 973
        while True:  # line 974
            so, se = process.communicate(input=inp)  # line 975
            if process.returncode is not None:  # line 976
                break  # line 976
            inp = sys.stdin.read()  # line 977
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 978
            if root is None:  # line 979
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 979
            m = Metadata(root)  # type: Metadata  # line 980
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 981
            m.saveBranches()  # line 982
    else:  # line 983
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 983


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 987
level = logging.DEBUG if verbose else logging.INFO  # line 988
force_sos = '--sos' in sys.argv  # type: bool  # line 989
force_vcs = '--vcs' in sys.argv  # type: bool  # line 990
_log = Logger(logging.getLogger(__name__))  # line 991
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 991
if __name__ == '__main__':  # line 992
    main()  # line 992
