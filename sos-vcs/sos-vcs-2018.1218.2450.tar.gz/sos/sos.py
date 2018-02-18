#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x651308eb

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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # line 6
try:  # try needed as paths differ when installed via pip TODO investigate further  # line 7
    from sos import version  # line 8
    from sos.utility import *  # line 9
    from sos.usage import *  # line 10
except:  # line 11
    import version  # line 12
    from utility import *  # line 13
    from usage import *  # line 14

# External dependencies
import configr  # line 17


# Constants
termWidth = getTermWidth() - 1  # uses curses or returns conservative default of 80  # line 21
APPNAME = "Subversion Offline Solution V%s (C) Arne Bachmann" % version.__release_version__  # type: str  # line 22


# Functions
def loadConfig() -> 'configr.Configr':  # Accessor when using defaults only  # line 26
    ''' Simplifies loading user-global config from file system or returning application defaults. '''  # line 27
    config = configr.Configr(COMMAND, defaults=defaults)  # type: configr.Configr  # defaults are used if key is not configured, but won't be saved  # line 28
    f, g = config.loadSettings(clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # latter for testing only  # line 29
    if f is None:  # line 30
        debug("Encountered a problem while loading the user configuration: %r" % g)  # line 30
    return config  # line 31

@_coconut_tco  # line 33
def saveConfig(config: 'configr.Configr') -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[Exception]]':  # line 33
    return _coconut_tail_call(config.saveSettings, clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # saves global config, not local one  # line 34


# Main data class
class Metadata:  # line 38
    ''' This class doesn't represent the entire repository state in memory,
      but serves as a container for different repo operations,
      using only parts of its attributes at any point in time. Use with care.
  '''  # line 42

    def __init__(_, path: '_coconut.typing.Optional[str]'=None, offline: 'bool'=False):  # line 44
        ''' Create empty container object for various repository operations, and import configuration. '''  # line 45
        _.root = (os.getcwd() if path is None else path)  # type: str  # line 46
        _.tags = []  # type: List[str]  # list of known (unique) tags  # line 47
        _.branch = None  # type: _coconut.typing.Optional[int]  # current branch number  # line 48
        _.branches = {}  # type: Dict[int, BranchInfo]  # branch number zero represents the initial state at branching  # line 49
        _.repoConf = {}  # type: Dict[str, Any]  # line 50
        _.track = None  # type: bool  # line 51
        _.picky = None  # type: bool  # line 51
        _.strict = None  # type: bool  # line 51
        _.compress = None  # type: bool  # line 51
        _.version = None  # type: _coconut.typing.Optional[str]  # line 51
        _.format = None  # type: _coconut.typing.Optional[int]  # line 51
        _.loadBranches(offline=offline)  # loads above values from repository, or uses application defaults  # line 52

        _.commits = {}  # type: Dict[int, CommitInfo]  # consecutive numbers per branch, starting at 0  # line 54
        _.paths = {}  # type: Dict[str, PathInfo]  # utf-8 encoded relative, normalized file system paths  # line 55
        _.commit = None  # type: _coconut.typing.Optional[int]  # current revision number  # line 56

        _.c = configr.Configr(data=_.repoConf, defaults=loadConfig())  # type: configr.Configr  # load global configuration with defaults behind the local configuration  # line 58

    def isTextType(_, filename: 'str') -> 'bool':  # line 60
        return (((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(mimetypes.guess_type(filename)[0])).startswith("text/") or any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.texttype])) and not any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.bintype])  # line 60

    def listChanges(_, changes: 'ChangeSet'):  # line 62
        moves = dict(changes.moves.values())  # type: Dict[str, PathInfo]  # line 63
        realadditions = {k: v for k, v in changes.additions.items() if k not in changes.moves}  # type: Dict[str, PathInfo]  # line 64
        realdeletions = {k: v for k, v in changes.deletions.items() if k not in moves}  # type: Dict[str, PathInfo]  # line 65
        if len(changes.moves) > 0:  # line 66
            printo(ajoin("MOV ", ["%s  <=  %s" % (path, dpath) for path, (dpath, dinfo) in sorted(changes.moves.items())], "\n"))  # line 66
        if len(realadditions) > 0:  # line 67
            printo(ajoin("ADD ", sorted(realadditions.keys()), "\n"))  # line 67
        if len(realdeletions) > 0:  # line 68
            printo(ajoin("DEL ", sorted(realdeletions.keys()), "\n"))  # line 68
        if len(changes.modifications) > 0:  # line 69
            printo(ajoin("MOD ", sorted(changes.modifications.keys()), "\n"))  # line 69

    def loadBranches(_, offline: 'bool'=False):  # line 71
        ''' Load list of branches and current branch info from metadata file. offline = offline command avoids message. '''  # line 72
        try:  # fails if not yet created (on initial branch/commit)  # line 73
            branches = None  # type: List[List]  # deserialized JSON is only list, while the real type of _.branches is a dict number -> BranchInfo (Coconut data type/named tuple)  # line 74
            with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "r", encoding=UTF8) as fd:  # line 75
                repo, branches, config = json.load(fd)  # line 76
            _.tags = repo["tags"]  # list of commit messages to treat as globally unique tags  # line 77
            _.branch = repo["branch"]  # current branch integer  # line 78
            _.track, _.picky, _.strict, _.compress, _.version, _.format = [repo.get(r, None) for r in ["track", "picky", "strict", "compress", "version", "format"]]  # line 79
            upgraded = []  # type: List[str]  # line 80
            if _.version is None:  # line 81
                _.version = "0 - pre-1.2"  # line 82
                upgraded.append("pre-1.2")  # line 83
            if len(branches[0]) < 6:  # For older versions, see https://pypi.python.org/simple/sos-vcs/  # line 84
                branches[:] = [branch + [[]] * (6 - len(branch)) for branch in branches]  # add untracking information, if missing  # line 85
                upgraded.append("2018.1210.3028")  # line 86
            if _.format is None:  # must be before 1.3.5+  # line 87
                _.format = METADATA_FORMAT  # marker for first metadata file format  # line 88
                branches[:] = [branch + [None] * (8 - len(branch)) for branch in branches]  # adds empty branching point information (branch/revision)  # line 89
                upgraded.append("1.3.5")  # line 90
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 91
            _.repoConf = config  # line 92
            if upgraded:  # line 93
                for upgrade in upgraded:  # line 94
                    warn("!!! Upgraded repository metadata to match SOS version %r" % upgrade)  # line 94
                warn("To revert the metadata upgrade%s, restore %s/%s from %s/%s NOW" % ("s" if len(upgraded) > 1 else "", metaFolder, metaFile, metaFolder, metaBack))  # line 95
                _.saveBranches()  # line 96
        except Exception as E:  # if not found, create metadata folder with default values  # line 97
            _.branches = {}  # line 98
            _.track, _.picky, _.strict, _.compress, _.version, _.format = [defaults[k] for k in ["track", "picky", "strict", "compress"]] + [version.__version__, METADATA_FORMAT]  # line 99
            (debug if offline else warn)("Couldn't read branches metadata: %r" % E)  # line 100

    def saveBranches(_, also: 'Dict[str, Any]'={}):  # line 102
        ''' Save list of branches and current branch info to metadata file. '''  # line 103
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # backup  # line 104
        with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "w", encoding=UTF8) as fd:  # line 105
            store = {"tags": _.tags, "branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress, "version": _.version, "format": METADATA_FORMAT}  # type: Dict[str, Any]  # line 106
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
        with codecs.open(encode(branchFolder(branch, file=metaFile)), "r", encoding=UTF8) as fd:  # line 131
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 132
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 133
        _.branch = branch  # line 134

    def saveBranch(_, branch: 'int'):  # line 136
        ''' Save all commits to a branch meta data file. '''  # line 137
        tryOrIgnore(lambda: shutil.copy2(encode(branchFolder(branch, file=metaFile)), encode(branchFolder(branch, metaBack))))  # backup  # line 138
        with codecs.open(encode(branchFolder(branch, file=metaFile)), "w", encoding=UTF8) as fd:  # line 139
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 140

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None, full: 'bool'=True):  # line 142
        ''' Create branch from an existing branch/revision.
        In case of full branching, copy all revisions, otherwise create only reference to originating branch/revision.
        branch: new target branch number (must not exist yet)
        name: optional name of new branch (currently always set by caller)
        initialMessage: message for commit if not last and file tree modified
        full: always create full branch copy, don't use a parent reference
        _.branch: current branch
    '''  # line 150
        debug("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 151
        now = int(time.time() * 1000)  # type: int  # line 152
        _.loadBranch(_.branch)  # load commits for current (originating) branch  # line 153
        revision = max(_.commits)  # type: int  # line 154
        _.commits.clear()  # line 155
        newBranch = dataCopy(BranchInfo, _.branches[_.branch], number=branch, ctime=now, name=("Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)) if name is None else name), tracked=[t for t in _.branches[_.branch].tracked], untracked=[u for u in _.branches[_.branch].untracked], parent=None if full else _.branch, revision=None if full else revision)  # type: BranchInfo  # line 156
        os.makedirs(encode(revisionFolder(branch, 0, base=_.root) if full else branchFolder(branch, base=_.root)))  # line 161
        if full:  # not fast branching via reference - copy all current files to new branch  # line 162
            _.computeSequentialPathSet(_.branch, revision)  # full set of files in latest revision in _.paths  # line 163
            for path, pinfo in _.paths.items():  # copy into initial branch revision  # line 164
                _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # copy into initial branch revision  # line 164
            _.commits[0] = CommitInfo(0, now, ("Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)) if initialMessage is None else initialMessage))  # store initial commit TODO also contain message from latest revision of originating branch  # line 165
            _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 166
        _.saveBranch(branch)  # save branch meta data to branch folder - for fast branching, only empty dict  # line 167
        _.branches[branch] = newBranch  # save branches meta data, needs to be saved in caller code  # line 168

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 170
        ''' Create a new branch from the current file tree. This clears all known commits and modifies the file system.
        branch: target branch number (must not exist yet)
        name: optional name of new branch
        initialMessage: commit message for revision 0 of the new branch
        _.branch: current branch, must exist already
    '''  # line 176
        now = int(time.time() * 1000)  # type: int  # line 177
        simpleMode = not (_.track or _.picky)  # line 178
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # in case of initial branch creation  # line 179
        untracked = [t for t in _.branches[_.branch].untracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # line 180
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 181
        _.paths = {}  # type: Dict[str, PathInfo]  # line 182
        if simpleMode:  # branches from file system state  # line 183
            changes, msg = _.findChanges(branch, 0, progress=simpleMode)  # creates revision folder and versioned files  # line 184
            _.listChanges(changes)  # line 185
            if msg:  # display compression factor  # line 186
                printo(msg)  # display compression factor  # line 186
            _.paths.update(changes.additions.items())  # line 187
        else:  # tracking or picky mode: branch from latest revision  # line 188
            os.makedirs(encode(revisionFolder(branch, 0, base=_.root)))  # line 189
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 190
                _.loadBranch(_.branch)  # line 191
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 192
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 193
                for path, pinfo in _.paths.items():  # line 194
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 195
        _.commits = {0: CommitInfo(0, now, ("Branched on %s" % strftime(now) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 196
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 197
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 198
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked, untracked)  # save branch info, in case it is needed  # line 199

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 201
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 202
        binfo = None  # type: BranchInfo  # line 203
        deps = [(binfo.number, binfo.revision) for binfo in _.branches.values() if binfo.parent is not None and _.getParentBranch(binfo.number, 0) == branch]  # type: List[Tuple[int, int]]  # get transitively depending branches  # line 204
        if deps:  # need to copy all parent revisions to dependet branches first  # line 205
            minrev = min([e[1] for e in deps])  # type: int  # minimum revision ever branched from parent (ignoring transitive branching!)  # line 206
            progress = ProgressIndicator()  # type: indicator  # line 207
            for rev in range(0, minrev + 1):  # rely on caching by copying revision-wise as long as needed in all depending branches  # line 208
                for dep, _rev in deps:  # line 209
                    if rev <= _rev:  # line 210
                        printo("\rIntegrating revision %02d into dependant branch %02d %s" % (rev, dep, progress.getIndicator()))  # line 211
                        shutil.copytree(encode(revisionFolder(branch, rev, base=_.root)), encode(revisionFolder(dep, rev, base=_.root)))  # folder would not exist yet  # line 212
            for dep, _rev in deps:  # copy remaining revisions per branch  # line 213
                for rev in range(minrev + 1, _rev + 1):  # line 214
                    printo("\rIntegrating revision %02d into dependant branch %02d %s" % (rev, dep, progress.getIndicator()))  # line 215
                    shutil.copytree(encode(revisionFolder(_.getParentBranch(dep, rev), rev, base=_.root)), encode(revisionFolder(dep, rev, base=_.root)))  # line 216
                _.branches[dep] = dataCopy(BranchInfo, _.branches[dep], parent=None, revision=None)  # remove reference information  # line 217
        printo(" " * termWidth + "\r")  # line 218
        tryOrIgnore(lambda: shutil.rmtree(encode(branchFolder(branch) + BACKUP_SUFFIX)))  # remove previous backup first  # line 219
        os.rename(encode(branchFolder(branch)), encode(branchFolder(branch) + BACKUP_SUFFIX))  # line 220
        binfo = _.branches[branch]  # keep reference for caller  # line 221
        del _.branches[branch]  # line 222
        _.branch = max(_.branches)  # switch to another valid branch  # line 223
        _.saveBranches()  # line 224
        _.commits.clear()  # line 225
        return binfo  # line 226

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 228
        ''' Load all file information from a commit meta data; if branched from another branch before specified revision, load correct revision recursively. '''  # line 229
        _branch = _.getParentBranch(branch, revision)  # type: int  # line 230
        with codecs.open(encode(revisionFolder(_branch, revision, base=_.root, file=metaFile)), "r", encoding=UTF8) as fd:  # line 231
            _.paths = json.load(fd)  # line 231
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 232
        _.branch = branch  # store current branch information = "switch" to loaded branch/commit  # line 233

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 235
        ''' Save all file information to a commit meta data file. '''  # line 236
        target = revisionFolder(branch, revision, base=_.root)  # type: str  # line 237
        try:  # line 238
            os.makedirs(encode(target))  # line 238
        except:  # line 239
            pass  # line 239
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(target, metaFile)), encode(os.path.join(target, metaBack))))  # ignore error for first backup  # line 240
        with codecs.open(encode(os.path.join(target, metaFile)), "w", encoding=UTF8) as fd:  # line 241
            json.dump(_.paths, fd, ensure_ascii=False)  # line 241

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'Tuple[ChangeSet, _coconut.typing.Optional[str]]':  # line 243
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes (always overrides considerOnly)
        progress: Show file names during processing
        returns: (ChangeSet = the state of file tree *differences*, unless "inverse" is True -> then return original data, message)
    '''  # line 252
        write = branch is not None and revision is not None  # line 253
        if write:  # line 254
            try:  # line 255
                os.makedirs(encode(revisionFolder(branch, revision, base=_.root)))  # line 255
            except FileExistsError:  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 256
                pass  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 256
        changes = ChangeSet({}, {}, {}, {})  # type: ChangeSet  # TODO Needs explicity initialization due to mypy problems with default arguments :-(  # line 257
        indicator = ProgressIndicator() if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # optional file list progress indicator  # line 258
        hashed = None  # type: _coconut.typing.Optional[str]  # line 259
        written = None  # type: int  # line 259
        compressed = 0  # type: int  # line 259
        original = 0  # type: int  # line 259
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 260
        for path, pinfo in _.paths.items():  # line 261
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 262
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 265
        for path, dirnames, filenames in os.walk(_.root):  # line 266
            path = decode(path)  # line 267
            dirnames[:] = [decode(d) for d in dirnames]  # line 268
            filenames[:] = [decode(f) for f in filenames]  # line 269
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 270
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 271
            dirnames.sort()  # line 272
            filenames.sort()  # line 272
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 273
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 274
            if dontConsider:  # line 275
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 276
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 277
                filename = relPath + SLASH + file  # line 278
                filepath = os.path.join(path, file)  # line 279
                try:  # line 280
                    stat = os.stat(encode(filepath))  # line 280
                except Exception as E:  # line 281
                    exception(E)  # line 281
                    continue  # line 281
                size, mtime = stat.st_size, int(stat.st_mtime * 1000)  # line 282
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 283
                if show:  # indication character returned  # line 284
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", show, filename)  # line 285
                    printo(outstring + " " * max(0, termWidth - len(outstring)), nl="")  # line 286
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 287
                    nameHash = hashStr(filename)  # line 288
                    try:  # line 289
                        hashed, written = hashFile(filepath, _.compress, saveTo=revisionFolder(branch, revision, base=_.root, file=nameHash) if write else None, callback=(lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if show else None) if size > 0 else (None, 0)  # line 290
                        changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 291
                        compressed += written  # line 292
                        original += size  # line 292
                    except Exception as E:  # line 293
                        exception(E)  # line 293
                    continue  # with next file  # line 294
                last = _.paths[filename]  # filename is known - check for modifications  # line 295
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 296
                    try:  # line 297
                        hashed, written = hashFile(filepath, _.compress, saveTo=revisionFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 298
                        changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 299
                        continue  # line 299
                    except Exception as E:  # line 300
                        exception(E)  # line 300
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and tryOrDefault(lambda: (hashFile(filepath, _.compress)[0] != last.hash), default=False)):  # detected a modification TODO wrap hashFile exception  # line 301
                    try:  # line 302
                        hashed, written = hashFile(filepath, _.compress, saveTo=revisionFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 303
                        changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 304
                    except Exception as E:  # line 305
                        exception(E)  # line 305
                else:  # with next file  # line 306
                    continue  # with next file  # line 306
                compressed += written  # line 307
                original += last.size if inverse else size  # line 307
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 308
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 308
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 309
            for file in names:  # line 310
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 311
                    continue  # don't mark ignored files as deleted  # line 311
                pth = path + SLASH + file  # type: str  # line 312
                changes.deletions[pth] = _.paths[pth]  # line 313
        for path, info in changes.additions.items():  # line 314
            for dpath, dinfo in changes.deletions.items():  # line 315
                if info.size == dinfo.size and info.mtime == dinfo.mtime and info.hash == dinfo.hash:  # was moved TODO check either mtime or hash?  # line 316
                    changes.moves[path] = (dpath, info)  # store new data and original name, but don't remove add/del  # line 317
                    break  # deletions loop, continue with next addition  # line 318
        if progress:  # forces clean line of progress output  # line 319
            printo("\r" + " " * termWidth + "\r", nl="")  # forces clean line of progress output  # line 319
        else:  # line 320
            debug("Finished detecting changes")  # line 320
        return (changes, ("Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else None)  # line 321

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 323
        ''' Returns nothing, just updates _.paths in place. '''  # line 324
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 325

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 327
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 328
        _.loadCommit(branch, 0)  # load initial paths  # line 329
        if incrementally:  # line 330
            yield _.paths  # line 330
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 331
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 331
        for rev in range(1, revision + 1):  # line 332
            m.loadCommit(_.getParentBranch(branch, rev), rev)  # line 333
            for p, info in m.paths.items():  # line 334
                if info.size == None:  # line 335
                    del _.paths[p]  # line 335
                else:  # line 336
                    _.paths[p] = info  # line 336
            if incrementally:  # line 337
                yield _.paths  # line 337
        yield None  # for the default case - not incrementally  # line 338

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None, negative: 'bool'=False) -> 'FrozenSet[str]':  # line 340
        ''' Returns list of tracking patterns (or untracking patterns if negative) for provided branch or current branch. '''  # line 341
        return _coconut.frozenset() if not (_.track or _.picky) else frozenset(_.branches[(_.branch if branch is None else branch)].untracked if negative else _.branches[(_.branch if branch is None else branch)].tracked)  # line 342

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 344
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 347
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 348
            return (_.branch, -1)  # no branch/revision specified  # line 348
        argument = argument.strip()  # line 349
        if argument.startswith(SLASH):  # current branch  # line 350
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 350
        if argument.endswith(SLASH):  # line 351
            try:  # line 352
                return (_.getBranchByName(argument[:-1]), -1)  # line 352
            except ValueError:  # line 353
                Exit("Unknown branch label '%s'" % argument)  # line 353
        if SLASH in argument:  # line 354
            b, r = argument.split(SLASH)[:2]  # line 355
            try:  # line 356
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 356
            except ValueError:  # line 357
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 357
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 358
        if branch not in _.branches:  # line 359
            branch = None  # line 359
        try:  # either branch name/number or reverse/absolute revision number  # line 360
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 360
        except:  # line 361
            Exit("Unknown branch label or wrong number format")  # line 361
        Exit("This should never happen. Please create a issue report")  # line 362
        return (None, None)  # line 362

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 364
        while True:  # find latest revision that contained the file physically  # line 365
            _branch = _.getParentBranch(branch, revision)  # type: int  # line 366
            source = revisionFolder(_branch, revision, base=_.root, file=nameHash)  # type: str  # line 367
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 368
                break  # line 368
            revision -= 1  # line 369
            if revision < 0:  # line 370
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 370
        return revision, source  # line 371

    def getParentBranch(_, branch: 'int', revision: 'int') -> 'int':  # line 373
        ''' Determine originating branch for a (potentially branched) revision, traversing all branch parents until found. '''  # line 374
        other = _.branches[branch].parent  # type: _coconut.typing.Optional[int]  # reference to originating parent branch, or None  # line 375
        if other is None or revision > _.branches[branch].revision:  # need to load commit from other branch instead  # line 376
            return branch  # need to load commit from other branch instead  # line 376
        while _.branches[other].parent is not None and revision <= _.branches[other].revision:  # line 377
            other = _.branches[other].parent  # line 377
        return other  # line 378

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 380
        ''' Copy versioned file to other branch/revision. '''  # line 381
        target = revisionFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 382
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 383
        shutil.copy2(encode(source), encode(target))  # line 384

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 386
        ''' Return file contents, or copy contents into file path provided. '''  # line 387
        source = revisionFolder(_.getParentBranch(branch, revision), revision, base=_.root, file=nameHash)  # type: str  # line 388
        try:  # line 389
            with openIt(source, "r", _.compress) as fd:  # line 390
                if toFile is None:  # read bytes into memory and return  # line 391
                    return fd.read()  # read bytes into memory and return  # line 391
                with open(encode(toFile), "wb") as to:  # line 392
                    while True:  # line 393
                        buffer = fd.read(bufSize)  # line 394
                        to.write(buffer)  # line 395
                        if len(buffer) < bufSize:  # line 396
                            break  # line 396
                    return None  # line 397
        except Exception as E:  # line 398
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 398
        return None  # line 399

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 401
        ''' Recreate file for given revision, or return binary contents if path is None. '''  # line 402
        if relPath is None:  # just return contents  # line 403
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 403
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 404
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 405
            try:  # line 406
                os.makedirs(encode(os.path.dirname(target)))  # line 406
            except:  # line 407
                pass  # line 407
        if pinfo.size == 0:  # line 408
            with open(encode(target), "wb"):  # line 409
                pass  # line 409
            try:  # update access/modification timestamps on file system  # line 410
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 410
            except Exception as E:  # line 411
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 411
            return None  # line 412
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 413
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 415
            while True:  # line 416
                buffer = fd.read(bufSize)  # line 417
                to.write(buffer)  # line 418
                if len(buffer) < bufSize:  # line 419
                    break  # line 419
        try:  # update access/modification timestamps on file system  # line 420
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 420
        except Exception as E:  # line 421
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 421
        return None  # line 422


# Main client operations
def offline(name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 426
    ''' Initial command to start working offline. '''  # line 427
    if os.path.exists(encode(metaFolder)):  # line 428
        if '--force' not in options:  # line 429
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 429
        try:  # line 430
            for entry in os.listdir(metaFolder):  # line 431
                resource = metaFolder + os.sep + entry  # line 432
                if os.path.isdir(resource):  # line 433
                    shutil.rmtree(encode(resource))  # line 433
                else:  # line 434
                    os.unlink(encode(resource))  # line 434
        except:  # line 435
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 435
    m = Metadata(offline=True)  # type: Metadata  # line 436
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 437
        m.compress = True  # plain file copies instead of compressed ones  # line 437
    if '--picky' in options or m.c.picky:  # Git-like  # line 438
        m.picky = True  # Git-like  # line 438
    elif '--track' in options or m.c.track:  # Svn-like  # line 439
        m.track = True  # Svn-like  # line 439
    if '--strict' in options or m.c.strict:  # always hash contents  # line 440
        m.strict = True  # always hash contents  # line 440
    debug(MARKER + "Going offline...")  # line 441
    m.createBranch(0, (defaults["defaultbranch"] if name is None else name), ("Offline repository created on %s" % strftime() if initialMessage is None else initialMessage))  # main branch's name may be None (e.g. for fossil)  # line 442
    m.branch = 0  # line 443
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 444
    info(MARKER + "Offline repository prepared. Use 'sos online' to finish offline work")  # line 445

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 447
    ''' Finish working offline. '''  # line 448
    debug(MARKER + "Going back online...")  # line 449
    force = '--force' in options  # type: bool  # line 450
    m = Metadata()  # type: Metadata  # line 451
    strict = '--strict' in options or m.strict  # type: bool  # line 452
    m.loadBranches()  # line 453
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 454
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 454
    m.loadBranch(m.branch)  # line 455
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # one commit guaranteed for first offline branch, for fast-branched branches a revision in branchinfo  # line 456
    if options.count("--force") < 2:  # line 457
        m.computeSequentialPathSet(m.branch, maxi)  # load all commits up to specified revision  # line 458
        changes, msg = m.findChanges(checkContent=strict, considerOnly=None if not (m.track or m.picky) else m.getTrackingPatterns(), dontConsider=None if not (m.track or m.picky) else m.getTrackingPatterns(negative=True), progress='--progress' in options)  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 459
        if modified(changes):  # line 460
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 464
    try:  # line 465
        shutil.rmtree(encode(metaFolder))  # line 465
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 465
    except Exception as E:  # line 466
        Exit("Error removing offline repository: %r" % E)  # line 466
    info(MARKER + "Offline repository removed, you're back online")  # line 467

def branch(name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 469
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it.
      Force not necessary, as either branching from last  revision anyway, or branching file tree anyway.
  '''  # line 472
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 473
    stay = '--stay' in options  # type: bool  # continue on current branch after branching (don't switch)  # line 474
    fast = '--fast' in options  # type: bool  # branch by referencing TODO move to default and use --full instead for old behavior  # line 475
    m = Metadata()  # type: Metadata  # line 476
    m.loadBranch(m.branch)  # line 477
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # line 478
    if name and m.getBranchByName(name) is not None:  # attempted to create a named branch  # line 479
        Exit("Branch '%s' already exists. Cannot proceed" % name)  # attempted to create a named branch  # line 479
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 480
    debug(MARKER + "Branching to %sbranch b%02d%s%s..." % ("unnamed " if name is None else "", branch, " '%s'" % name if name is not None else "", " from last revision" if last else ""))  # line 481
    if last:  # branch from last revision  # line 482
        m.duplicateBranch(branch, name, (initialMessage + " " if initialMessage else "") + "(Branched from r%02d/b%02d)" % (m.branch, maxi), not fast)  # branch from last revision  # line 482
    else:  # branch from current file tree state  # line 483
        m.createBranch(branch, name, ("Branched from file tree after r%02d/b%02d" % (m.branch, maxi) if initialMessage is None else initialMessage))  # branch from current file tree state  # line 483
    if not stay:  # line 484
        m.branch = branch  # line 484
    m.saveBranches()  # TODO or indent again?  # line 485
    info(MARKER + "%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if name is None else "", branch, " '%s'" % name if name else ""))  # line 486

def changes(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 488
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 489
    m = Metadata()  # type: Metadata  # line 490
    branch = None  # type: _coconut.typing.Optional[int]  # line 490
    revision = None  # type: _coconut.typing.Optional[int]  # line 490
    strict = '--strict' in options or m.strict  # type: bool  # line 491
    branch, revision = m.parseRevisionString(argument)  # line 492
    if branch not in m.branches:  # line 493
        Exit("Unknown branch")  # line 493
    m.loadBranch(branch)  # knows commits  # line 494
    revision = m.branches[branch].revision if not m.commits else (revision if revision >= 0 else max(m.commits) + 1 + revision)  # negative indexing  # line 495
    if revision < 0 or (m.commits and revision > max(m.commits)):  # line 496
        Exit("Unknown revision r%02d" % revision)  # line 496
    debug(MARKER + "Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 497
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 498
    changes, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 499
    m.listChanges(changes)  # line 504
    return changes  # for unit tests only TODO remove  # line 505

def _diff(m: 'Metadata', branch: 'int', revision: 'int', changes: 'ChangeSet', ignoreWhitespace: 'bool', textWrap: 'bool'=False):  # TODO introduce option to diff against committed revision  # line 507
    wrap = (lambda s: s) if textWrap else (lambda s: s[:termWidth])  # type: _coconut.typing.Callable[[str], str]  # line 508
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 509
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 510
    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 511
        content = None  # type: _coconut.typing.Optional[bytes]  # line 512
        if pinfo.size == 0:  # empty file contents  # line 513
            content = b""  # empty file contents  # line 513
        else:  # versioned file  # line 514
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 514
            assert content is not None  # versioned file  # line 514
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 515
        blocks = None  # type: List[MergeBlock]  # line 516
        nl = None  # type: bytes  # line 516
        blocks, nl = merge(filename=abspath, into=content, diffOnly=True, ignoreWhitespace=ignoreWhitespace)  # only determine change blocks  # line 517
        printo("DIF %s%s  %s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else "", NL_NAMES[nl]))  # line 518
        for block in blocks:  # line 519
#      if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:
#        pass  # TODO print some previous and following lines - which aren't accessible here anymore
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 522
                for no, line in enumerate(block.lines):  # line 523
                    printo(wrap("--- %04d |%s|" % (no + block.line, line)))  # line 523
            elif block.tipe == MergeBlockType.REMOVE:  # line 524
                for no, line in enumerate(block.lines):  # line 525
                    printo(wrap("+++ %04d |%s|" % (no + block.line, line)))  # line 525
            elif block.tipe == MergeBlockType.REPLACE:  # line 526
                for no, line in enumerate(block.replaces.lines):  # line 527
                    printo(wrap("- | %04d |%s|" % (no + block.replaces.line, line)))  # line 527
                for no, line in enumerate(block.lines):  # line 528
                    printo(wrap("+ | %04d |%s|" % (no + block.line, line)))  # line 528
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications
            if block.tipe != MergeBlockType.KEEP:  # line 531
                printo()  # line 531

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 533
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 534
    m = Metadata()  # type: Metadata  # line 535
    branch = None  # type: _coconut.typing.Optional[int]  # line 535
    revision = None  # type: _coconut.typing.Optional[int]  # line 535
    strict = '--strict' in options or m.strict  # type: bool  # line 536
    ignoreWhitespace = '--ignore-whitespace' in options or '--iw' in options  # type: bool  # line 537
    wrap = '--wrap' in options  # type: bool  # allow text to wrap around  # line 538
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 539
    if branch not in m.branches:  # line 540
        Exit("Unknown branch")  # line 540
    m.loadBranch(branch)  # knows commits  # line 541
    revision = m.branches[branch].revision if not m.commits else (revision if revision >= 0 else max(m.commits) + 1 + revision)  # negative indexing  # line 542
    if revision < 0 or (m.commits and revision > max(m.commits)):  # line 543
        Exit("Unknown revision r%02d" % revision)  # line 543
    debug(MARKER + "Textual differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 544
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 545
    changes, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 546
    _diff(m, branch, revision, changes, ignoreWhitespace=ignoreWhitespace, textWrap=wrap)  # line 551

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 553
    ''' Create new revision from file tree changes vs. last commit. '''  # line 554
    m = Metadata()  # type: Metadata  # line 555
    if argument is not None and argument in m.tags:  # line 556
        Exit("Illegal commit message. It was already used as a tag name")  # line 556
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 557
# No untracking patterns needed here
    if m.picky and not trackingPatterns:  # line 559
        Exit("No file patterns staged for commit in picky mode")  # line 559
    debug((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 560
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options, check=False, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but aborts if no changes  # line 561
    m.paths = changes.additions  # line 562
    m.paths.update(changes.modifications)  # update pathset to changeset only  # line 563
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changes.deletions.items()})  # line 564
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 565
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 566
    m.saveBranch(m.branch)  # line 567
    m.loadBranches()  # TODO is it necessary to load again?  # line 568
    if m.picky:  # remove tracked patterns  # line 569
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 569
    else:  # track or simple mode: set branch dirty  # line 570
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 570
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 571
        m.tags.append(argument)  # memorize unique tag  # line 571
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 571
    m.saveBranches()  # line 572
    info(MARKER + "Created new revision r%02d%s (+%02d/-%02d/\u00b1%02d/*%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions), len(changes.deletions), len(changes.modifications), len(changes.moves)))  # line 573

def status(argument: '_coconut.typing.Optional[str]'=None, vcs: '_coconut.typing.Optional[str]'=None, cmd: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 575
    ''' Show branches and current repository state. '''  # line 576
    m = Metadata()  # type: Metadata  # line 577
    if not m.c.useChangesCommand and not '--repo' in options:  # TODO for fossil not possible to restore SVN behavior  # line 578
        changes(argument, options, onlys, excps)  # TODO for fossil not possible to restore SVN behavior  # line 578
        return  # TODO for fossil not possible to restore SVN behavior  # line 578
    current = m.branch  # type: int  # line 579
    strict = '--strict' in options or m.strict  # type: bool  # line 580
    info(MARKER + "Offline repository status")  # line 581
    info("Repository root:     %s" % os.getcwd())  # line 582
    info("Underlying VCS root: %s" % vcs)  # line 583
    info("Underlying VCS type: %s" % cmd)  # line 584
    info("Installation path:   %s" % os.path.abspath(os.path.dirname(__file__)))  # line 585
    info("Current SOS version: %s" % version.__version__)  # line 586
    info("At creation version: %s" % m.version)  # line 587
    info("Metadata format:     %s" % m.format)  # line 588
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 589
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 590
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 591
    info("Number of branches:  %d" % len(m.branches))  # line 592
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 593
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 594
    m.loadBranch(current)  # line 595
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # line 596
    m.computeSequentialPathSet(current, maxi)  # load all commits up to specified revision  # line 508  # line 597
    _changes, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress=True)  # line 598
    printo("File tree %s" % ("has changes" if modified(_changes) else "is unchanged"))  # line 603
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 604
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 605
        m.loadBranch(branch.number)  # knows commit history  # line 606
        maxi = max(m.commits) if m.commits else m.branches[branch.number].revision  # line 607
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[maxi].message if maxi in m.commits and m.commits[maxi].message else ""))  # line 608
    if m.track or m.picky and (len(m.branches[m.branch].tracked) > 0 or len(m.branches[m.branch].untracked) > 0):  # line 609
        info("\nTracked file patterns:")  # TODO print matching untracking patterns side-by-side  # line 610
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 611
        info("\nUntracked file patterns:")  # line 612
        printo(ajoin("  | ", m.branches[m.branch].untracked, "\n"))  # line 613

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str], FrozenSet[str]]':  # line 615
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags.
  '''  # line 621
    assert not (check and commit)  # line 622
    m = Metadata()  # type: Metadata  # line 623
    force = '--force' in options  # type: bool  # line 624
    strict = '--strict' in options or m.strict  # type: bool  # line 625
    if argument is not None:  # line 626
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 627
        if branch is None:  # line 628
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 628
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 629
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # line 630

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 633
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 634
    m.computeSequentialPathSet(m.branch, maxi)  # load all commits up to specified revision  # line 635
    changes, msg = m.findChanges(m.branch if commit else None, maxi + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress='--progress' in options)  # line 636
    if check and modified(changes) and not force:  # line 641
        m.listChanges(changes)  # line 642
        Exit("File tree contains changes. Use --force to proceed")  # line 643
    elif commit:  # line 644
        if not modified(changes) and not force:  # line 645
            Exit("Nothing to commit")  # line 645
        m.listChanges(changes)  # line 646
        if msg:  # line 647
            printo(msg)  # line 647

    if argument is not None:  # branch/revision specified  # line 649
        m.loadBranch(branch)  # knows commits of target branch  # line 650
        maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # line 651
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 652
        if revision < 0 or revision > maxi:  # line 653
            Exit("Unknown revision r%02d" % revision)  # line 653
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch), m.getTrackingPatterns(branch, negative=True))  # line 654
    return (m, m.branch, maxi + (1 if commit else 0), changes, strict, force, trackingPatterns, untrackingPatterns)  # line 655

def switch(argument: 'str', options: 'List[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 657
    ''' Continue work on another branch, replacing file tree changes. '''  # line 658
    m, branch, revision, changes, strict, _force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, ["--force"] + options)  # line 659
    force = '--force' in options  # type: bool  # needed as we fake force in above access  # line 660

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 663
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked, untracked=m.branches[branch].untracked)  # line 664
    else:  # full file switch  # line 665
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 666
        todos, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((untrackingPatterns | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 667

# Now check for potential conflicts
        changes.deletions.clear()  # local deletions never create conflicts, modifications always  # line 674
        rms = []  # type: _coconut.typing.Sequence[str]  # local additions can be ignored if restoration from switch would be same  # line 675
        for a, pinfo in changes.additions.items():  # has potential corresponding re-add in switch operation:  # line 676
            if a in todos.deletions and pinfo.size == todos.deletions[a].size and (pinfo.hash == todos.deletions[a].hash if m.strict else pinfo.mtime == todos.deletions[a].mtime):  # line 677
                rms.append(a)  # line 677
        for rm in rms:  # TODO could also silently accept remote DEL for local ADD  # line 678
            del changes.additions[rm]  # TODO could also silently accept remote DEL for local ADD  # line 678
        if modified(changes) and not force:  # line 679
            m.listChanges(changes)  # line 679
            Exit("File tree contains changes. Use --force to proceed")  # line 679
        debug(MARKER + "Switching to branch %sb%02d/r%02d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 680
        if not modified(todos):  # line 681
            info("No changes to current file tree")  # line 682
        else:  # integration required  # line 683
            for path, pinfo in todos.deletions.items():  # line 684
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 685
                printo("ADD " + path)  # line 686
            for path, pinfo in todos.additions.items():  # line 687
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 688
                printo("DEL " + path)  # line 689
            for path, pinfo in todos.modifications.items():  # line 690
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 691
                printo("MOD " + path)  # line 692
    m.branch = branch  # line 693
    m.saveBranches()  # store switched path info  # line 694
    info(MARKER + "Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 695

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 697
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 701
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 702
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 703
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 704
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 705
    m = Metadata()  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 706
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 707
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 708
    debug(MARKER + "Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 709

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 712
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 713
    untrackingUnion = untrackingPatterns | m.getTrackingPatterns(branch, negative=True)  # type: FrozenSet[str]  # line 714
    changes, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingUnion), dontConsider=excps if not (m.track or m.picky) else (untrackingUnion if onlys is None else onlys), progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 715
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 720
        if trackingUnion != trackingPatterns:  # nothing added  # line 721
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 722
        else:  # line 723
            info("Nothing to update")  # but write back updated branch info below  # line 724
    else:  # integration required  # line 725
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 726
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 727
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 727
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 728
        for path, pinfo in changes.additions.items():  # line 729
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 730
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 730
            if mrg.value & MergeOperation.REMOVE.value:  # line 731
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 731
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 732
        for path, pinfo in changes.modifications.items():  # line 733
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 734
            binary = not m.isTextType(path)  # type: bool  # line 735
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 736
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 737
                printo(("MOD " if not binary else "BIN ") + path)  # line 738
                while True:  # line 739
                    printo(into)  # TODO print mtime, size differences?  # line 740
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 741
                    if op in ("it" if binary else "itm"):  # line 742
                        break  # line 742
            if op == "t":  # line 743
                printo("THR " + path)  # blockwise copy of contents  # line 744
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 744
            elif op == "m":  # line 745
                current = None  # type: bytes  # line 746
                with open(encode(into), "rb") as fd:  # TODO slurps file  # line 747
                    current = fd.read()  # TODO slurps file  # line 747
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 748
                if current == file:  # line 749
                    debug("No difference to versioned file")  # line 749
                elif file is not None:  # if None, error message was already logged  # line 750
                    contents = None  # type: bytes  # line 751
                    nl = None  # type: bytes  # line 751
                    contents, nl = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # line 752
                    if contents != current:  # line 753
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 754
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 754
                    else:  # TODO but update timestamp?  # line 755
                        debug("No change")  # TODO but update timestamp?  # line 755
            else:  # mine or wrong input  # line 756
                printo("MNE " + path)  # nothing to do! same as skip  # line 757
    info(MARKER + "Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 758
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 759
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 760
    m.saveBranches()  # line 761

def destroy(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 763
    ''' Remove a branch entirely. '''  # line 764
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options)  # line 765
    if len(m.branches) == 1:  # line 766
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 766
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 767
    if branch is None or branch not in m.branches:  # line 768
        Exit("Cannot delete unknown branch %r" % branch)  # line 768
    debug(MARKER + "Removing branch b%02d%s..." % (branch, " '%s'" % ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name))))  # line 769
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 770
    info(MARKER + "Branch b%02d%s removed" % (branch, " '%s'" % ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(binfo.name))))  # line 771

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[], negative: 'bool'=False):  # line 773
    ''' Add a tracked files pattern to current branch's tracked files. negative means tracking blacklisting. '''  # line 774
    force = '--force' in options  # type: bool  # line 775
    m = Metadata()  # type: Metadata  # line 776
    if not (m.track or m.picky):  # line 777
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 777
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 778
    if pattern in patterns:  # line 779
        Exit("Pattern '%s' already tracked" % pattern)  # line 779
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 780
        Exit("The pattern folder doesn't exist. Use --force to add the file pattern anyway")  # line 780
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 781
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 782
    patterns.append(pattern)  # line 783
    m.saveBranches()  # line 784
    info(MARKER + "Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 785

def remove(relPath: 'str', pattern: 'str', negative: 'bool'=False):  # line 787
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 788
    m = Metadata()  # type: Metadata  # line 789
    if not (m.track or m.picky):  # line 790
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 790
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 791
    if pattern not in patterns:  # line 792
        suggestion = _coconut.set()  # type: Set[str]  # line 793
        for pat in patterns:  # line 794
            if fnmatch.fnmatch(pattern, pat):  # line 795
                suggestion.add(pat)  # line 795
        if suggestion:  # TODO use same wording as in move  # line 796
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 796
        Exit("Tracked pattern '%s' not found" % pattern)  # line 797
    patterns.remove(pattern)  # line 798
    m.saveBranches()  # line 799
    info(MARKER + "Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 800

def ls(folder: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 802
    ''' List specified directory, augmenting with repository metadata. '''  # line 803
    folder = (os.getcwd() if folder is None else folder)  # line 804
    m = Metadata()  # type: Metadata  # line 805
    debug(MARKER + "Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 806
    relPath = relativize(m.root, os.path.join(folder, "-"))[0]  # type: str  # line 807
    if relPath.startswith(".."):  # line 808
        Exit("Cannot list contents of folder outside offline repository")  # line 808
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 809
    untrackingPatterns = m.getTrackingPatterns(negative=True) if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 810
    if '--tags' in options:  # line 811
        printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 812
        return  # line 813
    if '--patterns' in options:  # line 814
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 815
        if out:  # line 816
            printo(out)  # line 816
        return  # line 817
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 818
    printo("DIR %s" % relPath)  # line 819
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 820
        ignore = None  # type: _coconut.typing.Optional[str]  # line 821
        for ig in m.c.ignores:  # line 822
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 823
                ignore = ig  # remember first match  # line 823
                break  # remember first match  # line 823
        if ig:  # line 824
            for wl in m.c.ignoresWhitelist:  # line 825
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 826
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 826
                    break  # found a white list entry for ignored file, undo ignoring it  # line 826
        matches = []  # type: List[str]  # line 827
        if not ignore:  # line 828
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 829
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 830
                    matches.append(os.path.basename(pattern))  # line 830
        matches.sort(key=lambda element: len(element))  # sort in-place  # line 831
        printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else "\u00b7\u00b7\u00b7"), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 832

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 834
    ''' List previous commits on current branch. '''  # line 835
    m = Metadata()  # type: Metadata  # line 836
    m.loadBranch(m.branch)  # knows commit history  # line 837
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # one commit guaranteed for first offline branch, for fast-branched branches a revision in branchinfo  # line 838
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 839
    nl = len("%d" % maxi)  # type: int  # determine space needed for revision  # line 840
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, maxi)  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 841
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 842
    commit = None  # type: CommitInfo  # line 843
    for no in range(maxi + 1):  # line 844
        if no in m.commits:  # line 845
            commit = m.commits[no]  # line 845
        else:  # TODO clean this code  # line 846
            n = Metadata()  # type: Metadata  # line 847
            n.loadBranch(n.getParentBranch(m.branch, no))  # line 848
            commit = n.commits[no]  # line 849
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 850
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # side-effect: updates m.paths  # line 851
        _add = news - olds  # type: FrozenSet[str]  # line 852
        _del = olds - news  # type: FrozenSet[str]  # line 853
        _mod = frozenset([_ for _, info in nxts.items() if _ in m.paths and m.paths[_].size != info.size and (m.paths[_].hash != info.hash if m.strict else m.paths[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 854
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 855
        printo("  %s r%s @%s (+%02d/-%02d/*%02d +%02dT) |%s|%s" % ("*" if commit.number == maxi else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 856
        if '--changes' in options:  # TODO moves detection?  # line 857
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}, {}))  # TODO moves detection?  # line 857
        if '--diff' in options:  #  _diff(m, changes)  # needs from revision diff  # line 858
            pass  #  _diff(m, changes)  # needs from revision diff  # line 858
        olds = news  # line 859

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 861
    ''' Exported entire repository as archive for easy transfer. '''  # line 862
    debug(MARKER + "Dumping repository to archive...")  # line 863
    progress = '--progress' in options  # type: bool  # line 864
    import zipfile  # line 865
    try:  # HINT zlib is the library that contains the deflated algorithm  # line 866
        import zlib  # HINT zlib is the library that contains the deflated algorithm  # line 866
        compression = zipfile.ZIP_DEFLATED  # HINT zlib is the library that contains the deflated algorithm  # line 866
    except:  # line 867
        compression = zipfile.ZIP_STORED  # line 867

    if argument is None:  # line 869
        Exit("Argument missing (target filename)")  # line 869
    argument = argument if "." in argument else argument + DUMP_FILE  # TODO this logic lacks a bit, "v1.2" would not receive the suffix  # line 870
    if os.path.exists(encode(argument)):  # line 871
        try:  # line 872
            shutil.copy2(encode(argument), encode(argument + BACKUP_SUFFIX))  # line 872
        except Exception as E:  # line 873
            Exit("Error creating backup copy before dumping. Please resolve and retry. %r" % E)  # line 873
    with zipfile.ZipFile(argument, "w", compression) as _zip:  # line 874
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 875
        indicator = ProgressIndicator() if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 876
        totalsize = 0  # type: int  # line 877
        start_time = time.time()  # type: float  # line 878
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 879
            printo(dirpath.ljust(termWidth))  # TODO improve progress indicator output to | dir | dumpuing file  # line 880
            dirpath = decode(dirpath)  # line 881
            dirnames[:] = [decode(d) for d in dirnames]  # line 882
            filenames[:] = [decode(f) for f in filenames]  # line 883
            for filename in filenames:  # line 884
                abspath = os.path.join(dirpath, filename)  # type: str  # line 885
                relpath = os.path.relpath(abspath, repopath)  # type: str  # line 886
                totalsize += os.stat(encode(abspath)).st_size  # line 887
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 888
                if show:  # line 889
                    printo(("\rDumping %s @%.2f MiB/s %s" % (show, totalsize / (MEBI * (time.time() - start_time)), filename)).ljust(termWidth), nl="")  # line 889
                _zip.write(abspath, relpath.replace(os.sep, "/"))  # write entry into archive  # line 890
    info("\r" + (MARKER + "Finished dumping entire repository @%.2f MiB/s." % (totalsize / (MEBI * (time.time() - start_time)))).ljust(termWidth))  # clean line  # line 891

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 893
    command, key, value = (arguments + [None] * 2)[:3]  # line 894
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 895
        Exit("Unknown config command")  # line 895
    local = "--local" in options  # type: bool  # line 896
    m = Metadata()  # type: Metadata  # loads layered configuration as well. TODO warning if repo not exists  # line 897
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 898
    if command == "set":  # line 899
        if None in (key, value):  # line 900
            Exit("Key or value not specified")  # line 900
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 901
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 901
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 902
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 902
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 903
    elif command == "unset":  # line 904
        if key is None:  # line 905
            Exit("No key specified")  # line 905
        if key not in c.keys():  # HINT: Works on local configurations when used with --local  # line 906
            Exit("Unknown key")  # HINT: Works on local configurations when used with --local  # line 906
        del c[key]  # line 907
    elif command == "add":  # line 908
        if None in (key, value):  # line 909
            Exit("Key or value not specified")  # line 909
        if key not in CONFIGURABLE_LISTS:  # line 910
            Exit("Unsupported key %r" % key)  # line 910
        if key not in c.keys():  # prepare empty list, or copy from global, add new value below  # line 911
            c[key] = [_ for _ in c.__defaults[key]] if local else []  # prepare empty list, or copy from global, add new value below  # line 911
        elif value in c[key]:  # line 912
            Exit("Value already contained, nothing to do")  # line 912
        if ";" in value:  # line 913
            c[key].append(removePath(key, value))  # line 913
        else:  # line 914
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 914
    elif command == "rm":  # line 915
        if None in (key, value):  # line 916
            Exit("Key or value not specified")  # line 916
        if key not in c.keys():  # line 917
            Exit("Unknown key %r" % key)  # line 917
        if value not in c[key]:  # line 918
            Exit("Unknown value %r" % value)  # line 918
        c[key].remove(value)  # line 919
        if local and len(c[key]) == 0 and "--prune" in options:  # remove local enty, to fallback to global  # line 920
            del c[key]  # remove local enty, to fallback to global  # line 920
    else:  # Show or list  # line 921
        if key == "flags":  # list valid configuration items  # line 922
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 922
        elif key == "lists":  # line 923
            printo(", ".join(CONFIGURABLE_LISTS))  # line 923
        elif key == "texts":  # line 924
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 924
        else:  # line 925
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 926
            c = m.c  # always use full configuration chain  # line 927
            try:  # attempt single key  # line 928
                assert key is not None  # line 929
                c[key]  # line 929
                l = key in c.keys()  # type: bool  # line 930
                g = key in c.__defaults.keys()  # type: bool  # line 930
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 931
            except:  # normal value listing  # line 932
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 933
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 934
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 935
                for k, vt in sorted(vals.items()):  # line 936
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 936
                if len(c.keys()) == 0:  # line 937
                    info("No local configuration stored")  # line 937
                if len(c.__defaults.keys()) == 0:  # line 938
                    info("No global configuration stored")  # line 938
        return  # in case of list, no need to store anything  # line 939
    if local:  # saves changes of repoConfig  # line 940
        m.repoConf = c.__map  # saves changes of repoConfig  # line 940
        m.saveBranches()  # saves changes of repoConfig  # line 940
        Exit("OK", code=0)  # saves changes of repoConfig  # line 940
    else:  # global config  # line 941
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 942
        if f is None:  # line 943
            error("Error saving user configuration: %r" % h)  # line 943
        else:  # line 944
            Exit("OK", code=0)  # line 944

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[], negative: 'bool'=False):  # line 946
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique.
      for "mvnot" don't do any renaming (or do?)
  '''  # line 949
    debug(MARKER + "Renaming %r to %r" % (pattern, newPattern))  # line 950
    force = '--force' in options  # type: bool  # line 951
    soft = '--soft' in options  # type: bool  # line 952
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 953
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 953
    m = Metadata()  # type: Metadata  # line 954
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 955
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 956
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 957
    if not matching and not force:  # line 958
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 958
    if not (m.track or m.picky):  # line 959
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 959
    if pattern not in patterns:  # list potential alternatives and exit  # line 960
        for tracked in (t for t in patterns if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 961
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 962
            if alternative:  # line 963
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 963
        if not (force or soft):  # line 964
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 964
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 965
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 966
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 967
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 971
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 972
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 972
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 973
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 974
    if len({st[1] for st in matches}) != len(matches):  # line 975
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 975
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 976
    if os.path.exists(encode(newRelPath)):  # line 977
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 978
        if exists and not (force or soft):  # line 979
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 979
    else:  # line 980
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 980
    if not soft:  # perform actual renaming  # line 981
        for (source, target) in matches:  # line 982
            try:  # line 983
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 983
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 984
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 984
    patterns[patterns.index(pattern)] = newPattern  # line 985
    m.saveBranches()  # line 986

def parse(root: 'str', cwd: 'str', cmd: 'str'):  # line 988
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm, mv. '''  # line 989
    debug("Parsing command-line arguments...")  # line 990
    try:  # line 991
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 992
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: List[_coconut.typing.Optional[str]]  # line 993
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 994
        onlys, excps = parseOnlyOptions(cwd, options)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 995
        debug("Processing command %r with arguments %r and options %r." % (command, [_ for _ in arguments if _ is not None], options))  # line 996
        if command[:1] in "amr":  # line 997
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 997
        if command[:1] == "m":  # line 998
            if len(arguments) < 2:  # line 999
                Exit("Need a second file pattern argument as target for move command")  # line 999
            newRelPath, newPattern = relativize(root, os.path.join(cwd, arguments[1]))  # line 1000
        arguments[:] = (arguments + [None] * 3)[:3]  # line 1001
        if command[:1] == "a":  # addnot  # line 1002
            add(relPath, pattern, options, negative="n" in command)  # addnot  # line 1002
        elif command[:1] == "b":  # line 1003
            branch(arguments[0], arguments[1], options)  # line 1003
        elif command[:3] == "com":  # line 1004
            commit(arguments[0], options, onlys, excps)  # line 1004
        elif command[:2] == "ch":  # "changes" (legacy)  # line 1005
            changes(arguments[0], options, onlys, excps)  # "changes" (legacy)  # line 1005
        elif command[:2] == "ci":  # line 1006
            commit(arguments[0], options, onlys, excps)  # line 1006
        elif command[:3] == 'con':  # line 1007
            config(arguments, options)  # line 1007
        elif command[:2] == "de":  # line 1008
            destroy(arguments[0], options)  # line 1008
        elif command[:2] == "di":  # line 1009
            diff(arguments[0], options, onlys, excps)  # line 1009
        elif command[:2] == "du":  # line 1010
            dump(arguments[0], options)  # line 1010
        elif command[:1] == "h":  # line 1011
            usage(APPNAME, version.__version__)  # line 1011
        elif command[:2] == "lo":  # line 1012
            log(options)  # line 1012
        elif command[:2] == "li":  # line 1013
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 1013
        elif command[:2] == "ls":  # line 1014
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 1014
        elif command[:1] == "m":  # mvnot  # line 1015
            move(relPath, pattern, newRelPath, newPattern, options, negative="n" in command)  # mvnot  # line 1015
        elif command[:2] == "of":  # line 1016
            offline(arguments[0], arguments[1], options)  # line 1016
        elif command[:2] == "on":  # line 1017
            online(options)  # line 1017
        elif command[:1] == "r":  # rmnot  # line 1018
            remove(relPath, pattern, negative="n" in command)  # rmnot  # line 1018
        elif command[:2] == "st":  # line 1019
            status(arguments[0], cwd, cmd, options, onlys, excps)  # line 1019
        elif command[:2] == "sw":  # line 1020
            switch(arguments[0], options, onlys, excps)  # line 1020
        elif command[:1] == "u":  # line 1021
            update(arguments[0], options, onlys, excps)  # line 1021
        elif command[:1] == "v":  # line 1022
            usage(APPNAME, version.__version__, short=True)  # line 1022
        else:  # line 1023
            Exit("Unknown command '%s'" % command)  # line 1023
        Exit(code=0)  # regular exit  # line 1024
    except (Exception, RuntimeError) as E:  # line 1025
        exception(E)  # line 1026
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing")  # line 1027

def main():  # line 1029
    global debug, info, warn, error  # to modify logger  # line 1030
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 1031
    _log = Logger(logging.getLogger(__name__))  # line 1032
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1032
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 1033
        sys.argv.remove(option)  # clean up program arguments  # line 1033
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 1034
        usage(APPNAME, version.__version__)  # line 1034
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 1035
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 1036
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 1037
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 1038
    defaults["useChangesCommand"] = cmd == "fossil"  # sets dynamic default with SVN fallback  # line 1039
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in "hv":  # in offline mode or just going offline TODO what about git config?  # line 1040
        cwd = os.getcwd()  # line 1041
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 1042
        parse(root, cwd, cmd)  # line 1043
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 1044
        info("%s: Running '%s %s'" % (COMMAND.upper(), cmd, " ".join(sys.argv[1:])))  # line 1045
        import subprocess  # only required in this section  # line 1046
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 1047
        inp = ""  # type: str  # line 1048
        while True:  # line 1049
            so, se = process.communicate(input=inp)  # line 1050
            if process.returncode is not None:  # line 1051
                break  # line 1051
            inp = sys.stdin.read()  # line 1052
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 1053
            if root is None:  # line 1054
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 1054
            m = Metadata(root)  # type: Metadata  # line 1055
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 1056
            m.saveBranches()  # line 1057
    else:  # line 1058
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 1058


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 1062
level = logging.DEBUG if verbose else logging.INFO  # line 1063
force_sos = '--sos' in sys.argv  # type: bool  # line 1064
force_vcs = '--vcs' in sys.argv  # type: bool  # line 1065
_log = Logger(logging.getLogger(__name__))  # line 1066
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1066
if __name__ == '__main__':  # line 1067
    main()  # line 1067
