#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x25d481c5

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
    fsprecision = max(1., round(time.time() - start, 2))  # type: float  # line 32
    print("File system timestamp precision is %.2fs; wrote to the file %d times during that time" % (fsprecision, _count))  # line 33
    return fsprecision  # line 34


FS_PRECISION = determineFilesystemTimeResolution() * 1.05  # line 37


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
def wrapChannels(func: '_coconut.typing.Callable[..., Any]'):  # line 55
    ''' Wrap function call to capture and return strings emitted on stdout and stderr. '''  # line 56
    oldv = sys.argv  # line 57
    buf = TextIOWrapper(BufferedRandom(BytesIO(b"")), encoding=sos.UTF8)  # line 58
    sys.stdout = sys.stderr = buf  # line 59
    handler = logging.StreamHandler(buf)  # line 60
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
        for entry in os.listdir(testFolder):  # cannot remove testFolder on Windows when using TortoiseSVN as VCS  # line 87
            resource = os.path.join(testFolder, entry)  # line 88
            shutil.rmtree(resource) if os.path.isdir(resource) else os.unlink(resource)  # line 89
        os.chdir(testFolder)  # line 90


    def assertAllIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]', only: 'bool'=False):  # line 93
        for w in what:  # line 94
            _.assertIn(w, where)  # line 94
        if only:  # line 95
            _.assertEqual(len(what), len(where))  # line 95

    def assertAllNotIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]'):  # line 97
        for w in what:  # line 98
            _.assertNotIn(w, where)  # line 98

    def assertInAll(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 100
        for w in where:  # line 101
            _.assertIn(what, w)  # line 101

    def assertInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 103
        _.assertTrue(any((what in w for w in where)))  # line 103

    def assertNotInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 105
        _.assertFalse(any((what in w for w in where)))  # line 105

    def createFile(_, number: 'Union[int, str]', contents: 'str'="x" * 10, prefix: '_coconut.typing.Optional[str]'=None):  # line 107
        if prefix and not os.path.exists(prefix):  # line 108
            os.makedirs(prefix)  # line 108
        with open(("." if prefix is None else prefix) + os.sep + (("file%d" % number) if isinstance(number, int) else number), "wb") as fd:  # line 109
            fd.write(contents if isinstance(contents, bytes) else contents.encode("cp1252"))  # line 109

    def existsFile(_, number: 'Union[int, str]', expectedContents: 'bytes'=None) -> 'bool':  # line 111
        if not os.path.exists(("." + os.sep + "file%d" % number) if isinstance(number, int) else number):  # line 112
            return False  # line 112
        if expectedContents is None:  # line 113
            return True  # line 113
        with open(("." + os.sep + "file%d" % number) if isinstance(number, int) else number, "rb") as fd:  # line 114
            return fd.read() == expectedContents  # line 114

    def testAccessor(_):  # line 116
        a = sos.Accessor({"a": 1})  # line 117
        _.assertEqual((1, 1), (a["a"], a.a))  # line 118

    def testGetAnyOfmap(_):  # line 120
        _.assertEqual(2, sos.getAnyOfMap({"a": 1, "b": 2}, ["x", "b"]))  # line 121
        _.assertIsNone(sos.getAnyOfMap({"a": 1, "b": 2}, []))  # line 122

    def testAjoin(_):  # line 124
        _.assertEqual("a1a2", sos.ajoin("a", ["1", "2"]))  # line 125
        _.assertEqual("* a\n* b", sos.ajoin("* ", ["a", "b"], "\n"))  # line 126

    def testFindChanges(_):  # line 128
        m = sos.Metadata(os.getcwd())  # line 129
        try:  # line 130
            sos.config(["set", "texttype", "*"])  # line 130
        except SystemExit as E:  # line 131
            _.assertEqual(0, E.code)  # line 131
        try:  # will be stripped from leading paths anyway  # line 132
            sos.config(["set", "ignores", "test/*.cfg;D:\\apps\\*.cfg.bak"])  # will be stripped from leading paths anyway  # line 132
        except SystemExit as E:  # line 133
            _.assertEqual(0, E.code)  # line 133
        m = sos.Metadata(os.getcwd())  # reload from file system  # line 134
        for file in [f for f in os.listdir() if f.endswith(".bak")]:  # remove configuration file  # line 135
            os.unlink(file)  # remove configuration file  # line 135
        _.createFile(1, "1")  # line 136
        m.createBranch(0)  # line 137
        _.assertEqual(1, len(m.paths))  # line 138
        time.sleep(FS_PRECISION)  # time required by filesystem time resolution issues  # line 139
        _.createFile(1, "2")  # modify existing file  # line 140
        _.createFile(2, "2")  # add another file  # line 141
        m.loadCommit(0, 0)  # line 142
        changes, msg = m.findChanges()  # detect time skew  # line 143
        _.assertEqual(1, len(changes.additions))  # line 144
        _.assertEqual(0, len(changes.deletions))  # line 145
        _.assertEqual(1, len(changes.modifications))  # line 146
        _.assertEqual(0, len(changes.moves))  # line 147
        m.paths.update(changes.additions)  # line 148
        m.paths.update(changes.modifications)  # line 149
        _.createFile(2, "12")  # modify file again  # line 150
        changes, msg = m.findChanges(0, 1)  # by size, creating new commit  # line 151
        _.assertEqual(0, len(changes.additions))  # line 152
        _.assertEqual(0, len(changes.deletions))  # line 153
        _.assertEqual(1, len(changes.modifications))  # line 154
        _.assertEqual(0, len(changes.moves))  # line 155
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1)))  # line 156
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # line 157
# TODO test moves

    def testPatternPaths(_):  # line 160
        sos.offline(options=["--track"])  # line 161
        os.mkdir("sub")  # line 162
        _.createFile("sub" + os.sep + "file1", "sdfsdf")  # line 163
        sos.add("sub", "sub/file?")  # line 164
        sos.commit("test")  # should pick up sub/file1 pattern  # line 165
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # sub/file1 was added  # line 166
        _.createFile(1)  # line 167
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 168
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 168
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 168
        except:  # line 169
            pass  # line 169

    def testNoArgs(_):  # line 171
        pass  # call "sos" without arguments should simply show help or info about missing arguments  # line 172

    def testAutoUpgrade(_):  # line 174
        sos.offline()  # line 175
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "r", encoding=sos.UTF8) as fd:  # line 176
            repo, branches, config = json.load(fd)  # line 176
        repo["version"] = "0"  # lower than any pip version  # line 177
        branches[:] = [branch[:5] for branch in branches]  # simulate some older state  # line 178
        del repo["format"]  # simulate pre-1.3.5  # line 179
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "w", encoding=sos.UTF8) as fd:  # line 180
            json.dump((repo, branches, config), fd, ensure_ascii=False)  # line 180
        out = wrapChannels(lambda: sos.status(options=["--repo"]))  # line 181
        _.assertAllIn(["Upgraded repository metadata to match SOS version '2018.1210.3028'", "Upgraded repository metadata to match SOS version '1.3.5'"], out)  # line 182

    def testFastBranching(_):  # line 184
        _.createFile(1)  # line 185
        sos.offline(options=["--strict"])  # b0/r0 = ./file1  # line 186
        _.createFile(2)  # line 187
        os.unlink("file1")  # line 188
        sos.commit()  # b0/r1 = ./file2  # line 189
        sos.branch(options=["--fast", "--last"])  # branch b1 from b0/1 TODO modify once --fast becomes the new normal  # line 190
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0", "b1"], os.listdir(sos.metaFolder), only=True)  # line 191
        _.createFile(3)  # line 192
        sos.commit()  # b1/r2 = ./file2, ./file3  # line 193
        _.assertAllIn([sos.metaFile, "r2"], os.listdir(sos.branchFolder(1)), only=True)  # line 194
        sos.branch(options=["--fast", "--last"])  # branch b2 from b1/2  # line 195
        sos.destroy("0")  # remove parent of b1 and transitive parent of b2  # line 196
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1", "b2"], os.listdir(sos.metaFolder), only=True)  # branch 0 was removed  # line 197
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(1)), only=True)  # revisions were copied to branch 1  # line 198
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(2)), only=True)  # revisions were copied to branch 1  # line 199
# TODO test also other functions like status --repo, log

    def testGetParentBranch(_):  # line 202
        m = sos.Accessor({"branches": {0: sos.Accessor({"parent": None, "revision": None}), 1: sos.Accessor({"parent": 0, "revision": 1})}})  # line 203
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 0))  # line 204
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 1))  # line 205
        _.assertEqual(1, sos.Metadata.getParentBranch(m, 1, 2))  # line 206
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 0, 10))  # line 207

    def testTokenizeGlobPattern(_):  # line 209
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 210
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 211
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 212
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 213
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 214
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 215

    def testTokenizeGlobPatterns(_):  # line 217
        try:  # because number of literal strings differs  # line 218
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 218
            _.fail()  # because number of literal strings differs  # line 218
        except:  # line 219
            pass  # line 219
        try:  # because glob patterns differ  # line 220
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 220
            _.fail()  # because glob patterns differ  # line 220
        except:  # line 221
            pass  # line 221
        try:  # glob patterns differ, regardless of position  # line 222
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 222
            _.fail()  # glob patterns differ, regardless of position  # line 222
        except:  # line 223
            pass  # line 223
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 224
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 225
        try:  # succeeds, because glob patterns match (differ only in position)  # line 226
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 226
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 226
        except:  # line 227
            pass  # line 227

    def testConvertGlobFiles(_):  # line 229
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 230
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 231

    def testFolderRemove(_):  # line 233
        m = sos.Metadata(os.getcwd())  # line 234
        _.createFile(1)  # line 235
        _.createFile("a", prefix="sub")  # line 236
        sos.offline()  # line 237
        _.createFile(2)  # line 238
        os.unlink("sub" + os.sep + "a")  # line 239
        os.rmdir("sub")  # line 240
        changes = sos.changes()  # TODO replace by output check  # line 241
        _.assertEqual(1, len(changes.additions))  # line 242
        _.assertEqual(0, len(changes.modifications))  # line 243
        _.assertEqual(1, len(changes.deletions))  # line 244
        _.createFile("a", prefix="sub")  # line 245
        changes = sos.changes()  # line 246
        _.assertEqual(0, len(changes.deletions))  # line 247

    def testSwitchConflict(_):  # line 249
        sos.offline(options=["--strict"])  # (r0)  # line 250
        _.createFile(1)  # line 251
        sos.commit()  # add file (r1)  # line 252
        os.unlink("file1")  # line 253
        sos.commit()  # remove (r2)  # line 254
        _.createFile(1, "something else")  # line 255
        sos.commit()  # (r3)  # line 256
        sos.switch("/1")  # updates file1 - marked as MOD, because mtime was changed  # line 257
        _.existsFile(1, "x" * 10)  # line 258
        sos.switch("/2", ["--force"])  # remove file1 requires --force, because size/content (or mtime in non-strict mode) is different to head of branch  # line 259
        sos.switch("/0")  # do nothing, as file1 is already removed  # line 260
        sos.switch("/1")  # add file1 back  # line 261
        sos.switch("/", ["--force"])  # requires force because changed vs. head of branch  # line 262
        _.existsFile(1, "something else")  # line 263

    def testComputeSequentialPathSet(_):  # line 265
        os.makedirs(sos.revisionFolder(0, 0))  # line 266
        os.makedirs(sos.revisionFolder(0, 1))  # line 267
        os.makedirs(sos.revisionFolder(0, 2))  # line 268
        os.makedirs(sos.revisionFolder(0, 3))  # line 269
        os.makedirs(sos.revisionFolder(0, 4))  # line 270
        m = sos.Metadata(os.getcwd())  # line 271
        m.branch = 0  # line 272
        m.commit = 2  # line 273
        m.saveBranches()  # line 274
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 275
        m.saveCommit(0, 0)  # initial  # line 276
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 277
        m.saveCommit(0, 1)  # mod  # line 278
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 279
        m.saveCommit(0, 2)  # add  # line 280
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 281
        m.saveCommit(0, 3)  # del  # line 282
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")  # line 283
        m.saveCommit(0, 4)  # readd  # line 284
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 285
        m.saveBranch(0)  # line 286
        m.branches = {0: sos.BranchInfo(0, 0), 1: sos.BranchInfo(1, 0)}  # line 287
        m.saveBranches()  # line 288
        m.computeSequentialPathSet(0, 4)  # line 289
        _.assertEqual(2, len(m.paths))  # line 290

    def testParseRevisionString(_):  # line 292
        m = sos.Metadata(os.getcwd())  # line 293
        m.branch = 1  # line 294
        m.commits = {0: 0, 1: 1, 2: 2}  # line 295
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 296
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 297
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 298
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 299
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 300
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 301
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 302

    def testOfflineEmpty(_):  # line 304
        os.mkdir("." + os.sep + sos.metaFolder)  # line 305
        try:  # line 306
            sos.offline("trunk")  # line 306
            _.fail()  # line 306
        except SystemExit as E:  # line 307
            _.assertEqual(1, E.code)  # line 307
        os.rmdir("." + os.sep + sos.metaFolder)  # line 308
        sos.offline("test")  # line 309
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 310
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 311
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 312
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 313
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 314
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file  # line 315

    def testOfflineWithFiles(_):  # line 317
        _.createFile(1, "x" * 100)  # line 318
        _.createFile(2)  # line 319
        sos.offline("test")  # line 320
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 321
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 322
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 323
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 324
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 325
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 326
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file plus branch base file copies  # line 327

    def testBranch(_):  # line 329
        _.createFile(1, "x" * 100)  # line 330
        _.createFile(2)  # line 331
        sos.offline("test")  # b0/r0  # line 332
        sos.branch("other")  # b1/r0  # line 333
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 334
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 335
        _.assertEqual(list(sorted(os.listdir(sos.revisionFolder(0, 0)))), list(sorted(os.listdir(sos.revisionFolder(1, 0)))))  # line 337
        _.createFile(1, "z")  # modify file  # line 339
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 340
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 341
        _.createFile(3, "z")  # line 343
        sos.branch("from_last_revision", options=["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 344
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 345
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 350
        _.createFile(1, "x" * 100)  # line 351
        _.createFile(2)  # line 352
        sos.offline("test")  # line 353
        changes = sos.changes()  # line 354
        _.assertEqual(0, len(changes.additions))  # line 355
        _.assertEqual(0, len(changes.deletions))  # line 356
        _.assertEqual(0, len(changes.modifications))  # line 357
        _.createFile(1, "z")  # size change  # line 358
        changes = sos.changes()  # line 359
        _.assertEqual(0, len(changes.additions))  # line 360
        _.assertEqual(0, len(changes.deletions))  # line 361
        _.assertEqual(1, len(changes.modifications))  # line 362
        sos.commit("message")  # line 363
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 364
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.revisionFolder(0, 1)))  # line 365
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # no further files, only the modified one  # line 366
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 367
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 368
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 369
        os.unlink("file2")  # line 370
        changes = sos.changes()  # line 371
        _.assertEqual(0, len(changes.additions))  # line 372
        _.assertEqual(1, len(changes.deletions))  # line 373
        _.assertEqual(1, len(changes.modifications))  # line 374
        sos.commit("modified")  # line 375
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # no additional files, only mentions in metadata  # line 376
        try:  # expecting Exit due to no changes  # line 377
            sos.commit("nothing")  # expecting Exit due to no changes  # line 377
            _.fail()  # expecting Exit due to no changes  # line 377
        except:  # line 378
            pass  # line 378

    def testGetBranch(_):  # line 380
        m = sos.Metadata(os.getcwd())  # line 381
        m.branch = 1  # current branch  # line 382
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 383
        _.assertEqual(27, m.getBranchByName(27))  # line 384
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 385
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 386
        _.assertIsNone(m.getBranchByName("unknown"))  # line 387
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 388
        _.assertEqual(13, m.getRevisionByName("13"))  # line 389
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 390
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 391

    def testTagging(_):  # line 393
        m = sos.Metadata(os.getcwd())  # line 394
        sos.offline()  # line 395
        _.createFile(111)  # line 396
        sos.commit("tag", ["--tag"])  # line 397
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 398
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 399
        _.createFile(2)  # line 400
        try:  # line 401
            sos.commit("tag")  # line 401
            _.fail()  # line 401
        except:  # line 402
            pass  # line 402
        sos.commit("tag-2", ["--tag"])  # line 403
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 404
        _.assertIn("TAG tag", out)  # line 405

    def testSwitch(_):  # line 407
        _.createFile(1, "x" * 100)  # line 408
        _.createFile(2, "y")  # line 409
        sos.offline("test")  # file1-2  in initial branch commit  # line 410
        sos.branch("second")  # file1-2  switch, having same files  # line 411
        sos.switch("0")  # no change  switch back, no problem  # line 412
        sos.switch("second")  # no change  # switch back, no problem  # line 413
        _.createFile(3, "y")  # generate a file  # line 414
        try:  # uncommited changes detected  # line 415
            sos.switch("test")  # uncommited changes detected  # line 415
            _.fail()  # uncommited changes detected  # line 415
        except SystemExit as E:  # line 416
            _.assertEqual(1, E.code)  # line 416
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 417
        sos.changes()  # line 418
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 419
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 420
        _.createFile("XXX")  # line 421
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 422
        _.assertIn("File tree has changes", out)  # line 423
        _.assertNotIn("File tree is unchanged", out)  # line 424
        _.assertIn("  * b00   'test'", out)  # line 425
        _.assertIn("    b01 'second'", out)  # line 426
        _.assertIn("(dirty)", out)  # one branch has commits  # line 427
        _.assertIn("(in sync)", out)  # the other doesn't  # line 428
        _.createFile(4, "xy")  # generate a file  # line 429
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4  # line 430
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 431
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 432
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 433
        sos.switch("test", ["--force"])  # should restore file1 and remove file3  # line 434
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 435
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 436

    def testAutoDetectVCS(_):  # line 438
        os.mkdir(".git")  # line 439
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 440
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 441
            meta = fd.read()  # line 441
        _.assertTrue("\"master\"" in meta)  # line 442
        os.rmdir(".git")  # line 443

    def testUpdate(_):  # line 445
        sos.offline("trunk")  # create initial branch b0/r0  # line 446
        _.createFile(1, "x" * 100)  # line 447
        sos.commit("second")  # create b0/r1  # line 448

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 450
        _.assertFalse(_.existsFile(1))  # line 451

        sos.update("/1")  # recreate file1  # line 453
        _.assertTrue(_.existsFile(1))  # line 454

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 456
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2)))  # line 457
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2, file=sos.metaFile)))  # line 458
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta data file, no differential files  # line 459

        sos.update("/1")  # do nothing, as nothing has changed  # line 461
        _.assertTrue(_.existsFile(1))  # line 462

        _.createFile(2, "y" * 100)  # line 464
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", options=["--force"])  # automatically including file 2 (as we are in simple mode)  # line 467
        _.assertTrue(_.existsFile(2))  # line 468
        sos.update("trunk", ["--add"])  # only add stuff  # line 469
        _.assertTrue(_.existsFile(2))  # line 470
        sos.update("trunk")  # nothing to do  # line 471
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 472

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 474
        _.createFile(10, theirs)  # line 475
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 476
        _.createFile(11, mine)  # line 477
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 478
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 479

    def testUpdate2(_):  # line 481
        _.createFile("test.txt", "x" * 10)  # line 482
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 483
        sos.branch("mod")  # line 484
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 485
        time.sleep(FS_PRECISION)  # line 486
        sos.commit("mod")  # create b0/r1  # line 487
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 488
        with open("test.txt", "rb") as fd:  # line 489
            _.assertEqual(b"x" * 10, fd.read())  # line 489
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 490
        with open("test.txt", "rb") as fd:  # line 491
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 491
        _.createFile("test.txt", "x" * 10)  # line 492
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 493
        with open("test.txt", "rb") as fd:  # line 494
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 494
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 495
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 496
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 497
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 498
        with open("test.txt", "rb") as fd:  # line 499
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 499

    def testIsTextType(_):  # line 501
        m = sos.Metadata(".")  # line 502
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 503
        m.c.bintype = ["*.md.confluence"]  # line 504
        _.assertTrue(m.isTextType("ab.txt"))  # line 505
        _.assertTrue(m.isTextType("./ab.txt"))  # line 506
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 507
        _.assertFalse(m.isTextType("bc/ab."))  # line 508
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 509
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 510
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 511
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 512

    def testEolDet(_):  # line 514
        ''' Check correct end-of-line detection. '''  # line 515
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 516
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 517
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 518
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 519
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 520
        _.assertIsNone(sos.eoldet(b""))  # line 521
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 522

    def testMerge(_):  # line 524
        ''' Check merge results depending on user options. '''  # line 525
        a = b"a\nb\ncc\nd"  # type: bytes  # line 526
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 527
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge  # line 528
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace  # line 529
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace  # line 530
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge  # line 531
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 532
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 533
        a = b"a\nb\ncc\nd"  # line 534
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 535
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement  # line 536
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # line 537
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 538
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])  # line 540
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 541
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 543
        b = b"a\nc\ne"  # line 544
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 545
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 546
        a = b"a\nb\ne"  # intra-line merge  # line 547
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 548
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 549

    def testMergeEol(_):  # line 551
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])  # line 552
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 553
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF  # line 554
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])  # line 555
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])  # line 556

    def testPickyMode(_):  # line 558
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 559
        sos.offline("trunk", None, ["--picky"])  # line 560
        changes = sos.changes()  # line 561
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 562
        sos.add(".", "./file?", ["--force"])  # line 563
        _.createFile(1, "aa")  # line 564
        sos.commit("First")  # add one file  # line 565
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 566
        _.createFile(2, "b")  # line 567
        try:  # add nothing, because picky  # line 568
            sos.commit("Second")  # add nothing, because picky  # line 568
        except:  # line 569
            pass  # line 569
        sos.add(".", "./file?")  # line 570
        sos.commit("Third")  # line 571
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # line 572
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 573
        _.assertIn("  * r2", out)  # line 574
        _.createFile(3, prefix="sub")  # line 575
        sos.add("sub", "sub/file?")  # line 576
        changes = sos.changes()  # line 577
        _.assertEqual(1, len(changes.additions))  # line 578
        _.assertTrue("sub/file3" in changes.additions)  # line 579

    def testTrackedSubfolder(_):  # line 581
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 582
        os.mkdir("." + os.sep + "sub")  # line 583
        sos.offline("trunk", None, ["--track"])  # line 584
        _.createFile(1, "x")  # line 585
        _.createFile(1, "x", prefix="sub")  # line 586
        sos.add(".", "./file?")  # add glob pattern to track  # line 587
        sos.commit("First")  # line 588
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 589
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 590
        sos.commit("Second")  # one new file + meta  # line 591
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 592
        os.unlink("file1")  # remove from basefolder  # line 593
        _.createFile(2, "y")  # line 594
        sos.remove(".", "sub/file?")  # line 595
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 596
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 596
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 596
        except:  # line 597
            pass  # line 597
        sos.commit("Third")  # line 598
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta  # line 599
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 602
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 607
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 608
        _.createFile(1)  # line 609
        _.createFile("a123a")  # untracked file "a123a"  # line 610
        sos.add(".", "./file?")  # add glob tracking pattern  # line 611
        sos.commit("second")  # versions "file1"  # line 612
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 613
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 614
        _.assertIn("  | ./file?", out)  # line 615

        _.createFile(2)  # untracked file "file2"  # line 617
        sos.commit("third")  # versions "file2"  # line 618
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta file  # line 619

        os.mkdir("." + os.sep + "sub")  # line 621
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 622
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 623
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 3))))  # meta file only, no other tracked path/file  # line 624

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 626
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 627
        sos.add(".", "./a*a")  # add tracking pattern  # line 628
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 629
        _.assertEqual(0, len(changes.modifications))  # line 630
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 631
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 632

        sos.commit("Second_2")  # line 634
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(1, 1))))  # "a123a" + meta file  # line 635
        _.existsFile(1, b"x" * 10)  # line 636
        _.existsFile(2, b"x" * 10)  # line 637

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 639
        _.existsFile(1, b"x" * 10)  # line 640
        _.existsFile("a123a", b"x" * 10)  # line 641

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 643
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 644
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 645

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 647
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 648
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 649
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 650
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 651
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 652
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 653
# TODO test switch --meta

    def testLsTracked(_):  # line 656
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 657
        _.createFile(1)  # line 658
        _.createFile("foo")  # line 659
        sos.add(".", "./file*")  # capture one file  # line 660
        sos.ls()  # line 661
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 662
        _.assertInAny("TRK file1  (file*)", out)  # line 663
        _.assertNotInAny("... file1  (file*)", out)  # line 664
        _.assertInAny("··· foo", out)  # line 665
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 666
        _.assertInAny("TRK file*", out)  # line 667
        _.createFile("a", prefix="sub")  # line 668
        sos.add("sub", "sub/a")  # line 669
        sos.ls("sub")  # line 670
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 671

    def testLineMerge(_):  # line 673
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 674
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 675
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 676
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 677

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 679
        _.createFile(1)  # line 680
        sos.offline("master", options=["--force"])  # line 681
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 682
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 683
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 684
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 685
        _.createFile(2)  # line 686
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 687
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 688
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 689
        _.assertFalse(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 690

    def testLocalConfig(_):  # line 692
        sos.offline("bla", options=[])  # line 693
        try:  # line 694
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 694
        except SystemExit as E:  # line 695
            _.assertEqual(0, E.code)  # line 695
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 696

    def testConfigVariations(_):  # line 698
        def makeRepo():  # line 699
            try:  # line 700
                os.unlink("file1")  # line 700
            except:  # line 701
                pass  # line 701
            sos.offline("master", options=["--force"])  # line 702
            _.createFile(1)  # line 703
            sos.commit("Added file1")  # line 704
        try:  # line 705
            sos.config(["set", "strict", "on"])  # line 705
        except SystemExit as E:  # line 706
            _.assertEqual(0, E.code)  # line 706
        makeRepo()  # line 707
        _.assertTrue(checkRepoFlag("strict", True))  # line 708
        try:  # line 709
            sos.config(["set", "strict", "off"])  # line 709
        except SystemExit as E:  # line 710
            _.assertEqual(0, E.code)  # line 710
        makeRepo()  # line 711
        _.assertTrue(checkRepoFlag("strict", False))  # line 712
        try:  # line 713
            sos.config(["set", "strict", "yes"])  # line 713
        except SystemExit as E:  # line 714
            _.assertEqual(0, E.code)  # line 714
        makeRepo()  # line 715
        _.assertTrue(checkRepoFlag("strict", True))  # line 716
        try:  # line 717
            sos.config(["set", "strict", "no"])  # line 717
        except SystemExit as E:  # line 718
            _.assertEqual(0, E.code)  # line 718
        makeRepo()  # line 719
        _.assertTrue(checkRepoFlag("strict", False))  # line 720
        try:  # line 721
            sos.config(["set", "strict", "1"])  # line 721
        except SystemExit as E:  # line 722
            _.assertEqual(0, E.code)  # line 722
        makeRepo()  # line 723
        _.assertTrue(checkRepoFlag("strict", True))  # line 724
        try:  # line 725
            sos.config(["set", "strict", "0"])  # line 725
        except SystemExit as E:  # line 726
            _.assertEqual(0, E.code)  # line 726
        makeRepo()  # line 727
        _.assertTrue(checkRepoFlag("strict", False))  # line 728
        try:  # line 729
            sos.config(["set", "strict", "true"])  # line 729
        except SystemExit as E:  # line 730
            _.assertEqual(0, E.code)  # line 730
        makeRepo()  # line 731
        _.assertTrue(checkRepoFlag("strict", True))  # line 732
        try:  # line 733
            sos.config(["set", "strict", "false"])  # line 733
        except SystemExit as E:  # line 734
            _.assertEqual(0, E.code)  # line 734
        makeRepo()  # line 735
        _.assertTrue(checkRepoFlag("strict", False))  # line 736
        try:  # line 737
            sos.config(["set", "strict", "enable"])  # line 737
        except SystemExit as E:  # line 738
            _.assertEqual(0, E.code)  # line 738
        makeRepo()  # line 739
        _.assertTrue(checkRepoFlag("strict", True))  # line 740
        try:  # line 741
            sos.config(["set", "strict", "disable"])  # line 741
        except SystemExit as E:  # line 742
            _.assertEqual(0, E.code)  # line 742
        makeRepo()  # line 743
        _.assertTrue(checkRepoFlag("strict", False))  # line 744
        try:  # line 745
            sos.config(["set", "strict", "enabled"])  # line 745
        except SystemExit as E:  # line 746
            _.assertEqual(0, E.code)  # line 746
        makeRepo()  # line 747
        _.assertTrue(checkRepoFlag("strict", True))  # line 748
        try:  # line 749
            sos.config(["set", "strict", "disabled"])  # line 749
        except SystemExit as E:  # line 750
            _.assertEqual(0, E.code)  # line 750
        makeRepo()  # line 751
        _.assertTrue(checkRepoFlag("strict", False))  # line 752
        try:  # line 753
            sos.config(["set", "strict", "nope"])  # line 753
            _.fail()  # line 753
        except SystemExit as E:  # line 754
            _.assertEqual(1, E.code)  # line 754

    def testLsSimple(_):  # line 756
        _.createFile(1)  # line 757
        _.createFile("foo")  # line 758
        _.createFile("ign1")  # line 759
        _.createFile("ign2")  # line 760
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 761
        try:  # define an ignore pattern  # line 762
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 762
        except SystemExit as E:  # line 763
            _.assertEqual(0, E.code)  # line 763
        try:  # additional ignore pattern  # line 764
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 764
        except SystemExit as E:  # line 765
            _.assertEqual(0, E.code)  # line 765
        try:  # define a list of ignore patterns  # line 766
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 766
        except SystemExit as E:  # line 767
            _.assertEqual(0, E.code)  # line 767
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 768
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 769
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 770
        _.assertInAny('··· file1', out)  # line 771
        _.assertInAny('··· ign1', out)  # line 772
        _.assertInAny('··· ign2', out)  # line 773
        try:  # line 774
            sos.config(["rm", "foo", "bar"])  # line 774
            _.fail()  # line 774
        except SystemExit as E:  # line 775
            _.assertEqual(1, E.code)  # line 775
        try:  # line 776
            sos.config(["rm", "ignores", "foo"])  # line 776
            _.fail()  # line 776
        except SystemExit as E:  # line 777
            _.assertEqual(1, E.code)  # line 777
        try:  # line 778
            sos.config(["rm", "ignores", "ign1"])  # line 778
        except SystemExit as E:  # line 779
            _.assertEqual(0, E.code)  # line 779
        try:  # remove ignore pattern  # line 780
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 780
        except SystemExit as E:  # line 781
            _.assertEqual(0, E.code)  # line 781
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 782
        _.assertInAny('··· ign1', out)  # line 783
        _.assertInAny('IGN ign2', out)  # line 784
        _.assertNotInAny('··· ign2', out)  # line 785

    def testWhitelist(_):  # line 787
# TODO test same for simple mode
        _.createFile(1)  # line 789
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 790
        sos.offline("xx", options=["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 791
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 792
        sos.commit(options=["--force"])  # attempt to commit the file  # line 793
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta data, file1 was ignored  # line 794
        try:  # Exit because dirty  # line 795
            sos.online()  # Exit because dirty  # line 795
            _.fail()  # Exit because dirty  # line 795
        except:  # exception expected  # line 796
            pass  # exception expected  # line 796
        _.createFile("x2")  # add another change  # line 797
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 798
        try:  # force beyond dirty flag check  # line 799
            sos.online(["--force"])  # force beyond dirty flag check  # line 799
            _.fail()  # force beyond dirty flag check  # line 799
        except:  # line 800
            pass  # line 800
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 801
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 802

        _.createFile(1)  # line 804
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 805
        sos.offline("xx", None, ["--track"])  # line 806
        sos.add(".", "./file*")  # line 807
        sos.commit()  # should NOT ask for force here  # line 808
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 809

    def testRemove(_):  # line 811
        _.createFile(1, "x" * 100)  # line 812
        sos.offline("trunk")  # line 813
        try:  # line 814
            sos.destroy("trunk")  # line 814
            _fail()  # line 814
        except:  # line 815
            pass  # line 815
        _.createFile(2, "y" * 10)  # line 816
        sos.branch("added")  # creates new branch, writes repo metadata, and therefore creates backup copy  # line 817
        sos.destroy("trunk")  # line 818
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1"], os.listdir("." + os.sep + sos.metaFolder))  # line 819
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 820
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 821
        sos.branch("next")  # line 822
        _.createFile(3, "y" * 10)  # make a change  # line 823
        sos.destroy("added", "--force")  # should succeed  # line 824

    def testUsage(_):  # line 826
        try:  # TODO expect sys.exit(0)  # line 827
            sos.usage()  # TODO expect sys.exit(0)  # line 827
            _.fail()  # TODO expect sys.exit(0)  # line 827
        except:  # line 828
            pass  # line 828
        try:  # line 829
            sos.usage(short=True)  # line 829
            _.fail()  # line 829
        except:  # line 830
            pass  # line 830

    def testOnlyExcept(_):  # line 832
        ''' Test blacklist glob rules. '''  # line 833
        sos.offline(options=["--track"])  # line 834
        _.createFile("a.1")  # line 835
        _.createFile("a.2")  # line 836
        _.createFile("b.1")  # line 837
        _.createFile("b.2")  # line 838
        sos.add(".", "./a.?")  # line 839
        sos.add(".", "./?.1", negative=True)  # line 840
        out = wrapChannels(lambda: sos.commit())  # line 841
        _.assertIn("ADD ./a.2", out)  # line 842
        _.assertNotIn("ADD ./a.1", out)  # line 843
        _.assertNotIn("ADD ./b.1", out)  # line 844
        _.assertNotIn("ADD ./b.2", out)  # line 845

    def testOnly(_):  # line 847
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 848
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 849
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 850
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 851
        sos.offline(options=["--track", "--strict"])  # line 852
        _.createFile(1)  # line 853
        _.createFile(2)  # line 854
        sos.add(".", "./file1")  # line 855
        sos.add(".", "./file2")  # line 856
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 857
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta and file1  # line 858
        sos.commit()  # adds also file2  # line 859
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta and file1  # line 860
        _.createFile(1, "cc")  # modify both files  # line 861
        _.createFile(2, "dd")  # line 862
        try:  # line 863
            sos.config(["set", "texttype", "file2"])  # line 863
        except SystemExit as E:  # line 864
            _.assertEqual(0, E.code)  # line 864
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))  # line 865
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 866
        _.assertTrue("./file2" in changes.modifications)  # line 867
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 868
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 869

    def testDiff(_):  # line 871
        try:  # manually mark this file as "textual"  # line 872
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 872
        except SystemExit as E:  # line 873
            _.assertEqual(0, E.code)  # line 873
        sos.offline(options=["--strict"])  # line 874
        _.createFile(1)  # line 875
        _.createFile(2)  # line 876
        sos.commit()  # line 877
        _.createFile(1, "sdfsdgfsdf")  # line 878
        _.createFile(2, "12343")  # line 879
        sos.commit()  # line 880
        _.createFile(1, "foobar")  # line 881
        _.createFile(3)  # line 882
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 883
        _.assertIn("ADD ./file3", out)  # line 884
        _.assertAllIn(["MOD ./file2", "DIF ./file1  <No newline>", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 885
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 886

    def testReorderRenameActions(_):  # line 888
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 889
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 890
        try:  # line 891
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 891
            _.fail()  # line 891
        except:  # line 892
            pass  # line 892

    def testMove(_):  # line 894
        sos.offline(options=["--strict", "--track"])  # line 895
        _.createFile(1)  # line 896
        sos.add(".", "./file?")  # line 897
# test source folder missing
        try:  # line 899
            sos.move("sub", "sub/file?", ".", "?file")  # line 899
            _.fail()  # line 899
        except:  # line 900
            pass  # line 900
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 902
        _.assertTrue(os.path.exists("sub"))  # line 903
        _.assertTrue(os.path.exists("sub/file1"))  # line 904
        _.assertFalse(os.path.exists("file1"))  # line 905
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 907
        _.assertTrue(os.path.exists("1file"))  # line 908
        _.assertFalse(os.path.exists("sub/file1"))  # line 909
# test nothing matches source pattern
        try:  # line 911
            sos.move(".", "a*", ".", "b*")  # line 911
            _.fail()  # line 911
        except:  # line 912
            pass  # line 912
        sos.add(".", "*")  # anything pattern  # line 913
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 914
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 914
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 914
        except:  # line 915
            pass  # line 915
# test rename no conflict
        _.createFile(1)  # line 917
        _.createFile(2)  # line 918
        _.createFile(3)  # line 919
        sos.add(".", "./file*")  # line 920
        try:  # define an ignore pattern  # line 921
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 921
        except SystemExit as E:  # line 922
            _.assertEqual(0, E.code)  # line 922
        try:  # line 923
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 923
        except SystemExit as E:  # line 924
            _.assertEqual(0, E.code)  # line 924
        sos.move(".", "./file*", ".", "fi*le")  # line 925
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 926
        _.assertFalse(os.path.exists("fi4le"))  # line 927
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 929
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 933
        sos.add(".", "./?a?b", ["--force"])  # line 934
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 935
        _.createFile("1a2b")  # should not be tracked  # line 936
        _.createFile("a1b2")  # should be tracked  # line 937
        sos.commit()  # line 938
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 939
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 940
        _.createFile("1a1b1")  # line 941
        _.createFile("1a1b2")  # line 942
        sos.add(".", "?a?b*")  # line 943
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 944
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 948
        sos.offline()  # line 949
        _.createFile(1)  # line 950
        os.mkdir(sos.revisionFolder(0, 1))  # line 951
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.revisionFolder(0, 1))  # line 952
        _.createFile(1)  # line 953
        try:  # should exit with error due to collision detection  # line 954
            sos.commit()  # should exit with error due to collision detection  # line 954
            _.fail()  # should exit with error due to collision detection  # line 954
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 955
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 955

    def testFindBase(_):  # line 957
        old = os.getcwd()  # line 958
        try:  # line 959
            os.mkdir("." + os.sep + ".git")  # line 960
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 961
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 962
            os.chdir("a" + os.sep + "b")  # line 963
            s, vcs, cmd = sos.findSosVcsBase()  # line 964
            _.assertIsNotNone(s)  # line 965
            _.assertIsNotNone(vcs)  # line 966
            _.assertEqual("git", cmd)  # line 967
        finally:  # line 968
            os.chdir(old)  # line 968

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail

# TODO test +++ --- in diff
# TODO test +01/-02/*..
# TODO tests for loadcommit redirection
# TODO test wrong branch/revision after fast branching, would raise exception for -1 otherwise

if __name__ == '__main__':  # line 978
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 979
    c = configr.Configr("sos")  # line 980
    c.loadSettings()  # line 981
    if len(c.keys()) > 0:  # line 982
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 982
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 983
