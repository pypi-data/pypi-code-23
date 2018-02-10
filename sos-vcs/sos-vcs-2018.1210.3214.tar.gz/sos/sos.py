#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x7c2db802

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
        _.track = None  # type: bool  # line 57
        _.picky = None  # type: bool  # line 57
        _.strict = None  # type: bool  # line 57
        _.compress = None  # type: bool  # line 57
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
        tracked = [t for t in _.branches[_.branch].tracked]  # type: List[str]  # copy  # line 131
        untracked = [u for u in _.branches[_.branch].untracked]  # type: List[str]  # line 132
        os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 133
        _.loadBranch(_.branch)  # line 134
        revision = max(_.commits)  # type: int  # line 135
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 136
        for path, pinfo in _.paths.items():  # line 137
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 138
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 139
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 140
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 141
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].inSync, tracked, untracked)  # save branch info, before storing repo state at caller  # line 142

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 144
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 149
        simpleMode = not (_.track or _.picky)  # line 150
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # in case of initial branch creation  # line 151
        untracked = [t for t in _.branches[_.branch].untracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # line 152
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 153
        _.paths = {}  # type: Dict[str, PathInfo]  # line 154
        if simpleMode:  # branches from file system state  # line 155
            changes = _.findChanges(branch, 0, progress=simpleMode)  # type: ChangeSet  # creates revision folder and versioned files  # line 156
            _.listChanges(changes)  # line 157
            _.paths.update(changes.additions.items())  # line 158
        else:  # tracking or picky mode: branch from latest revision  # line 159
            os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 160
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 161
                _.loadBranch(_.branch)  # line 162
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 163
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 164
                for path, pinfo in _.paths.items():  # line 165
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 166
        ts = int(time.time() * 1000)  # line 167
        _.commits = {0: CommitInfo(0, ts, ("Branched on %s" % strftime(ts) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 168
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 169
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 170
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked, untracked)  # save branch info, in case it is needed  # line 171

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 173
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 174
        shutil.rmtree(encode(os.path.join(_.root, metaFolder, "b%d" % branch)))  # line 175
        binfo = _.branches[branch]  # line 176
        del _.branches[branch]  # line 177
        _.branch = max(_.branches)  # line 178
        _.saveBranches()  # line 179
        _.commits.clear()  # line 180
        return binfo  # line 181

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 183
        ''' Load all file information from a commit meta data. '''  # line 184
        with codecs.open(encode(branchFolder(branch, revision, base=_.root, file=metaFile)), "r", encoding=UTF8) as fd:  # line 185
            _.paths = json.load(fd)  # line 186
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 187
        _.branch = branch  # line 188

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 190
        ''' Save all file information to a commit meta data file. '''  # line 191
        target = branchFolder(branch, revision, base=_.root)  # type: str  # line 192
        try:  # line 193
            os.makedirs(encode(target))  # line 193
        except:  # line 194
            pass  # line 194
        with codecs.open(encode(os.path.join(target, metaFile)), "w", encoding=UTF8) as fd:  # line 195
            json.dump(_.paths, fd, ensure_ascii=False)  # line 196

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'ChangeSet':  # line 198
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        The function returns the state of file tree *differences*, unless "inverse" is True -> then return original data
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes (always overrides considerOnly)
        progress: Show file names during processing
    '''  # line 207
        write = branch is not None and revision is not None  # line 208
        if write:  # line 209
            try:  # line 210
                os.makedirs(encode(branchFolder(branch, revision, base=_.root)))  # line 210
            except FileExistsError:  # HINT "try" only necessary for testing hash collisions  # line 211
                pass  # HINT "try" only necessary for testing hash collisions  # line 211
        changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 212
        counter = Counter(-1)  # type: Counter  # line 213
        timer = time.time()  # type: float  # line 213
        hashed = None  # type: _coconut.typing.Optional[str]  # line 214
        written = None  # type: int  # line 214
        compressed = 0  # type: int  # line 214
        original = 0  # type: int  # line 214
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 215
        for path, pinfo in _.paths.items():  # line 216
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 217
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 220
        for path, dirnames, filenames in os.walk(_.root):  # line 221
            path = decode(path)  # line 222
            dirnames[:] = [decode(d) for d in dirnames]  # line 223
            filenames[:] = [decode(f) for f in filenames]  # line 224
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 225
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 226
            dirnames.sort()  # line 227
            filenames.sort()  # line 227
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 228
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 229
            if dontConsider:  # line 230
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 231
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 232
                filename = relPath + SLASH + file  # line 233
                filepath = os.path.join(path, file)  # line 234
                try:  # line 235
                    stat = os.stat(encode(filepath))  # line 235
                except Exception as E:  # line 236
                    exception(E)  # line 236
                    continue  # line 236
                size, mtime, newtime = stat.st_size, int(stat.st_mtime * 1000), time.time()  # line 237
                if progress and newtime - timer > .1:  # line 238
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", PROGRESS_MARKER[int(counter.inc() % 4)], filename)  # line 239
                    printo(outstring + " " * max(0, termWidth - len(outstring)), nl="")  # line 240
                    timer = newtime  # line 240
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 241
                    nameHash = hashStr(filename)  # line 242
                    try:  # line 243
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=nameHash) if write else None) if size > 0 else (None, 0)  # line 244
                        changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 245
                        compressed += written  # line 246
                        original += size  # line 246
                    except Exception as E:  # line 247
                        exception(E)  # line 247
                    continue  # with next file  # line 248
                last = _.paths[filename]  # filename is known - check for modifications  # line 249
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 250
                    try:  # line 251
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if size > 0 else (None, 0)  # line 252
                        changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 253
                        continue  # line 253
                    except Exception as E:  # line 254
                        exception(E)  # line 254
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and tryOrDefault(lambda: (hashFile(filepath, _.compress)[0] != last.hash), default=False)):  # detected a modification TODO wrap hashFile exception  # line 255
                    try:  # line 256
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 257
                        changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 258
                    except Exception as E:  # line 259
                        exception(E)  # line 259
                else:  # with next file  # line 260
                    continue  # with next file  # line 260
                compressed += written  # line 261
                original += last.size if inverse else size  # line 261
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 262
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 262
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 263
            for file in names:  # line 264
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 265
                    continue  # don't mark ignored files as deleted  # line 265
                pth = path + SLASH + file  # type: str  # line 266
                changes.deletions[pth] = _.paths[pth]  # line 267
        if progress:  # forces new line  # line 268
            printo("\rChecking finished.%s" % ((" Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else "").ljust(termWidth))  # forces new line  # line 268
        else:  # line 269
            debug("Finished detecting changes.%s" % ((" Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else ""))  # line 269
        return changes  # line 270

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 272
        ''' Returns nothing, just updates _.paths in place. '''  # line 273
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 274

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 276
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 277
        _.loadCommit(branch, 0)  # load initial paths  # line 278
        if incrementally:  # line 279
            yield _.paths  # line 279
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 280
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 280
        for rev in range(1, revision + 1):  # line 281
            m.loadCommit(branch, rev)  # line 282
            for p, info in m.paths.items():  # line 283
                if info.size == None:  # line 284
                    del _.paths[p]  # line 284
                else:  # line 285
                    _.paths[p] = info  # line 285
            if incrementally:  # line 286
                yield _.paths  # line 286
        yield None  # for the default case - not incrementally  # line 287

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 289
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 292
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 293
            return (_.branch, -1)  # no branch/revision specified  # line 293
        argument = argument.strip()  # line 294
        if argument.startswith(SLASH):  # current branch  # line 295
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 295
        if argument.endswith(SLASH):  # line 296
            try:  # line 297
                return (_.getBranchByName(argument[:-1]), -1)  # line 297
            except ValueError:  # line 298
                Exit("Unknown branch label '%s'" % argument)  # line 298
        if SLASH in argument:  # line 299
            b, r = argument.split(SLASH)[:2]  # line 300
            try:  # line 301
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 301
            except ValueError:  # line 302
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 302
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 303
        if branch not in _.branches:  # line 304
            branch = None  # line 304
        try:  # either branch name/number or reverse/absolute revision number  # line 305
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 305
        except:  # line 306
            Exit("Unknown branch label or wrong number format")  # line 306
        Exit("This should never happen. Please create a issue report")  # line 307
        return (None, None)  # line 307

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 309
        while True:  # find latest revision that contained the file physically  # line 310
            source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 311
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 312
                break  # line 312
            revision -= 1  # line 313
            if revision < 0:  # line 314
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 314
        return revision, source  # line 315

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 317
        ''' Copy versioned file to other branch/revision. '''  # line 318
        target = branchFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 319
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 320
        shutil.copy2(encode(source), encode(target))  # line 321

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 323
        ''' Return file contents, or copy contents into file path provided. '''  # line 324
        source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 325
        try:  # line 326
            with openIt(source, "r", _.compress) as fd:  # line 327
                if toFile is None:  # read bytes into memory and return  # line 328
                    return fd.read()  # read bytes into memory and return  # line 328
                with open(encode(toFile), "wb") as to:  # line 329
                    while True:  # line 330
                        buffer = fd.read(bufSize)  # line 331
                        to.write(buffer)  # line 332
                        if len(buffer) < bufSize:  # line 333
                            break  # line 333
                    return None  # line 334
        except Exception as E:  # line 335
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 335
        return None  # line 336

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 338
        ''' Recreate file for given revision, or return binary contents if path is None. '''  # line 339
        if relPath is None:  # just return contents  # line 340
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 340
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 341
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 342
            try:  # line 343
                os.makedirs(encode(os.path.dirname(target)))  # line 343
            except:  # line 344
                pass  # line 344
        if pinfo.size == 0:  # line 345
            with open(encode(target), "wb"):  # line 346
                pass  # line 346
            try:  # update access/modification timestamps on file system  # line 347
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 347
            except Exception as E:  # line 348
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 348
            return None  # line 349
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 350
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 352
            while True:  # line 353
                buffer = fd.read(bufSize)  # line 354
                to.write(buffer)  # line 355
                if len(buffer) < bufSize:  # line 356
                    break  # line 356
        try:  # update access/modification timestamps on file system  # line 357
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 357
        except Exception as E:  # line 358
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 358
        return None  # line 359

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None, negative: 'bool'=False) -> 'FrozenSet[str]':  # line 361
        ''' Returns list of tracking patterns (or untracking patterns if negative) for provided branch or current branch. '''  # line 362
        return _coconut.frozenset() if not (_.track or _.picky) else frozenset(_.branches[(_.branch if branch is None else branch)].untracked if negative else _.branches[(_.branch if branch is None else branch)].tracked)  # line 363


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 367
    ''' Initial command to start working offline. '''  # line 368
    if os.path.exists(encode(metaFolder)):  # line 369
        if '--force' not in options:  # line 370
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 370
        try:  # line 371
            for entry in os.listdir(metaFolder):  # line 372
                resource = metaFolder + os.sep + entry  # line 373
                if os.path.isdir(resource):  # line 374
                    shutil.rmtree(encode(resource))  # line 374
                else:  # line 375
                    os.unlink(encode(resource))  # line 375
        except:  # line 376
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 376
    m = Metadata(offline=True)  # type: Metadata  # line 377
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 378
        m.compress = True  # plain file copies instead of compressed ones  # line 378
    if '--picky' in options or m.c.picky:  # Git-like  # line 379
        m.picky = True  # Git-like  # line 379
    elif '--track' in options or m.c.track:  # Svn-like  # line 380
        m.track = True  # Svn-like  # line 380
    if '--strict' in options or m.c.strict:  # always hash contents  # line 381
        m.strict = True  # always hash contents  # line 381
    info(MARKER + "Going offline...")  # line 382
    m.createBranch(0, (defaults["defaultbranch"] if argument is None else argument), initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 383
    m.branch = 0  # line 384
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 385
    info(MARKER + "Offline repository prepared. Use 'sos online' to finish offline work")  # line 386

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 388
    ''' Finish working offline. '''  # line 389
    info(MARKER + "Going back online...")  # line 390
    force = '--force' in options  # type: bool  # line 391
    m = Metadata()  # type: Metadata  # line 392
    m.loadBranches()  # line 393
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 394
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 394
    strict = '--strict' in options or m.strict  # type: bool  # line 395
    if options.count("--force") < 2:  # line 396
        changes = m.findChanges(checkContent=strict, considerOnly=None if not (m.track or m.picky) else m.getTrackingPatterns(), dontConsider=None if not (m.track or m.picky) else m.getTrackingPatterns(negative=True), progress='--progress' in options)  # type: ChangeSet  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 397
        if modified(changes):  # line 398
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 402
    try:  # line 403
        shutil.rmtree(encode(metaFolder))  # line 403
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 403
    except Exception as E:  # line 404
        Exit("Error removing offline repository: %r" % E)  # line 404
    info(MARKER + "Offline repository removed, you're back online")  # line 405

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 407
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 408
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 409
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 410
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 411
    m = Metadata()  # type: Metadata  # line 412
    m.loadBranch(m.branch)  # line 413
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 414
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 414
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 415
    info(MARKER + "Branching to %sbranch b%02d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 416
    if last:  # branch from branch's last revision  # line 417
        m.duplicateBranch(branch, (("" if argument is None else argument)) + " (Branched from r%02d/b%02d)" % (m.branch, max(m.commits.keys())))  # branch from branch's last revision  # line 417
    else:  #  branch from current file tree state  # line 418
        m.createBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  #  branch from current file tree state  # line 418
    if not stay:  # line 419
        m.branch = branch  # line 420
        m.saveBranches()  # line 421
    info(MARKER + "%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 422

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 424
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 425
    m = Metadata()  # type: Metadata  # line 426
    branch = None  # type: _coconut.typing.Optional[int]  # line 426
    revision = None  # type: _coconut.typing.Optional[int]  # line 426
    strict = '--strict' in options or m.strict  # type: bool  # line 427
    branch, revision = m.parseRevisionString(argument)  # line 428
    if branch not in m.branches:  # line 429
        Exit("Unknown branch")  # line 429
    m.loadBranch(branch)  # knows commits  # line 430
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 431
    if revision < 0 or revision > max(m.commits):  # line 432
        Exit("Unknown revision r%02d" % revision)  # line 432
    info(MARKER + "Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 433
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 434
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # type: ChangeSet  # line 435
    m.listChanges(changes)  # line 440
    return changes  # for unit tests only TODO remove  # line 441

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 443
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 444
    m = Metadata()  # type: Metadata  # line 445
    branch = None  # type: _coconut.typing.Optional[int]  # line 445
    revision = None  # type: _coconut.typing.Optional[int]  # line 445
    strict = '--strict' in options or m.strict  # type: bool  # line 446
    _from = {None: option.split("--from=")[1] for option in options if option.startswith("--from=")}.get(None, None)  # type: _coconut.typing.Optional[str]  # TODO implement  # line 447
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 448
    if branch not in m.branches:  # line 449
        Exit("Unknown branch")  # line 449
    m.loadBranch(branch)  # knows commits  # line 450
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 451
    if revision < 0 or revision > max(m.commits):  # line 452
        Exit("Unknown revision r%02d" % revision)  # line 452
    info(MARKER + "Textual differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 453
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 454
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # type: ChangeSet  # line 455
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 460
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 461

    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 463
        content = None  # type: _coconut.typing.Optional[bytes]  # line 464
        if pinfo.size == 0:  # empty file contents  # line 465
            content = b""  # empty file contents  # line 465
        else:  # versioned file  # line 466
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 466
            assert content is not None  # versioned file  # line 466
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 467
        blocks = None  # type: List[MergeBlock]  # line 468
        nl = None  # type: bytes  # line 468
        blocks, nl = merge(filename=abspath, into=content, diffOnly=True)  # only determine change blocks  # line 469
        printo("DIF %s%s %s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else "", NL_NAMES[nl]))  # line 470
        for block in blocks:  # line 471
            if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:  # line 472
                pass  # TODO print some previous and following lines - which aren't accessible here anymore  # line 473
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 474
                for no, line in enumerate(block.lines):  # line 475
                    printo("+++ %04d |%s|" % (no + block.line, line))  # line 476
            elif block.tipe == MergeBlockType.REMOVE:  # line 477
                for no, line in enumerate(block.lines):  # line 478
                    printo("--- %04d |%s|" % (no + block.line, line))  # line 479
            elif block.tipe == MergeBlockType.REPLACE:  # TODO for MODIFY also show intra-line change ranges (TODO remove if that code was also removed)  # line 480
                for no, line in enumerate(block.replaces.lines):  # line 481
                    printo("- | %04d |%s|" % (no + block.replaces.line, line))  # line 482
                for no, line in enumerate(block.lines):  # line 483
                    printo("+ | %04d |%s|" % (no + block.line, line))  # line 484
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 488
    ''' Create new revision from file tree changes vs. last commit. '''  # line 489
    m = Metadata()  # type: Metadata  # line 490
    if argument is not None and argument in m.tags:  # line 491
        Exit("Illegal commit message. It was already used as a tag name")  # line 491
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 492
# No untracking patterns needed here
    if m.picky and not trackingPatterns:  # line 494
        Exit("No file patterns staged for commit in picky mode")  # line 494
    changes = None  # type: ChangeSet  # line 495
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but aborts if no changes  # line 496
    info((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 497
    m.paths = changes.additions  # line 498
    m.paths.update(changes.modifications)  # update pathset to changeset only  # line 499
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changes.deletions.items()})  # line 500
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 501
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 502
    m.saveBranch(m.branch)  # line 503
    m.loadBranches()  # TODO is it necessary to load again?  # line 504
    if m.picky:  # remove tracked patterns  # line 505
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 505
    else:  # track or simple mode: set branch dirty  # line 506
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 506
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 507
        m.tags.append(argument)  # memorize unique tag  # line 507
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 507
    m.saveBranches()  # line 508
    info(MARKER + "Created new revision r%02d%s (+%02d/-%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))  # TODO show compression factor  # line 509

def status(options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 511
    ''' Show branches and current repository state. '''  # line 512
    m = Metadata()  # type: Metadata  # line 513
    current = m.branch  # type: int  # line 514
    strict = '--strict' in options or m.strict  # type: bool  # line 515
    info(MARKER + "Offline repository status")  # line 516
    info("Installation path:   %s" % os.path.abspath(os.path.dirname(__file__)))  # line 517
    info("Current SOS version: %s" % version.__version__)  # line 518
    info("At creation version: %s" % m.version)  # line 519
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 520
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 521
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 522
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 523
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 524
    m.loadBranch(m.branch)  # line 525
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 508  # line 526
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress=True)  # type: ChangeSet  # line 527
    printo("File tree %s" % ("has changes vs. last revision of current branch" if modified(changes) else "is unchanged"))  # line 532
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 533
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 534
        m.loadBranch(branch.number)  # knows commit history  # line 535
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 536
    if m.track or m.picky and (len(m.branches[m.branch].tracked) > 0 or len(m.branches[m.branch].untracked) > 0):  # line 537
        info("\nTracked file patterns:")  # TODO print matching untracking patterns side-by-side  # line 538
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 539
        info("\nUntracked file patterns:")  # line 540
        printo(ajoin("  | ", m.branches[m.branch].untracked, "\n"))  # line 541

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str], FrozenSet[str]]':  # line 543
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags.
  '''  # line 549
    m = Metadata()  # type: Metadata  # line 550
    force = '--force' in options  # type: bool  # line 551
    strict = '--strict' in options or m.strict  # type: bool  # line 552
    if argument is not None:  # line 553
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 554
        if branch is None:  # line 555
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 555
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 556

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 559
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 560
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 561
    changes = m.findChanges(m.branch if commit else None, max(m.commits) + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress='--progress' in options)  # type: ChangeSet  # line 562
    if check and modified(changes) and not force:  # line 567
        m.listChanges(changes)  # line 568
        if not commit:  # line 569
            Exit("File tree contains changes. Use --force to proceed")  # line 569
    elif commit and not force:  #  and not check  # line 570
        Exit("Nothing to commit")  #  and not check  # line 570

    if argument is not None:  # branch/revision specified  # line 572
        m.loadBranch(branch)  # knows commits of target branch  # line 573
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 574
        if revision < 0 or revision > max(m.commits):  # line 575
            Exit("Unknown revision r%02d" % revision)  # line 575
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch), m.getTrackingPatterns(branch, negative=True))  # line 576
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns, untrackingPatterns)  # line 577

def switch(argument: 'str', options: 'List[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 579
    ''' Continue work on another branch, replacing file tree changes. '''  # line 580
    m, branch, revision, changes, strict, _force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, ["--force"] + options)  # line 581
    force = '--force' in options  # type: bool  # needed as we fake force in above access  # line 582

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 585
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked, untracked=m.branches[branch].untracked)  # line 586
    else:  # full file switch  # line 587
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 588
        todos = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((untrackingPatterns | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # type: ChangeSet  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 589

# Now check for potential conflicts
        changes.deletions.clear()  # local deletions never create conflicts, modifications always  # line 596
        rms = []  # type: _coconut.typing.Sequence[str]  # local additions can be ignored if restoration from switch would be same  # line 597
        for a, pinfo in changes.additions.items():  # has potential corresponding re-add in switch operation:  # line 598
            if a in todos.deletions and pinfo.size == todos.deletions[a].size and (pinfo.hash == todos.deletions[a].hash if m.strict else pinfo.mtime == todos.deletions[a].mtime):  # line 599
                rms.append(a)  # line 599
        for rm in rms:  # TODO could also silently accept remote DEL for local ADD  # line 600
            del changes.additions[rm]  # TODO could also silently accept remote DEL for local ADD  # line 600
        if modified(changes) and not force:  # line 601
            m.listChanges(changes)  # line 601
            Exit("File tree contains changes. Use --force to proceed")  # line 601
        info(MARKER + "Switching to branch %sb%02d/r%02d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 602
        if not modified(todos):  # line 603
            info("No changes to current file tree")  # line 604
        else:  # integration required  # line 605
            for path, pinfo in todos.deletions.items():  # line 606
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 607
                printo("ADD " + path)  # line 608
            for path, pinfo in todos.additions.items():  # line 609
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 610
                printo("DEL " + path)  # line 611
            for path, pinfo in todos.modifications.items():  # line 612
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 613
                printo("MOD " + path)  # line 614
    m.branch = branch  # line 615
    m.saveBranches()  # store switched path info  # line 616
    info(MARKER + "Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 617

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 619
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 623
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 624
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 625
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 626
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 627
    m = Metadata()  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 628
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 629
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 630
    info(MARKER + "Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 631

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 634
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 635
    untrackingUnion = untrackingPatterns | m.getTrackingPatterns(branch, negative=True)  # type: FrozenSet[str]  # line 636
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingUnion), dontConsider=excps if not (m.track or m.picky) else (untrackingUnion if onlys is None else onlys), progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 637
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 642
        if trackingUnion != trackingPatterns:  # nothing added  # line 643
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 644
        else:  # line 645
            info("Nothing to update")  # but write back updated branch info below  # line 646
    else:  # integration required  # line 647
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 648
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 649
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 649
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 650
        for path, pinfo in changes.additions.items():  # line 651
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 652
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 652
            if mrg.value & MergeOperation.REMOVE.value:  # line 653
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 653
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 654
        for path, pinfo in changes.modifications.items():  # line 655
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 656
            binary = not m.isTextType(path)  # type: bool  # line 657
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 658
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 659
                printo(("MOD " if not binary else "BIN ") + path)  # line 660
                while True:  # line 661
                    printo(into)  # TODO print mtime, size differences?  # line 662
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 663
                    if op in ("it" if binary else "itm"):  # line 664
                        break  # line 664
            if op == "t":  # line 665
                printo("THR " + path)  # blockwise copy of contents  # line 666
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 666
            elif op == "m":  # line 667
                current = None  # type: bytes  # line 668
                with open(encode(into), "rb") as fd:  # TODO slurps file  # line 669
                    current = fd.read()  # TODO slurps file  # line 669
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 670
                if current == file:  # line 671
                    debug("No difference to versioned file")  # line 671
                elif file is not None:  # if None, error message was already logged  # line 672
                    contents = None  # type: bytes  # line 673
                    nl = None  # type: bytes  # line 673
                    contents, nl = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # line 674
                    if contents != current:  # line 675
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 676
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 676
                    else:  # TODO but update timestamp?  # line 677
                        debug("No change")  # TODO but update timestamp?  # line 677
            else:  # mine or wrong input  # line 678
                printo("MNE " + path)  # nothing to do! same as skip  # line 679
    info(MARKER + "Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 680
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 681
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 682
    m.saveBranches()  # line 683

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 685
    ''' Remove a branch entirely. '''  # line 686
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options)  # line 687
    if len(m.branches) == 1:  # line 688
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 688
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 689
    if branch is None or branch not in m.branches:  # line 690
        Exit("Cannot delete unknown branch %r" % branch)  # line 690
    info(MARKER + "Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 691
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 692
    info(MARKER + "Branch b%02d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 693

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[], negative: 'bool'=False):  # line 695
    ''' Add a tracked files pattern to current branch's tracked files. negative means tracking blacklisting. '''  # line 696
    force = '--force' in options  # type: bool  # line 697
    m = Metadata()  # type: Metadata  # line 698
    if not (m.track or m.picky):  # line 699
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 699
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 700
    if pattern in patterns:  # line 701
        Exit("Pattern '%s' already tracked" % pattern)  # line 701
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 702
        Exit("The pattern folder doesn't exist. Use --force to add the file pattern anyway")  # line 702
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 703
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 704
    patterns.append(pattern)  # line 705
    m.saveBranches()  # line 706
    info(MARKER + "Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 707

def remove(relPath: 'str', pattern: 'str', negative: 'bool'=False):  # line 709
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 710
    m = Metadata()  # type: Metadata  # line 711
    if not (m.track or m.picky):  # line 712
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 712
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 713
    if pattern not in patterns:  # line 714
        suggestion = _coconut.set()  # type: Set[str]  # line 715
        for pat in patterns:  # line 716
            if fnmatch.fnmatch(pattern, pat):  # line 717
                suggestion.add(pat)  # line 717
        if suggestion:  # TODO use same wording as in move  # line 718
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 718
        Exit("Tracked pattern '%s' not found" % pattern)  # line 719
    patterns.remove(pattern)  # line 720
    m.saveBranches()  # line 721
    info(MARKER + "Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 722

def ls(folder: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 724
    ''' List specified directory, augmenting with repository metadata. '''  # line 725
    folder = (os.getcwd() if folder is None else folder)  # line 726
    m = Metadata()  # type: Metadata  # line 727
    info(MARKER + "Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 728
    relPath = relativize(m.root, os.path.join(folder, "-"))[0]  # type: str  # line 729
    if relPath.startswith(".."):  # line 730
        Exit("Cannot list contents of folder outside offline repository")  # line 730
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 731
    untrackingPatterns = m.getTrackingPatterns(negative=True) if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 732
    if '--tags' in options:  # line 733
        printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 734
        return  # line 735
    if '--patterns' in options:  # line 736
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 737
        if out:  # line 738
            printo(out)  # line 738
        return  # line 739
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 740
    printo("DIR %s" % relPath)  # line 741
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 742
        ignore = None  # type: _coconut.typing.Optional[str]  # line 743
        for ig in m.c.ignores:  # line 744
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 745
                ignore = ig  # remember first match  # line 745
                break  # remember first match  # line 745
        if ig:  # line 746
            for wl in m.c.ignoresWhitelist:  # line 747
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 748
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 748
                    break  # found a white list entry for ignored file, undo ignoring it  # line 748
        matches = []  # type: List[str]  # line 749
        if not ignore:  # line 750
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 751
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 752
                    matches.append(os.path.basename(pattern))  # line 752
        matches.sort(key=lambda element: len(element))  # line 753
        printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "\u00b7\u00b7\u00b7"), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 754

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 756
    ''' List previous commits on current branch. '''  # line 757
    m = Metadata()  # type: Metadata  # line 758
    m.loadBranch(m.branch)  # knows commit history  # line 759
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 760
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 761
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, max(m.commits))  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 762
    maxWidth = max([wcswidth((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) for commit in m.commits.values()])  # type: int  # line 763
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 764
    for no in range(max(m.commits) + 1):  # line 765
        commit = m.commits[no]  # type: CommitInfo  # line 766
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 767
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # side-effect: updates m.paths  # line 768
        _add = news - olds  # type: FrozenSet[str]  # line 769
        _del = olds - news  # type: FrozenSet[str]  # line 770
        _mod = frozenset([_ for _, info in nxts.items() if _ in m.paths and m.paths[_].size != info.size and (m.paths[_].hash != info.hash if m.strict else m.paths[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 771
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 772
        printo("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT) |%s|%s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)).ljust(maxWidth), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 773
        if '--changes' in options:  # line 774
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}))  # line 774
        if '--diff' in options:  # TODO needs to extract code from diff first to be reused here  # line 775
            pass  # TODO needs to extract code from diff first to be reused here  # line 775
        olds = news  # line 776

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 778
    ''' Exported entire repository as archive for easy transfer. '''  # line 779
    info(MARKER + "Dumping repository to archive...")  # line 780
    force = '--force' in options  # type: bool  # line 781
    progress = '--progress' in options  # type: bool  # line 782
    import zipfile  # TODO display compression ratio (if any)  # line 783
    try:  # line 784
        import zlib  # line 784
        compression = zipfile.ZIP_DEFLATED  # line 784
    except:  # line 785
        compression = zipfile.ZIP_STORED  # line 785

    if argument is None:  # line 787
        Exit("Argument missing (target filename)")  # line 787
    argument = argument if "." in argument else argument + ".sos.zip"  # line 788
    if os.path.exists(encode(argument)) and not force:  # line 789
        Exit("Target archive already exists. Use 'sos dump <arget> --force' to override")  # line 789
    with zipfile.ZipFile(argument, "w", compression) as fd:  # line 790
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 791
        counter = Counter(-1)  # type: Counter  # line 792
        timer = time.time()  # type: float  # line 792
        totalsize = 0  # type: int  # line 793
        start_time = time.time()  # type: float  # line 794
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 795
            dirpath = decode(dirpath)  # line 796
            dirnames[:] = [decode(d) for d in dirnames]  # line 797
            filenames[:] = [decode(f) for f in filenames]  # line 798
            for filename in filenames:  # line 799
                newtime = time.time()  # type: float  # TODO alternatively count bytes and use a threshold there  # line 800
                abspath = os.path.join(dirpath, filename)  # type: str  # line 801
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 802
                totalsize += os.stat(encode(abspath)).st_size  # line 803
                if progress and newtime - timer > .1:  # line 804
                    printo(("\rDumping %s@%6.2f MiB/s %s" % (PROGRESS_MARKER[int(counter.inc() % 4)], totalsize / (MEBI * (time.time() - start_time)), filename)).ljust(termWidth), nl="")  # line 804
                    timer = newtime  # line 804
                fd.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 805
    printo("\r" + (MARKER + "Finished dumping entire repository.").ljust(termWidth), nl="")  # clean line  # line 806

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 808
    command, key, value = (arguments + [None] * 2)[:3]  # line 809
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 810
        Exit("Unknown config command")  # line 810
    local = "--local" in options  # type: bool  # line 811
    m = Metadata()  # type: Metadata  # loads layered configuration as well. TODO warning if repo not exists  # line 812
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 813
    if command == "set":  # line 814
        if None in (key, value):  # line 815
            Exit("Key or value not specified")  # line 815
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 816
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 816
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 817
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 817
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 818
    elif command == "unset":  # line 819
        if key is None:  # line 820
            Exit("No key specified")  # line 820
        if key not in c.keys():  # line 821
            Exit("Unknown key")  # line 821
        del c[key]  # line 822
    elif command == "add":  # line 823
        if None in (key, value):  # line 824
            Exit("Key or value not specified")  # line 824
        if key not in CONFIGURABLE_LISTS:  # line 825
            Exit("Unsupported key %r" % key)  # line 825
        if key not in c.keys():  # add list  # line 826
            c[key] = [value]  # add list  # line 826
        elif value in c[key]:  # line 827
            Exit("Value already contained, nothing to do")  # line 827
        if ";" in value:  # line 828
            c[key].append(removePath(key, value))  # line 828
        else:  # line 829
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 829
    elif command == "rm":  # line 830
        if None in (key, value):  # line 831
            Exit("Key or value not specified")  # line 831
        if key not in c.keys():  # line 832
            Exit("Unknown key %r" % key)  # line 832
        if value not in c[key]:  # line 833
            Exit("Unknown value %r" % value)  # line 833
        c[key].remove(value)  # line 834
    else:  # Show or list  # line 835
        if key == "flags":  # list valid configuration items  # line 836
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 836
        elif key == "lists":  # line 837
            printo(", ".join(CONFIGURABLE_LISTS))  # line 837
        elif key == "texts":  # line 838
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 838
        else:  # line 839
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 840
            c = m.c  # always use full configuration chain  # line 841
            try:  # attempt single key  # line 842
                assert key is not None  # line 843
                c[key]  # line 843
                l = key in c.keys()  # type: bool  # line 844
                g = key in c.__defaults.keys()  # type: bool  # line 844
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 845
            except:  # normal value listing  # line 846
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 847
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 848
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 849
                for k, vt in sorted(vals.items()):  # line 850
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 850
                if len(c.keys()) == 0:  # line 851
                    info("No local configuration stored")  # line 851
                if len(c.__defaults.keys()) == 0:  # line 852
                    info("No global configuration stored")  # line 852
        return  # in case of list, no need to store anything  # line 853
    if local:  # saves changes of repoConfig  # line 854
        m.repoConf = c.__map  # saves changes of repoConfig  # line 854
        m.saveBranches()  # saves changes of repoConfig  # line 854
        Exit("OK", code=0)  # saves changes of repoConfig  # line 854
    else:  # global config  # line 855
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 856
        if f is None:  # line 857
            error("Error saving user configuration: %r" % h)  # line 857
        else:  # line 858
            Exit("OK", code=0)  # line 858

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[], negative: 'bool'=False):  # line 860
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique.
      for "mvnot" don't do any renaming (or do?)
  '''  # line 863
# TODO info(MARKER + TODO write tests for that
    force = '--force' in options  # type: bool  # line 865
    soft = '--soft' in options  # type: bool  # line 866
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 867
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 867
    m = Metadata()  # type: Metadata  # line 868
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 869
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 870
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 871
    if not matching and not force:  # line 872
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 872
    if not (m.track or m.picky):  # line 873
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 873
    if pattern not in patterns:  # list potential alternatives and exit  # line 874
        for tracked in (t for t in patterns if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 875
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 876
            if alternative:  # line 877
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 877
        if not (force or soft):  # line 878
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 878
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 879
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 880
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 881
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 885
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 886
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 886
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 887
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 888
    if len({st[1] for st in matches}) != len(matches):  # line 889
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 889
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 890
    if os.path.exists(encode(newRelPath)):  # line 891
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 892
        if exists and not (force or soft):  # line 893
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 893
    else:  # line 894
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 894
    if not soft:  # perform actual renaming  # line 895
        for (source, target) in matches:  # line 896
            try:  # line 897
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 897
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 898
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 898
    patterns[patterns.index(pattern)] = newPattern  # line 899
    m.saveBranches()  # line 900

def parse(root: 'str', cwd: 'str'):  # line 902
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm. '''  # line 903
    debug("Parsing command-line arguments...")  # line 904
    try:  # line 905
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 906
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: Union[List[str], str, None]  # line 907
        if len(arguments) == 0:  # line 908
            arguments = [None]  # line 908
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 909
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 910
        debug("Processing command %r with arguments %r and options %r." % (("" if command is None else command), arguments if arguments else "", options))  # line 911
        if command[:1] in "amr":  # line 912
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 912
        if command[:1] == "m" or command[:3] == "con":  # line 913
            if len(arguments) < 2:  # line 914
                Exit("Need a second file pattern argument as target for move/rename command")  # line 914
            newRelPath, newPattern = relativize(root, os.path.join(cwd, options[0]))  # line 915
        if command[:1] == "a":  # also addnot  # line 916
            add(relPath, pattern, options, negative="n" in command)  # also addnot  # line 916
        elif command[:1] == "b":  # line 917
            branch(arguments[0], options)  # line 917
        elif command[:2] == "ch":  # line 918
            changes(arguments[0], options, onlys, excps)  # line 918
        elif command[:3] == "com":  # line 919
            commit(arguments[0], options, onlys, excps)  # line 919
        elif command[:2] == "ci":  # line 920
            commit(arguments[0], options, onlys, excps)  # line 920
        elif command[:3] == 'con':  # line 921
            config(arguments, options)  # line 921
        elif command[:2] == "de":  # line 922
            delete(arguments[0], options)  # line 922
        elif command[:2] == "di":  # line 923
            diff(arguments[0], options, onlys, excps)  # line 923
        elif command[:2] == "du":  # line 924
            dump(arguments[0], options)  # line 924
        elif command[:1] == "h":  # line 925
            usage(APPNAME, version.__version__)  # line 925
        elif command[:2] == "lo":  # line 926
            log(options)  # line 926
        elif command[:2] == "li":  # line 927
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 927
        elif command[:2] == "ls":  # TODO avoid and/or normalize root super paths (..)?  # line 928
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # TODO avoid and/or normalize root super paths (..)?  # line 928
        elif command[:1] == "m":  # also mvnot  # line 929
            move(relPath, pattern, newRelPath, newPattern, options[1:], negative="n" in command)  # also mvnot  # line 929
        elif command[:2] == "of":  # line 930
            offline(arguments[0], options)  # line 930
        elif command[:2] == "on":  # line 931
            online(options)  # line 931
        elif command[:1] == "r":  # also rmnot  # line 932
            remove(relPath, pattern, negative="n" in command)  # also rmnot  # line 932
        elif command[:2] == "st":  # line 933
            status(options, onlys, excps)  # line 933
        elif command[:2] == "sw":  # line 934
            switch(arguments[0], options, onlys, excps)  # line 934
        elif command[:1] == "u":  # line 935
            update(arguments[0], options, onlys, excps)  # line 935
        elif command[:1] == "v":  # line 936
            usage(APPNAME, version.__version__, short=True)  # line 936
        else:  # line 937
            Exit("Unknown command '%s'" % command)  # line 937
        Exit(code=0)  # line 938
    except (Exception, RuntimeError) as E:  # line 939
        exception(E)  # line 940
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing.")  # line 941

def main():  # line 943
    global debug, info, warn, error  # line 944
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 945
    _log = Logger(logging.getLogger(__name__))  # line 946
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 946
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 947
        sys.argv.remove(option)  # clean up program arguments  # line 947
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 948
        usage()  # line 948
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 949
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 950
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 951
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 952
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in ["h", "v"]:  # in offline mode or just going offline TODO what about git config?  # line 953
        cwd = os.getcwd()  # line 954
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 955
        parse(root, cwd)  # line 956
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 957
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 958
        import subprocess  # only required in this section  # line 959
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 960
        inp = ""  # type: str  # line 961
        while True:  # line 962
            so, se = process.communicate(input=inp)  # line 963
            if process.returncode is not None:  # line 964
                break  # line 964
            inp = sys.stdin.read()  # line 965
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 966
            if root is None:  # line 967
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 967
            m = Metadata(root)  # type: Metadata  # line 968
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 969
            m.saveBranches()  # line 970
    else:  # line 971
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 971


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 975
level = logging.DEBUG if verbose else logging.INFO  # line 976
force_sos = '--sos' in sys.argv  # type: bool  # line 977
force_vcs = '--vcs' in sys.argv  # type: bool  # line 978
_log = Logger(logging.getLogger(__name__))  # line 979
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 979
if __name__ == '__main__':  # line 980
    main()  # line 980
