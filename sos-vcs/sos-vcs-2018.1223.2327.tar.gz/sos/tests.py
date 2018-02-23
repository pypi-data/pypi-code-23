#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x8611d789

# Compiled with Coconut version 1.3.1-post_dev20 [Dead Parrot]

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

import builtins  # line 4
import codecs  # line 4
import enum  # line 4
import json  # line 4
import logging  # line 4
import os  # line 4
import shutil  # line 4
sys = _coconut_sys  # line 4
import time  # line 4
import traceback  # line 4
import unittest  # line 4
import uuid  # line 4
from io import BytesIO  # line 5
from io import BufferedRandom  # line 5
from io import TextIOWrapper  # line 5
try:  # Python 3  # line 6
    from unittest import mock  # Python 3  # line 6
except:  # installed via pip  # line 7
    import mock  # installed via pip  # line 7

testFolder = os.path.abspath(os.path.join(os.getcwd(), "test"))  # line 9
import configr  # optional dependency  # line 10
os.environ["TEST"] = testFolder  # needed to mock configr library calls in sos  # line 11
import sos  # import of package, not file  # line 12
sos.defaults["defaultbranch"] = "trunk"  # because sos.main() is never called  # line 13
sos.defaults["useChangesCommand"] = True  # because sos.main() is never called  # line 14
sos.defaults["useUnicodeFont"] = False  # because sos.main() is never called  # line 15

def sync():  # line 17
    os.sync() if sys.version_info[:2] >= (3, 3) else None  # line 17


def determineFilesystemTimeResolution() -> 'float':  # line 20
    name = str(uuid.uuid4())  # type: str  # line 21
    with open(name, "w") as fd:  # create temporary file  # line 22
        fd.write("x")  # create temporary file  # line 22
    mt = os.stat(sos.encode(name)).st_mtime  # type: float  # get current timestamp  # line 23
    while os.stat(sos.encode(name)).st_mtime == mt:  # wait until timestamp modified  # line 24
        time.sleep(0.05)  # to avoid 0.00s bugs (came up some time for unknown reasons)  # line 25
        with open(name, "w") as fd:  # line 26
            fd.write("x")  # line 26
    mt, start, _count = os.stat(sos.encode(name)).st_mtime, time.time(), 0  # line 27
    while os.stat(sos.encode(name)).st_mtime == mt:  # now cound and measure time until modified again  # line 28
        time.sleep(0.05)  # line 29
        _count += 1  # line 30
        with open(name, "w") as fd:  # line 31
            fd.write("x")  # line 31
    os.unlink(name)  # line 32
    fsprecision = round(time.time() - start, 2)  # type: float  # line 33
    print("File system timestamp precision is %.2fs; wrote to the file %d times during that time" % (fsprecision, _count))  # line 34
    return fsprecision  # line 35


FS_PRECISION = determineFilesystemTimeResolution() * 1.55  # line 38


@_coconut_tco  # line 41
def debugTestRunner(post_mortem=None):  # line 41
    ''' Unittest runner doing post mortem debugging on failing tests. '''  # line 42
    import pdb  # line 43
    if post_mortem is None:  # line 44
        post_mortem = pdb.post_mortem  # line 44
    class DebugTestResult(unittest.TextTestResult):  # line 45
        def addError(_, test, err):  # called before tearDown()  # line 46
            traceback.print_exception(*err)  # line 47
            post_mortem(err[2])  # line 48
            super(DebugTestResult, _).addError(test, err)  # line 49
        def addFailure(_, test, err):  # line 50
            traceback.print_exception(*err)  # line 51
            post_mortem(err[2])  # line 52
            super(DebugTestResult, _).addFailure(test, err)  # line 53
    return _coconut_tail_call(unittest.TextTestRunner, resultclass=DebugTestResult)  # line 54

@_coconut_tco  # line 56
def wrapChannels(func: '_coconut.typing.Callable[..., Any]') -> 'str':  # line 56
    ''' Wrap function call to capture and return strings emitted on stdout and stderr. '''  # line 57
    oldv = sys.argv  # line 58
    buf = TextIOWrapper(BufferedRandom(BytesIO(b"")), encoding=sos.UTF8)  # line 59
    handler = logging.StreamHandler(buf)  # TODO doesn't seem to be captured  # line 60
    sys.stdout = sys.stderr = buf  # line 61
    logging.getLogger().addHandler(handler)  # line 62
    try:  # capture output into buf  # line 63
        func()  # capture output into buf  # line 63
    except Exception as E:  # line 64
        buf.write(str(E) + "\n")  # line 64
        traceback.print_exc(file=buf)  # line 64
    except SystemExit as F:  # line 65
        buf.write("EXIT CODE %s" % F.code + "\n")  # line 65
        traceback.print_exc(file=buf)  # line 65
    logging.getLogger().removeHandler(handler)  # line 66
    sys.argv, sys.stdout, sys.stderr = oldv, sys.__stdout__, sys.__stderr__  # TODO when run using pythonw.exe and/or no console, these could be None  # line 67
    buf.seek(0)  # line 68
    return _coconut_tail_call(buf.read)  # line 69

def mockInput(datas: '_coconut.typing.Sequence[str]', func) -> 'Any':  # line 71
    with mock.patch("builtins.input", side_effect=datas):  # line 72
        return func()  # line 72

def setRepoFlag(name: 'str', value: 'bool'):  # line 74
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 75
        flags, branches, config = json.loads(fd.read())  # line 75
    flags[name] = value  # line 76
    with open(sos.metaFolder + os.sep + sos.metaFile, "w") as fd:  # line 77
        fd.write(json.dumps((flags, branches, config)))  # line 77

def checkRepoFlag(name: 'str', flag: '_coconut.typing.Optional[bool]'=None, value: '_coconut.typing.Optional[Any]'=None) -> 'bool':  # line 79
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 80
        flags, branches, config = json.loads(fd.read())  # line 80
    return (name in flags and flags[name] == flag) if flag is not None else (name in config and config[name] == value)  # line 81


class Tests(unittest.TestCase):  # line 84
    ''' Entire test suite. '''  # line 85

    def setUp(_):  # line 87
        sos.Metadata.singleton = None  # line 88
        for entry in os.listdir(testFolder):  # cannot remove testFolder on Windows when using TortoiseSVN as VCS  # line 89
            resource = os.path.join(testFolder, entry)  # line 90
            shutil.rmtree(sos.encode(resource)) if os.path.isdir(sos.encode(resource)) else os.unlink(sos.encode(resource))  # line 91
        os.chdir(testFolder)  # line 92


    def assertAllIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]', only: 'bool'=False):  # line 95
        for w in what:  # line 96
            _.assertIn(w, where)  # line 96
        if only:  # line 97
            _.assertEqual(len(what), len(where))  # line 97

    def assertAllNotIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]'):  # line 99
        for w in what:  # line 100
            _.assertNotIn(w, where)  # line 100

    def assertInAll(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 102
        for w in where:  # line 103
            _.assertIn(what, w)  # line 103

    def assertInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 105
        _.assertTrue(any((what in w for w in where)))  # line 105

    def assertNotInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 107
        _.assertFalse(any((what in w for w in where)))  # line 107

    def createFile(_, number: 'Union[int, str]', contents: 'str'="x" * 10, prefix: '_coconut.typing.Optional[str]'=None):  # line 109
        if prefix and not os.path.exists(prefix):  # line 110
            os.makedirs(prefix)  # line 110
        with open(("." if prefix is None else prefix) + os.sep + (("file%d" % number) if isinstance(number, int) else number), "wb") as fd:  # line 111
            fd.write(contents if isinstance(contents, bytes) else contents.encode("cp1252"))  # line 111

    def existsFile(_, number: 'Union[int, str]', expectedContents: 'bytes'=None) -> 'bool':  # line 113
        if not os.path.exists(("." + os.sep + "file%d" % number) if isinstance(number, int) else number):  # line 114
            return False  # line 114
        if expectedContents is None:  # line 115
            return True  # line 115
        with open(("." + os.sep + "file%d" % number) if isinstance(number, int) else number, "rb") as fd:  # line 116
            return fd.read() == expectedContents  # line 116

    def testAccessor(_):  # line 118
        a = sos.Accessor({"a": 1})  # line 119
        _.assertEqual((1, 1), (a["a"], a.a))  # line 120

    def testGetAnyOfmap(_):  # line 122
        _.assertEqual(2, sos.getAnyOfMap({"a": 1, "b": 2}, ["x", "b"]))  # line 123
        _.assertIsNone(sos.getAnyOfMap({"a": 1, "b": 2}, []))  # line 124

    def testAjoin(_):  # line 126
        _.assertEqual("a1a2", sos.ajoin("a", ["1", "2"]))  # line 127
        _.assertEqual("* a\n* b", sos.ajoin("* ", ["a", "b"], "\n"))  # line 128

    def testFindChanges(_):  # line 130
        m = sos.Metadata(os.getcwd())  # line 131
        try:  # line 132
            sos.config(["set", "texttype", "*"])  # line 132
        except SystemExit as E:  # line 133
            _.assertEqual(0, E.code)  # line 133
        try:  # will be stripped from leading paths anyway  # line 134
            sos.config(["set", "ignores", "test/*.cfg;D:\\apps\\*.cfg.bak"])  # will be stripped from leading paths anyway  # line 134
        except SystemExit as E:  # line 135
            _.assertEqual(0, E.code)  # line 135
        m = sos.Metadata(os.getcwd())  # reload from file system  # line 136
        for file in [f for f in os.listdir() if f.endswith(".bak")]:  # remove configuration file  # line 137
            os.unlink(file)  # remove configuration file  # line 137
        _.createFile(1, "1")  # line 138
        m.createBranch(0)  # line 139
        _.assertEqual(1, len(m.paths))  # line 140
        time.sleep(FS_PRECISION)  # time required by filesystem time resolution issues  # line 141
        _.createFile(1, "2")  # modify existing file  # line 142
        _.createFile(2, "2")  # add another file  # line 143
        m.loadCommit(0, 0)  # line 144
        changes, msg = m.findChanges()  # detect time skew  # line 145
        _.assertEqual(1, len(changes.additions))  # line 146
        _.assertEqual(0, len(changes.deletions))  # line 147
        _.assertEqual(1, len(changes.modifications))  # line 148
        _.assertEqual(0, len(changes.moves))  # line 149
        m.paths.update(changes.additions)  # line 150
        m.paths.update(changes.modifications)  # line 151
        _.createFile(2, "12")  # modify file again  # line 152
        changes, msg = m.findChanges(0, 1)  # by size, creating new commit  # line 153
        _.assertEqual(0, len(changes.additions))  # line 154
        _.assertEqual(0, len(changes.deletions))  # line 155
        _.assertEqual(1, len(changes.modifications))  # line 156
        _.assertEqual(0, len(changes.moves))  # line 157
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1)))  # line 158
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # line 159
# TODO test moves

    def testMoves(_):  # line 162
        _.createFile(1, "1")  # line 163
        _.createFile(2, "2", "sub")  # line 164
        sos.offline(options=["--strict"])  # line 165
        os.renames(sos.encode("." + os.sep + "file1"), sos.encode("sub" + os.sep + "file1"))  # line 166
        os.renames(sos.encode("sub" + os.sep + "file2"), sos.encode("." + os.sep + "file2"))  # line 167
        out = wrapChannels(lambda: sos.changes())  # type: str  # line 168
        _.assertIn("MOV ./file2  <-  sub/file2", out)  # line 169
        _.assertIn("MOV sub/file1  <-  ./file1", out)  # line 170
        out = wrapChannels(lambda: sos.commit())  # line 171
        _.assertIn("MOV ./file2  <-  sub/file2", out)  # line 172
        _.assertIn("MOV sub/file1  <-  ./file1", out)  # line 173
        _.assertIn("Created new revision r01 (+00/-00/~00/#02)", out)  # TODO why is this not captured?  # line 174

    def testPatternPaths(_):  # line 176
        sos.offline(options=["--track"])  # line 177
        os.mkdir("sub")  # line 178
        _.createFile("sub" + os.sep + "file1", "sdfsdf")  # line 179
        sos.add("sub", "sub/file?")  # line 180
        sos.commit("test")  # should pick up sub/file1 pattern  # line 181
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # sub/file1 was added  # line 182
        _.createFile(1)  # line 183
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 184
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 184
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 184
        except:  # line 185
            pass  # line 185

    def testNoArgs(_):  # line 187
        pass  # call "sos" without arguments should simply show help or info about missing arguments  # line 188

    def testAutoUpgrade(_):  # line 190
        sos.offline()  # line 191
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "r", encoding=sos.UTF8) as fd:  # line 192
            repo, branches, config = json.load(fd)  # line 192
        repo["version"] = "0"  # lower than any pip version  # line 193
        branches[:] = [branch[:5] for branch in branches]  # simulate some older state  # line 194
        del repo["format"]  # simulate pre-1.3.5  # line 195
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "w", encoding=sos.UTF8) as fd:  # line 196
            json.dump((repo, branches, config), fd, ensure_ascii=False)  # line 196
        out = wrapChannels(lambda: sos.status(options=["--repo"]))  # line 197
        _.assertAllIn(["Upgraded repository metadata to match SOS version '2018.1210.3028'", "Upgraded repository metadata to match SOS version '1.3.5'"], out)  # line 198

    def testFastBranching(_):  # line 200
        _.createFile(1)  # line 201
        sos.offline(options=["--strict"])  # b0/r0 = ./file1  # line 202
        _.createFile(2)  # line 203
        os.unlink("file1")  # line 204
        sos.commit()  # b0/r1 = ./file2  # line 205
        sos.branch(options=["--fast", "--last"])  # branch b1 from b0/1 TODO modify once --fast becomes the new normal  # line 206
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0", "b1"], os.listdir(sos.metaFolder), only=True)  # line 207
        _.createFile(3)  # line 208
        sos.commit()  # b1/r2 = ./file2, ./file3  # line 209
        _.assertAllIn([sos.metaFile, "r2"], os.listdir(sos.branchFolder(1)), only=True)  # line 210
        sos.branch(options=["--fast", "--last"])  # branch b2 from b1/2  # line 211
        sos.destroy("0")  # remove parent of b1 and transitive parent of b2  # line 212
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1", "b2"], os.listdir(sos.metaFolder), only=True)  # branch 0 was removed  # line 213
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(1)), only=True)  # revisions were copied to branch 1  # line 214
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(2)), only=True)  # revisions were copied to branch 1  # line 215
# TODO test also other functions like status --repo, log

    def testGetParentBranch(_):  # line 218
        m = sos.Accessor({"branches": {0: sos.Accessor({"parent": None, "revision": None}), 1: sos.Accessor({"parent": 0, "revision": 1})}})  # line 219
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 0))  # line 220
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 1))  # line 221
        _.assertEqual(1, sos.Metadata.getParentBranch(m, 1, 2))  # line 222
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 0, 10))  # line 223

    def testTokenizeGlobPattern(_):  # line 225
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 226
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 227
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 228
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 229
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 230
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 231

    def testTokenizeGlobPatterns(_):  # line 233
        try:  # because number of literal strings differs  # line 234
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 234
            _.fail()  # because number of literal strings differs  # line 234
        except:  # line 235
            pass  # line 235
        try:  # because glob patterns differ  # line 236
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 236
            _.fail()  # because glob patterns differ  # line 236
        except:  # line 237
            pass  # line 237
        try:  # glob patterns differ, regardless of position  # line 238
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 238
            _.fail()  # glob patterns differ, regardless of position  # line 238
        except:  # line 239
            pass  # line 239
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 240
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 241
        try:  # succeeds, because glob patterns match (differ only in position)  # line 242
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 242
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 242
        except:  # line 243
            pass  # line 243

    def testConvertGlobFiles(_):  # line 245
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 246
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 247

    def testFolderRemove(_):  # line 249
        m = sos.Metadata(os.getcwd())  # line 250
        _.createFile(1)  # line 251
        _.createFile("a", prefix="sub")  # line 252
        sos.offline()  # line 253
        _.createFile(2)  # line 254
        os.unlink("sub" + os.sep + "a")  # line 255
        os.rmdir("sub")  # line 256
        changes = sos.changes()  # TODO replace by output check  # line 257
        _.assertEqual(1, len(changes.additions))  # line 258
        _.assertEqual(0, len(changes.modifications))  # line 259
        _.assertEqual(1, len(changes.deletions))  # line 260
        _.createFile("a", prefix="sub")  # line 261
        changes = sos.changes()  # line 262
        _.assertEqual(0, len(changes.deletions))  # line 263

    def testSwitchConflict(_):  # line 265
        sos.offline(options=["--strict"])  # (r0)  # line 266
        _.createFile(1)  # line 267
        sos.commit()  # add file (r1)  # line 268
        os.unlink("file1")  # line 269
        sos.commit()  # remove (r2)  # line 270
        _.createFile(1, "something else")  # line 271
        sos.commit()  # (r3)  # line 272
        sos.switch("/1")  # updates file1 - marked as MOD, because mtime was changed  # line 273
        _.existsFile(1, "x" * 10)  # line 274
        sos.switch("/2", ["--force"])  # remove file1 requires --force, because size/content (or mtime in non-strict mode) is different to head of branch  # line 275
        sos.switch("/0")  # do nothing, as file1 is already removed  # line 276
        sos.switch("/1")  # add file1 back  # line 277
        sos.switch("/", ["--force"])  # requires force because changed vs. head of branch  # line 278
        _.existsFile(1, "something else")  # line 279

    def testComputeSequentialPathSet(_):  # line 281
        os.makedirs(sos.revisionFolder(0, 0))  # line 282
        os.makedirs(sos.revisionFolder(0, 1))  # line 283
        os.makedirs(sos.revisionFolder(0, 2))  # line 284
        os.makedirs(sos.revisionFolder(0, 3))  # line 285
        os.makedirs(sos.revisionFolder(0, 4))  # line 286
        m = sos.Metadata(os.getcwd())  # line 287
        m.branch = 0  # line 288
        m.commit = 2  # line 289
        m.saveBranches()  # line 290
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 291
        m.saveCommit(0, 0)  # initial  # line 292
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 293
        m.saveCommit(0, 1)  # mod  # line 294
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 295
        m.saveCommit(0, 2)  # add  # line 296
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 297
        m.saveCommit(0, 3)  # del  # line 298
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")  # line 299
        m.saveCommit(0, 4)  # readd  # line 300
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 301
        m.saveBranch(0)  # line 302
        m.branches = {0: sos.BranchInfo(0, 0), 1: sos.BranchInfo(1, 0)}  # line 303
        m.saveBranches()  # line 304
        m.computeSequentialPathSet(0, 4)  # line 305
        _.assertEqual(2, len(m.paths))  # line 306

    def testParseRevisionString(_):  # line 308
        m = sos.Metadata(os.getcwd())  # line 309
        m.branch = 1  # line 310
        m.commits = {0: 0, 1: 1, 2: 2}  # line 311
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 312
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 313
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 314
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 315
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 316
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 317
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 318

    def testOfflineEmpty(_):  # line 320
        os.mkdir("." + os.sep + sos.metaFolder)  # line 321
        try:  # line 322
            sos.offline("trunk")  # line 322
            _.fail()  # line 322
        except SystemExit as E:  # line 323
            _.assertEqual(1, E.code)  # line 323
        os.rmdir("." + os.sep + sos.metaFolder)  # line 324
        sos.offline("test")  # line 325
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 326
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 327
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 328
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 329
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 330
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file  # line 331

    def testOfflineWithFiles(_):  # line 333
        _.createFile(1, "x" * 100)  # line 334
        _.createFile(2)  # line 335
        sos.offline("test")  # line 336
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 337
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 338
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 339
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 340
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 341
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 342
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file plus branch base file copies  # line 343

    def testBranch(_):  # line 345
        _.createFile(1, "x" * 100)  # line 346
        _.createFile(2)  # line 347
        sos.offline("test")  # b0/r0  # line 348
        sos.branch("other")  # b1/r0  # line 349
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 350
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 351
        _.assertEqual(list(sorted(os.listdir(sos.revisionFolder(0, 0)))), list(sorted(os.listdir(sos.revisionFolder(1, 0)))))  # line 353
        _.createFile(1, "z")  # modify file  # line 355
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 356
        _.assertNotEqual(os.stat(sos.encode("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa")).st_size, os.stat(sos.encode("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa")).st_size)  # line 357
        _.createFile(3, "z")  # line 359
        sos.branch("from_last_revision", options=["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 360
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 361
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 366
        _.createFile(1, "x" * 100)  # line 367
        _.createFile(2)  # line 368
        sos.offline("test")  # line 369
        changes = sos.changes()  # line 370
        _.assertEqual(0, len(changes.additions))  # line 371
        _.assertEqual(0, len(changes.deletions))  # line 372
        _.assertEqual(0, len(changes.modifications))  # line 373
        _.createFile(1, "z")  # size change  # line 374
        changes = sos.changes()  # line 375
        _.assertEqual(0, len(changes.additions))  # line 376
        _.assertEqual(0, len(changes.deletions))  # line 377
        _.assertEqual(1, len(changes.modifications))  # line 378
        sos.commit("message")  # line 379
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 380
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.revisionFolder(0, 1)))  # line 381
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # no further files, only the modified one  # line 382
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 383
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 384
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 385
        os.unlink("file2")  # line 386
        changes = sos.changes()  # line 387
        _.assertEqual(0, len(changes.additions))  # line 388
        _.assertEqual(1, len(changes.deletions))  # line 389
        _.assertEqual(1, len(changes.modifications))  # line 390
        sos.commit("modified")  # line 391
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # no additional files, only mentions in metadata  # line 392
        try:  # expecting Exit due to no changes  # line 393
            sos.commit("nothing")  # expecting Exit due to no changes  # line 393
            _.fail()  # expecting Exit due to no changes  # line 393
        except:  # line 394
            pass  # line 394

    def testGetBranch(_):  # line 396
        m = sos.Metadata(os.getcwd())  # line 397
        m.branch = 1  # current branch  # line 398
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 399
        _.assertEqual(27, m.getBranchByName(27))  # line 400
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 401
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 402
        _.assertIsNone(m.getBranchByName("unknown"))  # line 403
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 404
        _.assertEqual(13, m.getRevisionByName("13"))  # line 405
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 406
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 407

    def testTagging(_):  # line 409
        m = sos.Metadata(os.getcwd())  # line 410
        sos.offline()  # line 411
        _.createFile(111)  # line 412
        sos.commit("tag", ["--tag"])  # line 413
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 414
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 415
        _.createFile(2)  # line 416
        try:  # line 417
            sos.commit("tag")  # line 417
            _.fail()  # line 417
        except:  # line 418
            pass  # line 418
        sos.commit("tag-2", ["--tag"])  # line 419
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 420
        _.assertIn("TAG tag", out)  # line 421

    def testSwitch(_):  # line 423
        _.createFile(1, "x" * 100)  # line 424
        _.createFile(2, "y")  # line 425
        sos.offline("test")  # file1-2  in initial branch commit  # line 426
        sos.branch("second")  # file1-2  switch, having same files  # line 427
        sos.switch("0")  # no change  switch back, no problem  # line 428
        sos.switch("second")  # no change  # switch back, no problem  # line 429
        _.createFile(3, "y")  # generate a file  # line 430
        try:  # uncommited changes detected  # line 431
            sos.switch("test")  # uncommited changes detected  # line 431
            _.fail()  # uncommited changes detected  # line 431
        except SystemExit as E:  # line 432
            _.assertEqual(1, E.code)  # line 432
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 433
        sos.changes()  # line 434
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 435
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 436
        _.createFile("XXX")  # line 437
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 438
        _.assertIn("File tree has changes", out)  # line 439
        _.assertNotIn("File tree is unchanged", out)  # line 440
        _.assertIn("  * b00   'test'", out)  # line 441
        _.assertIn("    b01 'second'", out)  # line 442
        _.assertIn("(dirty)", out)  # one branch has commits  # line 443
        _.assertIn("(in sync)", out)  # the other doesn't  # line 444
        _.createFile(4, "xy")  # generate a file  # line 445
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4  # line 446
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 447
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 448
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 449
        sos.switch("test", ["--force"])  # should restore file1 and remove file3  # line 450
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 451
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 452

    def testAutoDetectVCS(_):  # line 454
        os.mkdir(".git")  # line 455
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 456
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 457
            meta = fd.read()  # line 457
        _.assertTrue("\"master\"" in meta)  # line 458
        os.rmdir(".git")  # line 459

    def testUpdate(_):  # line 461
        sos.offline("trunk")  # create initial branch b0/r0  # line 462
        _.createFile(1, "x" * 100)  # line 463
        sos.commit("second")  # create b0/r1  # line 464

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 466
        _.assertFalse(_.existsFile(1))  # line 467

        sos.update("/1")  # recreate file1  # line 469
        _.assertTrue(_.existsFile(1))  # line 470

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 472
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2)))  # line 473
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2, file=sos.metaFile)))  # line 474
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta data file, no differential files  # line 475

        sos.update("/1")  # do nothing, as nothing has changed  # line 477
        _.assertTrue(_.existsFile(1))  # line 478

        _.createFile(2, "y" * 100)  # line 480
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", options=["--force"])  # automatically including file 2 (as we are in simple mode)  # line 483
        _.assertTrue(_.existsFile(2))  # line 484
        sos.update("trunk", ["--add"])  # only add stuff  # line 485
        _.assertTrue(_.existsFile(2))  # line 486
        sos.update("trunk")  # nothing to do  # line 487
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 488

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 490
        _.createFile(10, theirs)  # line 491
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 492
        _.createFile(11, mine)  # line 493
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 494
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 495

    def testUpdate2(_):  # line 497
        _.createFile("test.txt", "x" * 10)  # line 498
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 499
        sos.branch("mod")  # line 500
        time.sleep(FS_PRECISION)  # line 501
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 502
        sos.commit("mod")  # create b0/r1  # line 503
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 504
        with open("test.txt", "rb") as fd:  # line 505
            _.assertEqual(b"x" * 10, fd.read())  # line 505
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 506
        with open("test.txt", "rb") as fd:  # line 507
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 507
        _.createFile("test.txt", "x" * 10)  # line 508
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 509
        with open("test.txt", "rb") as fd:  # line 510
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 510
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 511
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 512
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 513
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 514
        with open("test.txt", "rb") as fd:  # line 515
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 515

    def testIsTextType(_):  # line 517
        m = sos.Metadata(".")  # line 518
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 519
        m.c.bintype = ["*.md.confluence"]  # line 520
        _.assertTrue(m.isTextType("ab.txt"))  # line 521
        _.assertTrue(m.isTextType("./ab.txt"))  # line 522
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 523
        _.assertFalse(m.isTextType("bc/ab."))  # line 524
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 525
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 526
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 527
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 528

    def testEolDet(_):  # line 530
        ''' Check correct end-of-line detection. '''  # line 531
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 532
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 533
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 534
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 535
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 536
        _.assertIsNone(sos.eoldet(b""))  # line 537
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 538

    def testMerge(_):  # line 540
        ''' Check merge results depending on user options. '''  # line 541
        a = b"a\nb\ncc\nd"  # type: bytes  # line 542
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 543
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge  # line 544
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace  # line 545
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace  # line 546
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge  # line 547
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 548
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 549
        a = b"a\nb\ncc\nd"  # line 550
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 551
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement  # line 552
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # line 553
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 554
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])  # line 556
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 557
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 559
        b = b"a\nc\ne"  # line 560
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 561
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 562
        a = b"a\nb\ne"  # intra-line merge  # line 563
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 564
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 565

    def testMergeEol(_):  # line 567
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])  # line 568
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 569
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF  # line 570
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])  # line 571
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])  # line 572

    def testPickyMode(_):  # line 574
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 575
        sos.offline("trunk", None, ["--picky"])  # line 576
        changes = sos.changes()  # line 577
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 578
        sos.add(".", "./file?", ["--force"])  # line 579
        _.createFile(1, "aa")  # line 580
        sos.commit("First")  # add one file  # line 581
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 582
        _.createFile(2, "b")  # line 583
        try:  # add nothing, because picky  # line 584
            sos.commit("Second")  # add nothing, because picky  # line 584
        except:  # line 585
            pass  # line 585
        sos.add(".", "./file?")  # line 586
        sos.commit("Third")  # line 587
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # line 588
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 589
        _.assertIn("  * r2", out)  # line 590
        _.createFile(3, prefix="sub")  # line 591
        sos.add("sub", "sub/file?")  # line 592
        changes = sos.changes()  # line 593
        _.assertEqual(1, len(changes.additions))  # line 594
        _.assertTrue("sub/file3" in changes.additions)  # line 595

    def testTrackedSubfolder(_):  # line 597
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 598
        os.mkdir("." + os.sep + "sub")  # line 599
        sos.offline("trunk", None, ["--track"])  # line 600
        _.createFile(1, "x")  # line 601
        _.createFile(1, "x", prefix="sub")  # line 602
        sos.add(".", "./file?")  # add glob pattern to track  # line 603
        sos.commit("First")  # line 604
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 605
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 606
        sos.commit("Second")  # one new file + meta  # line 607
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 608
        os.unlink("file1")  # remove from basefolder  # line 609
        _.createFile(2, "y")  # line 610
        sos.remove(".", "sub/file?")  # line 611
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 612
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 612
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 612
        except:  # line 613
            pass  # line 613
        sos.commit("Third")  # line 614
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta  # line 615
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 618
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 623
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 624
        _.createFile(1)  # line 625
        _.createFile("a123a")  # untracked file "a123a"  # line 626
        sos.add(".", "./file?")  # add glob tracking pattern  # line 627
        sos.commit("second")  # versions "file1"  # line 628
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 629
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 630
        _.assertIn("  | ./file?", out)  # line 631

        _.createFile(2)  # untracked file "file2"  # line 633
        sos.commit("third")  # versions "file2"  # line 634
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta file  # line 635

        os.mkdir("." + os.sep + "sub")  # line 637
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 638
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 639
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 3))))  # meta file only, no other tracked path/file  # line 640

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 642
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 643
        sos.add(".", "./a*a")  # add tracking pattern  # line 644
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 645
        _.assertEqual(0, len(changes.modifications))  # line 646
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 647
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 648

        sos.commit("Second_2")  # line 650
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(1, 1))))  # "a123a" + meta file  # line 651
        _.existsFile(1, b"x" * 10)  # line 652
        _.existsFile(2, b"x" * 10)  # line 653

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 655
        _.existsFile(1, b"x" * 10)  # line 656
        _.existsFile("a123a", b"x" * 10)  # line 657

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 659
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 660
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 661

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 663
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 664
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 665
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 666
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 667
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 668
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 669
# TODO test switch --meta

    def testLsTracked(_):  # line 672
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 673
        _.createFile(1)  # line 674
        _.createFile("foo")  # line 675
        sos.add(".", "./file*")  # capture one file  # line 676
        sos.ls()  # line 677
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 678
        _.assertInAny("TRK file1  (file*)", out)  # line 679
        _.assertNotInAny("... file1  (file*)", out)  # line 680
        _.assertInAny("··· foo", out)  # line 681
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 682
        _.assertInAny("TRK file*", out)  # line 683
        _.createFile("a", prefix="sub")  # line 684
        sos.add("sub", "sub/a")  # line 685
        sos.ls("sub")  # line 686
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 687

    def testLineMerge(_):  # line 689
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 690
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 691
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 692
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 693

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 695
        _.createFile(1)  # line 696
        sos.offline("master", options=["--force"])  # line 697
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 698
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 699
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 700
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 701
        _.createFile(2)  # line 702
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 703
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 704
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 705
        _.assertFalse(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 706

    def testLocalConfig(_):  # line 708
        sos.offline("bla", options=[])  # line 709
        try:  # line 710
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 710
        except SystemExit as E:  # line 711
            _.assertEqual(0, E.code)  # line 711
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 712

    def testConfigVariations(_):  # line 714
        def makeRepo():  # line 715
            try:  # line 716
                os.unlink("file1")  # line 716
            except:  # line 717
                pass  # line 717
            sos.offline("master", options=["--force"])  # line 718
            _.createFile(1)  # line 719
            sos.commit("Added file1")  # line 720
        try:  # line 721
            sos.config(["set", "strict", "on"])  # line 721
        except SystemExit as E:  # line 722
            _.assertEqual(0, E.code)  # line 722
        makeRepo()  # line 723
        _.assertTrue(checkRepoFlag("strict", True))  # line 724
        try:  # line 725
            sos.config(["set", "strict", "off"])  # line 725
        except SystemExit as E:  # line 726
            _.assertEqual(0, E.code)  # line 726
        makeRepo()  # line 727
        _.assertTrue(checkRepoFlag("strict", False))  # line 728
        try:  # line 729
            sos.config(["set", "strict", "yes"])  # line 729
        except SystemExit as E:  # line 730
            _.assertEqual(0, E.code)  # line 730
        makeRepo()  # line 731
        _.assertTrue(checkRepoFlag("strict", True))  # line 732
        try:  # line 733
            sos.config(["set", "strict", "no"])  # line 733
        except SystemExit as E:  # line 734
            _.assertEqual(0, E.code)  # line 734
        makeRepo()  # line 735
        _.assertTrue(checkRepoFlag("strict", False))  # line 736
        try:  # line 737
            sos.config(["set", "strict", "1"])  # line 737
        except SystemExit as E:  # line 738
            _.assertEqual(0, E.code)  # line 738
        makeRepo()  # line 739
        _.assertTrue(checkRepoFlag("strict", True))  # line 740
        try:  # line 741
            sos.config(["set", "strict", "0"])  # line 741
        except SystemExit as E:  # line 742
            _.assertEqual(0, E.code)  # line 742
        makeRepo()  # line 743
        _.assertTrue(checkRepoFlag("strict", False))  # line 744
        try:  # line 745
            sos.config(["set", "strict", "true"])  # line 745
        except SystemExit as E:  # line 746
            _.assertEqual(0, E.code)  # line 746
        makeRepo()  # line 747
        _.assertTrue(checkRepoFlag("strict", True))  # line 748
        try:  # line 749
            sos.config(["set", "strict", "false"])  # line 749
        except SystemExit as E:  # line 750
            _.assertEqual(0, E.code)  # line 750
        makeRepo()  # line 751
        _.assertTrue(checkRepoFlag("strict", False))  # line 752
        try:  # line 753
            sos.config(["set", "strict", "enable"])  # line 753
        except SystemExit as E:  # line 754
            _.assertEqual(0, E.code)  # line 754
        makeRepo()  # line 755
        _.assertTrue(checkRepoFlag("strict", True))  # line 756
        try:  # line 757
            sos.config(["set", "strict", "disable"])  # line 757
        except SystemExit as E:  # line 758
            _.assertEqual(0, E.code)  # line 758
        makeRepo()  # line 759
        _.assertTrue(checkRepoFlag("strict", False))  # line 760
        try:  # line 761
            sos.config(["set", "strict", "enabled"])  # line 761
        except SystemExit as E:  # line 762
            _.assertEqual(0, E.code)  # line 762
        makeRepo()  # line 763
        _.assertTrue(checkRepoFlag("strict", True))  # line 764
        try:  # line 765
            sos.config(["set", "strict", "disabled"])  # line 765
        except SystemExit as E:  # line 766
            _.assertEqual(0, E.code)  # line 766
        makeRepo()  # line 767
        _.assertTrue(checkRepoFlag("strict", False))  # line 768
        try:  # line 769
            sos.config(["set", "strict", "nope"])  # line 769
            _.fail()  # line 769
        except SystemExit as E:  # line 770
            _.assertEqual(1, E.code)  # line 770

    def testLsSimple(_):  # line 772
        _.createFile(1)  # line 773
        _.createFile("foo")  # line 774
        _.createFile("ign1")  # line 775
        _.createFile("ign2")  # line 776
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 777
        try:  # define an ignore pattern  # line 778
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 778
        except SystemExit as E:  # line 779
            _.assertEqual(0, E.code)  # line 779
        try:  # additional ignore pattern  # line 780
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 780
        except SystemExit as E:  # line 781
            _.assertEqual(0, E.code)  # line 781
        try:  # define a list of ignore patterns  # line 782
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 782
        except SystemExit as E:  # line 783
            _.assertEqual(0, E.code)  # line 783
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 784
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 785
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 786
        _.assertInAny('··· file1', out)  # line 787
        _.assertInAny('··· ign1', out)  # line 788
        _.assertInAny('··· ign2', out)  # line 789
        try:  # line 790
            sos.config(["rm", "foo", "bar"])  # line 790
            _.fail()  # line 790
        except SystemExit as E:  # line 791
            _.assertEqual(1, E.code)  # line 791
        try:  # line 792
            sos.config(["rm", "ignores", "foo"])  # line 792
            _.fail()  # line 792
        except SystemExit as E:  # line 793
            _.assertEqual(1, E.code)  # line 793
        try:  # line 794
            sos.config(["rm", "ignores", "ign1"])  # line 794
        except SystemExit as E:  # line 795
            _.assertEqual(0, E.code)  # line 795
        try:  # remove ignore pattern  # line 796
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 796
        except SystemExit as E:  # line 797
            _.assertEqual(0, E.code)  # line 797
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 798
        _.assertInAny('··· ign1', out)  # line 799
        _.assertInAny('IGN ign2', out)  # line 800
        _.assertNotInAny('··· ign2', out)  # line 801

    def testWhitelist(_):  # line 803
# TODO test same for simple mode
        _.createFile(1)  # line 805
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 806
        sos.offline("xx", options=["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 807
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 808
        sos.commit(options=["--force"])  # attempt to commit the file  # line 809
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta data, file1 was ignored  # line 810
        try:  # Exit because dirty  # line 811
            sos.online()  # Exit because dirty  # line 811
            _.fail()  # Exit because dirty  # line 811
        except:  # exception expected  # line 812
            pass  # exception expected  # line 812
        _.createFile("x2")  # add another change  # line 813
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 814
        try:  # force beyond dirty flag check  # line 815
            sos.online(["--force"])  # force beyond dirty flag check  # line 815
            _.fail()  # force beyond dirty flag check  # line 815
        except:  # line 816
            pass  # line 816
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 817
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 818

        _.createFile(1)  # line 820
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 821
        sos.offline("xx", None, ["--track"])  # line 822
        sos.add(".", "./file*")  # line 823
        sos.commit()  # should NOT ask for force here  # line 824
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 825

    def testRemove(_):  # line 827
        _.createFile(1, "x" * 100)  # line 828
        sos.offline("trunk")  # line 829
        try:  # line 830
            sos.destroy("trunk")  # line 830
            _fail()  # line 830
        except:  # line 831
            pass  # line 831
        _.createFile(2, "y" * 10)  # line 832
        sos.branch("added")  # creates new branch, writes repo metadata, and therefore creates backup copy  # line 833
        sos.destroy("trunk")  # line 834
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1"], os.listdir("." + os.sep + sos.metaFolder))  # line 835
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 836
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 837
        sos.branch("next")  # line 838
        _.createFile(3, "y" * 10)  # make a change  # line 839
        sos.destroy("added", "--force")  # should succeed  # line 840

    def testUsage(_):  # line 842
        try:  # TODO expect sys.exit(0)  # line 843
            sos.usage()  # TODO expect sys.exit(0)  # line 843
            _.fail()  # TODO expect sys.exit(0)  # line 843
        except:  # line 844
            pass  # line 844
        try:  # line 845
            sos.usage(short=True)  # line 845
            _.fail()  # line 845
        except:  # line 846
            pass  # line 846

    def testOnlyExcept(_):  # line 848
        ''' Test blacklist glob rules. '''  # line 849
        sos.offline(options=["--track"])  # line 850
        _.createFile("a.1")  # line 851
        _.createFile("a.2")  # line 852
        _.createFile("b.1")  # line 853
        _.createFile("b.2")  # line 854
        sos.add(".", "./a.?")  # line 855
        sos.add(".", "./?.1", negative=True)  # line 856
        out = wrapChannels(lambda: sos.commit())  # line 857
        _.assertIn("ADD ./a.2", out)  # line 858
        _.assertNotIn("ADD ./a.1", out)  # line 859
        _.assertNotIn("ADD ./b.1", out)  # line 860
        _.assertNotIn("ADD ./b.2", out)  # line 861

    def testOnly(_):  # line 863
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 864
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 865
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 866
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 867
        sos.offline(options=["--track", "--strict"])  # line 868
        _.createFile(1)  # line 869
        _.createFile(2)  # line 870
        sos.add(".", "./file1")  # line 871
        sos.add(".", "./file2")  # line 872
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 873
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta and file1  # line 874
        sos.commit()  # adds also file2  # line 875
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta and file1  # line 876
        _.createFile(1, "cc")  # modify both files  # line 877
        _.createFile(2, "dd")  # line 878
        try:  # line 879
            sos.config(["set", "texttype", "file2"])  # line 879
        except SystemExit as E:  # line 880
            _.assertEqual(0, E.code)  # line 880
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))  # line 881
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 882
        _.assertTrue("./file2" in changes.modifications)  # line 883
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 884
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 885

    def testDiff(_):  # line 887
        try:  # manually mark this file as "textual"  # line 888
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 888
        except SystemExit as E:  # line 889
            _.assertEqual(0, E.code)  # line 889
        sos.offline(options=["--strict"])  # line 890
        _.createFile(1)  # line 891
        _.createFile(2)  # line 892
        sos.commit()  # line 893
        _.createFile(1, "sdfsdgfsdf")  # line 894
        _.createFile(2, "12343")  # line 895
        sos.commit()  # line 896
        _.createFile(1, "foobar")  # line 897
        _.createFile(3)  # line 898
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 899
        _.assertIn("ADD ./file3", out)  # line 900
        _.assertAllIn(["MOD ./file2", "DIF ./file1  <No newline>", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 901
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 902

    def testReorderRenameActions(_):  # line 904
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 905
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 906
        try:  # line 907
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 907
            _.fail()  # line 907
        except:  # line 908
            pass  # line 908

    def testMove(_):  # line 910
        sos.offline(options=["--strict", "--track"])  # line 911
        _.createFile(1)  # line 912
        sos.add(".", "./file?")  # line 913
# test source folder missing
        try:  # line 915
            sos.move("sub", "sub/file?", ".", "?file")  # line 915
            _.fail()  # line 915
        except:  # line 916
            pass  # line 916
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 918
        _.assertTrue(os.path.exists("sub"))  # line 919
        _.assertTrue(os.path.exists("sub/file1"))  # line 920
        _.assertFalse(os.path.exists("file1"))  # line 921
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 923
        _.assertTrue(os.path.exists("1file"))  # line 924
        _.assertFalse(os.path.exists("sub/file1"))  # line 925
# test nothing matches source pattern
        try:  # line 927
            sos.move(".", "a*", ".", "b*")  # line 927
            _.fail()  # line 927
        except:  # line 928
            pass  # line 928
        sos.add(".", "*")  # anything pattern  # line 929
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 930
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 930
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 930
        except:  # line 931
            pass  # line 931
# test rename no conflict
        _.createFile(1)  # line 933
        _.createFile(2)  # line 934
        _.createFile(3)  # line 935
        sos.add(".", "./file*")  # line 936
        try:  # define an ignore pattern  # line 937
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 937
        except SystemExit as E:  # line 938
            _.assertEqual(0, E.code)  # line 938
        try:  # line 939
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 939
        except SystemExit as E:  # line 940
            _.assertEqual(0, E.code)  # line 940
        sos.move(".", "./file*", ".", "fi*le")  # line 941
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 942
        _.assertFalse(os.path.exists("fi4le"))  # line 943
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 945
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 949
        sos.add(".", "./?a?b", ["--force"])  # line 950
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 951
        _.createFile("1a2b")  # should not be tracked  # line 952
        _.createFile("a1b2")  # should be tracked  # line 953
        sos.commit()  # line 954
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 955
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 956
        _.createFile("1a1b1")  # line 957
        _.createFile("1a1b2")  # line 958
        sos.add(".", "?a?b*")  # line 959
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 960
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 964
        sos.offline()  # line 965
        _.createFile(1)  # line 966
        os.mkdir(sos.revisionFolder(0, 1))  # line 967
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.revisionFolder(0, 1))  # line 968
        _.createFile(1)  # line 969
        try:  # should exit with error due to collision detection  # line 970
            sos.commit()  # should exit with error due to collision detection  # line 970
            _.fail()  # should exit with error due to collision detection  # line 970
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 971
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 971

    def testFindBase(_):  # line 973
        old = os.getcwd()  # line 974
        try:  # line 975
            os.mkdir("." + os.sep + ".git")  # line 976
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 977
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 978
            os.chdir("a" + os.sep + "b")  # line 979
            s, vcs, cmd = sos.findSosVcsBase()  # line 980
            _.assertIsNotNone(s)  # line 981
            _.assertIsNotNone(vcs)  # line 982
            _.assertEqual("git", cmd)  # line 983
        finally:  # line 984
            os.chdir(old)  # line 984

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail

# TODO test +++ --- in diff
# TODO test +01/-02/*..
# TODO tests for loadcommit redirection
# TODO test wrong branch/revision after fast branching, would raise exception for -1 otherwise

if __name__ == '__main__':  # line 994
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 995
    c = configr.Configr("sos")  # line 996
    c.loadSettings()  # line 997
    if len(c.keys()) > 0:  # line 998
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 998
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 999
