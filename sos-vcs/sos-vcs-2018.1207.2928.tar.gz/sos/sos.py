#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xad8c1da7

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
    from sos.usage import *  # line 13
except:  # line 14
    import version  # line 15
    from utility import *  # line 16
    from usage import *  # line 17

# External dependencies
import configr  # optional dependency  # line 20
#from enforce import runtime_validation  # https://github.com/RussBaz/enforce  TODO doesn't work for "data" types


# Constants
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": False, "texttype": [], "bintype": [], "ignoreDirs": [".*", "__pycache__"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout", "_FOSSIL_", "*.sos.zip"], "ignoresWhitelist": []})  # line 25
termWidth = getTermWidth() - 1  # uses curses or returns conservative default of 80  # line 26
APPNAME = "Subversion Offline Solution V%s (C) Arne Bachmann" % version.__release_version__  # type: str  # line 27


# Functions
def loadConfig() -> 'configr.Configr':  # Accessor when using defaults only  # line 31
    ''' Simplifies loading user-global config from file system or returning application defaults. '''  # line 32
    config = configr.Configr("sos", defaults=defaults)  # type: configr.Configr  # defaults are used if key is not configured, but won't be saved  # line 33
    f, g = config.loadSettings(clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # latter for testing only  # line 34
    if f is None:  # line 35
        debug("Encountered a problem while loading the user configuration: %r" % g)  # line 35
    return config  # line 36

@_coconut_tco  # line 38
def saveConfig(config: 'configr.Configr') -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[Exception]]':  # line 38
    return _coconut_tail_call(config.saveSettings, clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # saves global config, not local one  # line 39


# Main data class
#@runtime_validation
class Metadata:  # line 44
    ''' This class doesn't represent the entire repository state in memory,
      but serves as a container for different repo operations,
      using only parts of its attributes at any point in time. Use with care.
  '''  # line 48

    def __init__(_, path: '_coconut.typing.Optional[str]'=None):  # line 50
        ''' Create empty container object for various repository operations, and import configuration. '''  # line 51
        _.root = (os.getcwd() if path is None else path)  # type: str  # line 52
        _.tags = []  # type: List[str]  # list of known (unique) tags  # line 53
        _.branch = None  # type: _coconut.typing.Optional[int]  # current branch number  # line 54
        _.branches = {}  # type: Dict[int, BranchInfo]  # branch number zero represents the initial state at branching  # line 55
        _.repoConf = {}  # type: Dict[str, Any]  # line 56
        _.track = None  # type: bool  # TODO set defaults here?  # line 57
        _.picky = None  # type: bool  # TODO set defaults here?  # line 57
        _.strict = None  # type: bool  # TODO set defaults here?  # line 57
        _.compress = None  # type: bool  # TODO set defaults here?  # line 57
        _.loadBranches()  # loads above values from repository, or uses application defaults  # line 58

        _.commits = {}  # type: Dict[int, CommitInfo]  # consecutive numbers per branch, starting at 0  # line 60
        _.paths = {}  # type: Dict[str, PathInfo]  # utf-8 encoded relative, normalized file system paths  # line 61
        _.commit = None  # type: _coconut.typing.Optional[int]  # current revision number  # line 62

        _.c = configr.Configr(data=_.repoConf, defaults=loadConfig())  # type: configr.Configr  # load global configuration with defaults behind the local configuration  # line 64

    def isTextType(_, filename: 'str') -> 'bool':  # line 66
        return (((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(mimetypes.guess_type(filename)[0])).startswith("text/") or any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.texttype])) and not any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.bintype])  # line 66

    def listChanges(_, changes: 'ChangeSet'):  # line 68
        if len(changes.additions) > 0:  # line 69
            printo(ajoin("ADD ", sorted(changes.additions.keys()), "\n"))  # line 69
        if len(changes.deletions) > 0:  # line 70
            printo(ajoin("DEL ", sorted(changes.deletions.keys()), "\n"))  # line 70
        if len(changes.modifications) > 0:  # line 71
            printo(ajoin("MOD ", sorted(changes.modifications.keys()), "\n"))  # line 71

    def loadBranches(_):  # line 73
        ''' Load list of branches and current branch info from metadata file. '''  # line 74
        try:  # fails if not yet created (on initial branch/commit)  # line 75
            branches = None  # type: List[Tuple]  # line 76
            with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "r", encoding=UTF8) as fd:  # line 77
                repo, branches, config = json.load(fd)  # line 78
            _.tags = repo["tags"]  # list of commit messages to treat as globally unique tags  # line 79
            _.branch = repo["branch"]  # current branch integer  # line 80
            _.track, _.picky, _.strict, _.compress, _.version = [repo[r] for r in ["track", "picky", "strict", "compress", "version"]]  # line 81
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 82
            _.repoConf = config  # line 83
        except Exception as E:  # if not found, create metadata folder  # line 84
            _.branches = {}  # line 85
            _.track, _.picky, _.strict, _.compress, _.version = [defaults[k] for k in ["track", "picky", "strict", "compress"]] + [version.__version__]  # line 86
            warn("Couldn't read branches metadata: %r" % E)  # TODO when going offline, this message is not needed  # line 87

    def saveBranches(_, also: 'Dict[str, Any]'={}):  # line 89
        ''' Save list of branches and current branch info to metadata file. '''  # line 90
        with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "w", encoding=UTF8) as fd:  # line 91
            store = {"version": _.version, "tags": _.tags, "branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}  # type: Dict[str, Any]  # line 92
            store.update(also)  # allows overriding certain values at certain points in time  # line 93
            json.dump((store, list(_.branches.values()), _.repoConf), fd, ensure_ascii=False)  # stores using unicode codepoints, fd knows how to encode them  # line 94

    def getRevisionByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 96
        ''' Convenience accessor for named revisions (using commit message as name as a convention). '''  # line 97
        if name == "":  # line 98
            return -1  # line 98
        try:  # attempt to parse integer string  # line 99
            return int(name)  # attempt to parse integer string  # line 99
        except ValueError:  # line 100
            pass  # line 100
        found = [number for number, commit in _.commits.items() if name == commit.message]  # find any revision by commit message (usually used for tags)  # HINT allows finding any message, not only tagged ones  # line 101
        return found[0] if found else None  # line 102

    def getBranchByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 104
        ''' Convenience accessor for named branches. '''  # line 105
        if name == "":  # current  # line 106
            return _.branch  # current  # line 106
        try:  # attempt to parse integer string  # line 107
            return int(name)  # attempt to parse integer string  # line 107
        except ValueError:  # line 108
            pass  # line 108
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 109
        return found[0] if found else None  # line 110

    def loadBranch(_, branch: 'int'):  # line 112
        ''' Load all commit information from a branch meta data file. '''  # line 113
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "r", encoding=UTF8) as fd:  # line 114
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 115
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 116
        _.branch = branch  # line 117

    def saveBranch(_, branch: 'int'):  # line 119
        ''' Save all commit information to a branch meta data file. '''  # line 120
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "w", encoding=UTF8) as fd:  # line 121
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 122

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'):  # line 124
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 129
        debug("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 130
        tracked = [t for t in _.branches[_.branch].tracked]  # copy  # line 131
        os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 132
        _.loadBranch(_.branch)  # line 133
        revision = max(_.commits)  # type: int  # line 134
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 135
        for path, pinfo in _.paths.items():  # line 136
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 137
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 138
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 139
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 140
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].inSync, tracked)  # save branch info, before storing repo state at caller  # line 141

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 143
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 148
        simpleMode = not (_.track or _.picky)  # line 149
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # in case of initial branch creation  # line 150
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 151
        _.paths = {}  # type: Dict[str, PathInfo]  # line 152
        if simpleMode:  # branches from file system state  # line 153
            changes = _.findChanges(branch, 0, progress=simpleMode)  # type: ChangeSet  # creates revision folder and versioned files  # line 154
            _.listChanges(changes)  # line 155
            _.paths.update(changes.additions.items())  # line 156
        else:  # tracking or picky mode: branch from latest revision  # line 157
            os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 158
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 159
                _.loadBranch(_.branch)  # line 160
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 161
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 162
                for path, pinfo in _.paths.items():  # line 163
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 164
        ts = int(time.time() * 1000)  # line 165
        _.commits = {0: CommitInfo(0, ts, ("Branched on %s" % strftime(ts) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 166
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 167
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 168
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked)  # save branch info, in case it is needed  # line 169

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 171
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 172
        shutil.rmtree(encode(os.path.join(_.root, metaFolder, "b%d" % branch)))  # line 173
        binfo = _.branches[branch]  # line 174
        del _.branches[branch]  # line 175
        _.branch = max(_.branches)  # line 176
        _.saveBranches()  # line 177
        _.commits.clear()  # line 178
        return binfo  # line 179

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 181
        ''' Load all file information from a commit meta data. '''  # line 182
        with codecs.open(encode(branchFolder(branch, revision, base=_.root, file=metaFile)), "r", encoding=UTF8) as fd:  # line 183
            _.paths = json.load(fd)  # line 184
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 185
        _.branch = branch  # line 186

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 188
        ''' Save all file information to a commit meta data file. '''  # line 189
        target = branchFolder(branch, revision, base=_.root)  # type: str  # line 190
        try:  # line 191
            os.makedirs(encode(target))  # line 191
        except:  # line 192
            pass  # line 192
        with codecs.open(encode(os.path.join(target, metaFile)), "w", encoding=UTF8) as fd:  # line 193
            json.dump(_.paths, fd, ensure_ascii=False)  # line 194

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'ChangeSet':  # line 196
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        The function returns the state of file tree *differences*, unless "inverse" is True -> then return original data
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes
        progress: Show file names during processing
    '''  # line 205
        write = branch is not None and revision is not None  # line 206
        if write:  # line 207
            try:  # line 208
                os.makedirs(encode(branchFolder(branch, revision, base=_.root)))  # line 208
            except FileExistsError:  # HINT "try" only necessary for testing hash collisions  # line 209
                pass  # HINT "try" only necessary for testing hash collisions  # line 209
        changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 210
        counter = Counter(-1)  # type: Counter  # line 211
        timer = time.time()  # type: float  # line 211
        hashed = None  # type: _coconut.typing.Optional[str]  # line 212
        written = None  # type: int  # line 212
        compressed = 0  # type: int  # line 212
        original = 0  # type: int  # line 212
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 213
        for path, pinfo in _.paths.items():  # line 214
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 215
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 218
        for path, dirnames, filenames in os.walk(_.root):  # line 219
            path = decode(path)  # line 220
            dirnames[:] = [decode(d) for d in dirnames]  # line 221
            filenames[:] = [decode(f) for f in filenames]  # line 222
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 223
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 224
            dirnames.sort()  # line 225
            filenames.sort()  # line 225
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 226
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 227
            if dontConsider:  # line 228
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 229
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 230
                filename = relPath + SLASH + file  # line 231
                filepath = os.path.join(path, file)  # line 232
                stat = os.stat(encode(filepath))  # line 233
                size, mtime, newtime = stat.st_size, int(stat.st_mtime * 1000), time.time()  # line 234
                if progress and newtime - timer > .1:  # line 235
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", PROGRESS_MARKER[int(counter.inc() % 4)], filename)  # line 236
                    printo(outstring + " " * max(0, termWidth - len(outstring)), nl="")  # line 237
                    timer = newtime  # line 237
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 238
                    nameHash = hashStr(filename)  # line 239
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=nameHash) if write else None) if size > 0 else (None, 0)  # line 240
                    changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 241
                    compressed += written  # line 242
                    original += size  # line 242
                    continue  # with next file  # line 243
                last = _.paths[filename]  # filename is known - check for modifications  # line 244
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 245
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if size > 0 else (None, 0)  # line 246
                    changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 247
                    continue  # line 247
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and hashFile(filepath, _.compress)[0] != last.hash):  # detected a modification  # line 248
                    hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 249
                    changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 250
                else:  # with next file  # line 251
                    continue  # with next file  # line 251
                compressed += written  # line 252
                original += last.size if inverse else size  # line 252
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 253
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 253
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 254
            for file in names:  # line 255
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 256
                    continue  # don't mark ignored files as deleted  # line 256
                pth = path + SLASH + file  # type: str  # line 257
                changes.deletions[pth] = _.paths[pth]  # line 258
        if progress:  # forces new line  # line 259
            printo("\rChecking finished.%s" % ((" Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else "").ljust(termWidth))  # forces new line  # line 259
        else:  # line 260
            debug("Finished detecting changes.%s" % ((" Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else ""))  # line 260
        return changes  # line 261

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 263
        ''' Returns nothing, just updates _.paths in place. '''  # line 264
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 265

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 267
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 268
        _.loadCommit(branch, 0)  # load initial paths  # line 269
        if incrementally:  # line 270
            yield _.paths  # line 270
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 271
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 271
        for rev in range(1, revision + 1):  # line 272
            m.loadCommit(branch, rev)  # line 273
            for p, info in m.paths.items():  # line 274
                if info.size == None:  # line 275
                    del _.paths[p]  # line 275
                else:  # line 276
                    _.paths[p] = info  # line 276
            if incrementally:  # line 277
                yield _.paths  # line 277
        yield None  # for the default case - not incrementally  # line 278

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 280
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 283
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 284
            return (_.branch, -1)  # no branch/revision specified  # line 284
        argument = argument.strip()  # line 285
        if argument.startswith(SLASH):  # current branch  # line 286
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 286
        if argument.endswith(SLASH):  # line 287
            try:  # line 288
                return (_.getBranchByName(argument[:-1]), -1)  # line 288
            except ValueError:  # line 289
                Exit("Unknown branch label '%s'" % argument)  # line 289
        if SLASH in argument:  # line 290
            b, r = argument.split(SLASH)[:2]  # line 291
            try:  # line 292
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 292
            except ValueError:  # line 293
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 293
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 294
        if branch not in _.branches:  # line 295
            branch = None  # line 295
        try:  # either branch name/number or reverse/absolute revision number  # line 296
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 296
        except:  # line 297
            Exit("Unknown branch label or wrong number format")  # line 297
        Exit("This should never happen. Please create a issue report")  # line 298
        return (None, None)  # line 298

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 300
        while True:  # find latest revision that contained the file physically  # line 301
            source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 302
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 303
                break  # line 303
            revision -= 1  # line 304
            if revision < 0:  # line 305
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 305
        return revision, source  # line 306

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 308
        ''' Copy versioned file to other branch/revision. '''  # line 309
        target = branchFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 310
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 311
        shutil.copy2(encode(source), encode(target))  # line 312

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 314
        ''' Return file contents, or copy contents into file path provided. '''  # line 315
        source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 316
        try:  # line 317
            with openIt(source, "r", _.compress) as fd:  # line 318
                if toFile is None:  # read bytes into memory and return  # line 319
                    return fd.read()  # read bytes into memory and return  # line 319
                with open(encode(toFile), "wb") as to:  # line 320
                    while True:  # line 321
                        buffer = fd.read(bufSize)  # line 322
                        to.write(buffer)  # line 323
                        if len(buffer) < bufSize:  # line 324
                            break  # line 324
                    return None  # line 325
        except Exception as E:  # line 326
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 326
        return None  # line 327

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 329
        ''' Recreate file for given revision, or return binary contents if path is None. '''  # line 330
        if relPath is None:  # just return contents  # line 331
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 331
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 332
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 333
            try:  # line 334
                os.makedirs(encode(os.path.dirname(target)))  # line 334
            except:  # line 335
                pass  # line 335
        if pinfo.size == 0:  # line 336
            with open(encode(target), "wb"):  # line 337
                pass  # line 337
            try:  # update access/modification timestamps on file system  # line 338
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 338
            except Exception as E:  # line 339
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 339
            return None  # line 340
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 341
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 343
            while True:  # line 344
                buffer = fd.read(bufSize)  # line 345
                to.write(buffer)  # line 346
                if len(buffer) < bufSize:  # line 347
                    break  # line 347
        try:  # update access/modification timestamps on file system  # line 348
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 348
        except Exception as E:  # line 349
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 349
        return None  # line 350

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None) -> 'FrozenSet[str]':  # line 352
        ''' Returns list of tracking patterns for provided branch or current branch. '''  # line 353
        return _coconut.frozenset() if not _.track and not _.picky else frozenset(_.branches[_.branch if branch is None else branch].tracked)  # line 354


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 358
    ''' Initial command to start working offline. '''  # line 359
    if os.path.exists(encode(metaFolder)):  # line 360
        if '--force' not in options:  # line 361
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 361
        try:  # line 362
            for entry in os.listdir(metaFolder):  # line 363
                resource = metaFolder + os.sep + entry  # line 364
                if os.path.isdir(resource):  # line 365
                    shutil.rmtree(encode(resource))  # line 365
                else:  # line 366
                    os.unlink(encode(resource))  # line 366
        except:  # line 367
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 367
    m = Metadata()  # type: Metadata  # line 368
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 369
        m.compress = True  # plain file copies instead of compressed ones  # line 369
    if '--picky' in options or m.c.picky:  # Git-like  # line 370
        m.picky = True  # Git-like  # line 370
    elif '--track' in options or m.c.track:  # Svn-like  # line 371
        m.track = True  # Svn-like  # line 371
    if '--strict' in options or m.c.strict:  # always hash contents  # line 372
        m.strict = True  # always hash contents  # line 372
    debug("Preparing offline repository...")  # line 373
    m.createBranch(0, (defaults["defaultbranch"] if argument is None else argument), initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 374
    m.branch = 0  # line 375
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 376
    info("Offline repository prepared. Use 'sos online' to finish offline work")  # line 377

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 379
    ''' Finish working offline. '''  # line 380
    force = '--force' in options  # type: bool  # line 381
    m = Metadata()  # type: Metadata  # line 382
    m.loadBranches()  # line 383
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 384
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 384
    strict = '--strict' in options or m.strict  # type: bool  # line 385
    if options.count("--force") < 2:  # line 386
        changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track and not m.picky else m.getTrackingPatterns(), progress='--progress' in options)  # type: ChangeSet  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 387
        if modified(changes):  # line 388
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 388
    try:  # line 389
        shutil.rmtree(encode(metaFolder))  # line 389
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 389
    except Exception as E:  # line 390
        Exit("Error removing offline repository: %r" % E)  # line 390

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 392
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 393
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 394
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 395
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 396
    m = Metadata()  # type: Metadata  # line 397
    m.loadBranch(m.branch)  # line 398
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 399
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 399
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 400
    debug("Branching to %sbranch b%02d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 401
    if last:  # branch from branch's last revision  # line 402
        m.duplicateBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  # branch from branch's last revision  # line 402
    else:  #  branch from current file tree state  # line 403
        m.createBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  #  branch from current file tree state  # line 403
    if not stay:  # line 404
        m.branch = branch  # line 405
        m.saveBranches()  # line 406
    info("%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 407

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 409
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 410
    m = Metadata()  # type: Metadata  # line 411
    branch = None  # type: _coconut.typing.Optional[int]  # line 411
    revision = None  # type: _coconut.typing.Optional[int]  # line 411
    strict = '--strict' in options or m.strict  # type: bool  # line 412
    branch, revision = m.parseRevisionString(argument)  # line 413
    if branch not in m.branches:  # line 414
        Exit("Unknown branch")  # line 414
    m.loadBranch(branch)  # knows commits  # line 415
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 416
    if revision < 0 or revision > max(m.commits):  # line 417
        Exit("Unknown revision r%02d" % revision)  # line 417
    info(MARKER + " Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 418
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 419
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 420
    m.listChanges(changes)  # line 421
    return changes  # for unit tests only TODO remove  # line 422

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 424
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 425
    m = Metadata()  # type: Metadata  # line 426
    branch = None  # type: _coconut.typing.Optional[int]  # line 426
    revision = None  # type: _coconut.typing.Optional[int]  # line 426
    strict = '--strict' in options or m.strict  # type: bool  # line 427
    _from = {None: option.split("--from=")[1] for option in options if option.startswith("--from=")}.get(None, None)  # type: _coconut.typing.Optional[str]  # TODO implement  # line 428
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 429
    if branch not in m.branches:  # line 430
        Exit("Unknown branch")  # line 430
    m.loadBranch(branch)  # knows commits  # line 431
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 432
    if revision < 0 or revision > max(m.commits):  # line 433
        Exit("Unknown revision r%02d" % revision)  # line 433
    info(MARKER + " Differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 434
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 435
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 436
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 437
    if modified(onlyBinaryModifications):  # line 438
        debug(MARKER + " File changes")  # line 438
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 439

    if changes.modifications:  # line 441
        debug("%s%s Textual modifications" % ("\n" if modified(onlyBinaryModifications) else "", MARKER))  # line 441
    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 442
        content = None  # type: _coconut.typing.Optional[bytes]  # line 443
        if pinfo.size == 0:  # empty file contents  # line 444
            content = b""  # empty file contents  # line 444
        else:  # versioned file  # line 445
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 445
            assert content is not None  # versioned file  # line 445
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 446
        blocks = merge(filename=abspath, into=content, diffOnly=True)  # type: List[MergeBlock]  # only determine change blocks  # line 447
        printo("DIF %s%s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else ""))  # line 448
        for block in blocks:  # line 449
            if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:  # line 450
                pass  # TODO print some previous and following lines - which aren't accessible here anymore  # line 451
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 452
                for no, line in enumerate(block.lines):  # line 453
                    printo("+++ %04d |%s|" % (no + block.line, line))  # line 454
            elif block.tipe == MergeBlockType.REMOVE:  # line 455
                for no, line in enumerate(block.lines):  # line 456
                    printo("--- %04d |%s|" % (no + block.line, line))  # line 457
            elif block.tipe == MergeBlockType.REPLACE:  # TODO for MODIFY also show intra-line change ranges (TODO remove if that code was also removed)  # line 458
                for no, line in enumerate(block.replaces.lines):  # line 459
                    printo("- | %04d |%s|" % (no + block.replaces.line, line))  # line 460
                for no, line in enumerate(block.lines):  # line 461
                    printo("+ | %04d |%s|" % (no + block.line, line))  # line 462
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 466
    ''' Create new revision from file tree changes vs. last commit. '''  # line 467
    m = Metadata()  # type: Metadata  # line 468
    if argument is not None and argument in m.tags:  # line 469
        Exit("Illegal commit message. It was already used as a tag name")  # line 469
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 470
    if m.picky and not trackingPatterns:  # line 471
        Exit("No file patterns staged for commit in picky mode")  # line 471
    changes = None  # type: ChangeSet  # line 472
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but abort if no changes  # line 473
    info((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 474
    m.paths = changes.additions  # line 475
    m.paths.update(changes.modifications)  # update pathset to changeset only  # line 476
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changes.deletions.items()})  # line 477
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 478
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 479
    m.saveBranch(m.branch)  # line 480
    m.loadBranches()  # TODO is it necessary to load again?  # line 481
    if m.picky:  # remove tracked patterns  # line 482
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 482
    else:  # track or simple mode: set branch dirty  # line 483
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 483
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 484
        m.tags.append(argument)  # memorize unique tag  # line 484
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 484
    m.saveBranches()  # line 485
    info("Created new revision r%02d%s (+%02d/-%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))  # TODO show compression factor  # line 486

def status(options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 488
    ''' Show branches and current repository state. '''  # line 489
    m = Metadata()  # type: Metadata  # line 490
    current = m.branch  # type: int  # line 491
    strict = '--strict' in options or m.strict  # type: bool  # line 492
    info(MARKER + " Offline repository status")  # line 493
    info("SOS installation:    %s" % os.path.abspath(os.path.dirname(__file__)))  # line 494
    info("Current SOS version: %s" % version.__version__)  # line 495
    info("At creation version: %s" % m.version)  # line 496
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 497
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 498
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 499
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 500
    m.loadBranch(m.branch)  # line 501
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 508  # line 502
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps, progress=True)  # type: ChangeSet  # line 503
    printo("File tree %s" % ("has changes vs. last revision of current branch" if modified(changes) else "is unchanged"))  # line 504
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 505
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 506
        m.loadBranch(branch.number)  # knows commit history  # line 507
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 508
    if m.track or m.picky and len(m.branches[m.branch].tracked) > 0:  # line 509
        info("\nTracked file patterns:")  # line 510
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 511

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str]]':  # line 513
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags.
  '''  # line 519
    m = Metadata()  # type: Metadata  # line 520
    force = '--force' in options  # type: bool  # line 521
    strict = '--strict' in options or m.strict  # type: bool  # line 522
    if argument is not None:  # line 523
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 524
        if branch is None:  # line 525
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 525
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 526

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 529
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 530
    changes = m.findChanges(m.branch if commit else None, max(m.commits) + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 531
    if check and modified(changes) and not force:  # line 532
        m.listChanges(changes)  # line 533
        if not commit:  # line 534
            Exit("File tree contains changes. Use --force to proceed")  # line 534
    elif commit and not force:  #  and not check  # line 535
        Exit("Nothing to commit")  #  and not check  # line 535

    if argument is not None:  # branch/revision specified  # line 537
        m.loadBranch(branch)  # knows commits of target branch  # line 538
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 539
        if revision < 0 or revision > max(m.commits):  # line 540
            Exit("Unknown revision r%02d" % revision)  # line 540
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch))  # line 541
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns)  # line 542

def switch(argument: 'str', options: 'List[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 544
    ''' Continue work on another branch, replacing file tree changes. '''  # line 545
    m, branch, revision, changes, strict, _force, trackingPatterns = exitOnChanges(argument, ["--force"] + options)  # line 546
    force = '--force' in options  # type: bool  # needed as we fake force in above access  # line 547

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 550
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked)  # line 551
    else:  # full file switch  # line 552
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 553
        todos = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 554

# Now check for potential conflicts
        changes.deletions.clear()  # local deletions never create conflicts, modifications always  # line 557
        rms = []  # type: _coconut.typing.Sequence[str]  # local additions can be ignored if restoration from switch would be same  # line 558
        for a, pinfo in changes.additions.items():  # has potential corresponding re-add in switch operation:  # line 559
            if a in todos.deletions and pinfo.size == todos.deletions[a].size and (pinfo.hash == todos.deletions[a].hash if m.strict else pinfo.mtime == todos.deletions[a].mtime):  # line 560
                rms.append(a)  # line 560
        for rm in rms:  # TODO could also silently accept remote DEL for local ADD  # line 561
            del changes.additions[rm]  # TODO could also silently accept remote DEL for local ADD  # line 561
        if modified(changes) and not force:  # line 562
            m.listChanges(changes)  # line 562
            Exit("File tree contains changes. Use --force to proceed")  # line 562
        info(MARKER + " Switching to branch %sb%02d/r%02d" % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 563
        if not modified(todos):  # line 564
            info("No changes to current file tree")  # line 565
        else:  # integration required  # line 566
            for path, pinfo in todos.deletions.items():  # line 567
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 568
                printo("ADD " + path)  # line 569
            for path, pinfo in todos.additions.items():  # line 570
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 571
                printo("DEL " + path)  # line 572
            for path, pinfo in todos.modifications.items():  # line 573
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 574
                printo("MOD " + path)  # line 575
    m.branch = branch  # line 576
    m.saveBranches()  # store switched path info  # line 577
    info("Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 578

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 580
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 584
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 585
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 586
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 587
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 588
    m = Metadata()  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 589
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 590
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 591
    debug("Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 592

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 595
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 596
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingUnion), dontConsider=excps, progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 597
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 598
        if trackingUnion != trackingPatterns:  # nothing added  # line 599
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 600
        else:  # line 601
            info("Nothing to update")  # but write back updated branch info below  # line 602
    else:  # integration required  # line 603
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 604
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 605
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 605
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 606
        for path, pinfo in changes.additions.items():  # line 607
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 608
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 608
            if mrg.value & MergeOperation.REMOVE.value:  # line 609
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 609
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 610
        for path, pinfo in changes.modifications.items():  # line 611
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 612
            binary = not m.isTextType(path)  # type: bool  # line 613
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 614
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 615
                printo(("MOD " if not binary else "BIN ") + path)  # line 616
                while True:  # line 617
                    printo(into)  # TODO print mtime, size differences?  # line 618
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 619
                    if op in ("it" if binary else "itm"):  # line 620
                        break  # line 620
            if op == "t":  # line 621
                printo("THR " + path)  # blockwise copy of contents  # line 622
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 622
            elif op == "m":  # line 623
                current = None  # type: bytes  # line 624
                with open(encode(into), "rb") as fd:  # TODO slurps file  # line 625
                    current = fd.read()  # TODO slurps file  # line 625
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 626
                if current == file:  # line 627
                    debug("No difference to versioned file")  # line 627
                elif file is not None:  # if None, error message was already logged  # line 628
                    contents = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # type: bytes  # line 629
                    if contents != current:  # line 630
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 631
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 631
                    else:  # TODO but update timestamp?  # line 632
                        debug("No change")  # TODO but update timestamp?  # line 632
            else:  # mine or wrong input  # line 633
                printo("MNE " + path)  # nothing to do! same as skip  # line 634
    info("Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 635
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 636
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 637
    m.saveBranches()  # line 638

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 640
    ''' Remove a branch entirely. '''  # line 641
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options)  # line 642
    if len(m.branches) == 1:  # line 643
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 643
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 644
    if branch is None or branch not in m.branches:  # line 645
        Exit("Cannot delete unknown branch %r" % branch)  # line 645
    debug("Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 646
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 647
    info("Branch b%02d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 648

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 650
    ''' Add a tracked files pattern to current branch's tracked files. '''  # line 651
    force = '--force' in options  # type: bool  # line 652
    m = Metadata()  # type: Metadata  # line 653
    if not m.track and not m.picky:  # line 654
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 654
    if pattern in m.branches[m.branch].tracked:  # line 655
        Exit("Pattern '%s' already tracked" % pattern)  # line 655
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 656
        Exit("The pattern folder doesn't exist. Use --force to add it anyway")  # line 656
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 657
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 658
    m.branches[m.branch].tracked.append(pattern)  # line 659
    m.saveBranches()  # line 660
    info("Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 661

def remove(relPath: 'str', pattern: 'str'):  # line 663
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 664
    m = Metadata()  # type: Metadata  # line 665
    if not m.track and not m.picky:  # line 666
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 666
    if pattern not in m.branches[m.branch].tracked:  # line 667
        suggestion = _coconut.set()  # type: Set[str]  # line 668
        for pat in m.branches[m.branch].tracked:  # line 669
            if fnmatch.fnmatch(pattern, pat):  # line 670
                suggestion.add(pat)  # line 670
        if suggestion:  # TODO use same wording as in move  # line 671
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 671
        Exit("Tracked pattern '%s' not found" % pattern)  # line 672
    m.branches[m.branch].tracked.remove(pattern)  # line 673
    m.saveBranches()  # line 674
    info("Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 675

def ls(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 677
    ''' List specified directory, augmenting with repository metadata. '''  # line 678
    folder = "." if argument is None else argument  # type: str  # line 679
    m = Metadata()  # type: Metadata  # line 680
    info("Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 681
    relPath = os.path.relpath(folder, m.root).replace(os.sep, SLASH)  # type: str  # line 682
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 683
    if '--tags' in options:  # line 684
        printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 685
        return  # line 686
    if '--patterns' in options:  # line 687
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 688
        if out:  # line 689
            printo(out)  # line 689
        return  # line 690
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 691
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 692
        ignore = None  # type: _coconut.typing.Optional[str]  # line 693
        for ig in m.c.ignores:  # line 694
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 695
                ignore = ig  # remember first match  # line 695
                break  # remember first match  # line 695
        if ig:  # line 696
            for wl in m.c.ignoresWhitelist:  # line 697
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 698
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 698
                    break  # found a white list entry for ignored file, undo ignoring it  # line 698
        matches = []  # type: List[str]  # line 699
        if not ignore:  # line 700
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 701
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 702
                    matches.append(os.path.basename(pattern))  # line 702
        matches.sort(key=lambda element: len(element))  # line 703
        printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "..."), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 704

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 706
    ''' List previous commits on current branch. '''  # line 707
    m = Metadata()  # type: Metadata  # line 708
    m.loadBranch(m.branch)  # knows commit history  # line 709
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + " Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 710
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 711
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, max(m.commits))  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 712
    maxWidth = max([wcswidth((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) for commit in m.commits.values()])  # type: int  # line 713
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 714
    for no in range(max(m.commits) + 1):  # line 715
        commit = m.commits[no]  # type: CommitInfo  # line 716
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 717
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # side-effect: updates m.paths  # line 718
        _add = news - olds  # type: FrozenSet[str]  # line 719
        _del = olds - news  # type: FrozenSet[str]  # line 720
        _mod = frozenset([_ for _, info in nxts.items() if _ in m.paths and m.paths[_].size != info.size and (m.paths[_].hash != info.hash if m.strict else m.paths[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 721
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 722
        printo("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT) |%s|%s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)).ljust(maxWidth), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 723
        if '--changes' in options:  # line 724
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}))  # line 724
        if '--diff' in options:  # TODO needs to extract code from diff first to be reused here  # line 725
            pass  # TODO needs to extract code from diff first to be reused here  # line 725
        olds = news  # line 726

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 728
    ''' Exported entire repository as archive for easy transfer. '''  # line 729
    force = '--force' in options  # type: bool  # line 730
    progress = '--progress' in options  # type: bool  # line 731
    import zipfile  # TODO display compression ratio (if any)  # line 732
    try:  # line 733
        import zlib  # line 733
        compression = zipfile.ZIP_DEFLATED  # line 733
    except:  # line 734
        compression = zipfile.ZIP_STORED  # line 734

    if argument is None:  # line 736
        Exit("Argument missing (target filename)")  # line 736
    argument = argument if "." in argument else argument + ".sos.zip"  # line 737
    if os.path.exists(encode(argument)) and not force:  # line 738
        Exit("Target archive already exists. Use 'sos dump <arget> --force' to override")  # line 738
    with zipfile.ZipFile(argument, "w", compression) as fd:  # line 739
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 740
        counter = Counter(-1)  # type: Counter  # line 741
        timer = time.time()  # type: float  # line 741
        totalsize = 0  # type: int  # line 742
        start_time = time.time()  # type: float  # line 743
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 744
            dirpath = decode(dirpath)  # line 745
            dirnames[:] = [decode(d) for d in dirnames]  # line 746
            filenames[:] = [decode(f) for f in filenames]  # line 747
            for filename in filenames:  # line 748
                newtime = time.time()  # type: float  # TODO alternatively count bytes and use a threshold there  # line 749
                abspath = os.path.join(dirpath, filename)  # type: str  # line 750
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 751
                totalsize += os.stat(encode(abspath)).st_size  # line 752
                if progress and newtime - timer > .1:  # line 753
                    printo(("\rDumping %s@%6.2f MiB/s %s" % (PROGRESS_MARKER[int(counter.inc() % 4)], totalsize / (MEBI * (time.time() - start_time)), filename)).ljust(termwidth), nl="")  # line 753
                    timer = newtime  # line 753
                fd.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 754
    printo("\rDone dumping entire repository.".ljust(termwidth), nl="")  # clean line  # line 755

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 757
    command, key, value = (arguments + [None] * 2)[:3]  # line 758
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 759
        Exit("Unknown config command")  # line 759
    local = "--local" in options  # type: bool  # line 760
    m = Metadata()  # type: Metadata  # loads layered configuration as well. TODO warning if repo not exists  # line 761
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 762
    if command == "set":  # line 763
        if None in (key, value):  # line 764
            Exit("Key or value not specified")  # line 764
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 765
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 765
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 766
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 766
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 767
    elif command == "unset":  # line 768
        if key is None:  # line 769
            Exit("No key specified")  # line 769
        if key not in c.keys():  # line 770
            Exit("Unknown key")  # line 770
        del c[key]  # line 771
    elif command == "add":  # line 772
        if None in (key, value):  # line 773
            Exit("Key or value not specified")  # line 773
        if key not in CONFIGURABLE_LISTS:  # line 774
            Exit("Unsupported key %r" % key)  # line 774
        if key not in c.keys():  # add list  # line 775
            c[key] = [value]  # add list  # line 775
        elif value in c[key]:  # line 776
            Exit("Value already contained, nothing to do")  # line 776
        if ";" in value:  # line 777
            c[key].append(removePath(key, value))  # line 777
        else:  # line 778
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 778
    elif command == "rm":  # line 779
        if None in (key, value):  # line 780
            Exit("Key or value not specified")  # line 780
        if key not in c.keys():  # line 781
            Exit("Unknown key %r" % key)  # line 781
        if value not in c[key]:  # line 782
            Exit("Unknown value %r" % value)  # line 782
        c[key].remove(value)  # line 783
    else:  # Show or list  # line 784
        if key == "flags":  # list valid configuration items  # line 785
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 785
        elif key == "lists":  # line 786
            printo(", ".join(CONFIGURABLE_LISTS))  # line 786
        elif key == "texts":  # line 787
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 787
        else:  # line 788
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 789
            c = m.c  # always use full configuration chain  # line 790
            try:  # attempt single key  # line 791
                assert key is not None  # line 792
                c[key]  # line 792
                l = key in c.keys()  # type: bool  # line 793
                g = key in c.__defaults.keys()  # type: bool  # line 793
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 794
            except:  # normal value listing  # line 795
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 796
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 797
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 798
                for k, vt in sorted(vals.items()):  # line 799
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 799
                if len(c.keys()) == 0:  # line 800
                    info("No local configuration stored")  # line 800
                if len(c.__defaults.keys()) == 0:  # line 801
                    info("No global configuration stored")  # line 801
        return  # in case of list, no need to store anything  # line 802
    if local:  # saves changes of repoConfig  # line 803
        m.repoConf = c.__map  # saves changes of repoConfig  # line 803
        m.saveBranches()  # saves changes of repoConfig  # line 803
        Exit("OK", code=0)  # saves changes of repoConfig  # line 803
    else:  # global config  # line 804
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 805
        if f is None:  # line 806
            error("Error saving user configuration: %r" % h)  # line 806
        else:  # line 807
            Exit("OK", code=0)  # line 807

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[]):  # line 809
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique. '''  # line 810
    force = '--force' in options  # type: bool  # line 811
    soft = '--soft' in options  # type: bool  # line 812
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 813
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 813
    m = Metadata()  # type: Metadata  # line 814
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 815
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 816
    if not matching and not force:  # line 817
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 817
    if not m.track and not m.picky:  # line 818
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 818
    if pattern not in m.branches[m.branch].tracked:  # line 819
        for tracked in (t for t in m.branches[m.branch].tracked if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 820
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 821
            if alternative:  # line 822
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 822
        if not (force or soft):  # line 823
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 823
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 824
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 825
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 826
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 830
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 831
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 831
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 832
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 833
    if len({st[1] for st in matches}) != len(matches):  # line 834
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 834
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 835
    if os.path.exists(encode(newRelPath)):  # line 836
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 837
        if exists and not (force or soft):  # line 838
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 838
    else:  # line 839
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 839
    if not soft:  # perform actual renaming  # line 840
        for (source, target) in matches:  # line 841
            try:  # line 842
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 842
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 843
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 843
    m.branches[m.branch].tracked[m.branches[m.branch].tracked.index(pattern)] = newPattern  # line 844
    m.saveBranches()  # line 845

def parse(root: 'str', cwd: 'str'):  # line 847
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm. '''  # line 848
    debug("Parsing command-line arguments...")  # line 849
    try:  # line 850
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 851
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: Union[List[str], str, None]  # line 852
        if len(arguments) == 0:  # line 853
            arguments = [None]  # line 853
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 854
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 855
        debug("Processing command %r with arguments %r and options %r." % (("" if command is None else command), arguments if arguments else "", options))  # line 856
        if command[:1] in "amr":  # line 857
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 857
        if command[:1] == "m":  # line 858
            if len(arguments) < 2:  # line 859
                Exit("Need a second file pattern argument as target for move/rename command")  # line 859
            newRelPath, newPattern = relativize(root, os.path.join(cwd, options[0]))  # line 860
        if command[:1] == "a":  # line 861
            add(relPath, pattern, options)  # line 861
        elif command[:1] == "b":  # line 862
            branch(arguments[0], options)  # line 862
        elif command[:2] == "ch":  # line 863
            changes(arguments[0], options, onlys, excps)  # line 863
        elif command[:3] == "com":  # line 864
            commit(arguments[0], options, onlys, excps)  # line 864
        elif command[:2] == "ci":  # line 865
            commit(arguments[0], options, onlys, excps)  # line 865
        elif command[:3] == 'con':  # line 866
            config(arguments, options)  # line 866
        elif command[:2] == "de":  # line 867
            delete(arguments[0], options)  # line 867
        elif command[:2] == "di":  # line 868
            diff(arguments[0], options, onlys, excps)  # line 868
        elif command[:2] == "du":  # line 869
            dump(arguments[0], options)  # line 869
        elif command[:1] == "h":  # line 870
            usage(APPNAME, version.__version__)  # line 870
        elif command[:2] == "lo":  # line 871
            log(options)  # line 871
        elif command[:2] == "li":  # TODO handle absolute paths as well, also for Windows? think through  # line 872
            ls(relativize(root, cwd if not arguments else os.path.join(cwd, arguments[0]))[1], options)  # TODO handle absolute paths as well, also for Windows? think through  # line 872
        elif command[:2] == "ls":  # TODO avoid and/or normalize root super paths (..)  # line 873
            ls(relativize(root, cwd if not arguments else os.path.join(cwd, arguments[0]))[1], options)  # TODO avoid and/or normalize root super paths (..)  # line 873
        elif command[:1] == "m":  # line 874
            move(relPath, pattern, newRelPath, newPattern, options[1:])  # line 874
        elif command[:2] == "of":  # line 875
            offline(arguments[0], options)  # line 875
        elif command[:2] == "on":  # line 876
            online(options)  # line 876
        elif command[:1] == "r":  # line 877
            remove(relPath, pattern)  # line 877
        elif command[:2] == "st":  # line 878
            status(options, onlys, excps)  # line 878
        elif command[:2] == "sw":  # line 879
            switch(arguments[0], options, onlys, excps)  # line 879
        elif command[:1] == "u":  # line 880
            update(arguments[0], options, onlys, excps)  # line 880
        elif command[:1] == "v":  # line 881
            usage(APPNAME, version.__version__, short=True)  # line 881
        else:  # line 882
            Exit("Unknown command '%s'" % command)  # line 882
        Exit(code=0)  # line 883
    except (Exception, RuntimeError) as E:  # line 884
        printo(str(E))  # line 885
        import traceback  # line 886
        traceback.print_exc()  # line 887
        traceback.print_stack()  # line 888
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing.")  # line 889

def main():  # line 891
    global debug, info, warn, error  # line 892
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 893
    _log = Logger(logging.getLogger(__name__))  # line 894
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 894
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 895
        sys.argv.remove(option)  # clean up program arguments  # line 895
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 896
        usage()  # line 896
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 897
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 898
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 899
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 900
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in ["h", "v"]:  # in offline mode or just going offline TODO what about git config?  # line 901
        cwd = os.getcwd()  # line 902
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 903
        parse(root, cwd)  # line 904
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 905
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 906
        import subprocess  # only required in this section  # line 907
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 908
        inp = ""  # type: str  # line 909
        while True:  # line 910
            so, se = process.communicate(input=inp)  # line 911
            if process.returncode is not None:  # line 912
                break  # line 912
            inp = sys.stdin.read()  # line 913
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 914
            if root is None:  # line 915
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 915
            m = Metadata(root)  # type: Metadata  # line 916
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 917
            m.saveBranches()  # line 918
    else:  # line 919
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 919


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 923
level = logging.DEBUG if verbose else logging.INFO  # line 924
force_sos = '--sos' in sys.argv  # type: bool  # line 925
force_vcs = '--vcs' in sys.argv  # type: bool  # line 926
_log = Logger(logging.getLogger(__name__))  # line 927
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 927
if __name__ == '__main__':  # line 928
    main()  # line 928
