#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x1b7012be

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

import builtins  # line 4
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
try:  # only required for mypy  # line 8
    from typing import Any  # only required for mypy  # line 8
    from typing import List  # only required for mypy  # line 8
    from typing import Union  # only required for mypy  # line 8
except:  # line 9
    pass  # line 9

testFolder = os.path.abspath(os.path.join(os.getcwd(), "test"))  # line 11
import configr  # optional dependency  # line 12
os.environ["TEST"] = testFolder  # needed to mock configr library calls in sos  # line 13
import sos  # import of package, not file  # line 14
sos.defaults["defaultbranch"] = "trunk"  # because sos.main() is never called  # line 15

def sync():  # line 17
    if sys.version_info[:2] >= (3, 3):  # line 18
        os.sync()  # line 18


def determineFilesystemTimeResolution() -> 'float':  # line 21
    name = str(uuid.uuid4())  # type: str  # line 22
    with open(name, "w") as fd:  # create temporary file  # line 23
        fd.write("x")  # create temporary file  # line 23
    mt = os.stat(name).st_mtime  # type: float  # get current timestamp  # line 24
    while os.stat(name).st_mtime == mt:  # wait until timestamp modified  # line 25
        time.sleep(0.05)  # to avoid 0.00s bugs (came up some time for unknown reasons)  # line 26
        with open(name, "w") as fd:  # line 27
            fd.write("x")  # line 27
    mt, start, _count = os.stat(name).st_mtime, time.time(), 0  # line 28
    while os.stat(name).st_mtime == mt:  # now cound and measure time until modified again  # line 29
        time.sleep(0.05)  # line 30
        _count += 1  # line 31
        with open(name, "w") as fd:  # line 32
            fd.write("x")  # line 32
    os.unlink(name)  # line 33
    fsprecision = round(time.time() - start, 2)  # type: float  # line 34
    print("File system timestamp precision is %.2fs; wrote to the file %d times during that time" % (fsprecision, _count))  # line 35
    return fsprecision  # line 36


FS_PRECISION = determineFilesystemTimeResolution() * 1.05  # line 39


@_coconut_tco  # line 42
def debugTestRunner(post_mortem=None):  # line 42
    ''' Unittest runner doing post mortem debugging on failing tests. '''  # line 43
    import pdb  # line 44
    if post_mortem is None:  # line 45
        post_mortem = pdb.post_mortem  # line 45
    class DebugTestResult(unittest.TextTestResult):  # line 46
        def addError(_, test, err):  # called before tearDown()  # line 47
            traceback.print_exception(*err)  # line 48
            post_mortem(err[2])  # line 49
            super(DebugTestResult, _).addError(test, err)  # line 50
        def addFailure(_, test, err):  # line 51
            traceback.print_exception(*err)  # line 52
            post_mortem(err[2])  # line 53
            super(DebugTestResult, _).addFailure(test, err)  # line 54
    return _coconut_tail_call(unittest.TextTestRunner, resultclass=DebugTestResult)  # line 55

@_coconut_tco  # line 57
def wrapChannels(func: '_coconut.typing.Callable[..., Any]'):  # line 57
    ''' Wrap function call to capture and return strings emitted on stdout and stderr. '''  # line 58
    oldv = sys.argv  # line 59
    buf = TextIOWrapper(BufferedRandom(BytesIO(b"")), encoding="utf-8")  # line 60
    sys.stdout = sys.stderr = buf  # line 61
    handler = logging.StreamHandler(buf)  # line 62
    logging.getLogger().addHandler(handler)  # line 63
    try:  # capture output into buf  # line 64
        func()  # capture output into buf  # line 64
    except Exception as E:  # line 65
        buf.write(str(E) + "\n")  # line 65
        traceback.print_exc(file=buf)  # line 65
    except SystemExit as F:  # line 66
        buf.write("EXIT CODE %s" % F.code + "\n")  # line 66
        traceback.print_exc(file=buf)  # line 66
    logging.getLogger().removeHandler(handler)  # line 67
    sys.argv, sys.stdout, sys.stderr = oldv, sys.__stdout__, sys.__stderr__  # TODO when run using pythonw.exe and/or no console, these could be None  # line 68
    buf.seek(0)  # line 69
    return _coconut_tail_call(buf.read)  # line 70

def mockInput(datas: '_coconut.typing.Sequence[str]', func) -> 'Any':  # line 72
    with mock.patch("builtins.input", side_effect=datas):  # line 73
        return func()  # line 73

def setRepoFlag(name: 'str', value: 'bool'):  # line 75
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 76
        flags, branches, config = json.loads(fd.read())  # line 76
    flags[name] = value  # line 77
    with open(sos.metaFolder + os.sep + sos.metaFile, "w") as fd:  # line 78
        fd.write(json.dumps((flags, branches, config)))  # line 78

def checkRepoFlag(name: 'str', flag: '_coconut.typing.Optional[bool]'=None, value: '_coconut.typing.Optional[Any]'=None) -> 'bool':  # line 80
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 81
        flags, branches, config = json.loads(fd.read())  # line 81
    return (name in flags and flags[name] == flag) if flag is not None else (name in config and config[name] == value)  # line 82


class Tests(unittest.TestCase):  # line 85
    ''' Entire test suite. '''  # line 86

    def setUp(_):  # line 88
        for entry in os.listdir(testFolder):  # cannot remove testFolder on Windows when using TortoiseSVN as VCS  # line 89
            resource = os.path.join(testFolder, entry)  # line 90
            shutil.rmtree(resource) if os.path.isdir(resource) else os.unlink(resource)  # line 91
        os.chdir(testFolder)  # line 92


    def assertAllIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]'):  # line 95
        for w in what:  # line 96
            _.assertIn(w, where)  # line 96

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
        changes = m.findChanges()  # detect time skew  # line 144
        _.assertEqual(1, len(changes.additions))  # line 145
        _.assertEqual(0, len(changes.deletions))  # line 146
        _.assertEqual(1, len(changes.modifications))  # line 147
        m.paths.update(changes.additions)  # line 148
        m.paths.update(changes.modifications)  # line 149
        _.createFile(2, "12")  # modify file again  # line 150
        changes = m.findChanges(0, 1)  # by size, creating new commit  # line 151
        _.assertEqual(0, len(changes.additions))  # line 152
        _.assertEqual(0, len(changes.deletions))  # line 153
        _.assertEqual(1, len(changes.modifications))  # line 154
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1)))  # line 155
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # line 156

    def testPatternPaths(_):  # line 158
        sos.offline(options=["--track"])  # line 159
        os.mkdir("sub")  # line 160
        _.createFile("sub" + os.sep + "file1", "sdfsdf")  # line 161
        sos.add("sub", "sub/file?")  # line 162
        sos.commit("test")  # should pick up sub/file1 pattern  # line 163
        _.assertEqual(2, len(os.listdir(os.path.join(sos.metaFolder, "b0", "r1"))))  # sub/file1 was added  # line 164
        _.createFile(1)  # line 165
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 166
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 166
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 166
        except:  # line 167
            pass  # line 167

    def testTokenizeGlobPattern(_):  # line 169
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 170
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 171
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 172
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 173
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 174
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 175

    def testTokenizeGlobPatterns(_):  # line 177
        try:  # because number of literal strings differs  # line 178
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 178
            _.fail()  # because number of literal strings differs  # line 178
        except:  # line 179
            pass  # line 179
        try:  # because glob patterns differ  # line 180
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 180
            _.fail()  # because glob patterns differ  # line 180
        except:  # line 181
            pass  # line 181
        try:  # glob patterns differ, regardless of position  # line 182
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 182
            _.fail()  # glob patterns differ, regardless of position  # line 182
        except:  # line 183
            pass  # line 183
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 184
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 185
        try:  # succeeds, because glob patterns match (differ only in position)  # line 186
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 186
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 186
        except:  # line 187
            pass  # line 187

    def testConvertGlobFiles(_):  # line 189
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 190
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 191

    def testFolderRemove(_):  # line 193
        m = sos.Metadata(os.getcwd())  # line 194
        _.createFile(1)  # line 195
        _.createFile("a", prefix="sub")  # line 196
        sos.offline()  # line 197
        _.createFile(2)  # line 198
        os.unlink("sub" + os.sep + "a")  # line 199
        os.rmdir("sub")  # line 200
        changes = sos.changes()  # TODO replace by output check  # line 201
        _.assertEqual(1, len(changes.additions))  # line 202
        _.assertEqual(0, len(changes.modifications))  # line 203
        _.assertEqual(1, len(changes.deletions))  # line 204
        _.createFile("a", prefix="sub")  # line 205
        changes = sos.changes()  # line 206
        _.assertEqual(0, len(changes.deletions))  # line 207

    def testSwitchConflict(_):  # line 209
        sos.offline(options=["--strict"])  # (r0)  # line 210
        _.createFile(1)  # line 211
        sos.commit()  # add file (r1)  # line 212
        os.unlink("file1")  # line 213
        sos.commit()  # remove (r2)  # line 214
        _.createFile(1, "something else")  # line 215
        sos.commit()  # (r3)  # line 216
        sos.switch("/1")  # updates file1 - marked as MOD, because mtime was changed  # line 217
        _.existsFile(1, "x" * 10)  # line 218
        sos.switch("/2", ["--force"])  # remove file1 requires --force, because size/content (or mtime in non-strict mode) is different to head of branch  # line 219
        sos.switch("/0")  # do nothing, as file1 is already removed  # line 220
        sos.switch("/1")  # add file1 back  # line 221
        sos.switch("/", ["--force"])  # requires force because changed vs. head of branch  # line 222
        _.existsFile(1, "something else")  # line 223

    def testComputeSequentialPathSet(_):  # line 225
        os.makedirs(sos.branchFolder(0, 0))  # line 226
        os.makedirs(sos.branchFolder(0, 1))  # line 227
        os.makedirs(sos.branchFolder(0, 2))  # line 228
        os.makedirs(sos.branchFolder(0, 3))  # line 229
        os.makedirs(sos.branchFolder(0, 4))  # line 230
        m = sos.Metadata(os.getcwd())  # line 231
        m.branch = 0  # line 232
        m.commit = 2  # line 233
        m.saveBranches()  # line 234
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 235
        m.saveCommit(0, 0)  # initial  # line 236
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 237
        m.saveCommit(0, 1)  # mod  # line 238
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 239
        m.saveCommit(0, 2)  # add  # line 240
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 241
        m.saveCommit(0, 3)  # del  # line 242
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")  # line 243
        m.saveCommit(0, 4)  # readd  # line 244
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 245
        m.saveBranch(0)  # line 246
        m.computeSequentialPathSet(0, 4)  # line 247
        _.assertEqual(2, len(m.paths))  # line 248

    def testParseRevisionString(_):  # line 250
        m = sos.Metadata(os.getcwd())  # line 251
        m.branch = 1  # line 252
        m.commits = {0: 0, 1: 1, 2: 2}  # line 253
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 254
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 255
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 256
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 257
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 258
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 259
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 260

    def testOfflineEmpty(_):  # line 262
        os.mkdir("." + os.sep + sos.metaFolder)  # line 263
        try:  # line 264
            sos.offline("trunk")  # line 264
            _.fail()  # line 264
        except SystemExit as E:  # line 265
            _.assertEqual(1, E.code)  # line 265
        os.rmdir("." + os.sep + sos.metaFolder)  # line 266
        sos.offline("test")  # line 267
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 268
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 269
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 270
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 271
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 272
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file  # line 273

    def testOfflineWithFiles(_):  # line 275
        _.createFile(1, "x" * 100)  # line 276
        _.createFile(2)  # line 277
        sos.offline("test")  # line 278
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 279
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 280
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 281
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 282
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 283
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 284
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file plus branch base file copies  # line 285

    def testBranch(_):  # line 287
        _.createFile(1, "x" * 100)  # line 288
        _.createFile(2)  # line 289
        sos.offline("test")  # b0/r0  # line 290
        sos.branch("other")  # b1/r0  # line 291
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 292
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 293
        _.assertEqual(list(sorted(os.listdir(sos.branchFolder(0, 0)))), list(sorted(os.listdir(sos.branchFolder(1, 0)))))  # line 295
        _.createFile(1, "z")  # modify file  # line 297
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 298
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 299
        _.createFile(3, "z")  # line 301
        sos.branch("from_last_revision", ["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 302
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 303
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 308
        _.createFile(1, "x" * 100)  # line 309
        _.createFile(2)  # line 310
        sos.offline("test")  # line 311
        changes = sos.changes()  # line 312
        _.assertEqual(0, len(changes.additions))  # line 313
        _.assertEqual(0, len(changes.deletions))  # line 314
        _.assertEqual(0, len(changes.modifications))  # line 315
        _.createFile(1, "z")  # size change  # line 316
        changes = sos.changes()  # line 317
        _.assertEqual(0, len(changes.additions))  # line 318
        _.assertEqual(0, len(changes.deletions))  # line 319
        _.assertEqual(1, len(changes.modifications))  # line 320
        sos.commit("message")  # line 321
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 322
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.branchFolder(0, 1)))  # line 323
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # no further files, only the modified one  # line 324
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 325
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 326
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 327
        os.unlink("file2")  # line 328
        changes = sos.changes()  # line 329
        _.assertEqual(0, len(changes.additions))  # line 330
        _.assertEqual(1, len(changes.deletions))  # line 331
        _.assertEqual(1, len(changes.modifications))  # line 332
        sos.commit("modified")  # line 333
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # no additional files, only mentions in metadata  # line 334
        try:  # expecting Exit due to no changes  # line 335
            sos.commit("nothing")  # expecting Exit due to no changes  # line 335
            _.fail()  # expecting Exit due to no changes  # line 335
        except:  # line 336
            pass  # line 336

    def testGetBranch(_):  # line 338
        m = sos.Metadata(os.getcwd())  # line 339
        m.branch = 1  # current branch  # line 340
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 341
        _.assertEqual(27, m.getBranchByName(27))  # line 342
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 343
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 344
        _.assertIsNone(m.getBranchByName("unknown"))  # line 345
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 346
        _.assertEqual(13, m.getRevisionByName("13"))  # line 347
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 348
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 349

    def testTagging(_):  # line 351
        m = sos.Metadata(os.getcwd())  # line 352
        sos.offline()  # line 353
        _.createFile(111)  # line 354
        sos.commit("tag", ["--tag"])  # line 355
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 356
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 357
        _.createFile(2)  # line 358
        try:  # line 359
            sos.commit("tag")  # line 359
            _.fail()  # line 359
        except:  # line 360
            pass  # line 360
        sos.commit("tag-2", ["--tag"])  # line 361
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 362
        _.assertIn("TAG tag", out)  # line 363

    def testSwitch(_):  # line 365
        _.createFile(1, "x" * 100)  # line 366
        _.createFile(2, "y")  # line 367
        sos.offline("test")  # file1-2  in initial branch commit  # line 368
        sos.branch("second")  # file1-2  switch, having same files  # line 369
        sos.switch("0")  # no change  switch back, no problem  # line 370
        sos.switch("second")  # no change  # switch back, no problem  # line 371
        _.createFile(3, "y")  # generate a file  # line 372
        try:  # uncommited changes detected  # line 373
            sos.switch("test")  # uncommited changes detected  # line 373
            _.fail()  # uncommited changes detected  # line 373
        except SystemExit as E:  # line 374
            _.assertEqual(1, E.code)  # line 374
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 375
        sos.changes()  # line 376
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 377
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 378
        _.createFile("XXX")  # line 379
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 380
        _.assertIn("File tree has changes", out)  # line 381
        _.assertNotIn("File tree is unchanged", out)  # line 382
        _.assertIn("  * b00   'test'", out)  # line 383
        _.assertIn("    b01 'second'", out)  # line 384
        _.assertIn("(dirty)", out)  # one branch has commits  # line 385
        _.assertIn("(in sync)", out)  # the other doesn't  # line 386
        _.createFile(4, "xy")  # generate a file  # line 387
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4  # line 388
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 389
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 390
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 391
        sos.switch("test", ["--force"])  # should restore file1 and remove file3  # line 392
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 393
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 394

    def testAutoDetectVCS(_):  # line 396
        os.mkdir(".git")  # line 397
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 398
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 399
            meta = fd.read()  # line 399
        _.assertTrue("\"master\"" in meta)  # line 400
        os.rmdir(".git")  # line 401

    def testUpdate(_):  # line 403
        sos.offline("trunk")  # create initial branch b0/r0  # line 404
        _.createFile(1, "x" * 100)  # line 405
        sos.commit("second")  # create b0/r1  # line 406

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 408
        _.assertFalse(_.existsFile(1))  # line 409

        sos.update("/1")  # recreate file1  # line 411
        _.assertTrue(_.existsFile(1))  # line 412

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 414
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2)))  # line 415
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2, file=sos.metaFile)))  # line 416
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # only meta data file, no differential files  # line 417

        sos.update("/1")  # do nothing, as nothing has changed  # line 419
        _.assertTrue(_.existsFile(1))  # line 420

        _.createFile(2, "y" * 100)  # line 422
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", ["--force"])  # automatically including file 2 (as we are in simple mode)  # line 425
        _.assertTrue(_.existsFile(2))  # line 426
        sos.update("trunk", ["--add"])  # only add stuff  # line 427
        _.assertTrue(_.existsFile(2))  # line 428
        sos.update("trunk")  # nothing to do  # line 429
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 430

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 432
        _.createFile(10, theirs)  # line 433
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 434
        _.createFile(11, mine)  # line 435
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 436
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 437

    def testUpdate2(_):  # line 439
        _.createFile("test.txt", "x" * 10)  # line 440
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 441
        sos.branch("mod")  # line 442
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 443
        time.sleep(FS_PRECISION)  # line 444
        sos.commit("mod")  # create b0/r1  # line 445
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 446
        with open("test.txt", "rb") as fd:  # line 447
            _.assertEqual(b"x" * 10, fd.read())  # line 447
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 448
        with open("test.txt", "rb") as fd:  # line 449
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 449
        _.createFile("test.txt", "x" * 10)  # line 450
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 451
        with open("test.txt", "rb") as fd:  # line 452
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 452
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 453
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 454
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 455
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 456
        with open("test.txt", "rb") as fd:  # line 457
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 457

    def testIsTextType(_):  # line 459
        m = sos.Metadata(".")  # line 460
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 461
        m.c.bintype = ["*.md.confluence"]  # line 462
        _.assertTrue(m.isTextType("ab.txt"))  # line 463
        _.assertTrue(m.isTextType("./ab.txt"))  # line 464
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 465
        _.assertFalse(m.isTextType("bc/ab."))  # line 466
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 467
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 468
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 469
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 470

    def testEolDet(_):  # line 472
        ''' Check correct end-of-line detection. '''  # line 473
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 474
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 475
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 476
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 477
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 478
        _.assertIsNone(sos.eoldet(b""))  # line 479
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 480

    def testMerge(_):  # line 482
        ''' Check merge results depending on user options. '''  # line 483
        a = b"a\nb\ncc\nd"  # type: bytes  # line 484
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 485
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge  # line 486
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace  # line 487
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace  # line 488
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge  # line 489
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 490
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 491
        a = b"a\nb\ncc\nd"  # line 492
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 493
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement  # line 494
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # line 495
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 496
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])  # line 498
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 499
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 501
        b = b"a\nc\ne"  # line 502
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 503
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 504
        a = b"a\nb\ne"  # intra-line merge  # line 505
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 506
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 507

    def testMergeEol(_):  # line 509
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])  # line 510
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 511
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF  # line 512
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])  # line 513
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])  # line 514

    def testPickyMode(_):  # line 516
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 517
        sos.offline("trunk", ["--picky"])  # line 518
        changes = sos.changes()  # line 519
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 520
        sos.add(".", "./file?", ["--force"])  # line 521
        _.createFile(1, "aa")  # line 522
        sos.commit("First")  # add one file  # line 523
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 524
        _.createFile(2, "b")  # line 525
        try:  # add nothing, because picky  # line 526
            sos.commit("Second")  # add nothing, because picky  # line 526
        except:  # line 527
            pass  # line 527
        sos.add(".", "./file?")  # line 528
        sos.commit("Third")  # line 529
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # line 530
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 531
        _.assertIn("  * r2", out)  # line 532
        _.createFile(3, prefix="sub")  # line 533
        sos.add("sub", "sub/file?")  # line 534
        changes = sos.changes()  # line 535
        _.assertEqual(1, len(changes.additions))  # line 536
        _.assertTrue("sub/file3" in changes.additions)  # line 537

    def testTrackedSubfolder(_):  # line 539
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 540
        os.mkdir("." + os.sep + "sub")  # line 541
        sos.offline("trunk", ["--track"])  # line 542
        _.createFile(1, "x")  # line 543
        _.createFile(1, "x", prefix="sub")  # line 544
        sos.add(".", "./file?")  # add glob pattern to track  # line 545
        sos.commit("First")  # line 546
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 547
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 548
        sos.commit("Second")  # one new file + meta  # line 549
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 550
        os.unlink("file1")  # remove from basefolder  # line 551
        _.createFile(2, "y")  # line 552
        sos.remove(".", "sub/file?")  # line 553
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 554
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 554
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 554
        except:  # line 555
            pass  # line 555
        sos.commit("Third")  # line 556
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta  # line 557
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 560
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 565
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 566
        _.createFile(1)  # line 567
        _.createFile("a123a")  # untracked file "a123a"  # line 568
        sos.add(".", "./file?")  # add glob tracking pattern  # line 569
        sos.commit("second")  # versions "file1"  # line 570
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 571
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 572
        _.assertIn("  | ./file?", out)  # line 573

        _.createFile(2)  # untracked file "file2"  # line 575
        sos.commit("third")  # versions "file2"  # line 576
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta file  # line 577

        os.mkdir("." + os.sep + "sub")  # line 579
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 580
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 581
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 3))))  # meta file only, no other tracked path/file  # line 582

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 584
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 585
        sos.add(".", "./a*a")  # add tracking pattern  # line 586
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 587
        _.assertEqual(0, len(changes.modifications))  # line 588
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 589
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 590

        sos.commit("Second_2")  # line 592
        _.assertEqual(2, len(os.listdir(sos.branchFolder(1, 1))))  # "a123a" + meta file  # line 593
        _.existsFile(1, b"x" * 10)  # line 594
        _.existsFile(2, b"x" * 10)  # line 595

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 597
        _.existsFile(1, b"x" * 10)  # line 598
        _.existsFile("a123a", b"x" * 10)  # line 599

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 601
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 602
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 603

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 605
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 606
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 607
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 608
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 609
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 610
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 611
# TODO test switch --meta

    def testLsTracked(_):  # line 614
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 615
        _.createFile(1)  # line 616
        _.createFile("foo")  # line 617
        sos.add(".", "./file*")  # capture one file  # line 618
        sos.ls()  # line 619
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 620
        _.assertInAny("TRK file1  (file*)", out)  # line 621
        _.assertNotInAny("... file1  (file*)", out)  # line 622
        _.assertInAny("··· foo", out)  # line 623
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 624
        _.assertInAny("TRK file*", out)  # line 625
        _.createFile("a", prefix="sub")  # line 626
        sos.add("sub", "sub/a")  # line 627
        sos.ls("sub")  # line 628
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 629

    def testLineMerge(_):  # line 631
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 632
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 633
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 634
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 635

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 637
        _.createFile(1)  # line 638
        sos.offline("master", options=["--force"])  # line 639
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 640
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 641
        _.assertTrue(_.existsFile(sos.branchFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 642
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 643
        _.createFile(2)  # line 644
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 645
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 646
        _.assertTrue(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 647
        _.assertFalse(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 648

    def testLocalConfig(_):  # line 650
        sos.offline("bla", options=[])  # line 651
        try:  # line 652
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 652
        except SystemExit as E:  # line 653
            _.assertEqual(0, E.code)  # line 653
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 654

    def testConfigVariations(_):  # line 656
        def makeRepo():  # line 657
            try:  # line 658
                os.unlink("file1")  # line 658
            except:  # line 659
                pass  # line 659
            sos.offline("master", options=["--force"])  # line 660
            _.createFile(1)  # line 661
            sos.commit("Added file1")  # line 662
        try:  # line 663
            sos.config(["set", "strict", "on"])  # line 663
        except SystemExit as E:  # line 664
            _.assertEqual(0, E.code)  # line 664
        makeRepo()  # line 665
        _.assertTrue(checkRepoFlag("strict", True))  # line 666
        try:  # line 667
            sos.config(["set", "strict", "off"])  # line 667
        except SystemExit as E:  # line 668
            _.assertEqual(0, E.code)  # line 668
        makeRepo()  # line 669
        _.assertTrue(checkRepoFlag("strict", False))  # line 670
        try:  # line 671
            sos.config(["set", "strict", "yes"])  # line 671
        except SystemExit as E:  # line 672
            _.assertEqual(0, E.code)  # line 672
        makeRepo()  # line 673
        _.assertTrue(checkRepoFlag("strict", True))  # line 674
        try:  # line 675
            sos.config(["set", "strict", "no"])  # line 675
        except SystemExit as E:  # line 676
            _.assertEqual(0, E.code)  # line 676
        makeRepo()  # line 677
        _.assertTrue(checkRepoFlag("strict", False))  # line 678
        try:  # line 679
            sos.config(["set", "strict", "1"])  # line 679
        except SystemExit as E:  # line 680
            _.assertEqual(0, E.code)  # line 680
        makeRepo()  # line 681
        _.assertTrue(checkRepoFlag("strict", True))  # line 682
        try:  # line 683
            sos.config(["set", "strict", "0"])  # line 683
        except SystemExit as E:  # line 684
            _.assertEqual(0, E.code)  # line 684
        makeRepo()  # line 685
        _.assertTrue(checkRepoFlag("strict", False))  # line 686
        try:  # line 687
            sos.config(["set", "strict", "true"])  # line 687
        except SystemExit as E:  # line 688
            _.assertEqual(0, E.code)  # line 688
        makeRepo()  # line 689
        _.assertTrue(checkRepoFlag("strict", True))  # line 690
        try:  # line 691
            sos.config(["set", "strict", "false"])  # line 691
        except SystemExit as E:  # line 692
            _.assertEqual(0, E.code)  # line 692
        makeRepo()  # line 693
        _.assertTrue(checkRepoFlag("strict", False))  # line 694
        try:  # line 695
            sos.config(["set", "strict", "enable"])  # line 695
        except SystemExit as E:  # line 696
            _.assertEqual(0, E.code)  # line 696
        makeRepo()  # line 697
        _.assertTrue(checkRepoFlag("strict", True))  # line 698
        try:  # line 699
            sos.config(["set", "strict", "disable"])  # line 699
        except SystemExit as E:  # line 700
            _.assertEqual(0, E.code)  # line 700
        makeRepo()  # line 701
        _.assertTrue(checkRepoFlag("strict", False))  # line 702
        try:  # line 703
            sos.config(["set", "strict", "enabled"])  # line 703
        except SystemExit as E:  # line 704
            _.assertEqual(0, E.code)  # line 704
        makeRepo()  # line 705
        _.assertTrue(checkRepoFlag("strict", True))  # line 706
        try:  # line 707
            sos.config(["set", "strict", "disabled"])  # line 707
        except SystemExit as E:  # line 708
            _.assertEqual(0, E.code)  # line 708
        makeRepo()  # line 709
        _.assertTrue(checkRepoFlag("strict", False))  # line 710
        try:  # line 711
            sos.config(["set", "strict", "nope"])  # line 711
            _.fail()  # line 711
        except SystemExit as E:  # line 712
            _.assertEqual(1, E.code)  # line 712

    def testLsSimple(_):  # line 714
        _.createFile(1)  # line 715
        _.createFile("foo")  # line 716
        _.createFile("ign1")  # line 717
        _.createFile("ign2")  # line 718
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 719
        try:  # define an ignore pattern  # line 720
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 720
        except SystemExit as E:  # line 721
            _.assertEqual(0, E.code)  # line 721
        try:  # additional ignore pattern  # line 722
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 722
        except SystemExit as E:  # line 723
            _.assertEqual(0, E.code)  # line 723
        try:  # define a list of ignore patterns  # line 724
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 724
        except SystemExit as E:  # line 725
            _.assertEqual(0, E.code)  # line 725
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 726
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 727
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 728
        _.assertInAny('··· file1', out)  # line 729
        _.assertInAny('··· ign1', out)  # line 730
        _.assertInAny('··· ign2', out)  # line 731
        try:  # line 732
            sos.config(["rm", "foo", "bar"])  # line 732
            _.fail()  # line 732
        except SystemExit as E:  # line 733
            _.assertEqual(1, E.code)  # line 733
        try:  # line 734
            sos.config(["rm", "ignores", "foo"])  # line 734
            _.fail()  # line 734
        except SystemExit as E:  # line 735
            _.assertEqual(1, E.code)  # line 735
        try:  # line 736
            sos.config(["rm", "ignores", "ign1"])  # line 736
        except SystemExit as E:  # line 737
            _.assertEqual(0, E.code)  # line 737
        try:  # remove ignore pattern  # line 738
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 738
        except SystemExit as E:  # line 739
            _.assertEqual(0, E.code)  # line 739
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 740
        _.assertInAny('··· ign1', out)  # line 741
        _.assertInAny('IGN ign2', out)  # line 742
        _.assertNotInAny('··· ign2', out)  # line 743

    def testWhitelist(_):  # line 745
# TODO test same for simple mode
        _.createFile(1)  # line 747
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 748
        sos.offline("xx", ["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 749
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 750
        sos.commit(options=["--force"])  # attempt to commit the file  # line 751
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 1))))  # only meta data, file1 was ignored  # line 752
        try:  # Exit because dirty  # line 753
            sos.online()  # Exit because dirty  # line 753
            _.fail()  # Exit because dirty  # line 753
        except:  # exception expected  # line 754
            pass  # exception expected  # line 754
        _.createFile("x2")  # add another change  # line 755
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 756
        try:  # force beyond dirty flag check  # line 757
            sos.online(["--force"])  # force beyond dirty flag check  # line 757
            _.fail()  # force beyond dirty flag check  # line 757
        except:  # line 758
            pass  # line 758
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 759
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 760

        _.createFile(1)  # line 762
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 763
        sos.offline("xx", ["--track"])  # line 764
        sos.add(".", "./file*")  # line 765
        sos.commit()  # should NOT ask for force here  # line 766
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 767

    def testRemove(_):  # line 769
        _.createFile(1, "x" * 100)  # line 770
        sos.offline("trunk")  # line 771
        try:  # line 772
            sos.delete("trunk")  # line 772
            _fail()  # line 772
        except:  # line 773
            pass  # line 773
        _.createFile(2, "y" * 10)  # line 774
        sos.branch("added")  # line 775
        sos.delete("trunk")  # line 776
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # meta data file and "b1"  # line 777
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 778
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 779
        sos.branch("next")  # line 780
        _.createFile(3, "y" * 10)  # make a change  # line 781
        sos.delete("added", "--force")  # should succeed  # line 782

    def testUsage(_):  # line 784
        try:  # TODO expect sys.exit(0)  # line 785
            sos.usage()  # TODO expect sys.exit(0)  # line 785
            _.fail()  # TODO expect sys.exit(0)  # line 785
        except:  # line 786
            pass  # line 786
        try:  # line 787
            sos.usage(short=True)  # line 787
            _.fail()  # line 787
        except:  # line 788
            pass  # line 788

    def testOnlyExcept(_):  # line 790
        ''' Test blacklist glob rules. '''  # line 791
        sos.offline(options=["--track"])  # line 792
        _.createFile("a.1")  # line 793
        _.createFile("a.2")  # line 794
        _.createFile("b.1")  # line 795
        _.createFile("b.2")  # line 796
        sos.add(".", "./a.?")  # line 797
        sos.add(".", "./?.1", negative=True)  # line 798
        out = wrapChannels(lambda: sos.commit())  # line 799
        _.assertIn("ADD ./a.2", out)  # line 800
        _.assertNotIn("ADD ./a.1", out)  # line 801
        _.assertNotIn("ADD ./b.1", out)  # line 802
        _.assertNotIn("ADD ./b.2", out)  # line 803

    def testOnly(_):  # line 805
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 806
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 807
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 808
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 809
        sos.offline(options=["--track", "--strict"])  # line 810
        _.createFile(1)  # line 811
        _.createFile(2)  # line 812
        sos.add(".", "./file1")  # line 813
        sos.add(".", "./file2")  # line 814
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 815
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # only meta and file1  # line 816
        sos.commit()  # adds also file2  # line 817
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # only meta and file1  # line 818
        _.createFile(1, "cc")  # modify both files  # line 819
        _.createFile(2, "dd")  # line 820
        try:  # line 821
            sos.config(["set", "texttype", "file2"])  # line 821
        except SystemExit as E:  # line 822
            _.assertEqual(0, E.code)  # line 822
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))  # line 823
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 824
        _.assertTrue("./file2" in changes.modifications)  # line 825
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 826
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 827

    def testDiff(_):  # line 829
        try:  # manually mark this file as "textual"  # line 830
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 830
        except SystemExit as E:  # line 831
            _.assertEqual(0, E.code)  # line 831
        sos.offline(options=["--strict"])  # line 832
        _.createFile(1)  # line 833
        _.createFile(2)  # line 834
        sos.commit()  # line 835
        _.createFile(1, "sdfsdgfsdf")  # line 836
        _.createFile(2, "12343")  # line 837
        sos.commit()  # line 838
        _.createFile(1, "foobar")  # line 839
        _.createFile(3)  # line 840
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 841
        _.assertIn("ADD ./file3", out)  # line 842
        _.assertAllIn(["MOD ./file2", "DIF ./file1", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 843
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 844

    def testReorderRenameActions(_):  # line 846
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 847
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 848
        try:  # line 849
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 849
            _.fail()  # line 849
        except:  # line 850
            pass  # line 850

    def testMove(_):  # line 852
        sos.offline(options=["--strict", "--track"])  # line 853
        _.createFile(1)  # line 854
        sos.add(".", "./file?")  # line 855
# test source folder missing
        try:  # line 857
            sos.move("sub", "sub/file?", ".", "?file")  # line 857
            _.fail()  # line 857
        except:  # line 858
            pass  # line 858
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 860
        _.assertTrue(os.path.exists("sub"))  # line 861
        _.assertTrue(os.path.exists("sub/file1"))  # line 862
        _.assertFalse(os.path.exists("file1"))  # line 863
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 865
        _.assertTrue(os.path.exists("1file"))  # line 866
        _.assertFalse(os.path.exists("sub/file1"))  # line 867
# test nothing matches source pattern
        try:  # line 869
            sos.move(".", "a*", ".", "b*")  # line 869
            _.fail()  # line 869
        except:  # line 870
            pass  # line 870
        sos.add(".", "*")  # anything pattern  # line 871
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 872
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 872
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 872
        except:  # line 873
            pass  # line 873
# test rename no conflict
        _.createFile(1)  # line 875
        _.createFile(2)  # line 876
        _.createFile(3)  # line 877
        sos.add(".", "./file*")  # line 878
        try:  # define an ignore pattern  # line 879
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 879
        except SystemExit as E:  # line 880
            _.assertEqual(0, E.code)  # line 880
        try:  # line 881
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 881
        except SystemExit as E:  # line 882
            _.assertEqual(0, E.code)  # line 882
        sos.move(".", "./file*", ".", "fi*le")  # line 883
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 884
        _.assertFalse(os.path.exists("fi4le"))  # line 885
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 887
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 891
        sos.add(".", "./?a?b", ["--force"])  # line 892
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 893
        _.createFile("1a2b")  # should not be tracked  # line 894
        _.createFile("a1b2")  # should be tracked  # line 895
        sos.commit()  # line 896
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 897
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 898
        _.createFile("1a1b1")  # line 899
        _.createFile("1a1b2")  # line 900
        sos.add(".", "?a?b*")  # line 901
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 902
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 906
        sos.offline()  # line 907
        _.createFile(1)  # line 908
        os.mkdir(sos.branchFolder(0, 1))  # line 909
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.branchFolder(0, 1))  # line 910
        _.createFile(1)  # line 911
        try:  # should exit with error due to collision detection  # line 912
            sos.commit()  # should exit with error due to collision detection  # line 912
            _.fail()  # should exit with error due to collision detection  # line 912
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 913
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 913

    def testFindBase(_):  # line 915
        old = os.getcwd()  # line 916
        try:  # line 917
            os.mkdir("." + os.sep + ".git")  # line 918
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 919
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 920
            os.chdir("a" + os.sep + "b")  # line 921
            s, vcs, cmd = sos.findSosVcsBase()  # line 922
            _.assertIsNotNone(s)  # line 923
            _.assertIsNotNone(vcs)  # line 924
            _.assertEqual("git", cmd)  # line 925
        finally:  # line 926
            os.chdir(old)  # line 926

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail


if __name__ == '__main__':  # line 932
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 933
    c = configr.Configr("sos")  # line 934
    c.loadSettings()  # line 935
    if len(c.keys()) > 0:  # line 936
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 936
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 937
