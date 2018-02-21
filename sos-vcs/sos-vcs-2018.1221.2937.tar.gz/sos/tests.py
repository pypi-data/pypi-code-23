#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xbde26d8b

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

def sync():  # line 16
    os.sync() if sys.version_info[:2] >= (3, 3) else None  # line 16


def determineFilesystemTimeResolution() -> 'float':  # line 19
    name = str(uuid.uuid4())  # type: str  # line 20
    with open(name, "w") as fd:  # create temporary file  # line 21
        fd.write("x")  # create temporary file  # line 21
    mt = os.stat(name).st_mtime  # type: float  # get current timestamp  # line 22
    while os.stat(name).st_mtime == mt:  # wait until timestamp modified  # line 23
        time.sleep(0.05)  # to avoid 0.00s bugs (came up some time for unknown reasons)  # line 24
        with open(name, "w") as fd:  # line 25
            fd.write("x")  # line 25
    mt, start, _count = os.stat(name).st_mtime, time.time(), 0  # line 26
    while os.stat(name).st_mtime == mt:  # now cound and measure time until modified again  # line 27
        time.sleep(0.05)  # line 28
        _count += 1  # line 29
        with open(name, "w") as fd:  # line 30
            fd.write("x")  # line 30
    os.unlink(name)  # line 31
    fsprecision = round(time.time() - start, 2)  # type: float  # line 32
    print("File system timestamp precision is %.2fs; wrote to the file %d times during that time" % (fsprecision, _count))  # line 33
    return fsprecision  # line 34


FS_PRECISION = determineFilesystemTimeResolution() * 1.55  # line 37


@_coconut_tco  # line 40
def debugTestRunner(post_mortem=None):  # line 40
    ''' Unittest runner doing post mortem debugging on failing tests. '''  # line 41
    import pdb  # line 42
    if post_mortem is None:  # line 43
        post_mortem = pdb.post_mortem  # line 43
    class DebugTestResult(unittest.TextTestResult):  # line 44
        def addError(_, test, err):  # called before tearDown()  # line 45
            traceback.print_exception(*err)  # line 46
            post_mortem(err[2])  # line 47
            super(DebugTestResult, _).addError(test, err)  # line 48
        def addFailure(_, test, err):  # line 49
            traceback.print_exception(*err)  # line 50
            post_mortem(err[2])  # line 51
            super(DebugTestResult, _).addFailure(test, err)  # line 52
    return _coconut_tail_call(unittest.TextTestRunner, resultclass=DebugTestResult)  # line 53

@_coconut_tco  # line 55
def wrapChannels(func: '_coconut.typing.Callable[..., Any]') -> 'str':  # line 55
    ''' Wrap function call to capture and return strings emitted on stdout and stderr. '''  # line 56
    oldv = sys.argv  # line 57
    buf = TextIOWrapper(BufferedRandom(BytesIO(b"")), encoding=sos.UTF8)  # line 58
    handler = logging.StreamHandler(buf)  # TODO doesn't seem to be captured  # line 59
    sys.stdout = sys.stderr = buf  # line 60
    logging.getLogger().addHandler(handler)  # line 61
    try:  # capture output into buf  # line 62
        func()  # capture output into buf  # line 62
    except Exception as E:  # line 63
        buf.write(str(E) + "\n")  # line 63
        traceback.print_exc(file=buf)  # line 63
    except SystemExit as F:  # line 64
        buf.write("EXIT CODE %s" % F.code + "\n")  # line 64
        traceback.print_exc(file=buf)  # line 64
    logging.getLogger().removeHandler(handler)  # line 65
    sys.argv, sys.stdout, sys.stderr = oldv, sys.__stdout__, sys.__stderr__  # TODO when run using pythonw.exe and/or no console, these could be None  # line 66
    buf.seek(0)  # line 67
    return _coconut_tail_call(buf.read)  # line 68

def mockInput(datas: '_coconut.typing.Sequence[str]', func) -> 'Any':  # line 70
    with mock.patch("builtins.input", side_effect=datas):  # line 71
        return func()  # line 71

def setRepoFlag(name: 'str', value: 'bool'):  # line 73
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 74
        flags, branches, config = json.loads(fd.read())  # line 74
    flags[name] = value  # line 75
    with open(sos.metaFolder + os.sep + sos.metaFile, "w") as fd:  # line 76
        fd.write(json.dumps((flags, branches, config)))  # line 76

def checkRepoFlag(name: 'str', flag: '_coconut.typing.Optional[bool]'=None, value: '_coconut.typing.Optional[Any]'=None) -> 'bool':  # line 78
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 79
        flags, branches, config = json.loads(fd.read())  # line 79
    return (name in flags and flags[name] == flag) if flag is not None else (name in config and config[name] == value)  # line 80


class Tests(unittest.TestCase):  # line 83
    ''' Entire test suite. '''  # line 84

    def setUp(_):  # line 86
        sos.Metadata.singleton = None  # line 87
        for entry in os.listdir(testFolder):  # cannot remove testFolder on Windows when using TortoiseSVN as VCS  # line 88
            resource = os.path.join(testFolder, entry)  # line 89
            shutil.rmtree(resource) if os.path.isdir(resource) else os.unlink(resource)  # line 90
        os.chdir(testFolder)  # line 91


    def assertAllIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]', only: 'bool'=False):  # line 94
        for w in what:  # line 95
            _.assertIn(w, where)  # line 95
        if only:  # line 96
            _.assertEqual(len(what), len(where))  # line 96

    def assertAllNotIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]'):  # line 98
        for w in what:  # line 99
            _.assertNotIn(w, where)  # line 99

    def assertInAll(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 101
        for w in where:  # line 102
            _.assertIn(what, w)  # line 102

    def assertInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 104
        _.assertTrue(any((what in w for w in where)))  # line 104

    def assertNotInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 106
        _.assertFalse(any((what in w for w in where)))  # line 106

    def createFile(_, number: 'Union[int, str]', contents: 'str'="x" * 10, prefix: '_coconut.typing.Optional[str]'=None):  # line 108
        if prefix and not os.path.exists(prefix):  # line 109
            os.makedirs(prefix)  # line 109
        with open(("." if prefix is None else prefix) + os.sep + (("file%d" % number) if isinstance(number, int) else number), "wb") as fd:  # line 110
            fd.write(contents if isinstance(contents, bytes) else contents.encode("cp1252"))  # line 110

    def existsFile(_, number: 'Union[int, str]', expectedContents: 'bytes'=None) -> 'bool':  # line 112
        if not os.path.exists(("." + os.sep + "file%d" % number) if isinstance(number, int) else number):  # line 113
            return False  # line 113
        if expectedContents is None:  # line 114
            return True  # line 114
        with open(("." + os.sep + "file%d" % number) if isinstance(number, int) else number, "rb") as fd:  # line 115
            return fd.read() == expectedContents  # line 115

    def testAccessor(_):  # line 117
        a = sos.Accessor({"a": 1})  # line 118
        _.assertEqual((1, 1), (a["a"], a.a))  # line 119

    def testGetAnyOfmap(_):  # line 121
        _.assertEqual(2, sos.getAnyOfMap({"a": 1, "b": 2}, ["x", "b"]))  # line 122
        _.assertIsNone(sos.getAnyOfMap({"a": 1, "b": 2}, []))  # line 123

    def testAjoin(_):  # line 125
        _.assertEqual("a1a2", sos.ajoin("a", ["1", "2"]))  # line 126
        _.assertEqual("* a\n* b", sos.ajoin("* ", ["a", "b"], "\n"))  # line 127

    def testFindChanges(_):  # line 129
        m = sos.Metadata(os.getcwd())  # line 130
        try:  # line 131
            sos.config(["set", "texttype", "*"])  # line 131
        except SystemExit as E:  # line 132
            _.assertEqual(0, E.code)  # line 132
        try:  # will be stripped from leading paths anyway  # line 133
            sos.config(["set", "ignores", "test/*.cfg;D:\\apps\\*.cfg.bak"])  # will be stripped from leading paths anyway  # line 133
        except SystemExit as E:  # line 134
            _.assertEqual(0, E.code)  # line 134
        m = sos.Metadata(os.getcwd())  # reload from file system  # line 135
        for file in [f for f in os.listdir() if f.endswith(".bak")]:  # remove configuration file  # line 136
            os.unlink(file)  # remove configuration file  # line 136
        _.createFile(1, "1")  # line 137
        m.createBranch(0)  # line 138
        _.assertEqual(1, len(m.paths))  # line 139
        time.sleep(FS_PRECISION)  # time required by filesystem time resolution issues  # line 140
        _.createFile(1, "2")  # modify existing file  # line 141
        _.createFile(2, "2")  # add another file  # line 142
        m.loadCommit(0, 0)  # line 143
        changes, msg = m.findChanges()  # detect time skew  # line 144
        _.assertEqual(1, len(changes.additions))  # line 145
        _.assertEqual(0, len(changes.deletions))  # line 146
        _.assertEqual(1, len(changes.modifications))  # line 147
        _.assertEqual(0, len(changes.moves))  # line 148
        m.paths.update(changes.additions)  # line 149
        m.paths.update(changes.modifications)  # line 150
        _.createFile(2, "12")  # modify file again  # line 151
        changes, msg = m.findChanges(0, 1)  # by size, creating new commit  # line 152
        _.assertEqual(0, len(changes.additions))  # line 153
        _.assertEqual(0, len(changes.deletions))  # line 154
        _.assertEqual(1, len(changes.modifications))  # line 155
        _.assertEqual(0, len(changes.moves))  # line 156
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1)))  # line 157
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # line 158
# TODO test moves

    def testMoves(_):  # line 161
        _.createFile(1, "1")  # line 162
        _.createFile(2, "2", "sub")  # line 163
        sos.offline(options=["--strict"])  # line 164
        os.renames("." + os.sep + "file1", "sub" + os.sep + "file1")  # line 165
        os.renames("sub" + os.sep + "file2", "." + os.sep + "file2")  # line 166
        out = wrapChannels(lambda: sos.changes())  # type: str  # line 167
        _.assertIn("MOV ./file2  <-  sub/file2", out)  # line 168
        _.assertIn("MOV sub/file1  <-  ./file1", out)  # line 169
        out = wrapChannels(lambda: sos.commit())  # line 170
        _.assertIn("MOV ./file2  <-  sub/file2", out)  # line 171
        _.assertIn("MOV sub/file1  <-  ./file1", out)  # line 172
        _.assertIn("Created new revision r01 (+00/-00/\u00b100/\U0001F5C002)", out)  # TODO why is this not captured?  # line 173

    def testPatternPaths(_):  # line 175
        sos.offline(options=["--track"])  # line 176
        os.mkdir("sub")  # line 177
        _.createFile("sub" + os.sep + "file1", "sdfsdf")  # line 178
        sos.add("sub", "sub/file?")  # line 179
        sos.commit("test")  # should pick up sub/file1 pattern  # line 180
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # sub/file1 was added  # line 181
        _.createFile(1)  # line 182
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 183
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 183
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 183
        except:  # line 184
            pass  # line 184

    def testNoArgs(_):  # line 186
        pass  # call "sos" without arguments should simply show help or info about missing arguments  # line 187

    def testAutoUpgrade(_):  # line 189
        sos.offline()  # line 190
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "r", encoding=sos.UTF8) as fd:  # line 191
            repo, branches, config = json.load(fd)  # line 191
        repo["version"] = "0"  # lower than any pip version  # line 192
        branches[:] = [branch[:5] for branch in branches]  # simulate some older state  # line 193
        del repo["format"]  # simulate pre-1.3.5  # line 194
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "w", encoding=sos.UTF8) as fd:  # line 195
            json.dump((repo, branches, config), fd, ensure_ascii=False)  # line 195
        out = wrapChannels(lambda: sos.status(options=["--repo"]))  # line 196
        _.assertAllIn(["Upgraded repository metadata to match SOS version '2018.1210.3028'", "Upgraded repository metadata to match SOS version '1.3.5'"], out)  # line 197

    def testFastBranching(_):  # line 199
        _.createFile(1)  # line 200
        sos.offline(options=["--strict"])  # b0/r0 = ./file1  # line 201
        _.createFile(2)  # line 202
        os.unlink("file1")  # line 203
        sos.commit()  # b0/r1 = ./file2  # line 204
        sos.branch(options=["--fast", "--last"])  # branch b1 from b0/1 TODO modify once --fast becomes the new normal  # line 205
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0", "b1"], os.listdir(sos.metaFolder), only=True)  # line 206
        _.createFile(3)  # line 207
        sos.commit()  # b1/r2 = ./file2, ./file3  # line 208
        _.assertAllIn([sos.metaFile, "r2"], os.listdir(sos.branchFolder(1)), only=True)  # line 209
        sos.branch(options=["--fast", "--last"])  # branch b2 from b1/2  # line 210
        sos.destroy("0")  # remove parent of b1 and transitive parent of b2  # line 211
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1", "b2"], os.listdir(sos.metaFolder), only=True)  # branch 0 was removed  # line 212
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(1)), only=True)  # revisions were copied to branch 1  # line 213
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(2)), only=True)  # revisions were copied to branch 1  # line 214
# TODO test also other functions like status --repo, log

    def testGetParentBranch(_):  # line 217
        m = sos.Accessor({"branches": {0: sos.Accessor({"parent": None, "revision": None}), 1: sos.Accessor({"parent": 0, "revision": 1})}})  # line 218
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 0))  # line 219
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 1))  # line 220
        _.assertEqual(1, sos.Metadata.getParentBranch(m, 1, 2))  # line 221
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 0, 10))  # line 222

    def testTokenizeGlobPattern(_):  # line 224
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 225
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 226
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 227
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 228
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 229
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 230

    def testTokenizeGlobPatterns(_):  # line 232
        try:  # because number of literal strings differs  # line 233
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 233
            _.fail()  # because number of literal strings differs  # line 233
        except:  # line 234
            pass  # line 234
        try:  # because glob patterns differ  # line 235
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 235
            _.fail()  # because glob patterns differ  # line 235
        except:  # line 236
            pass  # line 236
        try:  # glob patterns differ, regardless of position  # line 237
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 237
            _.fail()  # glob patterns differ, regardless of position  # line 237
        except:  # line 238
            pass  # line 238
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 239
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 240
        try:  # succeeds, because glob patterns match (differ only in position)  # line 241
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 241
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 241
        except:  # line 242
            pass  # line 242

    def testConvertGlobFiles(_):  # line 244
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 245
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 246

    def testFolderRemove(_):  # line 248
        m = sos.Metadata(os.getcwd())  # line 249
        _.createFile(1)  # line 250
        _.createFile("a", prefix="sub")  # line 251
        sos.offline()  # line 252
        _.createFile(2)  # line 253
        os.unlink("sub" + os.sep + "a")  # line 254
        os.rmdir("sub")  # line 255
        changes = sos.changes()  # TODO replace by output check  # line 256
        _.assertEqual(1, len(changes.additions))  # line 257
        _.assertEqual(0, len(changes.modifications))  # line 258
        _.assertEqual(1, len(changes.deletions))  # line 259
        _.createFile("a", prefix="sub")  # line 260
        changes = sos.changes()  # line 261
        _.assertEqual(0, len(changes.deletions))  # line 262

    def testSwitchConflict(_):  # line 264
        sos.offline(options=["--strict"])  # (r0)  # line 265
        _.createFile(1)  # line 266
        sos.commit()  # add file (r1)  # line 267
        os.unlink("file1")  # line 268
        sos.commit()  # remove (r2)  # line 269
        _.createFile(1, "something else")  # line 270
        sos.commit()  # (r3)  # line 271
        sos.switch("/1")  # updates file1 - marked as MOD, because mtime was changed  # line 272
        _.existsFile(1, "x" * 10)  # line 273
        sos.switch("/2", ["--force"])  # remove file1 requires --force, because size/content (or mtime in non-strict mode) is different to head of branch  # line 274
        sos.switch("/0")  # do nothing, as file1 is already removed  # line 275
        sos.switch("/1")  # add file1 back  # line 276
        sos.switch("/", ["--force"])  # requires force because changed vs. head of branch  # line 277
        _.existsFile(1, "something else")  # line 278

    def testComputeSequentialPathSet(_):  # line 280
        os.makedirs(sos.revisionFolder(0, 0))  # line 281
        os.makedirs(sos.revisionFolder(0, 1))  # line 282
        os.makedirs(sos.revisionFolder(0, 2))  # line 283
        os.makedirs(sos.revisionFolder(0, 3))  # line 284
        os.makedirs(sos.revisionFolder(0, 4))  # line 285
        m = sos.Metadata(os.getcwd())  # line 286
        m.branch = 0  # line 287
        m.commit = 2  # line 288
        m.saveBranches()  # line 289
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 290
        m.saveCommit(0, 0)  # initial  # line 291
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 292
        m.saveCommit(0, 1)  # mod  # line 293
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 294
        m.saveCommit(0, 2)  # add  # line 295
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 296
        m.saveCommit(0, 3)  # del  # line 297
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")  # line 298
        m.saveCommit(0, 4)  # readd  # line 299
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 300
        m.saveBranch(0)  # line 301
        m.branches = {0: sos.BranchInfo(0, 0), 1: sos.BranchInfo(1, 0)}  # line 302
        m.saveBranches()  # line 303
        m.computeSequentialPathSet(0, 4)  # line 304
        _.assertEqual(2, len(m.paths))  # line 305

    def testParseRevisionString(_):  # line 307
        m = sos.Metadata(os.getcwd())  # line 308
        m.branch = 1  # line 309
        m.commits = {0: 0, 1: 1, 2: 2}  # line 310
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 311
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 312
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 313
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 314
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 315
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 316
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 317

    def testOfflineEmpty(_):  # line 319
        os.mkdir("." + os.sep + sos.metaFolder)  # line 320
        try:  # line 321
            sos.offline("trunk")  # line 321
            _.fail()  # line 321
        except SystemExit as E:  # line 322
            _.assertEqual(1, E.code)  # line 322
        os.rmdir("." + os.sep + sos.metaFolder)  # line 323
        sos.offline("test")  # line 324
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 325
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 326
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 327
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 328
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 329
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file  # line 330

    def testOfflineWithFiles(_):  # line 332
        _.createFile(1, "x" * 100)  # line 333
        _.createFile(2)  # line 334
        sos.offline("test")  # line 335
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 336
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 337
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 338
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 339
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 340
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 341
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file plus branch base file copies  # line 342

    def testBranch(_):  # line 344
        _.createFile(1, "x" * 100)  # line 345
        _.createFile(2)  # line 346
        sos.offline("test")  # b0/r0  # line 347
        sos.branch("other")  # b1/r0  # line 348
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 349
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 350
        _.assertEqual(list(sorted(os.listdir(sos.revisionFolder(0, 0)))), list(sorted(os.listdir(sos.revisionFolder(1, 0)))))  # line 352
        _.createFile(1, "z")  # modify file  # line 354
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 355
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 356
        _.createFile(3, "z")  # line 358
        sos.branch("from_last_revision", options=["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 359
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 360
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 365
        _.createFile(1, "x" * 100)  # line 366
        _.createFile(2)  # line 367
        sos.offline("test")  # line 368
        changes = sos.changes()  # line 369
        _.assertEqual(0, len(changes.additions))  # line 370
        _.assertEqual(0, len(changes.deletions))  # line 371
        _.assertEqual(0, len(changes.modifications))  # line 372
        _.createFile(1, "z")  # size change  # line 373
        changes = sos.changes()  # line 374
        _.assertEqual(0, len(changes.additions))  # line 375
        _.assertEqual(0, len(changes.deletions))  # line 376
        _.assertEqual(1, len(changes.modifications))  # line 377
        sos.commit("message")  # line 378
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 379
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.revisionFolder(0, 1)))  # line 380
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # no further files, only the modified one  # line 381
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 382
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 383
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 384
        os.unlink("file2")  # line 385
        changes = sos.changes()  # line 386
        _.assertEqual(0, len(changes.additions))  # line 387
        _.assertEqual(1, len(changes.deletions))  # line 388
        _.assertEqual(1, len(changes.modifications))  # line 389
        sos.commit("modified")  # line 390
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # no additional files, only mentions in metadata  # line 391
        try:  # expecting Exit due to no changes  # line 392
            sos.commit("nothing")  # expecting Exit due to no changes  # line 392
            _.fail()  # expecting Exit due to no changes  # line 392
        except:  # line 393
            pass  # line 393

    def testGetBranch(_):  # line 395
        m = sos.Metadata(os.getcwd())  # line 396
        m.branch = 1  # current branch  # line 397
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 398
        _.assertEqual(27, m.getBranchByName(27))  # line 399
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 400
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 401
        _.assertIsNone(m.getBranchByName("unknown"))  # line 402
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 403
        _.assertEqual(13, m.getRevisionByName("13"))  # line 404
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 405
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 406

    def testTagging(_):  # line 408
        m = sos.Metadata(os.getcwd())  # line 409
        sos.offline()  # line 410
        _.createFile(111)  # line 411
        sos.commit("tag", ["--tag"])  # line 412
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 413
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 414
        _.createFile(2)  # line 415
        try:  # line 416
            sos.commit("tag")  # line 416
            _.fail()  # line 416
        except:  # line 417
            pass  # line 417
        sos.commit("tag-2", ["--tag"])  # line 418
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 419
        _.assertIn("TAG tag", out)  # line 420

    def testSwitch(_):  # line 422
        _.createFile(1, "x" * 100)  # line 423
        _.createFile(2, "y")  # line 424
        sos.offline("test")  # file1-2  in initial branch commit  # line 425
        sos.branch("second")  # file1-2  switch, having same files  # line 426
        sos.switch("0")  # no change  switch back, no problem  # line 427
        sos.switch("second")  # no change  # switch back, no problem  # line 428
        _.createFile(3, "y")  # generate a file  # line 429
        try:  # uncommited changes detected  # line 430
            sos.switch("test")  # uncommited changes detected  # line 430
            _.fail()  # uncommited changes detected  # line 430
        except SystemExit as E:  # line 431
            _.assertEqual(1, E.code)  # line 431
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 432
        sos.changes()  # line 433
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 434
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 435
        _.createFile("XXX")  # line 436
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 437
        _.assertIn("File tree has changes", out)  # line 438
        _.assertNotIn("File tree is unchanged", out)  # line 439
        _.assertIn("  * b00   'test'", out)  # line 440
        _.assertIn("    b01 'second'", out)  # line 441
        _.assertIn("(dirty)", out)  # one branch has commits  # line 442
        _.assertIn("(in sync)", out)  # the other doesn't  # line 443
        _.createFile(4, "xy")  # generate a file  # line 444
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4  # line 445
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 446
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 447
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 448
        sos.switch("test", ["--force"])  # should restore file1 and remove file3  # line 449
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 450
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 451

    def testAutoDetectVCS(_):  # line 453
        os.mkdir(".git")  # line 454
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 455
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 456
            meta = fd.read()  # line 456
        _.assertTrue("\"master\"" in meta)  # line 457
        os.rmdir(".git")  # line 458

    def testUpdate(_):  # line 460
        sos.offline("trunk")  # create initial branch b0/r0  # line 461
        _.createFile(1, "x" * 100)  # line 462
        sos.commit("second")  # create b0/r1  # line 463

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 465
        _.assertFalse(_.existsFile(1))  # line 466

        sos.update("/1")  # recreate file1  # line 468
        _.assertTrue(_.existsFile(1))  # line 469

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 471
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2)))  # line 472
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2, file=sos.metaFile)))  # line 473
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta data file, no differential files  # line 474

        sos.update("/1")  # do nothing, as nothing has changed  # line 476
        _.assertTrue(_.existsFile(1))  # line 477

        _.createFile(2, "y" * 100)  # line 479
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", options=["--force"])  # automatically including file 2 (as we are in simple mode)  # line 482
        _.assertTrue(_.existsFile(2))  # line 483
        sos.update("trunk", ["--add"])  # only add stuff  # line 484
        _.assertTrue(_.existsFile(2))  # line 485
        sos.update("trunk")  # nothing to do  # line 486
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 487

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 489
        _.createFile(10, theirs)  # line 490
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 491
        _.createFile(11, mine)  # line 492
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 493
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 494

    def testUpdate2(_):  # line 496
        _.createFile("test.txt", "x" * 10)  # line 497
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 498
        sos.branch("mod")  # line 499
        time.sleep(FS_PRECISION)  # line 500
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 501
        sos.commit("mod")  # create b0/r1  # line 502
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 503
        with open("test.txt", "rb") as fd:  # line 504
            _.assertEqual(b"x" * 10, fd.read())  # line 504
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 505
        with open("test.txt", "rb") as fd:  # line 506
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 506
        _.createFile("test.txt", "x" * 10)  # line 507
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 508
        with open("test.txt", "rb") as fd:  # line 509
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 509
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 510
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 511
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 512
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 513
        with open("test.txt", "rb") as fd:  # line 514
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 514

    def testIsTextType(_):  # line 516
        m = sos.Metadata(".")  # line 517
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 518
        m.c.bintype = ["*.md.confluence"]  # line 519
        _.assertTrue(m.isTextType("ab.txt"))  # line 520
        _.assertTrue(m.isTextType("./ab.txt"))  # line 521
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 522
        _.assertFalse(m.isTextType("bc/ab."))  # line 523
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 524
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 525
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 526
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 527

    def testEolDet(_):  # line 529
        ''' Check correct end-of-line detection. '''  # line 530
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 531
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 532
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 533
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 534
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 535
        _.assertIsNone(sos.eoldet(b""))  # line 536
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 537

    def testMerge(_):  # line 539
        ''' Check merge results depending on user options. '''  # line 540
        a = b"a\nb\ncc\nd"  # type: bytes  # line 541
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 542
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge  # line 543
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace  # line 544
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace  # line 545
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge  # line 546
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 547
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 548
        a = b"a\nb\ncc\nd"  # line 549
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 550
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement  # line 551
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # line 552
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 553
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])  # line 555
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 556
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 558
        b = b"a\nc\ne"  # line 559
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 560
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 561
        a = b"a\nb\ne"  # intra-line merge  # line 562
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 563
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 564

    def testMergeEol(_):  # line 566
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])  # line 567
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 568
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF  # line 569
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])  # line 570
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])  # line 571

    def testPickyMode(_):  # line 573
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 574
        sos.offline("trunk", None, ["--picky"])  # line 575
        changes = sos.changes()  # line 576
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 577
        sos.add(".", "./file?", ["--force"])  # line 578
        _.createFile(1, "aa")  # line 579
        sos.commit("First")  # add one file  # line 580
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 581
        _.createFile(2, "b")  # line 582
        try:  # add nothing, because picky  # line 583
            sos.commit("Second")  # add nothing, because picky  # line 583
        except:  # line 584
            pass  # line 584
        sos.add(".", "./file?")  # line 585
        sos.commit("Third")  # line 586
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # line 587
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 588
        _.assertIn("  * r2", out)  # line 589
        _.createFile(3, prefix="sub")  # line 590
        sos.add("sub", "sub/file?")  # line 591
        changes = sos.changes()  # line 592
        _.assertEqual(1, len(changes.additions))  # line 593
        _.assertTrue("sub/file3" in changes.additions)  # line 594

    def testTrackedSubfolder(_):  # line 596
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 597
        os.mkdir("." + os.sep + "sub")  # line 598
        sos.offline("trunk", None, ["--track"])  # line 599
        _.createFile(1, "x")  # line 600
        _.createFile(1, "x", prefix="sub")  # line 601
        sos.add(".", "./file?")  # add glob pattern to track  # line 602
        sos.commit("First")  # line 603
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 604
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 605
        sos.commit("Second")  # one new file + meta  # line 606
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 607
        os.unlink("file1")  # remove from basefolder  # line 608
        _.createFile(2, "y")  # line 609
        sos.remove(".", "sub/file?")  # line 610
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 611
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 611
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 611
        except:  # line 612
            pass  # line 612
        sos.commit("Third")  # line 613
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta  # line 614
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 617
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 622
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 623
        _.createFile(1)  # line 624
        _.createFile("a123a")  # untracked file "a123a"  # line 625
        sos.add(".", "./file?")  # add glob tracking pattern  # line 626
        sos.commit("second")  # versions "file1"  # line 627
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 628
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 629
        _.assertIn("  | ./file?", out)  # line 630

        _.createFile(2)  # untracked file "file2"  # line 632
        sos.commit("third")  # versions "file2"  # line 633
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta file  # line 634

        os.mkdir("." + os.sep + "sub")  # line 636
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 637
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 638
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 3))))  # meta file only, no other tracked path/file  # line 639

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 641
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 642
        sos.add(".", "./a*a")  # add tracking pattern  # line 643
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 644
        _.assertEqual(0, len(changes.modifications))  # line 645
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 646
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 647

        sos.commit("Second_2")  # line 649
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(1, 1))))  # "a123a" + meta file  # line 650
        _.existsFile(1, b"x" * 10)  # line 651
        _.existsFile(2, b"x" * 10)  # line 652

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 654
        _.existsFile(1, b"x" * 10)  # line 655
        _.existsFile("a123a", b"x" * 10)  # line 656

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 658
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 659
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 660

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 662
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 663
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 664
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 665
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 666
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 667
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 668
# TODO test switch --meta

    def testLsTracked(_):  # line 671
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 672
        _.createFile(1)  # line 673
        _.createFile("foo")  # line 674
        sos.add(".", "./file*")  # capture one file  # line 675
        sos.ls()  # line 676
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 677
        _.assertInAny("TRK file1  (file*)", out)  # line 678
        _.assertNotInAny("... file1  (file*)", out)  # line 679
        _.assertInAny("··· foo", out)  # line 680
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 681
        _.assertInAny("TRK file*", out)  # line 682
        _.createFile("a", prefix="sub")  # line 683
        sos.add("sub", "sub/a")  # line 684
        sos.ls("sub")  # line 685
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 686

    def testLineMerge(_):  # line 688
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 689
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 690
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 691
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 692

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 694
        _.createFile(1)  # line 695
        sos.offline("master", options=["--force"])  # line 696
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 697
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 698
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 699
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 700
        _.createFile(2)  # line 701
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 702
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 703
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 704
        _.assertFalse(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 705

    def testLocalConfig(_):  # line 707
        sos.offline("bla", options=[])  # line 708
        try:  # line 709
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 709
        except SystemExit as E:  # line 710
            _.assertEqual(0, E.code)  # line 710
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 711

    def testConfigVariations(_):  # line 713
        def makeRepo():  # line 714
            try:  # line 715
                os.unlink("file1")  # line 715
            except:  # line 716
                pass  # line 716
            sos.offline("master", options=["--force"])  # line 717
            _.createFile(1)  # line 718
            sos.commit("Added file1")  # line 719
        try:  # line 720
            sos.config(["set", "strict", "on"])  # line 720
        except SystemExit as E:  # line 721
            _.assertEqual(0, E.code)  # line 721
        makeRepo()  # line 722
        _.assertTrue(checkRepoFlag("strict", True))  # line 723
        try:  # line 724
            sos.config(["set", "strict", "off"])  # line 724
        except SystemExit as E:  # line 725
            _.assertEqual(0, E.code)  # line 725
        makeRepo()  # line 726
        _.assertTrue(checkRepoFlag("strict", False))  # line 727
        try:  # line 728
            sos.config(["set", "strict", "yes"])  # line 728
        except SystemExit as E:  # line 729
            _.assertEqual(0, E.code)  # line 729
        makeRepo()  # line 730
        _.assertTrue(checkRepoFlag("strict", True))  # line 731
        try:  # line 732
            sos.config(["set", "strict", "no"])  # line 732
        except SystemExit as E:  # line 733
            _.assertEqual(0, E.code)  # line 733
        makeRepo()  # line 734
        _.assertTrue(checkRepoFlag("strict", False))  # line 735
        try:  # line 736
            sos.config(["set", "strict", "1"])  # line 736
        except SystemExit as E:  # line 737
            _.assertEqual(0, E.code)  # line 737
        makeRepo()  # line 738
        _.assertTrue(checkRepoFlag("strict", True))  # line 739
        try:  # line 740
            sos.config(["set", "strict", "0"])  # line 740
        except SystemExit as E:  # line 741
            _.assertEqual(0, E.code)  # line 741
        makeRepo()  # line 742
        _.assertTrue(checkRepoFlag("strict", False))  # line 743
        try:  # line 744
            sos.config(["set", "strict", "true"])  # line 744
        except SystemExit as E:  # line 745
            _.assertEqual(0, E.code)  # line 745
        makeRepo()  # line 746
        _.assertTrue(checkRepoFlag("strict", True))  # line 747
        try:  # line 748
            sos.config(["set", "strict", "false"])  # line 748
        except SystemExit as E:  # line 749
            _.assertEqual(0, E.code)  # line 749
        makeRepo()  # line 750
        _.assertTrue(checkRepoFlag("strict", False))  # line 751
        try:  # line 752
            sos.config(["set", "strict", "enable"])  # line 752
        except SystemExit as E:  # line 753
            _.assertEqual(0, E.code)  # line 753
        makeRepo()  # line 754
        _.assertTrue(checkRepoFlag("strict", True))  # line 755
        try:  # line 756
            sos.config(["set", "strict", "disable"])  # line 756
        except SystemExit as E:  # line 757
            _.assertEqual(0, E.code)  # line 757
        makeRepo()  # line 758
        _.assertTrue(checkRepoFlag("strict", False))  # line 759
        try:  # line 760
            sos.config(["set", "strict", "enabled"])  # line 760
        except SystemExit as E:  # line 761
            _.assertEqual(0, E.code)  # line 761
        makeRepo()  # line 762
        _.assertTrue(checkRepoFlag("strict", True))  # line 763
        try:  # line 764
            sos.config(["set", "strict", "disabled"])  # line 764
        except SystemExit as E:  # line 765
            _.assertEqual(0, E.code)  # line 765
        makeRepo()  # line 766
        _.assertTrue(checkRepoFlag("strict", False))  # line 767
        try:  # line 768
            sos.config(["set", "strict", "nope"])  # line 768
            _.fail()  # line 768
        except SystemExit as E:  # line 769
            _.assertEqual(1, E.code)  # line 769

    def testLsSimple(_):  # line 771
        _.createFile(1)  # line 772
        _.createFile("foo")  # line 773
        _.createFile("ign1")  # line 774
        _.createFile("ign2")  # line 775
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 776
        try:  # define an ignore pattern  # line 777
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 777
        except SystemExit as E:  # line 778
            _.assertEqual(0, E.code)  # line 778
        try:  # additional ignore pattern  # line 779
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 779
        except SystemExit as E:  # line 780
            _.assertEqual(0, E.code)  # line 780
        try:  # define a list of ignore patterns  # line 781
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 781
        except SystemExit as E:  # line 782
            _.assertEqual(0, E.code)  # line 782
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 783
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 784
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 785
        _.assertInAny('··· file1', out)  # line 786
        _.assertInAny('··· ign1', out)  # line 787
        _.assertInAny('··· ign2', out)  # line 788
        try:  # line 789
            sos.config(["rm", "foo", "bar"])  # line 789
            _.fail()  # line 789
        except SystemExit as E:  # line 790
            _.assertEqual(1, E.code)  # line 790
        try:  # line 791
            sos.config(["rm", "ignores", "foo"])  # line 791
            _.fail()  # line 791
        except SystemExit as E:  # line 792
            _.assertEqual(1, E.code)  # line 792
        try:  # line 793
            sos.config(["rm", "ignores", "ign1"])  # line 793
        except SystemExit as E:  # line 794
            _.assertEqual(0, E.code)  # line 794
        try:  # remove ignore pattern  # line 795
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 795
        except SystemExit as E:  # line 796
            _.assertEqual(0, E.code)  # line 796
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 797
        _.assertInAny('··· ign1', out)  # line 798
        _.assertInAny('IGN ign2', out)  # line 799
        _.assertNotInAny('··· ign2', out)  # line 800

    def testWhitelist(_):  # line 802
# TODO test same for simple mode
        _.createFile(1)  # line 804
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 805
        sos.offline("xx", options=["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 806
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 807
        sos.commit(options=["--force"])  # attempt to commit the file  # line 808
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta data, file1 was ignored  # line 809
        try:  # Exit because dirty  # line 810
            sos.online()  # Exit because dirty  # line 810
            _.fail()  # Exit because dirty  # line 810
        except:  # exception expected  # line 811
            pass  # exception expected  # line 811
        _.createFile("x2")  # add another change  # line 812
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 813
        try:  # force beyond dirty flag check  # line 814
            sos.online(["--force"])  # force beyond dirty flag check  # line 814
            _.fail()  # force beyond dirty flag check  # line 814
        except:  # line 815
            pass  # line 815
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 816
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 817

        _.createFile(1)  # line 819
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 820
        sos.offline("xx", None, ["--track"])  # line 821
        sos.add(".", "./file*")  # line 822
        sos.commit()  # should NOT ask for force here  # line 823
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 824

    def testRemove(_):  # line 826
        _.createFile(1, "x" * 100)  # line 827
        sos.offline("trunk")  # line 828
        try:  # line 829
            sos.destroy("trunk")  # line 829
            _fail()  # line 829
        except:  # line 830
            pass  # line 830
        _.createFile(2, "y" * 10)  # line 831
        sos.branch("added")  # creates new branch, writes repo metadata, and therefore creates backup copy  # line 832
        sos.destroy("trunk")  # line 833
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1"], os.listdir("." + os.sep + sos.metaFolder))  # line 834
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 835
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 836
        sos.branch("next")  # line 837
        _.createFile(3, "y" * 10)  # make a change  # line 838
        sos.destroy("added", "--force")  # should succeed  # line 839

    def testUsage(_):  # line 841
        try:  # TODO expect sys.exit(0)  # line 842
            sos.usage()  # TODO expect sys.exit(0)  # line 842
            _.fail()  # TODO expect sys.exit(0)  # line 842
        except:  # line 843
            pass  # line 843
        try:  # line 844
            sos.usage(short=True)  # line 844
            _.fail()  # line 844
        except:  # line 845
            pass  # line 845

    def testOnlyExcept(_):  # line 847
        ''' Test blacklist glob rules. '''  # line 848
        sos.offline(options=["--track"])  # line 849
        _.createFile("a.1")  # line 850
        _.createFile("a.2")  # line 851
        _.createFile("b.1")  # line 852
        _.createFile("b.2")  # line 853
        sos.add(".", "./a.?")  # line 854
        sos.add(".", "./?.1", negative=True)  # line 855
        out = wrapChannels(lambda: sos.commit())  # line 856
        _.assertIn("ADD ./a.2", out)  # line 857
        _.assertNotIn("ADD ./a.1", out)  # line 858
        _.assertNotIn("ADD ./b.1", out)  # line 859
        _.assertNotIn("ADD ./b.2", out)  # line 860

    def testOnly(_):  # line 862
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 863
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 864
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 865
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 866
        sos.offline(options=["--track", "--strict"])  # line 867
        _.createFile(1)  # line 868
        _.createFile(2)  # line 869
        sos.add(".", "./file1")  # line 870
        sos.add(".", "./file2")  # line 871
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 872
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta and file1  # line 873
        sos.commit()  # adds also file2  # line 874
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta and file1  # line 875
        _.createFile(1, "cc")  # modify both files  # line 876
        _.createFile(2, "dd")  # line 877
        try:  # line 878
            sos.config(["set", "texttype", "file2"])  # line 878
        except SystemExit as E:  # line 879
            _.assertEqual(0, E.code)  # line 879
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))  # line 880
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 881
        _.assertTrue("./file2" in changes.modifications)  # line 882
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 883
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 884

    def testDiff(_):  # line 886
        try:  # manually mark this file as "textual"  # line 887
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 887
        except SystemExit as E:  # line 888
            _.assertEqual(0, E.code)  # line 888
        sos.offline(options=["--strict"])  # line 889
        _.createFile(1)  # line 890
        _.createFile(2)  # line 891
        sos.commit()  # line 892
        _.createFile(1, "sdfsdgfsdf")  # line 893
        _.createFile(2, "12343")  # line 894
        sos.commit()  # line 895
        _.createFile(1, "foobar")  # line 896
        _.createFile(3)  # line 897
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 898
        _.assertIn("ADD ./file3", out)  # line 899
        _.assertAllIn(["MOD ./file2", "DIF ./file1  <No newline>", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 900
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 901

    def testReorderRenameActions(_):  # line 903
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 904
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 905
        try:  # line 906
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 906
            _.fail()  # line 906
        except:  # line 907
            pass  # line 907

    def testMove(_):  # line 909
        sos.offline(options=["--strict", "--track"])  # line 910
        _.createFile(1)  # line 911
        sos.add(".", "./file?")  # line 912
# test source folder missing
        try:  # line 914
            sos.move("sub", "sub/file?", ".", "?file")  # line 914
            _.fail()  # line 914
        except:  # line 915
            pass  # line 915
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 917
        _.assertTrue(os.path.exists("sub"))  # line 918
        _.assertTrue(os.path.exists("sub/file1"))  # line 919
        _.assertFalse(os.path.exists("file1"))  # line 920
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 922
        _.assertTrue(os.path.exists("1file"))  # line 923
        _.assertFalse(os.path.exists("sub/file1"))  # line 924
# test nothing matches source pattern
        try:  # line 926
            sos.move(".", "a*", ".", "b*")  # line 926
            _.fail()  # line 926
        except:  # line 927
            pass  # line 927
        sos.add(".", "*")  # anything pattern  # line 928
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 929
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 929
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 929
        except:  # line 930
            pass  # line 930
# test rename no conflict
        _.createFile(1)  # line 932
        _.createFile(2)  # line 933
        _.createFile(3)  # line 934
        sos.add(".", "./file*")  # line 935
        try:  # define an ignore pattern  # line 936
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 936
        except SystemExit as E:  # line 937
            _.assertEqual(0, E.code)  # line 937
        try:  # line 938
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 938
        except SystemExit as E:  # line 939
            _.assertEqual(0, E.code)  # line 939
        sos.move(".", "./file*", ".", "fi*le")  # line 940
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 941
        _.assertFalse(os.path.exists("fi4le"))  # line 942
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 944
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 948
        sos.add(".", "./?a?b", ["--force"])  # line 949
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 950
        _.createFile("1a2b")  # should not be tracked  # line 951
        _.createFile("a1b2")  # should be tracked  # line 952
        sos.commit()  # line 953
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 954
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 955
        _.createFile("1a1b1")  # line 956
        _.createFile("1a1b2")  # line 957
        sos.add(".", "?a?b*")  # line 958
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 959
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 963
        sos.offline()  # line 964
        _.createFile(1)  # line 965
        os.mkdir(sos.revisionFolder(0, 1))  # line 966
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.revisionFolder(0, 1))  # line 967
        _.createFile(1)  # line 968
        try:  # should exit with error due to collision detection  # line 969
            sos.commit()  # should exit with error due to collision detection  # line 969
            _.fail()  # should exit with error due to collision detection  # line 969
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 970
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 970

    def testFindBase(_):  # line 972
        old = os.getcwd()  # line 973
        try:  # line 974
            os.mkdir("." + os.sep + ".git")  # line 975
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 976
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 977
            os.chdir("a" + os.sep + "b")  # line 978
            s, vcs, cmd = sos.findSosVcsBase()  # line 979
            _.assertIsNotNone(s)  # line 980
            _.assertIsNotNone(vcs)  # line 981
            _.assertEqual("git", cmd)  # line 982
        finally:  # line 983
            os.chdir(old)  # line 983

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail

# TODO test +++ --- in diff
# TODO test +01/-02/*..
# TODO tests for loadcommit redirection
# TODO test wrong branch/revision after fast branching, would raise exception for -1 otherwise

if __name__ == '__main__':  # line 993
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 994
    c = configr.Configr("sos")  # line 995
    c.loadSettings()  # line 996
    if len(c.keys()) > 0:  # line 997
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 997
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 998
