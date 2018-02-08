#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x72ae1184

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

    def __init__(_, path: '_coconut.typing.Optional[str]'=None, offline: 'bool'=False):  # line 50
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
        _.loadBranches(offline=offline)  # loads above values from repository, or uses application defaults  # line 58

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

    def loadBranches(_, offline: 'bool'=False):  # line 73
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
            (debug if offline else warn)("Couldn't read branches metadata: %r" % E)  # line 87

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
                try:  # line 233
                    stat = os.stat(encode(filepath))  # line 233
                except Exception as E:  # line 234
                    exception(E)  # line 234
                    continue  # line 234
                size, mtime, newtime = stat.st_size, int(stat.st_mtime * 1000), time.time()  # line 235
                if progress and newtime - timer > .1:  # line 236
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", PROGRESS_MARKER[int(counter.inc() % 4)], filename)  # line 237
                    printo(outstring + " " * max(0, termWidth - len(outstring)), nl="")  # line 238
                    timer = newtime  # line 238
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 239
                    nameHash = hashStr(filename)  # line 240
                    try:  # line 241
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=nameHash) if write else None) if size > 0 else (None, 0)  # line 242
                        changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 243
                        compressed += written  # line 244
                        original += size  # line 244
                    except Exception as E:  # line 245
                        exception(E)  # line 245
                    continue  # with next file  # line 246
                last = _.paths[filename]  # filename is known - check for modifications  # line 247
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 248
                    try:  # line 249
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if size > 0 else (None, 0)  # line 250
                        changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 251
                        continue  # line 251
                    except Exception as E:  # line 252
                        exception(E)  # line 252
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and tryOrDefault(lambda: (hashFile(filepath, _.compress)[0] != last.hash), default=False)):  # detected a modification TODO wrap hashFile exception  # line 253
                    try:  # line 254
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 255
                        changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 256
                    except Exception as E:  # line 257
                        exception(E)  # line 257
                else:  # with next file  # line 258
                    continue  # with next file  # line 258
                compressed += written  # line 259
                original += last.size if inverse else size  # line 259
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 260
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 260
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 261
            for file in names:  # line 262
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 263
                    continue  # don't mark ignored files as deleted  # line 263
                pth = path + SLASH + file  # type: str  # line 264
                changes.deletions[pth] = _.paths[pth]  # line 265
        if progress:  # forces new line  # line 266
            printo("\rChecking finished.%s" % ((" Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else "").ljust(termWidth))  # forces new line  # line 266
        else:  # line 267
            debug("Finished detecting changes.%s" % ((" Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else ""))  # line 267
        return changes  # line 268

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 270
        ''' Returns nothing, just updates _.paths in place. '''  # line 271
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 272

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 274
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 275
        _.loadCommit(branch, 0)  # load initial paths  # line 276
        if incrementally:  # line 277
            yield _.paths  # line 277
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 278
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 278
        for rev in range(1, revision + 1):  # line 279
            m.loadCommit(branch, rev)  # line 280
            for p, info in m.paths.items():  # line 281
                if info.size == None:  # line 282
                    del _.paths[p]  # line 282
                else:  # line 283
                    _.paths[p] = info  # line 283
            if incrementally:  # line 284
                yield _.paths  # line 284
        yield None  # for the default case - not incrementally  # line 285

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 287
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 290
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 291
            return (_.branch, -1)  # no branch/revision specified  # line 291
        argument = argument.strip()  # line 292
        if argument.startswith(SLASH):  # current branch  # line 293
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 293
        if argument.endswith(SLASH):  # line 294
            try:  # line 295
                return (_.getBranchByName(argument[:-1]), -1)  # line 295
            except ValueError:  # line 296
                Exit("Unknown branch label '%s'" % argument)  # line 296
        if SLASH in argument:  # line 297
            b, r = argument.split(SLASH)[:2]  # line 298
            try:  # line 299
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 299
            except ValueError:  # line 300
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 300
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 301
        if branch not in _.branches:  # line 302
            branch = None  # line 302
        try:  # either branch name/number or reverse/absolute revision number  # line 303
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 303
        except:  # line 304
            Exit("Unknown branch label or wrong number format")  # line 304
        Exit("This should never happen. Please create a issue report")  # line 305
        return (None, None)  # line 305

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 307
        while True:  # find latest revision that contained the file physically  # line 308
            source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 309
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 310
                break  # line 310
            revision -= 1  # line 311
            if revision < 0:  # line 312
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 312
        return revision, source  # line 313

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 315
        ''' Copy versioned file to other branch/revision. '''  # line 316
        target = branchFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 317
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 318
        shutil.copy2(encode(source), encode(target))  # line 319

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 321
        ''' Return file contents, or copy contents into file path provided. '''  # line 322
        source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 323
        try:  # line 324
            with openIt(source, "r", _.compress) as fd:  # line 325
                if toFile is None:  # read bytes into memory and return  # line 326
                    return fd.read()  # read bytes into memory and return  # line 326
                with open(encode(toFile), "wb") as to:  # line 327
                    while True:  # line 328
                        buffer = fd.read(bufSize)  # line 329
                        to.write(buffer)  # line 330
                        if len(buffer) < bufSize:  # line 331
                            break  # line 331
                    return None  # line 332
        except Exception as E:  # line 333
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 333
        return None  # line 334

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 336
        ''' Recreate file for given revision, or return binary contents if path is None. '''  # line 337
        if relPath is None:  # just return contents  # line 338
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 338
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 339
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 340
            try:  # line 341
                os.makedirs(encode(os.path.dirname(target)))  # line 341
            except:  # line 342
                pass  # line 342
        if pinfo.size == 0:  # line 343
            with open(encode(target), "wb"):  # line 344
                pass  # line 344
            try:  # update access/modification timestamps on file system  # line 345
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 345
            except Exception as E:  # line 346
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 346
            return None  # line 347
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 348
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 350
            while True:  # line 351
                buffer = fd.read(bufSize)  # line 352
                to.write(buffer)  # line 353
                if len(buffer) < bufSize:  # line 354
                    break  # line 354
        try:  # update access/modification timestamps on file system  # line 355
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 355
        except Exception as E:  # line 356
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 356
        return None  # line 357

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None) -> 'FrozenSet[str]':  # line 359
        ''' Returns list of tracking patterns for provided branch or current branch. '''  # line 360
        return _coconut.frozenset() if not _.track and not _.picky else frozenset(_.branches[_.branch if branch is None else branch].tracked)  # line 361


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 365
    ''' Initial command to start working offline. '''  # line 366
    if os.path.exists(encode(metaFolder)):  # line 367
        if '--force' not in options:  # line 368
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 368
        try:  # line 369
            for entry in os.listdir(metaFolder):  # line 370
                resource = metaFolder + os.sep + entry  # line 371
                if os.path.isdir(resource):  # line 372
                    shutil.rmtree(encode(resource))  # line 372
                else:  # line 373
                    os.unlink(encode(resource))  # line 373
        except:  # line 374
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 374
    m = Metadata(offline=True)  # type: Metadata  # line 375
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 376
        m.compress = True  # plain file copies instead of compressed ones  # line 376
    if '--picky' in options or m.c.picky:  # Git-like  # line 377
        m.picky = True  # Git-like  # line 377
    elif '--track' in options or m.c.track:  # Svn-like  # line 378
        m.track = True  # Svn-like  # line 378
    if '--strict' in options or m.c.strict:  # always hash contents  # line 379
        m.strict = True  # always hash contents  # line 379
    debug("Preparing offline repository...")  # line 380
    m.createBranch(0, (defaults["defaultbranch"] if argument is None else argument), initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 381
    m.branch = 0  # line 382
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 383
    info("Offline repository prepared. Use 'sos online' to finish offline work")  # line 384

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 386
    ''' Finish working offline. '''  # line 387
    force = '--force' in options  # type: bool  # line 388
    m = Metadata()  # type: Metadata  # line 389
    m.loadBranches()  # line 390
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 391
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 391
    strict = '--strict' in options or m.strict  # type: bool  # line 392
    if options.count("--force") < 2:  # line 393
        changes = m.findChanges(checkContent=strict, considerOnly=None if not m.track and not m.picky else m.getTrackingPatterns(), progress='--progress' in options)  # type: ChangeSet  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 394
        if modified(changes):  # line 395
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 395
    try:  # line 396
        shutil.rmtree(encode(metaFolder))  # line 396
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 396
    except Exception as E:  # line 397
        Exit("Error removing offline repository: %r" % E)  # line 397

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 399
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 400
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 401
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 402
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 403
    m = Metadata()  # type: Metadata  # line 404
    m.loadBranch(m.branch)  # line 405
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 406
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 406
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 407
    debug("Branching to %sbranch b%02d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 408
    if last:  # branch from branch's last revision  # line 409
        m.duplicateBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  # branch from branch's last revision  # line 409
    else:  #  branch from current file tree state  # line 410
        m.createBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  #  branch from current file tree state  # line 410
    if not stay:  # line 411
        m.branch = branch  # line 412
        m.saveBranches()  # line 413
    info("%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 414

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 416
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 417
    m = Metadata()  # type: Metadata  # line 418
    branch = None  # type: _coconut.typing.Optional[int]  # line 418
    revision = None  # type: _coconut.typing.Optional[int]  # line 418
    strict = '--strict' in options or m.strict  # type: bool  # line 419
    branch, revision = m.parseRevisionString(argument)  # line 420
    if branch not in m.branches:  # line 421
        Exit("Unknown branch")  # line 421
    m.loadBranch(branch)  # knows commits  # line 422
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 423
    if revision < 0 or revision > max(m.commits):  # line 424
        Exit("Unknown revision r%02d" % revision)  # line 424
    info(MARKER + " Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 425
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 426
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 427
    m.listChanges(changes)  # line 428
    return changes  # for unit tests only TODO remove  # line 429

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 431
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 432
    m = Metadata()  # type: Metadata  # line 433
    branch = None  # type: _coconut.typing.Optional[int]  # line 433
    revision = None  # type: _coconut.typing.Optional[int]  # line 433
    strict = '--strict' in options or m.strict  # type: bool  # line 434
    _from = {None: option.split("--from=")[1] for option in options if option.startswith("--from=")}.get(None, None)  # type: _coconut.typing.Optional[str]  # TODO implement  # line 435
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 436
    if branch not in m.branches:  # line 437
        Exit("Unknown branch")  # line 437
    m.loadBranch(branch)  # knows commits  # line 438
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 439
    if revision < 0 or revision > max(m.commits):  # line 440
        Exit("Unknown revision r%02d" % revision)  # line 440
    info(MARKER + " Differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 441
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 442
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 443
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 444
    if modified(onlyBinaryModifications):  # line 445
        debug(MARKER + " File changes")  # line 445
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 446

    if changes.modifications:  # line 448
        debug("%s%s Textual modifications" % ("\n" if modified(onlyBinaryModifications) else "", MARKER))  # line 448
    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 449
        content = None  # type: _coconut.typing.Optional[bytes]  # line 450
        if pinfo.size == 0:  # empty file contents  # line 451
            content = b""  # empty file contents  # line 451
        else:  # versioned file  # line 452
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 452
            assert content is not None  # versioned file  # line 452
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 453
        blocks = merge(filename=abspath, into=content, diffOnly=True)  # type: List[MergeBlock]  # only determine change blocks  # line 454
        printo("DIF %s%s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else ""))  # line 455
        for block in blocks:  # line 456
            if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:  # line 457
                pass  # TODO print some previous and following lines - which aren't accessible here anymore  # line 458
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 459
                for no, line in enumerate(block.lines):  # line 460
                    printo("+++ %04d |%s|" % (no + block.line, line))  # line 461
            elif block.tipe == MergeBlockType.REMOVE:  # line 462
                for no, line in enumerate(block.lines):  # line 463
                    printo("--- %04d |%s|" % (no + block.line, line))  # line 464
            elif block.tipe == MergeBlockType.REPLACE:  # TODO for MODIFY also show intra-line change ranges (TODO remove if that code was also removed)  # line 465
                for no, line in enumerate(block.replaces.lines):  # line 466
                    printo("- | %04d |%s|" % (no + block.replaces.line, line))  # line 467
                for no, line in enumerate(block.lines):  # line 468
                    printo("+ | %04d |%s|" % (no + block.line, line))  # line 469
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 473
    ''' Create new revision from file tree changes vs. last commit. '''  # line 474
    m = Metadata()  # type: Metadata  # line 475
    if argument is not None and argument in m.tags:  # line 476
        Exit("Illegal commit message. It was already used as a tag name")  # line 476
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 477
    if m.picky and not trackingPatterns:  # line 478
        Exit("No file patterns staged for commit in picky mode")  # line 478
    changes = None  # type: ChangeSet  # line 479
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but abort if no changes  # line 480
    info((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 481
    m.paths = changes.additions  # line 482
    m.paths.update(changes.modifications)  # update pathset to changeset only  # line 483
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changes.deletions.items()})  # line 484
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 485
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 486
    m.saveBranch(m.branch)  # line 487
    m.loadBranches()  # TODO is it necessary to load again?  # line 488
    if m.picky:  # remove tracked patterns  # line 489
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 489
    else:  # track or simple mode: set branch dirty  # line 490
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 490
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 491
        m.tags.append(argument)  # memorize unique tag  # line 491
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 491
    m.saveBranches()  # line 492
    info("Created new revision r%02d%s (+%02d/-%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))  # TODO show compression factor  # line 493

def status(options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 495
    ''' Show branches and current repository state. '''  # line 496
    m = Metadata()  # type: Metadata  # line 497
    current = m.branch  # type: int  # line 498
    strict = '--strict' in options or m.strict  # type: bool  # line 499
    info(MARKER + " Offline repository status")  # line 500
    info("SOS installation:    %s" % os.path.abspath(os.path.dirname(__file__)))  # line 501
    info("Current SOS version: %s" % version.__version__)  # line 502
    info("At creation version: %s" % m.version)  # line 503
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 504
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 505
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 506
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 507
    m.loadBranch(m.branch)  # line 508
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 508  # line 509
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps, progress=True)  # type: ChangeSet  # line 510
    printo("File tree %s" % ("has changes vs. last revision of current branch" if modified(changes) else "is unchanged"))  # line 511
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 512
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 513
        m.loadBranch(branch.number)  # knows commit history  # line 514
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 515
    if m.track or m.picky and len(m.branches[m.branch].tracked) > 0:  # line 516
        info("\nTracked file patterns:")  # line 517
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 518

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str]]':  # line 520
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags.
  '''  # line 526
    m = Metadata()  # type: Metadata  # line 527
    force = '--force' in options  # type: bool  # line 528
    strict = '--strict' in options or m.strict  # type: bool  # line 529
    if argument is not None:  # line 530
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 531
        if branch is None:  # line 532
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 532
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 533

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 536
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 537
    changes = m.findChanges(m.branch if commit else None, max(m.commits) + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # line 538
    if check and modified(changes) and not force:  # line 539
        m.listChanges(changes)  # line 540
        if not commit:  # line 541
            Exit("File tree contains changes. Use --force to proceed")  # line 541
    elif commit and not force:  #  and not check  # line 542
        Exit("Nothing to commit")  #  and not check  # line 542

    if argument is not None:  # branch/revision specified  # line 544
        m.loadBranch(branch)  # knows commits of target branch  # line 545
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 546
        if revision < 0 or revision > max(m.commits):  # line 547
            Exit("Unknown revision r%02d" % revision)  # line 547
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch))  # line 548
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns)  # line 549

def switch(argument: 'str', options: 'List[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 551
    ''' Continue work on another branch, replacing file tree changes. '''  # line 552
    m, branch, revision, changes, strict, _force, trackingPatterns = exitOnChanges(argument, ["--force"] + options)  # line 553
    force = '--force' in options  # type: bool  # needed as we fake force in above access  # line 554

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 557
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked)  # line 558
    else:  # full file switch  # line 559
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 560
        todos = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps, progress='--progress' in options)  # type: ChangeSet  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 561

# Now check for potential conflicts
        changes.deletions.clear()  # local deletions never create conflicts, modifications always  # line 564
        rms = []  # type: _coconut.typing.Sequence[str]  # local additions can be ignored if restoration from switch would be same  # line 565
        for a, pinfo in changes.additions.items():  # has potential corresponding re-add in switch operation:  # line 566
            if a in todos.deletions and pinfo.size == todos.deletions[a].size and (pinfo.hash == todos.deletions[a].hash if m.strict else pinfo.mtime == todos.deletions[a].mtime):  # line 567
                rms.append(a)  # line 567
        for rm in rms:  # TODO could also silently accept remote DEL for local ADD  # line 568
            del changes.additions[rm]  # TODO could also silently accept remote DEL for local ADD  # line 568
        if modified(changes) and not force:  # line 569
            m.listChanges(changes)  # line 569
            Exit("File tree contains changes. Use --force to proceed")  # line 569
        info(MARKER + " Switching to branch %sb%02d/r%02d" % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 570
        if not modified(todos):  # line 571
            info("No changes to current file tree")  # line 572
        else:  # integration required  # line 573
            for path, pinfo in todos.deletions.items():  # line 574
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 575
                printo("ADD " + path)  # line 576
            for path, pinfo in todos.additions.items():  # line 577
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 578
                printo("DEL " + path)  # line 579
            for path, pinfo in todos.modifications.items():  # line 580
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 581
                printo("MOD " + path)  # line 582
    m.branch = branch  # line 583
    m.saveBranches()  # store switched path info  # line 584
    info("Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 585

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 587
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 591
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 592
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 593
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 594
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 595
    m = Metadata()  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 596
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 597
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 598
    debug("Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 599

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 602
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 603
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not m.track and not m.picky else conditionalIntersection(onlys, trackingUnion), dontConsider=excps, progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 604
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 605
        if trackingUnion != trackingPatterns:  # nothing added  # line 606
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 607
        else:  # line 608
            info("Nothing to update")  # but write back updated branch info below  # line 609
    else:  # integration required  # line 610
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 611
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 612
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 612
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 613
        for path, pinfo in changes.additions.items():  # line 614
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 615
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 615
            if mrg.value & MergeOperation.REMOVE.value:  # line 616
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 616
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 617
        for path, pinfo in changes.modifications.items():  # line 618
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 619
            binary = not m.isTextType(path)  # type: bool  # line 620
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 621
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 622
                printo(("MOD " if not binary else "BIN ") + path)  # line 623
                while True:  # line 624
                    printo(into)  # TODO print mtime, size differences?  # line 625
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 626
                    if op in ("it" if binary else "itm"):  # line 627
                        break  # line 627
            if op == "t":  # line 628
                printo("THR " + path)  # blockwise copy of contents  # line 629
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 629
            elif op == "m":  # line 630
                current = None  # type: bytes  # line 631
                with open(encode(into), "rb") as fd:  # TODO slurps file  # line 632
                    current = fd.read()  # TODO slurps file  # line 632
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 633
                if current == file:  # line 634
                    debug("No difference to versioned file")  # line 634
                elif file is not None:  # if None, error message was already logged  # line 635
                    contents = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # type: bytes  # line 636
                    if contents != current:  # line 637
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 638
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 638
                    else:  # TODO but update timestamp?  # line 639
                        debug("No change")  # TODO but update timestamp?  # line 639
            else:  # mine or wrong input  # line 640
                printo("MNE " + path)  # nothing to do! same as skip  # line 641
    info("Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 642
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 643
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 644
    m.saveBranches()  # line 645

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 647
    ''' Remove a branch entirely. '''  # line 648
    m, branch, revision, changes, strict, force, trackingPatterns = exitOnChanges(None, options)  # line 649
    if len(m.branches) == 1:  # line 650
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 650
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 651
    if branch is None or branch not in m.branches:  # line 652
        Exit("Cannot delete unknown branch %r" % branch)  # line 652
    debug("Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 653
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 654
    info("Branch b%02d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 655

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 657
    ''' Add a tracked files pattern to current branch's tracked files. '''  # line 658
    force = '--force' in options  # type: bool  # line 659
    m = Metadata()  # type: Metadata  # line 660
    if not m.track and not m.picky:  # line 661
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 661
    if pattern in m.branches[m.branch].tracked:  # line 662
        Exit("Pattern '%s' already tracked" % pattern)  # line 662
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 663
        Exit("The pattern folder doesn't exist. Use --force to add it anyway")  # line 663
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 664
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 665
    m.branches[m.branch].tracked.append(pattern)  # line 666
    m.saveBranches()  # line 667
    info("Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 668

def remove(relPath: 'str', pattern: 'str'):  # line 670
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 671
    m = Metadata()  # type: Metadata  # line 672
    if not m.track and not m.picky:  # line 673
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 673
    if pattern not in m.branches[m.branch].tracked:  # line 674
        suggestion = _coconut.set()  # type: Set[str]  # line 675
        for pat in m.branches[m.branch].tracked:  # line 676
            if fnmatch.fnmatch(pattern, pat):  # line 677
                suggestion.add(pat)  # line 677
        if suggestion:  # TODO use same wording as in move  # line 678
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 678
        Exit("Tracked pattern '%s' not found" % pattern)  # line 679
    m.branches[m.branch].tracked.remove(pattern)  # line 680
    m.saveBranches()  # line 681
    info("Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 682

def ls(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 684
    ''' List specified directory, augmenting with repository metadata. '''  # line 685
    folder = "." if argument is None else argument  # type: str  # line 686
    m = Metadata()  # type: Metadata  # line 687
    info("Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 688
    relPath = os.path.relpath(folder, m.root).replace(os.sep, SLASH)  # type: str  # line 689
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 690
    if '--tags' in options:  # line 691
        printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 692
        return  # line 693
    if '--patterns' in options:  # line 694
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 695
        if out:  # line 696
            printo(out)  # line 696
        return  # line 697
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 698
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 699
        ignore = None  # type: _coconut.typing.Optional[str]  # line 700
        for ig in m.c.ignores:  # line 701
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 702
                ignore = ig  # remember first match  # line 702
                break  # remember first match  # line 702
        if ig:  # line 703
            for wl in m.c.ignoresWhitelist:  # line 704
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 705
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 705
                    break  # found a white list entry for ignored file, undo ignoring it  # line 705
        matches = []  # type: List[str]  # line 706
        if not ignore:  # line 707
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 708
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 709
                    matches.append(os.path.basename(pattern))  # line 709
        matches.sort(key=lambda element: len(element))  # line 710
        printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "..."), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 711

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 713
    ''' List previous commits on current branch. '''  # line 714
    m = Metadata()  # type: Metadata  # line 715
    m.loadBranch(m.branch)  # knows commit history  # line 716
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + " Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 717
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 718
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, max(m.commits))  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 719
    maxWidth = max([wcswidth((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) for commit in m.commits.values()])  # type: int  # line 720
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 721
    for no in range(max(m.commits) + 1):  # line 722
        commit = m.commits[no]  # type: CommitInfo  # line 723
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 724
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # side-effect: updates m.paths  # line 725
        _add = news - olds  # type: FrozenSet[str]  # line 726
        _del = olds - news  # type: FrozenSet[str]  # line 727
        _mod = frozenset([_ for _, info in nxts.items() if _ in m.paths and m.paths[_].size != info.size and (m.paths[_].hash != info.hash if m.strict else m.paths[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 728
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 729
        printo("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT) |%s|%s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)).ljust(maxWidth), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 730
        if '--changes' in options:  # line 731
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}))  # line 731
        if '--diff' in options:  # TODO needs to extract code from diff first to be reused here  # line 732
            pass  # TODO needs to extract code from diff first to be reused here  # line 732
        olds = news  # line 733

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 735
    ''' Exported entire repository as archive for easy transfer. '''  # line 736
    force = '--force' in options  # type: bool  # line 737
    progress = '--progress' in options  # type: bool  # line 738
    import zipfile  # TODO display compression ratio (if any)  # line 739
    try:  # line 740
        import zlib  # line 740
        compression = zipfile.ZIP_DEFLATED  # line 740
    except:  # line 741
        compression = zipfile.ZIP_STORED  # line 741

    if argument is None:  # line 743
        Exit("Argument missing (target filename)")  # line 743
    argument = argument if "." in argument else argument + ".sos.zip"  # line 744
    if os.path.exists(encode(argument)) and not force:  # line 745
        Exit("Target archive already exists. Use 'sos dump <arget> --force' to override")  # line 745
    with zipfile.ZipFile(argument, "w", compression) as fd:  # line 746
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 747
        counter = Counter(-1)  # type: Counter  # line 748
        timer = time.time()  # type: float  # line 748
        totalsize = 0  # type: int  # line 749
        start_time = time.time()  # type: float  # line 750
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 751
            dirpath = decode(dirpath)  # line 752
            dirnames[:] = [decode(d) for d in dirnames]  # line 753
            filenames[:] = [decode(f) for f in filenames]  # line 754
            for filename in filenames:  # line 755
                newtime = time.time()  # type: float  # TODO alternatively count bytes and use a threshold there  # line 756
                abspath = os.path.join(dirpath, filename)  # type: str  # line 757
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 758
                totalsize += os.stat(encode(abspath)).st_size  # line 759
                if progress and newtime - timer > .1:  # line 760
                    printo(("\rDumping %s@%6.2f MiB/s %s" % (PROGRESS_MARKER[int(counter.inc() % 4)], totalsize / (MEBI * (time.time() - start_time)), filename)).ljust(termwidth), nl="")  # line 760
                    timer = newtime  # line 760
                fd.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 761
    printo("\rDone dumping entire repository.".ljust(termwidth), nl="")  # clean line  # line 762

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 764
    command, key, value = (arguments + [None] * 2)[:3]  # line 765
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 766
        Exit("Unknown config command")  # line 766
    local = "--local" in options  # type: bool  # line 767
    m = Metadata()  # type: Metadata  # loads layered configuration as well. TODO warning if repo not exists  # line 768
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 769
    if command == "set":  # line 770
        if None in (key, value):  # line 771
            Exit("Key or value not specified")  # line 771
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 772
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 772
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 773
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 773
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 774
    elif command == "unset":  # line 775
        if key is None:  # line 776
            Exit("No key specified")  # line 776
        if key not in c.keys():  # line 777
            Exit("Unknown key")  # line 777
        del c[key]  # line 778
    elif command == "add":  # line 779
        if None in (key, value):  # line 780
            Exit("Key or value not specified")  # line 780
        if key not in CONFIGURABLE_LISTS:  # line 781
            Exit("Unsupported key %r" % key)  # line 781
        if key not in c.keys():  # add list  # line 782
            c[key] = [value]  # add list  # line 782
        elif value in c[key]:  # line 783
            Exit("Value already contained, nothing to do")  # line 783
        if ";" in value:  # line 784
            c[key].append(removePath(key, value))  # line 784
        else:  # line 785
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 785
    elif command == "rm":  # line 786
        if None in (key, value):  # line 787
            Exit("Key or value not specified")  # line 787
        if key not in c.keys():  # line 788
            Exit("Unknown key %r" % key)  # line 788
        if value not in c[key]:  # line 789
            Exit("Unknown value %r" % value)  # line 789
        c[key].remove(value)  # line 790
    else:  # Show or list  # line 791
        if key == "flags":  # list valid configuration items  # line 792
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 792
        elif key == "lists":  # line 793
            printo(", ".join(CONFIGURABLE_LISTS))  # line 793
        elif key == "texts":  # line 794
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 794
        else:  # line 795
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 796
            c = m.c  # always use full configuration chain  # line 797
            try:  # attempt single key  # line 798
                assert key is not None  # line 799
                c[key]  # line 799
                l = key in c.keys()  # type: bool  # line 800
                g = key in c.__defaults.keys()  # type: bool  # line 800
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 801
            except:  # normal value listing  # line 802
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 803
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 804
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 805
                for k, vt in sorted(vals.items()):  # line 806
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 806
                if len(c.keys()) == 0:  # line 807
                    info("No local configuration stored")  # line 807
                if len(c.__defaults.keys()) == 0:  # line 808
                    info("No global configuration stored")  # line 808
        return  # in case of list, no need to store anything  # line 809
    if local:  # saves changes of repoConfig  # line 810
        m.repoConf = c.__map  # saves changes of repoConfig  # line 810
        m.saveBranches()  # saves changes of repoConfig  # line 810
        Exit("OK", code=0)  # saves changes of repoConfig  # line 810
    else:  # global config  # line 811
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 812
        if f is None:  # line 813
            error("Error saving user configuration: %r" % h)  # line 813
        else:  # line 814
            Exit("OK", code=0)  # line 814

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[]):  # line 816
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique. '''  # line 817
    force = '--force' in options  # type: bool  # line 818
    soft = '--soft' in options  # type: bool  # line 819
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 820
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 820
    m = Metadata()  # type: Metadata  # line 821
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 822
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 823
    if not matching and not force:  # line 824
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 824
    if not m.track and not m.picky:  # line 825
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 825
    if pattern not in m.branches[m.branch].tracked:  # line 826
        for tracked in (t for t in m.branches[m.branch].tracked if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 827
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 828
            if alternative:  # line 829
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 829
        if not (force or soft):  # line 830
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 830
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 831
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 832
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 833
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 837
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 838
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 838
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 839
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 840
    if len({st[1] for st in matches}) != len(matches):  # line 841
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 841
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 842
    if os.path.exists(encode(newRelPath)):  # line 843
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 844
        if exists and not (force or soft):  # line 845
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 845
    else:  # line 846
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 846
    if not soft:  # perform actual renaming  # line 847
        for (source, target) in matches:  # line 848
            try:  # line 849
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 849
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 850
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 850
    m.branches[m.branch].tracked[m.branches[m.branch].tracked.index(pattern)] = newPattern  # line 851
    m.saveBranches()  # line 852

def parse(root: 'str', cwd: 'str'):  # line 854
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm. '''  # line 855
    debug("Parsing command-line arguments...")  # line 856
    try:  # line 857
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 858
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: Union[List[str], str, None]  # line 859
        if len(arguments) == 0:  # line 860
            arguments = [None]  # line 860
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 861
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 862
        debug("Processing command %r with arguments %r and options %r." % (("" if command is None else command), arguments if arguments else "", options))  # line 863
        if command[:1] in "amr":  # line 864
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 864
        if command[:1] == "m":  # line 865
            if len(arguments) < 2:  # line 866
                Exit("Need a second file pattern argument as target for move/rename command")  # line 866
            newRelPath, newPattern = relativize(root, os.path.join(cwd, options[0]))  # line 867
        if command[:1] == "a":  # line 868
            add(relPath, pattern, options)  # line 868
        elif command[:1] == "b":  # line 869
            branch(arguments[0], options)  # line 869
        elif command[:2] == "ch":  # line 870
            changes(arguments[0], options, onlys, excps)  # line 870
        elif command[:3] == "com":  # line 871
            commit(arguments[0], options, onlys, excps)  # line 871
        elif command[:2] == "ci":  # line 872
            commit(arguments[0], options, onlys, excps)  # line 872
        elif command[:3] == 'con':  # line 873
            config(arguments, options)  # line 873
        elif command[:2] == "de":  # line 874
            delete(arguments[0], options)  # line 874
        elif command[:2] == "di":  # line 875
            diff(arguments[0], options, onlys, excps)  # line 875
        elif command[:2] == "du":  # line 876
            dump(arguments[0], options)  # line 876
        elif command[:1] == "h":  # line 877
            usage(APPNAME, version.__version__)  # line 877
        elif command[:2] == "lo":  # line 878
            log(options)  # line 878
        elif command[:2] == "li":  # TODO handle absolute paths as well, also for Windows? think through  # line 879
            ls(relativize(root, cwd if not arguments else os.path.join(cwd, arguments[0]))[1], options)  # TODO handle absolute paths as well, also for Windows? think through  # line 879
        elif command[:2] == "ls":  # TODO avoid and/or normalize root super paths (..)  # line 880
            ls(relativize(root, cwd if not arguments else os.path.join(cwd, arguments[0]))[1], options)  # TODO avoid and/or normalize root super paths (..)  # line 880
        elif command[:1] == "m":  # line 881
            move(relPath, pattern, newRelPath, newPattern, options[1:])  # line 881
        elif command[:2] == "of":  # line 882
            offline(arguments[0], options)  # line 882
        elif command[:2] == "on":  # line 883
            online(options)  # line 883
        elif command[:1] == "r":  # line 884
            remove(relPath, pattern)  # line 884
        elif command[:2] == "st":  # line 885
            status(options, onlys, excps)  # line 885
        elif command[:2] == "sw":  # line 886
            switch(arguments[0], options, onlys, excps)  # line 886
        elif command[:1] == "u":  # line 887
            update(arguments[0], options, onlys, excps)  # line 887
        elif command[:1] == "v":  # line 888
            usage(APPNAME, version.__version__, short=True)  # line 888
        else:  # line 889
            Exit("Unknown command '%s'" % command)  # line 889
        Exit(code=0)  # line 890
    except (Exception, RuntimeError) as E:  # line 891
        exception(E)  # line 892
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing.")  # line 893

def main():  # line 895
    global debug, info, warn, error  # line 896
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 897
    _log = Logger(logging.getLogger(__name__))  # line 898
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 898
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 899
        sys.argv.remove(option)  # clean up program arguments  # line 899
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 900
        usage()  # line 900
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 901
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 902
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 903
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 904
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in ["h", "v"]:  # in offline mode or just going offline TODO what about git config?  # line 905
        cwd = os.getcwd()  # line 906
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 907
        parse(root, cwd)  # line 908
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 909
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 910
        import subprocess  # only required in this section  # line 911
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 912
        inp = ""  # type: str  # line 913
        while True:  # line 914
            so, se = process.communicate(input=inp)  # line 915
            if process.returncode is not None:  # line 916
                break  # line 916
            inp = sys.stdin.read()  # line 917
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 918
            if root is None:  # line 919
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 919
            m = Metadata(root)  # type: Metadata  # line 920
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 921
            m.saveBranches()  # line 922
    else:  # line 923
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 923


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 927
level = logging.DEBUG if verbose else logging.INFO  # line 928
force_sos = '--sos' in sys.argv  # type: bool  # line 929
force_vcs = '--vcs' in sys.argv  # type: bool  # line 930
_log = Logger(logging.getLogger(__name__))  # line 931
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 931
if __name__ == '__main__':  # line 932
    main()  # line 932
