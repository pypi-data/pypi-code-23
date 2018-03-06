#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x72161306

# Compiled with Coconut version 1.3.1-post_dev25 [Dead Parrot]

# Coconut Header: -------------------------------------------------------------

import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_cached_module = _coconut_sys.modules.get("__coconut__")
if _coconut_cached_module is not None and _coconut_os_path.dirname(_coconut_cached_module.__file__) != _coconut_file_path:
    del _coconut_sys.modules["__coconut__"]
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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # TODO this looks just wrong, but is currently required  # line 6
try:  # try needed as paths differ when installed via pip TODO investigate further  # line 7
    from sos import version  # line 8
    from sos.utility import *  # line 9
    from sos.usage import *  # line 10
    import sos.utility as _utility  # WARN necessary because "tests" can only mock "sos.utility.input", because "sos" does "import *"" from "utility" and "sos.input" cannot be mocked for some reason  # line 11
except:  # line 12
    import version  # line 13
    from utility import *  # line 14
    from usage import *  # line 15
    import utility as _utility  # line 16

# External dependencies
import configr  # line 19


# Constants
APPNAME = "Subversion Offline Solution V%s (C) Arne Bachmann" % version.__release_version__  # type: str  # line 23


# Functions
def loadConfig() -> 'configr.Configr':  # Accessor when using defaults only  # line 27
    ''' Simplifies loading user-global config from file system or returning application defaults. '''  # line 28
    config = configr.Configr(COMMAND, defaults=defaults)  # type: configr.Configr  # defaults are used if key is not configured, but won't be saved  # line 29
    f, g = config.loadSettings(clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # latter for testing only  # line 30
    if f is None:  # line 31
        debug("Encountered a problem while loading the user configuration: %r" % g)  # line 31
    return config  # line 32

@_coconut_tco  # line 34
def saveConfig(config: 'configr.Configr') -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[Exception]]':  # line 34
    return _coconut_tail_call(config.saveSettings, clientCodeLocation=os.path.abspath(__file__), location=os.environ.get("TEST", None))  # saves global config, not local one  # line 35


# Main data class
class Metadata:  # line 39
    ''' This class doesn't represent the entire repository state in memory,
      but serves as a container for different repo operations,
      using only parts of its attributes at any point in time. Use with care.
  '''  # line 43

    singleton = None  # type: _coconut.typing.Optional[configr.Configr]  # line 45

    def __init__(_, path: '_coconut.typing.Optional[str]'=None, offline: 'bool'=False) -> 'None':  # line 47
        ''' Create empty container object for various repository operations, and import configuration. '''  # line 48
        _.root = (os.getcwd() if path is None else path)  # type: str  # line 49
        _.tags = []  # type: List[str]  # list of known (unique) tags  # line 50
        _.branch = None  # type: _coconut.typing.Optional[int]  # current branch number  # line 51
        _.branches = {}  # type: Dict[int, BranchInfo]  # branch number zero represents the initial state at branching  # line 52
        _.repoConf = {}  # type: Dict[str, Any]  # line 53
        _.track = None  # type: bool  # line 54
        _.picky = None  # type: bool  # line 54
        _.strict = None  # type: bool  # line 54
        _.compress = None  # type: bool  # line 54
        _.version = None  # type: _coconut.typing.Optional[str]  # line 54
        _.format = None  # type: _coconut.typing.Optional[int]  # line 54
        _.loadBranches(offline=offline)  # loads above values from repository, or uses application defaults  # line 55

        _.commits = {}  # type: Dict[int, CommitInfo]  # consecutive numbers per branch, starting at 0  # line 57
        _.paths = {}  # type: Dict[str, PathInfo]  # utf-8 encoded relative, normalized file system paths  # line 58
        _.commit = None  # type: _coconut.typing.Optional[int]  # current revision number  # line 59

        if Metadata.singleton is None:  # only load once  # line 61
            Metadata.singleton = configr.Configr(data=_.repoConf, defaults=loadConfig())  # load global configuration with defaults behind the local configuration  # line 62
        _.c = Metadata.singleton  # type: configr.Configr  # line 63

    def isTextType(_, filename: 'str') -> 'bool':  # line 65
        return (((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(mimetypes.guess_type(filename)[0])).startswith("text/") or any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.texttype])) and not any([fnmatch.fnmatch(filename, pattern) for pattern in _.c.bintype])  # line 65

    def listChanges(_, changed: 'ChangeSet', commitTime: '_coconut.typing.Optional[float]'=None):  # line 67
        ''' List changes. If commitTime (in ms) is defined, also check timestamps of modified files for plausibility (if mtime older than last commit, note so). '''  # line 68
        moves = dict(changed.moves.values())  # type: Dict[str, PathInfo]  # of origin-pathinfo  # line 69
        realadditions = {k: v for k, v in changed.additions.items() if k not in changed.moves}  # type: Dict[str, PathInfo]  # line 70
        realdeletions = {k: v for k, v in changed.deletions.items() if k not in moves}  # type: Dict[str, PathInfo]  # line 71
        if len(changed.moves) > 0:  # line 72
            printo(ajoin("MOV ", ["%s  <-  %s" % (path, dpath) for path, (dpath, dinfo) in sorted(changed.moves.items())], "\n"))  # line 72
        if len(realadditions) > 0:  # line 73
            printo(ajoin("ADD ", sorted(realadditions.keys()), "\n"))  # line 73
        if len(realdeletions) > 0:  # line 74
            printo(ajoin("DEL ", sorted(realdeletions.keys()), "\n"))  # line 74
        if len(changed.modifications) > 0:  # line 75
            printo(ajoin("MOD ", [m if commitTime is None else (m + (" <older than previously committed>" if pi.mtime < _.paths[m].mtime else "") + (" <older than last revision>" if pi.mtime < commitTime else "")) for (m, pi) in sorted(changed.modifications.items())], "\n"))  # line 75

    def loadBranches(_, offline: 'bool'=False):  # line 77
        ''' Load list of branches and current branch info from metadata file. offline = offline command avoids message. '''  # line 78
        try:  # fails if not yet created (on initial branch/commit)  # line 79
            branches = None  # type: List[List]  # deserialized JSON is only list, while the real type of _.branches is a dict number -> BranchInfo (Coconut data type/named tuple)  # line 80
            with codecs.open(encode(os.path.join(_.root, metaFolder, metaFile)), "r", encoding=UTF8) as fd:  # line 81
                repo, branches, config = json.load(fd)  # line 82
            _.tags = repo["tags"]  # list of commit messages to treat as globally unique tags  # line 83
            _.branch = repo["branch"]  # current branch integer  # line 84
            _.track, _.picky, _.strict, _.compress, _.version, _.format = [repo.get(r, None) for r in ["track", "picky", "strict", "compress", "version", "format"]]  # line 85
            upgraded = []  # type: List[str]  # line 86
            if _.version is None:  # line 87
                _.version = "0 - pre-1.2"  # line 88
                upgraded.append("pre-1.2")  # line 89
            if len(branches[0]) < 6:  # For older versions, see https://pypi.python.org/simple/sos-vcs/  # line 90
                branches[:] = [branch + [[]] * (6 - len(branch)) for branch in branches]  # add untracking information, if missing  # line 91
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
                warn("To revert the metadata upgrade%s, restore %s/%s from %s/%s NOW" % ("s" if len(upgraded) > 1 else "", metaFolder, metaFile, metaFolder, metaBack))  # line 101
                _.saveBranches()  # line 102
        except Exception as E:  # if not found, create metadata folder with default values  # line 103
            _.branches = {}  # line 104
            _.track, _.picky, _.strict, _.compress, _.version, _.format = [defaults[k] for k in ["track", "picky", "strict", "compress"]] + [version.__version__, METADATA_FORMAT]  # line 105
            (debug if offline else warn)("Couldn't read branches metadata: %r" % E)  # line 106

    def saveBranches(_, also: 'Dict[str, Any]'={}):  # line 108
        ''' Save list of branches and current branch info to metadata file. '''  # line 109
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(_.root, metaFolder, metaFile)), encode(os.path.join(_.root, metaFolder, metaBack))))  # backup  # line 110
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
        with codecs.open(encode(branchFolder(branch, file=metaFile)), "r", encoding=UTF8) as fd:  # line 137
            commits = json.load(fd)  # type: List[List[Any]]  # list of CommitInfo that needs to be unmarshalled into value types  # line 138
        _.commits = {i.number: i for i in (CommitInfo(*item) for item in commits)}  # re-create type info  # line 139
        _.branch = branch  # line 140

    def saveBranch(_, branch: 'int'):  # line 142
        ''' Save all commits to a branch meta data file. '''  # line 143
        tryOrIgnore(lambda: shutil.copy2(encode(branchFolder(branch, file=metaFile)), encode(branchFolder(branch, metaBack))))  # backup  # line 144
        with codecs.open(encode(branchFolder(branch, file=metaFile)), "w", encoding=UTF8) as fd:  # line 145
            json.dump(list(_.commits.values()), fd, ensure_ascii=False)  # line 146

    def duplicateBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None, full: 'bool'=True):  # line 148
        ''' Create branch from an existing branch/revision.
        In case of full branching, copy all revisions, otherwise create only reference to originating branch/revision.
        branch: new target branch number (must not exist yet)
        name: optional name of new branch (currently always set by caller)
        initialMessage: message for commit if not last and file tree modified
        full: always create full branch copy, don't use a parent reference
        _.branch: current branch
    '''  # line 156
        if verbose:  # line 157
            info("Duplicating branch '%s' to '%s'..." % ((lambda _coconut_none_coalesce_item: ("b%d" % _.branch) if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name), (("b%d" % branch if name is None else name))))  # line 157
        now = int(time.time() * 1000)  # type: int  # line 158
        _.loadBranch(_.branch)  # load commits for current (originating) branch  # line 159
        revision = max(_.commits)  # type: int  # line 160
        _.commits.clear()  # line 161
        newBranch = dataCopy(BranchInfo, _.branches[_.branch], number=branch, ctime=now, name=("Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)) if name is None else name), tracked=[t for t in _.branches[_.branch].tracked], untracked=[u for u in _.branches[_.branch].untracked], parent=None if full else _.branch, revision=None if full else revision)  # type: BranchInfo  # line 162
        os.makedirs(encode(revisionFolder(branch, 0, base=_.root) if full else branchFolder(branch, base=_.root)))  # line 167
        if full:  # not fast branching via reference - copy all current files to new branch  # line 168
            _.computeSequentialPathSet(_.branch, revision)  # full set of files in latest revision in _.paths  # line 169
            for path, pinfo in _.paths.items():  # copy into initial branch revision  # line 170
                _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # copy into initial branch revision  # line 170
            _.commits[0] = CommitInfo(number=0, ctime=now, message=("Branched from '%s'" % ((lambda _coconut_none_coalesce_item: "b%d" % _.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(_.branches[_.branch].name)) if initialMessage is None else initialMessage))  # store initial commit TODO also contain message from latest revision of originating branch  # line 171
            _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 172
        _.saveBranch(branch)  # save branch meta data to branch folder - for fast branching, only empty dict  # line 173
        _.branches[branch] = newBranch  # save branches meta data, needs to be saved in caller code  # line 174

    def createBranch(_, branch: 'int', name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None):  # line 176
        ''' Create a new branch from the current file tree. This clears all known commits and modifies the file system.
        branch: target branch number (must not exist yet)
        name: optional name of new branch
        initialMessage: commit message for revision 0 of the new branch
        _.branch: current branch, must exist already
    '''  # line 182
        now = int(time.time() * 1000)  # type: int  # line 183
        simpleMode = not (_.track or _.picky)  # line 184
        tracked = [t for t in _.branches[_.branch].tracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # in case of initial branch creation  # line 185
        untracked = [t for t in _.branches[_.branch].untracked] if _.track and len(_.branches) > 0 else []  # type: List[str]  # line 186
        if verbose:  # line 187
            info((lambda _coconut_none_coalesce_item: "b%d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)("Creating branch '%s'..." % name))  # line 187
        _.paths = {}  # type: Dict[str, PathInfo]  # line 188
        if simpleMode:  # branches from file system state  # line 189
            changed, msg = _.findChanges(branch, 0, progress=simpleMode)  # creates revision folder and versioned files  # line 190
            _.listChanges(changed)  # line 191
            if msg:  # display compression factor and time taken  # line 192
                printo(msg)  # display compression factor and time taken  # line 192
            _.paths.update(changed.additions.items())  # line 193
        else:  # tracking or picky mode: branch from latest revision  # line 194
            os.makedirs(encode(revisionFolder(branch, 0, base=_.root)))  # line 195
            if _.branch is not None:  # not immediately after "offline" - copy files from current branch  # line 196
                _.loadBranch(_.branch)  # line 197
                revision = max(_.commits)  # type: int  # TODO what if last switch was to an earlier revision? no persisting of last checkout  # line 198
                _.computeSequentialPathSet(_.branch, revision)  # full set of files in revision to _.paths  # line 199
                for path, pinfo in _.paths.items():  # line 200
                    _.copyVersionedFile(_.branch, revision, branch, 0, pinfo)  # line 201
        _.commits = {0: CommitInfo(number=0, ctime=now, message=("Branched on %s" % strftime(now) if initialMessage is None else initialMessage))}  # store initial commit for new branch  # line 202
        _.saveBranch(branch)  # save branch meta data (revisions) to branch folder  # line 203
        _.saveCommit(branch, 0)  # save commit meta data to revision folder  # line 204
        _.branches[branch] = BranchInfo(branch, _.commits[0].ctime, name, True if len(_.branches) == 0 else _.branches[_.branch].inSync, tracked, untracked)  # save branch info, in case it is needed  # line 205

    def removeBranch(_, branch: 'int') -> 'BranchInfo':  # line 207
        ''' Entirely remove a branch and all its revisions from the file system. '''  # line 208
        binfo = None  # type: BranchInfo  # line 209
        deps = [(binfo.number, binfo.revision) for binfo in _.branches.values() if binfo.parent is not None and _.getParentBranch(binfo.number, 0) == branch]  # type: List[Tuple[int, int]]  # get transitively depending branches  # line 210
        if deps:  # need to copy all parent revisions to dependet branches first  # line 211
            minrev = min([e[1] for e in deps])  # type: int  # minimum revision ever branched from parent (ignoring transitive branching!)  # line 212
            progress = ProgressIndicator(PROGRESS_MARKER[1 if _.c.useUnicodeFont else 0])  # type: ProgressIndicator  # line 213
            for rev in range(0, minrev + 1):  # rely on caching by copying revision-wise as long as needed in all depending branches  # line 214
                for dep, _rev in deps:  # line 215
                    if rev <= _rev:  # line 216
                        printo("\rIntegrating revision %02d into dependant branch %02d %s" % (rev, dep, progress.getIndicator()))  # line 217
                        shutil.copytree(encode(revisionFolder(branch, rev, base=_.root)), encode(revisionFolder(dep, rev, base=_.root)))  # folder would not exist yet  # line 218
            for dep, _rev in deps:  # copy remaining revisions per branch  # line 219
                for rev in range(minrev + 1, _rev + 1):  # line 220
                    printo("\rIntegrating revision %02d into dependant branch %02d %s" % (rev, dep, progress.getIndicator()))  # line 221
                    shutil.copytree(encode(revisionFolder(_.getParentBranch(dep, rev), rev, base=_.root)), encode(revisionFolder(dep, rev, base=_.root)))  # line 222
                _.branches[dep] = dataCopy(BranchInfo, _.branches[dep], parent=None, revision=None)  # remove reference information  # line 223
        printo(" " * termWidth + "\r")  # line 224
        tryOrIgnore(lambda: shutil.rmtree(encode(branchFolder(branch) + BACKUP_SUFFIX)))  # remove previous backup first  # line 225
        os.rename(encode(branchFolder(branch)), encode(branchFolder(branch) + BACKUP_SUFFIX))  # line 226
        binfo = _.branches[branch]  # keep reference for caller  # line 227
        del _.branches[branch]  # line 228
        _.branch = max(_.branches)  # switch to another valid branch  # line 229
        _.saveBranches()  # line 230
        _.commits.clear()  # line 231
        return binfo  # line 232

    def loadCommit(_, branch: 'int', revision: 'int'):  # line 234
        ''' Load all file information from a commit meta data; if branched from another branch before specified revision, load correct revision recursively. '''  # line 235
        _branch = _.getParentBranch(branch, revision)  # type: int  # line 236
        with codecs.open(encode(revisionFolder(_branch, revision, base=_.root, file=metaFile)), "r", encoding=UTF8) as fd:  # line 237
            _.paths = json.load(fd)  # line 237
        _.paths = {path: PathInfo(*item) for path, item in _.paths.items()}  # re-create type info  # line 238
        _.branch = branch  # store current branch information = "switch" to loaded branch/commit  # line 239

    def saveCommit(_, branch: 'int', revision: 'int'):  # line 241
        ''' Save all file information to a commit meta data file. '''  # line 242
        target = revisionFolder(branch, revision, base=_.root)  # type: str  # line 243
        try:  # line 244
            os.makedirs(encode(target))  # line 244
        except:  # line 245
            pass  # line 245
        tryOrIgnore(lambda: shutil.copy2(encode(os.path.join(target, metaFile)), encode(os.path.join(target, metaBack))))  # ignore error for first backup  # line 246
        with codecs.open(encode(os.path.join(target, metaFile)), "w", encoding=UTF8) as fd:  # line 247
            json.dump(_.paths, fd, ensure_ascii=False)  # line 247

    def findChanges(_, branch: '_coconut.typing.Optional[int]'=None, revision: '_coconut.typing.Optional[int]'=None, checkContent: 'bool'=False, inverse: 'bool'=False, considerOnly: '_coconut.typing.Optional[FrozenSet[str]]'=None, dontConsider: '_coconut.typing.Optional[FrozenSet[str]]'=None, progress: 'bool'=False) -> 'Tuple[ChangeSet, _coconut.typing.Optional[str]]':  # line 249
        ''' Find changes on the file system vs. in-memory paths (which should reflect the latest commit state).
        Only if both branch and revision are *not* None, write modified/added files to the specified revision folder (thus creating a new revision)
        checkContent: also computes file content hashes
        inverse: retain original state (size, mtime, hash) instead of updated one
        considerOnly: set of tracking patterns. None for simple mode. For update operation, consider union of other and current branch
        dontConsider: set of tracking patterns to not consider in changes (always overrides considerOnly)
        progress: Show file names during processing
        returns: (ChangeSet = the state of file tree *differences*, unless "inverse" is True -> then return original data, message)
    '''  # line 258
        write = branch is not None and revision is not None  # line 259
        if write:  # line 260
            try:  # line 261
                os.makedirs(encode(revisionFolder(branch, revision, base=_.root)))  # line 261
            except FileExistsError:  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 262
                pass  # HINT "try" only necessary for *testing* hash collision code (!) TODO probably raise exception otherwise in any case?  # line 262
        changed = ChangeSet({}, {}, {}, {})  # type: ChangeSet  # TODO Needs explicity initialization due to mypy problems with default arguments :-(  # line 263
        indicator = ProgressIndicator(PROGRESS_MARKER[1 if _.c.useUnicodeFont else 0]) if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # optional file list progress indicator  # line 264
        hashed = None  # type: _coconut.typing.Optional[str]  # line 265
        written = None  # type: int  # line 265
        compressed = 0  # type: int  # line 265
        original = 0  # type: int  # line 265
        start_time = time.time()  # type: float  # line 265
        knownPaths = collections.defaultdict(list)  # type: Dict[str, List[str]]  # line 266
        for path, pinfo in _.paths.items():  # line 267
            if pinfo.size is not None and (considerOnly is None or any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in considerOnly))) and (dontConsider is None or not any((path[:path.rindex(SLASH)] == pattern[:pattern.rindex(SLASH)] and fnmatch.fnmatch(path[path.rindex(SLASH) + 1:], pattern[pattern.rindex(SLASH) + 1:]) for pattern in dontConsider))):  # line 268
                knownPaths[os.path.dirname(path)].append(os.path.basename(path))  # TODO reimplement using fnmatch.filter and set operations for all files per path for speed  # line 271
        for path, dirnames, filenames in os.walk(_.root):  # line 272
            path = decode(path)  # line 273
            dirnames[:] = [decode(d) for d in dirnames]  # line 274
            filenames[:] = [decode(f) for f in filenames]  # line 275
            dirnames[:] = [d for d in dirnames if len([n for n in _.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in _.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 276
            filenames[:] = [f for f in filenames if len([n for n in _.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 277
            dirnames.sort()  # line 278
            filenames.sort()  # line 278
            relPath = os.path.relpath(path, _.root).replace(os.sep, SLASH)  # type: str  # line 279
            walk = list(filenames if considerOnly is None else reduce(lambda last, pattern: last | set(fnmatch.filter(filenames, os.path.basename(pattern))), (p for p in considerOnly if os.path.dirname(p).replace(os.sep, SLASH) == relPath), _coconut.set()))  # type: List[str]  # line 280
            if dontConsider:  # line 281
                walk[:] = [fn for fn in walk if not any((fnmatch.fnmatch(fn, os.path.basename(p)) for p in dontConsider if os.path.dirname(p).replace(os.sep, SLASH) == relPath))]  # line 282
            for file in walk:  # if m.track or m.picky: only files that match any path-relevant tracking patterns  # line 283
                filename = relPath + SLASH + file  # line 284
                filepath = os.path.join(path, file)  # line 285
                try:  # line 286
                    stat = os.stat(encode(filepath))  # line 286
                except Exception as E:  # line 287
                    exception(E)  # line 287
                    continue  # line 287
                size, mtime = stat.st_size, int(stat.st_mtime * 1000)  # line 288
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 289
                if show:  # indication character returned  # line 290
                    outstring = "\r%s %s  %s" % ("Preparing" if write else "Checking", show, filename)  # line 291
                    printo(outstring + " " * max(0, termWidth - wcswidth(outstring)), nl="")  # line 292
                progressSymbols = PROGRESS_MARKER[1 if _.c.useUnicodeFont else 0]  # type: str  # line 293
                if filename not in _.paths:  # detected file not present (or untracked) in (other) branch  # line 294
                    nameHash = hashStr(filename)  # line 295
                    try:  # line 296
                        hashed, written = hashFile(filepath, _.compress, symbols=progressSymbols, saveTo=revisionFolder(branch, revision, base=_.root, file=nameHash) if write else None, callback=(lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - wcswidth(outstring) - 2), nl="")) if show else None) if size > 0 else (None, 0)  # line 297
                        changed.additions[filename] = PathInfo(nameHash, size, mtime, hashed)  # line 298
                        compressed += written  # line 299
                        original += size  # line 299
                    except Exception as E:  # line 300
                        exception(E)  # line 300
                    continue  # with next file  # line 301
                last = _.paths[filename]  # filename is known - check for modifications  # line 302
                if last.size is None:  # was removed before but is now added back - does not apply for tracking mode (which never marks files for removal in the history)  # line 303
                    try:  # line 304
                        hashed, written = hashFile(filepath, _.compress, symbols=progressSymbols, saveTo=revisionFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - wcswidth(outstring) - 2), nl="")) if size > 0 else (None, 0)  # line 305
                        changed.additions[filename] = PathInfo(last.nameHash, size, mtime, hashed)  # line 306
                        continue  # line 306
                    except Exception as E:  # line 307
                        exception(E)  # line 307
                elif size != last.size or (not checkContent and mtime != last.mtime) or (checkContent and tryOrDefault(lambda: (hashFile(filepath, _.compress, symbols=progressSymbols)[0] != last.hash), default=False)):  # detected a modification TODO wrap hashFile exception  # line 308
                    try:  # line 309
                        hashed, written = hashFile(filepath, _.compress, symbols=progressSymbols, saveTo=revisionFolder(branch, revision, base=_.root, file=last.nameHash) if write else None, callback=None if not progress else lambda sign: printo(outstring + " " + sign + " " * max(0, termWidth - wcswidth(outstring) - 2), nl="")) if (last.size if inverse else size) > 0 else (last.hash if inverse else None, 0)  # line 310
                        changed.modifications[filename] = PathInfo(last.nameHash, last.size if inverse else size, last.mtime if inverse else mtime, hashed)  # line 311
                    except Exception as E:  # line 312
                        exception(E)  # line 312
                else:  # with next file  # line 313
                    continue  # with next file  # line 313
                compressed += written  # line 314
                original += last.size if inverse else size  # line 314
            if relPath in knownPaths:  # at least one file is tracked TODO may leave empty lists in dict  # line 315
                knownPaths[relPath][:] = list(set(knownPaths[relPath]) - set(walk))  # at least one file is tracked TODO may leave empty lists in dict  # line 315
        for path, names in knownPaths.items():  # all paths that weren't walked by  # line 316
            for file in names:  # line 317
                if len([n for n in _.c.ignores if fnmatch.fnmatch(file, n)]) > 0 and len([p for p in _.c.ignoresWhitelist if fnmatch.fnmatch(file, p)]) == 0:  # don't mark ignored files as deleted  # line 318
                    continue  # don't mark ignored files as deleted  # line 318
                pth = path + SLASH + file  # type: str  # line 319
                changed.deletions[pth] = _.paths[pth]  # line 320
        changed = dataCopy(ChangeSet, changed, moves=detectMoves(changed))  # line 321
        if progress:  # forces clean line of progress output  # line 322
            printo("\r" + " " * termWidth + "\r", nl="")  # forces clean line of progress output  # line 322
        elif verbose:  # line 323
            info("Finished detecting changes")  # line 323
        tt = time.time() - start_time  # type: float  # line 324
        speed = (original / (KIBI * tt)) if tt > 0. else 0.  # type: float  # line 324
        msg = (("Compression advantage is %.1f%%" % (original * 100. / compressed - 100.)) if _.compress and write and compressed > 0 else "")  # type: str  # line 325
        msg = (msg + " | " if msg else "") + ("Transfer speed was %.2f %siB/s." % (speed if speed < 1500. else speed / KIBI, "k" if speed < 1500. else "M") if original > 0 and tt > 0. else "")  # line 326
        return (changed, msg if msg else None)  # line 327

    def computeSequentialPathSet(_, branch: 'int', revision: 'int'):  # line 329
        ''' Returns nothing, just updates _.paths in place. '''  # line 330
        next(_.computeSequentialPathSetIterator(branch, revision, incrementally=False))  # simply invoke the generator once to get full results  # line 331

    def computeSequentialPathSetIterator(_, branch: 'int', revision: 'int', incrementally: 'bool'=True) -> '_coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]':  # line 333
        ''' In-memory computation of current list of valid PathInfo entries for specified branch and until specified revision (inclusively) by traversing revision on the file system. '''  # line 334
        _.loadCommit(branch, 0)  # load initial paths  # line 335
        if incrementally:  # line 336
            yield _.paths  # line 336
        m = Metadata(_.root)  # type: Metadata  # next changes TODO avoid loading all metadata and config  # line 337
        rev = None  # type: int  # next changes TODO avoid loading all metadata and config  # line 337
        for rev in range(1, revision + 1):  # line 338
            m.loadCommit(_.getParentBranch(branch, rev), rev)  # line 339
            for p, info in m.paths.items():  # line 340
                if info.size == None:  # line 341
                    del _.paths[p]  # line 341
                else:  # line 342
                    _.paths[p] = info  # line 342
            if incrementally:  # line 343
                yield _.paths  # line 343
        yield None  # for the default case - not incrementally  # line 344

    def getTrackingPatterns(_, branch: '_coconut.typing.Optional[int]'=None, negative: 'bool'=False) -> 'FrozenSet[str]':  # line 346
        ''' Returns list of tracking patterns (or untracking patterns if negative) for provided branch or current branch. '''  # line 347
        return _coconut.frozenset() if not (_.track or _.picky) else frozenset(_.branches[(_.branch if branch is None else branch)].untracked if negative else _.branches[(_.branch if branch is None else branch)].tracked)  # line 348

    def parseRevisionString(_, argument: 'str') -> 'Tuple[_coconut.typing.Optional[int], _coconut.typing.Optional[int]]':  # line 350
        ''' Commit identifiers can be str or int for branch, and int for revision.
        Revision identifiers can be negative, with -1 being last commit.
    '''  # line 353
        if argument is None or argument == SLASH:  # no branch/revision specified  # line 354
            return (_.branch, -1)  # no branch/revision specified  # line 354
        argument = argument.strip()  # line 355
        if argument.startswith(SLASH):  # current branch  # line 356
            return (_.branch, _.getRevisionByName(argument[1:]))  # current branch  # line 356
        if argument.endswith(SLASH):  # line 357
            try:  # line 358
                return (_.getBranchByName(argument[:-1]), -1)  # line 358
            except ValueError:  # line 359
                Exit("Unknown branch label '%s'" % argument)  # line 359
        if SLASH in argument:  # line 360
            b, r = argument.split(SLASH)[:2]  # line 361
            try:  # line 362
                return (_.getBranchByName(b), _.getRevisionByName(r))  # line 362
            except ValueError:  # line 363
                Exit("Unknown branch label or wrong number format '%s/%s'" % (b, r))  # line 363
        branch = _.getBranchByName(argument)  # type: int  # returns number if given (revision) integer  # line 364
        if branch not in _.branches:  # line 365
            branch = None  # line 365
        try:  # either branch name/number or reverse/absolute revision number  # line 366
            return ((_.branch if branch is None else branch), int(argument if argument else "-1") if branch is None else -1)  # either branch name/number or reverse/absolute revision number  # line 366
        except:  # line 367
            Exit("Unknown branch label or wrong number format")  # line 367
        Exit("This should never happen. Please create a issue report")  # line 368
        return (None, None)  # line 368

    def findRevision(_, branch: 'int', revision: 'int', nameHash: 'str') -> 'Tuple[int, str]':  # line 370
        while True:  # find latest revision that contained the file physically  # line 371
            _branch = _.getParentBranch(branch, revision)  # type: int  # line 372
            source = revisionFolder(_branch, revision, base=_.root, file=nameHash)  # type: str  # line 373
            if os.path.exists(encode(source)) and os.path.isfile(source):  # line 374
                break  # line 374
            revision -= 1  # line 375
            if revision < 0:  # line 376
                Exit("Cannot determine versioned file '%s' from specified branch '%d'" % (nameHash, branch))  # line 376
        return revision, source  # line 377

    def getParentBranch(_, branch: 'int', revision: 'int') -> 'int':  # line 379
        ''' Determine originating branch for a (potentially branched) revision, traversing all branch parents until found. '''  # line 380
        other = _.branches[branch].parent  # type: _coconut.typing.Optional[int]  # reference to originating parent branch, or None  # line 381
        if other is None or revision > _.branches[branch].revision:  # need to load commit from other branch instead  # line 382
            return branch  # need to load commit from other branch instead  # line 382
        while _.branches[other].parent is not None and revision <= _.branches[other].revision:  # line 383
            other = _.branches[other].parent  # line 383
        return other  # line 384

    def copyVersionedFile(_, branch: 'int', revision: 'int', toBranch: 'int', toRevision: 'int', pinfo: 'PathInfo'):  # line 386
        ''' Copy versioned file to other branch/revision. '''  # line 387
        target = revisionFolder(toBranch, toRevision, base=_.root, file=pinfo.nameHash)  # type: str  # line 388
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 389
        shutil.copy2(encode(source), encode(target))  # line 390

    def readOrCopyVersionedFile(_, branch: 'int', revision: 'int', nameHash: 'str', toFile: '_coconut.typing.Optional[str]'=None) -> '_coconut.typing.Optional[bytes]':  # line 392
        ''' Return file contents, or copy contents into file path provided. '''  # line 393
        source = revisionFolder(_.getParentBranch(branch, revision), revision, base=_.root, file=nameHash)  # type: str  # line 394
        try:  # line 395
            with openIt(source, "r", _.compress) as fd:  # line 396
                if toFile is None:  # read bytes into memory and return  # line 397
                    return fd.read()  # read bytes into memory and return  # line 397
                with open(encode(toFile), "wb") as to:  # line 398
                    while True:  # line 399
                        buffer = fd.read(bufSize)  # line 400
                        to.write(buffer)  # line 401
                        if len(buffer) < bufSize:  # line 402
                            break  # line 402
                    return None  # line 403
        except Exception as E:  # line 404
            warn("Cannot read versioned file: %r (%d/%d/%s)" % (E, branch, revision, nameHash))  # line 404
        return None  # line 405

    def restoreFile(_, relPath: '_coconut.typing.Optional[str]', branch: 'int', revision: 'int', pinfo: 'PathInfo', ensurePath: 'bool'=False) -> '_coconut.typing.Optional[bytes]':  # line 407
        ''' Recreate file for given revision, or return binary contents if path is None. '''  # line 408
        if relPath is None:  # just return contents  # line 409
            return _.readOrCopyVersionedFile(branch, _.findRevision(branch, revision, pinfo.nameHash)[0], pinfo.nameHash) if pinfo.size > 0 else b''  # just return contents  # line 409
        target = os.path.join(_.root, relPath.replace(SLASH, os.sep))  # type: str  # line 410
        if ensurePath:  #  and not os.path.exists(encode(os.path.dirname(target))):  # line 411
            try:  # line 412
                os.makedirs(encode(os.path.dirname(target)))  # line 412
            except:  # line 413
                pass  # line 413
        if pinfo.size == 0:  # line 414
            with open(encode(target), "wb"):  # line 415
                pass  # line 415
            try:  # update access/modification timestamps on file system  # line 416
                os.utime(encode(target), (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 416
            except Exception as E:  # line 417
                error("Cannot update file's timestamp after restoration '%r'" % E)  # line 417
            return None  # line 418
        revision, source = _.findRevision(branch, revision, pinfo.nameHash)  # line 419
# Restore file by copying buffer-wise
        with openIt(source, "r", _.compress) as fd, open(encode(target), "wb") as to:  # using Coconut's Enhanced Parenthetical Continuation  # line 421
            while True:  # line 422
                buffer = fd.read(bufSize)  # line 423
                to.write(buffer)  # line 424
                if len(buffer) < bufSize:  # line 425
                    break  # line 425
        try:  # update access/modification timestamps on file system  # line 426
            os.utime(encode(target), (pinfo.mtime / 1000., pinfo.mtime / 1000.))  # update access/modification timestamps on file system  # line 426
        except Exception as E:  # line 427
            error("Cannot update file's timestamp after restoration '%r'" % E)  # line 427
        return None  # line 428


# Main client operations
def offline(name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 432
    ''' Initial command to start working offline. '''  # line 433
    if os.path.exists(encode(metaFolder)):  # line 434
        if '--force' not in options:  # line 435
            Exit("Repository folder is either already offline or older branches and commits were left over.\nUse 'sos online' to check for dirty branches, or\nWipe existing offline branches with 'sos offline --force'")  # line 435
        try:  # line 436
            for entry in os.listdir(metaFolder):  # line 437
                resource = metaFolder + os.sep + entry  # line 438
                if os.path.isdir(resource):  # line 439
                    shutil.rmtree(encode(resource))  # line 439
                else:  # line 440
                    os.unlink(encode(resource))  # line 440
        except:  # line 441
            Exit("Cannot reliably remove previous repository contents. Please remove .sos folder manually prior to going offline")  # line 441
    m = Metadata(offline=True)  # type: Metadata  # line 442
    if '--compress' in options or m.c.compress:  # plain file copies instead of compressed ones  # line 443
        m.compress = True  # plain file copies instead of compressed ones  # line 443
    if '--picky' in options or m.c.picky:  # Git-like  # line 444
        m.picky = True  # Git-like  # line 444
    elif '--track' in options or m.c.track:  # Svn-like  # line 445
        m.track = True  # Svn-like  # line 445
    if '--strict' in options or m.c.strict:  # always hash contents  # line 446
        m.strict = True  # always hash contents  # line 446
    if verbose:  # line 447
        info(MARKER + "Going offline...")  # line 447
    m.createBranch(0, (defaults["defaultbranch"] if name is None else name), ("Offline repository created on %s" % strftime() if initialMessage is None else initialMessage))  # main branch's name may be None (e.g. for fossil)  # line 448
    m.branch = 0  # line 449
    m.saveBranches(also={"version": version.__version__})  # stores version info only once. no change immediately after going offline, going back online won't issue a warning  # line 450
    info(MARKER + "Offline repository prepared. Use 'sos online' to finish offline work")  # line 451

def online(options: '_coconut.typing.Sequence[str]'=[]):  # line 453
    ''' Finish working offline. '''  # line 454
    if verbose:  # line 455
        info(MARKER + "Going back online...")  # line 455
    force = '--force' in options  # type: bool  # line 456
    m = Metadata()  # type: Metadata  # line 457
    strict = '--strict' in options or m.strict  # type: bool  # line 458
    m.loadBranches()  # line 459
    if any([not b.inSync for b in m.branches.values()]) and not force:  # line 460
        Exit("There are still unsynchronized (dirty) branches.\nUse 'sos log' to list them.\nUse 'sos commit' and 'sos switch' to commit dirty branches to your VCS before leaving offline mode.\nUse 'sos online --force' to erase all aggregated offline revisions")  # line 460
    m.loadBranch(m.branch)  # line 461
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # one commit guaranteed for first offline branch, for fast-branched branches a revision in branchinfo  # line 462
    if options.count("--force") < 2:  # line 463
        m.computeSequentialPathSet(m.branch, maxi)  # load all commits up to specified revision  # line 464
        changed, msg = m.findChanges(checkContent=strict, considerOnly=None if not (m.track or m.picky) else m.getTrackingPatterns(), dontConsider=None if not (m.track or m.picky) else m.getTrackingPatterns(negative=True), progress='--progress' in options)  # HINT no option for --only/--except here on purpose. No check for picky here, because online is not a command that considers staged files (but we could use --only here, alternatively)  # line 465
        if modified(changed):  # line 466
            Exit("File tree is modified vs. current branch.\nUse 'sos online --force --force' to continue with removing the offline repository")  # line 470
    try:  # line 471
        shutil.rmtree(encode(metaFolder))  # line 471
        info("Exited offline mode. Continue working with your traditional VCS.")  # line 471
    except Exception as E:  # line 472
        Exit("Error removing offline repository: %r" % E)  # line 472
    info(MARKER + "Offline repository removed, you're back online")  # line 473

def branch(name: '_coconut.typing.Optional[str]'=None, initialMessage: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 475
    ''' Create a new branch (from file tree or last revision) and (by default) continue working on it.
      Force not necessary, as either branching from last  revision anyway, or branching file tree anyway.
  '''  # line 478
    last = '--last' in options  # type: bool  # use last revision for branching, not current file tree  # line 479
    stay = '--stay' in options  # type: bool  # continue on current branch after branching (don't switch)  # line 480
    fast = '--fast' in options  # type: bool  # branch by referencing TODO move to default and use --full instead for old behavior  # line 481
    m = Metadata()  # type: Metadata  # line 482
    m.loadBranch(m.branch)  # line 483
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # line 484
    if name and m.getBranchByName(name) is not None:  # attempted to create a named branch  # line 485
        Exit("Branch '%s' already exists. Cannot proceed" % name)  # attempted to create a named branch  # line 485
    branch = max(m.branches.keys()) + 1  # next branch's key - this isn't atomic but we assume single-user non-concurrent use here  # line 486
    if verbose:  # line 487
        info(MARKER + "Branching to %sbranch b%02d%s%s..." % ("unnamed " if name is None else "", branch, " '%s'" % name if name is not None else "", " from last revision" if last else ""))  # line 487
    if last:  # branch from last revision  # line 488
        m.duplicateBranch(branch, name, (initialMessage + " " if initialMessage else "") + "(Branched from r%02d/b%02d)" % (m.branch, maxi), not fast)  # branch from last revision  # line 488
    else:  # branch from current file tree state  # line 489
        m.createBranch(branch, name, ("Branched from file tree after r%02d/b%02d" % (m.branch, maxi) if initialMessage is None else initialMessage))  # branch from current file tree state  # line 489
    if not stay:  # line 490
        m.branch = branch  # line 490
    m.saveBranches()  # TODO or indent again?  # line 491
    info(MARKER + "%s new %sbranch b%02d%s" % ("Continue work after branching" if stay else "Switched to", "unnamed " if name is None else "", branch, " '%s'" % name if name else ""))  # line 492

def changes(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'ChangeSet':  # line 494
    ''' Show changes of file tree vs. (last or specified) revision on current or specified branch. '''  # line 495
    m = Metadata()  # type: Metadata  # line 496
    branch = None  # type: _coconut.typing.Optional[int]  # line 496
    revision = None  # type: _coconut.typing.Optional[int]  # line 496
    strict = '--strict' in options or m.strict  # type: bool  # line 497
    branch, revision = m.parseRevisionString(argument)  # line 498
    if branch not in m.branches:  # line 499
        Exit("Unknown branch")  # line 499
    m.loadBranch(branch)  # knows commits  # line 500
    revision = m.branches[branch].revision if not m.commits else (revision if revision >= 0 else max(m.commits) + 1 + revision)  # negative indexing  # line 501
    if revision < 0 or (m.commits and revision > max(m.commits)):  # line 502
        Exit("Unknown revision r%02d" % revision)  # line 502
    if verbose:  # line 503
        info(MARKER + "Changes of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 503
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 504
    changed, msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 505
    m.listChanges(changed, commitTime=m.commits[max(m.commits)].ctime)  # line 510
    return changed  # for unit tests only TODO remove  # line 511

def _diff(m: 'Metadata', branch: 'int', revision: 'int', changed: 'ChangeSet', ignoreWhitespace: 'bool', textWrap: 'bool'=False):  # TODO introduce option to diff against committed revision  # line 513
    ''' The diff display code. '''  # line 514
    wrap = (lambda s: s) if textWrap else (lambda s: s[:termWidth])  # type: _coconut.typing.Callable[[str], str]  # HINT since we don't know the actual width of unicode strings, we cannot be sure this is really maximizing horizontal space (like ljust), but probably not worth iteratively finding the right size  # line 515
    onlyBinaryModifications = dataCopy(ChangeSet, changed, modifications={k: v for k, v in changed.modifications.items() if not m.isTextType(os.path.basename(k))})  # type: ChangeSet  # line 516
    m.listChanges(onlyBinaryModifications, commitTime=m.commits[max(m.commits)].ctime)  # only list modified binary files  # line 517
    for path, pinfo in (c for c in changed.modifications.items() if m.isTextType(os.path.basename(c[0]))):  # only consider modified text files  # line 518
        content = b""  # type: _coconut.typing.Optional[bytes]  # line 519
        if pinfo.size != 0:  # versioned file  # line 520
            content = m.restoreFile(None, branch, revision, pinfo)  # versioned file  # line 520
            assert content is not None  # versioned file  # line 520
        abspath = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # current file  # line 521
        blocks = None  # type: List[MergeBlock]  # line 522
        nl = None  # type: bytes  # line 522
        blocks, nl = merge(filename=abspath, into=content, diffOnly=True, ignoreWhitespace=ignoreWhitespace)  # only determine change blocks  # line 523
        printo("DIF %s%s  %s" % (path, " <timestamp or newline>" if len(blocks) == 1 and blocks[0].tipe == MergeBlockType.KEEP else "", NL_NAMES[nl]))  # line 524
        linemax = requiredDecimalDigits(max([block.line for block in blocks]) if len(blocks) > 0 else 1)  # type: int  # line 525
        for block in blocks:  # line 526
#      if block.tipe in [MergeBlockType.INSERT, MergeBlockType.REMOVE]:
#        pass  # TODO print some previous and following lines - which aren't accessible here anymore
            if block.tipe == MergeBlockType.INSERT:  # TODO show color via (n)curses or other library?  # line 529
                for no, line in enumerate(block.lines):  # line 530
                    printo(wrap("--- %%0%dd |%%s|" % linemax % (no + block.line, line)))  # line 530
            elif block.tipe == MergeBlockType.REMOVE:  # line 531
                for no, line in enumerate(block.lines):  # line 532
                    printo(wrap("+++ %%0%dd |%%s|" % linemax % (no + block.line, line)))  # line 532
            elif block.tipe == MergeBlockType.REPLACE:  # line 533
                for no, line in enumerate(block.replaces.lines):  # line 534
                    printo(wrap("- | %%0%dd |%%s|" % linemax % (no + block.replaces.line, line)))  # line 534
                for no, line in enumerate(block.lines):  # line 535
                    printo(wrap("+ | %%0%dd |%%s|" % linemax % (no + block.line, line)))  # line 535
#      elif block.tipe == MergeBlockType.KEEP: pass  # TODO allow to show kept stuff, or a part of pre-post lines
#      elif block.tipe == MergeBlockType.MOVE:  # intra-line modifications
            if block.tipe != MergeBlockType.KEEP:  # line 538
                printo()  # line 538

def diff(argument: 'str'="", options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 540
    ''' Show text file differences of file tree vs. (last or specified) revision on current or specified branch. '''  # line 541
    m = Metadata()  # type: Metadata  # line 542
    branch = None  # type: _coconut.typing.Optional[int]  # line 542
    revision = None  # type: _coconut.typing.Optional[int]  # line 542
    strict = '--strict' in options or m.strict  # type: bool  # line 543
    ignoreWhitespace = '--ignore-whitespace' in options or '--iw' in options  # type: bool  # line 544
    wrap = '--wrap' in options  # type: bool  # allow text to wrap around  # line 545
    branch, revision = m.parseRevisionString(argument)  # if nothing given, use last commit  # line 546
    if branch not in m.branches:  # line 547
        Exit("Unknown branch")  # line 547
    m.loadBranch(branch)  # knows commits  # line 548
    revision = m.branches[branch].revision if not m.commits else (revision if revision >= 0 else max(m.commits) + 1 + revision)  # negative indexing  # line 549
    if revision < 0 or (m.commits and revision > max(m.commits)):  # line 550
        Exit("Unknown revision r%02d" % revision)  # line 550
    if verbose:  # line 551
        info(MARKER + "Textual differences of file tree vs. revision '%s/r%02d'" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 551
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision  # line 552
    changed, msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, m.getTrackingPatterns() | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((m.getTrackingPatterns(negative=True) | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # line 553
    _diff(m, branch, revision, changed, ignoreWhitespace=ignoreWhitespace, textWrap=wrap)  # line 558

def commit(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 560
    ''' Create new revision from file tree changes vs. last commit. '''  # line 561
    m = Metadata()  # type: Metadata  # line 562
    if argument is not None and argument in m.tags:  # line 563
        Exit("Illegal commit message. It was already used as a tag name")  # line 563
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # SVN-like mode  # line 564
# No untracking patterns needed here
    if m.picky and not trackingPatterns:  # line 566
        Exit("No file patterns staged for commit in picky mode")  # line 566
    if verbose:  # line 567
        info((lambda _coconut_none_coalesce_item: "b%d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Committing changes to branch '%s'..." % m.branches[m.branch].name))  # line 567
    m, branch, revision, changed, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options, check=False, commit=True, onlys=onlys, excps=excps)  # special flag creates new revision for detected changes, but aborts if no changes  # line 568
    changed = dataCopy(ChangeSet, changed, moves=detectMoves(changed))  # line 569
    m.paths = {k: v for k, v in changed.additions.items()}  # copy to avoid wrong file numbers report below  # line 570
    m.paths.update(changed.modifications)  # update pathset to changeset only  # line 571
    m.paths.update({k: dataCopy(PathInfo, v, size=None, hash=None) for k, v in changed.deletions.items()})  # line 572
    m.saveCommit(m.branch, revision)  # revision has already been incremented  # line 573
    m.commits[revision] = CommitInfo(number=revision, ctime=int(time.time() * 1000), message=argument)  # comment can be None  # line 574
    m.saveBranch(m.branch)  # line 575
    m.loadBranches()  # TODO is it necessary to load again?  # line 576
    if m.picky:  # remove tracked patterns  # line 577
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=[], inSync=False)  # remove tracked patterns  # line 577
    else:  # track or simple mode: set branch dirty  # line 578
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=False)  # track or simple mode: set branch dirty  # line 578
    if "--tag" in options and argument is not None:  # memorize unique tag  # line 579
        m.tags.append(argument)  # memorize unique tag  # line 579
        info("Version was tagged with %s" % argument)  # memorize unique tag  # line 579
    m.saveBranches()  # line 580
    printo(MARKER + "Created new revision r%02d%s (+%02d/-%02d/%s%02d/%s%02d)" % (revision, ((" '%s'" % argument) if argument is not None else ""), len(changed.additions) - len(changed.moves), len(changed.deletions) - len(changed.moves), PLUSMINUS_SYMBOL if m.c.useUnicodeFont else "~", len(changed.modifications), MOVE_SYMBOL if m.c.useUnicodeFont else "#", len(changed.moves)))  # line 581

def status(argument: '_coconut.typing.Optional[str]'=None, vcs: '_coconut.typing.Optional[str]'=None, cmd: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 583
    ''' Show branches and current repository state. '''  # line 584
    m = Metadata()  # type: Metadata  # line 585
    if not (m.c.useChangesCommand or '--repo' in options):  # line 586
        changes(argument, options, onlys, excps)  # line 586
        return  # line 586
    current = m.branch  # type: int  # line 587
    strict = '--strict' in options or m.strict  # type: bool  # line 588
    info(MARKER + "Offline repository status")  # line 589
    info("Repository root:     %s" % os.getcwd())  # line 590
    info("Underlying VCS root: %s" % vcs)  # line 591
    info("Underlying VCS type: %s" % cmd)  # line 592
    info("Installation path:   %s" % os.path.abspath(os.path.dirname(__file__)))  # line 593
    info("Current SOS version: %s" % version.__version__)  # line 594
    info("At creation version: %s" % m.version)  # line 595
    info("Metadata format:     %s" % m.format)  # line 596
    info("Content checking:    %sactivated" % ("" if m.strict else "de"))  # line 597
    info("Data compression:    %sactivated" % ("" if m.compress else "de"))  # line 598
    info("Repository mode:     %s" % ("track" if m.track else ("picky" if m.picky else "simple")))  # line 599
    info("Number of branches:  %d" % len(m.branches))  # line 600
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 601
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 602
    m.loadBranch(current)  # line 603
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # line 604
    m.computeSequentialPathSet(current, maxi)  # load all commits up to specified revision  # line 508  # line 605
    changed, _msg = m.findChanges(checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress=True)  # line 606
    printo("%s File tree %s" % ((CROSS_SYMBOL if m.c.useUnicodeFont else "!") if modified(changed) else (CHECKMARK_SYMBOL if m.c.useUnicodeFont else " "), "has changes" if modified(changed) else "is unchanged"))  # TODO use other marks if no unicode console detected TODO bad choice of symbols for changed vs. unchanged  # line 611
    sl = max([len((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(b.name)) for b in m.branches.values()])  # type: int  # line 612
    for branch in sorted(m.branches.values(), key=lambda b: b.number):  # line 613
        m.loadBranch(branch.number)  # knows commit history  # line 614
        maxi = max(m.commits) if m.commits else m.branches[branch.number].revision  # line 615
        printo("  %s b%02d%s @%s (%s) with %d commits%s" % ("*" if current == branch.number else " ", branch.number, ((" %%%ds" % (sl + 2)) % ("'%s'" % branch.name)) if branch.name else "", strftime(branch.ctime), "in sync" if branch.inSync else "dirty", len(m.commits), ". Last comment: '%s'" % m.commits[maxi].message if maxi in m.commits and m.commits[maxi].message else ""))  # line 616
    if m.track or m.picky and (len(m.branches[m.branch].tracked) > 0 or len(m.branches[m.branch].untracked) > 0):  # line 617
        info("\nTracked file patterns:")  # TODO print matching untracking patterns side-by-side  # line 618
        printo(ajoin("  | ", m.branches[m.branch].tracked, "\n"))  # line 619
        info("\nUntracked file patterns:")  # line 620
        printo(ajoin("  | ", m.branches[m.branch].untracked, "\n"))  # line 621

def exitOnChanges(argument: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[], check: 'bool'=True, commit: 'bool'=False, onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None) -> 'Tuple[Metadata, _coconut.typing.Optional[int], int, ChangeSet, bool, bool, FrozenSet[str], FrozenSet[str]]':  # line 623
    ''' Common behavior for switch, update, delete, commit.
      Should not be called for picky mode, unless tracking patterns were added.
      check: stop program on detected change
      commit: don't stop on changes, because that's what we need in the operation
      Returns (Metadata, (current or target) branch, revision, set of changes vs. last commit on current branch, strict, force flags.
  '''  # line 629
    assert not (check and commit)  # line 630
    m = Metadata()  # type: Metadata  # line 631
    force = '--force' in options  # type: bool  # line 632
    strict = '--strict' in options or m.strict  # type: bool  # line 633
    if argument is not None:  # line 634
        branch, revision = m.parseRevisionString(argument)  # for early abort  # line 635
        if branch is None:  # line 636
            Exit("Branch '%s' doesn't exist. Cannot proceed" % argument)  # line 636
    m.loadBranch(m.branch)  # knows last commits of *current* branch  # line 637
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # line 638

# Determine current changes
    trackingPatterns = m.getTrackingPatterns()  # type: FrozenSet[str]  # line 641
    untrackingPatterns = m.getTrackingPatterns(negative=True)  # type: FrozenSet[str]  # line 642
    m.computeSequentialPathSet(m.branch, maxi)  # load all commits up to specified revision  # line 643
    changed, msg = m.findChanges(m.branch if commit else None, maxi + 1 if commit else None, checkContent=strict, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns), dontConsider=excps if not (m.track or m.picky) else (untrackingPatterns if excps is None else excps), progress='--progress' in options)  # line 644
    if check and modified(changed) and not force:  # line 649
        m.listChanges(changed, commitTime=m.commits[max(m.commits)].ctime if len(m.commits) > 0 else 0)  # line 650
        Exit("File tree contains changes. Use --force to proceed")  # line 651
    elif commit:  # line 652
        if not modified(changed) and not force:  # line 653
            Exit("Nothing to commit")  # line 653
        m.listChanges(changed, commitTime=m.commits[max(m.commits)].ctime if len(m.commits) > 0 else 0)  # line 654
        if msg:  # line 655
            printo(msg)  # line 655

    if argument is not None:  # branch/revision specified  # line 657
        m.loadBranch(branch)  # knows commits of target branch  # line 658
        maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # line 659
        revision = revision if revision >= 0 else len(m.commits) + revision  # negative indexing  # line 660
        if revision < 0 or revision > maxi:  # line 661
            Exit("Unknown revision r%02d" % revision)  # line 661
        return (m, branch, revision, changed, strict, force, m.getTrackingPatterns(branch), m.getTrackingPatterns(branch, negative=True))  # line 662
    return (m, m.branch, maxi + (1 if commit else 0), changed, strict, force, trackingPatterns, untrackingPatterns)  # line 663

def switch(argument: 'str', options: 'List[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 665
    ''' Continue work on another branch, replacing file tree changes. '''  # line 666
    m, branch, revision, changed, strict, _force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, ["--force"] + options)  # line 667
    force = '--force' in options  # type: bool  # needed as we fake force in above access  # line 668

# Determine file changes from other branch to current file tree
    if '--meta' in options:  # only switch meta data  # line 671
        m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], tracked=m.branches[branch].tracked, untracked=m.branches[branch].untracked)  # line 672
    else:  # full file switch  # line 673
        m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for target branch into memory  # line 674
        todos, _msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingPatterns | m.getTrackingPatterns(branch)), dontConsider=excps if not (m.track or m.picky) else ((untrackingPatterns | m.getTrackingPatterns(branch, negative=True)) if excps is None else excps), progress='--progress' in options)  # determine difference of other branch vs. file tree (forced or in sync with current branch; "addition" means exists now and should be removed)  # line 675

# Now check for potential conflicts
        changed.deletions.clear()  # local deletions never create conflicts, modifications always  # line 682
        rms = []  # type: _coconut.typing.Sequence[str]  # local additions can be ignored if restoration from switch would be same  # line 683
        for a, pinfo in changed.additions.items():  # has potential corresponding re-add in switch operation:  # line 684
            if a in todos.deletions and pinfo.size == todos.deletions[a].size and (pinfo.hash == todos.deletions[a].hash if m.strict else pinfo.mtime == todos.deletions[a].mtime):  # line 685
                rms.append(a)  # line 685
        for rm in rms:  # TODO could also silently accept remote DEL for local ADD  # line 686
            del changed.additions[rm]  # TODO could also silently accept remote DEL for local ADD  # line 686
        if modified(changed) and not force:  # line 687
            m.listChanges(changed)  # line 687
            Exit("File tree contains changes. Use --force to proceed")  # line 687
        if verbose:  # line 688
            info(MARKER + "Switching to branch %sb%02d/r%02d..." % ("'%s' " % m.branches[branch].name if m.branches[branch].name else "", branch, revision))  # line 688
        if not modified(todos):  # line 689
            info("No changes to current file tree")  # line 690
        else:  # integration required  # line 691
            for path, pinfo in todos.deletions.items():  # line 692
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # is deleted in current file tree: restore from branch to reach target  # line 693
                printo("ADD " + path)  # line 694
            for path, pinfo in todos.additions.items():  # line 695
                os.unlink(encode(os.path.join(m.root, path.replace(SLASH, os.sep))))  # is added in current file tree: remove from branch to reach target  # line 696
                printo("DEL " + path)  # line 697
            for path, pinfo in todos.modifications.items():  # line 698
                m.restoreFile(path, branch, revision, pinfo)  # is modified in current file tree: restore from branch to reach target  # line 699
                printo("MOD " + path)  # line 700
    m.branch = branch  # line 701
    m.saveBranches()  # store switched path info  # line 702
    info(MARKER + "Switched to branch %sb%02d/r%02d" % ("'%s' " % (m.branches[branch].name if m.branches[branch].name else ""), branch, revision))  # line 703

def update(argument: 'str', options: '_coconut.typing.Sequence[str]'=[], onlys: '_coconut.typing.Optional[FrozenSet[str]]'=None, excps: '_coconut.typing.Optional[FrozenSet[str]]'=None):  # line 705
    ''' Load and integrate a specified other branch/revision into current life file tree.
      In tracking mode, this also updates the set of tracked patterns.
      User options for merge operation: --add/--rm/--ask --add-lines/--rm-lines/--ask-lines (inside each file), --add-chars/--rm-chars/--ask-chars
  '''  # line 709
    mrg = getAnyOfMap({"--add": MergeOperation.INSERT, "--rm": MergeOperation.REMOVE, "--ask": MergeOperation.ASK}, options, MergeOperation.BOTH)  # type: MergeOperation  # default operation is replicate remote state  # line 710
    mrgline = getAnyOfMap({'--add-lines': MergeOperation.INSERT, '--rm-lines': MergeOperation.REMOVE, "--ask-lines": MergeOperation.ASK}, options, mrg)  # type: MergeOperation  # default operation for modified files is same as for files  # line 711
    mrgchar = getAnyOfMap({'--add-chars': MergeOperation.INSERT, '--rm-chars': MergeOperation.REMOVE, "--ask-chars": MergeOperation.ASK}, options, mrgline)  # type: MergeOperation  # default operation for modified files is same as for lines  # line 712
    eol = '--eol' in options  # type: bool  # use remote eol style  # line 713
    m = Metadata()  # type: Metadata  # TODO same is called inside stop on changes - could return both current and designated branch instead  # line 714
    currentBranch = m.branch  # type: _coconut.typing.Optional[int]  # line 715
    m, branch, revision, changes, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(argument, options, check=False, onlys=onlys, excps=excps)  # don't check for current changes, only parse arguments  # line 716
    if verbose:  # line 717
        info(MARKER + "Integrating changes from '%s/r%02d' into file tree..." % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 717

# Determine file changes from other branch over current file tree
    m.computeSequentialPathSet(branch, revision)  # load all commits up to specified revision for branch to integrate  # line 720
    trackingUnion = trackingPatterns | m.getTrackingPatterns(branch)  # type: FrozenSet[str]  # line 721
    untrackingUnion = untrackingPatterns | m.getTrackingPatterns(branch, negative=True)  # type: FrozenSet[str]  # line 722
    changed, _msg = m.findChanges(checkContent=strict, inverse=True, considerOnly=onlys if not (m.track or m.picky) else conditionalIntersection(onlys, trackingUnion), dontConsider=excps if not (m.track or m.picky) else (untrackingUnion if onlys is None else onlys), progress='--progress' in options)  # determine difference of other branch vs. file tree. "addition" means exists now but not in other, and should be removed unless in tracking mode  # line 723
    if not (mrg.value & MergeOperation.INSERT.value and changed.additions or (mrg.value & MergeOperation.REMOVE.value and changed.deletions) or changed.modifications):  # no file ops  # line 728
        if trackingUnion != trackingPatterns:  # nothing added  # line 729
            info("No file changes detected, but tracking patterns were merged (run 'sos switch /-1 --meta' to undo)")  # TODO write test to see if this works  # line 730
        else:  # line 731
            info("Nothing to update")  # but write back updated branch info below  # line 732
    else:  # integration required  # line 733
        for path, pinfo in changed.deletions.items():  # file-based update. Deletions mark files not present in current file tree -> needs addition!  # line 734
            if mrg.value & MergeOperation.INSERT.value:  # deleted in current file tree: restore from branch to reach target  # line 735
                m.restoreFile(path, branch, revision, pinfo, ensurePath=True)  # deleted in current file tree: restore from branch to reach target  # line 735
            printo("ADD " + path if mrg.value & MergeOperation.INSERT.value else "(A) " + path)  # line 736
        for path, pinfo in changed.additions.items():  # line 737
            if m.track or m.picky:  # because untracked files of other branch cannot be detected (which is good)  # line 738
                Exit("This should never happen. Please create an issue report")  # because untracked files of other branch cannot be detected (which is good)  # line 738
            if mrg.value & MergeOperation.REMOVE.value:  # line 739
                os.unlink(encode(m.root + os.sep + path.replace(SLASH, os.sep)))  # line 739
            printo("DEL " + path if mrg.value & MergeOperation.REMOVE.value else "(D) " + path)  # not contained in other branch, but maybe kept  # line 740
        for path, pinfo in changed.modifications.items():  # line 741
            into = os.path.normpath(os.path.join(m.root, path.replace(SLASH, os.sep)))  # type: str  # line 742
            binary = not m.isTextType(path)  # type: bool  # line 743
            op = "m"  # type: str  # merge as default for text files, always asks for binary (TODO unless --theirs or --mine)  # line 744
            if mrg == MergeOperation.ASK or binary:  # TODO this may ask user even if no interaction was asked for  # line 745
                printo(("MOD " if not binary else "BIN ") + path)  # line 746
                while True:  # line 747
                    printo(into)  # TODO print mtime, size differences?  # line 748
                    op = (_utility.input if coco_version >= (1, 3, 1, 21) else input)(" Resolve: *M[I]ne (skip), [T]heirs" + (": " if binary else ", [M]erge: ")).strip().lower()  # TODO set encoding on stdin  # line 749
                    if op in ("it" if binary else "itm"):  # line 750
                        break  # line 750
            if op == "t":  # line 751
                printo("THR " + path)  # blockwise copy of contents  # line 752
                m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash, toFile=into)  # blockwise copy of contents  # line 752
            elif op == "m":  # line 753
                with open(encode(into), "rb") as fd:  # TODO slurps current file  # line 754
                    current = fd.read()  # type: bytes  # TODO slurps current file  # line 754
                file = m.readOrCopyVersionedFile(branch, revision, pinfo.nameHash) if pinfo.size > 0 else b''  # type: _coconut.typing.Optional[bytes]  # parse lines  # line 755
                if current == file and verbose:  # line 756
                    info("No difference to versioned file")  # line 756
                elif file is not None:  # if None, error message was already logged  # line 757
                    merged = None  # type: bytes  # line 758
                    nl = None  # type: bytes  # line 758
                    merged, nl = merge(file=file, into=current, mergeOperation=mrgline, charMergeOperation=mrgchar, eol=eol)  # line 759
                    if merged != current:  # line 760
                        with open(encode(path), "wb") as fd:  # TODO write to temp file first, in case writing fails  # line 761
                            fd.write(merged)  # TODO write to temp file first, in case writing fails  # line 761
                    elif verbose:  # TODO but update timestamp?  # line 762
                        info("No change")  # TODO but update timestamp?  # line 762
            else:  # mine or wrong input  # line 763
                printo("MNE " + path)  # nothing to do! same as skip  # line 764
    info(MARKER + "Integrated changes from '%s/r%02d' into file tree" % ((lambda _coconut_none_coalesce_item: "b%02d" % branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name), revision))  # line 765
    m.branches[currentBranch] = dataCopy(BranchInfo, m.branches[currentBranch], inSync=False, tracked=list(trackingUnion))  # line 766
    m.branch = currentBranch  # need to restore setting before saving TODO operate on different objects instead  # line 767
    m.saveBranches()  # line 768

def destroy(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 770
    ''' Remove a branch entirely. '''  # line 771
    m, branch, revision, changed, strict, force, trackingPatterns, untrackingPatterns = exitOnChanges(None, options)  # line 772
    if len(m.branches) == 1:  # line 773
        Exit("Cannot remove the only remaining branch. Use 'sos online' to leave offline mode")  # line 773
    branch, revision = m.parseRevisionString(argument)  # not from exitOnChanges, because we have to set argument to None there  # line 774
    if branch is None or branch not in m.branches:  # line 775
        Exit("Cannot delete unknown branch %r" % branch)  # line 775
    if verbose:  # line 776
        info(MARKER + "Removing branch b%02d%s..." % (branch, " '%s'" % ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(m.branches[branch].name))))  # line 776
    binfo = m.removeBranch(branch)  # need to keep a reference to removed entry for output below  # line 777
    info(MARKER + "Branch b%02d%s removed" % (branch, " '%s'" % ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(binfo.name))))  # line 778

def add(relPath: 'str', pattern: 'str', options: '_coconut.typing.Sequence[str]'=[], negative: 'bool'=False):  # line 780
    ''' Add a tracked files pattern to current branch's tracked files. negative means tracking blacklisting. '''  # line 781
    force = '--force' in options  # type: bool  # line 782
    m = Metadata()  # type: Metadata  # line 783
    if not (m.track or m.picky):  # line 784
        Exit("Repository is in simple mode. Create offline repositories via 'sos offline --track' or 'sos offline --picky' or configure a user-wide default via 'sos config track on'")  # line 784
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 785
    if pattern in patterns:  # line 786
        Exit("Pattern '%s' already tracked" % pattern)  # line 786
    if not force and not os.path.exists(encode(relPath.replace(SLASH, os.sep))):  # line 787
        Exit("The pattern folder doesn't exist. Use --force to add the file pattern anyway")  # line 787
    if not force and len(fnmatch.filter(os.listdir(os.path.abspath(relPath.replace(SLASH, os.sep))), os.path.basename(pattern.replace(SLASH, os.sep)))) == 0:  # doesn't match any current file  # line 788
        Exit("Pattern doesn't match any file in specified folder. Use --force to add it anyway")  # line 789
    patterns.append(pattern)  # line 790
    m.saveBranches()  # line 791
    info(MARKER + "Added tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern.replace(SLASH, os.sep)), os.path.abspath(relPath)))  # line 792

def remove(relPath: 'str', pattern: 'str', negative: 'bool'=False):  # line 794
    ''' Remove a tracked files pattern from current branch's tracked files. '''  # line 795
    m = Metadata()  # type: Metadata  # line 796
    if not (m.track or m.picky):  # line 797
        Exit("Repository is in simple mode. Needs 'offline --track' or 'offline --picky' instead")  # line 797
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 798
    if pattern not in patterns:  # line 799
        suggestion = _coconut.set()  # type: Set[str]  # line 800
        for pat in patterns:  # line 801
            if fnmatch.fnmatch(pattern, pat):  # line 802
                suggestion.add(pat)  # line 802
        if suggestion:  # TODO use same wording as in move  # line 803
            printo("Do you mean any of the following tracked file patterns? '%s'" % (", ".join(sorted(suggestion))))  # TODO use same wording as in move  # line 803
        Exit("Tracked pattern '%s' not found" % pattern)  # line 804
    patterns.remove(pattern)  # line 805
    m.saveBranches()  # line 806
    info(MARKER + "Removed tracking pattern '%s' for folder '%s'" % (os.path.basename(pattern), os.path.abspath(relPath.replace(SLASH, os.sep))))  # line 807

def ls(folder: '_coconut.typing.Optional[str]'=None, options: '_coconut.typing.Sequence[str]'=[]):  # line 809
    ''' List specified directory, augmenting with repository metadata. '''  # line 810
    m = Metadata()  # type: Metadata  # line 811
    folder = (os.getcwd() if folder is None else folder)  # line 812
    if '--all' in options:  # always start at SOS repo root with --all  # line 813
        folder = m.root  # always start at SOS repo root with --all  # line 813
    recursive = '--recursive' in options or '-r' in options or '--all' in options  # type: bool  # line 814
    patterns = '--patterns' in options or '-p' in options  # type: bool  # line 815
    DOT = (DOT_SYMBOL if m.c.useUnicodeFont else " ") * 3  # type: str  # line 816
    if verbose:  # line 817
        info(MARKER + "Repository is in %s mode" % ("tracking" if m.track else ("picky" if m.picky else "simple")))  # line 817
    relPath = relativize(m.root, os.path.join(folder, "-"))[0]  # type: str  # line 818
    if relPath.startswith(os.pardir):  # line 819
        Exit("Cannot list contents of folder outside offline repository")  # line 819
    trackingPatterns = m.getTrackingPatterns() if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 820
    untrackingPatterns = m.getTrackingPatterns(negative=True) if m.track or m.picky else _coconut.frozenset()  # type: _coconut.typing.Optional[FrozenSet[str]]  # for current branch  # line 821
    if '--tags' in options:  # TODO this has nothing to do with "ls" - it's an entirely different command. Move if something like "sos tag" has been implemented  # line 822
        if len(m.tags) > 0:  # line 823
            printo(ajoin("TAG ", sorted(m.tags), nl="\n"))  # line 823
        return  # line 824
    for dirpath, dirnames, _filenames in os.walk(folder):  # line 825
        if not recursive:  # avoid recursion  # line 826
            dirnames.clear()  # avoid recursion  # line 826
        dirnames[:] = sorted([decode(d) for d in dirnames])  # line 827
        dirnames[:] = [d for d in dirnames if len([n for n in m.c.ignoreDirs if fnmatch.fnmatch(d, n)]) == 0 or len([p for p in m.c.ignoreDirsWhitelist if fnmatch.fnmatch(d, p)]) > 0]  # global ignores  # line 828

        folder = decode(dirpath)  # line 830
        relPath = relativize(m.root, os.path.join(folder, "-"))[0]  # line 831
        if patterns:  # line 832
            out = ajoin("TRK ", [os.path.basename(p) for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath], nl="\n")  # type: str  # line 833
            if out:  # line 834
                printo("DIR %s\n" % relPath + out)  # line 834
            continue  # with next folder  # line 835
        files = list(sorted((entry for entry in os.listdir(folder) if os.path.isfile(os.path.join(folder, entry)))))  # type: List[str]  # line 836
        if len(files) > 0:  # line 837
            printo("DIR %s" % relPath)  # line 837
        for file in files:  # for each file list all tracking patterns that match, or none (e.g. in picky mode after commit)  # line 838
            ignore = None  # type: _coconut.typing.Optional[str]  # line 839
            for ig in m.c.ignores:  # line 840
                if fnmatch.fnmatch(file, ig):  # remember first match  # line 841
                    ignore = ig  # remember first match  # line 841
                    break  # remember first match  # line 841
            if ig:  # line 842
                for wl in m.c.ignoresWhitelist:  # line 843
                    if fnmatch.fnmatch(file, wl):  # found a white list entry for ignored file, undo ignoring it  # line 844
                        ignore = None  # found a white list entry for ignored file, undo ignoring it  # line 844
                        break  # found a white list entry for ignored file, undo ignoring it  # line 844
            matches = []  # type: List[str]  # line 845
            if not ignore:  # line 846
                for pattern in (p for p in trackingPatterns if os.path.dirname(p).replace(os.sep, SLASH) == relPath):  # only patterns matching current folder  # line 847
                    if fnmatch.fnmatch(file, os.path.basename(pattern)):  # line 848
                        matches.append(os.path.basename(pattern))  # line 848
            matches.sort(key=lambda element: len(element))  # sort in-place  # line 849
            printo("%s %s%s" % ("IGN" if ignore is not None else ("TRK" if len(matches) > 0 else DOT), file, "  (%s)" % ignore if ignore is not None else ("  (%s)" % ("; ".join(matches)) if len(matches) > 0 else "")))  # line 850

def log(options: '_coconut.typing.Sequence[str]'=[]):  # line 852
    ''' List previous commits on current branch. '''  # line 853
    m = Metadata()  # type: Metadata  # line 854
    m.loadBranch(m.branch)  # knows commit history  # line 855
    maxi = max(m.commits) if m.commits else m.branches[m.branch].revision  # type: int  # one commit guaranteed for first offline branch, for fast-branched branches a revision in branchinfo  # line 856
    info((lambda _coconut_none_coalesce_item: "r%02d" % m.branch if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(MARKER + "Offline commit history of branch '%s'" % m.branches[m.branch].name))  # TODO also retain info of "from branch/revision" on branching?  # line 857
    nl = len("%d" % maxi)  # type: int  # determine space needed for revision  # line 858
    changesetIterator = m.computeSequentialPathSetIterator(m.branch, maxi)  # type: _coconut.typing.Optional[Iterator[Dict[str, PathInfo]]]  # line 859
    olds = _coconut.frozenset()  # type: FrozenSet[str]  # last revision's entries  # line 860
    last = {}  # type: Dict[str, PathInfo]  # path infos from previous revision  # line 861
    commit = None  # type: CommitInfo  # line 862
    for no in range(maxi + 1):  # line 863
        if no in m.commits:  # line 864
            commit = m.commits[no]  # line 864
        else:  # TODO clean this code  # line 865
            n = Metadata()  # type: Metadata  # line 866
            n.loadBranch(n.getParentBranch(m.branch, no))  # line 867
            commit = n.commits[no]  # line 868
        nxts = next(changesetIterator)  # type: Dict[str, PathInfo]  # line 869
        news = frozenset(nxts.keys())  # type: FrozenSet[str]  # line 870
        _add = news - olds  # type: FrozenSet[str]  # line 871
        _del = olds - news  # type: FrozenSet[str]  # line 872
#    _mod_:Dict[str,PathInfo] = {k: nxts[k] for k in news - _add - _del}
        _mod = frozenset([_ for _, info in {k: nxts[k] for k in news - _add - _del}.items() if last[_].size != info.size or (last[_].hash != info.hash if m.strict else last[_].mtime != info.mtime)])  # type: FrozenSet[str]  # line 874
#    _mov:FrozenSet[str] = detectMoves(ChangeSet(nxts, {o: None for o in olds})  # TODO determine moves - can we reuse detectMoves(changes)?
        _txt = len([a for a in _add if m.isTextType(a)])  # type: int  # line 876
        printo("  %s r%s @%s (+%02d/-%02d/%s%02d/T%02d) |%s|%s" % ("*" if commit.number == maxi else " ", ("%%%ds" % nl) % commit.number, strftime(commit.ctime), len(_add), len(_del), PLUSMINUS_SYMBOL if m.c.useUnicodeFont else "~", len(_mod), _txt, ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)), "TAG" if ((lambda _coconut_none_coalesce_item: "" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(commit.message)) in m.tags else ""))  # line 877
        if '--changes' in options:  # TODO moves detection?  # line 878
            m.listChanges(ChangeSet({a: None for a in _add}, {d: None for d in _del}, {m: None for m in _mod}, {}))  # TODO moves detection?  # line 878
        if '--diff' in options:  #  _diff(m, changes)  # needs from revision diff  # line 879
            pass  #  _diff(m, changes)  # needs from revision diff  # line 879
        olds = news  # replaces olds for next revision compare  # line 880
        last = {k: v for k, v in nxts.items()}  # create new reference  # line 881

def dump(argument: 'str', options: '_coconut.typing.Sequence[str]'=[]):  # line 883
    ''' Exported entire repository as archive for easy transfer. '''  # line 884
    if verbose:  # line 885
        info(MARKER + "Dumping repository to archive...")  # line 885
    m = Metadata()  # type: Metadata  # to load the configuration  # line 886
    progress = '--progress' in options  # type: bool  # line 887
    delta = '--full' not in options  # type: bool  # line 888
    skipBackup = '--skip-backup' in options  # type: bool  # line 889
    import warnings  # line 890
    import zipfile  # line 890
    try:  # HINT zlib is the library that contains the deflated algorithm  # line 891
        import zlib  # HINT zlib is the library that contains the deflated algorithm  # line 891
        compression = zipfile.ZIP_DEFLATED  # HINT zlib is the library that contains the deflated algorithm  # line 891
    except:  # line 892
        compression = zipfile.ZIP_STORED  # line 892

    if argument is None:  # line 894
        Exit("Argument missing (target filename)")  # line 894
    argument = argument if "." in argument else argument + DUMP_FILE  # TODO this logic lacks a bit, "v1.2" would not receive the suffix  # line 895
    entries = []  # type: List[str]  # line 896
    if os.path.exists(encode(argument)) and not skipBackup:  # line 897
        try:  # line 898
            if verbose:  # line 899
                info("Creating backup...")  # line 899
            shutil.copy2(encode(argument), encode(argument + BACKUP_SUFFIX))  # line 900
            if delta:  # line 901
                with zipfile.ZipFile(argument, "r") as _zip:  # list of pure relative paths without leading dot, normal slashes  # line 902
                    entries = _zip.namelist()  # list of pure relative paths without leading dot, normal slashes  # line 902
        except Exception as E:  # line 903
            Exit("Error creating backup copy before dumping. Please resolve and retry. %r" % E)  # line 903
    if verbose:  # line 904
        info("Dumping revisions...")  # line 904
    if delta:  # don't show duplicate entries warnings  # line 905
        warnings.filterwarnings('ignore', 'Duplicate name.*', UserWarning, "zipfile", 0)  # don't show duplicate entries warnings  # line 905
    with zipfile.ZipFile(argument, "a" if delta else "w", compression) as _zip:  # create  # line 906
        _zip.debug = 0  # suppress debugging output  # line 907
        _zip.comment = ("Repository dump from %r" % strftime()).encode(UTF8)  # line 908
        repopath = os.path.join(os.getcwd(), metaFolder)  # type: str  # line 909
        indicator = ProgressIndicator(PROGRESS_MARKER[1 if m.c.useUnicodeFont else 0]) if progress else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 910
        totalsize = 0  # type: int  # line 911
        start_time = time.time()  # type: float  # line 912
        for dirpath, dirnames, filenames in os.walk(repopath):  # TODO use index knowledge instead of walking to avoid adding stuff not needed?  # line 913
            dirpath = decode(dirpath)  # line 914
            if dirpath.endswith(BACKUP_SUFFIX):  # don't backup backups  # line 915
                continue  # don't backup backups  # line 915
            printo(ljust(dirpath))  # TODO improve progress indicator output to | dir | dumpuing file  # line 916
            dirnames[:] = sorted([decode(d) for d in dirnames])  # HINT sort for reproducible delta dumps  # line 917
            filenames[:] = sorted([decode(f) for f in filenames])  # line 918
            for filename in filenames:  # line 919
                abspath = os.path.join(dirpath, filename)  # type: str  # line 920
                relpath = os.path.join(metaFolder, os.path.relpath(abspath, repopath)).replace(os.sep, "/")  # type: str  # line 921
                totalsize += os.stat(encode(abspath)).st_size  # line 922
                show = indicator.getIndicator() if progress else None  # type: _coconut.typing.Optional[str]  # line 923
                if relpath.endswith(BACKUP_SUFFIX):  # don't backup backups  # line 924
                    continue  # don't backup backups  # line 924
                if not delta or relpath.endswith(metaFile) or relpath not in entries:  # always update metadata, otherwise only add new revision files  # line 925
                    if show:  # line 926
                        printo("\r" + ljust("Dumping %s @%.2f MiB/s %s" % (show, totalsize / (MEBI * (time.time() - start_time)), filename)), nl="")  # line 926
                    _zip.write(abspath, relpath)  # write entry into archive  # line 927
        if delta:  # line 928
            _zip.comment = ("Delta dump from %r" % strftime()).encode(UTF8)  # line 928
    info("\r" + ljust(MARKER + "Finished dumping %s repository @%.2f MiB/s." % ("differential" if delta else "entire", totalsize / (MEBI * (time.time() - start_time)))))  # clean line  # line 929

def config(arguments: 'List[str]', options: 'List[str]'=[]):  # line 931
    command, key, value = (arguments + [None] * 2)[:3]  # line 932
    if command not in ["set", "unset", "show", "list", "add", "rm"]:  # line 933
        Exit("Unknown config command")  # line 933
    local = "--local" in options  # type: bool  # line 934
    m = Metadata()  # type: Metadata  # loads layered configuration as well. TODO warning if repo not exists  # line 935
    c = m.c if local else m.c.__defaults  # type: configr.Configr  # line 936
    if command == "set":  # line 937
        if None in (key, value):  # line 938
            Exit("Key or value not specified")  # line 938
        if key not in (["defaultbranch"] + ([] if local else CONFIGURABLE_FLAGS) + CONFIGURABLE_LISTS):  # line 939
            Exit("Unsupported key for %s configuration %r" % ("local " if local else "global", key))  # line 939
        if key in CONFIGURABLE_FLAGS and value.lower() not in TRUTH_VALUES + FALSE_VALUES:  # line 940
            Exit("Cannot set flag to '%s'. Try on/off instead" % value.lower())  # line 940
        c[key] = value.lower() in TRUTH_VALUES if key in CONFIGURABLE_FLAGS else (removePath(key, value.strip()) if key not in CONFIGURABLE_LISTS else [removePath(key, v) for v in safeSplit(value, ";")])  # TODO sanitize texts?  # line 941
    elif command == "unset":  # line 942
        if key is None:  # line 943
            Exit("No key specified")  # line 943
        if key not in c.keys():  # HINT: Works on local configurations when used with --local  # line 944
            Exit("Unknown key")  # HINT: Works on local configurations when used with --local  # line 944
        del c[key]  # line 945
    elif command == "add":  # line 946
        if None in (key, value):  # line 947
            Exit("Key or value not specified")  # line 947
        if key not in CONFIGURABLE_LISTS:  # line 948
            Exit("Unsupported key %r" % key)  # line 948
        if key not in c.keys():  # prepare empty list, or copy from global, add new value below  # line 949
            c[key] = [_ for _ in c.__defaults[key]] if local else []  # prepare empty list, or copy from global, add new value below  # line 949
        elif value in c[key]:  # line 950
            Exit("Value already contained, nothing to do")  # line 950
        if ";" in value:  # line 951
            c[key].append(removePath(key, value))  # line 951
        else:  # line 952
            c[key].extend([removePath(key, v) for v in value.split(";")])  # line 952
    elif command == "rm":  # line 953
        if None in (key, value):  # line 954
            Exit("Key or value not specified")  # line 954
        if key not in c.keys():  # line 955
            Exit("Unknown key %r" % key)  # line 955
        if value not in c[key]:  # line 956
            Exit("Unknown value %r" % value)  # line 956
        c[key].remove(value)  # line 957
        if local and len(c[key]) == 0 and "--prune" in options:  # remove local enty, to fallback to global  # line 958
            del c[key]  # remove local enty, to fallback to global  # line 958
    else:  # Show or list  # line 959
        if key == "flags":  # list valid configuration items  # line 960
            printo(", ".join(CONFIGURABLE_FLAGS))  # list valid configuration items  # line 960
        elif key == "lists":  # line 961
            printo(", ".join(CONFIGURABLE_LISTS))  # line 961
        elif key == "texts":  # line 962
            printo(", ".join([_ for _ in defaults.keys() if _ not in (CONFIGURABLE_FLAGS + CONFIGURABLE_LISTS)]))  # line 962
        else:  # line 963
            out = {3: "[default]", 2: "[global] ", 1: "[local]  "}  # type: Dict[int, str]  # line 964
            c = m.c  # always use full configuration chain  # line 965
            try:  # attempt single key  # line 966
                assert key is not None  # line 967
                c[key]  # line 967
                l = key in c.keys()  # type: bool  # line 968
                g = key in c.__defaults.keys()  # type: bool  # line 968
                printo("%s %s %r" % (key.rjust(20), out[3] if not (l or g) else (out[1] if l else out[2]), c[key]))  # line 969
            except:  # normal value listing  # line 970
                vals = {k: (repr(v), 3) for k, v in defaults.items()}  # type: Dict[str, Tuple[str, int]]  # line 971
                vals.update({k: (repr(v), 2) for k, v in c.__defaults.items()})  # line 972
                vals.update({k: (repr(v), 1) for k, v in c.__map.items()})  # line 973
                for k, vt in sorted(vals.items()):  # line 974
                    printo("%s %s %s" % (k.rjust(20), out[vt[1]], vt[0]))  # line 974
                if len(c.keys()) == 0:  # line 975
                    info("No local configuration stored")  # line 975
                if len(c.__defaults.keys()) == 0:  # line 976
                    info("No global configuration stored")  # line 976
        return  # in case of list, no need to store anything  # line 977
    if local:  # saves changes of repoConfig  # line 978
        m.repoConf = c.__map  # saves changes of repoConfig  # line 978
        m.saveBranches()  # saves changes of repoConfig  # line 978
        Exit("OK", code=0)  # saves changes of repoConfig  # line 978
    else:  # global config  # line 979
        f, h = saveConfig(c)  # only saves c.__defaults (nested Configr)  # line 980
        if f is None:  # line 981
            error("Error saving user configuration: %r" % h)  # line 981
        else:  # line 982
            Exit("OK", code=0)  # line 982

def move(relPath: 'str', pattern: 'str', newRelPath: 'str', newPattern: 'str', options: 'List[str]'=[], negative: 'bool'=False):  # line 984
    ''' Path differs: Move files, create folder if not existing. Pattern differs: Attempt to rename file, unless exists in target or not unique.
      for "mvnot" don't do any renaming (or do?)
  '''  # line 987
    if verbose:  # line 988
        info(MARKER + "Renaming %r to %r" % (pattern, newPattern))  # line 988
    force = '--force' in options  # type: bool  # line 989
    soft = '--soft' in options  # type: bool  # line 990
    if not os.path.exists(encode(relPath.replace(SLASH, os.sep))) and not force:  # line 991
        Exit("Source folder doesn't exist. Use --force to proceed anyway")  # line 991
    m = Metadata()  # type: Metadata  # line 992
    patterns = m.branches[m.branch].untracked if negative else m.branches[m.branch].tracked  # type: List[str]  # line 993
    matching = fnmatch.filter(os.listdir(relPath.replace(SLASH, os.sep)) if os.path.exists(encode(relPath.replace(SLASH, os.sep))) else [], os.path.basename(pattern))  # type: List[str]  # find matching files in source  # line 994
    matching[:] = [f for f in matching if len([n for n in m.c.ignores if fnmatch.fnmatch(f, n)]) == 0 or len([p for p in m.c.ignoresWhitelist if fnmatch.fnmatch(f, p)]) > 0]  # line 995
    if not matching and not force:  # line 996
        Exit("No files match the specified file pattern. Use --force to proceed anyway")  # line 996
    if not (m.track or m.picky):  # line 997
        Exit("Repository is in simple mode. Simply use basic file operations to modify files, then execute 'sos commit' to version the changes")  # line 997
    if pattern not in patterns:  # list potential alternatives and exit  # line 998
        for tracked in (t for t in patterns if os.path.dirname(t) == relPath):  # for all patterns of the same source folder  # line 999
            alternative = fnmatch.filter(matching, os.path.basename(tracked))  # type: _coconut.typing.Sequence[str]  # find if it matches any of the files in the source folder, too  # line 1000
            if alternative:  # line 1001
                info("  '%s' matches %d files" % (tracked, len(alternative)))  # line 1001
        if not (force or soft):  # line 1002
            Exit("File pattern '%s' is not tracked on current branch. 'sos move' only works on tracked patterns" % pattern)  # line 1002
    basePattern = os.path.basename(pattern)  # type: str  # pure glob without folder  # line 1003
    newBasePattern = os.path.basename(newPattern)  # type: str  # line 1004
    if basePattern.count("*") < newBasePattern.count("*") or (basePattern.count("?") - basePattern.count("[?]")) < (newBasePattern.count("?") - newBasePattern.count("[?]")) or (basePattern.count("[") - basePattern.count("\\[")) < (newBasePattern.count("[") - newBasePattern.count("\\[")) or (basePattern.count("]") - basePattern.count("\\]")) < (newBasePattern.count("]") - newBasePattern.count("\\]")):  # line 1005
        Exit("Glob markers from '%s' to '%s' don't match, cannot move/rename tracked matching files" % (basePattern, newBasePattern))  # line 1009
    oldTokens = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 1010
    newToken = None  # type: _coconut.typing.Sequence[GlobBlock]  # line 1010
    oldTokens, newTokens = tokenizeGlobPatterns(os.path.basename(pattern), os.path.basename(newPattern))  # line 1011
    matches = convertGlobFiles(matching, oldTokens, newTokens)  # type: _coconut.typing.Sequence[Tuple[str, str]]  # computes list of source - target filename pairs  # line 1012
    if len({st[1] for st in matches}) != len(matches):  # line 1013
        Exit("Some target filenames are not unique and different move/rename actions would point to the same target file")  # line 1013
    matches = reorderRenameActions(matches, exitOnConflict=not soft)  # attempts to find conflict-free renaming order, or exits  # line 1014
    if os.path.exists(encode(newRelPath)):  # line 1015
        exists = [filename[1] for filename in matches if os.path.exists(encode(os.path.join(newRelPath, filename[1]).replace(SLASH, os.sep)))]  # type: _coconut.typing.Sequence[str]  # line 1016
        if exists and not (force or soft):  # line 1017
            Exit("%s files would write over existing files in %s cases. Use --force to execute it anyway" % ("Moving" if relPath != newRelPath else "Renaming", "all" if len(exists) == len(matches) else "some"))  # line 1017
    else:  # line 1018
        os.makedirs(encode(os.path.abspath(newRelPath.replace(SLASH, os.sep))))  # line 1018
    if not soft:  # perform actual renaming  # line 1019
        for (source, target) in matches:  # line 1020
            try:  # line 1021
                shutil.move(encode(os.path.abspath(os.path.join(relPath, source).replace(SLASH, os.sep))), encode(os.path.abspath(os.path.join(newRelPath, target).replace(SLASH, os.sep))))  # line 1021
            except Exception as E:  # one error can lead to another in case of delicate renaming order  # line 1022
                error("Cannot move/rename file '%s' to '%s'" % (source, os.path.join(newRelPath, target)))  # one error can lead to another in case of delicate renaming order  # line 1022
    patterns[patterns.index(pattern)] = newPattern  # line 1023
    m.saveBranches()  # line 1024

def parse(root: 'str', cwd: 'str', cmd: 'str'):  # line 1026
    ''' Main operation. Main has already chdir into SOS root folder, cwd is original working directory for add, rm, mv. '''  # line 1027
    debug("Parsing command-line arguments...")  # line 1028
    try:  # line 1029
        onlys, excps = parseOnlyOptions(cwd, sys.argv)  # extracts folder-relative information for changes, commit, diff, switch, update  # line 1030
        command = sys.argv[1].strip() if len(sys.argv) > 1 else ""  # line 1031
        arguments = [c.strip() for c in sys.argv[2:] if not c.startswith("--")]  # type: List[_coconut.typing.Optional[str]]  # line 1032
        options = [c.strip() for c in sys.argv[2:] if c.startswith("--")]  # line 1033
        debug("Processing command %r with arguments %r and options %r." % (command, [_ for _ in arguments if _ is not None], options))  # line 1034
        if command[:1] in "amr":  # line 1035
            relPath, pattern = relativize(root, os.path.join(cwd, arguments[0] if arguments else "."))  # line 1035
        if command[:1] == "m":  # line 1036
            if len(arguments) < 2:  # line 1037
                Exit("Need a second file pattern argument as target for move command")  # line 1037
            newRelPath, newPattern = relativize(root, os.path.join(cwd, arguments[1]))  # line 1038
        arguments[:] = (arguments + [None] * 3)[:3]  # line 1039
        if command[:1] == "a":  # addnot  # line 1040
            add(relPath, pattern, options, negative="n" in command)  # addnot  # line 1040
        elif command[:1] == "b":  # line 1041
            branch(arguments[0], arguments[1], options)  # line 1041
        elif command[:3] == "com":  # line 1042
            commit(arguments[0], options, onlys, excps)  # line 1042
        elif command[:2] == "ch":  # "changes" (legacy)  # line 1043
            changes(arguments[0], options, onlys, excps)  # "changes" (legacy)  # line 1043
        elif command[:2] == "ci":  # line 1044
            commit(arguments[0], options, onlys, excps)  # line 1044
        elif command[:3] == 'con':  # line 1045
            config(arguments, options)  # line 1045
        elif command[:2] == "de":  # line 1046
            destroy(arguments[0], options)  # line 1046
        elif command[:2] == "di":  # line 1047
            diff(arguments[0], options, onlys, excps)  # line 1047
        elif command[:2] == "du":  # line 1048
            dump(arguments[0], options)  # line 1048
        elif command[:1] == "h":  # line 1049
            usage(APPNAME, version.__version__)  # line 1049
        elif command[:2] == "lo":  # line 1050
            log(options)  # line 1050
        elif command[:2] == "li":  # line 1051
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 1051
        elif command[:2] == "ls":  # line 1052
            ls(os.path.relpath((lambda _coconut_none_coalesce_item: cwd if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(arguments[0]), root), options)  # line 1052
        elif command[:1] == "m":  # mvnot  # line 1053
            move(relPath, pattern, newRelPath, newPattern, options, negative="n" in command)  # mvnot  # line 1053
        elif command[:2] == "of":  # line 1054
            offline(arguments[0], arguments[1], options)  # line 1054
        elif command[:2] == "on":  # line 1055
            online(options)  # line 1055
        elif command[:1] == "r":  # rmnot  # line 1056
            remove(relPath, pattern, negative="n" in command)  # rmnot  # line 1056
        elif command[:2] == "st":  # line 1057
            status(arguments[0], cwd, cmd, options, onlys, excps)  # line 1057
        elif command[:2] == "sw":  # line 1058
            switch(arguments[0], options, onlys, excps)  # line 1058
        elif command[:1] == "u":  # line 1059
            update(arguments[0], options, onlys, excps)  # line 1059
        elif command[:1] == "v":  # line 1060
            usage(APPNAME, version.__version__, short=True)  # line 1060
        else:  # line 1061
            Exit("Unknown command '%s'" % command)  # line 1061
        Exit(code=0)  # regular exit  # line 1062
    except (Exception, RuntimeError) as E:  # line 1063
        exception(E)  # line 1064
        Exit("An internal error occurred in SOS. Please report above message to the project maintainer at  https://github.com/ArneBachmann/sos/issues  via 'New Issue'.\nPlease state your installed version via 'sos version', and what you were doing")  # line 1065

def main():  # line 1067
    global debug, info, warn, error  # to modify logger  # line 1068
    logging.basicConfig(level=level, stream=sys.stderr, format=("%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '--log' in sys.argv else "%(message)s"))  # line 1069
    _log = Logger(logging.getLogger(__name__))  # line 1070
    debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1070
    for option in (o for o in ['--log', '--debug', '--verbose', '-v', '--sos', '--vcs'] if o in sys.argv):  # clean up program arguments  # line 1071
        sys.argv.remove(option)  # clean up program arguments  # line 1071
    if '--help' in sys.argv or len(sys.argv) < 2:  # line 1072
        usage(APPNAME, version.__version__)  # line 1072
    command = sys.argv[1] if len(sys.argv) > 1 else None  # type: _coconut.typing.Optional[str]  # line 1073
    root, vcs, cmd = findSosVcsBase()  # root is None if no .sos folder exists up the folder tree (still working online); vcs is checkout/repo root folder; cmd is the VCS base command  # line 1074
    debug("Found root folders for SOS | VCS:  %s | %s" % (("-" if root is None else root), ("-" if vcs is None else vcs)))  # line 1075
    defaults["defaultbranch"] = (lambda _coconut_none_coalesce_item: "default" if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(vcsBranches.get(cmd, "trunk"))  # sets dynamic default with SVN fallback  # line 1076
    defaults["useChangesCommand"] = cmd == "fossil"  # sets dynamic default with SVN fallback  # line 1077
    if force_sos or root is not None or (("" if command is None else command))[:2] == "of" or (("" if command is None else command))[:1] in "hv":  # in offline mode or just going offline TODO what about git config?  # line 1078
        cwd = os.getcwd()  # line 1079
        os.chdir(cwd if command[:2] == "of" else (cwd if root is None else root))  # line 1080
        parse(root, cwd, cmd)  # line 1081
    elif force_vcs or cmd is not None:  # online mode - delegate to VCS  # line 1082
        info("%s: Running '%s %s'" % (COMMAND.upper(), cmd, " ".join(sys.argv[1:])))  # line 1083
        import subprocess  # only required in this section  # line 1084
        process = subprocess.Popen([cmd] + sys.argv[1:], shell=False, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stderr)  # line 1085
        inp = ""  # type: str  # line 1086
        while True:  # line 1087
            so, se = process.communicate(input=inp)  # line 1088
            if process.returncode is not None:  # line 1089
                break  # line 1089
            inp = sys.stdin.read()  # line 1090
        if sys.argv[1][:2] == "co" and process.returncode == 0:  # successful commit - assume now in sync again (but leave meta data folder with potential other feature branches behind until "online")  # line 1091
            if root is None:  # line 1092
                Exit("Cannot determine VCS root folder: Unable to mark repository as synchronized and will show a warning when leaving offline mode")  # line 1092
            m = Metadata(root)  # type: Metadata  # line 1093
            m.branches[m.branch] = dataCopy(BranchInfo, m.branches[m.branch], inSync=True)  # mark as committed  # line 1094
            m.saveBranches()  # line 1095
    else:  # line 1096
        Exit("No offline repository present, and unable to detect VCS file tree")  # line 1096


# Main part
force_sos = '--sos' in sys.argv  # type: bool  # line 1100
force_vcs = '--vcs' in sys.argv  # type: bool  # line 1101
verbose = '--verbose' in sys.argv or '-v' in sys.argv  # type: bool  # imported from utility, and only modified here  # line 1102
debug_ = os.environ.get("DEBUG", "False").lower() == "true" or '--debug' in sys.argv  # type: bool  # line 1103
level = logging.DEBUG if '--log' in sys.argv else logging.INFO  # line 1104
_log = Logger(logging.getLogger(__name__))  # line 1105
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 1105
if __name__ == '__main__':  # line 1106
    main()  # line 1106
