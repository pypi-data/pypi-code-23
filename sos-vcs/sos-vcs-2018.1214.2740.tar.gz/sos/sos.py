#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xeded209d

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
        moves = dict(changes.moves.values())  # type: Dict[str, PathInfo]  # line 69
        realadditions = {k: v for k, v in changes.additions.items() if k not in changes.moves}  # type: Dict[str, PathInfo]  # line 70
        realdeletions = {k: v for k, v in changes.deletions.items() if k not in moves}  # type: Dict[str, PathInfo]  # line 71
        if len(changes.moves) > 0:  # line 72
            printo(ajoin("MOV ", ["%s  <=  %s" % (path, dpath) for path, (dpath, dinfo) in sorted(changes.moves.items())], "\n"))  # line 72
        if len(realadditions) > 0:  # line 73
            printo(ajoin("ADD ", sorted(realadditions.keys()), "\n"))  # line 73
        if len(realdeletions) > 0:  # line 74
            printo(ajoin("DEL ", sorted(realdeletions.keys()), "\n"))  # line 74
        if len(changes.modifications) > 0:  # line 75
            printo(ajoin("MOD ", sorted(changes.modifications.keys()), "\n"))  # line 75

    def loadBranches(_, offline: 'bool'=False):  # line 77
        ''' Load list of branches and current branch info from metadata file. '''  # line 78
        try:  # fails if not yet created (on initial branch/commit)  # line 79
            branches = None  # type: List[Tuple]  # line 80
            with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "r", encoding=UTF8) as fd:  # line 81
                repo, branches, config = json.load(fd)  # line 82
            _.tags = repo["tags"]  # list of commit messages to treat as globally unique tags  # line 83
            _.branch = repo["branch"]  # current branch integer  # line 84
            _.track, _.picky, _.strict, _.compress, _.version = [repo[r] for r in ["track", "picky", "strict", "compress", "version"]]  # line 85
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 86
            _.repoConf = config  # line 87
        except Exception as E:  # if not found, create metadata folder  # line 88
            _.branches = {}  # line 89
            _.track, _.picky, _.strict, _.compress, _.version = [defaults[k] for k in ["track", "picky", "strict", "compress"]] + [version.__version__]  # line 90
            (debug if offline else warn)("Couldn't read branches metadata: %r" % E)  # line 91

    def saveBranches(_, also: 'Dict[str, Any]'={}):  # line 93
        ''' Save list of branches and current branch info to metadata file. '''  # line 94
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # line 95
        with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "w", encoding=UTF8) as fd:  # line 96
            store = {"version": _.version, "tags": _.tags, "branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}  # type: Dict[str, Any]  # line 97
            store.update(also)  # allows overriding certain values at certain points in time  # line 98
            json.dump((store, list(_.branches.values()), _.repoConf), fd, ensure_ascii=False)  # stores using unicode codepoints, fd knows how to encode them  # line 99

    def getRevisionByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 101
        ''' Convenience accessor for named revisions (using commit message as name as a convention). '''  # line 102
        if name == "":  # line 103
            return -1  # line 103
        try:  # attempt to parse integer string  # line 104
            return int(name)  # attempt to parse integer string  # line 104
        except ValueError:  # line 105
            pass  # line 105
        found = [number for number, commit in _.commits.items() if name == commit.message]  # find any revision by commit message (usually used for tags)  # HINT allows finding any message, not only tagged ones  # line 106
        return found[0] if found else None  # line 107

    def getBranchByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 109
        ''' Convenience accessor for named branches. '''  # line 110
        if name == "":  # current  # line 111
            return _.branch  # current  # line 111
        try:  # attempt to parse integer string  # line 112
            return int(name)  # attempt to parse integer string  # line 112
        except ValueError:  # line 113
            pass  # line 113
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 114
        return found[0] if found else None  # line 115

    def loadBranch(_, branch: 'int'):  # line 117
        ''' Load all commit information from a branch meta data file. '''  # line 118
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "r", encoding=UTF8) as fd:  # line 119
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 120
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 121
        _.branch = branch  # line 122

    def saveBranch(_, branch: 'int'):  # line 124
        ''' Save all commit information to a branch meta data file. '''  # line 125
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # line 126
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "w", encoding=UTF8) as fd:  # line 127
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 128

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'):  # line 130
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 135
        debug("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 136
        tracked = [t for t in _.branches[_.branch].tracked]  # type: List[str]  # copy  # line 137
        untracked = [u for u in _.branches[_.branch].untracked]  # type: List[str]  # line 138
        os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 139
        _.loadBranch(_.branch)  # line 140
        revision = max(_.commits)  # type: int  # line 141
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 142
        for path, pinfo in _.paths.items():  # line 143
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 144
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 145
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 146
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 147
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].inSync, tracked, untracked)  # save branch info, before storing repo state at caller  # line 148

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 150
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 155
        simpleMode = not (_.track or _.picky)  # line 156
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # in case of initial branch creation  # line 157
        untracked = [t for t in _.branches[_.branch].untracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # line 158
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 159
        _.paths = {}  # type: Dict[str, PathInfo]  # line 160
        if simpleMode:  # branches from file system state  # line 161
            changes, msg = _.findChanges(branch, 0, progress=simpleMode)  # creates revision folder and versioned files  # line 162
            _.listChanges(changes)  # line 163
            if msg:  # display compression factor  # line 164
                printo(msg)  # display compression factor  # line 164
            _.paths.update(changes.additions.items())  # line 165
        else:  # tracking or picky mode: branch from latest revision  # line 166
            os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 167
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 168
                _.loadBranch(_.branch)  # line 169
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 170
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 171
                for path, pinfo in _.paths.items():  # line 172
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 173
        ts = int(time.time() * 1000)  # line 174
        _.commits = {0: CommitInfo(0, ts, ("Branched on %s" % strftime(ts) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 175
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 176
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 177
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked, untracked)  # save branch info, in case it is needed  # line 178

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 180
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 181
        shutil.rmtree(encode(os.path.join(_.root, metaFolder, "b%d" % branch)))  # TODO put into recycle bin, under ./sos?  # line 182
        binfo = _.branches[branch]  # line 183
        del _.branches[branch]  # line 184
        _.branch = max(_.branches)  # line 185
        _.saveBranches()  # line 186
        _.commits.clear()  # line 187
        return binfo  # line 188

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 190
        ''' Load all file information from a commit meta data. '''  # line 191
        with codecs.open(encode(branchFolder(branch, revision, base=_.root, file=metaFile)), "r", encoding=UTF8) as fd:  # line 192
            _.paths = json.load(fd)  # line 193
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 194
        _.branch = branch  # line 195

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 197
        ''' Save all file information to a commit meta data file. '''  # line 198
        target = branchFolder(branch, revision, base=_.root)  # type: str  # line 199
        try:  # line 200
            os.makedirs(encode(target))  # line 200
        except:  # line 201
            pass  # line 201
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(target, metaFile)), encode(os.path.join(target, metaBack))))  # line 202
        with codecs.open(encode(os.path.join(target, metaFile)), "w", encoding=UTF8) as fd:  # line 203
            json.dump(_.paths, fd, ensure_ascii=False)  # line 204

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'Tuple[ChangeSet, _coconut.typing.Optional[str]]':  # line 206
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes (always overrides considerOnly)
        progress: Show file names during processing
        returns: (ChangeSet = the state of file tree *differences*, unless "inverse" is True -> then return original data, message)
    '''  # line 215
        write = branch is not None and revision is not None  # line 216
        if write:  # line 217
            try:  # line 218
                os.makedirs(encode(branchFolder(branch, revision, base=_.root)))  # line 218
            except FileExistsError:  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 219
                pass  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 219
        changes = ChangeSet({}, {}, {}, {})  # type: ChangeSet  # TODO Needs explicity initialization due to mypy problems with default arguments :-(  # line 220
        indicator = ProgressIndicator() if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # optional file list progress indicator  # line 221
        hashed = None  # type: _coconut.typing.Optional[str]  # line 222
        written = None  # type: int  # line 222
        compressed = 0  # type: int  # line 222
        original = 0  # type: int  # line 222
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 223
        for path, pinfo in _.paths.items():  # line 224
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 225
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 228
        for path, dirnames, filenames in os.walk(_.root):  # line 229
            path = decode(path)  # line 230
            dirnames[:] = [decode(d) for d in dirnames]  # line 231
            filenames[:] = [decode(f) for f in filenames]  # line 232
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 233
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 234
            dirnames.sort()  # line 235
            filenames.sort()  # line 235
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 236
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 237
            if dontConsider:  # line 238
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 239
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 240
                filename = relPath + SLASH + file  # line 241
                filepath = os.path.join(path, file)  # line 242
                try:  # line 243
                    stat = os.stat(encode(filepath))  # line 243
                except Exception as E:  # line 244
                    exception(E)  # line 244
                    continue  # line 244
                size, mtime = stat.st_size, int(stat.st_mtime * 1000)  # line 245
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 246
                if show:  # indication character returned  # line 247
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", show, filename)  # line 248
                    printo(outstring + " " * max(0, termWidth - len(outstring)), nl="")  # line 249
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 250
                    nameHash = hashStr(filename)  # line 251
                    try:  # line 252
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 253
                        changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 254
                        compressed += written  # line 255
                        original += size  # line 255
                    except Exception as E:  # line 256
                        exception(E)  # line 256
                    continue  # with next file  # line 257
                last = _.paths[filename]  # filename is known - check for modifications  # line 258
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 259
                    try:  # line 260
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 261
                        changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 262
                        continue  # line 262
                    except Exception as E:  # line 263
                        exception(E)  # line 263
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and tryOrDefault(lambda: (hashFile(filepath, _.compress)[0] != last.hash), default=False)):  # detected a modification TODO wrap hashFile exception  # line 264
                    try:  # line 265
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 266
                        changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 267
                    except Exception as E:  # line 268
                        exception(E)  # line 268
                else:  # with next file  # line 269
                    continue  # with next file  # line 269
                compressed += written  # line 270
                original += last.size if inverse else size  # line 270
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 271
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 271
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 272
            for file in names:  # line 273
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 274
                    continue  # don't mark ignored files as deleted  # line 274
                pth = path + SLASH + file  # type: str  # line 275
                changes.deletions[pth] = _.paths[pth]  # line 276
        for path, info in changes.additions.items():  # line 277
            for dpath, dinfo in changes.deletions.items():  # line 278
                if info.size == dinfo.size and info.mtime == dinfo.mtime and info.hash == dinfo.hash:  # was moved TODO check either mtime or hash?  # line 279
                    changes.moves[path] = (dpath, info)  # store new data and original name, but don't remove add/del  # line 280
                    break  # deletions loop, continue with next addition  # line 281
        if progress:  # forces clean line of progress output  # line 282
            printo("\r" + " " * termWidth + "\r", nl="")  # forces clean line of progress output  # line 282
        else:  # line 283
            debug("Finished detecting changes")  # line 283
        return (changes, ("Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else None)  # line 284

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 286
        ''' Returns nothing, just updates _.paths in place. '''  # line 287
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 288

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 290
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 291
        _.loadCommit(branch, 0)  # load initial paths  # line 292
        if incrementally:  # line 293
            yield _.paths  # line 293
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 294
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 294
        for rev in range(1, revision + 1):  # line 295
            m.loadCommit(branch, rev)  # line 296
            for p, info in m.paths.items():  # line 297
                if info.size == None:  # line 298
                    del _.paths[p]  # line 298
                else:  # line 299
                    _.paths[p] = info  # line 299
            if incrementally:  # line 300
                yield _.paths  # line 300
        yield None  # for the default case - not incrementally  # line 301

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 303
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 306
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 307
            return (_.branch, -1)  # no branch/revision specified  # line 307
        argument = argument.strip()  # line 308
        if argument.startswith(SLASH):  # current branch  # line 309
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 309
        if argument.endswith(SLASH):  # line 310
            try:  # line 311
                return (_.getBranchByName(argument[:-1]), -1)  # line 311
            except ValueError:  # line 312
                Exit("Unknown branch label '%s'" % argument)  # line 312
        if SLASH in argument:  # line 313
            b, r = argument.split(SLASH)[:2]  # line 314
            try:  # line 315
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 315
            except ValueError:  # line 316
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 316
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 317
        if branch not in _.branches:  # line 318
            branch = None  # line 318
        try:  # either branch name/number or reverse/absolute revision number  # line 319
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 319
        except:  # line 320
            Exit("Unknown branch label or wrong number format")  # line 320
        Exit("This should never happen. Please create a issue report")  # line 321
        return (None, None)  # line 321

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 323
        while True:  # find latest revision that contained the file physically  # line 324
            source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 325
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 326
                break  # line 326
            revision -= 1  # line 327
            if revision < 0:  # line 328
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 328
        return revision, source  # line 329

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 331
        ''' Copy versioned file to other branch/revision. '''  # line 332
        target = branchFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 333
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 334
        shutil.copy2(encode(source), encode(target))  # line 335

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 337
        ''' Return file contents, or copy contents into file path provided. '''  # line 338
        source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 339
        try:  # line 340
            with openIt(source, "r", _.compress) as fd:  # line 341
                if toFile is None:  # read bytes into memory and return  # line 342
                    return fd.read()  # read bytes into memory and return  # line 342
                with open(encode(toFile), "wb") as to:  # line 343
                    while True:  # line 344
                        buffer = fd.read(bufSize)  # line 345
                        to.write(buffer)  # line 346
                        if len(buffer) < bufSize:  # line 347
                            break  # line 347
                    return None  # line 348
        except Exception as E:  # line 349
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 349
        return None  # line 350

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 352
        ''' Recreate file for given revision, or return binary contents if path is None. '''  # line 353
        if relPath is None:  # just return contents  # line 354
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 354
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 355
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 356
            try:  # line 357
                os.makedirs(encode(os.path.dirname(target)))  # line 357
            except:  # line 358
                pass  # line 358
        if pinfo.size == 0:  # line 359
            with open(encode(target), "wb"):  # line 360
                pass  # line 360
            try:  # update access/modification timestamps on file system  # line 361
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 361
            except Exception as E:  # line 362
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 362
            return None  # line 363
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 364
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 366
            while True:  # line 367
                buffer = fd.read(bufSize)  # line 368
                to.write(buffer)  # line 369
                if len(buffer) < bufSize:  # line 370
                    break  # line 370
        try:  # update access/modification timestamps on file system  # line 371
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 371
        except Exception as E:  # line 372
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 372
        return None  # line 373

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None, negative: 'bool'=False) -> 'FrozenSet[str]':  # line 375
        ''' Returns list of tracking patterns (or untracking patterns if negative) for provided branch or current branch. '''  # line 376
        return _coconut.frozenset() if not (_.track or _.picky) else frozenset(_.branches[(_.branch if branch is None else branch)].untracked if negative else _.branches[(_.branch if branch is None else branch)].tracked)  # line 377


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 381
    ''' Initial command to start working offline. '''  # line 382
    if os.path.exists(encode(metaFolder)):  # line 383
        if '--force' not in options:  # line 384
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 384
        try:  # line 385
            for entry in os.listdir(metaFolder):  # line 386
                resource = metaFolder + os.sep + entry  # line 387
                if os.path.isdir(resource):  # line 388
                    shutil.rmtree(encode(resource))  # line 388
                else:  # line 389
                    os.unlink(encode(resource))  # line 389
        except:  # line 390
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 390
    m = Metadata(offline=True)  # type: Metadata  # line 391
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 392
        m.compress = True  # plain file copies instead of compressed ones  # line 392
    if '--picky' in options or m.c.picky:  # Git-like  # line 393
        m.picky = True  # Git-like  # line 393
    elif '--track' in options or m.c.track:  # Svn-like  # line 394
        m.track = True  # Svn-like  # line 394
    if '--strict' in options or m.c.strict:  # always hash contents  # line 395
        m.strict = True  # always hash contents  # line 395
    debug(MARKER + "Going offline...")  # line 396
    m.createBranch(0, (defaults["defaultbranch"] if argument is None else argument), initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 397
    m.branch = 0  # line 398
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 399
    info(MARKER + "Offline repository prepared. Use 'sos online' to finish offline work")  # line 400

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 402
    ''' Finish working offline. '''  # line 403
    debug(MARKER + "Going back online...")  # line 404
    force = '--force' in options  # type: bool  # line 405
    m = Metadata()  # type: Metadata  # line 406
    m.loadBranches()  # line 407
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 408
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 408
    strict = '--strict' in options or m.strict  # type: bool  # line 409
    if options.count("--force") < 2:  # line 410
        changes, msg = m.findChanges(checkContent=strict, considerOnly=None if not (m.track or m.picky) else m.getTrackingPatterns(), dontConsider=None if not (m.track or m.picky) else m.getTrackingPatterns(negative=True), progress='--progress' in options)  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 411
        if modified(changes):  # line 412
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 416
    try:  # line 417
        shutil.rmtree(encode(metaFolder))  # line 417
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 417
    except Exception as E:  # line 418
        Exit("Error removing offline repository: %r" % E)  # line 418
    info(MARKER + "Offline repository removed, you're back online")  # line 419

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 421
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 422
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 423
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 424
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 425
    m = Metadata()  # type: Metadata  # line 426
    m.loadBranch(m.branch)  # line 427
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 428
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 428
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 429
    debug(MARKER + "Branching to %sbranch b%02d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 430
    if last:  # branch from branch's last revision  # line 431
        m.duplicateBranch(branch, (("" if argument is None else argument)) + " (Branched from r%02d/b%02d)" % (m.branch, max(m.commits.keys())))  # branch from branch's last revision  # line 431
    else:  #  branch from current file tree state  # line 432
        m.createBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  #  branch from current file tree state  # line 432
    if not stay:  # line 433
        m.branch = branch  # line 434
        m.saveBranches()  # line 435
    info(MARKER + "%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 436

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 438
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 439
    if '--repo' in options:  # line 440
        status(options, onlys, excps)  # line 440
        return  # line 440
    m = Metadata()  # type: Metadata  # line 441
    branch = None  # type: _coconut.typing.Optional[int]  # line 441
    revision = None  # type: _coconut.typing.Optional[int]  # line 441
    strict = '--strict' in options or m.strict  # type: bool  # line 442
    branch, revision = m.parseRevisionString(argument)  # line 443
    if branch not in m.branches:  # line 444
        Exit("Unknown branch")  # line 444
    m.loadBranch(branch)  # knows commits  # line 445
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 446
    if revision < 0 or revision > max(m.commits):  # line 447
        Exit("Unknown revision r%02d" % revision)  # line 447
    debug(MARKER + "Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 448
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 449
    changes, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 450
    m.listChanges(changes)  # line 455
    return changes  # for unit tests only TODO remove  # line 456

def _diff(m: 'Metadata', branch: 'int', revision: 'int', changes: 'ChangeSet'):  # TODO introduce option to diff against committed revision  # line 458
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 459
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 460
    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 461
        content = None  # type: _coconut.typing.Optional[bytes]  # line 462
        if pinfo.size == 0:  # empty file contents  # line 463
            content = b""  # empty file contents  # line 463
        else:  # versioned file  # line 464
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 464
            assert content is not None  # versioned file  # line 464
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 465
        blocks = None  # type: List[MergeBlock]  # line 466
        nl = None  # type: bytes  # line 466
        blocks, nl = merge(filename=abspath, into=content, diffOnly=True)  # only determine change blocks  # line 467
        printo("DIF %s%s  %s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else "", NL_NAMES[nl]))  # line 468
        for block in blocks:  # line 469
#      if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:
#        pass  # TODO print some previous and following lines - which aren't accessible here anymore
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 472
                for no, line in enumerate(block.lines):  # line 473
                    printo("--- %04d |%s|" % (no + block.line, line))  # line 474
            elif block.tipe == MergeBlockType.REMOVE:  # line 475
                for no, line in enumerate(block.lines):  # line 476
                    printo("+++ %04d |%s|" % (no + block.line, line))  # line 477
            elif block.tipe == MergeBlockType.REPLACE:  # TODO for MODIFY also show intra-line change ranges (TODO remove if that code was also removed)  # line 478
                for no, line in enumerate(block.replaces.lines):  # line 479
                    printo("- | %04d |%s|" % (no + block.replaces.line, line))  # line 480
                for no, line in enumerate(block.lines):  # line 481
                    printo("+ | %04d |%s|" % (no + block.line, line))  # line 482
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 486
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 487
    m = Metadata()  # type: Metadata  # line 488
    branch = None  # type: _coconut.typing.Optional[int]  # line 488
    revision = None  # type: _coconut.typing.Optional[int]  # line 488
    strict = '--strict' in options or m.strict  # type: bool  # line 489
    _from = {None: option.split("--from=")[1] for option in options if option.startswith("--from=")}.get(None, None)  # type: _coconut.typing.Optional[str]  # TODO implement  # line 490
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 491
    if branch not in m.branches:  # line 492
        Exit("Unknown branch")  # line 492
    m.loadBranch(branch)  # knows commits  # line 493
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 494
    if revision < 0 or revision > max(m.commits):  # line 495
        Exit("Unknown revision r%02d" % revision)  # line 495
    debug(MARKER + "Textual differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 496
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 497
    changes, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 498
    _diff(m, branch, revision, changes)  # line 503

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 505
    ''' Create new revision from file tree changes vs. last commit. '''  # line 506
    m = Metadata()  # type: Metadata  # line 507
    if argument is not None and argument in m.tags:  # line 508
        Exit("Illegal commit message. It was already used as a tag name")  # line 508
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 509
# No untracking patterns needed here
    if m.picky and not trackingPatterns:  # line 511
        Exit("No file patterns staged for commit in picky mode")  # line 511
    debug((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 512
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options, check=False, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but aborts if no changes  # line 513
    m.paths = changes.additions  # line 514
    m.paths.update(changes.modifications)  # update pathset to changeset only  # line 515
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changes.deletions.items()})  # line 516
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 517
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 518
    m.saveBranch(m.branch)  # line 519
    m.loadBranches()  # TODO is it necessary to load again?  # line 520
    if m.picky:  # remove tracked patterns  # line 521
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 521
    else:  # track or simple mode: set branch dirty  # line 522
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 522
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 523
        m.tags.append(argument)  # memorize unique tag  # line 523
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 523
    m.saveBranches()  # line 524
    info(MARKER + "Created new revision r%02d%s (+%02d/-%02d/\u00b1%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications), len(changes.moves)))  # line 525

def status(options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 527
    ''' Show branches and current repository state. '''  # line 528
    m = Metadata()  # type: Metadata  # line 529
    current = m.branch  # type: int  # line 530
    strict = '--strict' in options or m.strict  # type: bool  # line 531
    info(MARKER + "Offline repository status")  # line 532
    info("Installation path:   %s" % os.path.abspath(os.path.dirname(__file__)))  # line 533
    info("Current SOS version: %s" % version.__version__)  # line 534
    info("At creation version: %s" % m.version)  # line 535
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 536
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 537
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 538
    info("Number of branches:  %d" % len(m.branches))  # line 539
#  info("Revisions:           %d" % sum([]))
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 541
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 542
    m.loadBranch(m.branch)  # line 543
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 508  # line 544
    changes, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress=True)  # line 545
    printo("File tree %s" % ("has changes vs. last revision of current branch" if modified(changes) else "is unchanged"))  # line 550
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 551
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 552
        m.loadBranch(branch.number)  # knows commit history  # line 553
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 554
    if m.track or m.picky and (len(m.branches[m.branch].tracked) > 0 or len(m.branches[m.branch].untracked) > 0):  # line 555
        info("\nTracked file patterns:")  # TODO print matching untracking patterns side-by-side  # line 556
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 557
        info("\nUntracked file patterns:")  # line 558
        printo(ajoin("  | ", m.branches[m.branch].untracked, "\n"))  # line 559

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str], FrozenSet[str]]':  # line 561
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags.
  '''  # line 567
    assert not (check and commit)  # line 568
    m = Metadata()  # type: Metadata  # line 569
    force = '--force' in options  # type: bool  # line 570
    strict = '--strict' in options or m.strict  # type: bool  # line 571
    if argument is not None:  # line 572
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 573
        if branch is None:  # line 574
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 574
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 575

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 578
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 579
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 580
    changes, msg = m.findChanges(m.branch if commit else None, max(m.commits) + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress='--progress' in options)  # line 581
    if check and modified(changes) and not force:  # line 586
        m.listChanges(changes)  # line 587
        Exit("File tree contains changes. Use --force to proceed")  # line 588
    elif commit:  # line 589
        if not modified(changes) and not force:  # line 590
            Exit("Nothing to commit")  # line 590
        m.listChanges(changes)  # line 591
        if msg:  # line 592
            printo(msg)  # line 592

    if argument is not None:  # branch/revision specified  # line 594
        m.loadBranch(branch)  # knows commits of target branch  # line 595
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 596
        if revision < 0 or revision > max(m.commits):  # line 597
            Exit("Unknown revision r%02d" % revision)  # line 597
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch), m.getTrackingPatterns(branch, negative=True))  # line 598
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns, untrackingPatterns)  # line 599

def switch(argument: 'str', options: 'List[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 601
    ''' Continue work on another branch, replacing file tree changes. '''  # line 602
    m, branch, revision, changes, strict, _force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, ["--force"] + options)  # line 603
    force = '--force' in options  # type: bool  # needed as we fake force in above access  # line 604

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 607
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked, untracked=m.branches[branch].untracked)  # line 608
    else:  # full file switch  # line 609
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 610
        todos, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((untrackingPatterns | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 611

# Now check for potential conflicts
        changes.deletions.clear()  # local deletions never create conflicts, modifications always  # line 618
        rms = []  # type: _coconut.typing.Sequence[str]  # local additions can be ignored if restoration from switch would be same  # line 619
        for a, pinfo in changes.additions.items():  # has potential corresponding re-add in switch operation:  # line 620
            if a in todos.deletions and pinfo.size == todos.deletions[a].size and (pinfo.hash == todos.deletions[a].hash if m.strict else pinfo.mtime == todos.deletions[a].mtime):  # line 621
                rms.append(a)  # line 621
        for rm in rms:  # TODO could also silently accept remote DEL for local ADD  # line 622
            del changes.additions[rm]  # TODO could also silently accept remote DEL for local ADD  # line 622
        if modified(changes) and not force:  # line 623
            m.listChanges(changes)  # line 623
            Exit("File tree contains changes. Use --force to proceed")  # line 623
        debug(MARKER + "Switching to branch %sb%02d/r%02d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 624
        if not modified(todos):  # line 625
            info("No changes to current file tree")  # line 626
        else:  # integration required  # line 627
            for path, pinfo in todos.deletions.items():  # line 628
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 629
                printo("ADD " + path)  # line 630
            for path, pinfo in todos.additions.items():  # line 631
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 632
                printo("DEL " + path)  # line 633
            for path, pinfo in todos.modifications.items():  # line 634
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 635
                printo("MOD " + path)  # line 636
    m.branch = branch  # line 637
    m.saveBranches()  # store switched path info  # line 638
    info(MARKER + "Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 639

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 641
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 645
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 646
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 647
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 648
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 649
    m = Metadata()  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 650
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 651
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 652
    debug(MARKER + "Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 653

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 656
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 657
    untrackingUnion = untrackingPatterns | m.getTrackingPatterns(branch, negative=True)  # type: FrozenSet[str]  # line 658
    changes, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingUnion), dontConsider=excps if not (m.track or m.picky) else (untrackingUnion if onlys is None else onlys), progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 659
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 664
        if trackingUnion != trackingPatterns:  # nothing added  # line 665
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 666
        else:  # line 667
            info("Nothing to update")  # but write back updated branch info below  # line 668
    else:  # integration required  # line 669
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 670
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 671
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 671
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 672
        for path, pinfo in changes.additions.items():  # line 673
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 674
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 674
            if mrg.value & MergeOperation.REMOVE.value:  # line 675
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 675
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 676
        for path, pinfo in changes.modifications.items():  # line 677
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 678
            binary = not m.isTextType(path)  # type: bool  # line 679
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 680
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 681
                printo(("MOD " if not binary else "BIN ") + path)  # line 682
                while True:  # line 683
                    printo(into)  # TODO print mtime, size differences?  # line 684
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 685
                    if op in ("it" if binary else "itm"):  # line 686
                        break  # line 686
            if op == "t":  # line 687
                printo("THR " + path)  # blockwise copy of contents  # line 688
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 688
            elif op == "m":  # line 689
                current = None  # type: bytes  # line 690
                with open(encode(into), "rb") as fd:  # TODO slurps file  # line 691
                    current = fd.read()  # TODO slurps file  # line 691
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 692
                if current == file:  # line 693
                    debug("No difference to versioned file")  # line 693
                elif file is not None:  # if None, error message was already logged  # line 694
                    contents = None  # type: bytes  # line 695
                    nl = None  # type: bytes  # line 695
                    contents, nl = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # line 696
                    if contents != current:  # line 697
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 698
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 698
                    else:  # TODO but update timestamp?  # line 699
                        debug("No change")  # TODO but update timestamp?  # line 699
            else:  # mine or wrong input  # line 700
                printo("MNE " + path)  # nothing to do! same as skip  # line 701
    info(MARKER + "Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 702
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 703
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 704
    m.saveBranches()  # line 705

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 707
    ''' Remove a branch entirely. '''  # line 708
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options)  # line 709
    if len(m.branches) == 1:  # line 710
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 710
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 711
    if branch is None or branch not in m.branches:  # line 712
        Exit("Cannot delete unknown branch %r" % branch)  # line 712
    debug(MARKER + "Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 713
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 714
    info(MARKER + "Branch b%02d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 715

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[], negative: 'bool'=False):  # line 717
    ''' Add a tracked files pattern to current branch's tracked files. negative means tracking blacklisting. '''  # line 718
    force = '--force' in options  # type: bool  # line 719
    m = Metadata()  # type: Metadata  # line 720
    if not (m.track or m.picky):  # line 721
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 721
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 722
    if pattern in patterns:  # line 723
        Exit("Pattern '%s' already tracked" % pattern)  # line 723
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 724
        Exit("The pattern folder doesn't exist. Use --force to add the file pattern anyway")  # line 724
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 725
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 726
    patterns.append(pattern)  # line 727
    m.saveBranches()  # line 728
    info(MARKER + "Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 729

def remove(relPath: 'str', pattern: 'str', negative: 'bool'=False):  # line 731
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 732
    m = Metadata()  # type: Metadata  # line 733
    if not (m.track or m.picky):  # line 734
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 734
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 735
    if pattern not in patterns:  # line 736
        suggestion = _coconut.set()  # type: Set[str]  # line 737
        for pat in patterns:  # line 738
            if fnmatch.fnmatch(pattern, pat):  # line 739
                suggestion.add(pat)  # line 739
        if suggestion:  # TODO use same wording as in move  # line 740
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 740
        Exit("Tracked pattern '%s' not found" % pattern)  # line 741
    patterns.remove(pattern)  # line 742
    m.saveBranches()  # line 743
    info(MARKER + "Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 744

def ls(folder: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 746
    ''' List specified directory, augmenting with repository metadata. '''  # line 747
    folder = (os.getcwd() if folder is None else folder)  # line 748
    m = Metadata()  # type: Metadata  # line 749
    debug(MARKER + "Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 750
    relPath = relativize(m.root, os.path.join(folder, "-"))[0]  # type: str  # line 751
    if relPath.startswith(".."):  # line 752
        Exit("Cannot list contents of folder outside offline repository")  # line 752
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 753
    untrackingPatterns = m.getTrackingPatterns(negative=True) if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 754
    if '--tags' in options:  # line 755
        printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 756
        return  # line 757
    if '--patterns' in options:  # line 758
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 759
        if out:  # line 760
            printo(out)  # line 760
        return  # line 761
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 762
    printo("DIR %s" % relPath)  # line 763
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 764
        ignore = None  # type: _coconut.typing.Optional[str]  # line 765
        for ig in m.c.ignores:  # line 766
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 767
                ignore = ig  # remember first match  # line 767
                break  # remember first match  # line 767
        if ig:  # line 768
            for wl in m.c.ignoresWhitelist:  # line 769
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 770
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 770
                    break  # found a white list entry for ignored file, undo ignoring it  # line 770
        matches = []  # type: List[str]  # line 771
        if not ignore:  # line 772
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 773
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 774
                    matches.append(os.path.basename(pattern))  # line 774
        matches.sort(key=lambda element: len(element))  # line 775
        printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "\u00b7\u00b7\u00b7"), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 776

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 778
    ''' List previous commits on current branch. '''  # line 779
    m = Metadata()  # type: Metadata  # line 780
    m.loadBranch(m.branch)  # knows commit history  # line 781
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 782
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 783
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, max(m.commits))  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 784
    maxWidth = max([wcswidth((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) for commit in m.commits.values()])  # type: int  # line 785
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 786
    for no in range(max(m.commits) + 1):  # line 787
        commit = m.commits[no]  # type: CommitInfo  # line 788
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 789
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # side-effect: updates m.paths  # line 790
        _add = news - olds  # type: FrozenSet[str]  # line 791
        _del = olds - news  # type: FrozenSet[str]  # line 792
        _mod = frozenset([_ for _, info in nxts.items() if _ in m.paths and m.paths[_].size != info.size and (m.paths[_].hash != info.hash if m.strict else m.paths[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 793
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 794
        printo("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT) |%s|%s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)).ljust(maxWidth), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 795
        if '--changes' in options:  # TODO moves detection?  # line 796
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}, {}))  # TODO moves detection?  # line 796
        if '--diff' in options:  #  _diff(m, changes)  # needs from revision diff  # line 797
            pass  #  _diff(m, changes)  # needs from revision diff  # line 797
        olds = news  # line 798

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 800
    ''' Exported entire repository as archive for easy transfer. '''  # line 801
    debug(MARKER + "Dumping repository to archive...")  # line 802
    progress = '--progress' in options  # type: bool  # line 803
    import zipfile  # TODO display compression ratio (if any)  # line 804
    try:  # line 805
        import zlib  # line 805
        compression = zipfile.ZIP_DEFLATED  # line 805
    except:  # line 806
        compression = zipfile.ZIP_STORED  # line 806

    if argument is None:  # line 808
        Exit("Argument missing (target filename)")  # line 808
    argument = argument if "." in argument else argument + ".sos.zip"  # line 809
    if os.path.exists(encode(argument)):  # line 810
        try:  # line 811
            shutil.copy2(encode(argument), encode(argument + BACKUP_SUFFIX))  # line 811
        except Exception as E:  # line 812
            Exit("Error creating backup copy before dumping. Please resolve and retry. %r" % E)  # line 812
    with zipfile.ZipFile(argument, "w", compression) as _zip:  # line 813
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 814
        indicator = ProgressIndicator() if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 815
        totalsize = 0  # type: int  # line 816
        start_time = time.time()  # type: float  # line 817
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 818
            dirpath = decode(dirpath)  # line 819
            dirnames[:] = [decode(d) for d in dirnames]  # line 820
            filenames[:] = [decode(f) for f in filenames]  # line 821
            for filename in filenames:  # line 822
                abspath = os.path.join(dirpath, filename)  # type: str  # line 823
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 824
                totalsize += os.stat(encode(abspath)).st_size  # line 825
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 826
                if show:  # line 827
                    printo(("\rDumping %s @%.2f MiB/s %s" % (show, totalsize / (MEBI * (time.time() - start_time)), filename)).ljust(termWidth), nl="")  # line 827
                _zip.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 828
    info("\r" + (MARKER + "Finished dumping entire repository.").ljust(termWidth))  # clean line  # line 829

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 831
    command, key, value = (arguments + [None] * 2)[:3]  # line 832
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 833
        Exit("Unknown config command")  # line 833
    local = "--local" in options  # type: bool  # line 834
    m = Metadata()  # type: Metadata  # loads layered configuration as well. TODO warning if repo not exists  # line 835
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 836
    if command == "set":  # line 837
        if None in (key, value):  # line 838
            Exit("Key or value not specified")  # line 838
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 839
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 839
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 840
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 840
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 841
    elif command == "unset":  # line 842
        if key is None:  # line 843
            Exit("No key specified")  # line 843
        if key not in c.keys():  # HINT: Works on local configurations when used with --local  # line 844
            Exit("Unknown key")  # HINT: Works on local configurations when used with --local  # line 844
        del c[key]  # line 845
    elif command == "add":  # line 846
        if None in (key, value):  # line 847
            Exit("Key or value not specified")  # line 847
        if key not in CONFIGURABLE_LISTS:  # line 848
            Exit("Unsupported key %r" % key)  # line 848
        if key not in c.keys():  # prepare empty list, or copy from global, add new value below  # line 849
            c[key] = [_ for _ in c.__defaults[key]] if local else []  # prepare empty list, or copy from global, add new value below  # line 849
        elif value in c[key]:  # line 850
            Exit("Value already contained, nothing to do")  # line 850
        if ";" in value:  # line 851
            c[key].append(removePath(key, value))  # line 851
        else:  # line 852
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 852
    elif command == "rm":  # line 853
        if None in (key, value):  # line 854
            Exit("Key or value not specified")  # line 854
        if key not in c.keys():  # line 855
            Exit("Unknown key %r" % key)  # line 855
        if value not in c[key]:  # line 856
            Exit("Unknown value %r" % value)  # line 856
        c[key].remove(value)  # line 857
        if local and len(c[key]) == 0 and "--prune" in options:  # remove local enty, to fallback to global  # line 858
            del c[key]  # remove local enty, to fallback to global  # line 858
    else:  # Show or list  # line 859
        if key == "flags":  # list valid configuration items  # line 860
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 860
        elif key == "lists":  # line 861
            printo(", ".join(CONFIGURABLE_LISTS))  # line 861
        elif key == "texts":  # line 862
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 862
        else:  # line 863
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 864
            c = m.c  # always use full configuration chain  # line 865
            try:  # attempt single key  # line 866
                assert key is not None  # line 867
                c[key]  # line 867
                l = key in c.keys()  # type: bool  # line 868
                g = key in c.__defaults.keys()  # type: bool  # line 868
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 869
            except:  # normal value listing  # line 870
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 871
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 872
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 873
                for k, vt in sorted(vals.items()):  # line 874
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 874
                if len(c.keys()) == 0:  # line 875
                    info("No local configuration stored")  # line 875
                if len(c.__defaults.keys()) == 0:  # line 876
                    info("No global configuration stored")  # line 876
        return  # in case of list, no need to store anything  # line 877
    if local:  # saves changes of repoConfig  # line 878
        m.repoConf = c.__map  # saves changes of repoConfig  # line 878
        m.saveBranches()  # saves changes of repoConfig  # line 878
        Exit("OK", code=0)  # saves changes of repoConfig  # line 878
    else:  # global config  # line 879
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 880
        if f is None:  # line 881
            error("Error saving user configuration: %r" % h)  # line 881
        else:  # line 882
            Exit("OK", code=0)  # line 882

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[], negative: 'bool'=False):  # line 884
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique.
      for "mvnot" don't do any renaming (or do?)
  '''  # line 887
# TODO info(MARKER + TODO write tests for that
    force = '--force' in options  # type: bool  # line 889
    soft = '--soft' in options  # type: bool  # line 890
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 891
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 891
    m = Metadata()  # type: Metadata  # line 892
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 893
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 894
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 895
    if not matching and not force:  # line 896
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 896
    if not (m.track or m.picky):  # line 897
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 897
    if pattern not in patterns:  # list potential alternatives and exit  # line 898
        for tracked in (t for t in patterns if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 899
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 900
            if alternative:  # line 901
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 901
        if not (force or soft):  # line 902
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 902
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 903
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 904
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 905
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 909
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 910
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 910
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 911
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 912
    if len({st[1] for st in matches}) != len(matches):  # line 913
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 913
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 914
    if os.path.exists(encode(newRelPath)):  # line 915
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 916
        if exists and not (force or soft):  # line 917
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 917
    else:  # line 918
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 918
    if not soft:  # perform actual renaming  # line 919
        for (source, target) in matches:  # line 920
            try:  # line 921
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 921
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 922
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 922
    patterns[patterns.index(pattern)] = newPattern  # line 923
    m.saveBranches()  # line 924

def parse(root: 'str', cwd: 'str'):  # line 926
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm. '''  # line 927
    debug("Parsing command-line arguments...")  # line 928
    try:  # line 929
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 930
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: Union[List[str], str, None]  # line 931
        if len(arguments) == 0:  # line 932
            arguments = [None]  # line 932
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 933
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 934
        debug("Processing command %r with arguments %r and options %r." % (("" if command is None else command), arguments if arguments else "", options))  # line 935
        if command[:1] in "amr":  # line 936
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 936
        if command[:1] == "m":  # line 937
            if len(arguments) < 2:  # line 938
                Exit("Need a second file pattern argument as target for move or config command")  # line 938
            newRelPath, newPattern = relativize(root, os.path.join(cwd, options[0]))  # line 939
        if command[:1] == "a":  # also addnot  # line 940
            add(relPath, pattern, options, negative="n" in command)  # also addnot  # line 940
        elif command[:1] == "b":  # line 941
            branch(arguments[0], options)  # line 941
        elif command[:3] == "com":  # line 942
            commit(arguments[0], options, onlys, excps)  # line 942
        elif command[:2] == "ch":  # "changes" (legacy)  # line 943
            changes(arguments[0], options, onlys, excps)  # "changes" (legacy)  # line 943
        elif command[:2] == "ci":  # line 944
            commit(arguments[0], options, onlys, excps)  # line 944
        elif command[:3] == 'con':  # line 945
            config(arguments, options)  # line 945
        elif command[:2] == "de":  # line 946
            delete(arguments[0], options)  # line 946
        elif command[:2] == "di":  # line 947
            diff(arguments[0], options, onlys, excps)  # line 947
        elif command[:2] == "du":  # line 948
            dump(arguments[0], options)  # line 948
        elif command[:1] == "h":  # line 949
            usage(APPNAME, version.__version__)  # line 949
        elif command[:2] == "lo":  # line 950
            log(options)  # line 950
        elif command[:2] == "li":  # line 951
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 951
        elif command[:2] == "ls":  # TODO avoid and/or normalize root super paths (..)?  # line 952
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # TODO avoid and/or normalize root super paths (..)?  # line 952
        elif command[:1] == "m":  # also mvnot  # line 953
            move(relPath, pattern, newRelPath, newPattern, options[1:], negative="n" in command)  # also mvnot  # line 953
        elif command[:2] == "of":  # line 954
            offline(arguments[0], options)  # line 954
        elif command[:2] == "on":  # line 955
            online(options)  # line 955
        elif command[:1] == "r":  # also rmnot  # line 956
            remove(relPath, pattern, negative="n" in command)  # also rmnot  # line 956
        elif command[:2] == "st":  # line 957
            changes(arguments[0], options, onlys, excps)  # line 957
        elif command[:2] == "sw":  # line 958
            switch(arguments[0], options, onlys, excps)  # line 958
        elif command[:1] == "u":  # line 959
            update(arguments[0], options, onlys, excps)  # line 959
        elif command[:1] == "v":  # line 960
            usage(APPNAME, version.__version__, short=True)  # line 960
        else:  # line 961
            Exit("Unknown command '%s'" % command)  # line 961
        Exit(code=0)  # line 962
    except (Exception, RuntimeError) as E:  # line 963
        exception(E)  # line 964
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing.")  # line 965

def main():  # line 967
    global debug, info, warn, error  # line 968
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 969
    _log = Logger(logging.getLogger(__name__))  # line 970
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 970
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 971
        sys.argv.remove(option)  # clean up program arguments  # line 971
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 972
        usage(APPNAME, version.__version__)  # line 972
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
