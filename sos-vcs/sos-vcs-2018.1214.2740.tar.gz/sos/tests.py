#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x1226736e

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
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1)))  # line 157
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # line 158
# TODO test moves

    def testPatternPaths(_):  # line 161
        sos.offline(options=["--track"])  # line 162
        os.mkdir("sub")  # line 163
        _.createFile("sub" + os.sep + "file1", "sdfsdf")  # line 164
        sos.add("sub", "sub/file?")  # line 165
        sos.commit("test")  # should pick up sub/file1 pattern  # line 166
        _.assertEqual(2, len(os.listdir(os.path.join(sos.metaFolder, "b0", "r1"))))  # sub/file1 was added  # line 167
        _.createFile(1)  # line 168
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 169
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 169
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 169
        except:  # line 170
            pass  # line 170

    def testTokenizeGlobPattern(_):  # line 172
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 173
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 174
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 175
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 176
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 177
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 178

    def testTokenizeGlobPatterns(_):  # line 180
        try:  # because number of literal strings differs  # line 181
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 181
            _.fail()  # because number of literal strings differs  # line 181
        except:  # line 182
            pass  # line 182
        try:  # because glob patterns differ  # line 183
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 183
            _.fail()  # because glob patterns differ  # line 183
        except:  # line 184
            pass  # line 184
        try:  # glob patterns differ, regardless of position  # line 185
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 185
            _.fail()  # glob patterns differ, regardless of position  # line 185
        except:  # line 186
            pass  # line 186
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 187
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 188
        try:  # succeeds, because glob patterns match (differ only in position)  # line 189
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 189
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 189
        except:  # line 190
            pass  # line 190

    def testConvertGlobFiles(_):  # line 192
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 193
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 194

    def testFolderRemove(_):  # line 196
        m = sos.Metadata(os.getcwd())  # line 197
        _.createFile(1)  # line 198
        _.createFile("a", prefix="sub")  # line 199
        sos.offline()  # line 200
        _.createFile(2)  # line 201
        os.unlink("sub" + os.sep + "a")  # line 202
        os.rmdir("sub")  # line 203
        changes = sos.changes()  # TODO replace by output check  # line 204
        _.assertEqual(1, len(changes.additions))  # line 205
        _.assertEqual(0, len(changes.modifications))  # line 206
        _.assertEqual(1, len(changes.deletions))  # line 207
        _.createFile("a", prefix="sub")  # line 208
        changes = sos.changes()  # line 209
        _.assertEqual(0, len(changes.deletions))  # line 210

    def testSwitchConflict(_):  # line 212
        sos.offline(options=["--strict"])  # (r0)  # line 213
        _.createFile(1)  # line 214
        sos.commit()  # add file (r1)  # line 215
        os.unlink("file1")  # line 216
        sos.commit()  # remove (r2)  # line 217
        _.createFile(1, "something else")  # line 218
        sos.commit()  # (r3)  # line 219
        sos.switch("/1")  # updates file1 - marked as MOD, because mtime was changed  # line 220
        _.existsFile(1, "x" * 10)  # line 221
        sos.switch("/2", ["--force"])  # remove file1 requires --force, because size/content (or mtime in non-strict mode) is different to head of branch  # line 222
        sos.switch("/0")  # do nothing, as file1 is already removed  # line 223
        sos.switch("/1")  # add file1 back  # line 224
        sos.switch("/", ["--force"])  # requires force because changed vs. head of branch  # line 225
        _.existsFile(1, "something else")  # line 226

    def testComputeSequentialPathSet(_):  # line 228
        os.makedirs(sos.branchFolder(0, 0))  # line 229
        os.makedirs(sos.branchFolder(0, 1))  # line 230
        os.makedirs(sos.branchFolder(0, 2))  # line 231
        os.makedirs(sos.branchFolder(0, 3))  # line 232
        os.makedirs(sos.branchFolder(0, 4))  # line 233
        m = sos.Metadata(os.getcwd())  # line 234
        m.branch = 0  # line 235
        m.commit = 2  # line 236
        m.saveBranches()  # line 237
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 238
        m.saveCommit(0, 0)  # initial  # line 239
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 240
        m.saveCommit(0, 1)  # mod  # line 241
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 242
        m.saveCommit(0, 2)  # add  # line 243
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 244
        m.saveCommit(0, 3)  # del  # line 245
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")  # line 246
        m.saveCommit(0, 4)  # readd  # line 247
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 248
        m.saveBranch(0)  # line 249
        m.computeSequentialPathSet(0, 4)  # line 250
        _.assertEqual(2, len(m.paths))  # line 251

    def testParseRevisionString(_):  # line 253
        m = sos.Metadata(os.getcwd())  # line 254
        m.branch = 1  # line 255
        m.commits = {0: 0, 1: 1, 2: 2}  # line 256
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 257
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 258
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 259
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 260
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 261
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 262
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 263

    def testOfflineEmpty(_):  # line 265
        os.mkdir("." + os.sep + sos.metaFolder)  # line 266
        try:  # line 267
            sos.offline("trunk")  # line 267
            _.fail()  # line 267
        except SystemExit as E:  # line 268
            _.assertEqual(1, E.code)  # line 268
        os.rmdir("." + os.sep + sos.metaFolder)  # line 269
        sos.offline("test")  # line 270
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 271
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 272
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 273
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 274
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 275
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file  # line 276

    def testOfflineWithFiles(_):  # line 278
        _.createFile(1, "x" * 100)  # line 279
        _.createFile(2)  # line 280
        sos.offline("test")  # line 281
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 282
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 283
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 284
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 285
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 286
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 287
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file plus branch base file copies  # line 288

    def testBranch(_):  # line 290
        _.createFile(1, "x" * 100)  # line 291
        _.createFile(2)  # line 292
        sos.offline("test")  # b0/r0  # line 293
        sos.branch("other")  # b1/r0  # line 294
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 295
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 296
        _.assertEqual(list(sorted(os.listdir(sos.branchFolder(0, 0)))), list(sorted(os.listdir(sos.branchFolder(1, 0)))))  # line 298
        _.createFile(1, "z")  # modify file  # line 300
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 301
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 302
        _.createFile(3, "z")  # line 304
        sos.branch("from_last_revision", ["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 305
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 306
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 311
        _.createFile(1, "x" * 100)  # line 312
        _.createFile(2)  # line 313
        sos.offline("test")  # line 314
        changes = sos.changes()  # line 315
        _.assertEqual(0, len(changes.additions))  # line 316
        _.assertEqual(0, len(changes.deletions))  # line 317
        _.assertEqual(0, len(changes.modifications))  # line 318
        _.createFile(1, "z")  # size change  # line 319
        changes = sos.changes()  # line 320
        _.assertEqual(0, len(changes.additions))  # line 321
        _.assertEqual(0, len(changes.deletions))  # line 322
        _.assertEqual(1, len(changes.modifications))  # line 323
        sos.commit("message")  # line 324
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 325
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.branchFolder(0, 1)))  # line 326
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # no further files, only the modified one  # line 327
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 328
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 329
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 330
        os.unlink("file2")  # line 331
        changes = sos.changes()  # line 332
        _.assertEqual(0, len(changes.additions))  # line 333
        _.assertEqual(1, len(changes.deletions))  # line 334
        _.assertEqual(1, len(changes.modifications))  # line 335
        sos.commit("modified")  # line 336
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # no additional files, only mentions in metadata  # line 337
        try:  # expecting Exit due to no changes  # line 338
            sos.commit("nothing")  # expecting Exit due to no changes  # line 338
            _.fail()  # expecting Exit due to no changes  # line 338
        except:  # line 339
            pass  # line 339

    def testGetBranch(_):  # line 341
        m = sos.Metadata(os.getcwd())  # line 342
        m.branch = 1  # current branch  # line 343
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 344
        _.assertEqual(27, m.getBranchByName(27))  # line 345
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 346
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 347
        _.assertIsNone(m.getBranchByName("unknown"))  # line 348
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 349
        _.assertEqual(13, m.getRevisionByName("13"))  # line 350
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 351
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 352

    def testTagging(_):  # line 354
        m = sos.Metadata(os.getcwd())  # line 355
        sos.offline()  # line 356
        _.createFile(111)  # line 357
        sos.commit("tag", ["--tag"])  # line 358
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 359
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 360
        _.createFile(2)  # line 361
        try:  # line 362
            sos.commit("tag")  # line 362
            _.fail()  # line 362
        except:  # line 363
            pass  # line 363
        sos.commit("tag-2", ["--tag"])  # line 364
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 365
        _.assertIn("TAG tag", out)  # line 366

    def testSwitch(_):  # line 368
        _.createFile(1, "x" * 100)  # line 369
        _.createFile(2, "y")  # line 370
        sos.offline("test")  # file1-2  in initial branch commit  # line 371
        sos.branch("second")  # file1-2  switch, having same files  # line 372
        sos.switch("0")  # no change  switch back, no problem  # line 373
        sos.switch("second")  # no change  # switch back, no problem  # line 374
        _.createFile(3, "y")  # generate a file  # line 375
        try:  # uncommited changes detected  # line 376
            sos.switch("test")  # uncommited changes detected  # line 376
            _.fail()  # uncommited changes detected  # line 376
        except SystemExit as E:  # line 377
            _.assertEqual(1, E.code)  # line 377
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 378
        sos.changes()  # line 379
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 380
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 381
        _.createFile("XXX")  # line 382
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 383
        _.assertIn("File tree has changes", out)  # line 384
        _.assertNotIn("File tree is unchanged", out)  # line 385
        _.assertIn("  * b00   'test'", out)  # line 386
        _.assertIn("    b01 'second'", out)  # line 387
        _.assertIn("(dirty)", out)  # one branch has commits  # line 388
        _.assertIn("(in sync)", out)  # the other doesn't  # line 389
        _.createFile(4, "xy")  # generate a file  # line 390
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4  # line 391
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 392
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 393
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 394
        sos.switch("test", ["--force"])  # should restore file1 and remove file3  # line 395
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 396
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 397

    def testAutoDetectVCS(_):  # line 399
        os.mkdir(".git")  # line 400
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 401
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 402
            meta = fd.read()  # line 402
        _.assertTrue("\"master\"" in meta)  # line 403
        os.rmdir(".git")  # line 404

    def testUpdate(_):  # line 406
        sos.offline("trunk")  # create initial branch b0/r0  # line 407
        _.createFile(1, "x" * 100)  # line 408
        sos.commit("second")  # create b0/r1  # line 409

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 411
        _.assertFalse(_.existsFile(1))  # line 412

        sos.update("/1")  # recreate file1  # line 414
        _.assertTrue(_.existsFile(1))  # line 415

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 417
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2)))  # line 418
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2, file=sos.metaFile)))  # line 419
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # only meta data file, no differential files  # line 420

        sos.update("/1")  # do nothing, as nothing has changed  # line 422
        _.assertTrue(_.existsFile(1))  # line 423

        _.createFile(2, "y" * 100)  # line 425
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", ["--force"])  # automatically including file 2 (as we are in simple mode)  # line 428
        _.assertTrue(_.existsFile(2))  # line 429
        sos.update("trunk", ["--add"])  # only add stuff  # line 430
        _.assertTrue(_.existsFile(2))  # line 431
        sos.update("trunk")  # nothing to do  # line 432
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 433

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 435
        _.createFile(10, theirs)  # line 436
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 437
        _.createFile(11, mine)  # line 438
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 439
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 440

    def testUpdate2(_):  # line 442
        _.createFile("test.txt", "x" * 10)  # line 443
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 444
        sos.branch("mod")  # line 445
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 446
        time.sleep(FS_PRECISION)  # line 447
        sos.commit("mod")  # create b0/r1  # line 448
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 449
        with open("test.txt", "rb") as fd:  # line 450
            _.assertEqual(b"x" * 10, fd.read())  # line 450
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 451
        with open("test.txt", "rb") as fd:  # line 452
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 452
        _.createFile("test.txt", "x" * 10)  # line 453
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 454
        with open("test.txt", "rb") as fd:  # line 455
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 455
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 456
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 457
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 458
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 459
        with open("test.txt", "rb") as fd:  # line 460
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 460

    def testIsTextType(_):  # line 462
        m = sos.Metadata(".")  # line 463
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 464
        m.c.bintype = ["*.md.confluence"]  # line 465
        _.assertTrue(m.isTextType("ab.txt"))  # line 466
        _.assertTrue(m.isTextType("./ab.txt"))  # line 467
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 468
        _.assertFalse(m.isTextType("bc/ab."))  # line 469
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 470
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 471
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 472
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 473

    def testEolDet(_):  # line 475
        ''' Check correct end-of-line detection. '''  # line 476
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 477
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 478
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 479
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 480
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 481
        _.assertIsNone(sos.eoldet(b""))  # line 482
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 483

    def testMerge(_):  # line 485
        ''' Check merge results depending on user options. '''  # line 486
        a = b"a\nb\ncc\nd"  # type: bytes  # line 487
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 488
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge  # line 489
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace  # line 490
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace  # line 491
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge  # line 492
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 493
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 494
        a = b"a\nb\ncc\nd"  # line 495
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 496
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement  # line 497
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # line 498
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 499
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])  # line 501
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 502
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 504
        b = b"a\nc\ne"  # line 505
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 506
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 507
        a = b"a\nb\ne"  # intra-line merge  # line 508
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 509
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 510

    def testMergeEol(_):  # line 512
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])  # line 513
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 514
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF  # line 515
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])  # line 516
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])  # line 517

    def testPickyMode(_):  # line 519
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 520
        sos.offline("trunk", ["--picky"])  # line 521
        changes = sos.changes()  # line 522
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 523
        sos.add(".", "./file?", ["--force"])  # line 524
        _.createFile(1, "aa")  # line 525
        sos.commit("First")  # add one file  # line 526
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 527
        _.createFile(2, "b")  # line 528
        try:  # add nothing, because picky  # line 529
            sos.commit("Second")  # add nothing, because picky  # line 529
        except:  # line 530
            pass  # line 530
        sos.add(".", "./file?")  # line 531
        sos.commit("Third")  # line 532
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # line 533
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 534
        _.assertIn("  * r2", out)  # line 535
        _.createFile(3, prefix="sub")  # line 536
        sos.add("sub", "sub/file?")  # line 537
        changes = sos.changes()  # line 538
        _.assertEqual(1, len(changes.additions))  # line 539
        _.assertTrue("sub/file3" in changes.additions)  # line 540

    def testTrackedSubfolder(_):  # line 542
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 543
        os.mkdir("." + os.sep + "sub")  # line 544
        sos.offline("trunk", ["--track"])  # line 545
        _.createFile(1, "x")  # line 546
        _.createFile(1, "x", prefix="sub")  # line 547
        sos.add(".", "./file?")  # add glob pattern to track  # line 548
        sos.commit("First")  # line 549
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 550
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 551
        sos.commit("Second")  # one new file + meta  # line 552
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 553
        os.unlink("file1")  # remove from basefolder  # line 554
        _.createFile(2, "y")  # line 555
        sos.remove(".", "sub/file?")  # line 556
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 557
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 557
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 557
        except:  # line 558
            pass  # line 558
        sos.commit("Third")  # line 559
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta  # line 560
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 563
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 568
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 569
        _.createFile(1)  # line 570
        _.createFile("a123a")  # untracked file "a123a"  # line 571
        sos.add(".", "./file?")  # add glob tracking pattern  # line 572
        sos.commit("second")  # versions "file1"  # line 573
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 574
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 575
        _.assertIn("  | ./file?", out)  # line 576

        _.createFile(2)  # untracked file "file2"  # line 578
        sos.commit("third")  # versions "file2"  # line 579
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta file  # line 580

        os.mkdir("." + os.sep + "sub")  # line 582
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 583
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 584
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 3))))  # meta file only, no other tracked path/file  # line 585

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 587
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 588
        sos.add(".", "./a*a")  # add tracking pattern  # line 589
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 590
        _.assertEqual(0, len(changes.modifications))  # line 591
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 592
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 593

        sos.commit("Second_2")  # line 595
        _.assertEqual(2, len(os.listdir(sos.branchFolder(1, 1))))  # "a123a" + meta file  # line 596
        _.existsFile(1, b"x" * 10)  # line 597
        _.existsFile(2, b"x" * 10)  # line 598

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 600
        _.existsFile(1, b"x" * 10)  # line 601
        _.existsFile("a123a", b"x" * 10)  # line 602

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 604
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 605
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 606

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 608
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 609
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 610
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 611
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 612
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 613
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 614
# TODO test switch --meta

    def testLsTracked(_):  # line 617
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 618
        _.createFile(1)  # line 619
        _.createFile("foo")  # line 620
        sos.add(".", "./file*")  # capture one file  # line 621
        sos.ls()  # line 622
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 623
        _.assertInAny("TRK file1  (file*)", out)  # line 624
        _.assertNotInAny("... file1  (file*)", out)  # line 625
        _.assertInAny("··· foo", out)  # line 626
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 627
        _.assertInAny("TRK file*", out)  # line 628
        _.createFile("a", prefix="sub")  # line 629
        sos.add("sub", "sub/a")  # line 630
        sos.ls("sub")  # line 631
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 632

    def testLineMerge(_):  # line 634
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 635
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 636
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 637
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 638

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 640
        _.createFile(1)  # line 641
        sos.offline("master", options=["--force"])  # line 642
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 643
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 644
        _.assertTrue(_.existsFile(sos.branchFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 645
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 646
        _.createFile(2)  # line 647
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 648
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 649
        _.assertTrue(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 650
        _.assertFalse(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 651

    def testLocalConfig(_):  # line 653
        sos.offline("bla", options=[])  # line 654
        try:  # line 655
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 655
        except SystemExit as E:  # line 656
            _.assertEqual(0, E.code)  # line 656
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 657

    def testConfigVariations(_):  # line 659
        def makeRepo():  # line 660
            try:  # line 661
                os.unlink("file1")  # line 661
            except:  # line 662
                pass  # line 662
            sos.offline("master", options=["--force"])  # line 663
            _.createFile(1)  # line 664
            sos.commit("Added file1")  # line 665
        try:  # line 666
            sos.config(["set", "strict", "on"])  # line 666
        except SystemExit as E:  # line 667
            _.assertEqual(0, E.code)  # line 667
        makeRepo()  # line 668
        _.assertTrue(checkRepoFlag("strict", True))  # line 669
        try:  # line 670
            sos.config(["set", "strict", "off"])  # line 670
        except SystemExit as E:  # line 671
            _.assertEqual(0, E.code)  # line 671
        makeRepo()  # line 672
        _.assertTrue(checkRepoFlag("strict", False))  # line 673
        try:  # line 674
            sos.config(["set", "strict", "yes"])  # line 674
        except SystemExit as E:  # line 675
            _.assertEqual(0, E.code)  # line 675
        makeRepo()  # line 676
        _.assertTrue(checkRepoFlag("strict", True))  # line 677
        try:  # line 678
            sos.config(["set", "strict", "no"])  # line 678
        except SystemExit as E:  # line 679
            _.assertEqual(0, E.code)  # line 679
        makeRepo()  # line 680
        _.assertTrue(checkRepoFlag("strict", False))  # line 681
        try:  # line 682
            sos.config(["set", "strict", "1"])  # line 682
        except SystemExit as E:  # line 683
            _.assertEqual(0, E.code)  # line 683
        makeRepo()  # line 684
        _.assertTrue(checkRepoFlag("strict", True))  # line 685
        try:  # line 686
            sos.config(["set", "strict", "0"])  # line 686
        except SystemExit as E:  # line 687
            _.assertEqual(0, E.code)  # line 687
        makeRepo()  # line 688
        _.assertTrue(checkRepoFlag("strict", False))  # line 689
        try:  # line 690
            sos.config(["set", "strict", "true"])  # line 690
        except SystemExit as E:  # line 691
            _.assertEqual(0, E.code)  # line 691
        makeRepo()  # line 692
        _.assertTrue(checkRepoFlag("strict", True))  # line 693
        try:  # line 694
            sos.config(["set", "strict", "false"])  # line 694
        except SystemExit as E:  # line 695
            _.assertEqual(0, E.code)  # line 695
        makeRepo()  # line 696
        _.assertTrue(checkRepoFlag("strict", False))  # line 697
        try:  # line 698
            sos.config(["set", "strict", "enable"])  # line 698
        except SystemExit as E:  # line 699
            _.assertEqual(0, E.code)  # line 699
        makeRepo()  # line 700
        _.assertTrue(checkRepoFlag("strict", True))  # line 701
        try:  # line 702
            sos.config(["set", "strict", "disable"])  # line 702
        except SystemExit as E:  # line 703
            _.assertEqual(0, E.code)  # line 703
        makeRepo()  # line 704
        _.assertTrue(checkRepoFlag("strict", False))  # line 705
        try:  # line 706
            sos.config(["set", "strict", "enabled"])  # line 706
        except SystemExit as E:  # line 707
            _.assertEqual(0, E.code)  # line 707
        makeRepo()  # line 708
        _.assertTrue(checkRepoFlag("strict", True))  # line 709
        try:  # line 710
            sos.config(["set", "strict", "disabled"])  # line 710
        except SystemExit as E:  # line 711
            _.assertEqual(0, E.code)  # line 711
        makeRepo()  # line 712
        _.assertTrue(checkRepoFlag("strict", False))  # line 713
        try:  # line 714
            sos.config(["set", "strict", "nope"])  # line 714
            _.fail()  # line 714
        except SystemExit as E:  # line 715
            _.assertEqual(1, E.code)  # line 715

    def testLsSimple(_):  # line 717
        _.createFile(1)  # line 718
        _.createFile("foo")  # line 719
        _.createFile("ign1")  # line 720
        _.createFile("ign2")  # line 721
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 722
        try:  # define an ignore pattern  # line 723
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 723
        except SystemExit as E:  # line 724
            _.assertEqual(0, E.code)  # line 724
        try:  # additional ignore pattern  # line 725
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 725
        except SystemExit as E:  # line 726
            _.assertEqual(0, E.code)  # line 726
        try:  # define a list of ignore patterns  # line 727
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 727
        except SystemExit as E:  # line 728
            _.assertEqual(0, E.code)  # line 728
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 729
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 730
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 731
        _.assertInAny('··· file1', out)  # line 732
        _.assertInAny('··· ign1', out)  # line 733
        _.assertInAny('··· ign2', out)  # line 734
        try:  # line 735
            sos.config(["rm", "foo", "bar"])  # line 735
            _.fail()  # line 735
        except SystemExit as E:  # line 736
            _.assertEqual(1, E.code)  # line 736
        try:  # line 737
            sos.config(["rm", "ignores", "foo"])  # line 737
            _.fail()  # line 737
        except SystemExit as E:  # line 738
            _.assertEqual(1, E.code)  # line 738
        try:  # line 739
            sos.config(["rm", "ignores", "ign1"])  # line 739
        except SystemExit as E:  # line 740
            _.assertEqual(0, E.code)  # line 740
        try:  # remove ignore pattern  # line 741
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 741
        except SystemExit as E:  # line 742
            _.assertEqual(0, E.code)  # line 742
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 743
        _.assertInAny('··· ign1', out)  # line 744
        _.assertInAny('IGN ign2', out)  # line 745
        _.assertNotInAny('··· ign2', out)  # line 746

    def testWhitelist(_):  # line 748
# TODO test same for simple mode
        _.createFile(1)  # line 750
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 751
        sos.offline("xx", ["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 752
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 753
        sos.commit(options=["--force"])  # attempt to commit the file  # line 754
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 1))))  # only meta data, file1 was ignored  # line 755
        try:  # Exit because dirty  # line 756
            sos.online()  # Exit because dirty  # line 756
            _.fail()  # Exit because dirty  # line 756
        except:  # exception expected  # line 757
            pass  # exception expected  # line 757
        _.createFile("x2")  # add another change  # line 758
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 759
        try:  # force beyond dirty flag check  # line 760
            sos.online(["--force"])  # force beyond dirty flag check  # line 760
            _.fail()  # force beyond dirty flag check  # line 760
        except:  # line 761
            pass  # line 761
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 762
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 763

        _.createFile(1)  # line 765
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 766
        sos.offline("xx", ["--track"])  # line 767
        sos.add(".", "./file*")  # line 768
        sos.commit()  # should NOT ask for force here  # line 769
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 770

    def testRemove(_):  # line 772
        _.createFile(1, "x" * 100)  # line 773
        sos.offline("trunk")  # line 774
        try:  # line 775
            sos.delete("trunk")  # line 775
            _fail()  # line 775
        except:  # line 776
            pass  # line 776
        _.createFile(2, "y" * 10)  # line 777
        sos.branch("added")  # creates new branch, writes repo metadata, and therefore creates backup copy  # line 778
        sos.delete("trunk")  # line 779
        _.assertEqual(3, len(os.listdir("." + os.sep + sos.metaFolder)))  # meta data file, backup and "b1"  # line 780
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 781
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 782
        sos.branch("next")  # line 783
        _.createFile(3, "y" * 10)  # make a change  # line 784
        sos.delete("added", "--force")  # should succeed  # line 785

    def testUsage(_):  # line 787
        try:  # TODO expect sys.exit(0)  # line 788
            sos.usage()  # TODO expect sys.exit(0)  # line 788
            _.fail()  # TODO expect sys.exit(0)  # line 788
        except:  # line 789
            pass  # line 789
        try:  # line 790
            sos.usage(short=True)  # line 790
            _.fail()  # line 790
        except:  # line 791
            pass  # line 791

    def testOnlyExcept(_):  # line 793
        ''' Test blacklist glob rules. '''  # line 794
        sos.offline(options=["--track"])  # line 795
        _.createFile("a.1")  # line 796
        _.createFile("a.2")  # line 797
        _.createFile("b.1")  # line 798
        _.createFile("b.2")  # line 799
        sos.add(".", "./a.?")  # line 800
        sos.add(".", "./?.1", negative=True)  # line 801
        out = wrapChannels(lambda: sos.commit())  # line 802
        _.assertIn("ADD ./a.2", out)  # line 803
        _.assertNotIn("ADD ./a.1", out)  # line 804
        _.assertNotIn("ADD ./b.1", out)  # line 805
        _.assertNotIn("ADD ./b.2", out)  # line 806

    def testOnly(_):  # line 808
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 809
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 810
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 811
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 812
        sos.offline(options=["--track", "--strict"])  # line 813
        _.createFile(1)  # line 814
        _.createFile(2)  # line 815
        sos.add(".", "./file1")  # line 816
        sos.add(".", "./file2")  # line 817
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 818
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # only meta and file1  # line 819
        sos.commit()  # adds also file2  # line 820
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # only meta and file1  # line 821
        _.createFile(1, "cc")  # modify both files  # line 822
        _.createFile(2, "dd")  # line 823
        try:  # line 824
            sos.config(["set", "texttype", "file2"])  # line 824
        except SystemExit as E:  # line 825
            _.assertEqual(0, E.code)  # line 825
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))  # line 826
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 827
        _.assertTrue("./file2" in changes.modifications)  # line 828
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 829
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 830

    def testDiff(_):  # line 832
        try:  # manually mark this file as "textual"  # line 833
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 833
        except SystemExit as E:  # line 834
            _.assertEqual(0, E.code)  # line 834
        sos.offline(options=["--strict"])  # line 835
        _.createFile(1)  # line 836
        _.createFile(2)  # line 837
        sos.commit()  # line 838
        _.createFile(1, "sdfsdgfsdf")  # line 839
        _.createFile(2, "12343")  # line 840
        sos.commit()  # line 841
        _.createFile(1, "foobar")  # line 842
        _.createFile(3)  # line 843
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 844
        _.assertIn("ADD ./file3", out)  # line 845
        _.assertAllIn(["MOD ./file2", "DIF ./file1  <No newline>", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 846
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 847

    def testReorderRenameActions(_):  # line 849
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 850
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 851
        try:  # line 852
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 852
            _.fail()  # line 852
        except:  # line 853
            pass  # line 853

    def testMove(_):  # line 855
        sos.offline(options=["--strict", "--track"])  # line 856
        _.createFile(1)  # line 857
        sos.add(".", "./file?")  # line 858
# test source folder missing
        try:  # line 860
            sos.move("sub", "sub/file?", ".", "?file")  # line 860
            _.fail()  # line 860
        except:  # line 861
            pass  # line 861
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 863
        _.assertTrue(os.path.exists("sub"))  # line 864
        _.assertTrue(os.path.exists("sub/file1"))  # line 865
        _.assertFalse(os.path.exists("file1"))  # line 866
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 868
        _.assertTrue(os.path.exists("1file"))  # line 869
        _.assertFalse(os.path.exists("sub/file1"))  # line 870
# test nothing matches source pattern
        try:  # line 872
            sos.move(".", "a*", ".", "b*")  # line 872
            _.fail()  # line 872
        except:  # line 873
            pass  # line 873
        sos.add(".", "*")  # anything pattern  # line 874
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 875
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 875
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 875
        except:  # line 876
            pass  # line 876
# test rename no conflict
        _.createFile(1)  # line 878
        _.createFile(2)  # line 879
        _.createFile(3)  # line 880
        sos.add(".", "./file*")  # line 881
        try:  # define an ignore pattern  # line 882
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 882
        except SystemExit as E:  # line 883
            _.assertEqual(0, E.code)  # line 883
        try:  # line 884
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 884
        except SystemExit as E:  # line 885
            _.assertEqual(0, E.code)  # line 885
        sos.move(".", "./file*", ".", "fi*le")  # line 886
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 887
        _.assertFalse(os.path.exists("fi4le"))  # line 888
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 890
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 894
        sos.add(".", "./?a?b", ["--force"])  # line 895
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 896
        _.createFile("1a2b")  # should not be tracked  # line 897
        _.createFile("a1b2")  # should be tracked  # line 898
        sos.commit()  # line 899
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 900
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 901
        _.createFile("1a1b1")  # line 902
        _.createFile("1a1b2")  # line 903
        sos.add(".", "?a?b*")  # line 904
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 905
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 909
        sos.offline()  # line 910
        _.createFile(1)  # line 911
        os.mkdir(sos.branchFolder(0, 1))  # line 912
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.branchFolder(0, 1))  # line 913
        _.createFile(1)  # line 914
        try:  # should exit with error due to collision detection  # line 915
            sos.commit()  # should exit with error due to collision detection  # line 915
            _.fail()  # should exit with error due to collision detection  # line 915
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 916
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 916

    def testFindBase(_):  # line 918
        old = os.getcwd()  # line 919
        try:  # line 920
            os.mkdir("." + os.sep + ".git")  # line 921
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 922
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 923
            os.chdir("a" + os.sep + "b")  # line 924
            s, vcs, cmd = sos.findSosVcsBase()  # line 925
            _.assertIsNotNone(s)  # line 926
            _.assertIsNotNone(vcs)  # line 927
            _.assertEqual("git", cmd)  # line 928
        finally:  # line 929
            os.chdir(old)  # line 929

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail

# TODO test +++ --- in diff
# TODO test +01/-02/*..

if __name__ == '__main__':  # line 937
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 938
    c = configr.Configr("sos")  # line 939
    c.loadSettings()  # line 940
    if len(c.keys()) > 0:  # line 941
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 941
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 942
