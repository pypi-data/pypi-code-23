#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x9f0f1d2a

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
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # line 91
        with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "w", encoding=UTF8) as fd:  # line 92
            store = {"version": _.version, "tags": _.tags, "branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}  # type: Dict[str, Any]  # line 93
            store.update(also)  # allows overriding certain values at certain points in time  # line 94
            json.dump((store, list(_.branches.values()), _.repoConf), fd, ensure_ascii=False)  # stores using unicode codepoints, fd knows how to encode them  # line 95

    def getRevisionByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 97
        ''' Convenience accessor for named revisions (using commit message as name as a convention). '''  # line 98
        if name == "":  # line 99
            return -1  # line 99
        try:  # attempt to parse integer string  # line 100
            return int(name)  # attempt to parse integer string  # line 100
        except ValueError:  # line 101
            pass  # line 101
        found = [number for number, commit in _.commits.items() if name == commit.message]  # find any revision by commit message (usually used for tags)  # HINT allows finding any message, not only tagged ones  # line 102
        return found[0] if found else None  # line 103

    def getBranchByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 105
        ''' Convenience accessor for named branches. '''  # line 106
        if name == "":  # current  # line 107
            return _.branch  # current  # line 107
        try:  # attempt to parse integer string  # line 108
            return int(name)  # attempt to parse integer string  # line 108
        except ValueError:  # line 109
            pass  # line 109
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 110
        return found[0] if found else None  # line 111

    def loadBranch(_, branch: 'int'):  # line 113
        ''' Load all commit information from a branch meta data file. '''  # line 114
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "r", encoding=UTF8) as fd:  # line 115
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 116
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 117
        _.branch = branch  # line 118

    def saveBranch(_, branch: 'int'):  # line 120
        ''' Save all commit information to a branch meta data file. '''  # line 121
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # line 122
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "w", encoding=UTF8) as fd:  # line 123
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 124

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'):  # line 126
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 131
        debug("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 132
        tracked = [t for t in _.branches[_.branch].tracked]  # type: List[str]  # copy  # line 133
        untracked = [u for u in _.branches[_.branch].untracked]  # type: List[str]  # line 134
        os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 135
        _.loadBranch(_.branch)  # line 136
        revision = max(_.commits)  # type: int  # line 137
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 138
        for path, pinfo in _.paths.items():  # line 139
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 140
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 141
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 142
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 143
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].inSync, tracked, untracked)  # save branch info, before storing repo state at caller  # line 144

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 146
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 151
        simpleMode = not (_.track or _.picky)  # line 152
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # in case of initial branch creation  # line 153
        untracked = [t for t in _.branches[_.branch].untracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # line 154
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 155
        _.paths = {}  # type: Dict[str, PathInfo]  # line 156
        if simpleMode:  # branches from file system state  # line 157
            changes = _.findChanges(branch, 0, progress=simpleMode)  # type: ChangeSet  # creates revision folder and versioned files  # line 158
            _.listChanges(changes)  # line 159
            _.paths.update(changes.additions.items())  # line 160
        else:  # tracking or picky mode: branch from latest revision  # line 161
            os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 162
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 163
                _.loadBranch(_.branch)  # line 164
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 165
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 166
                for path, pinfo in _.paths.items():  # line 167
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 168
        ts = int(time.time() * 1000)  # line 169
        _.commits = {0: CommitInfo(0, ts, ("Branched on %s" % strftime(ts) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 170
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 171
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 172
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked, untracked)  # save branch info, in case it is needed  # line 173

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 175
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 176
        shutil.rmtree(encode(os.path.join(_.root, metaFolder, "b%d" % branch)))  # TODO put into recycle bin, under ./sos?  # line 177
        binfo = _.branches[branch]  # line 178
        del _.branches[branch]  # line 179
        _.branch = max(_.branches)  # line 180
        _.saveBranches()  # line 181
        _.commits.clear()  # line 182
        return binfo  # line 183

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 185
        ''' Load all file information from a commit meta data. '''  # line 186
        with codecs.open(encode(branchFolder(branch, revision, base=_.root, file=metaFile)), "r", encoding=UTF8) as fd:  # line 187
            _.paths = json.load(fd)  # line 188
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 189
        _.branch = branch  # line 190

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 192
        ''' Save all file information to a commit meta data file. '''  # line 193
        target = branchFolder(branch, revision, base=_.root)  # type: str  # line 194
        try:  # line 195
            os.makedirs(encode(target))  # line 195
        except:  # line 196
            pass  # line 196
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(target, metaFile)), encode(os.path.join(target, metaBack))))  # line 197
        with codecs.open(encode(os.path.join(target, metaFile)), "w", encoding=UTF8) as fd:  # line 198
            json.dump(_.paths, fd, ensure_ascii=False)  # line 199

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'ChangeSet':  # line 201
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        The function returns the state of file tree *differences*, unless "inverse" is True -> then return original data
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes (always overrides considerOnly)
        progress: Show file names during processing
    '''  # line 210
        write = branch is not None and revision is not None  # line 211
        if write:  # line 212
            try:  # line 213
                os.makedirs(encode(branchFolder(branch, revision, base=_.root)))  # line 213
            except FileExistsError:  # HINT "try" only necessary for testing hash collision code  # line 214
                pass  # HINT "try" only necessary for testing hash collision code  # line 214
        changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 215
        indicator = ProgressIndicator() if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # optional file list progress indicator  # line 216
        hashed = None  # type: _coconut.typing.Optional[str]  # line 217
        written = None  # type: int  # line 217
        compressed = 0  # type: int  # line 217
        original = 0  # type: int  # line 217
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 218
        for path, pinfo in _.paths.items():  # line 219
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 220
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 223
        for path, dirnames, filenames in os.walk(_.root):  # line 224
            path = decode(path)  # line 225
            dirnames[:] = [decode(d) for d in dirnames]  # line 226
            filenames[:] = [decode(f) for f in filenames]  # line 227
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 228
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 229
            dirnames.sort()  # line 230
            filenames.sort()  # line 230
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 231
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 232
            if dontConsider:  # line 233
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 234
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 235
                filename = relPath + SLASH + file  # line 236
                filepath = os.path.join(path, file)  # line 237
                try:  # line 238
                    stat = os.stat(encode(filepath))  # line 238
                except Exception as E:  # line 239
                    exception(E)  # line 239
                    continue  # line 239
                size, mtime = stat.st_size, int(stat.st_mtime * 1000)  # line 240
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 241
                if show:  # indication character returned  # line 242
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", show, filename)  # line 243
                    printo(outstring + " " * max(0, termWidth - len(outstring)), nl="")  # line 244
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 245
                    nameHash = hashStr(filename)  # line 246
                    try:  # line 247
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 248
                        changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 249
                        compressed += written  # line 250
                        original += size  # line 250
                    except Exception as E:  # line 251
                        exception(E)  # line 251
                    continue  # with next file  # line 252
                last = _.paths[filename]  # filename is known - check for modifications  # line 253
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 254
                    try:  # line 255
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 256
                        changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 257
                        continue  # line 257
                    except Exception as E:  # line 258
                        exception(E)  # line 258
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and tryOrDefault(lambda: (hashFile(filepath, _.compress)[0] != last.hash), default=False)):  # detected a modification TODO wrap hashFile exception  # line 259
                    try:  # line 260
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 261
                        changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 262
                    except Exception as E:  # line 263
                        exception(E)  # line 263
                else:  # with next file  # line 264
                    continue  # with next file  # line 264
                compressed += written  # line 265
                original += last.size if inverse else size  # line 265
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 266
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 266
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 267
            for file in names:  # line 268
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 269
                    continue  # don't mark ignored files as deleted  # line 269
                pth = path + SLASH + file  # type: str  # line 270
                changes.deletions[pth] = _.paths[pth]  # line 271
        if progress:  # forces new line  # line 272
            printo("\rChecking finished.%s" % ((" Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else "").ljust(termWidth))  # forces new line  # line 272
        else:  # line 273
            debug("Finished detecting changes.%s" % ((" Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else ""))  # line 273
        return changes  # line 274

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 276
        ''' Returns nothing, just updates _.paths in place. '''  # line 277
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 278

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 280
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 281
        _.loadCommit(branch, 0)  # load initial paths  # line 282
        if incrementally:  # line 283
            yield _.paths  # line 283
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 284
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 284
        for rev in range(1, revision + 1):  # line 285
            m.loadCommit(branch, rev)  # line 286
            for p, info in m.paths.items():  # line 287
                if info.size == None:  # line 288
                    del _.paths[p]  # line 288
                else:  # line 289
                    _.paths[p] = info  # line 289
            if incrementally:  # line 290
                yield _.paths  # line 290
        yield None  # for the default case - not incrementally  # line 291

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 293
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 296
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 297
            return (_.branch, -1)  # no branch/revision specified  # line 297
        argument = argument.strip()  # line 298
        if argument.startswith(SLASH):  # current branch  # line 299
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 299
        if argument.endswith(SLASH):  # line 300
            try:  # line 301
                return (_.getBranchByName(argument[:-1]), -1)  # line 301
            except ValueError:  # line 302
                Exit("Unknown branch label '%s'" % argument)  # line 302
        if SLASH in argument:  # line 303
            b, r = argument.split(SLASH)[:2]  # line 304
            try:  # line 305
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 305
            except ValueError:  # line 306
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 306
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 307
        if branch not in _.branches:  # line 308
            branch = None  # line 308
        try:  # either branch name/number or reverse/absolute revision number  # line 309
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 309
        except:  # line 310
            Exit("Unknown branch label or wrong number format")  # line 310
        Exit("This should never happen. Please create a issue report")  # line 311
        return (None, None)  # line 311

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 313
        while True:  # find latest revision that contained the file physically  # line 314
            source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 315
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 316
                break  # line 316
            revision -= 1  # line 317
            if revision < 0:  # line 318
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 318
        return revision, source  # line 319

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 321
        ''' Copy versioned file to other branch/revision. '''  # line 322
        target = branchFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 323
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 324
        shutil.copy2(encode(source), encode(target))  # line 325

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 327
        ''' Return file contents, or copy contents into file path provided. '''  # line 328
        source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 329
        try:  # line 330
            with openIt(source, "r", _.compress) as fd:  # line 331
                if toFile is None:  # read bytes into memory and return  # line 332
                    return fd.read()  # read bytes into memory and return  # line 332
                with open(encode(toFile), "wb") as to:  # line 333
                    while True:  # line 334
                        buffer = fd.read(bufSize)  # line 335
                        to.write(buffer)  # line 336
                        if len(buffer) < bufSize:  # line 337
                            break  # line 337
                    return None  # line 338
        except Exception as E:  # line 339
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 339
        return None  # line 340

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 342
        ''' Recreate file for given revision, or return binary contents if path is None. '''  # line 343
        if relPath is None:  # just return contents  # line 344
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 344
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 345
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 346
            try:  # line 347
                os.makedirs(encode(os.path.dirname(target)))  # line 347
            except:  # line 348
                pass  # line 348
        if pinfo.size == 0:  # line 349
            with open(encode(target), "wb"):  # line 350
                pass  # line 350
            try:  # update access/modification timestamps on file system  # line 351
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 351
            except Exception as E:  # line 352
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 352
            return None  # line 353
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 354
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 356
            while True:  # line 357
                buffer = fd.read(bufSize)  # line 358
                to.write(buffer)  # line 359
                if len(buffer) < bufSize:  # line 360
                    break  # line 360
        try:  # update access/modification timestamps on file system  # line 361
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 361
        except Exception as E:  # line 362
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 362
        return None  # line 363

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None, negative: 'bool'=False) -> 'FrozenSet[str]':  # line 365
        ''' Returns list of tracking patterns (or untracking patterns if negative) for provided branch or current branch. '''  # line 366
        return _coconut.frozenset() if not (_.track or _.picky) else frozenset(_.branches[(_.branch if branch is None else branch)].untracked if negative else _.branches[(_.branch if branch is None else branch)].tracked)  # line 367


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 371
    ''' Initial command to start working offline. '''  # line 372
    if os.path.exists(encode(metaFolder)):  # line 373
        if '--force' not in options:  # line 374
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 374
        try:  # line 375
            for entry in os.listdir(metaFolder):  # line 376
                resource = metaFolder + os.sep + entry  # line 377
                if os.path.isdir(resource):  # line 378
                    shutil.rmtree(encode(resource))  # line 378
                else:  # line 379
                    os.unlink(encode(resource))  # line 379
        except:  # line 380
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 380
    m = Metadata(offline=True)  # type: Metadata  # line 381
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 382
        m.compress = True  # plain file copies instead of compressed ones  # line 382
    if '--picky' in options or m.c.picky:  # Git-like  # line 383
        m.picky = True  # Git-like  # line 383
    elif '--track' in options or m.c.track:  # Svn-like  # line 384
        m.track = True  # Svn-like  # line 384
    if '--strict' in options or m.c.strict:  # always hash contents  # line 385
        m.strict = True  # always hash contents  # line 385
    debug(MARKER + "Going offline...")  # line 386
    m.createBranch(0, (defaults["defaultbranch"] if argument is None else argument), initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 387
    m.branch = 0  # line 388
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 389
    info(MARKER + "Offline repository prepared. Use 'sos online' to finish offline work")  # line 390

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 392
    ''' Finish working offline. '''  # line 393
    debug(MARKER + "Going back online...")  # line 394
    force = '--force' in options  # type: bool  # line 395
    m = Metadata()  # type: Metadata  # line 396
    m.loadBranches()  # line 397
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 398
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 398
    strict = '--strict' in options or m.strict  # type: bool  # line 399
    if options.count("--force") < 2:  # line 400
        changes = m.findChanges(checkContent=strict, considerOnly=None if not (m.track or m.picky) else m.getTrackingPatterns(), dontConsider=None if not (m.track or m.picky) else m.getTrackingPatterns(negative=True), progress='--progress' in options)  # type: ChangeSet  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 401
        if modified(changes):  # line 402
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 406
    try:  # line 407
        shutil.rmtree(encode(metaFolder))  # line 407
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 407
    except Exception as E:  # line 408
        Exit("Error removing offline repository: %r" % E)  # line 408
    info(MARKER + "Offline repository removed, you're back online")  # line 409

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 411
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 412
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 413
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 414
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 415
    m = Metadata()  # type: Metadata  # line 416
    m.loadBranch(m.branch)  # line 417
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 418
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 418
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 419
    debug(MARKER + "Branching to %sbranch b%02d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 420
    if last:  # branch from branch's last revision  # line 421
        m.duplicateBranch(branch, (("" if argument is None else argument)) + " (Branched from r%02d/b%02d)" % (m.branch, max(m.commits.keys())))  # branch from branch's last revision  # line 421
    else:  #  branch from current file tree state  # line 422
        m.createBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  #  branch from current file tree state  # line 422
    if not stay:  # line 423
        m.branch = branch  # line 424
        m.saveBranches()  # line 425
    info(MARKER + "%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 426

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 428
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 429
    if '--repo' in options:  # line 430
        status(options, onlys, excps)  # line 430
        return  # line 430
    m = Metadata()  # type: Metadata  # line 431
    branch = None  # type: _coconut.typing.Optional[int]  # line 431
    revision = None  # type: _coconut.typing.Optional[int]  # line 431
    strict = '--strict' in options or m.strict  # type: bool  # line 432
    branch, revision = m.parseRevisionString(argument)  # line 433
    if branch not in m.branches:  # line 434
        Exit("Unknown branch")  # line 434
    m.loadBranch(branch)  # knows commits  # line 435
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 436
    if revision < 0 or revision > max(m.commits):  # line 437
        Exit("Unknown revision r%02d" % revision)  # line 437
    debug(MARKER + "Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 438
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 439
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # type: ChangeSet  # line 440
    m.listChanges(changes)  # line 445
    return changes  # for unit tests only TODO remove  # line 446

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 448
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 449
    m = Metadata()  # type: Metadata  # line 450
    branch = None  # type: _coconut.typing.Optional[int]  # line 450
    revision = None  # type: _coconut.typing.Optional[int]  # line 450
    strict = '--strict' in options or m.strict  # type: bool  # line 451
    _from = {None: option.split("--from=")[1] for option in options if option.startswith("--from=")}.get(None, None)  # type: _coconut.typing.Optional[str]  # TODO implement  # line 452
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 453
    if branch not in m.branches:  # line 454
        Exit("Unknown branch")  # line 454
    m.loadBranch(branch)  # knows commits  # line 455
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 456
    if revision < 0 or revision > max(m.commits):  # line 457
        Exit("Unknown revision r%02d" % revision)  # line 457
    debug(MARKER + "Textual differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 458
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 459
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # type: ChangeSet  # line 460
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 465
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 466

    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 468
        content = None  # type: _coconut.typing.Optional[bytes]  # line 469
        if pinfo.size == 0:  # empty file contents  # line 470
            content = b""  # empty file contents  # line 470
        else:  # versioned file  # line 471
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 471
            assert content is not None  # versioned file  # line 471
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 472
        blocks = None  # type: List[MergeBlock]  # line 473
        nl = None  # type: bytes  # line 473
        blocks, nl = merge(filename=abspath, into=content, diffOnly=True)  # only determine change blocks  # line 474
        printo("DIF %s%s %s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else "", NL_NAMES[nl]))  # line 475
        for block in blocks:  # line 476
            if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:  # line 477
                pass  # TODO print some previous and following lines - which aren't accessible here anymore  # line 478
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 479
                for no, line in enumerate(block.lines):  # line 480
                    printo("+++ %04d |%s|" % (no + block.line, line))  # line 481
            elif block.tipe == MergeBlockType.REMOVE:  # line 482
                for no, line in enumerate(block.lines):  # line 483
                    printo("--- %04d |%s|" % (no + block.line, line))  # line 484
            elif block.tipe == MergeBlockType.REPLACE:  # TODO for MODIFY also show intra-line change ranges (TODO remove if that code was also removed)  # line 485
                for no, line in enumerate(block.replaces.lines):  # line 486
                    printo("- | %04d |%s|" % (no + block.replaces.line, line))  # line 487
                for no, line in enumerate(block.lines):  # line 488
                    printo("+ | %04d |%s|" % (no + block.line, line))  # line 489
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 493
    ''' Create new revision from file tree changes vs. last commit. '''  # line 494
    m = Metadata()  # type: Metadata  # line 495
    if argument is not None and argument in m.tags:  # line 496
        Exit("Illegal commit message. It was already used as a tag name")  # line 496
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 497
# No untracking patterns needed here
    if m.picky and not trackingPatterns:  # line 499
        Exit("No file patterns staged for commit in picky mode")  # line 499
    changes = None  # type: ChangeSet  # line 500
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but aborts if no changes  # line 501
    debug((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 502
    m.paths = changes.additions  # line 503
    m.paths.update(changes.modifications)  # update pathset to changeset only  # line 504
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changes.deletions.items()})  # line 505
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 506
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 507
    m.saveBranch(m.branch)  # line 508
    m.loadBranches()  # TODO is it necessary to load again?  # line 509
    if m.picky:  # remove tracked patterns  # line 510
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 510
    else:  # track or simple mode: set branch dirty  # line 511
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 511
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 512
        m.tags.append(argument)  # memorize unique tag  # line 512
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 512
    m.saveBranches()  # line 513
    info(MARKER + "Created new revision r%02d%s (+%02d/-%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications)))  # TODO show compression factor  # line 514

def status(options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 516
    ''' Show branches and current repository state. '''  # line 517
    m = Metadata()  # type: Metadata  # line 518
    current = m.branch  # type: int  # line 519
    strict = '--strict' in options or m.strict  # type: bool  # line 520
    info(MARKER + "Offline repository status")  # line 521
    info("Installation path:   %s" % os.path.abspath(os.path.dirname(__file__)))  # line 522
    info("Current SOS version: %s" % version.__version__)  # line 523
    info("At creation version: %s" % m.version)  # line 524
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 525
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 526
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 527
    info("Number of branches:  %d" % len(m.branches))  # line 528
#  info("Revisions:           %d" % sum([]))
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 530
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 531
    m.loadBranch(m.branch)  # line 532
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 508  # line 533
    changes = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress=True)  # type: ChangeSet  # line 534
    printo("File tree %s" % ("has changes vs. last revision of current branch" if modified(changes) else "is unchanged"))  # line 539
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 540
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 541
        m.loadBranch(branch.number)  # knows commit history  # line 542
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 543
    if m.track or m.picky and (len(m.branches[m.branch].tracked) > 0 or len(m.branches[m.branch].untracked) > 0):  # line 544
        info("\nTracked file patterns:")  # TODO print matching untracking patterns side-by-side  # line 545
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 546
        info("\nUntracked file patterns:")  # line 547
        printo(ajoin("  | ", m.branches[m.branch].untracked, "\n"))  # line 548

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str], FrozenSet[str]]':  # line 550
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags.
  '''  # line 556
    m = Metadata()  # type: Metadata  # line 557
    force = '--force' in options  # type: bool  # line 558
    strict = '--strict' in options or m.strict  # type: bool  # line 559
    if argument is not None:  # line 560
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 561
        if branch is None:  # line 562
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 562
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 563

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 566
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 567
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 568
    changes = m.findChanges(m.branch if commit else None, max(m.commits) + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress='--progress' in options)  # type: ChangeSet  # line 569
    if check and modified(changes) and not force:  # line 574
        m.listChanges(changes)  # line 575
        if not commit:  # line 576
            Exit("File tree contains changes. Use --force to proceed")  # line 576
    elif commit and not force:  #  and not check  # line 577
        Exit("Nothing to commit")  #  and not check  # line 577

    if argument is not None:  # branch/revision specified  # line 579
        m.loadBranch(branch)  # knows commits of target branch  # line 580
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 581
        if revision < 0 or revision > max(m.commits):  # line 582
            Exit("Unknown revision r%02d" % revision)  # line 582
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch), m.getTrackingPatterns(branch, negative=True))  # line 583
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns, untrackingPatterns)  # line 584

def switch(argument: 'str', options: 'List[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 586
    ''' Continue work on another branch, replacing file tree changes. '''  # line 587
    m, branch, revision, changes, strict, _force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, ["--force"] + options)  # line 588
    force = '--force' in options  # type: bool  # needed as we fake force in above access  # line 589

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 592
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked, untracked=m.branches[branch].untracked)  # line 593
    else:  # full file switch  # line 594
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 595
        todos = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((untrackingPatterns | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # type: ChangeSet  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 596

# Now check for potential conflicts
        changes.deletions.clear()  # local deletions never create conflicts, modifications always  # line 603
        rms = []  # type: _coconut.typing.Sequence[str]  # local additions can be ignored if restoration from switch would be same  # line 604
        for a, pinfo in changes.additions.items():  # has potential corresponding re-add in switch operation:  # line 605
            if a in todos.deletions and pinfo.size == todos.deletions[a].size and (pinfo.hash == todos.deletions[a].hash if m.strict else pinfo.mtime == todos.deletions[a].mtime):  # line 606
                rms.append(a)  # line 606
        for rm in rms:  # TODO could also silently accept remote DEL for local ADD  # line 607
            del changes.additions[rm]  # TODO could also silently accept remote DEL for local ADD  # line 607
        if modified(changes) and not force:  # line 608
            m.listChanges(changes)  # line 608
            Exit("File tree contains changes. Use --force to proceed")  # line 608
        debug(MARKER + "Switching to branch %sb%02d/r%02d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 609
        if not modified(todos):  # line 610
            info("No changes to current file tree")  # line 611
        else:  # integration required  # line 612
            for path, pinfo in todos.deletions.items():  # line 613
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 614
                printo("ADD " + path)  # line 615
            for path, pinfo in todos.additions.items():  # line 616
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 617
                printo("DEL " + path)  # line 618
            for path, pinfo in todos.modifications.items():  # line 619
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 620
                printo("MOD " + path)  # line 621
    m.branch = branch  # line 622
    m.saveBranches()  # store switched path info  # line 623
    info(MARKER + "Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 624

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 626
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 630
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 631
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 632
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 633
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 634
    m = Metadata()  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 635
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 636
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 637
    debug(MARKER + "Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 638

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 641
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 642
    untrackingUnion = untrackingPatterns | m.getTrackingPatterns(branch, negative=True)  # type: FrozenSet[str]  # line 643
    changes = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingUnion), dontConsider=excps if not (m.track or m.picky) else (untrackingUnion if onlys is None else onlys), progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 644
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 649
        if trackingUnion != trackingPatterns:  # nothing added  # line 650
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 651
        else:  # line 652
            info("Nothing to update")  # but write back updated branch info below  # line 653
    else:  # integration required  # line 654
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 655
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 656
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 656
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 657
        for path, pinfo in changes.additions.items():  # line 658
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 659
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 659
            if mrg.value & MergeOperation.REMOVE.value:  # line 660
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 660
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 661
        for path, pinfo in changes.modifications.items():  # line 662
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 663
            binary = not m.isTextType(path)  # type: bool  # line 664
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 665
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 666
                printo(("MOD " if not binary else "BIN ") + path)  # line 667
                while True:  # line 668
                    printo(into)  # TODO print mtime, size differences?  # line 669
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 670
                    if op in ("it" if binary else "itm"):  # line 671
                        break  # line 671
            if op == "t":  # line 672
                printo("THR " + path)  # blockwise copy of contents  # line 673
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 673
            elif op == "m":  # line 674
                current = None  # type: bytes  # line 675
                with open(encode(into), "rb") as fd:  # TODO slurps file  # line 676
                    current = fd.read()  # TODO slurps file  # line 676
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 677
                if current == file:  # line 678
                    debug("No difference to versioned file")  # line 678
                elif file is not None:  # if None, error message was already logged  # line 679
                    contents = None  # type: bytes  # line 680
                    nl = None  # type: bytes  # line 680
                    contents, nl = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # line 681
                    if contents != current:  # line 682
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 683
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 683
                    else:  # TODO but update timestamp?  # line 684
                        debug("No change")  # TODO but update timestamp?  # line 684
            else:  # mine or wrong input  # line 685
                printo("MNE " + path)  # nothing to do! same as skip  # line 686
    info(MARKER + "Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 687
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 688
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 689
    m.saveBranches()  # line 690

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 692
    ''' Remove a branch entirely. '''  # line 693
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options)  # line 694
    if len(m.branches) == 1:  # line 695
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 695
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 696
    if branch is None or branch not in m.branches:  # line 697
        Exit("Cannot delete unknown branch %r" % branch)  # line 697
    debug(MARKER + "Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 698
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 699
    info(MARKER + "Branch b%02d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 700

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[], negative: 'bool'=False):  # line 702
    ''' Add a tracked files pattern to current branch's tracked files. negative means tracking blacklisting. '''  # line 703
    force = '--force' in options  # type: bool  # line 704
    m = Metadata()  # type: Metadata  # line 705
    if not (m.track or m.picky):  # line 706
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 706
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 707
    if pattern in patterns:  # line 708
        Exit("Pattern '%s' already tracked" % pattern)  # line 708
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 709
        Exit("The pattern folder doesn't exist. Use --force to add the file pattern anyway")  # line 709
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 710
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 711
    patterns.append(pattern)  # line 712
    m.saveBranches()  # line 713
    info(MARKER + "Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 714

def remove(relPath: 'str', pattern: 'str', negative: 'bool'=False):  # line 716
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 717
    m = Metadata()  # type: Metadata  # line 718
    if not (m.track or m.picky):  # line 719
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 719
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 720
    if pattern not in patterns:  # line 721
        suggestion = _coconut.set()  # type: Set[str]  # line 722
        for pat in patterns:  # line 723
            if fnmatch.fnmatch(pattern, pat):  # line 724
                suggestion.add(pat)  # line 724
        if suggestion:  # TODO use same wording as in move  # line 725
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 725
        Exit("Tracked pattern '%s' not found" % pattern)  # line 726
    patterns.remove(pattern)  # line 727
    m.saveBranches()  # line 728
    info(MARKER + "Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 729

def ls(folder: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 731
    ''' List specified directory, augmenting with repository metadata. '''  # line 732
    folder = (os.getcwd() if folder is None else folder)  # line 733
    m = Metadata()  # type: Metadata  # line 734
    debug(MARKER + "Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 735
    relPath = relativize(m.root, os.path.join(folder, "-"))[0]  # type: str  # line 736
    if relPath.startswith(".."):  # line 737
        Exit("Cannot list contents of folder outside offline repository")  # line 737
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 738
    untrackingPatterns = m.getTrackingPatterns(negative=True) if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 739
    if '--tags' in options:  # line 740
        printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 741
        return  # line 742
    if '--patterns' in options:  # line 743
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 744
        if out:  # line 745
            printo(out)  # line 745
        return  # line 746
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 747
    printo("DIR %s" % relPath)  # line 748
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 749
        ignore = None  # type: _coconut.typing.Optional[str]  # line 750
        for ig in m.c.ignores:  # line 751
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 752
                ignore = ig  # remember first match  # line 752
                break  # remember first match  # line 752
        if ig:  # line 753
            for wl in m.c.ignoresWhitelist:  # line 754
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 755
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 755
                    break  # found a white list entry for ignored file, undo ignoring it  # line 755
        matches = []  # type: List[str]  # line 756
        if not ignore:  # line 757
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 758
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 759
                    matches.append(os.path.basename(pattern))  # line 759
        matches.sort(key=lambda element: len(element))  # line 760
        printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "\u00b7\u00b7\u00b7"), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 761

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 763
    ''' List previous commits on current branch. '''  # line 764
    m = Metadata()  # type: Metadata  # line 765
    m.loadBranch(m.branch)  # knows commit history  # line 766
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 767
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 768
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, max(m.commits))  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 769
    maxWidth = max([wcswidth((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) for commit in m.commits.values()])  # type: int  # line 770
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 771
    for no in range(max(m.commits) + 1):  # line 772
        commit = m.commits[no]  # type: CommitInfo  # line 773
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 774
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # side-effect: updates m.paths  # line 775
        _add = news - olds  # type: FrozenSet[str]  # line 776
        _del = olds - news  # type: FrozenSet[str]  # line 777
        _mod = frozenset([_ for _, info in nxts.items() if _ in m.paths and m.paths[_].size != info.size and (m.paths[_].hash != info.hash if m.strict else m.paths[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 778
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 779
        printo("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT) |%s|%s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)).ljust(maxWidth), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 780
        if '--changes' in options:  # line 781
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}))  # line 781
        if '--diff' in options:  # TODO needs to extract code from diff first to be reused here  # line 782
            pass  # TODO needs to extract code from diff first to be reused here  # line 782
        olds = news  # line 783

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 785
    ''' Exported entire repository as archive for easy transfer. '''  # line 786
    debug(MARKER + "Dumping repository to archive...")  # line 787
    progress = '--progress' in options  # type: bool  # line 788
    import zipfile  # TODO display compression ratio (if any)  # line 789
    try:  # line 790
        import zlib  # line 790
        compression = zipfile.ZIP_DEFLATED  # line 790
    except:  # line 791
        compression = zipfile.ZIP_STORED  # line 791

    if argument is None:  # line 793
        Exit("Argument missing (target filename)")  # line 793
    argument = argument if "." in argument else argument + ".sos.zip"  # line 794
    if os.path.exists(encode(argument)):  # line 795
        try:  # line 796
            shutil.copy2(encode(argument), encode(argument + BACKUP_SUFFIX))  # line 796
        except Exception as E:  # line 797
            Exit("Error creating backup copy before dumping. Please resolve and retry. %r" % E)  # line 797
    with zipfile.ZipFile(argument, "w", compression) as _zip:  # line 798
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 799
        indicator = ProgressIndicator(progress)  # type: ProgressIndicator  # line 800
        totalsize = 0  # type: int  # line 801
        start_time = time.time()  # type: float  # line 802
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 803
            dirpath = decode(dirpath)  # line 804
            dirnames[:] = [decode(d) for d in dirnames]  # line 805
            filenames[:] = [decode(f) for f in filenames]  # line 806
            for filename in filenames:  # line 807
                abspath = os.path.join(dirpath, filename)  # type: str  # line 808
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 809
                totalsize += os.stat(encode(abspath)).st_size  # line 810
                show = indicator.getIndicator()  # type: _coconut.typing.Optional[str]  # line 811
                if show:  # line 812
                    printo(("\rDumping %s @%.2f MiB/s %s" % (show, totalsize / (MEBI * (time.time() - start_time)), filename)).ljust(termWidth), nl="")  # line 812
                _zip.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 813
    info("\r" + (MARKER + "Finished dumping entire repository.").ljust(termWidth))  # clean line  # line 814

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 816
    command, key, value = (arguments + [None] * 2)[:3]  # line 817
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 818
        Exit("Unknown config command")  # line 818
    local = "--local" in options  # type: bool  # line 819
    m = Metadata()  # type: Metadata  # loads layered configuration as well. TODO warning if repo not exists  # line 820
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 821
    if command == "set":  # line 822
        if None in (key, value):  # line 823
            Exit("Key or value not specified")  # line 823
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 824
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 824
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 825
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 825
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 826
    elif command == "unset":  # line 827
        if key is None:  # line 828
            Exit("No key specified")  # line 828
        if key not in c.keys():  # line 829
            Exit("Unknown key")  # line 829
        del c[key]  # line 830
    elif command == "add":  # line 831
        if None in (key, value):  # line 832
            Exit("Key or value not specified")  # line 832
        if key not in CONFIGURABLE_LISTS:  # line 833
            Exit("Unsupported key %r" % key)  # line 833
        if key not in c.keys():  # add list  # line 834
            c[key] = [value]  # add list  # line 834
        elif value in c[key]:  # line 835
            Exit("Value already contained, nothing to do")  # line 835
        if ";" in value:  # line 836
            c[key].append(removePath(key, value))  # line 836
        else:  # line 837
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 837
    elif command == "rm":  # line 838
        if None in (key, value):  # line 839
            Exit("Key or value not specified")  # line 839
        if key not in c.keys():  # line 840
            Exit("Unknown key %r" % key)  # line 840
        if value not in c[key]:  # line 841
            Exit("Unknown value %r" % value)  # line 841
        c[key].remove(value)  # line 842
    else:  # Show or list  # line 843
        if key == "flags":  # list valid configuration items  # line 844
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 844
        elif key == "lists":  # line 845
            printo(", ".join(CONFIGURABLE_LISTS))  # line 845
        elif key == "texts":  # line 846
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 846
        else:  # line 847
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 848
            c = m.c  # always use full configuration chain  # line 849
            try:  # attempt single key  # line 850
                assert key is not None  # line 851
                c[key]  # line 851
                l = key in c.keys()  # type: bool  # line 852
                g = key in c.__defaults.keys()  # type: bool  # line 852
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 853
            except:  # normal value listing  # line 854
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 855
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 856
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 857
                for k, vt in sorted(vals.items()):  # line 858
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 858
                if len(c.keys()) == 0:  # line 859
                    info("No local configuration stored")  # line 859
                if len(c.__defaults.keys()) == 0:  # line 860
                    info("No global configuration stored")  # line 860
        return  # in case of list, no need to store anything  # line 861
    if local:  # saves changes of repoConfig  # line 862
        m.repoConf = c.__map  # saves changes of repoConfig  # line 862
        m.saveBranches()  # saves changes of repoConfig  # line 862
        Exit("OK", code=0)  # saves changes of repoConfig  # line 862
    else:  # global config  # line 863
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 864
        if f is None:  # line 865
            error("Error saving user configuration: %r" % h)  # line 865
        else:  # line 866
            Exit("OK", code=0)  # line 866

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[], negative: 'bool'=False):  # line 868
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique.
      for "mvnot" don't do any renaming (or do?)
  '''  # line 871
# TODO info(MARKER + TODO write tests for that
    force = '--force' in options  # type: bool  # line 873
    soft = '--soft' in options  # type: bool  # line 874
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 875
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 875
    m = Metadata()  # type: Metadata  # line 876
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 877
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 878
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 879
    if not matching and not force:  # line 880
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 880
    if not (m.track or m.picky):  # line 881
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 881
    if pattern not in patterns:  # list potential alternatives and exit  # line 882
        for tracked in (t for t in patterns if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 883
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
    if os.path.exists(encode(newRelPath)):  # line 899
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 900
        if exists and not (force or soft):  # line 901
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 901
    else:  # line 902
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 902
    if not soft:  # perform actual renaming  # line 903
        for (source, target) in matches:  # line 904
            try:  # line 905
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 905
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 906
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 906
    patterns[patterns.index(pattern)] = newPattern  # line 907
    m.saveBranches()  # line 908

def parse(root: 'str', cwd: 'str'):  # line 910
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm. '''  # line 911
    debug("Parsing command-line arguments...")  # line 912
    try:  # line 913
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 914
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: Union[List[str], str, None]  # line 915
        if len(arguments) == 0:  # line 916
            arguments = [None]  # line 916
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 917
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 918
        debug("Processing command %r with arguments %r and options %r." % (("" if command is None else command), arguments if arguments else "", options))  # line 919
        if command[:1] in "amr":  # line 920
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 920
        if command[:1] == "m" or command[:3] == "con":  # line 921
            if len(arguments) < 2:  # line 922
                Exit("Need a second file pattern argument as target for move/rename command")  # line 922
            newRelPath, newPattern = relativize(root, os.path.join(cwd, options[0]))  # line 923
        if command[:1] == "a":  # also addnot  # line 924
            add(relPath, pattern, options, negative="n" in command)  # also addnot  # line 924
        elif command[:1] == "b":  # line 925
            branch(arguments[0], options)  # line 925
        elif command[:3] == "com":  # line 926
            commit(arguments[0], options, onlys, excps)  # line 926
        elif command[:2] == "ch":  # "changes" (legacy)  # line 927
            changes(arguments[0], options, onlys, excps)  # "changes" (legacy)  # line 927
        elif command[:2] == "ci":  # line 928
            commit(arguments[0], options, onlys, excps)  # line 928
        elif command[:3] == 'con':  # line 929
            config(arguments, options)  # line 929
        elif command[:2] == "de":  # line 930
            delete(arguments[0], options)  # line 930
        elif command[:2] == "di":  # line 931
            diff(arguments[0], options, onlys, excps)  # line 931
        elif command[:2] == "du":  # line 932
            dump(arguments[0], options)  # line 932
        elif command[:1] == "h":  # line 933
            usage(APPNAME, version.__version__)  # line 933
        elif command[:2] == "lo":  # line 934
            log(options)  # line 934
        elif command[:2] == "li":  # line 935
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 935
        elif command[:2] == "ls":  # TODO avoid and/or normalize root super paths (..)?  # line 936
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # TODO avoid and/or normalize root super paths (..)?  # line 936
        elif command[:1] == "m":  # also mvnot  # line 937
            move(relPath, pattern, newRelPath, newPattern, options[1:], negative="n" in command)  # also mvnot  # line 937
        elif command[:2] == "of":  # line 938
            offline(arguments[0], options)  # line 938
        elif command[:2] == "on":  # line 939
            online(options)  # line 939
        elif command[:1] == "r":  # also rmnot  # line 940
            remove(relPath, pattern, negative="n" in command)  # also rmnot  # line 940
        elif command[:2] == "st":  # line 941
            changes(arguments[0], options, onlys, excps)  # line 941
        elif command[:2] == "sw":  # line 942
            switch(arguments[0], options, onlys, excps)  # line 942
        elif command[:1] == "u":  # line 943
            update(arguments[0], options, onlys, excps)  # line 943
        elif command[:1] == "v":  # line 944
            usage(APPNAME, version.__version__, short=True)  # line 944
        else:  # line 945
            Exit("Unknown command '%s'" % command)  # line 945
        Exit(code=0)  # line 946
    except (Exception, RuntimeError) as E:  # line 947
        exception(E)  # line 948
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing.")  # line 949

def main():  # line 951
    global debug, info, warn, error  # line 952
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 953
    _log = Logger(logging.getLogger(__name__))  # line 954
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 954
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 955
        sys.argv.remove(option)  # clean up program arguments  # line 955
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 956
        usage(APPNAME, version.__version__)  # line 956
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 957
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 958
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 959
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 960
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in ["h", "v"]:  # in offline mode or just going offline TODO what about git config?  # line 961
        cwd = os.getcwd()  # line 962
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 963
        parse(root, cwd)  # line 964
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 965
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 966
        import subprocess  # only required in this section  # line 967
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 968
        inp = ""  # type: str  # line 969
        while True:  # line 970
            so, se = process.communicate(input=inp)  # line 971
            if process.returncode is not None:  # line 972
                break  # line 972
            inp = sys.stdin.read()  # line 973
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 974
            if root is None:  # line 975
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 975
            m = Metadata(root)  # type: Metadata  # line 976
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 977
            m.saveBranches()  # line 978
    else:  # line 979
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 979


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 983
level = logging.DEBUG if verbose else logging.INFO  # line 984
force_sos = '--sos' in sys.argv  # type: bool  # line 985
force_vcs = '--vcs' in sys.argv  # type: bool  # line 986
_log = Logger(logging.getLogger(__name__))  # line 987
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 987
if __name__ == '__main__':  # line 988
    main()  # line 988
