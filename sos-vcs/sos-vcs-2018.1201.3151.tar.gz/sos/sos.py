#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xd89c727

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
try:  # optional dependency  # line 18
    import configr  # optional dependency  # line 18
except:  # declare as undefined  # line 19
    configr = None  # declare as undefined  # line 19
#from enforce import runtime_validation  # https://github.com/RussBaz/enforce  TODO doesn't work for "data" types


# Constants
MARKER = r"/###/"  # line 24
APPNAME = "Subversion Offline Solution V%s (C) Arne Bachmann" % version.__release_version__  # type: str  # line 25
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": False, "texttype": [], "bintype": [], "ignoreDirs": [".*", "__pycache__"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout", "_FOSSIL_"], "ignoresWhitelist": []})  # line 26
termWidth = getTermWidth() - 1  # uses curses or returns conservative default of 80  # line 27


# Functions
def loadConfig() -> 'Union[configr.Configr, Accessor]':  # Accessor when using defaults only  # line 31
    ''' Simplifies loading config from file system or returning the defaults. '''  # line 32
    config = None  # type: Union[configr.Configr, Accessor]  # line 33
    if not configr:  # this only applies for the case that configr is not available, thus no settings will be persisted anyway  # line 34
        return defaults  # this only applies for the case that configr is not available, thus no settings will be persisted anyway  # line 34
    config = configr.Configr("sos", defaults=defaults)  # defaults are used if key is not configured, but won't be saved  # line 35
    f, g = config.loadSettings(clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # line 36
    if f is None:  # line 37
        debug("Encountered a problem while loading the user configuration: %r" % g)  # line 37
    return config  # line 38

@_coconut_tco  # line 40
def saveConfig(config: 'configr.Configr') -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[Exception]]':  # line 40
    return _coconut_tail_call(config.saveSettings, clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # line 41

def usage(short: 'bool'=False) -> 'None':  # line 43
    print("{marker} {appname}{version}".format(marker=MARKER, appname=APPNAME, version="" if not short else " (PyPI: %s)" % version.__version__))  # line 44
    if not short:  # line 45
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
    --verbose                    Enable verbose output, including show compression ratios""".format(appname=APPNAME, cmd="sos", CMD="SOS"))  # line 124
    Exit(code=0)  # line 125

# Main data class
#@runtime_validation
class Metadata:  # line 129
    ''' This class doesn't represent the entire repository state in memory,
      but serves as a container for different repo operations,
      using only parts of its attributes at any point in time. Use with care.
  '''  # line 133

    def __init__(_, path: 'str') -> 'None':  # line 135
        ''' Create empty container object for various repository operations. '''  # line 136
        _.c = loadConfig()  # line 137
        _.root = path  # type: str  # line 138
        _.branches = {}  # type: Dict[int, BranchInfo]  # branch number zero represents the initial state at branching  # line 139
        _.commits = {}  # type: Dict[int, CommitInfo]  # consecutive numbers per branch, starting at 0  # line 140
        _.paths = {}  # type: Dict[str, PathInfo]  # utf-8 encoded relative, normalized file system paths  # line 141
        _.tags = []  # type: List[str]  # line 142
        _.branch = None  # type: _coconut.typing.Optional[int]  # current branch number  # line 143
        _.commit = None  # type: _coconut.typing.Optional[int]  # current revision number  # line 144
        _.track = _.c.track  # type: bool  # track file name patterns in the repository (per branch)  # line 145
        _.picky = _.c.picky  # type: bool  # pick files to commit per operation  # line 146
        _.strict = _.c.strict  # type: bool  # be always strict (regarding file contents comparsion)  # line 147
        _.compress = _.c.compress  # type: bool  # these flags are stored in the repository  # line 148

    def isTextType(_, filename: 'str') -> 'bool':  # line 150
        return (((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(mimetypes.guess_type(filename)[0])).startswith("text/") or any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.texttype])) and not any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.bintype])  # line 150

    def listChanges(_, changes: 'ChangeSet') -> 'None':  # line 152
        if len(changes.additions) > 0:  # line 153
            print(ajoin("ADD ", sorted(changes.additions.keys()), "\n"))  # line 153
        if len(changes.deletions) > 0:  # line 154
            print(ajoin("DEL ", sorted(changes.deletions.keys()), "\n"))  # line 154
        if len(changes.modifications) > 0:  # line 155
            print(ajoin("MOD ", sorted(changes.modifications.keys()), "\n"))  # line 155

    def loadBranches(_) -> 'None':  # line 157
        ''' Load list of branches and current branch info from metadata file. '''  # line 158
        try:  # fails if not yet created (on initial branch/commit)  # line 159
            branches = None  # type: List[Tuple]  # line 160
            with codecs.open(os.path.join(_.root, metaFolder, metaFile), "r", encoding=UTF8) as fd:  # line 161
                flags, branches = json.load(fd)  # line 162
            _.tags = flags["tags"]  # list of commit messages to treat as globally unique tags  # line 163
            _.branch = flags["branch"]  # current branch integer  # line 164
            _.track = flags["track"]  # line 165
            _.picky = flags["picky"]  # line 166
            _.strict = flags["strict"]  # line 167
            _.compress = flags["compress"]  # line 168
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 169
        except Exception as E:  # if not found, create metadata folder  # line 170
            _.branches = {}  # line 171
            warn("Couldn't read branches metadata: %r" % E)  # line 172

    def saveBranches(_) -> 'None':  # line 174
        ''' Save list of branches and current branch info to metadata file. '''  # line 175
        with codecs.open(os.path.join(_.root, metaFolder, metaFile), "w", encoding=UTF8) as fd:  # line 176
            json.dump(({"tags": _.tags, "branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}, list(_.branches.values())), fd, ensure_ascii=False)  # line 177

    def getRevisionByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 179
        ''' Convenience accessor for named revisions (using commit message as name). '''  # line 180
        if name == "":  # line 181
            return -1  # line 181
        try:  # attempt to parse integer string  # line 182
            return int(name)  # attempt to parse integer string  # line 182
        except ValueError:  # line 183
            pass  # line 183
        found = [number for number, commit in _.commits.items() if name == commit.message]  # find any revision by commit message (usually used for tags)  # TODO only allow finding real tags?  # line 184
        return found[0] if found else None  # line 185

    def getBranchByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 187
        ''' Convenience accessor for named branches. '''  # line 188
        if name == "":  # line 189
            return _.branch  # line 189
        try:  # attempt to parse integer string  # line 190
            return int(name)  # attempt to parse integer string  # line 190
        except ValueError:  # line 191
            pass  # line 191
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 192
        return found[0] if found else None  # line 193

    def loadBranch(_, branch: 'int') -> 'None':  # line 195
        ''' Load all commit information from a branch meta data file. '''  # line 196
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "r", encoding=UTF8) as fd:  # line 197
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 198
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 199
        _.branch = branch  # line 200

    def saveBranch(_, branch: 'int') -> 'None':  # line 202
        ''' Save all commit information to a branch meta data file. '''  # line 203
        with codecs.open(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile), "w", encoding=UTF8) as fd:  # line 204
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 205

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]') -> 'None':  # line 207
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 212
        debug("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 213
        tracked = [t for t in _.branches[_.branch].tracked]  # copy  # line 214
        os.makedirs(branchFolder(branch, 0, base=_.root))  # line 215
        _.loadBranch(_.branch)  # line 216
        revision = max(_.commits)  # type: int  # line 217
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 218
        for path, pinfo in _.paths.items():  # line 219
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 220
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 221
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 222
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 223
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].inSync, tracked)  # save branch info, before storing repo state at caller  # line 224

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 226
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 231
        simpleMode = not (_.track or _.picky)  # line 232
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # in case of initial branch creation  # line 233
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 234
        _.paths = {}  # type: Dict[str, PathInfo]  # line 235
        if simpleMode:  # branches from file system state  # line 236
            changes = _.findChanges(branch, 0, progress=simpleMode)  # type: ChangeSet  # creates revision folder and versioned files  # line 237
            _.listChanges(changes)  # line 238
            _.paths.update(changes.additions.items())  # line 239
        else:  # tracking or picky mode: branch from lastest revision  # line 240
            os.makedirs(branchFolder(branch, 0, base=_.root))  # line 241
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 242
                _.loadBranch(_.branch)  # line 243
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 244
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 245
                for path, pinfo in _.paths.items():  # line 246
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 247
        ts = int(time.time() * 1000)  # line 248
        _.commits = {0: CommitInfo(0, ts, ("Branched on %s" % strftime(ts) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 249
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 250
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 251
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked)  # save branch info, in case it is needed  # line 252

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 254
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 255
        shutil.rmtree(os.path.join(_.root, metaFolder, "b%d" % branch))  # line 256
        binfo = _.branches[branch]  # line 257
        del _.branches[branch]  # line 258
        _.branch = max(_.branches)  # line 259
        _.saveBranches()  # line 260
        _.commits.clear()  # line 261
        return binfo  # line 262

    def loadCommit(_, branch: 'int', revision: 'int') -> 'None':  # line 264
        ''' Load all file information from a commit meta data. '''  # line 265
        with codecs.open(branchFolder(branch, revision, base=_.root, file=metaFile), "r", encoding=UTF8) as fd:  # line 266
            _.paths = json.load(fd)  # line 267
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 268
        _.branch = branch  # line 269

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 271
        ''' Save all file information to a commit meta data file. '''  # line 272
        target = branchFolder(branch, revision, base=_.root)  # line 273
        try:  # line 274
            os.makedirs(target)  # line 274
        except:  # line 275
            pass  # line 275
        with codecs.open(os.path.join(target, metaFile), "w", encoding=UTF8) as fd:  # line 276
            json.dump(_.paths, fd, ensure_ascii=False)  # line 277

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'ChangeSet':  # line 279
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        The function returns the state of file tree *differences*, unless "inverse" is True -> then return original data
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes
        progress: Show file names during processing
    '''  # line 288
        write = branch is not None and revision is not None  # line 289
        if write:  # line 290
            try:  # line 291
                os.makedirs(branchFolder(branch, revision, base=_.root))  # line 291
            except FileExistsError:  # HINT "try" only necessary for testing hash collisions  # line 292
                pass  # HINT "try" only necessary for testing hash collisions  # line 292
        changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 293
        counter = Counter(-1)  # type: Counter  # line 294
        timer = time.time()  # type: float  # line 294
        hashed = None  # type: _coconut.typing.Optional[str]  # line 295
        written = None  # type: int  # line 295
        compressed = 0  # type: int  # line 295
        original = 0  # type: int  # line 295
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 296
        for path, pinfo in _.paths.items():  # line 297
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 298
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 301
        for path, dirnames, filenames in os.walk(_.root):  # line 302
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 303
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 304
            dirnames.sort()  # line 305
            filenames.sort()  # line 305
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 306
            walk = filenames if considerOnly is None else list(reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # line 307
            if dontConsider:  # line 308
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 309
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 310
                filename = relPath + SLASH + file  # line 311
                filepath = os.path.join(path, file)  # line 312
                stat = os.stat(filepath)  # line 313
                size, mtime, newtime = stat.st_size, int(stat.st_mtime * 1000), time.time()  # line 314
                if progress and newtime - timer > .1:  # line 315
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", PROGRESS_MARKER[int(counter.inc() % 4)], filename)  # line 316
                    sys.stdout.write(outstring + " " * max(0, termWidth - len(outstring)))  # TODO could write to new line instead of carriage return (still true?)  # line 317
                    sys.stdout.flush()  # TODO could write to new line instead of carriage return (still true?)  # line 317
                    timer = newtime  # TODO could write to new line instead of carriage return (still true?)  # line 317
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 318
                    nameHash = hashStr(filename)  # line 319
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=nameHash) if write else None) if size > 0 else (None, 0)  # line 320
                    changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 321
                    compressed += written  # line 322
                    original += size  # line 322
                    continue  # line 323
                last = _.paths[filename]  # filename is known - check for modifications  # line 324
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 325
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if size > 0 else (None, 0)  # line 326
                    changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 327
                    continue  # line 327
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and hashFile(filepath, _.compress)[0] != last.hash):  # detected a modification  # line 328
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 329
                    changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 330
                else:  # line 331
                    continue  # line 331
                compressed += written  # line 332
                original += last.size if inverse else size  # line 332
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 333
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 333
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 334
            for file in names:  # line 335
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 336
                    continue  # don't mark ignored files as deleted  # line 336
                pth = path + SLASH + file  # type: str  # line 337
                changes.deletions[pth] = _.paths[pth]  # line 338
        if progress:  # force new line  # line 339
            print("\rPreparation finished.%s" % (" Compression advantage %s" % ("is %.1f%%" % (original * 100. / compressed - 100.) if compressed > 0 else "cannot be computed") if _.compress else "").ljust(termWidth), file=sys.stdout)  # force new line  # line 339
        else:  # line 340
            debug("Finished detecting changes.%s" % (" Compression advantage %s" % ("is %.1f%%" % (original * 100. / compressed - 100.) if compressed > 0 else "cannot be computed") if _.compress else ""))  # line 340
        return changes  # line 341

    def integrateChangeset(_, changes: 'ChangeSet', clear=False) -> 'None':  # line 343
        ''' In-memory update from a changeset, marking deleted files with size=None. Use clear = True to start on an empty path set. '''  # line 344
        if clear:  # line 345
            _.paths.clear()  # line 345
        else:  # line 346
            rm = [p for p, info in _.paths.items() if info.size is None]  # remove files deleted in earlier change sets (revisions)  # line 347
            for old in rm:  # remove previously removed entries completely  # line 348
                del _.paths[old]  # remove previously removed entries completely  # line 348
        for d, info in changes.deletions.items():  # mark now removed entries as deleted  # line 349
            _.paths[d] = PathInfo(info.nameHash, None, info.mtime, None)  # mark now removed entries as deleted  # line 349
        _.paths.update(changes.additions)  # line 350
        _.paths.update(changes.modifications)  # line 351

    def computeSequentialPathSet(_, branch: 'int', revision: 'int') -> 'None':  # line 353
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once  # line 354

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[ChangeSet]]':  # line 356
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 357
        _.loadCommit(branch, 0)  # load initial paths  # line 358
        if incrementally:  # line 359
            yield diffPathSets({}, _.paths)  # line 359
        n = Metadata(_.root)  # type: Metadata  # next changes  # line 360
        for revision in range(1, revision + 1):  # line 361
            n.loadCommit(branch, revision)  # line 362
            changes = diffPathSets(_.paths, n.paths)  # type: ChangeSet  # line 363
            _.integrateChangeset(changes)  # line 364
            if incrementally:  # line 365
                yield changes  # line 365
        yield None  # for the default case - not incrementally  # line 366

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 368
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 371
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 372
            return (_.branch, -1)  # no branch/revision specified  # line 372
        argument = argument.strip()  # line 373
        if argument.startswith(SLASH):  # current branch  # line 374
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 374
        if argument.endswith(SLASH):  # line 375
            try:  # line 376
                return (_.getBranchByName(argument[:-1]), -1)  # line 376
            except ValueError:  # line 377
                Exit("Unknown branch label '%s'" % argument)  # line 377
        if SLASH in argument:  # line 378
            b, r = argument.split(SLASH)[:2]  # line 379
            try:  # line 380
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 380
            except ValueError:  # line 381
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 381
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 382
        if branch not in _.branches:  # line 383
            branch = None  # line 383
        try:  # either branch name/number or reverse/absolute revision number  # line 384
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 384
        except:  # line 385
            Exit("Unknown branch label or wrong number format")  # line 385
        Exit("This should never happen. Please create a issue report")  # line 386
        return (None, None)  # line 386

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 388
        while True:  # find latest revision that contained the file physically  # line 389
            source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 390
            if os.path.exists(source) and os.path.isfile(source):  # line 391
                break  # line 391
            revision -= 1  # line 392
            if revision < 0:  # line 393
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 393
        return revision, source  # line 394

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo') -> 'None':  # line 396
        ''' Copy versioned file to other branch/revision. '''  # line 397
        target = branchFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 398
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 399
        shutil.copy2(source, target)  # line 400

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 402
        ''' Return file contents, or copy contents into file path provided. '''  # line 403
        source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 404
        try:  # line 405
            with openIt(source, "r", _.compress) as fd:  # line 406
                if toFile is None:  # read bytes into memory and return  # line 407
                    return fd.read()  # read bytes into memory and return  # line 407
                with open(toFile, "wb") as to:  # line 408
                    while True:  # line 409
                        buffer = fd.read(bufSize)  # line 410
                        to.write(buffer)  # line 411
                        if len(buffer) < bufSize:  # line 412
                            break  # line 412
                    return None  # line 413
        except Exception as E:  # line 414
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 414
        return None  # line 415

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 417
        ''' Recreate file for given revision, or return contents if path is None. '''  # line 418
        if relPath is None:  # just return contents  # line 419
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 419
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 420
        if ensurePath:  #  and not os.path.exists(os.path.dirname(target)):  # line 421
            try:  # line 422
                os.makedirs(os.path.dirname(target))  # line 422
            except:  # line 423
                pass  # line 423
        if pinfo.size == 0:  # line 424
            with open(target, "wb"):  # line 425
                pass  # line 425
            try:  # update access/modification timestamps on file system  # line 426
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 426
            except Exception as E:  # line 427
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 427
            return None  # line 428
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 429
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(target, "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 431
            while True:  # line 432
                buffer = fd.read(bufSize)  # line 433
                to.write(buffer)  # line 434
                if len(buffer) < bufSize:  # line 435
                    break  # line 435
        try:  # update access/modification timestamps on file system  # line 436
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 436
        except Exception as E:  # line 437
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 437
        return None  # line 438

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None) -> 'FrozenSet[str]':  # line 440
        ''' Returns list of tracking patterns for provided branch or current branch. '''  # line 441
        return _coconut.frozenset() if not _.track and not _.picky else frozenset(_.branches[_.branch if branch is None else branch].tracked)  # line 442


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 446
    ''' Initial command to start working offline. '''  # line 447
    if os.path.exists(metaFolder):  # line 448
        if '--force' not in options:  # line 449
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 449
        try:  # line 450
            for entry in os.listdir(metaFolder):  # line 451
                resource = metaFolder + os.sep + entry  # line 452
                if os.path.isdir(resource):  # line 453
                    shutil.rmtree(resource)  # line 453
                else:  # line 454
                    os.unlink(resource)  # line 454
        except:  # line 455
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 455
    m = Metadata(os.getcwd())  # type: Metadata  # line 456
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 457
        m.compress = True  # plain file copies instead of compressed ones  # line 457
    if '--picky' in options or m.c.picky:  # Git-like  # line 458
        m.picky = True  # Git-like  # line 458
    elif '--track' in options or m.c.track:  # Svn-like  # line 459
        m.track = True  # Svn-like  # line 459
    if '--strict' in options or m.c.strict:  # always hash contents  # line 460
        m.strict = True  # always hash contents  # line 460
    debug("Preparing offline repository...")  # line 461
    m.createBranch(0, (defaults["defaultbranch"] if argument is None else argument), initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 462
    m.branch = 0  # line 463
    m.saveBranches()  # no change immediately after going offline, going back online won't issue a warning  # line 464
    info("Offline repository prepared. Use 'sos online' to finish offline work")  # line 465

def online(options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 467
    ''' Finish working offline. '''  # line 468
    force = '--force' in options  # type: bool  # line 469
    m = Metadata(os.getcwd())  # line 470
    m.loadBranches()  # line 471
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 472
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 472
    strict = '--strict' in options or m.strict  # type: bool  # line 473
    if options.count("--force") < 2:  # line 474
        changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track and not m.picky else m.getTrackingPatterns(), progress='--progress' in options)  # type: ChangeSet  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 475
        if modified(changes):  # line 476
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 476
    try:  # line 477
        shutil.rmtree(metaFolder)  # line 477
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 477
    except Exception as E:  # line 478
        Exit("Error removing offline repository: %r" % E)  # line 478

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 480
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 481
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 482
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 483
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 484
    m = Metadata(os.getcwd())  # type: Metadata  # line 485
    m.loadBranches()  # line 486
    m.loadBranch(m.branch)  # line 487
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 488
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 488
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 489
    debug("Branching to %sbranch b%02d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 490
    if last:  # line 491
        m.duplicateBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  # branch from branch's last revision  # line 492
    else:  # from file tree state  # line 493
        m.createBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  # branch from current file tree  # line 494
    if not stay:  # line 495
        m.branch = branch  # line 496
        m.saveBranches()  # line 497
    info("%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 498

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 500
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 501
    m = Metadata(os.getcwd())  # type: Metadata  # line 502
    branch = None  # type: _coconut.typing.Optional[int]  # line 502
    revision = None  # type: _coconut.typing.Optional[int]  # line 502
    m.loadBranches()  # knows current branch  # line 503
    strict = '--strict' in options or m.strict  # type: bool  # line 504
    branch, revision = m.parseRevisionString(argument)  # line 505
    if branch not in m.branches:  # line 506
        Exit("Unknown branch")  # line 506
    m.loadBranch(branch)  # knows commits  # line 507
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 508
    if revision < 0 or revision > max(m.commits):  # line 509
        Exit("Unknown revision r%02d" % revision)  # line 509
    info(MARKER + " Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 510
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 511
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 512
    m.listChanges(changes)  # line 513
    return changes  # for unit tests only  # line 514

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'None':  # line 516
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 517
    m = Metadata(os.getcwd())  # type: Metadata  # line 518
    branch = None  # type: _coconut.typing.Optional[int]  # line 518
    revision = None  # type: _coconut.typing.Optional[int]  # line 518
    m.loadBranches()  # knows current branch  # line 519
    strict = '--strict' in options or m.strict  # type: bool  # line 520
    _from = {None: option.split("--from=")[1] for option in options if option.startswith("--from=")}.get(None, None)  # type: _coconut.typing.Optional[str]  # line 521
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 522
    if branch not in m.branches:  # line 523
        Exit("Unknown branch")  # line 523
    m.loadBranch(branch)  # knows commits  # line 524
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 525
    if revision < 0 or revision > max(m.commits):  # line 526
        Exit("Unknown revision r%02d" % revision)  # line 526
    info(MARKER + " Differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 527
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 528
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 529
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 530
    if modified(onlyBinaryModifications):  # line 531
        debug(MARKER + " File changes")  # line 531
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 532

    if changes.modifications:  # line 534
        debug("%s%s Textual modifications" % ("\n" if modified(onlyBinaryModifications) else "", MARKER))  # line 534
    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 535
        content = None  # type: _coconut.typing.Optional[bytes]  # line 536
        if pinfo.size == 0:  # empty file contents  # line 537
            content = b""  # empty file contents  # line 537
        else:  # versioned file  # line 538
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 538
            assert content is not None  # versioned file  # line 538
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 539
        blocks = merge(filename=abspath, into=content, diffOnly=True)  # type: List[MergeBlock]  # only determine change blocks  # line 540
        print("DIF %s%s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else ""))  # line 541
        for block in blocks:  # line 542
            if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:  # line 543
                pass  # TODO print some previous and following lines - which aren't accessible here anymore  # line 544
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 545
                for no, line in enumerate(block.lines):  # line 546
                    print("+++ %04d |%s|" % (no + block.line, line))  # line 547
            elif block.tipe == MergeBlockType.REMOVE:  # line 548
                for no, line in enumerate(block.lines):  # line 549
                    print("--- %04d |%s|" % (no + block.line, line))  # line 550
            elif block.tipe == MergeBlockType.REPLACE:  # TODO for MODIFY also show intra-line change ranges (TODO remove if that code was also removed)  # line 551
                for no, line in enumerate(block.replaces.lines):  # line 552
                    print("- | %04d |%s|" % (no + block.replaces.line, line))  # line 553
                for no, line in enumerate(block.lines):  # line 554
                    print("+ | %04d |%s|" % (no + block.line, line))  # line 555
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MODIFY:  # intra-line modifications
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'None':  # line 560
    ''' Create new revision from file tree changes vs. last commit. '''  # line 561
    m = Metadata(os.getcwd())  # type: Metadata  # line 562
    m.loadBranches()  # knows current branch  # line 563
    if argument is not None and argument in m.tags:  # line 564
        Exit("Illegal commit message. It was already used as a tag name")  # line 564
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 565
    if m.picky and not trackingPatterns:  # line 566
        Exit("No file patterns staged for commit in picky mode")  # line 566
    changes = None  # type: ChangeSet  # line 567
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but abort if no changes  # line 568
    info((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 569
    m.integrateChangeset(changes, clear=True)  # update pathset to changeset only  # line 570
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 571
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 572
    m.saveBranch(m.branch)  # line 573
    m.loadBranches()  # TODO is it necessary to load again?  # line 574
    if m.picky:  # line 575
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 576
    else:  # track or simple mode  # line 577
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # set branch dirty  # line 578
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 579
        m.tags.append(argument)  # memorize unique tag  # line 579
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 579
    m.saveBranches()  # line 580
    info("Created new revision r%02d%s (+%02d/-%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))  # TODO show compression factor  # line 581

def status(options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'None':  # line 583
    ''' Show branches and current repository state. '''  # line 584
    m = Metadata(os.getcwd())  # type: Metadata  # line 585
    m.loadBranches()  # knows current branch  # line 586
    current = m.branch  # type: int  # line 587
    strict = '--strict' in options or m.strict  # type: bool  # line 588
    info(MARKER + " Offline repository status")  # line 589
    info("Content checking:  %sactivated" % ("" if m.strict else "de"))  # line 590
    info("Data compression:  %sactivated" % ("" if m.compress else "de"))  # line 591
    info("Repository mode:   %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 592
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 593
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps, progress=True)  # type: ChangeSet  # line 594
    print("File tree %s" % ("has changes vs. last revision of current branch" if modified(changes) else "is unchanged"))  # line 595
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 596
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 597
        m.loadBranch(branch.number)  # knows commit history  # line 598
        print("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 599
    if m.track or m.picky and len(m.branches[m.branch].tracked) > 0:  # line 600
        info("\nTracked file patterns:")  # line 601
        print(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 602

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str]]':  # line 604
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags. '''  # line 609
    m = Metadata(os.getcwd())  # type: Metadata  # line 610
    m.loadBranches()  # knows current branch  # line 611
    force = '--force' in options  # type: bool  # line 612
    strict = '--strict' in options or m.strict  # type: bool  # line 613
    if argument is not None:  # line 614
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 615
        if branch is None:  # line 616
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 616
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 617

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 620
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 621
    changes = m.findChanges(m.branch if commit else None, max(m.commits) + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 622
    if check and modified(changes) and not force:  # line 623
        m.listChanges(changes)  # line 624
        if not commit:  # line 625
            Exit("File tree contains changes. Use --force to proceed")  # line 625
    elif commit and not force:  #  and not check  # line 626
        Exit("Nothing to commit")  #  and not check  # line 626

    if argument is not None:  # branch/revision specified  # line 628
        m.loadBranch(branch)  # knows commits of target branch  # line 629
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 630
        if revision < 0 or revision > max(m.commits):  # line 631
            Exit("Unknown revision r%02d" % revision)  # line 631
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch))  # line 632
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns)  # line 633

def switch(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'None':  # line 635
    ''' Continue work on another branch, replacing file tree changes. '''  # line 636
    changes = None  # type: ChangeSet  # line 637
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options)  # line 638
    info(MARKER + " Switching to branch %sb%02d/r%02d" % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 639

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 642
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked)  # line 643
    else:  # full file switch  # line 644
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 645
        changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 646
        if not modified(changes):  # line 647
            info("No changes to current file tree")  # line 648
        else:  # integration required  # line 649
            for path, pinfo in changes.deletions.items():  # line 650
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 651
                print("ADD " + path)  # line 652
            for path, pinfo in changes.additions.items():  # line 653
                os.unlink(os.path.join(m.root, path.replace(SLASH, os.sep)))  # is added in current file tree: remove from branch to reach target  # line 654
                print("DEL " + path)  # line 655
            for path, pinfo in changes.modifications.items():  # line 656
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 657
                print("MOD " + path)  # line 658
    m.branch = branch  # line 659
    m.saveBranches()  # store switched path info  # line 660
    info("Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 661

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'None':  # line 663
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 667
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 668
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 669
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 670
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 671
    m = Metadata(os.getcwd())  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 672
    m.loadBranches()  # line 673
    changes = None  # type: ChangeSet  # line 673
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 674
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 675
    debug("Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 676

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 679
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 680
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingUnion), dontConsider=excps, progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 681
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 682
        if trackingUnion != trackingPatterns:  # nothing added  # line 683
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 684
        else:  # line 685
            info("Nothing to update")  # but write back updated branch info below  # line 686
    else:  # integration required  # line 687
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 688
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 689
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 689
            print("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 690
        for path, pinfo in changes.additions.items():  # line 691
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 692
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 692
            if mrg.value & MergeOperation.REMOVE.value:  # line 693
                os.unlink(m.root + os.sep + path.replace(SLASH, os.sep))  # line 693
            print("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 694
        for path, pinfo in changes.modifications.items():  # line 695
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 696
            binary = not m.isTextType(path)  # type: bool  # line 697
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 698
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 699
                print(("MOD " if not binary else "BIN ") + path)  # line 700
                while True:  # line 701
                    print(into)  # TODO print mtime, size differences?  # line 702
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 703
                    if op in ("it" if binary else "itm"):  # line 704
                        break  # line 704
            if op == "t":  # line 705
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 706
                print("THR " + path)  # line 707
            elif op == "m":  # line 708
                current = None  # type: bytes  # line 709
                with open(into, "rb") as fd:  # TODO slurps file  # line 710
                    current = fd.read()  # TODO slurps file  # line 710
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 711
                if current == file:  # line 712
                    debug("No difference to versioned file")  # line 712
                elif file is not None:  # if None, error message was already logged  # line 713
                    contents = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # type: bytes  # line 714
                    if contents != current:  # line 715
                        with open(path, "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 716
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 716
                    else:  # TODO but update timestamp?  # line 717
                        debug("No change")  # TODO but update timestamp?  # line 717
            else:  # mine or wrong input  # line 718
                print("MNE " + path)  # nothing to do! same as skip  # line 719
    info("Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 720
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 721
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 722
    m.saveBranches()  # line 723

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 725
    ''' Remove a branch entirely. '''  # line 726
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options)  # line 727
    if len(m.branches) == 1:  # line 728
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 728
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 729
    if branch is None or branch not in m.branches:  # line 730
        Exit("Cannot delete unknown branch %r" % branch)  # line 730
    debug("Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 731
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 732
    info("Branch b%02d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 733

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 735
    ''' Add a tracked files pattern to current branch's tracked files. '''  # line 736
    force = '--force' in options  # type: bool  # line 737
    m = Metadata(os.getcwd())  # type: Metadata  # line 738
    m.loadBranches()  # line 739
    if not m.track and not m.picky:  # line 740
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 740
    if pattern in m.branches[m.branch].tracked:  # line 741
        Exit("Pattern '%s' already tracked" % pattern)  # line 741
    if not force and not os.path.exists(relPath.replace(SLASH, os.sep)):  # line 742
        Exit("The pattern folder doesn't exist. Use --force to add it anyway")  # line 742
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 743
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 744
    m.branches[m.branch].tracked.append(pattern)  # line 745
    m.saveBranches()  # line 746
    info("Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 747

def remove(relPath: 'str', pattern: 'str') -> 'None':  # line 749
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 750
    m = Metadata(os.getcwd())  # type: Metadata  # line 751
    m.loadBranches()  # line 752
    if not m.track and not m.picky:  # line 753
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 753
    if pattern not in m.branches[m.branch].tracked:  # line 754
        suggestion = _coconut.set()  # type: Set[str]  # line 755
        for pat in m.branches[m.branch].tracked:  # line 756
            if fnmatch.fnmatch(pattern, pat):  # line 757
                suggestion.add(pat)  # line 757
        if suggestion:  # TODO use same wording as in move  # line 758
            print("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 758
        Exit("Tracked pattern '%s' not found" % pattern)  # line 759
    m.branches[m.branch].tracked.remove(pattern)  # line 760
    m.saveBranches()  # line 761
    info("Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 762

def ls(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 764
    ''' List specified directory, augmenting with repository metadata. '''  # line 765
    folder = "." if argument is None else argument  # type: str  # line 766
    m = Metadata(os.getcwd())  # type: Metadata  # line 767
    m.loadBranches()  # line 768
    info("Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 769
    relPath = os.path.relpath(folder, m.root).replace(os.sep, SLASH)  # type: str  # line 770
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 771
    if '--tags' in options:  # line 772
        print(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 773
        return  # line 774
    if '--patterns' in options:  # line 775
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 776
        if out:  # line 777
            print(out)  # line 777
        return  # line 778
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 779
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 780
        ignore = None  # type: _coconut.typing.Optional[str]  # line 781
        for ig in m.c.ignores:  # line 782
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 783
                ignore = ig  # remember first match  # line 783
                break  # remember first match  # line 783
        if ig:  # line 784
            for wl in m.c.ignoresWhitelist:  # line 785
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 786
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 786
                    break  # found a white list entry for ignored file, undo ignoring it  # line 786
        matches = []  # type: List[str]  # line 787
        if not ignore:  # line 788
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 789
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 790
                    matches.append(os.path.basename(pattern))  # line 790
        matches.sort(key=lambda element: len(element))  # line 791
        print("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "..."), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 792

def log(options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 794
    ''' List previous commits on current branch. '''  # line 795
    m = Metadata(os.getcwd())  # type: Metadata  # line 796
    m.loadBranches()  # knows current branch  # line 797
    m.loadBranch(m.branch)  # knows commit history  # line 798
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + " Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 799
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 800
    changeset = m.computeSequentialPathSetIterator(m.branch, max(m.commits))  # line 801
    maxWidth = max([wcswidth((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) for commit in m.commits.values()])  # type: int  # line 802
    for no in range(max(m.commits) + 1):  # line 803
        commit = m.commits[no]  # type: CommitInfo  # line 804
        changes = next(changeset)  # type: ChangeSet  # side-effect: updates m.paths  # line 805
        newTextFiles = len([file for file in changes.additions.keys() if m.isTextType(file)])  # type: int  # line 806
        print("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT/%05.1f%%) |%s|%s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(changes.additions), len(changes.deletions), len(changes.modifications), newTextFiles, 0. if len(changes.additions) == 0 else newTextFiles * 100. / len(changes.additions), ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)).ljust(maxWidth), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 807
        if '--changes' in options:  # line 808
            m.listChanges(changes)  # line 808
        if '--diff' in options:  # TODO needs to extract code from diff first to be reused here  # line 809
            pass  # TODO needs to extract code from diff first to be reused here  # line 809

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]) -> 'None':  # line 811
    ''' Exported entire repository as archive for easy transfer. '''  # line 812
    force = '--force' in options  # type: bool  # line 813
    progress = '--progress' in options  # type: bool  # line 814
    import zipfile  # TODO display compression ratio (if any)  # line 815
    try:  # line 816
        import zlib  # line 816
        compression = zipfile.ZIP_DEFLATED  # line 816
    except:  # line 817
        compression = zipfile.ZIP_STORED  # line 817

    if argument is None:  # line 819
        Exit("Argument missing (target filename)")  # line 819
    argument = argument if "." in argument else argument + ".sos.zip"  # line 820
    if os.path.exists(argument) and not force:  # line 821
        Exit("Target archive already exists. Use 'sos dump <arget> --force' to override")  # line 821
    with zipfile.ZipFile(argument, "w", compression) as fd:  # line 822
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 823
        counter = Counter(-1)  # type: Counter  # line 824
        timer = time.time()  # type: float  # line 824
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 825
            for filename in filenames:  # line 826
                newtime = time.time()  # type: float  # TODO alternatively count bytes and use a threshold there  # line 827
                if progress and newtime - timer > .1:  # line 828
                    sys.stdout.write("%s\r" % PROGRESS_MARKER[int(counter.inc() % 4)])  # line 828
                    sys.stdout.flush()  # line 828
                    timer = newtime  # line 828
                abspath = os.path.join(dirpath, filename)  # type: str  # line 829
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 830
                fd.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 831

def config(argument: 'str', options: 'List[str]'=[]) -> 'None':  # line 833
    if argument not in ["set", "unset", "show", "list", "add", "rm"]:  # line 834
        Exit("Unknown config command")  # line 834
    if not configr:  # line 835
        Exit("Cannot execute config command. 'configr' module not installed")  # line 835
    c = loadConfig()  # type: Union[configr.Configr, Accessor]  # line 836
    if argument == "set":  # line 837
        if len(options) < 2:  # line 838
            Exit("No key nor value specified")  # line 838
        if options[0] not in (["defaultbranch"] + CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS):  # line 839
            Exit("Unsupported key %r" % options[0])  # line 839
        if options[0] in CONFIGURABLE_FLAGS and options[1].lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 840
            Exit("Cannot set flag to '%s'. Try on/off instead" % options[1].lower())  # line 840
        c[options[0]] = options[1].lower() in TRUTH_VALUES if options[0] in CONFIGURABLE_FLAGS else (options[1].strip() if options[0] not in CONFIGURABLE_LISTS else safeSplit(options[1], ";"))  # TODO sanitize texts?  # line 841
    elif argument == "unset":  # line 842
        if len(options) < 1:  # line 843
            Exit("No key specified")  # line 843
        if options[0] not in c.keys():  # line 844
            Exit("Unknown key")  # line 844
        del c[options[0]]  # line 845
    elif argument == "add":  # line 846
        if len(options) < 2:  # line 847
            Exit("No key nor value specified")  # line 847
        if options[0] not in CONFIGURABLE_LISTS:  # line 848
            Exit("Unsupported key for add %r" % options[0])  # line 848
        if options[0] not in c.keys():  # add list  # line 849
            c[options[0]] = [options[1]]  # add list  # line 849
        elif options[1] in c[options[0]]:  # line 850
            Exit("Value already contained")  # line 850
        c[options[0]].append(options[1])  # line 851
    elif argument == "rm":  # line 852
        if len(options) < 2:  # line 853
            Exit("No key nor value specified")  # line 853
        if options[0] not in c.keys():  # line 854
            Exit("Unknown key specified: %r" % options[0])  # line 854
        if options[1] not in c[options[0]]:  # line 855
            Exit("Unknown value: %r" % options[1])  # line 855
        c[options[0]].remove(options[1])  # line 856
    else:  # Show or list  # line 857
        if "flags" in options:  # line 858
            print(", ".join(CONFIGURABLE_FLAGS))  # line 858
        elif "lists" in options:  # line 859
            print(", ".join(CONFIGURABLE_LISTS))  # line 859
        elif "texts" in options:  # line 860
            print(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 860
        elif len(options) > 0 and (options[0] in c.keys() or options[0] in c.__defaults):  # show a single value  # line 861
            print("%s %s %r" % (options[0].rjust(20), "[default]" if options[0] not in c.keys() else "[user]   ", c[options[0]]))  # line 862
        else:  # normal value listing  # line 863
            vals = c.__defaults  # type: Dict[str, Any]  # TODO uses internal knowledge of the configr project  # line 864
            vals.update(c.__map)  # line 865
            for k, v in sorted(vals.items()):  # line 866
                print("%s %s %r" % (k.rjust(20), "[default]" if k not in c.keys() else "[user]   ", v))  # line 866
            if len(c.keys()) == 0:  # TODO list defaults instead? Or display [DEFAULT] for each item above if unmodified  # line 867
                info("No configuration stored, using only defaults.")  # TODO list defaults instead? Or display [DEFAULT] for each item above if unmodified  # line 867
        return  # line 868
    f, g = saveConfig(c)  # line 869
    if f is None:  # line 870
        error("Error saving user configuration: %r" % g)  # line 870
    else:  # line 871
        Exit("OK", code=0)  # line 871

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[]) -> 'None':  # line 873
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique. '''  # line 874
    force = '--force' in options  # type: bool  # line 875
    soft = '--soft' in options  # type: bool  # line 876
    if not os.path.exists(relPath.replace(SLASH, os.sep)) and not force:  # line 877
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 877
    m = Metadata(os.getcwd())  # type: Metadata  # line 878
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(relPath.replace(SLASH, os.sep)) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 879
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 880
    if not matching and not force:  # line 881
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 881
    m.loadBranches()  # knows current branch  # line 882
    if not m.track and not m.picky:  # line 883
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 883
    if pattern not in m.branches[m.branch].tracked:  # line 884
        for tracked in (t for t in m.branches[m.branch].tracked if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 885
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 886
            if alternative:  # line 887
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 887
        if not (force or soft):  # line 888
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 888
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 889
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 890
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 891
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 895
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 896
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 896
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 897
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 898
    if len({st[1] for st in matches}) != len(matches):  # line 899
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 899
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 900
    if os.path.exists(newRelPath):  # line 901
        exists = [filename[1] for filename in matches if os.path.exists(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep))]  # type: _coconut.typing.Sequence[str]  # line 902
        if exists and not (force or soft):  # line 903
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 903
    else:  # line 904
        os.makedirs(os.path.abspath(newRelPath.replace(SLASH, os.sep)))  # line 904
    if not soft:  # perform actual renaming  # line 905
        for (source, target) in matches:  # line 906
            try:  # line 907
                shutil.move(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep)), os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep)))  # line 907
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 908
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 908
    m.branches[m.branch].tracked[m.branches[m.branch].tracked.index(pattern)] = newPattern  # line 909
    m.saveBranches()  # line 910

def parse(root: 'str', cwd: 'str'):  # line 912
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm. '''  # line 913
    debug("Parsing command-line arguments...")  # line 914
    try:  # line 915
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 916
        argument = sys.argv[2].strip() if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None  # line 917
        options = sys.argv[3:] if command == "config" else [c for c in sys.argv[2:] if c.startswith("--")]  # consider second parameter for no-arg command, otherwise from third on  # line 918
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 919
        debug("Processing command %r with argument '%s' and options %r." % (("" if command is None else command), ("" if argument is None else argument), options))  # line 920
        if command[:1] in "amr":  # line 921
            relPath, pattern = relativize(root, os.path.join(cwd, ("." if argument is None else argument)))  # line 921
        if command[:1] == "m":  # line 922
            if not options:  # line 923
                Exit("Need a second file pattern argument as target for move/rename command")  # line 923
            newRelPath, newPattern = relativize(root, os.path.join(cwd, options[0]))  # line 924
        if command[:1] == "a":  # line 925
            add(relPath, pattern, options)  # line 925
        elif command[:1] == "b":  # line 926
            branch(argument, options)  # line 926
        elif command[:2] == "ch":  # line 927
            changes(argument, options, onlys, excps)  # line 927
        elif command[:3] == "com":  # line 928
            commit(argument, options, onlys, excps)  # line 928
        elif command[:2] == "ci":  # line 929
            commit(argument, options, onlys, excps)  # line 929
        elif command[:3] == 'con':  # line 930
            config(argument, options)  # line 930
        elif command[:2] == "de":  # line 931
            delete(argument, options)  # line 931
        elif command[:2] == "di":  # line 932
            diff(argument, options, onlys, excps)  # line 932
        elif command[:2] == "du":  # line 933
            dump(argument, options)  # line 933
        elif command[:1] == "h":  # line 934
            usage()  # line 934
        elif command[:2] == "lo":  # line 935
            log(options)  # line 935
        elif command[:2] == "li":  # TODO handle absolute paths as well, also for Windows? think through  # line 936
            ls(relativize(root, cwd if argument is None else os.path.join(cwd, argument))[1], options)  # TODO handle absolute paths as well, also for Windows? think through  # line 936
        elif command[:2] == "ls":  # TODO avoid and/or normalize root super paths (..)  # line 937
            ls(relativize(root, cwd if argument is None else os.path.join(cwd, argument))[1], options)  # TODO avoid and/or normalize root super paths (..)  # line 937
        elif command[:1] == "m":  # line 938
            move(relPath, pattern, newRelPath, newPattern, options[1:])  # line 938
        elif command[:2] == "of":  # line 939
            offline(argument, options)  # line 939
        elif command[:2] == "on":  # line 940
            online(options)  # line 940
        elif command[:1] == "r":  # line 941
            remove(relPath, pattern)  # line 941
        elif command[:2] == "st":  # line 942
            status(options, onlys, excps)  # line 942
        elif command[:2] == "sw":  # line 943
            switch(argument, options, onlys, excps)  # line 943
        elif command[:1] == "u":  # line 944
            update(argument, options, onlys, excps)  # line 944
        elif command[:1] == "v":  # line 945
            usage(short=True)  # line 945
        else:  # line 946
            Exit("Unknown command '%s'" % command)  # line 946
        Exit(code=0)  # line 947
    except (Exception, RuntimeError) as E:  # line 948
        print(str(E))  # line 949
        import traceback  # line 950
        traceback.print_exc()  # line 951
        traceback.print_stack()  # line 952
        try:  # line 953
            traceback.print_last()  # line 953
        except:  # line 954
            pass  # line 954
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing.")  # line 955

def main() -> 'None':  # line 957
    global debug, info, warn, error  # line 958
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 959
    _log = Logger(logging.getLogger(__name__))  # line 960
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 960
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 961
        sys.argv.remove(option)  # clean up program arguments  # line 961
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 962
        usage()  # line 962
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 963
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 964
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 965
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 966
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in ["h", "v"]:  # in offline mode or just going offline TODO what about git config?  # line 967
        cwd = os.getcwd()  # line 968
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 969
        parse(root, cwd)  # line 970
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 971
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 972
        import subprocess  # only required in this section  # line 973
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 974
        inp = ""  # type: str  # line 975
        while True:  # line 976
            so, se = process.communicate(input=inp)  # line 977
            if process.returncode is not None:  # line 978
                break  # line 978
            inp = sys.stdin.read()  # line 979
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 980
            if root is None:  # line 981
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 981
            m = Metadata(root)  # line 982
            m.loadBranches()  # read repo  # line 983
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 984
            m.saveBranches()  # line 985
    else:  # line 986
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 986


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 990
level = logging.DEBUG if verbose else logging.INFO  # line 991
force_sos = '--sos' in sys.argv  # type: bool  # line 992
force_vcs = '--vcs' in sys.argv  # type: bool  # line 993
_log = Logger(logging.getLogger(__name__))  # line 994
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 994
if __name__ == '__main__':  # line 995
    main()  # line 995
