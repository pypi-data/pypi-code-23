#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x7d5d22f9

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
    if sys.version_info[:2] >= (3, 3):  # line 17
        os.sync()  # line 17


def determineFilesystemTimeResolution() -> 'float':  # line 20
    name = str(uuid.uuid4())  # type: str  # line 21
    with open(name, "w") as fd:  # create temporary file  # line 22
        fd.write("x")  # create temporary file  # line 22
    mt = os.stat(name).st_mtime  # type: float  # get current timestamp  # line 23
    while os.stat(name).st_mtime == mt:  # wait until timestamp modified  # line 24
        time.sleep(0.05)  # to avoid 0.00s bugs (came up some time for unknown reasons)  # line 25
        with open(name, "w") as fd:  # line 26
            fd.write("x")  # line 26
    mt, start, _count = os.stat(name).st_mtime, time.time(), 0  # line 27
    while os.stat(name).st_mtime == mt:  # now cound and measure time until modified again  # line 28
        time.sleep(0.05)  # line 29
        _count += 1  # line 30
        with open(name, "w") as fd:  # line 31
            fd.write("x")  # line 31
    os.unlink(name)  # line 32
    fsprecision = round(time.time() - start, 2)  # type: float  # line 33
    print("File system timestamp precision is %.2fs; wrote to the file %d times during that time" % (fsprecision, _count))  # line 34
    return fsprecision  # line 35


FS_PRECISION = determineFilesystemTimeResolution() * 1.05  # line 38


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
def wrapChannels(func: '_coconut.typing.Callable[..., Any]'):  # line 56
    ''' Wrap function call to capture and return strings emitted on stdout and stderr. '''  # line 57
    oldv = sys.argv  # line 58
    buf = TextIOWrapper(BufferedRandom(BytesIO(b"")), encoding=sos.UTF8)  # line 59
    sys.stdout = sys.stderr = buf  # line 60
    handler = logging.StreamHandler(buf)  # line 61
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

    def testPatternPaths(_):  # line 161
        sos.offline(options=["--track"])  # line 162
        os.mkdir("sub")  # line 163
        _.createFile("sub" + os.sep + "file1", "sdfsdf")  # line 164
        sos.add("sub", "sub/file?")  # line 165
        sos.commit("test")  # should pick up sub/file1 pattern  # line 166
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # sub/file1 was added  # line 167
        _.createFile(1)  # line 168
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 169
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 169
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 169
        except:  # line 170
            pass  # line 170

    def testNoArgs(_):  # line 172
        pass  # call "sos" without arguments should simply show help or info about missing arguments  # line 173

    def testAutoUpgrade(_):  # line 175
        sos.offline()  # line 176
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "r", encoding=sos.UTF8) as fd:  # line 177
            repo, branches, config = json.load(fd)  # line 177
        repo["version"] = "0"  # lower than any pip version  # line 178
        branches[:] = [branch[:5] for branch in branches]  # simulate some older state  # line 179
        del repo["format"]  # simulate pre-1.3.5  # line 180
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "w", encoding=sos.UTF8) as fd:  # line 181
            json.dump((repo, branches, config), fd, ensure_ascii=False)  # line 181
        out = wrapChannels(lambda: sos.status(options=["--repo"]))  # line 182
        _.assertAllIn(["Upgraded repository metadata to match SOS version '2018.1210.3028'", "Upgraded repository metadata to match SOS version '1.3.5'"], out)  # line 183

    def testFastBranching(_):  # line 185
        _.createFile(1)  # line 186
        sos.offline(options=["--strict"])  # b0/r0 = ./file1  # line 187
        _.createFile(2)  # line 188
        os.unlink("file1")  # line 189
        sos.commit()  # b0/r1 = ./file2  # line 190
        sos.branch(options=["--fast", "--last"])  # branch b1 from b0/1 TODO modify once --fast becomes the new normal  # line 191
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0", "b1"], os.listdir(sos.metaFolder), only=True)  # line 192
        _.createFile(3)  # line 193
        sos.commit()  # b1/r2 = ./file2, ./file3  # line 194
        _.assertAllIn([sos.metaFile, "r2"], os.listdir(sos.branchFolder(1)), only=True)  # line 195
        sos.branch(options=["--fast", "--last"])  # branch b2 from b1/2  # line 196
        sos.destroy("0")  # remove parent of b1 and transitive parent of b2  # line 197
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1", "b2"], os.listdir(sos.metaFolder), only=True)  # branch 0 was removed  # line 198
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(1)), only=True)  # revisions were copied to branch 1  # line 199
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(2)), only=True)  # revisions were copied to branch 1  # line 200
# TODO test also other functions like status --repo, log

    def testGetParentBranch(_):  # line 203
        m = sos.Accessor({"branches": {0: sos.Accessor({"parent": None, "revision": None}), 1: sos.Accessor({"parent": 0, "revision": 1})}})  # line 204
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 0))  # line 205
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 1))  # line 206
        _.assertEqual(1, sos.Metadata.getParentBranch(m, 1, 2))  # line 207
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 0, 10))  # line 208

    def testTokenizeGlobPattern(_):  # line 210
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 211
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 212
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 213
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 214
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 215
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 216

    def testTokenizeGlobPatterns(_):  # line 218
        try:  # because number of literal strings differs  # line 219
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 219
            _.fail()  # because number of literal strings differs  # line 219
        except:  # line 220
            pass  # line 220
        try:  # because glob patterns differ  # line 221
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 221
            _.fail()  # because glob patterns differ  # line 221
        except:  # line 222
            pass  # line 222
        try:  # glob patterns differ, regardless of position  # line 223
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 223
            _.fail()  # glob patterns differ, regardless of position  # line 223
        except:  # line 224
            pass  # line 224
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 225
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 226
        try:  # succeeds, because glob patterns match (differ only in position)  # line 227
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 227
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 227
        except:  # line 228
            pass  # line 228

    def testConvertGlobFiles(_):  # line 230
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 231
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 232

    def testFolderRemove(_):  # line 234
        m = sos.Metadata(os.getcwd())  # line 235
        _.createFile(1)  # line 236
        _.createFile("a", prefix="sub")  # line 237
        sos.offline()  # line 238
        _.createFile(2)  # line 239
        os.unlink("sub" + os.sep + "a")  # line 240
        os.rmdir("sub")  # line 241
        changes = sos.changes()  # TODO replace by output check  # line 242
        _.assertEqual(1, len(changes.additions))  # line 243
        _.assertEqual(0, len(changes.modifications))  # line 244
        _.assertEqual(1, len(changes.deletions))  # line 245
        _.createFile("a", prefix="sub")  # line 246
        changes = sos.changes()  # line 247
        _.assertEqual(0, len(changes.deletions))  # line 248

    def testSwitchConflict(_):  # line 250
        sos.offline(options=["--strict"])  # (r0)  # line 251
        _.createFile(1)  # line 252
        sos.commit()  # add file (r1)  # line 253
        os.unlink("file1")  # line 254
        sos.commit()  # remove (r2)  # line 255
        _.createFile(1, "something else")  # line 256
        sos.commit()  # (r3)  # line 257
        sos.switch("/1")  # updates file1 - marked as MOD, because mtime was changed  # line 258
        _.existsFile(1, "x" * 10)  # line 259
        sos.switch("/2", ["--force"])  # remove file1 requires --force, because size/content (or mtime in non-strict mode) is different to head of branch  # line 260
        sos.switch("/0")  # do nothing, as file1 is already removed  # line 261
        sos.switch("/1")  # add file1 back  # line 262
        sos.switch("/", ["--force"])  # requires force because changed vs. head of branch  # line 263
        _.existsFile(1, "something else")  # line 264

    def testComputeSequentialPathSet(_):  # line 266
        os.makedirs(sos.revisionFolder(0, 0))  # line 267
        os.makedirs(sos.revisionFolder(0, 1))  # line 268
        os.makedirs(sos.revisionFolder(0, 2))  # line 269
        os.makedirs(sos.revisionFolder(0, 3))  # line 270
        os.makedirs(sos.revisionFolder(0, 4))  # line 271
        m = sos.Metadata(os.getcwd())  # line 272
        m.branch = 0  # line 273
        m.commit = 2  # line 274
        m.saveBranches()  # line 275
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 276
        m.saveCommit(0, 0)  # initial  # line 277
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 278
        m.saveCommit(0, 1)  # mod  # line 279
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 280
        m.saveCommit(0, 2)  # add  # line 281
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 282
        m.saveCommit(0, 3)  # del  # line 283
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")  # line 284
        m.saveCommit(0, 4)  # readd  # line 285
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 286
        m.saveBranch(0)  # line 287
        m.branches = {0: sos.BranchInfo(0, 0), 1: sos.BranchInfo(1, 0)}  # line 288
        m.saveBranches()  # line 289
        m.computeSequentialPathSet(0, 4)  # line 290
        _.assertEqual(2, len(m.paths))  # line 291

    def testParseRevisionString(_):  # line 293
        m = sos.Metadata(os.getcwd())  # line 294
        m.branch = 1  # line 295
        m.commits = {0: 0, 1: 1, 2: 2}  # line 296
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 297
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 298
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 299
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 300
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 301
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 302
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 303

    def testOfflineEmpty(_):  # line 305
        os.mkdir("." + os.sep + sos.metaFolder)  # line 306
        try:  # line 307
            sos.offline("trunk")  # line 307
            _.fail()  # line 307
        except SystemExit as E:  # line 308
            _.assertEqual(1, E.code)  # line 308
        os.rmdir("." + os.sep + sos.metaFolder)  # line 309
        sos.offline("test")  # line 310
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 311
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 312
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 313
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 314
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 315
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file  # line 316

    def testOfflineWithFiles(_):  # line 318
        _.createFile(1, "x" * 100)  # line 319
        _.createFile(2)  # line 320
        sos.offline("test")  # line 321
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 322
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 323
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 324
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 325
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 326
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 327
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file plus branch base file copies  # line 328

    def testBranch(_):  # line 330
        _.createFile(1, "x" * 100)  # line 331
        _.createFile(2)  # line 332
        sos.offline("test")  # b0/r0  # line 333
        sos.branch("other")  # b1/r0  # line 334
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 335
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 336
        _.assertEqual(list(sorted(os.listdir(sos.revisionFolder(0, 0)))), list(sorted(os.listdir(sos.revisionFolder(1, 0)))))  # line 338
        _.createFile(1, "z")  # modify file  # line 340
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 341
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 342
        _.createFile(3, "z")  # line 344
        sos.branch("from_last_revision", options=["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 345
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 346
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 351
        _.createFile(1, "x" * 100)  # line 352
        _.createFile(2)  # line 353
        sos.offline("test")  # line 354
        changes = sos.changes()  # line 355
        _.assertEqual(0, len(changes.additions))  # line 356
        _.assertEqual(0, len(changes.deletions))  # line 357
        _.assertEqual(0, len(changes.modifications))  # line 358
        _.createFile(1, "z")  # size change  # line 359
        changes = sos.changes()  # line 360
        _.assertEqual(0, len(changes.additions))  # line 361
        _.assertEqual(0, len(changes.deletions))  # line 362
        _.assertEqual(1, len(changes.modifications))  # line 363
        sos.commit("message")  # line 364
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 365
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.revisionFolder(0, 1)))  # line 366
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # no further files, only the modified one  # line 367
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 368
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 369
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 370
        os.unlink("file2")  # line 371
        changes = sos.changes()  # line 372
        _.assertEqual(0, len(changes.additions))  # line 373
        _.assertEqual(1, len(changes.deletions))  # line 374
        _.assertEqual(1, len(changes.modifications))  # line 375
        sos.commit("modified")  # line 376
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # no additional files, only mentions in metadata  # line 377
        try:  # expecting Exit due to no changes  # line 378
            sos.commit("nothing")  # expecting Exit due to no changes  # line 378
            _.fail()  # expecting Exit due to no changes  # line 378
        except:  # line 379
            pass  # line 379

    def testGetBranch(_):  # line 381
        m = sos.Metadata(os.getcwd())  # line 382
        m.branch = 1  # current branch  # line 383
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 384
        _.assertEqual(27, m.getBranchByName(27))  # line 385
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 386
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 387
        _.assertIsNone(m.getBranchByName("unknown"))  # line 388
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 389
        _.assertEqual(13, m.getRevisionByName("13"))  # line 390
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 391
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 392

    def testTagging(_):  # line 394
        m = sos.Metadata(os.getcwd())  # line 395
        sos.offline()  # line 396
        _.createFile(111)  # line 397
        sos.commit("tag", ["--tag"])  # line 398
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 399
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 400
        _.createFile(2)  # line 401
        try:  # line 402
            sos.commit("tag")  # line 402
            _.fail()  # line 402
        except:  # line 403
            pass  # line 403
        sos.commit("tag-2", ["--tag"])  # line 404
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 405
        _.assertIn("TAG tag", out)  # line 406

    def testSwitch(_):  # line 408
        _.createFile(1, "x" * 100)  # line 409
        _.createFile(2, "y")  # line 410
        sos.offline("test")  # file1-2  in initial branch commit  # line 411
        sos.branch("second")  # file1-2  switch, having same files  # line 412
        sos.switch("0")  # no change  switch back, no problem  # line 413
        sos.switch("second")  # no change  # switch back, no problem  # line 414
        _.createFile(3, "y")  # generate a file  # line 415
        try:  # uncommited changes detected  # line 416
            sos.switch("test")  # uncommited changes detected  # line 416
            _.fail()  # uncommited changes detected  # line 416
        except SystemExit as E:  # line 417
            _.assertEqual(1, E.code)  # line 417
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 418
        sos.changes()  # line 419
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 420
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 421
        _.createFile("XXX")  # line 422
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 423
        _.assertIn("File tree has changes", out)  # line 424
        _.assertNotIn("File tree is unchanged", out)  # line 425
        _.assertIn("  * b00   'test'", out)  # line 426
        _.assertIn("    b01 'second'", out)  # line 427
        _.assertIn("(dirty)", out)  # one branch has commits  # line 428
        _.assertIn("(in sync)", out)  # the other doesn't  # line 429
        _.createFile(4, "xy")  # generate a file  # line 430
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4  # line 431
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 432
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 433
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 434
        sos.switch("test", ["--force"])  # should restore file1 and remove file3  # line 435
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 436
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 437

    def testAutoDetectVCS(_):  # line 439
        os.mkdir(".git")  # line 440
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 441
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 442
            meta = fd.read()  # line 442
        _.assertTrue("\"master\"" in meta)  # line 443
        os.rmdir(".git")  # line 444

    def testUpdate(_):  # line 446
        sos.offline("trunk")  # create initial branch b0/r0  # line 447
        _.createFile(1, "x" * 100)  # line 448
        sos.commit("second")  # create b0/r1  # line 449

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 451
        _.assertFalse(_.existsFile(1))  # line 452

        sos.update("/1")  # recreate file1  # line 454
        _.assertTrue(_.existsFile(1))  # line 455

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 457
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2)))  # line 458
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2, file=sos.metaFile)))  # line 459
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta data file, no differential files  # line 460

        sos.update("/1")  # do nothing, as nothing has changed  # line 462
        _.assertTrue(_.existsFile(1))  # line 463

        _.createFile(2, "y" * 100)  # line 465
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", options=["--force"])  # automatically including file 2 (as we are in simple mode)  # line 468
        _.assertTrue(_.existsFile(2))  # line 469
        sos.update("trunk", ["--add"])  # only add stuff  # line 470
        _.assertTrue(_.existsFile(2))  # line 471
        sos.update("trunk")  # nothing to do  # line 472
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 473

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 475
        _.createFile(10, theirs)  # line 476
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 477
        _.createFile(11, mine)  # line 478
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 479
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 480

    def testUpdate2(_):  # line 482
        _.createFile("test.txt", "x" * 10)  # line 483
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 484
        sos.branch("mod")  # line 485
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 486
        time.sleep(FS_PRECISION)  # line 487
        sos.commit("mod")  # create b0/r1  # line 488
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 489
        with open("test.txt", "rb") as fd:  # line 490
            _.assertEqual(b"x" * 10, fd.read())  # line 490
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 491
        with open("test.txt", "rb") as fd:  # line 492
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 492
        _.createFile("test.txt", "x" * 10)  # line 493
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 494
        with open("test.txt", "rb") as fd:  # line 495
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 495
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 496
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 497
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 498
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 499
        with open("test.txt", "rb") as fd:  # line 500
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 500

    def testIsTextType(_):  # line 502
        m = sos.Metadata(".")  # line 503
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 504
        m.c.bintype = ["*.md.confluence"]  # line 505
        _.assertTrue(m.isTextType("ab.txt"))  # line 506
        _.assertTrue(m.isTextType("./ab.txt"))  # line 507
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 508
        _.assertFalse(m.isTextType("bc/ab."))  # line 509
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 510
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 511
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 512
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 513

    def testEolDet(_):  # line 515
        ''' Check correct end-of-line detection. '''  # line 516
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 517
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 518
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 519
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 520
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 521
        _.assertIsNone(sos.eoldet(b""))  # line 522
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 523

    def testMerge(_):  # line 525
        ''' Check merge results depending on user options. '''  # line 526
        a = b"a\nb\ncc\nd"  # type: bytes  # line 527
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 528
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge  # line 529
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace  # line 530
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace  # line 531
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge  # line 532
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 533
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 534
        a = b"a\nb\ncc\nd"  # line 535
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 536
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement  # line 537
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # line 538
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 539
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])  # line 541
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 542
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 544
        b = b"a\nc\ne"  # line 545
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 546
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 547
        a = b"a\nb\ne"  # intra-line merge  # line 548
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 549
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 550

    def testMergeEol(_):  # line 552
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])  # line 553
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 554
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF  # line 555
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])  # line 556
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])  # line 557

    def testPickyMode(_):  # line 559
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 560
        sos.offline("trunk", None, ["--picky"])  # line 561
        changes = sos.changes()  # line 562
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 563
        sos.add(".", "./file?", ["--force"])  # line 564
        _.createFile(1, "aa")  # line 565
        sos.commit("First")  # add one file  # line 566
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 567
        _.createFile(2, "b")  # line 568
        try:  # add nothing, because picky  # line 569
            sos.commit("Second")  # add nothing, because picky  # line 569
        except:  # line 570
            pass  # line 570
        sos.add(".", "./file?")  # line 571
        sos.commit("Third")  # line 572
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # line 573
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 574
        _.assertIn("  * r2", out)  # line 575
        _.createFile(3, prefix="sub")  # line 576
        sos.add("sub", "sub/file?")  # line 577
        changes = sos.changes()  # line 578
        _.assertEqual(1, len(changes.additions))  # line 579
        _.assertTrue("sub/file3" in changes.additions)  # line 580

    def testTrackedSubfolder(_):  # line 582
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 583
        os.mkdir("." + os.sep + "sub")  # line 584
        sos.offline("trunk", None, ["--track"])  # line 585
        _.createFile(1, "x")  # line 586
        _.createFile(1, "x", prefix="sub")  # line 587
        sos.add(".", "./file?")  # add glob pattern to track  # line 588
        sos.commit("First")  # line 589
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 590
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 591
        sos.commit("Second")  # one new file + meta  # line 592
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 593
        os.unlink("file1")  # remove from basefolder  # line 594
        _.createFile(2, "y")  # line 595
        sos.remove(".", "sub/file?")  # line 596
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 597
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 597
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 597
        except:  # line 598
            pass  # line 598
        sos.commit("Third")  # line 599
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta  # line 600
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 603
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 608
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 609
        _.createFile(1)  # line 610
        _.createFile("a123a")  # untracked file "a123a"  # line 611
        sos.add(".", "./file?")  # add glob tracking pattern  # line 612
        sos.commit("second")  # versions "file1"  # line 613
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 614
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 615
        _.assertIn("  | ./file?", out)  # line 616

        _.createFile(2)  # untracked file "file2"  # line 618
        sos.commit("third")  # versions "file2"  # line 619
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta file  # line 620

        os.mkdir("." + os.sep + "sub")  # line 622
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 623
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 624
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 3))))  # meta file only, no other tracked path/file  # line 625

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 627
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 628
        sos.add(".", "./a*a")  # add tracking pattern  # line 629
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 630
        _.assertEqual(0, len(changes.modifications))  # line 631
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 632
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 633

        sos.commit("Second_2")  # line 635
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(1, 1))))  # "a123a" + meta file  # line 636
        _.existsFile(1, b"x" * 10)  # line 637
        _.existsFile(2, b"x" * 10)  # line 638

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 640
        _.existsFile(1, b"x" * 10)  # line 641
        _.existsFile("a123a", b"x" * 10)  # line 642

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 644
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 645
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 646

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 648
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 649
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 650
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 651
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 652
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 653
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 654
# TODO test switch --meta

    def testLsTracked(_):  # line 657
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 658
        _.createFile(1)  # line 659
        _.createFile("foo")  # line 660
        sos.add(".", "./file*")  # capture one file  # line 661
        sos.ls()  # line 662
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 663
        _.assertInAny("TRK file1  (file*)", out)  # line 664
        _.assertNotInAny("... file1  (file*)", out)  # line 665
        _.assertInAny("··· foo", out)  # line 666
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 667
        _.assertInAny("TRK file*", out)  # line 668
        _.createFile("a", prefix="sub")  # line 669
        sos.add("sub", "sub/a")  # line 670
        sos.ls("sub")  # line 671
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 672

    def testLineMerge(_):  # line 674
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 675
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 676
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 677
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 678

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 680
        _.createFile(1)  # line 681
        sos.offline("master", options=["--force"])  # line 682
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 683
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 684
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 685
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 686
        _.createFile(2)  # line 687
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 688
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 689
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 690
        _.assertFalse(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 691

    def testLocalConfig(_):  # line 693
        sos.offline("bla", options=[])  # line 694
        try:  # line 695
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 695
        except SystemExit as E:  # line 696
            _.assertEqual(0, E.code)  # line 696
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 697

    def testConfigVariations(_):  # line 699
        def makeRepo():  # line 700
            try:  # line 701
                os.unlink("file1")  # line 701
            except:  # line 702
                pass  # line 702
            sos.offline("master", options=["--force"])  # line 703
            _.createFile(1)  # line 704
            sos.commit("Added file1")  # line 705
        try:  # line 706
            sos.config(["set", "strict", "on"])  # line 706
        except SystemExit as E:  # line 707
            _.assertEqual(0, E.code)  # line 707
        makeRepo()  # line 708
        _.assertTrue(checkRepoFlag("strict", True))  # line 709
        try:  # line 710
            sos.config(["set", "strict", "off"])  # line 710
        except SystemExit as E:  # line 711
            _.assertEqual(0, E.code)  # line 711
        makeRepo()  # line 712
        _.assertTrue(checkRepoFlag("strict", False))  # line 713
        try:  # line 714
            sos.config(["set", "strict", "yes"])  # line 714
        except SystemExit as E:  # line 715
            _.assertEqual(0, E.code)  # line 715
        makeRepo()  # line 716
        _.assertTrue(checkRepoFlag("strict", True))  # line 717
        try:  # line 718
            sos.config(["set", "strict", "no"])  # line 718
        except SystemExit as E:  # line 719
            _.assertEqual(0, E.code)  # line 719
        makeRepo()  # line 720
        _.assertTrue(checkRepoFlag("strict", False))  # line 721
        try:  # line 722
            sos.config(["set", "strict", "1"])  # line 722
        except SystemExit as E:  # line 723
            _.assertEqual(0, E.code)  # line 723
        makeRepo()  # line 724
        _.assertTrue(checkRepoFlag("strict", True))  # line 725
        try:  # line 726
            sos.config(["set", "strict", "0"])  # line 726
        except SystemExit as E:  # line 727
            _.assertEqual(0, E.code)  # line 727
        makeRepo()  # line 728
        _.assertTrue(checkRepoFlag("strict", False))  # line 729
        try:  # line 730
            sos.config(["set", "strict", "true"])  # line 730
        except SystemExit as E:  # line 731
            _.assertEqual(0, E.code)  # line 731
        makeRepo()  # line 732
        _.assertTrue(checkRepoFlag("strict", True))  # line 733
        try:  # line 734
            sos.config(["set", "strict", "false"])  # line 734
        except SystemExit as E:  # line 735
            _.assertEqual(0, E.code)  # line 735
        makeRepo()  # line 736
        _.assertTrue(checkRepoFlag("strict", False))  # line 737
        try:  # line 738
            sos.config(["set", "strict", "enable"])  # line 738
        except SystemExit as E:  # line 739
            _.assertEqual(0, E.code)  # line 739
        makeRepo()  # line 740
        _.assertTrue(checkRepoFlag("strict", True))  # line 741
        try:  # line 742
            sos.config(["set", "strict", "disable"])  # line 742
        except SystemExit as E:  # line 743
            _.assertEqual(0, E.code)  # line 743
        makeRepo()  # line 744
        _.assertTrue(checkRepoFlag("strict", False))  # line 745
        try:  # line 746
            sos.config(["set", "strict", "enabled"])  # line 746
        except SystemExit as E:  # line 747
            _.assertEqual(0, E.code)  # line 747
        makeRepo()  # line 748
        _.assertTrue(checkRepoFlag("strict", True))  # line 749
        try:  # line 750
            sos.config(["set", "strict", "disabled"])  # line 750
        except SystemExit as E:  # line 751
            _.assertEqual(0, E.code)  # line 751
        makeRepo()  # line 752
        _.assertTrue(checkRepoFlag("strict", False))  # line 753
        try:  # line 754
            sos.config(["set", "strict", "nope"])  # line 754
            _.fail()  # line 754
        except SystemExit as E:  # line 755
            _.assertEqual(1, E.code)  # line 755

    def testLsSimple(_):  # line 757
        _.createFile(1)  # line 758
        _.createFile("foo")  # line 759
        _.createFile("ign1")  # line 760
        _.createFile("ign2")  # line 761
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 762
        try:  # define an ignore pattern  # line 763
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 763
        except SystemExit as E:  # line 764
            _.assertEqual(0, E.code)  # line 764
        try:  # additional ignore pattern  # line 765
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 765
        except SystemExit as E:  # line 766
            _.assertEqual(0, E.code)  # line 766
        try:  # define a list of ignore patterns  # line 767
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 767
        except SystemExit as E:  # line 768
            _.assertEqual(0, E.code)  # line 768
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 769
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 770
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 771
        _.assertInAny('··· file1', out)  # line 772
        _.assertInAny('··· ign1', out)  # line 773
        _.assertInAny('··· ign2', out)  # line 774
        try:  # line 775
            sos.config(["rm", "foo", "bar"])  # line 775
            _.fail()  # line 775
        except SystemExit as E:  # line 776
            _.assertEqual(1, E.code)  # line 776
        try:  # line 777
            sos.config(["rm", "ignores", "foo"])  # line 777
            _.fail()  # line 777
        except SystemExit as E:  # line 778
            _.assertEqual(1, E.code)  # line 778
        try:  # line 779
            sos.config(["rm", "ignores", "ign1"])  # line 779
        except SystemExit as E:  # line 780
            _.assertEqual(0, E.code)  # line 780
        try:  # remove ignore pattern  # line 781
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 781
        except SystemExit as E:  # line 782
            _.assertEqual(0, E.code)  # line 782
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 783
        _.assertInAny('··· ign1', out)  # line 784
        _.assertInAny('IGN ign2', out)  # line 785
        _.assertNotInAny('··· ign2', out)  # line 786

    def testWhitelist(_):  # line 788
# TODO test same for simple mode
        _.createFile(1)  # line 790
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 791
        sos.offline("xx", options=["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 792
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 793
        sos.commit(options=["--force"])  # attempt to commit the file  # line 794
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta data, file1 was ignored  # line 795
        try:  # Exit because dirty  # line 796
            sos.online()  # Exit because dirty  # line 796
            _.fail()  # Exit because dirty  # line 796
        except:  # exception expected  # line 797
            pass  # exception expected  # line 797
        _.createFile("x2")  # add another change  # line 798
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 799
        try:  # force beyond dirty flag check  # line 800
            sos.online(["--force"])  # force beyond dirty flag check  # line 800
            _.fail()  # force beyond dirty flag check  # line 800
        except:  # line 801
            pass  # line 801
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 802
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 803

        _.createFile(1)  # line 805
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 806
        sos.offline("xx", None, ["--track"])  # line 807
        sos.add(".", "./file*")  # line 808
        sos.commit()  # should NOT ask for force here  # line 809
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 810

    def testRemove(_):  # line 812
        _.createFile(1, "x" * 100)  # line 813
        sos.offline("trunk")  # line 814
        try:  # line 815
            sos.destroy("trunk")  # line 815
            _fail()  # line 815
        except:  # line 816
            pass  # line 816
        _.createFile(2, "y" * 10)  # line 817
        sos.branch("added")  # creates new branch, writes repo metadata, and therefore creates backup copy  # line 818
        sos.destroy("trunk")  # line 819
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1"], os.listdir("." + os.sep + sos.metaFolder))  # line 820
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 821
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 822
        sos.branch("next")  # line 823
        _.createFile(3, "y" * 10)  # make a change  # line 824
        sos.destroy("added", "--force")  # should succeed  # line 825

    def testUsage(_):  # line 827
        try:  # TODO expect sys.exit(0)  # line 828
            sos.usage()  # TODO expect sys.exit(0)  # line 828
            _.fail()  # TODO expect sys.exit(0)  # line 828
        except:  # line 829
            pass  # line 829
        try:  # line 830
            sos.usage(short=True)  # line 830
            _.fail()  # line 830
        except:  # line 831
            pass  # line 831

    def testOnlyExcept(_):  # line 833
        ''' Test blacklist glob rules. '''  # line 834
        sos.offline(options=["--track"])  # line 835
        _.createFile("a.1")  # line 836
        _.createFile("a.2")  # line 837
        _.createFile("b.1")  # line 838
        _.createFile("b.2")  # line 839
        sos.add(".", "./a.?")  # line 840
        sos.add(".", "./?.1", negative=True)  # line 841
        out = wrapChannels(lambda: sos.commit())  # line 842
        _.assertIn("ADD ./a.2", out)  # line 843
        _.assertNotIn("ADD ./a.1", out)  # line 844
        _.assertNotIn("ADD ./b.1", out)  # line 845
        _.assertNotIn("ADD ./b.2", out)  # line 846

    def testOnly(_):  # line 848
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 849
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 850
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 851
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 852
        sos.offline(options=["--track", "--strict"])  # line 853
        _.createFile(1)  # line 854
        _.createFile(2)  # line 855
        sos.add(".", "./file1")  # line 856
        sos.add(".", "./file2")  # line 857
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 858
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta and file1  # line 859
        sos.commit()  # adds also file2  # line 860
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta and file1  # line 861
        _.createFile(1, "cc")  # modify both files  # line 862
        _.createFile(2, "dd")  # line 863
        try:  # line 864
            sos.config(["set", "texttype", "file2"])  # line 864
        except SystemExit as E:  # line 865
            _.assertEqual(0, E.code)  # line 865
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))  # line 866
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 867
        _.assertTrue("./file2" in changes.modifications)  # line 868
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 869
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 870

    def testDiff(_):  # line 872
        try:  # manually mark this file as "textual"  # line 873
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 873
        except SystemExit as E:  # line 874
            _.assertEqual(0, E.code)  # line 874
        sos.offline(options=["--strict"])  # line 875
        _.createFile(1)  # line 876
        _.createFile(2)  # line 877
        sos.commit()  # line 878
        _.createFile(1, "sdfsdgfsdf")  # line 879
        _.createFile(2, "12343")  # line 880
        sos.commit()  # line 881
        _.createFile(1, "foobar")  # line 882
        _.createFile(3)  # line 883
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 884
        _.assertIn("ADD ./file3", out)  # line 885
        _.assertAllIn(["MOD ./file2", "DIF ./file1  <No newline>", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 886
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 887

    def testReorderRenameActions(_):  # line 889
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 890
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 891
        try:  # line 892
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 892
            _.fail()  # line 892
        except:  # line 893
            pass  # line 893

    def testMove(_):  # line 895
        sos.offline(options=["--strict", "--track"])  # line 896
        _.createFile(1)  # line 897
        sos.add(".", "./file?")  # line 898
# test source folder missing
        try:  # line 900
            sos.move("sub", "sub/file?", ".", "?file")  # line 900
            _.fail()  # line 900
        except:  # line 901
            pass  # line 901
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 903
        _.assertTrue(os.path.exists("sub"))  # line 904
        _.assertTrue(os.path.exists("sub/file1"))  # line 905
        _.assertFalse(os.path.exists("file1"))  # line 906
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 908
        _.assertTrue(os.path.exists("1file"))  # line 909
        _.assertFalse(os.path.exists("sub/file1"))  # line 910
# test nothing matches source pattern
        try:  # line 912
            sos.move(".", "a*", ".", "b*")  # line 912
            _.fail()  # line 912
        except:  # line 913
            pass  # line 913
        sos.add(".", "*")  # anything pattern  # line 914
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 915
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 915
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 915
        except:  # line 916
            pass  # line 916
# test rename no conflict
        _.createFile(1)  # line 918
        _.createFile(2)  # line 919
        _.createFile(3)  # line 920
        sos.add(".", "./file*")  # line 921
        try:  # define an ignore pattern  # line 922
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 922
        except SystemExit as E:  # line 923
            _.assertEqual(0, E.code)  # line 923
        try:  # line 924
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 924
        except SystemExit as E:  # line 925
            _.assertEqual(0, E.code)  # line 925
        sos.move(".", "./file*", ".", "fi*le")  # line 926
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 927
        _.assertFalse(os.path.exists("fi4le"))  # line 928
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 930
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 934
        sos.add(".", "./?a?b", ["--force"])  # line 935
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 936
        _.createFile("1a2b")  # should not be tracked  # line 937
        _.createFile("a1b2")  # should be tracked  # line 938
        sos.commit()  # line 939
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 940
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 941
        _.createFile("1a1b1")  # line 942
        _.createFile("1a1b2")  # line 943
        sos.add(".", "?a?b*")  # line 944
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 945
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 949
        sos.offline()  # line 950
        _.createFile(1)  # line 951
        os.mkdir(sos.revisionFolder(0, 1))  # line 952
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.revisionFolder(0, 1))  # line 953
        _.createFile(1)  # line 954
        try:  # should exit with error due to collision detection  # line 955
            sos.commit()  # should exit with error due to collision detection  # line 955
            _.fail()  # should exit with error due to collision detection  # line 955
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 956
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 956

    def testFindBase(_):  # line 958
        old = os.getcwd()  # line 959
        try:  # line 960
            os.mkdir("." + os.sep + ".git")  # line 961
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 962
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 963
            os.chdir("a" + os.sep + "b")  # line 964
            s, vcs, cmd = sos.findSosVcsBase()  # line 965
            _.assertIsNotNone(s)  # line 966
            _.assertIsNotNone(vcs)  # line 967
            _.assertEqual("git", cmd)  # line 968
        finally:  # line 969
            os.chdir(old)  # line 969

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail

# TODO test +++ --- in diff
# TODO test +01/-02/*..
# TODO tests for loadcommit redirection
# TODO test wrong branch/revision after fast branching, would raise exception for -1 otherwise

if __name__ == '__main__':  # line 979
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 980
    c = configr.Configr("sos")  # line 981
    c.loadSettings()  # line 982
    if len(c.keys()) > 0:  # line 983
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 983
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 984
