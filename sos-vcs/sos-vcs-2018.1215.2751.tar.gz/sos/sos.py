#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xf275fca

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
        _.version = None  # type: _coconut.typing.Optional[str]  # line 57
        _.format = None  # type: _coconut.typing.Optional[int]  # line 57
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
            _.track, _.picky, _.strict, _.compress, _.version, _.format = [repo.get(r, None) for r in ["track", "picky", "strict", "compress", "version", "format"]]  # line 85
            upgraded = []  # type: List[str]  # line 86
            if _.version is None:  # line 87
                _.version = version.__version__  # line 88
                upgraded.append("ancient")  # line 89
            if _.version < "2018.1210.3028":  # For older versions, see https://pypi.python.org/simple/sos-vcs/  # line 90
                branches[:] = [branch + [None] * (6 - len(branch)) for branch in branches]  # add untracking information  # line 91
                upgraded.append("2018.1210.3028")  # line 92
            if _.format is None:  # must be before 1.3.5+  # line 93
                _.format = METADATA_FORMAT  # marker for first metadata file format  # line 94
                branches[:] = [branch + [None] * (8 - len(branch)) for branch in branches]  # adds empty branching point information (branch/revision)  # line 95
                upgraded.append("1.3.5")  # line 96
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 97
            _.repoConf = config  # line 98
            if upgraded:  # line 99
                for upgrade in upgraded:  # line 100
                    warn("!!! Upgraded repository metadata to match SOS version %r" % upgrade)  # line 100
                warn("To revert the metadata upgrade%s, restore %s/%s from %s/%s NOW" % (metaFolder, metaFile, "s" if len(upgraded) > 1 else "", metaFolder, metaBack))  # line 101
                _.saveBranches()  # line 102
        except Exception as E:  # if not found, create metadata folder with default values  # line 103
            _.branches = {}  # line 104
            _.track, _.picky, _.strict, _.compress, _.version, _.format = [defaults[k] for k in ["track", "picky", "strict", "compress"]] + [version.__version__, METADATA_FORMAT]  # line 105
            (debug if offline else warn)("Couldn't read branches metadata: %r" % E)  # line 106

    def saveBranches(_, also: 'Dict[str, Any]'={}):  # line 108
        ''' Save list of branches and current branch info to metadata file. '''  # line 109
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # line 110
        with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "w", encoding=UTF8) as fd:  # line 111
            store = {"tags": _.tags, "branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress, "version": _.version, "format": METADATA_FORMAT}  # type: Dict[str, Any]  # line 112
            store.update(also)  # allows overriding certain values at certain points in time  # line 116
            json.dump((store, list(_.branches.values()), _.repoConf), fd, ensure_ascii=False)  # stores using unicode codepoints, fd knows how to encode them  # line 117

    def getRevisionByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 119
        ''' Convenience accessor for named revisions (using commit message as name as a convention). '''  # line 120
        if name == "":  # line 121
            return -1  # line 121
        try:  # attempt to parse integer string  # line 122
            return int(name)  # attempt to parse integer string  # line 122
        except ValueError:  # line 123
            pass  # line 123
        found = [number for number, commit in _.commits.items() if name == commit.message]  # find any revision by commit message (usually used for tags)  # HINT allows finding any message, not only tagged ones  # line 124
        return found[0] if found else None  # line 125

    def getBranchByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 127
        ''' Convenience accessor for named branches. '''  # line 128
        if name == "":  # current  # line 129
            return _.branch  # current  # line 129
        try:  # attempt to parse integer string  # line 130
            return int(name)  # attempt to parse integer string  # line 130
        except ValueError:  # line 131
            pass  # line 131
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 132
        return found[0] if found else None  # line 133

    def loadBranch(_, branch: 'int'):  # line 135
        ''' Load all commit information from a branch meta data file. '''  # line 136
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "r", encoding=UTF8) as fd:  # line 137
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 138
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 139
        _.branch = branch  # line 140

    def saveBranch(_, branch: 'int'):  # line 142
        ''' Save all commit information to a branch meta data file. '''  # line 143
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # line 144
        with codecs.open(encode(os.path.join(_.root, metaFolder, "b%d" % branch, metaFile)), "w", encoding=UTF8) as fd:  # line 145
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 146

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'):  # line 148
        ''' Create branch from an existing branch/revision. WARN: Caller must have loaded branches information.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch
    '''  # line 153
        debug("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 154
        tracked = [t for t in _.branches[_.branch].tracked]  # type: List[str]  # copy  # line 155
        untracked = [u for u in _.branches[_.branch].untracked]  # type: List[str]  # line 156
        os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 157
        _.loadBranch(_.branch)  # line 158
        revision = max(_.commits)  # type: int  # line 159
        _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 160
        for path, pinfo in _.paths.items():  # line 161
            _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 162
        _.commits = {0: CommitInfo(0, int(time.time() * 1000), "Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)))}  # store initial commit  # line 163
        _.saveBranch(branch)  # save branch meta data to branch folder  # line 164
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 165
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, _.branches[_.branch].inSync, tracked, untracked)  # save branch info, before storing repo state at caller  # line 166

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 168
        ''' Create a new branch from current file tree. This clears all known commits and modifies the file system.
        branch: target branch (should not exist yet)
        name: optional name of new branch
        _.branch: current branch, must exist already
    '''  # line 173
        simpleMode = not (_.track or _.picky)  # line 174
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # in case of initial branch creation  # line 175
        untracked = [t for t in _.branches[_.branch].untracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # line 176
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 177
        _.paths = {}  # type: Dict[str, PathInfo]  # line 178
        if simpleMode:  # branches from file system state  # line 179
            changes, msg = _.findChanges(branch, 0, progress=simpleMode)  # creates revision folder and versioned files  # line 180
            _.listChanges(changes)  # line 181
            if msg:  # display compression factor  # line 182
                printo(msg)  # display compression factor  # line 182
            _.paths.update(changes.additions.items())  # line 183
        else:  # tracking or picky mode: branch from latest revision  # line 184
            os.makedirs(encode(branchFolder(branch, 0, base=_.root)))  # line 185
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 186
                _.loadBranch(_.branch)  # line 187
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 188
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 189
                for path, pinfo in _.paths.items():  # line 190
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 191
        ts = int(time.time() * 1000)  # line 192
        _.commits = {0: CommitInfo(0, ts, ("Branched on %s" % strftime(ts) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 193
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 194
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 195
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked, untracked)  # save branch info, in case it is needed  # line 196

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 198
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 199
        shutil.rmtree(encode(os.path.join(_.root, metaFolder, "b%d" % branch)))  # TODO put into recycle bin, under ./sos?  # line 200
        binfo = _.branches[branch]  # line 201
        del _.branches[branch]  # line 202
        _.branch = max(_.branches)  # line 203
        _.saveBranches()  # line 204
        _.commits.clear()  # line 205
        return binfo  # line 206

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 208
        ''' Load all file information from a commit meta data; if branched from another branch before specified revision, load correct revision recursively. '''  # line 209
        other = _.branches[branch].parent  # type: _coconut.typing.Optional[int]  # reference to originating parent branch, or None  # line 210
        if other is not None and revision <= _.branches[branch].revision:  # need to load commit from other branch instead  # line 211
            while _.branches[other].parent is not None:  # line 212
                other = _.branches[other].parent  # line 212
            _branch = other  # line 213
        else:  # line 214
            _branch = branch  # line 214
        with codecs.open(encode(branchFolder(_branch, revision, base=_.root, file=metaFile)), "r", encoding=UTF8) as fd:  # line 215
            _.paths = json.load(fd)  # line 216
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 217
        _.branch = branch  # line 218

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 220
        ''' Save all file information to a commit meta data file. '''  # line 221
        target = branchFolder(branch, revision, base=_.root)  # type: str  # line 222
        try:  # line 223
            os.makedirs(encode(target))  # line 223
        except:  # line 224
            pass  # line 224
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(target, metaFile)), encode(os.path.join(target, metaBack))))  # line 225
        with codecs.open(encode(os.path.join(target, metaFile)), "w", encoding=UTF8) as fd:  # line 226
            json.dump(_.paths, fd, ensure_ascii=False)  # line 227

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'Tuple[ChangeSet, _coconut.typing.Optional[str]]':  # line 229
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes (always overrides considerOnly)
        progress: Show file names during processing
        returns: (ChangeSet = the state of file tree *differences*, unless "inverse" is True -> then return original data, message)
    '''  # line 238
        write = branch is not None and revision is not None  # line 239
        if write:  # line 240
            try:  # line 241
                os.makedirs(encode(branchFolder(branch, revision, base=_.root)))  # line 241
            except FileExistsError:  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 242
                pass  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 242
        changes = ChangeSet({}, {}, {}, {})  # type: ChangeSet  # TODO Needs explicity initialization due to mypy problems with default arguments :-(  # line 243
        indicator = ProgressIndicator() if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # optional file list progress indicator  # line 244
        hashed = None  # type: _coconut.typing.Optional[str]  # line 245
        written = None  # type: int  # line 245
        compressed = 0  # type: int  # line 245
        original = 0  # type: int  # line 245
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 246
        for path, pinfo in _.paths.items():  # line 247
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 248
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 251
        for path, dirnames, filenames in os.walk(_.root):  # line 252
            path = decode(path)  # line 253
            dirnames[:] = [decode(d) for d in dirnames]  # line 254
            filenames[:] = [decode(f) for f in filenames]  # line 255
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 256
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 257
            dirnames.sort()  # line 258
            filenames.sort()  # line 258
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 259
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 260
            if dontConsider:  # line 261
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 262
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 263
                filename = relPath + SLASH + file  # line 264
                filepath = os.path.join(path, file)  # line 265
                try:  # line 266
                    stat = os.stat(encode(filepath))  # line 266
                except Exception as E:  # line 267
                    exception(E)  # line 267
                    continue  # line 267
                size, mtime = stat.st_size, int(stat.st_mtime * 1000)  # line 268
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 269
                if show:  # indication character returned  # line 270
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", show, filename)  # line 271
                    printo(outstring + " " * max(0, termWidth - len(outstring)), nl="")  # line 272
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 273
                    nameHash = hashStr(filename)  # line 274
                    try:  # line 275
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 276
                        changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 277
                        compressed += written  # line 278
                        original += size  # line 278
                    except Exception as E:  # line 279
                        exception(E)  # line 279
                    continue  # with next file  # line 280
                last = _.paths[filename]  # filename is known - check for modifications  # line 281
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 282
                    try:  # line 283
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 284
                        changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 285
                        continue  # line 285
                    except Exception as E:  # line 286
                        exception(E)  # line 286
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and tryOrDefault(lambda: (hashFile(filepath, _.compress)[0] != last.hash), default=False)):  # detected a modification TODO wrap hashFile exception  # line 287
                    try:  # line 288
                        hashed, written = hashFile(filepath, _.compress, saveTo=branchFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 289
                        changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 290
                    except Exception as E:  # line 291
                        exception(E)  # line 291
                else:  # with next file  # line 292
                    continue  # with next file  # line 292
                compressed += written  # line 293
                original += last.size if inverse else size  # line 293
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 294
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 294
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 295
            for file in names:  # line 296
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 297
                    continue  # don't mark ignored files as deleted  # line 297
                pth = path + SLASH + file  # type: str  # line 298
                changes.deletions[pth] = _.paths[pth]  # line 299
        for path, info in changes.additions.items():  # line 300
            for dpath, dinfo in changes.deletions.items():  # line 301
                if info.size == dinfo.size and info.mtime == dinfo.mtime and info.hash == dinfo.hash:  # was moved TODO check either mtime or hash?  # line 302
                    changes.moves[path] = (dpath, info)  # store new data and original name, but don't remove add/del  # line 303
                    break  # deletions loop, continue with next addition  # line 304
        if progress:  # forces clean line of progress output  # line 305
            printo("\r" + " " * termWidth + "\r", nl="")  # forces clean line of progress output  # line 305
        else:  # line 306
            debug("Finished detecting changes")  # line 306
        return (changes, ("Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else None)  # line 307

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 309
        ''' Returns nothing, just updates _.paths in place. '''  # line 310
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 311

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 313
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 314
        _.loadCommit(branch, 0)  # load initial paths  # line 315
        if incrementally:  # line 316
            yield _.paths  # line 316
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 317
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 317
        for rev in range(1, revision + 1):  # line 318
            m.loadCommit(branch, rev)  # line 319
            for p, info in m.paths.items():  # line 320
                if info.size == None:  # line 321
                    del _.paths[p]  # line 321
                else:  # line 322
                    _.paths[p] = info  # line 322
            if incrementally:  # line 323
                yield _.paths  # line 323
        yield None  # for the default case - not incrementally  # line 324

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 326
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 329
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 330
            return (_.branch, -1)  # no branch/revision specified  # line 330
        argument = argument.strip()  # line 331
        if argument.startswith(SLASH):  # current branch  # line 332
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 332
        if argument.endswith(SLASH):  # line 333
            try:  # line 334
                return (_.getBranchByName(argument[:-1]), -1)  # line 334
            except ValueError:  # line 335
                Exit("Unknown branch label '%s'" % argument)  # line 335
        if SLASH in argument:  # line 336
            b, r = argument.split(SLASH)[:2]  # line 337
            try:  # line 338
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 338
            except ValueError:  # line 339
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 339
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 340
        if branch not in _.branches:  # line 341
            branch = None  # line 341
        try:  # either branch name/number or reverse/absolute revision number  # line 342
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 342
        except:  # line 343
            Exit("Unknown branch label or wrong number format")  # line 343
        Exit("This should never happen. Please create a issue report")  # line 344
        return (None, None)  # line 344

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 346
        while True:  # find latest revision that contained the file physically  # line 347
            source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 348
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 349
                break  # line 349
            revision -= 1  # line 350
            if revision < 0:  # line 351
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 351
        return revision, source  # line 352

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 354
        ''' Copy versioned file to other branch/revision. '''  # line 355
        target = branchFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 356
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 357
        shutil.copy2(encode(source), encode(target))  # line 358

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 360
        ''' Return file contents, or copy contents into file path provided. '''  # line 361
        source = branchFolder(branch, revision, base=_.root, file=nameHash)  # type: str  # line 362
        try:  # line 363
            with openIt(source, "r", _.compress) as fd:  # line 364
                if toFile is None:  # read bytes into memory and return  # line 365
                    return fd.read()  # read bytes into memory and return  # line 365
                with open(encode(toFile), "wb") as to:  # line 366
                    while True:  # line 367
                        buffer = fd.read(bufSize)  # line 368
                        to.write(buffer)  # line 369
                        if len(buffer) < bufSize:  # line 370
                            break  # line 370
                    return None  # line 371
        except Exception as E:  # line 372
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 372
        return None  # line 373

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 375
        ''' Recreate file for given revision, or return binary contents if path is None. '''  # line 376
        if relPath is None:  # just return contents  # line 377
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 377
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 378
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 379
            try:  # line 380
                os.makedirs(encode(os.path.dirname(target)))  # line 380
            except:  # line 381
                pass  # line 381
        if pinfo.size == 0:  # line 382
            with open(encode(target), "wb"):  # line 383
                pass  # line 383
            try:  # update access/modification timestamps on file system  # line 384
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 384
            except Exception as E:  # line 385
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 385
            return None  # line 386
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 387
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 389
            while True:  # line 390
                buffer = fd.read(bufSize)  # line 391
                to.write(buffer)  # line 392
                if len(buffer) < bufSize:  # line 393
                    break  # line 393
        try:  # update access/modification timestamps on file system  # line 394
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 394
        except Exception as E:  # line 395
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 395
        return None  # line 396

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None, negative: 'bool'=False) -> 'FrozenSet[str]':  # line 398
        ''' Returns list of tracking patterns (or untracking patterns if negative) for provided branch or current branch. '''  # line 399
        return _coconut.frozenset() if not (_.track or _.picky) else frozenset(_.branches[(_.branch if branch is None else branch)].untracked if negative else _.branches[(_.branch if branch is None else branch)].tracked)  # line 400


# Main client operations
def offline(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 404
    ''' Initial command to start working offline. '''  # line 405
    if os.path.exists(encode(metaFolder)):  # line 406
        if '--force' not in options:  # line 407
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 407
        try:  # line 408
            for entry in os.listdir(metaFolder):  # line 409
                resource = metaFolder + os.sep + entry  # line 410
                if os.path.isdir(resource):  # line 411
                    shutil.rmtree(encode(resource))  # line 411
                else:  # line 412
                    os.unlink(encode(resource))  # line 412
        except:  # line 413
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 413
    m = Metadata(offline=True)  # type: Metadata  # line 414
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 415
        m.compress = True  # plain file copies instead of compressed ones  # line 415
    if '--picky' in options or m.c.picky:  # Git-like  # line 416
        m.picky = True  # Git-like  # line 416
    elif '--track' in options or m.c.track:  # Svn-like  # line 417
        m.track = True  # Svn-like  # line 417
    if '--strict' in options or m.c.strict:  # always hash contents  # line 418
        m.strict = True  # always hash contents  # line 418
    debug(MARKER + "Going offline...")  # line 419
    m.createBranch(0, (defaults["defaultbranch"] if argument is None else argument), initialMessage="Offline repository created on %s" % strftime())  # main branch's name may be None (e.g. for fossil)  # line 420
    m.branch = 0  # line 421
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 422
    info(MARKER + "Offline repository prepared. Use 'sos online' to finish offline work")  # line 423

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 425
    ''' Finish working offline. '''  # line 426
    debug(MARKER + "Going back online...")  # line 427
    force = '--force' in options  # type: bool  # line 428
    m = Metadata()  # type: Metadata  # line 429
    m.loadBranches()  # line 430
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 431
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 431
    strict = '--strict' in options or m.strict  # type: bool  # line 432
    if options.count("--force") < 2:  # line 433
        changes, msg = m.findChanges(checkContent=strict, considerOnly=None if not (m.track or m.picky) else m.getTrackingPatterns(), dontConsider=None if not (m.track or m.picky) else m.getTrackingPatterns(negative=True), progress='--progress' in options)  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 434
        if modified(changes):  # line 435
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 439
    try:  # line 440
        shutil.rmtree(encode(metaFolder))  # line 440
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 440
    except Exception as E:  # line 441
        Exit("Error removing offline repository: %r" % E)  # line 441
    info(MARKER + "Offline repository removed, you're back online")  # line 442

def branch(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 444
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it. '''  # line 445
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 446
    stay = '--stay' in options  # type: bool  # continue on current branch after branching  # line 447
    force = '--force' in options  # type: bool  # branch even with local modifications  # line 448
    m = Metadata()  # type: Metadata  # line 449
    m.loadBranch(m.branch)  # line 450
    if argument and m.getBranchByName(argument) is not None:  # create a named branch  # line 451
        Exit("Branch '%s' already exists. Cannot proceed" % argument)  # create a named branch  # line 451
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 452
    debug(MARKER + "Branching to %sbranch b%02d%s%s..." % ("unnamed " if argument is None else "", branch, " '%s'" % argument if argument else "", " from last revision" if last else ""))  # line 453
    if last:  # branch from branch's last revision  # line 454
        m.duplicateBranch(branch, (("" if argument is None else argument)) + " (Branched from r%02d/b%02d)" % (m.branch, max(m.commits.keys())))  # branch from branch's last revision  # line 454
    else:  #  branch from current file tree state  # line 455
        m.createBranch(branch, ("Branched from r%02d/b%02d" % (m.branch, max(m.commits.keys())) if argument is None else argument))  #  branch from current file tree state  # line 455
    if not stay:  # line 456
        m.branch = branch  # line 457
        m.saveBranches()  # line 458
    info(MARKER + "%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if argument is None else "", branch, " '%s'" % argument if argument else ""))  # line 459

def changes(argument: 'str'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 461
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 462
    if '--repo' in options:  # line 463
        status(options, onlys, excps)  # line 463
        return  # line 463
    m = Metadata()  # type: Metadata  # line 464
    branch = None  # type: _coconut.typing.Optional[int]  # line 464
    revision = None  # type: _coconut.typing.Optional[int]  # line 464
    strict = '--strict' in options or m.strict  # type: bool  # line 465
    branch, revision = m.parseRevisionString(argument)  # line 466
    if branch not in m.branches:  # line 467
        Exit("Unknown branch")  # line 467
    m.loadBranch(branch)  # knows commits  # line 468
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 469
    if revision < 0 or revision > max(m.commits):  # line 470
        Exit("Unknown revision r%02d" % revision)  # line 470
    debug(MARKER + "Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 471
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 472
    changes, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 473
    m.listChanges(changes)  # line 478
    return changes  # for unit tests only TODO remove  # line 479

def _diff(m: 'Metadata', branch: 'int', revision: 'int', changes: 'ChangeSet', ignoreWhitespace: 'bool'):  # TODO introduce option to diff against committed revision  # line 481
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 482
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 483
    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 484
        content = None  # type: _coconut.typing.Optional[bytes]  # line 485
        if pinfo.size == 0:  # empty file contents  # line 486
            content = b""  # empty file contents  # line 486
        else:  # versioned file  # line 487
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 487
            assert content is not None  # versioned file  # line 487
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 488
        blocks = None  # type: List[MergeBlock]  # line 489
        nl = None  # type: bytes  # line 489
        blocks, nl = merge(filename=abspath, into=content, diffOnly=True, ignoreWhitespace=ignoreWhitespace)  # only determine change blocks  # line 490
        printo("DIF %s%s  %s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else "", NL_NAMES[nl]))  # line 491
        for block in blocks:  # line 492
            if block.tipe != MergeBlockType.KEEP:  # line 493
                printo()  # line 493
#      if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:
#        pass  # TODO print some previous and following lines - which aren't accessible here anymore
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 496
                for no, line in enumerate(block.lines):  # line 497
                    printo(("--- %04d |%s|" % (no + block.line, line))[:termWidth])  # line 497
            elif block.tipe == MergeBlockType.REMOVE:  # line 498
                for no, line in enumerate(block.lines):  # line 499
                    printo(("+++ %04d |%s|" % (no + block.line, line))[:termWidth])  # line 499
            elif block.tipe == MergeBlockType.REPLACE:  # TODO for MODIFY also show intra-line change ranges (TODO remove if that code was also removed)  # line 500
                for no, line in enumerate(block.replaces.lines):  # line 501
                    printo(("- | %04d |%s|" % (no + block.replaces.line, line))[:termWidth])  # line 501
                for no, line in enumerate(block.lines):  # line 502
                    printo(("+ | %04d |%s|" % (no + block.line, line))[:termWidth])  # line 502
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 506
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 507
    m = Metadata()  # type: Metadata  # line 508
    branch = None  # type: _coconut.typing.Optional[int]  # line 508
    revision = None  # type: _coconut.typing.Optional[int]  # line 508
    strict = '--strict' in options or m.strict  # type: bool  # line 509
    _from = {None: option.split("--from=")[1] for option in options if option.startswith("--from=")}.get(None, None)  # type: _coconut.typing.Optional[str]  # TODO implement  # line 510
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 511
    if branch not in m.branches:  # line 512
        Exit("Unknown branch")  # line 512
    m.loadBranch(branch)  # knows commits  # line 513
    revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 514
    if revision < 0 or revision > max(m.commits):  # line 515
        Exit("Unknown revision r%02d" % revision)  # line 515
    debug(MARKER + "Textual differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 516
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 517
    changes, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 518
    _diff(m, branch, revision, changes, ignoreWhitespace='--ignore-whitespace' in options or '--nows' in options)  # line 523

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 525
    ''' Create new revision from file tree changes vs. last commit. '''  # line 526
    m = Metadata()  # type: Metadata  # line 527
    if argument is not None and argument in m.tags:  # line 528
        Exit("Illegal commit message. It was already used as a tag name")  # line 528
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 529
# No untracking patterns needed here
    if m.picky and not trackingPatterns:  # line 531
        Exit("No file patterns staged for commit in picky mode")  # line 531
    debug((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 532
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options, check=False, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but aborts if no changes  # line 533
    m.paths = changes.additions  # line 534
    m.paths.update(changes.modifications)  # update pathset to changeset only  # line 535
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changes.deletions.items()})  # line 536
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 537
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 538
    m.saveBranch(m.branch)  # line 539
    m.loadBranches()  # TODO is it necessary to load again?  # line 540
    if m.picky:  # remove tracked patterns  # line 541
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 541
    else:  # track or simple mode: set branch dirty  # line 542
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 542
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 543
        m.tags.append(argument)  # memorize unique tag  # line 543
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 543
    m.saveBranches()  # line 544
    info(MARKER + "Created new revision r%02d%s (+%02d/-%02d/\u00b1%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications), len(changes.moves)))  # line 545

def status(options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 547
    ''' Show branches and current repository state. '''  # line 548
    m = Metadata()  # type: Metadata  # line 549
    current = m.branch  # type: int  # line 550
    strict = '--strict' in options or m.strict  # type: bool  # line 551
    info(MARKER + "Offline repository status")  # line 552
    info("Installation path:   %s" % os.path.abspath(os.path.dirname(__file__)))  # line 553
    info("Current SOS version: %s" % version.__version__)  # line 554
    info("At creation version: %s" % m.version)  # line 555
    info("Metadata format:     %s" % m.format)  # line 556
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 557
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 558
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 559
    info("Number of branches:  %d" % len(m.branches))  # line 560
#  info("Revisions:           %d" % sum([]))
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 562
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 563
    m.loadBranch(m.branch)  # line 564
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 508  # line 565
    changes, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress=True)  # line 566
    printo("File tree %s" % ("has changes vs. last revision of current branch" if modified(changes) else "is unchanged"))  # line 571
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 572
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 573
        m.loadBranch(branch.number)  # knows commit history  # line 574
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[max(m.commits)].message if m.commits[max(m.commits)].message else ""))  # line 575
    if m.track or m.picky and (len(m.branches[m.branch].tracked) > 0 or len(m.branches[m.branch].untracked) > 0):  # line 576
        info("\nTracked file patterns:")  # TODO print matching untracking patterns side-by-side  # line 577
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 578
        info("\nUntracked file patterns:")  # line 579
        printo(ajoin("  | ", m.branches[m.branch].untracked, "\n"))  # line 580

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str], FrozenSet[str]]':  # line 582
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags.
  '''  # line 588
    assert not (check and commit)  # line 589
    m = Metadata()  # type: Metadata  # line 590
    force = '--force' in options  # type: bool  # line 591
    strict = '--strict' in options or m.strict  # type: bool  # line 592
    if argument is not None:  # line 593
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 594
        if branch is None:  # line 595
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 595
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 596

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 599
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 600
    m.computeSequentialPathSet(m.branch, max(m.commits))  # load all commits up to specified revision  # line 601
    changes, msg = m.findChanges(m.branch if commit else None, max(m.commits) + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress='--progress' in options)  # line 602
    if check and modified(changes) and not force:  # line 607
        m.listChanges(changes)  # line 608
        Exit("File tree contains changes. Use --force to proceed")  # line 609
    elif commit:  # line 610
        if not modified(changes) and not force:  # line 611
            Exit("Nothing to commit")  # line 611
        m.listChanges(changes)  # line 612
        if msg:  # line 613
            printo(msg)  # line 613

    if argument is not None:  # branch/revision specified  # line 615
        m.loadBranch(branch)  # knows commits of target branch  # line 616
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 617
        if revision < 0 or revision > max(m.commits):  # line 618
            Exit("Unknown revision r%02d" % revision)  # line 618
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch), m.getTrackingPatterns(branch, negative=True))  # line 619
    return (m, m.branch, max(m.commits) + (1 if commit else 0), changes, strict, force, trackingPatterns, untrackingPatterns)  # line 620

def switch(argument: 'str', options: 'List[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 622
    ''' Continue work on another branch, replacing file tree changes. '''  # line 623
    m, branch, revision, changes, strict, _force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, ["--force"] + options)  # line 624
    force = '--force' in options  # type: bool  # needed as we fake force in above access  # line 625

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 628
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked, untracked=m.branches[branch].untracked)  # line 629
    else:  # full file switch  # line 630
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 631
        todos, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((untrackingPatterns | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 632

# Now check for potential conflicts
        changes.deletions.clear()  # local deletions never create conflicts, modifications always  # line 639
        rms = []  # type: _coconut.typing.Sequence[str]  # local additions can be ignored if restoration from switch would be same  # line 640
        for a, pinfo in changes.additions.items():  # has potential corresponding re-add in switch operation:  # line 641
            if a in todos.deletions and pinfo.size == todos.deletions[a].size and (pinfo.hash == todos.deletions[a].hash if m.strict else pinfo.mtime == todos.deletions[a].mtime):  # line 642
                rms.append(a)  # line 642
        for rm in rms:  # TODO could also silently accept remote DEL for local ADD  # line 643
            del changes.additions[rm]  # TODO could also silently accept remote DEL for local ADD  # line 643
        if modified(changes) and not force:  # line 644
            m.listChanges(changes)  # line 644
            Exit("File tree contains changes. Use --force to proceed")  # line 644
        debug(MARKER + "Switching to branch %sb%02d/r%02d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 645
        if not modified(todos):  # line 646
            info("No changes to current file tree")  # line 647
        else:  # integration required  # line 648
            for path, pinfo in todos.deletions.items():  # line 649
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 650
                printo("ADD " + path)  # line 651
            for path, pinfo in todos.additions.items():  # line 652
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 653
                printo("DEL " + path)  # line 654
            for path, pinfo in todos.modifications.items():  # line 655
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 656
                printo("MOD " + path)  # line 657
    m.branch = branch  # line 658
    m.saveBranches()  # store switched path info  # line 659
    info(MARKER + "Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 660

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 662
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 666
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 667
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 668
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 669
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 670
    m = Metadata()  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 671
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 672
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 673
    debug(MARKER + "Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 674

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 677
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 678
    untrackingUnion = untrackingPatterns | m.getTrackingPatterns(branch, negative=True)  # type: FrozenSet[str]  # line 679
    changes, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingUnion), dontConsider=excps if not (m.track or m.picky) else (untrackingUnion if onlys is None else onlys), progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 680
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 685
        if trackingUnion != trackingPatterns:  # nothing added  # line 686
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 687
        else:  # line 688
            info("Nothing to update")  # but write back updated branch info below  # line 689
    else:  # integration required  # line 690
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 691
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 692
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 692
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 693
        for path, pinfo in changes.additions.items():  # line 694
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 695
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 695
            if mrg.value & MergeOperation.REMOVE.value:  # line 696
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 696
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 697
        for path, pinfo in changes.modifications.items():  # line 698
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 699
            binary = not m.isTextType(path)  # type: bool  # line 700
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 701
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 702
                printo(("MOD " if not binary else "BIN ") + path)  # line 703
                while True:  # line 704
                    printo(into)  # TODO print mtime, size differences?  # line 705
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 706
                    if op in ("it" if binary else "itm"):  # line 707
                        break  # line 707
            if op == "t":  # line 708
                printo("THR " + path)  # blockwise copy of contents  # line 709
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 709
            elif op == "m":  # line 710
                current = None  # type: bytes  # line 711
                with open(encode(into), "rb") as fd:  # TODO slurps file  # line 712
                    current = fd.read()  # TODO slurps file  # line 712
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 713
                if current == file:  # line 714
                    debug("No difference to versioned file")  # line 714
                elif file is not None:  # if None, error message was already logged  # line 715
                    contents = None  # type: bytes  # line 716
                    nl = None  # type: bytes  # line 716
                    contents, nl = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # line 717
                    if contents != current:  # line 718
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 719
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 719
                    else:  # TODO but update timestamp?  # line 720
                        debug("No change")  # TODO but update timestamp?  # line 720
            else:  # mine or wrong input  # line 721
                printo("MNE " + path)  # nothing to do! same as skip  # line 722
    info(MARKER + "Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 723
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 724
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 725
    m.saveBranches()  # line 726

def delete(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 728
    ''' Remove a branch entirely. '''  # line 729
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options)  # line 730
    if len(m.branches) == 1:  # line 731
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 731
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 732
    if branch is None or branch not in m.branches:  # line 733
        Exit("Cannot delete unknown branch %r" % branch)  # line 733
    debug(MARKER + "Removing branch %d%s..." % (branch, " '%s'" % m.branches[branch].name if m.branches[branch].name else ""))  # line 734
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 735
    info(MARKER + "Branch b%02d%s removed" % (branch, " '%s'" % binfo.name if binfo.name else ""))  # line 736

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[], negative: 'bool'=False):  # line 738
    ''' Add a tracked files pattern to current branch's tracked files. negative means tracking blacklisting. '''  # line 739
    force = '--force' in options  # type: bool  # line 740
    m = Metadata()  # type: Metadata  # line 741
    if not (m.track or m.picky):  # line 742
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 742
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 743
    if pattern in patterns:  # line 744
        Exit("Pattern '%s' already tracked" % pattern)  # line 744
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 745
        Exit("The pattern folder doesn't exist. Use --force to add the file pattern anyway")  # line 745
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 746
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 747
    patterns.append(pattern)  # line 748
    m.saveBranches()  # line 749
    info(MARKER + "Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 750

def remove(relPath: 'str', pattern: 'str', negative: 'bool'=False):  # line 752
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 753
    m = Metadata()  # type: Metadata  # line 754
    if not (m.track or m.picky):  # line 755
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 755
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 756
    if pattern not in patterns:  # line 757
        suggestion = _coconut.set()  # type: Set[str]  # line 758
        for pat in patterns:  # line 759
            if fnmatch.fnmatch(pattern, pat):  # line 760
                suggestion.add(pat)  # line 760
        if suggestion:  # TODO use same wording as in move  # line 761
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 761
        Exit("Tracked pattern '%s' not found" % pattern)  # line 762
    patterns.remove(pattern)  # line 763
    m.saveBranches()  # line 764
    info(MARKER + "Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 765

def ls(folder: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 767
    ''' List specified directory, augmenting with repository metadata. '''  # line 768
    folder = (os.getcwd() if folder is None else folder)  # line 769
    m = Metadata()  # type: Metadata  # line 770
    debug(MARKER + "Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 771
    relPath = relativize(m.root, os.path.join(folder, "-"))[0]  # type: str  # line 772
    if relPath.startswith(".."):  # line 773
        Exit("Cannot list contents of folder outside offline repository")  # line 773
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 774
    untrackingPatterns = m.getTrackingPatterns(negative=True) if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 775
    if '--tags' in options:  # line 776
        printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 777
        return  # line 778
    if '--patterns' in options:  # line 779
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 780
        if out:  # line 781
            printo(out)  # line 781
        return  # line 782
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 783
    printo("DIR %s" % relPath)  # line 784
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 785
        ignore = None  # type: _coconut.typing.Optional[str]  # line 786
        for ig in m.c.ignores:  # line 787
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 788
                ignore = ig  # remember first match  # line 788
                break  # remember first match  # line 788
        if ig:  # line 789
            for wl in m.c.ignoresWhitelist:  # line 790
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 791
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 791
                    break  # found a white list entry for ignored file, undo ignoring it  # line 791
        matches = []  # type: List[str]  # line 792
        if not ignore:  # line 793
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 794
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 795
                    matches.append(os.path.basename(pattern))  # line 795
        matches.sort(key=lambda element: len(element))  # line 796
        printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "\u00b7\u00b7\u00b7"), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 797

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 799
    ''' List previous commits on current branch. '''  # line 800
    m = Metadata()  # type: Metadata  # line 801
    m.loadBranch(m.branch)  # knows commit history  # line 802
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 803
    nl = len("%d" % max(m.commits))  # determine space needed for revision  # line 804
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, max(m.commits))  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 805
    maxWidth = max([wcswidth((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) for commit in m.commits.values()])  # type: int  # line 806
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 807
    for no in range(max(m.commits) + 1):  # line 808
        commit = m.commits[no]  # type: CommitInfo  # line 809
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 810
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # side-effect: updates m.paths  # line 811
        _add = news - olds  # type: FrozenSet[str]  # line 812
        _del = olds - news  # type: FrozenSet[str]  # line 813
        _mod = frozenset([_ for _, info in nxts.items() if _ in m.paths and m.paths[_].size != info.size and (m.paths[_].hash != info.hash if m.strict else m.paths[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 814
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 815
        printo("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT) |%s|%s" % ("*" if commit.number == max(m.commits) else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)).ljust(maxWidth), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 816
        if '--changes' in options:  # TODO moves detection?  # line 817
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}, {}))  # TODO moves detection?  # line 817
        if '--diff' in options:  #  _diff(m, changes)  # needs from revision diff  # line 818
            pass  #  _diff(m, changes)  # needs from revision diff  # line 818
        olds = news  # line 819

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 821
    ''' Exported entire repository as archive for easy transfer. '''  # line 822
    debug(MARKER + "Dumping repository to archive...")  # line 823
    progress = '--progress' in options  # type: bool  # line 824
    import zipfile  # TODO display compression ratio (if any)  # line 825
    try:  # line 826
        import zlib  # line 826
        compression = zipfile.ZIP_DEFLATED  # line 826
    except:  # line 827
        compression = zipfile.ZIP_STORED  # line 827

    if argument is None:  # line 829
        Exit("Argument missing (target filename)")  # line 829
    argument = argument if "." in argument else argument + ".sos.zip"  # line 830
    if os.path.exists(encode(argument)):  # line 831
        try:  # line 832
            shutil.copy2(encode(argument), encode(argument + BACKUP_SUFFIX))  # line 832
        except Exception as E:  # line 833
            Exit("Error creating backup copy before dumping. Please resolve and retry. %r" % E)  # line 833
    with zipfile.ZipFile(argument, "w", compression) as _zip:  # line 834
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 835
        indicator = ProgressIndicator() if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 836
        totalsize = 0  # type: int  # line 837
        start_time = time.time()  # type: float  # line 838
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 839
            printo(dirpath.ljust(termWidth))  # TODO improve progress indicator output to | dir | dumpuing file  # line 840
            dirpath = decode(dirpath)  # line 841
            dirnames[:] = [decode(d) for d in dirnames]  # line 842
            filenames[:] = [decode(f) for f in filenames]  # line 843
            for filename in filenames:  # line 844
                abspath = os.path.join(dirpath, filename)  # type: str  # line 845
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 846
                totalsize += os.stat(encode(abspath)).st_size  # line 847
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 848
                if show:  # line 849
                    printo(("\rDumping %s @%.2f MiB/s %s" % (show, totalsize / (MEBI * (time.time() - start_time)), filename)).ljust(termWidth), nl="")  # line 849
                _zip.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 850
    info("\r" + (MARKER + "Finished dumping entire repository.").ljust(termWidth))  # clean line  # line 851

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 853
    command, key, value = (arguments + [None] * 2)[:3]  # line 854
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 855
        Exit("Unknown config command")  # line 855
    local = "--local" in options  # type: bool  # line 856
    m = Metadata()  # type: Metadata  # loads layered configuration as well. TODO warning if repo not exists  # line 857
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 858
    if command == "set":  # line 859
        if None in (key, value):  # line 860
            Exit("Key or value not specified")  # line 860
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 861
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 861
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 862
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 862
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 863
    elif command == "unset":  # line 864
        if key is None:  # line 865
            Exit("No key specified")  # line 865
        if key not in c.keys():  # HINT: Works on local configurations when used with --local  # line 866
            Exit("Unknown key")  # HINT: Works on local configurations when used with --local  # line 866
        del c[key]  # line 867
    elif command == "add":  # line 868
        if None in (key, value):  # line 869
            Exit("Key or value not specified")  # line 869
        if key not in CONFIGURABLE_LISTS:  # line 870
            Exit("Unsupported key %r" % key)  # line 870
        if key not in c.keys():  # prepare empty list, or copy from global, add new value below  # line 871
            c[key] = [_ for _ in c.__defaults[key]] if local else []  # prepare empty list, or copy from global, add new value below  # line 871
        elif value in c[key]:  # line 872
            Exit("Value already contained, nothing to do")  # line 872
        if ";" in value:  # line 873
            c[key].append(removePath(key, value))  # line 873
        else:  # line 874
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 874
    elif command == "rm":  # line 875
        if None in (key, value):  # line 876
            Exit("Key or value not specified")  # line 876
        if key not in c.keys():  # line 877
            Exit("Unknown key %r" % key)  # line 877
        if value not in c[key]:  # line 878
            Exit("Unknown value %r" % value)  # line 878
        c[key].remove(value)  # line 879
        if local and len(c[key]) == 0 and "--prune" in options:  # remove local enty, to fallback to global  # line 880
            del c[key]  # remove local enty, to fallback to global  # line 880
    else:  # Show or list  # line 881
        if key == "flags":  # list valid configuration items  # line 882
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 882
        elif key == "lists":  # line 883
            printo(", ".join(CONFIGURABLE_LISTS))  # line 883
        elif key == "texts":  # line 884
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 884
        else:  # line 885
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 886
            c = m.c  # always use full configuration chain  # line 887
            try:  # attempt single key  # line 888
                assert key is not None  # line 889
                c[key]  # line 889
                l = key in c.keys()  # type: bool  # line 890
                g = key in c.__defaults.keys()  # type: bool  # line 890
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 891
            except:  # normal value listing  # line 892
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 893
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 894
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 895
                for k, vt in sorted(vals.items()):  # line 896
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 896
                if len(c.keys()) == 0:  # line 897
                    info("No local configuration stored")  # line 897
                if len(c.__defaults.keys()) == 0:  # line 898
                    info("No global configuration stored")  # line 898
        return  # in case of list, no need to store anything  # line 899
    if local:  # saves changes of repoConfig  # line 900
        m.repoConf = c.__map  # saves changes of repoConfig  # line 900
        m.saveBranches()  # saves changes of repoConfig  # line 900
        Exit("OK", code=0)  # saves changes of repoConfig  # line 900
    else:  # global config  # line 901
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 902
        if f is None:  # line 903
            error("Error saving user configuration: %r" % h)  # line 903
        else:  # line 904
            Exit("OK", code=0)  # line 904

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[], negative: 'bool'=False):  # line 906
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique.
      for "mvnot" don't do any renaming (or do?)
  '''  # line 909
# TODO info(MARKER + TODO write tests for that
    force = '--force' in options  # type: bool  # line 911
    soft = '--soft' in options  # type: bool  # line 912
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 913
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 913
    m = Metadata()  # type: Metadata  # line 914
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 915
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 916
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 917
    if not matching and not force:  # line 918
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 918
    if not (m.track or m.picky):  # line 919
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 919
    if pattern not in patterns:  # list potential alternatives and exit  # line 920
        for tracked in (t for t in patterns if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 921
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 922
            if alternative:  # line 923
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 923
        if not (force or soft):  # line 924
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 924
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 925
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 926
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 927
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 931
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 932
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 932
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 933
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 934
    if len({st[1] for st in matches}) != len(matches):  # line 935
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 935
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 936
    if os.path.exists(encode(newRelPath)):  # line 937
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 938
        if exists and not (force or soft):  # line 939
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 939
    else:  # line 940
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 940
    if not soft:  # perform actual renaming  # line 941
        for (source, target) in matches:  # line 942
            try:  # line 943
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 943
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 944
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 944
    patterns[patterns.index(pattern)] = newPattern  # line 945
    m.saveBranches()  # line 946

def parse(root: 'str', cwd: 'str'):  # line 948
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm. '''  # line 949
    debug("Parsing command-line arguments...")  # line 950
    try:  # line 951
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 952
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: Union[List[str], str, None]  # line 953
        if len(arguments) == 0:  # line 954
            arguments = [None]  # line 954
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 955
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 956
        debug("Processing command %r with arguments %r and options %r." % (("" if command is None else command), arguments if arguments else "", options))  # line 957
        if command[:1] in "amr":  # line 958
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 958
        if command[:1] == "m":  # line 959
            if len(arguments) < 2:  # line 960
                Exit("Need a second file pattern argument as target for move or config command")  # line 960
            newRelPath, newPattern = relativize(root, os.path.join(cwd, options[0]))  # line 961
        if command[:1] == "a":  # also addnot  # line 962
            add(relPath, pattern, options, negative="n" in command)  # also addnot  # line 962
        elif command[:1] == "b":  # line 963
            branch(arguments[0], options)  # line 963
        elif command[:3] == "com":  # line 964
            commit(arguments[0], options, onlys, excps)  # line 964
        elif command[:2] == "ch":  # "changes" (legacy)  # line 965
            changes(arguments[0], options, onlys, excps)  # "changes" (legacy)  # line 965
        elif command[:2] == "ci":  # line 966
            commit(arguments[0], options, onlys, excps)  # line 966
        elif command[:3] == 'con':  # line 967
            config(arguments, options)  # line 967
        elif command[:2] == "de":  # line 968
            delete(arguments[0], options)  # line 968
        elif command[:2] == "di":  # line 969
            diff(arguments[0], options, onlys, excps)  # line 969
        elif command[:2] == "du":  # line 970
            dump(arguments[0], options)  # line 970
        elif command[:1] == "h":  # line 971
            usage(APPNAME, version.__version__)  # line 971
        elif command[:2] == "lo":  # line 972
            log(options)  # line 972
        elif command[:2] == "li":  # line 973
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 973
        elif command[:2] == "ls":  # TODO avoid and/or normalize root super paths (..)?  # line 974
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # TODO avoid and/or normalize root super paths (..)?  # line 974
        elif command[:1] == "m":  # also mvnot  # line 975
            move(relPath, pattern, newRelPath, newPattern, options[1:], negative="n" in command)  # also mvnot  # line 975
        elif command[:2] == "of":  # line 976
            offline(arguments[0], options)  # line 976
        elif command[:2] == "on":  # line 977
            online(options)  # line 977
        elif command[:1] == "r":  # also rmnot  # line 978
            remove(relPath, pattern, negative="n" in command)  # also rmnot  # line 978
        elif command[:2] == "st":  # line 979
            changes(arguments[0], options, onlys, excps)  # line 979
        elif command[:2] == "sw":  # line 980
            switch(arguments[0], options, onlys, excps)  # line 980
        elif command[:1] == "u":  # line 981
            update(arguments[0], options, onlys, excps)  # line 981
        elif command[:1] == "v":  # line 982
            usage(APPNAME, version.__version__, short=True)  # line 982
        else:  # line 983
            Exit("Unknown command '%s'" % command)  # line 983
        Exit(code=0)  # line 984
    except (Exception, RuntimeError) as E:  # line 985
        exception(E)  # line 986
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing.")  # line 987

def main():  # line 989
    global debug, info, warn, error  # line 990
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 991
    _log = Logger(logging.getLogger(__name__))  # line 992
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 992
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 993
        sys.argv.remove(option)  # clean up program arguments  # line 993
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 994
        usage(APPNAME, version.__version__)  # line 994
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 995
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 996
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 997
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 998
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in ["h", "v"]:  # in offline mode or just going offline TODO what about git config?  # line 999
        cwd = os.getcwd()  # line 1000
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 1001
        parse(root, cwd)  # line 1002
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 1003
        info("SOS: Running '%s %s'" % (cmd, " ".join(sys.argv[1:])))  # line 1004
        import subprocess  # only required in this section  # line 1005
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 1006
        inp = ""  # type: str  # line 1007
        while True:  # line 1008
            so, se = process.communicate(input=inp)  # line 1009
            if process.returncode is not None:  # line 1010
                break  # line 1010
            inp = sys.stdin.read()  # line 1011
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 1012
            if root is None:  # line 1013
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 1013
            m = Metadata(root)  # type: Metadata  # line 1014
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 1015
            m.saveBranches()  # line 1016
    else:  # line 1017
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 1017


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 1021
level = logging.DEBUG if verbose else logging.INFO  # line 1022
force_sos = '--sos' in sys.argv  # type: bool  # line 1023
force_vcs = '--vcs' in sys.argv  # type: bool  # line 1024
_log = Logger(logging.getLogger(__name__))  # line 1025
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1025
if __name__ == '__main__':  # line 1026
    main()  # line 1026
