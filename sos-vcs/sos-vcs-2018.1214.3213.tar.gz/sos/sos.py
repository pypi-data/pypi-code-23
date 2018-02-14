#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xbe6e351b

# Compiled with Coconut version 1.3.1-post_dev18 [Dead Parrot]

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
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": False, "texttype": ["*.md", "*.coco", "*.py"], "bintype": [], "ignoreDirs": [".*", "__pycache__"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout", "_FOSSIL_", "*.sos.zip"], "ignoresWhitelist": []})  # line 25
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
            upgraded = []  # type: List[str]  # line 86
            if repo["version"] < "2018.1210.3028":  # For older versions, see https://pypi.python.org/simple/sos-vcs/  # line 87
                branches[:] = [branch + ([[]] if len(branch) < 6 else []) for branch in branches]  # add untracking information  # line 88
                upgraded.append("2018.1210.3028")  # line 89
            if "format" not in repo:  # must be pre-1.4  # line 90
                repo["format"] = 1  # 1.4+  # line 91
                branches[:] = [branch + [None] for branch in branches]  # adds empty branching point information  # line 92
                upgraded.append("1.4")  # line 93
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 94
            _.repoConf = config  # line 95
            if upgraded:  # line 96
                for upgrade in upgraded:  # line 97
                    warn("!!! Upgraded repository metadata to match SOS version %r" % upgrade)  # line 97
                warn("To undo upgrade%s, restore metadata *now* from '%s/%s'" % ("s" if len(upgraded) > 1 else "", metaFolder, metaBack))  # line 98
                _.saveBranches()  # line 99
        except Exception as E:  # if not found, create metadata folder  # line 100
            _.branches = {}  # line 101
            _.track, _.picky, _.strict, _.compress, _.version = [defaults[k] for k in ["track", "picky", "strict", "compress"]] + [version.__version__]  # line 102
            (debug if offline else warn)("Couldn't read branches metadata: %r" % E)  # line 103

    def saveBranches(_, also: 'Dict[str, Any]'={}):  # line 105
        ''' Save list of branches and current branch info to metadata file. '''  # line 106
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # line 107
        with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "w", encoding=UTF8) as fd:  # line 108
            store = {"format": 1, "version": _.version, "tags": _.tags, "branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress}  # type: Dict[str, Any]  # line 109
            store.update(also)  # allows overriding certain values at certain points in time  # line 110
            json.dump((store, list(_.branches.values()), _.repoConf), fd, ensure_ascii=False)  # stores using unicode codepoints, fd knows how to encode them  # line 111

    def getRevisionByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 113
        ''' Convenience accessor for named revisions (using commit message as name as a convention). '''  # line 114
        if name == "":  # line 115
            return -1  # line 115
        try:  # attempt to parse integer string  # line 116
            return int(name)  # attempt to parse integer string  # line 116
        except ValueError:  # line 117
            pass  # line 117
        found = [number for number, commit in _.commits.items() if name == commit.message]  # find any revision by commit message (usually used for tags)  # HINT allows finding any message, not only tagged ones  # line 118
        return found[0] if found else None  # line 119

    def getBranchByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 121
        ''' Convenience accessor for named branches. '''  # line 122
        if name == "":  # current  # line 123
            return _.branch  # current  # line 123
        try:  # attempt to parse integer string  # line 124
            return int(name)  # attempt to parse integer string  # line 124
        except ValueError:  # line 125
            pass  # line 125
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 126
        return found[0] if found else None  # line 127

    def loadBranch(_, branch: 'int'):  # line 129
        ''' Load all commit information from a branch meta data file. '''  # line 130
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "r", encoding=UTF8) as fd:  # line 131
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 132
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 133
        _.branch = branch  # line 134

    def saveBranch(_, branch: 'int'):  # line 136
        ''' Save all commit information to a branch meta data file. '''  # line 137
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # line 138
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "w", encoding=UTF8) as fd:  # line 139
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 140

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'):  # line 142
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 147
        debug("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 148
        tracked = [t for t in _.branches[_.branch].tracked]  # type: List[str]  # copy  # line 149
        untracked = [u for u in _.branches[_.branch].untracked]  # type: List[str]  # line 150
        os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 151
        _.loadBranch(_.branch)  # line 152
        revision = max(_.commits)  # type: int  # line 153
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 154
        for path, pinfo in _.paths.items():  # line 155
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 156
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 157
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 158
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 159
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].inSync, tracked, untracked)  # save branch info, before storing repo state at caller  # line 160

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 162
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 167
        simpleMode = not (_.track or _.picky)  # line 168
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # in case of initial branch creation  # line 169
        untracked = [t for t in _.branches[_.branch].untracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # line 170
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 171
        _.paths = {}  # type: Dict[str, PathInfo]  # line 172
        if simpleMode:  # branches from file system state  # line 173
            changes, msg = _.findChanges(branch, 0, progress=simpleMode)  # creates revision folder and versioned files  # line 174
            _.listChanges(changes)  # line 175
            if msg:  # display compression factor  # line 176
                printo(msg)  # display compression factor  # line 176
            _.paths.update(changes.additions.items())  # line 177
        else:  # tracking or picky mode: branch from latest revision  # line 178
            os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 179
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 180
                _.loadBranch(_.branch)  # line 181
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 182
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 183
                for path, pinfo in _.paths.items():  # line 184
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 185
        ts = int(time.time() * 1000)  # line 186
        _.commits = {0: CommitInfo(0, ts, ("Branched on %s" % strftime(ts) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 187
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 188
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 189
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked, untracked)  # save branch info, in case it is needed  # line 190

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 192
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 193
        shutil.rmtree(encode(os.path.join(_.root, metaFolder, "b%d" % branch)))  # TODO put into recycle bin, under ./sos?  # line 194
        binfo = _.branches[branch]  # line 195
        del _.branches[branch]  # line 196
        _.branch = max(_.branches)  # line 197
        _.saveBranches()  # line 198
        _.commits.clear()  # line 199
        return binfo  # line 200

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 202
        ''' Load all file information from a commit meta data. '''  # line 203
        with codecs.open(encode(branchFolder(branch, revision, base=_.root, file=metaFile)), "r", encoding=UTF8) as fd:  # line 204
            _.paths = json.load(fd)  # line 205
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 206
        _.branch = branch  # line 207

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 209
        ''' Save all file information to a commit meta data file. '''  # line 210
        target = branchFolder(branch, revision, base=_.root)  # type: str  # line 211
        try:  # line 212
            os.makedirs(encode(target))  # line 212
        except:  # line 213
            pass  # line 213
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(target, metaFile)), encode(os.path.join(target, metaBack))))  # line 214
        with codecs.open(encode(os.path.join(target, metaFile)), "w", encoding=UTF8) as fd:  # line 215
            json.dump(_.paths, fd, ensure_ascii=False)  # line 216

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'Tuple[ChangeSet, _coconut.typing.Optional[str]]':  # line 218
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes (always overrides considerOnly)
        progress: Show file names during processing
        returns: (ChangeSet = the state of file tree *differences*, unless "inverse" is True -> then return original data, message)
    '''  # line 227
        write = branch is not None and revision is not None  # line 228
        if write:  # line 229
            try:  # line 230
                os.makedirs(encode(branchFolder(branch, revision, base=_.root)))  # line 230
            except FileExistsError:  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 231
                pass  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 231
        changes = ChangeSet({}, {}, {}, {})  # type: ChangeSet  # TODO Needs explicity initialization due to mypy problems with default arguments :-(  # line 232
        indicator = ProgressIndicator() if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # optional file list progress indicator  # line 233
        hashed = None  # type: _coconut.typing.Optional[str]  # line 234
        written = None  # type: int  # line 234
        compressed = 0  # type: int  # line 234
        original = 0  # type: int  # line 234
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 235
        for path, pinfo in _.paths.items():  # line 236
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 237
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 240
        for path, dirnames, filenames in os.walk(_.root):  # line 241
            path = decode(path)  # line 242
            dirnames[:] = [decode(d) for d in dirnames]  # line 243
            filenames[:] = [decode(f) for f in filenames]  # line 244
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 245
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 246
            dirnames.sort()  # line 247
            filenames.sort()  # line 247
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 248
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 249
            if dontConsider:  # line 250
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 251
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 252
                filename = relPath + SLASH + file  # line 253
                filepath = os.path.join(path, file)  # line 254
                try:  # line 255
                    stat = os.stat(encode(filepath))  # line 255
                except Exception as E:  # line 256
                    exception(E)  # line 256
                    continue  # line 256
                size, mtime = stat.st_size, int(stat.st_mtime * 1000)  # line 257
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 258
                if show:  # indication character returned  # line 259
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", show, filename)  # line 260
                    printo(outstring + " " * max(0, termWidth - len(outstring)), nl="")  # line 261
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 262
                    nameHash = hashStr(filename)  # line 263
                    try:  # line 264
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 265
                        changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 266
                        compressed += written  # line 267
                        original += size  # line 267
                    except Exception as E:  # line 268
                        exception(E)  # line 268
                    continue  # with next file  # line 269
                last = _.paths[filename]  # filename is known - check for modifications  # line 270
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 271
                    try:  # line 272
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 273
                        changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 274
                        continue  # line 274
                    except Exception as E:  # line 275
                        exception(E)  # line 275
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and tryOrDefault(lambda: (hashFile(filepath, _.compress)[0] != last.hash), default=False)):  # detected a modification TODO wrap hashFile exception  # line 276
                    try:  # line 277
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 278
                        changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 279
                    except Exception as E:  # line 280
                        exception(E)  # line 280
                else:  # with next file  # line 281
                    continue  # with next file  # line 281
                compressed += written  # line 282
                original += last.size if inverse else size  # line 282
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 283
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 283
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 284
            for file in names:  # line 285
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 286
                    continue  # don't mark ignored files as deleted  # line 286
                pth = path + SLASH + file  # type: str  # line 287
                changes.deletions[pth] = _.paths[pth]  # line 288
        for path, info in changes.additions.items():  # line 289
            for dpath, dinfo in changes.deletions.items():  # line 290
                if info.size == dinfo.size and info.mtime == dinfo.mtime and info.hash == dinfo.hash:  # was moved TODO check either mtime or hash?  # line 291
                    changes.moves[path] = (dpath, info)  # store new data and original name, but don't remove add/del  # line 292
                    break  # deletions loop, continue with next addition  # line 293
        if progress:  # forces clean line of progress output  # line 294
            printo("\r" + " " * termWidth + "\r", nl="")  # forces clean line of progress output  # line 294
        else:  # line 295
            debug("Finished detecting changes")  # line 295
        return (changes, ("Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else None)  # line 296

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 298
        ''' Returns nothing, just updates _.paths in place. '''  # line 299
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 300

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 302
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 303
        _.loadCommit(branch, 0)  # load initial paths  # line 304
        if incrementally:  # line 305
            yield _.paths  # line 305
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 306
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 306
        for rev in range(1, revision + 1):  # line 307
            m.loadCommit(branch, rev)  # line 308
            for p, info in m.paths.items():  # line 309
                if info.size == None:  # line 310
                    del _.paths[p]  # line 310
                else:  # line 311
                    _.paths[p] = info  # line 311
            if incrementally:  # line 312
                yield _.paths  # line 312
        yield None  # for the default case - not incrementally  # line 313

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 315
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 318
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 319
            return (_.branch, -1)  # no branch/revision specified  # line 319
        argument = argument.strip()  # line 320
        if argument.startswith(SLASH):  # current branch  # line 321
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 321
        if argument.endswith(SLASH):  # line 322
            try:  # line 323
                return (_.getBranchByName(argument[:-1]), -1)  # line 323
            except ValueError:  # line 324
                Exit("Unknown branch label '%s'" % argument)  # line 324
        if SLASH in argument:  # line 325
            b, r = argument.split(SLASH)[:2]  # line 326
            try:  # line 327
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 327
            except ValueError:  # line 328
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 328
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 329
        if branch not in _.branches:  # line 330
            branch = None  # line 330
        try:  # either branch name/number or reverse/absolute revision number  # line 331
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 331
        except:  # line 332
            Exit("Unknown branch label or wrong number format")  # line 332
        Exit("This should never happen. Please create a issue report")  # line 333
        return (None, None)  # line 333

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 335
        while True:  # find latest revision that contained the file physically  # line 336
            source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 337
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 338
                break  # line 338
            revision -= 1  # line 339
            if revision < 0:  # line 340
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 340
        return revision, source  # line 341

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 343
        ''' Copy versioned file to other branch/revision. '''  # line 344
        target = branchFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 345
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 346
        shutil.copy2(encode(source), encode(target))  # line 347

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 349
        ''' Return file contents, or copy contents into file path provided. '''  # line 350
        source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 351
        try:  # line 352
            with openIt(source, "r", _.compress) as fd:  # line 353
                if toFile is None:  # read bytes into memory and return  # line 354
                    return fd.read()  # read bytes into memory and return  # line 354
                with open(encode(toFile), "wb") as to:  # line 355
                    while True:  # line 356
                        buffer = fd.read(bufSize)  # line 357
                        to.write(buffer)  # line 358
                        if len(buffer) < bufSize:  # line 359
                            break  # line 359
                    return None  # line 360
        except Exception as E:  # line 361
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 361
        return None  # line 362

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 364
        ''' Recreate file for given revision, or return binary contents if path is None. '''  # line 365
        if relPath is None:  # just return contents  # line 366
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 366
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 367
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 368
            try:  # line 369
                os.makedirs(encode(os.path.dirname(target)))  # line 369
            except:  # line 370
                pass  # line 370
        if pinfo.size == 0:  # line 371
            with open(encode(target), "wb"):  # line 372
                pass  # line 372
            try:  # update access/modification timestamps on file system  # line 373
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 373
            except Exception as E:  # line 374
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 374
            return None  # line 375
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 376
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 378
            while True:  # line 379
                buffer = fd.read(bufSize)  # line 380
                to.write(buffer)  # line 381
                if len(buffer) < bufSize:  # line 382
                    break  # line 382
        try:  # update access/modification timestamps on file system  # line 383
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 383
        except Exception as E:  # line 384
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 384
        return None  # line 385

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None, negative: 'bool'=False) -> 'FrozenSet[str]':  # line 387
        ''' Returns list of tracking patterns (or untracking patterns if negative) for provided branch or current branch. '''  # line 388
        return _coconut.frozenset() if not (_.track or _.picky) else frozenset(_.branches[(_.branch if branch is None else branch)].untracked if negative else _.branches[(_.branch if branch is None else branch)].tracked)  # line 389


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 393
    ''' Initial command to start working offline. '''  # line 394
    if os.path.exists(encode(metaFolder)):  # line 395
        if '--force' not in options:  # line 396
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 396
        try:  # line 397
            for entry in os.listdir(metaFolder):  # line 398
                resource = metaFolder + os.sep + entry  # line 399
                if os.path.isdir(resource):  # line 400
                    shutil.rmtree(encode(resource))  # line 400
                else:  # line 401
                    os.unlink(encode(resource))  # line 401
        except:  # line 402
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 402
    m = Metadata(offline=True)  # type: Metadata  # line 403
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 404
        m.compress = True  # plain file copies instead of compressed ones  # line 404
    if '--picky' in options or m.c.picky:  # Git-like  # line 405
        m.picky = True  # Git-like  # line 405
    elif '--track' in options or m.c.track:  # Svn-like  # line 406
        m.track = True  # Svn-like  # line 406
    if '--strict' in options or m.c.strict:  # always hash contents  # line 407
        m.strict = True  # always hash contents  # line 407
    debug(MARKER + "Going offline...")  # line 408
    m.createBranch(0, (defaults["defaultbranch"] if argument is None else argument), initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 409
    m.branch = 0  # line 410
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 411
    info(MARKER + "Offline repository prepared. Use 'sos online' to finish offline work")  # line 412

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 414
    ''' Finish working offline. '''  # line 415
    debug(MARKER + "Going back online...")  # line 416
    force = '--force' in options  # type: bool  # line 417
    m = Metadata()  # type: Metadata  # line 418
    m.loadBranches()  # line 419
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 420
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 420
    strict = '--strict' in options or m.strict  # type: bool  # line 421
    if options.count("--force") < 2:  # line 422
        changes, msg = m.findChanges(checkContent=strict, considerOnly=None if not (m.track or m.picky) else m.getTrackingPatterns(), dontConsider=None if not (m.track or m.picky) else m.getTrackingPatterns(negative=True), progress='--progress' in options)  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 423
        if modified(changes):  # line 424
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 428
    try:  # line 429
        shutil.rmtree(encode(metaFolder))  # line 429
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 429
    except Exception as E:  # line 430
        Exit("Error removing offline repository: %r" % E)  # line 430
    info(MARKER + "Offline repository removed, you're back online")  # line 431

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 433
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 434
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 435
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 436
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 437
    m = Metadata()  # type: Metadata  # line 438
    m.loadBranch(m.branch)  # line 439
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 440
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 440
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 441
    debug(MARKER + "Branching to %sbranch b%02d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 442
    if last:  # branch from branch's last revision  # line 443
        m.duplicateBranch(branch, (("" if argument is None else argument)) + " (Branched from r%02d/b%02d)" % (m.branch, max(m.commits.keys())))  # branch from branch's last revision  # line 443
    else:  #  branch from current file tree state  # line 444
        m.createBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  #  branch from current file tree state  # line 444
    if not stay:  # line 445
        m.branch = branch  # line 446
        m.saveBranches()  # line 447
    info(MARKER + "%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 448

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 450
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 451
    if '--repo' in options:  # line 452
        status(options, onlys, excps)  # line 452
        return  # line 452
    m = Metadata()  # type: Metadata  # line 453
    branch = None  # type: _coconut.typing.Optional[int]  # line 453
    revision = None  # type: _coconut.typing.Optional[int]  # line 453
    strict = '--strict' in options or m.strict  # type: bool  # line 454
    branch, revision = m.parseRevisionString(argument)  # line 455
    if branch not in m.branches:  # line 456
        Exit("Unknown branch")  # line 456
    m.loadBranch(branch)  # knows commits  # line 457
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 458
    if revision < 0 or revision > max(m.commits):  # line 459
        Exit("Unknown revision r%02d" % revision)  # line 459
    debug(MARKER + "Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 460
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 461
    changes, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 462
    m.listChanges(changes)  # line 467
    return changes  # for unit tests only TODO remove  # line 468

def _diff(m: 'Metadata', branch: 'int', revision: 'int', changes: 'ChangeSet'):  # TODO introduce option to diff against committed revision  # line 470
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 471
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 472
    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 473
        content = None  # type: _coconut.typing.Optional[bytes]  # line 474
        if pinfo.size == 0:  # empty file contents  # line 475
            content = b""  # empty file contents  # line 475
        else:  # versioned file  # line 476
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 476
            assert content is not None  # versioned file  # line 476
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 477
        blocks = None  # type: List[MergeBlock]  # line 478
        nl = None  # type: bytes  # line 478
        blocks, nl = merge(filename=abspath, into=content, diffOnly=True)  # only determine change blocks  # line 479
        printo("DIF %s%s  %s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else "", NL_NAMES[nl]))  # line 480
        for block in blocks:  # line 481
#      if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:
#        pass  # TODO print some previous and following lines - which aren't accessible here anymore
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 484
                for no, line in enumerate(block.lines):  # line 485
                    printo("--- %04d |%s|" % (no + block.line, line))  # line 486
            elif block.tipe == MergeBlockType.REMOVE:  # line 487
                for no, line in enumerate(block.lines):  # line 488
                    printo("+++ %04d |%s|" % (no + block.line, line))  # line 489
            elif block.tipe == MergeBlockType.REPLACE:  # TODO for MODIFY also show intra-line change ranges (TODO remove if that code was also removed)  # line 490
                for no, line in enumerate(block.replaces.lines):  # line 491
                    printo("- | %04d |%s|" % (no + block.replaces.line, line))  # line 492
                for no, line in enumerate(block.lines):  # line 493
                    printo("+ | %04d |%s|" % (no + block.line, line))  # line 494
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 498
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 499
    m = Metadata()  # type: Metadata  # line 500
    branch = None  # type: _coconut.typing.Optional[int]  # line 500
    revision = None  # type: _coconut.typing.Optional[int]  # line 500
    strict = '--strict' in options or m.strict  # type: bool  # line 501
    _from = {None: option.split("--from=")[1] for option in options if option.startswith("--from=")}.get(None, None)  # type: _coconut.typing.Optional[str]  # TODO implement  # line 502
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 503
    if branch not in m.branches:  # line 504
        Exit("Unknown branch")  # line 504
    m.loadBranch(branch)  # knows commits  # line 505
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 506
    if revision < 0 or revision > max(m.commits):  # line 507
        Exit("Unknown revision r%02d" % revision)  # line 507
    debug(MARKER + "Textual differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 508
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 509
    changes, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 510
    _diff(m, branch, revision, changes)  # line 515

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 517
    ''' Create new revision from file tree changes vs. last commit. '''  # line 518
    m = Metadata()  # type: Metadata  # line 519
    if argument is not None and argument in m.tags:  # line 520
        Exit("Illegal commit message. It was already used as a tag name")  # line 520
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 521
# No untracking patterns needed here
    if m.picky and not trackingPatterns:  # line 523
        Exit("No file patterns staged for commit in picky mode")  # line 523
    debug((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 524
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options, check=False, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but aborts if no changes  # line 525
    m.paths = changes.additions  # line 526
    m.paths.update(changes.modifications)  # update pathset to changeset only  # line 527
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changes.deletions.items()})  # line 528
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 529
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 530
    m.saveBranch(m.branch)  # line 531
    m.loadBranches()  # TODO is it necessary to load again?  # line 532
    if m.picky:  # remove tracked patterns  # line 533
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 533
    else:  # track or simple mode: set branch dirty  # line 534
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 534
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 535
        m.tags.append(argument)  # memorize unique tag  # line 535
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 535
    m.saveBranches()  # line 536
    info(MARKER + "Created new revision r%02d%s (+%02d/-%02d/\u00b1%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications), len(changes.moves)))  # line 537

def status(options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 539
    ''' Show branches and current repository state. '''  # line 540
    m = Metadata()  # type: Metadata  # line 541
    current = m.branch  # type: int  # line 542
    strict = '--strict' in options or m.strict  # type: bool  # line 543
    info(MARKER + "Offline repository status")  # line 544
    info("Installation path:   %s" % os.path.abspath(os.path.dirname(__file__)))  # line 545
    info("Current SOS version: %s" % version.__version__)  # line 546
    info("At creation version: %s" % m.version)  # line 547
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 548
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 549
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 550
    info("Number of branches:  %d" % len(m.branches))  # line 551
#  info("Revisions:           %d" % sum([]))
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 553
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 554
    m.loadBranch(m.branch)  # line 555
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 508  # line 556
    changes, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress=True)  # line 557
    printo("File tree %s" % ("has changes vs. last revision of current branch" if modified(changes) else "is unchanged"))  # line 562
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 563
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 564
        m.loadBranch(branch.number)  # knows commit history  # line 565
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 566
    if m.track or m.picky and (len(m.branches[m.branch].tracked) > 0 or len(m.branches[m.branch].untracked) > 0):  # line 567
        info("\nTracked file patterns:")  # TODO print matching untracking patterns side-by-side  # line 568
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 569
        info("\nUntracked file patterns:")  # line 570
        printo(ajoin("  | ", m.branches[m.branch].untracked, "\n"))  # line 571

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str], FrozenSet[str]]':  # line 573
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags.
  '''  # line 579
    assert not (check and commit)  # line 580
    m = Metadata()  # type: Metadata  # line 581
    force = '--force' in options  # type: bool  # line 582
    strict = '--strict' in options or m.strict  # type: bool  # line 583
    if argument is not None:  # line 584
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 585
        if branch is None:  # line 586
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 586
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 587

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 590
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 591
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 592
    changes, msg = m.findChanges(m.branch if commit else None, max(m.commits) + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress='--progress' in options)  # line 593
    if check and modified(changes) and not force:  # line 598
        m.listChanges(changes)  # line 599
        Exit("File tree contains changes. Use --force to proceed")  # line 600
    elif commit:  # line 601
        if not modified(changes) and not force:  # line 602
            Exit("Nothing to commit")  # line 602
        m.listChanges(changes)  # line 603
        if msg:  # line 604
            printo(msg)  # line 604

    if argument is not None:  # branch/revision specified  # line 606
        m.loadBranch(branch)  # knows commits of target branch  # line 607
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 608
        if revision < 0 or revision > max(m.commits):  # line 609
            Exit("Unknown revision r%02d" % revision)  # line 609
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch), m.getTrackingPatterns(branch, negative=True))  # line 610
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns, untrackingPatterns)  # line 611

def switch(argument: 'str', options: 'List[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 613
    ''' Continue work on another branch, replacing file tree changes. '''  # line 614
    m, branch, revision, changes, strict, _force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, ["--force"] + options)  # line 615
    force = '--force' in options  # type: bool  # needed as we fake force in above access  # line 616

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 619
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked, untracked=m.branches[branch].untracked)  # line 620
    else:  # full file switch  # line 621
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 622
        todos, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((untrackingPatterns | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 623

# Now check for potential conflicts
        changes.deletions.clear()  # local deletions never create conflicts, modifications always  # line 630
        rms = []  # type: _coconut.typing.Sequence[str]  # local additions can be ignored if restoration from switch would be same  # line 631
        for a, pinfo in changes.additions.items():  # has potential corresponding re-add in switch operation:  # line 632
            if a in todos.deletions and pinfo.size == todos.deletions[a].size and (pinfo.hash == todos.deletions[a].hash if m.strict else pinfo.mtime == todos.deletions[a].mtime):  # line 633
                rms.append(a)  # line 633
        for rm in rms:  # TODO could also silently accept remote DEL for local ADD  # line 634
            del changes.additions[rm]  # TODO could also silently accept remote DEL for local ADD  # line 634
        if modified(changes) and not force:  # line 635
            m.listChanges(changes)  # line 635
            Exit("File tree contains changes. Use --force to proceed")  # line 635
        debug(MARKER + "Switching to branch %sb%02d/r%02d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 636
        if not modified(todos):  # line 637
            info("No changes to current file tree")  # line 638
        else:  # integration required  # line 639
            for path, pinfo in todos.deletions.items():  # line 640
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 641
                printo("ADD " + path)  # line 642
            for path, pinfo in todos.additions.items():  # line 643
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 644
                printo("DEL " + path)  # line 645
            for path, pinfo in todos.modifications.items():  # line 646
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 647
                printo("MOD " + path)  # line 648
    m.branch = branch  # line 649
    m.saveBranches()  # store switched path info  # line 650
    info(MARKER + "Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 651

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 653
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 657
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 658
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 659
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 660
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 661
    m = Metadata()  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 662
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 663
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 664
    debug(MARKER + "Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 665

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 668
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 669
    untrackingUnion = untrackingPatterns | m.getTrackingPatterns(branch, negative=True)  # type: FrozenSet[str]  # line 670
    changes, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingUnion), dontConsider=excps if not (m.track or m.picky) else (untrackingUnion if onlys is None else onlys), progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 671
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 676
        if trackingUnion != trackingPatterns:  # nothing added  # line 677
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 678
        else:  # line 679
            info("Nothing to update")  # but write back updated branch info below  # line 680
    else:  # integration required  # line 681
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 682
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 683
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 683
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 684
        for path, pinfo in changes.additions.items():  # line 685
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 686
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 686
            if mrg.value & MergeOperation.REMOVE.value:  # line 687
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 687
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 688
        for path, pinfo in changes.modifications.items():  # line 689
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 690
            binary = not m.isTextType(path)  # type: bool  # line 691
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 692
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 693
                printo(("MOD " if not binary else "BIN ") + path)  # line 694
                while True:  # line 695
                    printo(into)  # TODO print mtime, size differences?  # line 696
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 697
                    if op in ("it" if binary else "itm"):  # line 698
                        break  # line 698
            if op == "t":  # line 699
                printo("THR " + path)  # blockwise copy of contents  # line 700
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 700
            elif op == "m":  # line 701
                current = None  # type: bytes  # line 702
                with open(encode(into), "rb") as fd:  # TODO slurps file  # line 703
                    current = fd.read()  # TODO slurps file  # line 703
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 704
                if current == file:  # line 705
                    debug("No difference to versioned file")  # line 705
                elif file is not None:  # if None, error message was already logged  # line 706
                    contents = None  # type: bytes  # line 707
                    nl = None  # type: bytes  # line 707
                    contents, nl = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # line 708
                    if contents != current:  # line 709
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 710
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 710
                    else:  # TODO but update timestamp?  # line 711
                        debug("No change")  # TODO but update timestamp?  # line 711
            else:  # mine or wrong input  # line 712
                printo("MNE " + path)  # nothing to do! same as skip  # line 713
    info(MARKER + "Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 714
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 715
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 716
    m.saveBranches()  # line 717

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 719
    ''' Remove a branch entirely. '''  # line 720
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options)  # line 721
    if len(m.branches) == 1:  # line 722
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 722
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 723
    if branch is None or branch not in m.branches:  # line 724
        Exit("Cannot delete unknown branch %r" % branch)  # line 724
    debug(MARKER + "Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 725
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 726
    info(MARKER + "Branch b%02d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 727

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[], negative: 'bool'=False):  # line 729
    ''' Add a tracked files pattern to current branch's tracked files. negative means tracking blacklisting. '''  # line 730
    force = '--force' in options  # type: bool  # line 731
    m = Metadata()  # type: Metadata  # line 732
    if not (m.track or m.picky):  # line 733
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 733
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 734
    if pattern in patterns:  # line 735
        Exit("Pattern '%s' already tracked" % pattern)  # line 735
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 736
        Exit("The pattern folder doesn't exist. Use --force to add the file pattern anyway")  # line 736
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 737
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 738
    patterns.append(pattern)  # line 739
    m.saveBranches()  # line 740
    info(MARKER + "Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 741

def remove(relPath: 'str', pattern: 'str', negative: 'bool'=False):  # line 743
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 744
    m = Metadata()  # type: Metadata  # line 745
    if not (m.track or m.picky):  # line 746
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 746
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 747
    if pattern not in patterns:  # line 748
        suggestion = _coconut.set()  # type: Set[str]  # line 749
        for pat in patterns:  # line 750
            if fnmatch.fnmatch(pattern, pat):  # line 751
                suggestion.add(pat)  # line 751
        if suggestion:  # TODO use same wording as in move  # line 752
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 752
        Exit("Tracked pattern '%s' not found" % pattern)  # line 753
    patterns.remove(pattern)  # line 754
    m.saveBranches()  # line 755
    info(MARKER + "Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 756

def ls(folder: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 758
    ''' List specified directory, augmenting with repository metadata. '''  # line 759
    folder = (os.getcwd() if folder is None else folder)  # line 760
    m = Metadata()  # type: Metadata  # line 761
    debug(MARKER + "Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 762
    relPath = relativize(m.root, os.path.join(folder, "-"))[0]  # type: str  # line 763
    if relPath.startswith(".."):  # line 764
        Exit("Cannot list contents of folder outside offline repository")  # line 764
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 765
    untrackingPatterns = m.getTrackingPatterns(negative=True) if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 766
    if '--tags' in options:  # line 767
        printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 768
        return  # line 769
    if '--patterns' in options:  # line 770
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 771
        if out:  # line 772
            printo(out)  # line 772
        return  # line 773
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 774
    printo("DIR %s" % relPath)  # line 775
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 776
        ignore = None  # type: _coconut.typing.Optional[str]  # line 777
        for ig in m.c.ignores:  # line 778
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 779
                ignore = ig  # remember first match  # line 779
                break  # remember first match  # line 779
        if ig:  # line 780
            for wl in m.c.ignoresWhitelist:  # line 781
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 782
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 782
                    break  # found a white list entry for ignored file, undo ignoring it  # line 782
        matches = []  # type: List[str]  # line 783
        if not ignore:  # line 784
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 785
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 786
                    matches.append(os.path.basename(pattern))  # line 786
        matches.sort(key=lambda element: len(element))  # line 787
        printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "\u00b7\u00b7\u00b7"), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 788

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 790
    ''' List previous commits on current branch. '''  # line 791
    m = Metadata()  # type: Metadata  # line 792
    m.loadBranch(m.branch)  # knows commit history  # line 793
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 794
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 795
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, max(m.commits))  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 796
    maxWidth = max([wcswidth((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) for commit in m.commits.values()])  # type: int  # line 797
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 798
    for no in range(max(m.commits) + 1):  # line 799
        commit = m.commits[no]  # type: CommitInfo  # line 800
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 801
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # side-effect: updates m.paths  # line 802
        _add = news - olds  # type: FrozenSet[str]  # line 803
        _del = olds - news  # type: FrozenSet[str]  # line 804
        _mod = frozenset([_ for _, info in nxts.items() if _ in m.paths and m.paths[_].size != info.size and (m.paths[_].hash != info.hash if m.strict else m.paths[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 805
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 806
        printo("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT) |%s|%s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)).ljust(maxWidth), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 807
        if '--changes' in options:  # TODO moves detection?  # line 808
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}, {}))  # TODO moves detection?  # line 808
        if '--diff' in options:  #  _diff(m, changes)  # needs from revision diff  # line 809
            pass  #  _diff(m, changes)  # needs from revision diff  # line 809
        olds = news  # line 810

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 812
    ''' Exported entire repository as archive for easy transfer. '''  # line 813
    debug(MARKER + "Dumping repository to archive...")  # line 814
    progress = '--progress' in options  # type: bool  # line 815
    import zipfile  # TODO display compression ratio (if any)  # line 816
    try:  # line 817
        import zlib  # line 817
        compression = zipfile.ZIP_DEFLATED  # line 817
    except:  # line 818
        compression = zipfile.ZIP_STORED  # line 818

    if argument is None:  # line 820
        Exit("Argument missing (target filename)")  # line 820
    argument = argument if "." in argument else argument + ".sos.zip"  # line 821
    if os.path.exists(encode(argument)):  # line 822
        try:  # line 823
            shutil.copy2(encode(argument), encode(argument + BACKUP_SUFFIX))  # line 823
        except Exception as E:  # line 824
            Exit("Error creating backup copy before dumping. Please resolve and retry. %r" % E)  # line 824
    with zipfile.ZipFile(argument, "w", compression) as _zip:  # line 825
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 826
        indicator = ProgressIndicator() if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 827
        totalsize = 0  # type: int  # line 828
        start_time = time.time()  # type: float  # line 829
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 830
            dirpath = decode(dirpath)  # line 831
            dirnames[:] = [decode(d) for d in dirnames]  # line 832
            filenames[:] = [decode(f) for f in filenames]  # line 833
            for filename in filenames:  # line 834
                abspath = os.path.join(dirpath, filename)  # type: str  # line 835
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 836
                totalsize += os.stat(encode(abspath)).st_size  # line 837
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 838
                if show:  # line 839
                    printo(("\rDumping %s @%.2f MiB/s %s" % (show, totalsize / (MEBI * (time.time() - start_time)), filename)).ljust(termWidth), nl="")  # line 839
                _zip.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 840
    info("\r" + (MARKER + "Finished dumping entire repository.").ljust(termWidth))  # clean line  # line 841

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 843
    command, key, value = (arguments + [None] * 2)[:3]  # line 844
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 845
        Exit("Unknown config command")  # line 845
    local = "--local" in options  # type: bool  # line 846
    m = Metadata()  # type: Metadata  # loads layered configuration as well. TODO warning if repo not exists  # line 847
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 848
    if command == "set":  # line 849
        if None in (key, value):  # line 850
            Exit("Key or value not specified")  # line 850
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 851
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 851
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 852
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 852
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 853
    elif command == "unset":  # line 854
        if key is None:  # line 855
            Exit("No key specified")  # line 855
        if key not in c.keys():  # HINT: Works on local configurations when used with --local  # line 856
            Exit("Unknown key")  # HINT: Works on local configurations when used with --local  # line 856
        del c[key]  # line 857
    elif command == "add":  # line 858
        if None in (key, value):  # line 859
            Exit("Key or value not specified")  # line 859
        if key not in CONFIGURABLE_LISTS:  # line 860
            Exit("Unsupported key %r" % key)  # line 860
        if key not in c.keys():  # prepare empty list, or copy from global, add new value below  # line 861
            c[key] = [_ for _ in c.__defaults[key]] if local else []  # prepare empty list, or copy from global, add new value below  # line 861
        elif value in c[key]:  # line 862
            Exit("Value already contained, nothing to do")  # line 862
        if ";" in value:  # line 863
            c[key].append(removePath(key, value))  # line 863
        else:  # line 864
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 864
    elif command == "rm":  # line 865
        if None in (key, value):  # line 866
            Exit("Key or value not specified")  # line 866
        if key not in c.keys():  # line 867
            Exit("Unknown key %r" % key)  # line 867
        if value not in c[key]:  # line 868
            Exit("Unknown value %r" % value)  # line 868
        c[key].remove(value)  # line 869
        if local and len(c[key]) == 0 and "--prune" in options:  # remove local enty, to fallback to global  # line 870
            del c[key]  # remove local enty, to fallback to global  # line 870
    else:  # Show or list  # line 871
        if key == "flags":  # list valid configuration items  # line 872
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 872
        elif key == "lists":  # line 873
            printo(", ".join(CONFIGURABLE_LISTS))  # line 873
        elif key == "texts":  # line 874
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 874
        else:  # line 875
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 876
            c = m.c  # always use full configuration chain  # line 877
            try:  # attempt single key  # line 878
                assert key is not None  # line 879
                c[key]  # line 879
                l = key in c.keys()  # type: bool  # line 880
                g = key in c.__defaults.keys()  # type: bool  # line 880
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 881
            except:  # normal value listing  # line 882
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 883
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 884
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 885
                for k, vt in sorted(vals.items()):  # line 886
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 886
                if len(c.keys()) == 0:  # line 887
                    info("No local configuration stored")  # line 887
                if len(c.__defaults.keys()) == 0:  # line 888
                    info("No global configuration stored")  # line 888
        return  # in case of list, no need to store anything  # line 889
    if local:  # saves changes of repoConfig  # line 890
        m.repoConf = c.__map  # saves changes of repoConfig  # line 890
        m.saveBranches()  # saves changes of repoConfig  # line 890
        Exit("OK", code=0)  # saves changes of repoConfig  # line 890
    else:  # global config  # line 891
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 892
        if f is None:  # line 893
            error("Error saving user configuration: %r" % h)  # line 893
        else:  # line 894
            Exit("OK", code=0)  # line 894

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[], negative: 'bool'=False):  # line 896
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique.
      for "mvnot" don't do any renaming (or do?)
  '''  # line 899
# TODO info(MARKER + TODO write tests for that
    force = '--force' in options  # type: bool  # line 901
    soft = '--soft' in options  # type: bool  # line 902
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 903
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 903
    m = Metadata()  # type: Metadata  # line 904
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 905
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 906
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 907
    if not matching and not force:  # line 908
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 908
    if not (m.track or m.picky):  # line 909
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 909
    if pattern not in patterns:  # list potential alternatives and exit  # line 910
        for tracked in (t for t in patterns if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 911
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 912
            if alternative:  # line 913
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 913
        if not (force or soft):  # line 914
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 914
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 915
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 916
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 917
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 921
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 922
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 922
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 923
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 924
    if len({st[1] for st in matches}) != len(matches):  # line 925
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 925
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 926
    if os.path.exists(encode(newRelPath)):  # line 927
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 928
        if exists and not (force or soft):  # line 929
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 929
    else:  # line 930
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 930
    if not soft:  # perform actual renaming  # line 931
        for (source, target) in matches:  # line 932
            try:  # line 933
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 933
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 934
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 934
    patterns[patterns.index(pattern)] = newPattern  # line 935
    m.saveBranches()  # line 936

def parse(root: 'str', cwd: 'str'):  # line 938
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm. '''  # line 939
    debug("Parsing command-line arguments...")  # line 940
    try:  # line 941
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 942
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: Union[List[str], str, None]  # line 943
        if len(arguments) == 0:  # line 944
            arguments = [None]  # line 944
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 945
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 946
        debug("Processing command %r with arguments %r and options %r." % (("" if command is None else command), arguments if arguments else "", options))  # line 947
        if command[:1] in "amr":  # line 948
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 948
        if command[:1] == "m":  # line 949
            if len(arguments) < 2:  # line 950
                Exit("Need a second file pattern argument as target for move or config command")  # line 950
            newRelPath, newPattern = relativize(root, os.path.join(cwd, options[0]))  # line 951
        if command[:1] == "a":  # also addnot  # line 952
            add(relPath, pattern, options, negative="n" in command)  # also addnot  # line 952
        elif command[:1] == "b":  # line 953
            branch(arguments[0], options)  # line 953
        elif command[:3] == "com":  # line 954
            commit(arguments[0], options, onlys, excps)  # line 954
        elif command[:2] == "ch":  # "changes" (legacy)  # line 955
            changes(arguments[0], options, onlys, excps)  # "changes" (legacy)  # line 955
        elif command[:2] == "ci":  # line 956
            commit(arguments[0], options, onlys, excps)  # line 956
        elif command[:3] == 'con':  # line 957
            config(arguments, options)  # line 957
        elif command[:2] == "de":  # line 958
            delete(arguments[0], options)  # line 958
        elif command[:2] == "di":  # line 959
            diff(arguments[0], options, onlys, excps)  # line 959
        elif command[:2] == "du":  # line 960
            dump(arguments[0], options)  # line 960
        elif command[:1] == "h":  # line 961
            usage(APPNAME, version.__version__)  # line 961
        elif command[:2] == "lo":  # line 962
            log(options)  # line 962
        elif command[:2] == "li":  # line 963
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 963
        elif command[:2] == "ls":  # TODO avoid and/or normalize root super paths (..)?  # line 964
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # TODO avoid and/or normalize root super paths (..)?  # line 964
        elif command[:1] == "m":  # also mvnot  # line 965
            move(relPath, pattern, newRelPath, newPattern, options[1:], negative="n" in command)  # also mvnot  # line 965
        elif command[:2] == "of":  # line 966
            offline(arguments[0], options)  # line 966
        elif command[:2] == "on":  # line 967
            online(options)  # line 967
        elif command[:1] == "r":  # also rmnot  # line 968
            remove(relPath, pattern, negative="n" in command)  # also rmnot  # line 968
        elif command[:2] == "st":  # line 969
            changes(arguments[0], options, onlys, excps)  # line 969
        elif command[:2] == "sw":  # line 970
            switch(arguments[0], options, onlys, excps)  # line 970
        elif command[:1] == "u":  # line 971
            update(arguments[0], options, onlys, excps)  # line 971
        elif command[:1] == "v":  # line 972
            usage(APPNAME, version.__version__, short=True)  # line 972
        else:  # line 973
            Exit("Unknown command '%s'" % command)  # line 973
        Exit(code=0)  # line 974
    except (Exception, RuntimeError) as E:  # line 975
        exception(E)  # line 976
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing.")  # line 977

def main():  # line 979
    global debug, info, warn, error  # line 980
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 981
    _log = Logger(logging.getLogger(__name__))  # line 982
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 982
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 983
        sys.argv.remove(option)  # clean up program arguments  # line 983
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 984
        usage(APPNAME, version.__version__)  # line 984
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 985
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 986
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 987
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 988
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in ["h", "v"]:  # in offline mode or just going offline TODO what about git config?  # line 989
        cwd = os.getcwd()  # line 990
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 991
        parse(root, cwd)  # line 992
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 993
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 994
        import subprocess  # only required in this section  # line 995
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 996
        inp = ""  # type: str  # line 997
        while True:  # line 998
            so, se = process.communicate(input=inp)  # line 999
            if process.returncode is not None:  # line 1000
                break  # line 1000
            inp = sys.stdin.read()  # line 1001
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 1002
            if root is None:  # line 1003
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 1003
            m = Metadata(root)  # type: Metadata  # line 1004
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 1005
            m.saveBranches()  # line 1006
    else:  # line 1007
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 1007


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 1011
level = logging.DEBUG if verbose else logging.INFO  # line 1012
force_sos = '--sos' in sys.argv  # type: bool  # line 1013
force_vcs = '--vcs' in sys.argv  # type: bool  # line 1014
_log = Logger(logging.getLogger(__name__))  # line 1015
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1015
if __name__ == '__main__':  # line 1016
    main()  # line 1016
