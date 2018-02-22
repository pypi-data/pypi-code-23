#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x9de0a784

# Compiled with Coconut version 1.3.1-post_dev19 [Dead Parrot]

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

    singleton = None  # type: _coconut.typing.Optional[configr.Configr]  # line 44

    def __init__(_, path: '_coconut.typing.Optional[str]'=None, offline: 'bool'=False):  # line 46
        ''' Create empty container object for various repository operations, and import configuration. '''  # line 47
        _.root = (os.getcwd() if path is None else path)  # type: str  # line 48
        _.tags = []  # type: List[str]  # list of known (unique) tags  # line 49
        _.branch = None  # type: _coconut.typing.Optional[int]  # current branch number  # line 50
        _.branches = {}  # type: Dict[int, BranchInfo]  # branch number zero represents the initial state at branching  # line 51
        _.repoConf = {}  # type: Dict[str, Any]  # line 52
        _.track = None  # type: bool  # line 53
        _.picky = None  # type: bool  # line 53
        _.strict = None  # type: bool  # line 53
        _.compress = None  # type: bool  # line 53
        _.version = None  # type: _coconut.typing.Optional[str]  # line 53
        _.format = None  # type: _coconut.typing.Optional[int]  # line 53
        _.loadBranches(offline=offline)  # loads above values from repository, or uses application defaults  # line 54

        _.commits = {}  # type: Dict[int, CommitInfo]  # consecutive numbers per branch, starting at 0  # line 56
        _.paths = {}  # type: Dict[str, PathInfo]  # utf-8 encoded relative, normalized file system paths  # line 57
        _.commit = None  # type: _coconut.typing.Optional[int]  # current revision number  # line 58

        if Metadata.singleton is None:  # only load once  # line 60
            Metadata.singleton = configr.Configr(data=_.repoConf, defaults=loadConfig())  # load global configuration with defaults behind the local configuration  # line 61
        _.c = Metadata.singleton  # type: configr.Configr  # line 62

    def isTextType(_, filename: 'str') -> 'bool':  # line 64
        return (((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(mimetypes.guess_type(filename)[0])).startswith("text/") or any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.texttype])) and not any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.bintype])  # line 64

    def listChanges(_, changes: 'ChangeSet'):  # line 66
        moves = dict(changes.moves.values())  # type: Dict[str, PathInfo]  # line 67
        realadditions = {k: v for k, v in changes.additions.items() if k not in changes.moves}  # type: Dict[str, PathInfo]  # line 68
        realdeletions = {k: v for k, v in changes.deletions.items() if k not in moves}  # type: Dict[str, PathInfo]  # line 69
        if len(changes.moves) > 0:  # line 70
            printo(ajoin("MOV ", ["%s  <-  %s" % (path, dpath) for path, (dpath, dinfo) in sorted(changes.moves.items())], "\n"))  # line 70
        if len(realadditions) > 0:  # line 71
            printo(ajoin("ADD ", sorted(realadditions.keys()), "\n"))  # line 71
        if len(realdeletions) > 0:  # line 72
            printo(ajoin("DEL ", sorted(realdeletions.keys()), "\n"))  # line 72
        if len(changes.modifications) > 0:  # line 73
            printo(ajoin("MOD ", sorted(changes.modifications.keys()), "\n"))  # line 73

    def loadBranches(_, offline: 'bool'=False):  # line 75
        ''' Load list of branches and current branch info from metadata file. offline = offline command avoids message. '''  # line 76
        try:  # fails if not yet created (on initial branch/commit)  # line 77
            branches = None  # type: List[List]  # deserialized JSON is only list, while the real type of _.branches is a dict number -> BranchInfo (Coconut data type/named tuple)  # line 78
            with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "r", encoding=UTF8) as fd:  # line 79
                repo, branches, config = json.load(fd)  # line 80
            _.tags = repo["tags"]  # list of commit messages to treat as globally unique tags  # line 81
            _.branch = repo["branch"]  # current branch integer  # line 82
            _.track, _.picky, _.strict, _.compress, _.version, _.format = [repo.get(r, None) for r in ["track", "picky", "strict", "compress", "version", "format"]]  # line 83
            upgraded = []  # type: List[str]  # line 84
            if _.version is None:  # line 85
                _.version = "0 - pre-1.2"  # line 86
                upgraded.append("pre-1.2")  # line 87
            if len(branches[0]) < 6:  # For older versions, see https://pypi.python.org/simple/sos-vcs/  # line 88
                branches[:] = [branch + [[]] * (6 - len(branch)) for branch in branches]  # add untracking information, if missing  # line 89
                upgraded.append("2018.1210.3028")  # line 90
            if _.format is None:  # must be before 1.3.5+  # line 91
                _.format = METADATA_FORMAT  # marker for first metadata file format  # line 92
                branches[:] = [branch + [None] * (8 - len(branch)) for branch in branches]  # adds empty branching point information (branch/revision)  # line 93
                upgraded.append("1.3.5")  # line 94
            _.branches = {i.number: i for i in (BranchInfo(*item) for item in branches)}  # re-create type info  # line 95
            _.repoConf = config  # line 96
            if upgraded:  # line 97
                for upgrade in upgraded:  # line 98
                    warn("!!! Upgraded repository metadata to match SOS version %r" % upgrade)  # line 98
                warn("To revert the metadata upgrade%s, restore %s/%s from %s/%s NOW" % ("s" if len(upgraded) > 1 else "", metaFolder, metaFile, metaFolder, metaBack))  # line 99
                _.saveBranches()  # line 100
        except Exception as E:  # if not found, create metadata folder with default values  # line 101
            _.branches = {}  # line 102
            _.track, _.picky, _.strict, _.compress, _.version, _.format = [defaults[k] for k in ["track", "picky", "strict", "compress"]] + [version.__version__, METADATA_FORMAT]  # line 103
            (debug if offline else warn)("Couldn't read branches metadata: %r" % E)  # line 104

    def saveBranches(_, also: 'Dict[str, Any]'={}):  # line 106
        ''' Save list of branches and current branch info to metadata file. '''  # line 107
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # backup  # line 108
        with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "w", encoding=UTF8) as fd:  # line 109
            store = {"tags": _.tags, "branch": _.branch, "track": _.track, "picky": _.picky, "strict": _.strict, "compress": _.compress, "version": _.version, "format": METADATA_FORMAT}  # type: Dict[str, Any]  # line 110
            store.update(also)  # allows overriding certain values at certain points in time  # line 114
            json.dump((store, list(_.branches.values()), _.repoConf), fd, ensure_ascii=False)  # stores using unicode codepoints, fd knows how to encode them  # line 115

    def getRevisionByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 117
        ''' Convenience accessor for named revisions (using commit message as name as a convention). '''  # line 118
        if name == "":  # line 119
            return -1  # line 119
        try:  # attempt to parse integer string  # line 120
            return int(name)  # attempt to parse integer string  # line 120
        except ValueError:  # line 121
            pass  # line 121
        found = [number for number, commit in _.commits.items() if name == commit.message]  # find any revision by commit message (usually used for tags)  # HINT allows finding any message, not only tagged ones  # line 122
        return found[0] if found else None  # line 123

    def getBranchByName(_, name: 'str') -> '_coconut.typing.Optional[int]':  # line 125
        ''' Convenience accessor for named branches. '''  # line 126
        if name == "":  # current  # line 127
            return _.branch  # current  # line 127
        try:  # attempt to parse integer string  # line 128
            return int(name)  # attempt to parse integer string  # line 128
        except ValueError:  # line 129
            pass  # line 129
        found = [number for number, branch in _.branches.items() if name == branch.name]  # line 130
        return found[0] if found else None  # line 131

    def loadBranch(_, branch: 'int'):  # line 133
        ''' Load all commit information from a branch meta data file. '''  # line 134
        with codecs.open(encode(branchFolder(branch, file=metaFile)), "r", encoding=UTF8) as fd:  # line 135
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 136
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 137
        _.branch = branch  # line 138

    def saveBranch(_, branch: 'int'):  # line 140
        ''' Save all commits to a branch meta data file. '''  # line 141
        tryOrIgnore(lambda: shutil.copy2(encode(branchFolder(branch, file=metaFile)), encode(branchFolder(branch, metaBack))))  # backup  # line 142
        with codecs.open(encode(branchFolder(branch, file=metaFile)), "w", encoding=UTF8) as fd:  # line 143
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 144

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None, full: 'bool'=True):  # line 146
        ''' Create branch from an existing branch/revision.
        In case of full branching, copy all revisions, otherwise create only reference to originating branch/revision.
        branch: new target branch number (must not exist yet)
        name: optional name of new branch (currently always set by caller)
        initialMessage: message for commit if not last and file tree modified
        full: always create full branch copy, don't use a parent reference
        _.branch: current branch
    '''  # line 154
        debug("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 155
        now = int(time.time() * 1000)  # type: int  # line 156
        _.loadBranch(_.branch)  # load commits for current (originating) branch  # line 157
        revision = max(_.commits)  # type: int  # line 158
        _.commits.clear()  # line 159
        newBranch = dataCopy(BranchInfo, _.branches[_.branch], number=branch, ctime=now, name=("Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)) if name is None else name), tracked=[t for t in _.branches[_.branch].tracked], untracked=[u for u in _.branches[_.branch].untracked], parent=None if full else _.branch, revision=None if full else revision)  # type: BranchInfo  # line 160
        os.makedirs(encode(revisionFolder(branch, 0, base=_.root) if full else branchFolder(branch, base=_.root)))  # line 165
        if full:  # not fast branching via reference - copy all current files to new branch  # line 166
            _.computeSequentialPathSet(_.branch, revision)  # full set of files in latest revision in _.paths  # line 167
            for path, pinfo in _.paths.items():  # copy into initial branch revision  # line 168
                _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # copy into initial branch revision  # line 168
            _.commits[0] = CommitInfo(0, now, ("Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)) if initialMessage is None else initialMessage))  # store initial commit TODO also contain message from latest revision of originating branch  # line 169
            _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 170
        _.saveBranch(branch)  # save branch meta data to branch folder - for fast branching, only empty dict  # line 171
        _.branches[branch] = newBranch  # save branches meta data, needs to be saved in caller code  # line 172

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 174
        ''' Create a new branch from the current file tree. This clears all known commits and modifies the file system.
        branch: target branch number (must not exist yet)
        name: optional name of new branch
        initialMessage: commit message for revision 0 of the new branch
        _.branch: current branch, must exist already
    '''  # line 180
        now = int(time.time() * 1000)  # type: int  # line 181
        simpleMode = not (_.track or _.picky)  # line 182
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # in case of initial branch creation  # line 183
        untracked = [t for t in _.branches[_.branch].untracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # line 184
        debug((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 185
        _.paths = {}  # type: Dict[str, PathInfo]  # line 186
        if simpleMode:  # branches from file system state  # line 187
            changes, msg = _.findChanges(branch, 0, progress=simpleMode)  # creates revision folder and versioned files  # line 188
            _.listChanges(changes)  # line 189
            if msg:  # display compression factor  # line 190
                printo(msg)  # display compression factor  # line 190
            _.paths.update(changes.additions.items())  # line 191
        else:  # tracking or picky mode: branch from latest revision  # line 192
            os.makedirs(encode(revisionFolder(branch, 0, base=_.root)))  # line 193
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 194
                _.loadBranch(_.branch)  # line 195
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 196
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 197
                for path, pinfo in _.paths.items():  # line 198
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 199
        _.commits = {0: CommitInfo(0, now, ("Branched on %s" % strftime(now) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 200
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 201
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 202
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked, untracked)  # save branch info, in case it is needed  # line 203

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 205
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 206
        binfo = None  # type: BranchInfo  # line 207
        deps = [(binfo.number, binfo.revision) for binfo in _.branches.values() if binfo.parent is not None and _.getParentBranch(binfo.number, 0) == branch]  # type: List[Tuple[int, int]]  # get transitively depending branches  # line 208
        if deps:  # need to copy all parent revisions to dependet branches first  # line 209
            minrev = min([e[1] for e in deps])  # type: int  # minimum revision ever branched from parent (ignoring transitive branching!)  # line 210
            progress = ProgressIndicator(PROGRESS_MARKER[1 if _.c.useUnicodeFont else 0])  # type: ProgressIndicator  # line 211
            for rev in range(0, minrev + 1):  # rely on caching by copying revision-wise as long as needed in all depending branches  # line 212
                for dep, _rev in deps:  # line 213
                    if rev <= _rev:  # line 214
                        printo("\rIntegrating revision %02d into dependant branch %02d %s" % (rev, dep, progress.getIndicator()))  # line 215
                        shutil.copytree(encode(revisionFolder(branch, rev, base=_.root)), encode(revisionFolder(dep, rev, base=_.root)))  # folder would not exist yet  # line 216
            for dep, _rev in deps:  # copy remaining revisions per branch  # line 217
                for rev in range(minrev + 1, _rev + 1):  # line 218
                    printo("\rIntegrating revision %02d into dependant branch %02d %s" % (rev, dep, progress.getIndicator()))  # line 219
                    shutil.copytree(encode(revisionFolder(_.getParentBranch(dep, rev), rev, base=_.root)), encode(revisionFolder(dep, rev, base=_.root)))  # line 220
                _.branches[dep] = dataCopy(BranchInfo, _.branches[dep], parent=None, revision=None)  # remove reference information  # line 221
        printo(" " * termWidth + "\r")  # line 222
        tryOrIgnore(lambda: shutil.rmtree(encode(branchFolder(branch) + BACKUP_SUFFIX)))  # remove previous backup first  # line 223
        os.rename(encode(branchFolder(branch)), encode(branchFolder(branch) + BACKUP_SUFFIX))  # line 224
        binfo = _.branches[branch]  # keep reference for caller  # line 225
        del _.branches[branch]  # line 226
        _.branch = max(_.branches)  # switch to another valid branch  # line 227
        _.saveBranches()  # line 228
        _.commits.clear()  # line 229
        return binfo  # line 230

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 232
        ''' Load all file information from a commit meta data; if branched from another branch before specified revision, load correct revision recursively. '''  # line 233
        _branch = _.getParentBranch(branch, revision)  # type: int  # line 234
        with codecs.open(encode(revisionFolder(_branch, revision, base=_.root, file=metaFile)), "r", encoding=UTF8) as fd:  # line 235
            _.paths = json.load(fd)  # line 235
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 236
        _.branch = branch  # store current branch information = "switch" to loaded branch/commit  # line 237

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 239
        ''' Save all file information to a commit meta data file. '''  # line 240
        target = revisionFolder(branch, revision, base=_.root)  # type: str  # line 241
        try:  # line 242
            os.makedirs(encode(target))  # line 242
        except:  # line 243
            pass  # line 243
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(target, metaFile)), encode(os.path.join(target, metaBack))))  # ignore error for first backup  # line 244
        with codecs.open(encode(os.path.join(target, metaFile)), "w", encoding=UTF8) as fd:  # line 245
            json.dump(_.paths, fd, ensure_ascii=False)  # line 245

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'Tuple[ChangeSet, _coconut.typing.Optional[str]]':  # line 247
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes (always overrides considerOnly)
        progress: Show file names during processing
        returns: (ChangeSet = the state of file tree *differences*, unless "inverse" is True -> then return original data, message)
    '''  # line 256
        write = branch is not None and revision is not None  # line 257
        if write:  # line 258
            try:  # line 259
                os.makedirs(encode(revisionFolder(branch, revision, base=_.root)))  # line 259
            except FileExistsError:  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 260
                pass  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 260
        changes = ChangeSet({}, {}, {}, {})  # type: ChangeSet  # TODO Needs explicity initialization due to mypy problems with default arguments :-(  # line 261
        indicator = ProgressIndicator(PROGRESS_MARKER[1 if _.c.useUnicodeFont else 0]) if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # optional file list progress indicator  # line 262
        hashed = None  # type: _coconut.typing.Optional[str]  # line 263
        written = None  # type: int  # line 263
        compressed = 0  # type: int  # line 263
        original = 0  # type: int  # line 263
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 264
        for path, pinfo in _.paths.items():  # line 265
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 266
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 269
        for path, dirnames, filenames in os.walk(_.root):  # line 270
            path = decode(path)  # line 271
            dirnames[:] = [decode(d) for d in dirnames]  # line 272
            filenames[:] = [decode(f) for f in filenames]  # line 273
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 274
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 275
            dirnames.sort()  # line 276
            filenames.sort()  # line 276
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # line 277
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 278
            if dontConsider:  # line 279
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 280
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 281
                filename = relPath + SLASH + file  # line 282
                filepath = os.path.join(path, file)  # line 283
                try:  # line 284
                    stat = os.stat(encode(filepath))  # line 284
                except Exception as E:  # line 285
                    exception(E)  # line 285
                    continue  # line 285
                size, mtime = stat.st_size, int(stat.st_mtime * 1000)  # line 286
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 287
                if show:  # indication character returned  # line 288
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", show, filename)  # line 289
                    printo(outstring + " " * max(0, termWidth - len(outstring)), nl="")  # line 290
                progressSymbols = PROGRESS_MARKER[1 if _.c.useUnicodeFont else 0]  # type: str  # line 291
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 292
                    nameHash = hashStr(filename)  # line 293
                    try:  # line 294
                        hashed, written = hashFile(filepath, _.compress, symbols=progressSymbols, saveTo=revisionFolder(branch, revision, base=_.root, file=nameHash) if write else None, callback=(lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if show else None) if size > 0 else (None, 0)  # line 295
                        changes.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 296
                        compressed += written  # line 297
                        original += size  # line 297
                    except Exception as E:  # line 298
                        exception(E)  # line 298
                    continue  # with next file  # line 299
                last = _.paths[filename]  # filename is known - check for modifications  # line 300
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 301
                    try:  # line 302
                        hashed, written = hashFile(filepath, _.compress, symbols=progressSymbols, saveTo=revisionFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 303
                        changes.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 304
                        continue  # line 304
                    except Exception as E:  # line 305
                        exception(E)  # line 305
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and tryOrDefault(lambda: (hashFile(filepath, _.compress, symbols=progressSymbols)[0] != last.hash), default=False)):  # detected a modification TODO wrap hashFile exception  # line 306
                    try:  # line 307
                        hashed, written = hashFile(filepath, _.compress, symbols=progressSymbols, saveTo=revisionFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - len(outstring) - 2), nl="")) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 308
                        changes.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 309
                    except Exception as E:  # line 310
                        exception(E)  # line 310
                else:  # with next file  # line 311
                    continue  # with next file  # line 311
                compressed += written  # line 312
                original += last.size if inverse else size  # line 312
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 313
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 313
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 314
            for file in names:  # line 315
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 316
                    continue  # don't mark ignored files as deleted  # line 316
                pth = path + SLASH + file  # type: str  # line 317
                changes.deletions[pth] = _.paths[pth]  # line 318
        changes = dataCopy(ChangeSet, changes, moves=detectMoves(changes))  # line 319
        if progress:  # forces clean line of progress output  # line 320
            printo("\r" + " " * termWidth + "\r", nl="")  # forces clean line of progress output  # line 320
        else:  # line 321
            debug("Finished detecting changes")  # line 321
        return (changes, ("Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else None)  # line 322

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 324
        ''' Returns nothing, just updates _.paths in place. '''  # line 325
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 326

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 328
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 329
        _.loadCommit(branch, 0)  # load initial paths  # line 330
        if incrementally:  # line 331
            yield _.paths  # line 331
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 332
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 332
        for rev in range(1, revision + 1):  # line 333
            m.loadCommit(_.getParentBranch(branch, rev), rev)  # line 334
            for p, info in m.paths.items():  # line 335
                if info.size == None:  # line 336
                    del _.paths[p]  # line 336
                else:  # line 337
                    _.paths[p] = info  # line 337
            if incrementally:  # line 338
                yield _.paths  # line 338
        yield None  # for the default case - not incrementally  # line 339

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None, negative: 'bool'=False) -> 'FrozenSet[str]':  # line 341
        ''' Returns list of tracking patterns (or untracking patterns if negative) for provided branch or current branch. '''  # line 342
        return _coconut.frozenset() if not (_.track or _.picky) else frozenset(_.branches[(_.branch if branch is None else branch)].untracked if negative else _.branches[(_.branch if branch is None else branch)].tracked)  # line 343

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 345
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 348
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 349
            return (_.branch, -1)  # no branch/revision specified  # line 349
        argument = argument.strip()  # line 350
        if argument.startswith(SLASH):  # current branch  # line 351
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 351
        if argument.endswith(SLASH):  # line 352
            try:  # line 353
                return (_.getBranchByName(argument[:-1]), -1)  # line 353
            except ValueError:  # line 354
                Exit("Unknown branch label '%s'" % argument)  # line 354
        if SLASH in argument:  # line 355
            b, r = argument.split(SLASH)[:2]  # line 356
            try:  # line 357
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 357
            except ValueError:  # line 358
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 358
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 359
        if branch not in _.branches:  # line 360
            branch = None  # line 360
        try:  # either branch name/number or reverse/absolute revision number  # line 361
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 361
        except:  # line 362
            Exit("Unknown branch label or wrong number format")  # line 362
        Exit("This should never happen. Please create a issue report")  # line 363
        return (None, None)  # line 363

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 365
        while True:  # find latest revision that contained the file physically  # line 366
            _branch = _.getParentBranch(branch, revision)  # type: int  # line 367
            source = revisionFolder(_branch, revision, base=_.root, file=nameHash)  # type: str  # line 368
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 369
                break  # line 369
            revision -= 1  # line 370
            if revision < 0:  # line 371
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 371
        return revision, source  # line 372

    def getParentBranch(_, branch: 'int', revision: 'int') -> 'int':  # line 374
        ''' Determine originating branch for a (potentially branched) revision, traversing all branch parents until found. '''  # line 375
        other = _.branches[branch].parent  # type: _coconut.typing.Optional[int]  # reference to originating parent branch, or None  # line 376
        if other is None or revision > _.branches[branch].revision:  # need to load commit from other branch instead  # line 377
            return branch  # need to load commit from other branch instead  # line 377
        while _.branches[other].parent is not None and revision <= _.branches[other].revision:  # line 378
            other = _.branches[other].parent  # line 378
        return other  # line 379

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 381
        ''' Copy versioned file to other branch/revision. '''  # line 382
        target = revisionFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 383
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 384
        shutil.copy2(encode(source), encode(target))  # line 385

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 387
        ''' Return file contents, or copy contents into file path provided. '''  # line 388
        source = revisionFolder(_.getParentBranch(branch, revision), revision, base=_.root, file=nameHash)  # type: str  # line 389
        try:  # line 390
            with openIt(source, "r", _.compress) as fd:  # line 391
                if toFile is None:  # read bytes into memory and return  # line 392
                    return fd.read()  # read bytes into memory and return  # line 392
                with open(encode(toFile), "wb") as to:  # line 393
                    while True:  # line 394
                        buffer = fd.read(bufSize)  # line 395
                        to.write(buffer)  # line 396
                        if len(buffer) < bufSize:  # line 397
                            break  # line 397
                    return None  # line 398
        except Exception as E:  # line 399
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 399
        return None  # line 400

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 402
        ''' Recreate file for given revision, or return binary contents if path is None. '''  # line 403
        if relPath is None:  # just return contents  # line 404
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 404
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 405
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 406
            try:  # line 407
                os.makedirs(encode(os.path.dirname(target)))  # line 407
            except:  # line 408
                pass  # line 408
        if pinfo.size == 0:  # line 409
            with open(encode(target), "wb"):  # line 410
                pass  # line 410
            try:  # update access/modification timestamps on file system  # line 411
                os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 411
            except Exception as E:  # line 412
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 412
            return None  # line 413
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 414
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 416
            while True:  # line 417
                buffer = fd.read(bufSize)  # line 418
                to.write(buffer)  # line 419
                if len(buffer) < bufSize:  # line 420
                    break  # line 420
        try:  # update access/modification timestamps on file system  # line 421
            os.utime(target, (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 421
        except Exception as E:  # line 422
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 422
        return None  # line 423


# Main client operations
def offline(name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 427
    ''' Initial command to start working offline. '''  # line 428
    if os.path.exists(encode(metaFolder)):  # line 429
        if '--force' not in options:  # line 430
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 430
        try:  # line 431
            for entry in os.listdir(metaFolder):  # line 432
                resource = metaFolder + os.sep + entry  # line 433
                if os.path.isdir(resource):  # line 434
                    shutil.rmtree(encode(resource))  # line 434
                else:  # line 435
                    os.unlink(encode(resource))  # line 435
        except:  # line 436
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 436
    m = Metadata(offline=True)  # type: Metadata  # line 437
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 438
        m.compress = True  # plain file copies instead of compressed ones  # line 438
    if '--picky' in options or m.c.picky:  # Git-like  # line 439
        m.picky = True  # Git-like  # line 439
    elif '--track' in options or m.c.track:  # Svn-like  # line 440
        m.track = True  # Svn-like  # line 440
    if '--strict' in options or m.c.strict:  # always hash contents  # line 441
        m.strict = True  # always hash contents  # line 441
    debug(MARKER + "Going offline...")  # line 442
    m.createBranch(0, (defaults["defaultbranch"] if name is None else name), ("Offline repository created on %s" % strftime() if initialMessage is None else initialMessage))  # main branch's name may be None (e.g. for fossil)  # line 443
    m.branch = 0  # line 444
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 445
    info(MARKER + "Offline repository prepared. Use 'sos online' to finish offline work")  # line 446

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 448
    ''' Finish working offline. '''  # line 449
    debug(MARKER + "Going back online...")  # line 450
    force = '--force' in options  # type: bool  # line 451
    m = Metadata()  # type: Metadata  # line 452
    strict = '--strict' in options or m.strict  # type: bool  # line 453
    m.loadBranches()  # line 454
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 455
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 455
    m.loadBranch(m.branch)  # line 456
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # one commit guaranteed for first offline branch, for fast-branched branches a revision in branchinfo  # line 457
    if options.count("--force") < 2:  # line 458
        m.computeSequentialPathSet(m.branch, maxi)  # load all commits up to specified revision  # line 459
        changes, msg = m.findChanges(checkContent=strict, considerOnly=None if not (m.track or m.picky) else m.getTrackingPatterns(), dontConsider=None if not (m.track or m.picky) else m.getTrackingPatterns(negative=True), progress='--progress' in options)  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 460
        if modified(changes):  # line 461
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 465
    try:  # line 466
        shutil.rmtree(encode(metaFolder))  # line 466
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 466
    except Exception as E:  # line 467
        Exit("Error removing offline repository: %r" % E)  # line 467
    info(MARKER + "Offline repository removed, you're back online")  # line 468

def branch(name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 470
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it.
      Force not necessary, as either branching from last  revision anyway, or branching file tree anyway.
  '''  # line 473
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 474
    stay = '--stay' in options  # type: bool  # continue on current branch after branching (don't switch)  # line 475
    fast = '--fast' in options  # type: bool  # branch by referencing TODO move to default and use --full instead for old behavior  # line 476
    m = Metadata()  # type: Metadata  # line 477
    m.loadBranch(m.branch)  # line 478
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # line 479
    if name and m.getBranchByName(name) is not None:  # attempted to create a named branch  # line 480
        Exit("Branch '%s' already exists. Cannot proceed" % name)  # attempted to create a named branch  # line 480
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 481
    debug(MARKER + "Branching to %sbranch b%02d%s%s..." % ("unnamed " if name is None else "", branch, " '%s'" % name if name is not None else "", " from last revision" if last else ""))  # line 482
    if last:  # branch from last revision  # line 483
        m.duplicateBranch(branch, name, (initialMessage + " " if initialMessage else "") + "(Branched from r%02d/b%02d)" % (m.branch, maxi), not fast)  # branch from last revision  # line 483
    else:  # branch from current file tree state  # line 484
        m.createBranch(branch, name, ("Branched from file tree after r%02d/b%02d" % (m.branch, maxi) if initialMessage is None else initialMessage))  # branch from current file tree state  # line 484
    if not stay:  # line 485
        m.branch = branch  # line 485
    m.saveBranches()  # TODO or indent again?  # line 486
    info(MARKER + "%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if name is None else "", branch, " '%s'" % name if name else ""))  # line 487

def changes(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 489
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 490
    m = Metadata()  # type: Metadata  # line 491
    branch = None  # type: _coconut.typing.Optional[int]  # line 491
    revision = None  # type: _coconut.typing.Optional[int]  # line 491
    strict = '--strict' in options or m.strict  # type: bool  # line 492
    branch, revision = m.parseRevisionString(argument)  # line 493
    if branch not in m.branches:  # line 494
        Exit("Unknown branch")  # line 494
    m.loadBranch(branch)  # knows commits  # line 495
    revision = m.branches[branch].revision if not m.commits else (revision if revision >= 0 else max(m.commits) + 1 + revision)  # negative indexing  # line 496
    if revision < 0 or (m.commits and revision > max(m.commits)):  # line 497
        Exit("Unknown revision r%02d" % revision)  # line 497
    debug(MARKER + "Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 498
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 499
    changes, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 500
    m.listChanges(changes)  # line 505
    return changes  # for unit tests only TODO remove  # line 506

def _diff(m: 'Metadata', branch: 'int', revision: 'int', changes: 'ChangeSet', ignoreWhitespace: 'bool', textWrap: 'bool'=False):  # TODO introduce option to diff against committed revision  # line 508
    wrap = (lambda s: s) if textWrap else (lambda s: s[:termWidth])  # type: _coconut.typing.Callable[[str], str]  # line 509
    onlyBinaryModifications = dataCopy(ChangeSet, changes, modifications={k: v for k, v in changes.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 510
    m.listChanges(onlyBinaryModifications)  # only list modified binary files  # line 511
    for path, pinfo in (c for c in changes.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 512
        content = None  # type: _coconut.typing.Optional[bytes]  # line 513
        if pinfo.size == 0:  # empty file contents  # line 514
            content = b""  # empty file contents  # line 514
        else:  # versioned file  # line 515
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 515
            assert content is not None  # versioned file  # line 515
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 516
        blocks = None  # type: List[MergeBlock]  # line 517
        nl = None  # type: bytes  # line 517
        blocks, nl = merge(filename=abspath, into=content, diffOnly=True, ignoreWhitespace=ignoreWhitespace)  # only determine change blocks  # line 518
        printo("DIF %s%s  %s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else "", NL_NAMES[nl]))  # line 519
        for block in blocks:  # line 520
#      if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:
#        pass  # TODO print some previous and following lines - which aren't accessible here anymore
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 523
                for no, line in enumerate(block.lines):  # line 524
                    printo(wrap("--- %04d |%s|" % (no + block.line, line)))  # line 524
            elif block.tipe == MergeBlockType.REMOVE:  # line 525
                for no, line in enumerate(block.lines):  # line 526
                    printo(wrap("+++ %04d |%s|" % (no + block.line, line)))  # line 526
            elif block.tipe == MergeBlockType.REPLACE:  # line 527
                for no, line in enumerate(block.replaces.lines):  # line 528
                    printo(wrap("- | %04d |%s|" % (no + block.replaces.line, line)))  # line 528
                for no, line in enumerate(block.lines):  # line 529
                    printo(wrap("+ | %04d |%s|" % (no + block.line, line)))  # line 529
#      elif block.tipe == MergeBlockType.KEEP: pass
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications
            if block.tipe != MergeBlockType.KEEP:  # line 532
                printo()  # line 532

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 534
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 535
    m = Metadata()  # type: Metadata  # line 536
    branch = None  # type: _coconut.typing.Optional[int]  # line 536
    revision = None  # type: _coconut.typing.Optional[int]  # line 536
    strict = '--strict' in options or m.strict  # type: bool  # line 537
    ignoreWhitespace = '--ignore-whitespace' in options or '--iw' in options  # type: bool  # line 538
    wrap = '--wrap' in options  # type: bool  # allow text to wrap around  # line 539
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 540
    if branch not in m.branches:  # line 541
        Exit("Unknown branch")  # line 541
    m.loadBranch(branch)  # knows commits  # line 542
    revision = m.branches[branch].revision if not m.commits else (revision if revision >= 0 else max(m.commits) + 1 + revision)  # negative indexing  # line 543
    if revision < 0 or (m.commits and revision > max(m.commits)):  # line 544
        Exit("Unknown revision r%02d" % revision)  # line 544
    debug(MARKER + "Textual differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 545
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 546
    changes, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 547
    _diff(m, branch, revision, changes, ignoreWhitespace=ignoreWhitespace, textWrap=wrap)  # line 552

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 554
    ''' Create new revision from file tree changes vs. last commit. '''  # line 555
    m = Metadata()  # type: Metadata  # line 556
    if argument is not None and argument in m.tags:  # line 557
        Exit("Illegal commit message. It was already used as a tag name")  # line 557
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 558
# No untracking patterns needed here
    if m.picky and not trackingPatterns:  # line 560
        Exit("No file patterns staged for commit in picky mode")  # line 560
    debug((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 561
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options, check=False, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but aborts if no changes  # line 562
    changes = dataCopy(ChangeSet, changes, moves=detectMoves(changes))  # line 563
    m.paths = {k: v for k, v in changes.additions.items()}  # copy to avoid wrong file numbers report below  # line 564
    m.paths.update(changes.modifications)  # update pathset to changeset only  # line 565
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changes.deletions.items()})  # line 566
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 567
    m.commits[revision] = CommitInfo(revision, int(time.time() * 1000), argument)  # comment can be None  # line 568
    m.saveBranch(m.branch)  # line 569
    m.loadBranches()  # TODO is it necessary to load again?  # line 570
# TODO moved files recognition not used here
    if m.picky:  # remove tracked patterns  # line 572
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 572
    else:  # track or simple mode: set branch dirty  # line 573
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 573
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 574
        m.tags.append(argument)  # memorize unique tag  # line 574
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 574
    m.saveBranches()  # line 575
    printo(MARKER + "Created new revision r%02d%s (+%02d/-%02d/%s%02d/%s%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changes.additions) - len(changes.moves), len(changes.deletions) - len(changes.moves), PLUSMINUS_SYMBOL if m.c.useUnicodeFont else "~", len(changes.modifications), FOLDER_SYMBOL if m.c.useUnicodeFont else "#", len(changes.moves)))  # line 576

def status(argument: '_coconut.typing.Optional[str]'=None, vcs: '_coconut.typing.Optional[str]'=None, cmd: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 578
    ''' Show branches and current repository state. '''  # line 579
    m = Metadata()  # type: Metadata  # line 580
    if not m.c.useChangesCommand and not '--repo' in options:  # TODO for fossil not possible to restore SVN behavior  # line 581
        changes(argument, options, onlys, excps)  # TODO for fossil not possible to restore SVN behavior  # line 581
        return  # TODO for fossil not possible to restore SVN behavior  # line 581
    current = m.branch  # type: int  # line 582
    strict = '--strict' in options or m.strict  # type: bool  # line 583
    info(MARKER + "Offline repository status")  # line 584
    info("Repository root:     %s" % os.getcwd())  # line 585
    info("Underlying VCS root: %s" % vcs)  # line 586
    info("Underlying VCS type: %s" % cmd)  # line 587
    info("Installation path:   %s" % os.path.abspath(os.path.dirname(__file__)))  # line 588
    info("Current SOS version: %s" % version.__version__)  # line 589
    info("At creation version: %s" % m.version)  # line 590
    info("Metadata format:     %s" % m.format)  # line 591
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 592
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 593
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 594
    info("Number of branches:  %d" % len(m.branches))  # line 595
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 596
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 597
    m.loadBranch(current)  # line 598
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # line 599
    m.computeSequentialPathSet(current, maxi)  # load all commits up to specified revision  # line 508  # line 600
    _changes, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress=True)  # line 601
    printo("%s File tree %s" % ((CROSS_SYMBOL if m.c.useUnicodeFont else "!") if modified(_changes) else (CHECKMARK_SYMBOL if m.c.useUnicodeFont else " "), "has changes" if modified(_changes) else "is unchanged"))  # TODO use other marks if no unicode console detected TODO bad choice of symbols for changed vs. unchanged  # line 606
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 607
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 608
        m.loadBranch(branch.number)  # knows commit history  # line 609
        maxi = max(m.commits) if m.commits else m.branches[branch.number].revision  # line 610
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[maxi].message if maxi in m.commits and m.commits[maxi].message else ""))  # line 611
    if m.track or m.picky and (len(m.branches[m.branch].tracked) > 0 or len(m.branches[m.branch].untracked) > 0):  # line 612
        info("\nTracked file patterns:")  # TODO print matching untracking patterns side-by-side  # line 613
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 614
        info("\nUntracked file patterns:")  # line 615
        printo(ajoin("  | ", m.branches[m.branch].untracked, "\n"))  # line 616

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str], FrozenSet[str]]':  # line 618
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags.
  '''  # line 624
    assert not (check and commit)  # line 625
    m = Metadata()  # type: Metadata  # line 626
    force = '--force' in options  # type: bool  # line 627
    strict = '--strict' in options or m.strict  # type: bool  # line 628
    if argument is not None:  # line 629
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 630
        if branch is None:  # line 631
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 631
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 632
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # line 633

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 636
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 637
    m.computeSequentialPathSet(m.branch, maxi)  # load all commits up to specified revision  # line 638
    changes, msg = m.findChanges(m.branch if commit else None, maxi + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress='--progress' in options)  # line 639
    if check and modified(changes) and not force:  # line 644
        m.listChanges(changes)  # line 645
        Exit("File tree contains changes. Use --force to proceed")  # line 646
    elif commit:  # line 647
        if not modified(changes) and not force:  # line 648
            Exit("Nothing to commit")  # line 648
        m.listChanges(changes)  # line 649
        if msg:  # line 650
            printo(msg)  # line 650

    if argument is not None:  # branch/revision specified  # line 652
        m.loadBranch(branch)  # knows commits of target branch  # line 653
        maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # line 654
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 655
        if revision < 0 or revision > maxi:  # line 656
            Exit("Unknown revision r%02d" % revision)  # line 656
        return (m, branch, revision, changes, strict, force, m.getTrackingPatterns(branch), m.getTrackingPatterns(branch, negative=True))  # line 657
    return (m, m.branch, maxi + (1 if commit else 0), changes, strict, force, trackingPatterns, untrackingPatterns)  # line 658

def switch(argument: 'str', options: 'List[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 660
    ''' Continue work on another branch, replacing file tree changes. '''  # line 661
    m, branch, revision, changes, strict, _force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, ["--force"] + options)  # line 662
    force = '--force' in options  # type: bool  # needed as we fake force in above access  # line 663

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 666
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked, untracked=m.branches[branch].untracked)  # line 667
    else:  # full file switch  # line 668
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 669
        todos, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((untrackingPatterns | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 670

# Now check for potential conflicts
        changes.deletions.clear()  # local deletions never create conflicts, modifications always  # line 677
        rms = []  # type: _coconut.typing.Sequence[str]  # local additions can be ignored if restoration from switch would be same  # line 678
        for a, pinfo in changes.additions.items():  # has potential corresponding re-add in switch operation:  # line 679
            if a in todos.deletions and pinfo.size == todos.deletions[a].size and (pinfo.hash == todos.deletions[a].hash if m.strict else pinfo.mtime == todos.deletions[a].mtime):  # line 680
                rms.append(a)  # line 680
        for rm in rms:  # TODO could also silently accept remote DEL for local ADD  # line 681
            del changes.additions[rm]  # TODO could also silently accept remote DEL for local ADD  # line 681
        if modified(changes) and not force:  # line 682
            m.listChanges(changes)  # line 682
            Exit("File tree contains changes. Use --force to proceed")  # line 682
        debug(MARKER + "Switching to branch %sb%02d/r%02d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 683
        if not modified(todos):  # line 684
            info("No changes to current file tree")  # line 685
        else:  # integration required  # line 686
            for path, pinfo in todos.deletions.items():  # line 687
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 688
                printo("ADD " + path)  # line 689
            for path, pinfo in todos.additions.items():  # line 690
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 691
                printo("DEL " + path)  # line 692
            for path, pinfo in todos.modifications.items():  # line 693
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 694
                printo("MOD " + path)  # line 695
    m.branch = branch  # line 696
    m.saveBranches()  # store switched path info  # line 697
    info(MARKER + "Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 698

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 700
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 704
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 705
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 706
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 707
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 708
    m = Metadata()  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 709
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 710
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 711
    debug(MARKER + "Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 712

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 715
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 716
    untrackingUnion = untrackingPatterns | m.getTrackingPatterns(branch, negative=True)  # type: FrozenSet[str]  # line 717
    changes, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingUnion), dontConsider=excps if not (m.track or m.picky) else (untrackingUnion if onlys is None else onlys), progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 718
    if not (mrg.value & MergeOperation.INSERT.value and changes.additions or (mrg.value & MergeOperation.REMOVE.value and changes.deletions) or changes.modifications):  # no file ops  # line 723
        if trackingUnion != trackingPatterns:  # nothing added  # line 724
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 725
        else:  # line 726
            info("Nothing to update")  # but write back updated branch info below  # line 727
    else:  # integration required  # line 728
        for path, pinfo in changes.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 729
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 730
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 730
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 731
        for path, pinfo in changes.additions.items():  # line 732
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 733
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 733
            if mrg.value & MergeOperation.REMOVE.value:  # line 734
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 734
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 735
        for path, pinfo in changes.modifications.items():  # line 736
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 737
            binary = not m.isTextType(path)  # type: bool  # line 738
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 739
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 740
                printo(("MOD " if not binary else "BIN ") + path)  # line 741
                while True:  # line 742
                    printo(into)  # TODO print mtime, size differences?  # line 743
                    op = input(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 744
                    if op in ("it" if binary else "itm"):  # line 745
                        break  # line 745
            if op == "t":  # line 746
                printo("THR " + path)  # blockwise copy of contents  # line 747
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 747
            elif op == "m":  # line 748
                current = None  # type: bytes  # line 749
                with open(encode(into), "rb") as fd:  # TODO slurps file  # line 750
                    current = fd.read()  # TODO slurps file  # line 750
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 751
                if current == file:  # line 752
                    debug("No difference to versioned file")  # line 752
                elif file is not None:  # if None, error message was already logged  # line 753
                    contents = None  # type: bytes  # line 754
                    nl = None  # type: bytes  # line 754
                    contents, nl = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # line 755
                    if contents != current:  # line 756
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 757
                            fd.write(contents)  # TODO write to temp file first, in case writing fails  # line 757
                    else:  # TODO but update timestamp?  # line 758
                        debug("No change")  # TODO but update timestamp?  # line 758
            else:  # mine or wrong input  # line 759
                printo("MNE " + path)  # nothing to do! same as skip  # line 760
    info(MARKER + "Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 761
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 762
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 763
    m.saveBranches()  # line 764

def destroy(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 766
    ''' Remove a branch entirely. '''  # line 767
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options)  # line 768
    if len(m.branches) == 1:  # line 769
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 769
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 770
    if branch is None or branch not in m.branches:  # line 771
        Exit("Cannot delete unknown branch %r" % branch)  # line 771
    debug(MARKER + "Removing branch b%02d%s..." % (branch, " '%s'" % ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name))))  # line 772
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 773
    info(MARKER + "Branch b%02d%s removed" % (branch, " '%s'" % ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(binfo.name))))  # line 774

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[], negative: 'bool'=False):  # line 776
    ''' Add a tracked files pattern to current branch's tracked files. negative means tracking blacklisting. '''  # line 777
    force = '--force' in options  # type: bool  # line 778
    m = Metadata()  # type: Metadata  # line 779
    if not (m.track or m.picky):  # line 780
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 780
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 781
    if pattern in patterns:  # line 782
        Exit("Pattern '%s' already tracked" % pattern)  # line 782
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 783
        Exit("The pattern folder doesn't exist. Use --force to add the file pattern anyway")  # line 783
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 784
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 785
    patterns.append(pattern)  # line 786
    m.saveBranches()  # line 787
    info(MARKER + "Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 788

def remove(relPath: 'str', pattern: 'str', negative: 'bool'=False):  # line 790
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 791
    m = Metadata()  # type: Metadata  # line 792
    if not (m.track or m.picky):  # line 793
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 793
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 794
    if pattern not in patterns:  # line 795
        suggestion = _coconut.set()  # type: Set[str]  # line 796
        for pat in patterns:  # line 797
            if fnmatch.fnmatch(pattern, pat):  # line 798
                suggestion.add(pat)  # line 798
        if suggestion:  # TODO use same wording as in move  # line 799
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 799
        Exit("Tracked pattern '%s' not found" % pattern)  # line 800
    patterns.remove(pattern)  # line 801
    m.saveBranches()  # line 802
    info(MARKER + "Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 803

def ls(folder: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 805
    ''' List specified directory, augmenting with repository metadata. '''  # line 806
    folder = (os.getcwd() if folder is None else folder)  # line 807
    m = Metadata()  # type: Metadata  # line 808
    debug(MARKER + "Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 809
    relPath = relativize(m.root, os.path.join(folder, "-"))[0]  # type: str  # line 810
    if relPath.startswith(os.pardir):  # line 811
        Exit("Cannot list contents of folder outside offline repository")  # line 811
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 812
    untrackingPatterns = m.getTrackingPatterns(negative=True) if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 813
    if '--tags' in options:  # line 814
        printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 815
        return  # line 816
    if '--patterns' in options:  # line 817
        out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 818
        if out:  # line 819
            printo(out)  # line 819
        return  # line 820
    files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 821
    printo("DIR %s" % relPath)  # line 822
    for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 823
        ignore = None  # type: _coconut.typing.Optional[str]  # line 824
        for ig in m.c.ignores:  # line 825
            if fnmatch.fnmatch(file, ig):  # remember first match  # line 826
                ignore = ig  # remember first match  # line 826
                break  # remember first match  # line 826
        if ig:  # line 827
            for wl in m.c.ignoresWhitelist:  # line 828
                if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 829
                    ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 829
                    break  # found a white list entry for ignored file, undo ignoring it  # line 829
        matches = []  # type: List[str]  # line 830
        if not ignore:  # line 831
            for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 832
                if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 833
                    matches.append(os.path.basename(pattern))  # line 833
        matches.sort(key=lambda element: len(element))  # sort in-place  # line 834
        printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else DOT_SYMBOL * 3), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 835

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 837
    ''' List previous commits on current branch. '''  # line 838
    m = Metadata()  # type: Metadata  # line 839
    m.loadBranch(m.branch)  # knows commit history  # line 840
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # one commit guaranteed for first offline branch, for fast-branched branches a revision in branchinfo  # line 841
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 842
    nl = len("%d" % maxi)  # type: int  # determine space needed for revision  # line 843
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, maxi)  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 844
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 845
    commit = None  # type: CommitInfo  # line 846
    for no in range(maxi + 1):  # line 847
        if no in m.commits:  # line 848
            commit = m.commits[no]  # line 848
        else:  # TODO clean this code  # line 849
            n = Metadata()  # type: Metadata  # line 850
            n.loadBranch(n.getParentBranch(m.branch, no))  # line 851
            commit = n.commits[no]  # line 852
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 853
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # line 854
        _add = news - olds  # type: FrozenSet[str]  # line 855
        _del = olds - news  # type: FrozenSet[str]  # line 856
        _mod = frozenset([_ for _, info in nxts.items() if _ in m.paths and m.paths[_].size != info.size and (m.paths[_].hash != info.hash if m.strict else m.paths[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 857
#    _mov:FrozenSet[str] = detectMoves(ChangeSet(nxts, {o: None for o in olds})  # TODO determine moves - can we reuse detectMoves(changes)?
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 859
        printo("  %s r%s @%s (+%02d/-%02d/%s%02d/T%02d) |%s|%s" % ("*" if commit.number == maxi else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), PLUSMINUS_SYMBOL if m.c.useUnicodeFont else "~", len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 860
        if '--changes' in options:  # TODO moves detection?  # line 861
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}, {}))  # TODO moves detection?  # line 861
        if '--diff' in options:  #  _diff(m, changes)  # needs from revision diff  # line 862
            pass  #  _diff(m, changes)  # needs from revision diff  # line 862
        olds = news  # replaces olds for next revision compare  # line 863

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 865
    ''' Exported entire repository as archive for easy transfer. '''  # line 866
    debug(MARKER + "Dumping repository to archive...")  # line 867
    m = Metadata()  # type: Metadata()  # to load the configuration  # line 868
    progress = '--progress' in options  # type: bool  # line 869
    delta = not '--full' in options  # type: bool  # line 870
    import warnings  # line 871
    import zipfile  # line 871
    try:  # HINT zlib is the library that contains the deflated algorithm  # line 872
        import zlib  # HINT zlib is the library that contains the deflated algorithm  # line 872
        compression = zipfile.ZIP_DEFLATED  # HINT zlib is the library that contains the deflated algorithm  # line 872
    except:  # line 873
        compression = zipfile.ZIP_STORED  # line 873

    if argument is None:  # line 875
        Exit("Argument missing (target filename)")  # line 875
    argument = argument if "." in argument else argument + DUMP_FILE  # TODO this logic lacks a bit, "v1.2" would not receive the suffix  # line 876
    entries = []  # type: List[zipfile.ZipInfo]  # line 877
    if os.path.exists(encode(argument)):  # line 878
        try:  # line 879
            debug("Creating backup...")  # line 880
            shutil.copy2(encode(argument), encode(argument + BACKUP_SUFFIX))  # line 881
            if delta:  # line 882
                with zipfile.ZipFile(argument, "r") as _zip:  # list of pure relative paths without leading dot, normal slashes  # line 883
                    entries = _zip.namelist()  # list of pure relative paths without leading dot, normal slashes  # line 883
        except Exception as E:  # line 884
            Exit("Error creating backup copy before dumping. Please resolve and retry. %r" % E)  # line 884
    debug("Dumping revisions...")  # line 885
    if delta:  # don't show duplicate entries warnings  # line 886
        warnings.filterwarnings('ignore', 'Duplicate name.*', UserWarning, "zipfile", 0)  # don't show duplicate entries warnings  # line 886
    with zipfile.ZipFile(argument, "a" if delta else "w", compression) as _zip:  # create  # line 887
        _zip.debug = 0  # no debugging output  # line 888
        _zip.comment = ("Repository dump from %r" % strftime()).encode(UTF8)  # line 889
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 890
        indicator = ProgressIndicator(PROGRESS_MARKER[1 if m.c.useUnicodeFont else 0]) if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 891
        totalsize = 0  # type: int  # line 892
        start_time = time.time()  # type: float  # line 893
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 894
            dirpath = decode(dirpath)  # line 895
            if dirpath.endswith(BACKUP_SUFFIX):  # don't backup backups  # line 896
                continue  # don't backup backups  # line 896
            printo(dirpath.ljust(termWidth))  # TODO improve progress indicator output to | dir | dumpuing file  # line 897
            dirnames[:] = [decode(d) for d in dirnames]  # line 898
            filenames[:] = [decode(f) for f in filenames]  # line 899
            for filename in filenames:  # line 900
                abspath = os.path.join(dirpath, filename)  # type: str  # line 901
                relpath = os.path.relpath(abspath, repopath).replace(os.sep, "/")  # type: str  # line 902
                totalsize += os.stat(encode(abspath)).st_size  # line 903
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 904
                if relpath.endswith(BACKUP_SUFFIX):  # don't backup backups  # line 905
                    continue  # don't backup backups  # line 905
                if not delta or relpath.endswith(metaFile) or relpath not in entries:  # always update metadata, otherwise only add new revision files  # line 906
                    if show:  # line 907
                        printo(("\rDumping %s @%.2f MiB/s %s" % (show, totalsize / (MEBI * (time.time() - start_time)), filename)).ljust(termWidth), nl="")  # line 907
                    _zip.write(abspath, relpath)  # write entry into archive  # line 908
        if delta:  # line 909
            _zip.comment = ("Delta dump from %r" % strftime()).encode(UTF8)  # line 909
    info("\r" + (MARKER + "Finished dumping entire repository @%.2f MiB/s." % (totalsize / (MEBI * (time.time() - start_time)))).ljust(termWidth))  # clean line  # line 910

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 912
    command, key, value = (arguments + [None] * 2)[:3]  # line 913
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 914
        Exit("Unknown config command")  # line 914
    local = "--local" in options  # type: bool  # line 915
    m = Metadata()  # type: Metadata  # loads layered configuration as well. TODO warning if repo not exists  # line 916
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 917
    if command == "set":  # line 918
        if None in (key, value):  # line 919
            Exit("Key or value not specified")  # line 919
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 920
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 920
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 921
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 921
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 922
    elif command == "unset":  # line 923
        if key is None:  # line 924
            Exit("No key specified")  # line 924
        if key not in c.keys():  # HINT: Works on local configurations when used with --local  # line 925
            Exit("Unknown key")  # HINT: Works on local configurations when used with --local  # line 925
        del c[key]  # line 926
    elif command == "add":  # line 927
        if None in (key, value):  # line 928
            Exit("Key or value not specified")  # line 928
        if key not in CONFIGURABLE_LISTS:  # line 929
            Exit("Unsupported key %r" % key)  # line 929
        if key not in c.keys():  # prepare empty list, or copy from global, add new value below  # line 930
            c[key] = [_ for _ in c.__defaults[key]] if local else []  # prepare empty list, or copy from global, add new value below  # line 930
        elif value in c[key]:  # line 931
            Exit("Value already contained, nothing to do")  # line 931
        if ";" in value:  # line 932
            c[key].append(removePath(key, value))  # line 932
        else:  # line 933
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 933
    elif command == "rm":  # line 934
        if None in (key, value):  # line 935
            Exit("Key or value not specified")  # line 935
        if key not in c.keys():  # line 936
            Exit("Unknown key %r" % key)  # line 936
        if value not in c[key]:  # line 937
            Exit("Unknown value %r" % value)  # line 937
        c[key].remove(value)  # line 938
        if local and len(c[key]) == 0 and "--prune" in options:  # remove local enty, to fallback to global  # line 939
            del c[key]  # remove local enty, to fallback to global  # line 939
    else:  # Show or list  # line 940
        if key == "flags":  # list valid configuration items  # line 941
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 941
        elif key == "lists":  # line 942
            printo(", ".join(CONFIGURABLE_LISTS))  # line 942
        elif key == "texts":  # line 943
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 943
        else:  # line 944
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 945
            c = m.c  # always use full configuration chain  # line 946
            try:  # attempt single key  # line 947
                assert key is not None  # line 948
                c[key]  # line 948
                l = key in c.keys()  # type: bool  # line 949
                g = key in c.__defaults.keys()  # type: bool  # line 949
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 950
            except:  # normal value listing  # line 951
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 952
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 953
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 954
                for k, vt in sorted(vals.items()):  # line 955
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 955
                if len(c.keys()) == 0:  # line 956
                    info("No local configuration stored")  # line 956
                if len(c.__defaults.keys()) == 0:  # line 957
                    info("No global configuration stored")  # line 957
        return  # in case of list, no need to store anything  # line 958
    if local:  # saves changes of repoConfig  # line 959
        m.repoConf = c.__map  # saves changes of repoConfig  # line 959
        m.saveBranches()  # saves changes of repoConfig  # line 959
        Exit("OK", code=0)  # saves changes of repoConfig  # line 959
    else:  # global config  # line 960
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 961
        if f is None:  # line 962
            error("Error saving user configuration: %r" % h)  # line 962
        else:  # line 963
            Exit("OK", code=0)  # line 963

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[], negative: 'bool'=False):  # line 965
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique.
      for "mvnot" don't do any renaming (or do?)
  '''  # line 968
    debug(MARKER + "Renaming %r to %r" % (pattern, newPattern))  # line 969
    force = '--force' in options  # type: bool  # line 970
    soft = '--soft' in options  # type: bool  # line 971
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 972
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 972
    m = Metadata()  # type: Metadata  # line 973
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 974
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 975
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 976
    if not matching and not force:  # line 977
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 977
    if not (m.track or m.picky):  # line 978
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 978
    if pattern not in patterns:  # list potential alternatives and exit  # line 979
        for tracked in (t for t in patterns if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 980
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 981
            if alternative:  # line 982
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 982
        if not (force or soft):  # line 983
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 983
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 984
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 985
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 986
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 990
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 991
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 991
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 992
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 993
    if len({st[1] for st in matches}) != len(matches):  # line 994
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 994
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 995
    if os.path.exists(encode(newRelPath)):  # line 996
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 997
        if exists and not (force or soft):  # line 998
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 998
    else:  # line 999
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 999
    if not soft:  # perform actual renaming  # line 1000
        for (source, target) in matches:  # line 1001
            try:  # line 1002
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 1002
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 1003
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 1003
    patterns[patterns.index(pattern)] = newPattern  # line 1004
    m.saveBranches()  # line 1005

def parse(root: 'str', cwd: 'str', cmd: 'str'):  # line 1007
    ''' Main operation. Main has already chdir into VCS root folder, cwd is original working directory for add, rm, mv. '''  # line 1008
    debug("Parsing command-line arguments...")  # line 1009
    try:  # line 1010
        onlys, excps = parseOnlyOptions(cwd, sys.argv)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 1011
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 1012
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: List[_coconut.typing.Optional[str]]  # line 1013
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 1014
        debug("Processing command %r with arguments %r and options %r." % (command, [_ for _ in arguments if _ is not None], options))  # line 1015
        if command[:1] in "amr":  # line 1016
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 1016
        if command[:1] == "m":  # line 1017
            if len(arguments) < 2:  # line 1018
                Exit("Need a second file pattern argument as target for move command")  # line 1018
            newRelPath, newPattern = relativize(root, os.path.join(cwd, arguments[1]))  # line 1019
        arguments[:] = (arguments + [None] * 3)[:3]  # line 1020
        if command[:1] == "a":  # addnot  # line 1021
            add(relPath, pattern, options, negative="n" in command)  # addnot  # line 1021
        elif command[:1] == "b":  # line 1022
            branch(arguments[0], arguments[1], options)  # line 1022
        elif command[:3] == "com":  # line 1023
            commit(arguments[0], options, onlys, excps)  # line 1023
        elif command[:2] == "ch":  # "changes" (legacy)  # line 1024
            changes(arguments[0], options, onlys, excps)  # "changes" (legacy)  # line 1024
        elif command[:2] == "ci":  # line 1025
            commit(arguments[0], options, onlys, excps)  # line 1025
        elif command[:3] == 'con':  # line 1026
            config(arguments, options)  # line 1026
        elif command[:2] == "de":  # line 1027
            destroy(arguments[0], options)  # line 1027
        elif command[:2] == "di":  # line 1028
            diff(arguments[0], options, onlys, excps)  # line 1028
        elif command[:2] == "du":  # line 1029
            dump(arguments[0], options)  # line 1029
        elif command[:1] == "h":  # line 1030
            usage(APPNAME, version.__version__)  # line 1030
        elif command[:2] == "lo":  # line 1031
            log(options)  # line 1031
        elif command[:2] == "li":  # line 1032
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 1032
        elif command[:2] == "ls":  # line 1033
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 1033
        elif command[:1] == "m":  # mvnot  # line 1034
            move(relPath, pattern, newRelPath, newPattern, options, negative="n" in command)  # mvnot  # line 1034
        elif command[:2] == "of":  # line 1035
            offline(arguments[0], arguments[1], options)  # line 1035
        elif command[:2] == "on":  # line 1036
            online(options)  # line 1036
        elif command[:1] == "r":  # rmnot  # line 1037
            remove(relPath, pattern, negative="n" in command)  # rmnot  # line 1037
        elif command[:2] == "st":  # line 1038
            status(arguments[0], cwd, cmd, options, onlys, excps)  # line 1038
        elif command[:2] == "sw":  # line 1039
            switch(arguments[0], options, onlys, excps)  # line 1039
        elif command[:1] == "u":  # line 1040
            update(arguments[0], options, onlys, excps)  # line 1040
        elif command[:1] == "v":  # line 1041
            usage(APPNAME, version.__version__, short=True)  # line 1041
        else:  # line 1042
            Exit("Unknown command '%s'" % command)  # line 1042
        Exit(code=0)  # regular exit  # line 1043
    except (Exception, RuntimeError) as E:  # line 1044
        exception(E)  # line 1045
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing")  # line 1046

def main():  # line 1048
    global debug, info, warn, error  # to modify logger  # line 1049
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 1050
    _log = Logger(logging.getLogger(__name__))  # line 1051
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1051
    for option in (o for o in ['--log', '--verbose', '-v', '--sos'] if o in sys.argv):  # clean up program arguments  # line 1052
        sys.argv.remove(option)  # clean up program arguments  # line 1052
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 1053
        usage(APPNAME, version.__version__)  # line 1053
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 1054
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 1055
    debug("Found root folders for SOS|VCS: %s|%s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 1056
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 1057
    defaults["useChangesCommand"] = cmd == "fossil"  # sets dynamic default with SVN fallback  # line 1058
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in "hv":  # in offline mode or just going offline TODO what about git config?  # line 1059
        cwd = os.getcwd()  # line 1060
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 1061
        parse(root, cwd, cmd)  # line 1062
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 1063
        info("%s: Running '%s %s'" % (COMMAND.upper(), cmd, " ".join(sys.argv[1:])))  # line 1064
        import subprocess  # only required in this section  # line 1065
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 1066
        inp = ""  # type: str  # line 1067
        while True:  # line 1068
            so, se = process.communicate(input=inp)  # line 1069
            if process.returncode is not None:  # line 1070
                break  # line 1070
            inp = sys.stdin.read()  # line 1071
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 1072
            if root is None:  # line 1073
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 1073
            m = Metadata(root)  # type: Metadata  # line 1074
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 1075
            m.saveBranches()  # line 1076
    else:  # line 1077
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 1077


# Main part
verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 1081
level = logging.DEBUG if verbose else logging.INFO  # line 1082
force_sos = '--sos' in sys.argv  # type: bool  # line 1083
force_vcs = '--vcs' in sys.argv  # type: bool  # line 1084
_log = Logger(logging.getLogger(__name__))  # line 1085
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1085
if __name__ == '__main__':  # line 1086
    main()  # line 1086
