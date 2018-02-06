#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x52ab445d

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
    buf = TextIOWrapper(BufferedRandom(BytesIO(b"\0" * 10000)), encoding="utf-8")  # line 60
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

    def testComputeSequentialPathSet(_):  # line 209
        os.makedirs(sos.branchFolder(0, 0))  # line 210
        os.makedirs(sos.branchFolder(0, 1))  # line 211
        os.makedirs(sos.branchFolder(0, 2))  # line 212
        os.makedirs(sos.branchFolder(0, 3))  # line 213
        os.makedirs(sos.branchFolder(0, 4))  # line 214
        m = sos.Metadata(os.getcwd())  # line 215
        m.branch = 0  # line 216
        m.commit = 2  # line 217
        m.saveBranches()  # line 218
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 219
        m.saveCommit(0, 0)  # initial  # line 220
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 221
        m.saveCommit(0, 1)  # mod  # line 222
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 223
        m.saveCommit(0, 2)  # add  # line 224
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 225
        m.saveCommit(0, 3)  # del  # line 226
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")  # line 227
        m.saveCommit(0, 4)  # readd  # line 228
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 229
        m.saveBranch(0)  # line 230
        m.computeSequentialPathSet(0, 4)  # line 231
        _.assertEqual(2, len(m.paths))  # line 232

    def testParseRevisionString(_):  # line 234
        m = sos.Metadata(os.getcwd())  # line 235
        m.branch = 1  # line 236
        m.commits = {0: 0, 1: 1, 2: 2}  # line 237
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 238
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 239
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 240
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 241
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 242
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 243
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 244

    def testOfflineEmpty(_):  # line 246
        os.mkdir("." + os.sep + sos.metaFolder)  # line 247
        try:  # line 248
            sos.offline("trunk")  # line 248
            _.fail()  # line 248
        except SystemExit as E:  # line 249
            _.assertEqual(1, E.code)  # line 249
        os.rmdir("." + os.sep + sos.metaFolder)  # line 250
        sos.offline("test")  # line 251
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 252
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 253
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 254
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 255
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 256
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file  # line 257

    def testOfflineWithFiles(_):  # line 259
        _.createFile(1, "x" * 100)  # line 260
        _.createFile(2)  # line 261
        sos.offline("test")  # line 262
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 263
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 264
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 265
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 266
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 267
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 268
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file plus branch base file copies  # line 269

    def testBranch(_):  # line 271
        _.createFile(1, "x" * 100)  # line 272
        _.createFile(2)  # line 273
        sos.offline("test")  # b0/r0  # line 274
        sos.branch("other")  # b1/r0  # line 275
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 276
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 277
        _.assertEqual(list(sorted(os.listdir(sos.branchFolder(0, 0)))), list(sorted(os.listdir(sos.branchFolder(1, 0)))))  # line 279
        _.createFile(1, "z")  # modify file  # line 281
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 282
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 283
        _.createFile(3, "z")  # line 285
        sos.branch("from_last_revision", ["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 286
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 287
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 292
        _.createFile(1, "x" * 100)  # line 293
        _.createFile(2)  # line 294
        sos.offline("test")  # line 295
        changes = sos.changes()  # line 296
        _.assertEqual(0, len(changes.additions))  # line 297
        _.assertEqual(0, len(changes.deletions))  # line 298
        _.assertEqual(0, len(changes.modifications))  # line 299
        _.createFile(1, "z")  # size change  # line 300
        changes = sos.changes()  # line 301
        _.assertEqual(0, len(changes.additions))  # line 302
        _.assertEqual(0, len(changes.deletions))  # line 303
        _.assertEqual(1, len(changes.modifications))  # line 304
        sos.commit("message")  # line 305
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 306
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.branchFolder(0, 1)))  # line 307
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # no further files, only the modified one  # line 308
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 309
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 310
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 311
        os.unlink("file2")  # line 312
        changes = sos.changes()  # line 313
        _.assertEqual(0, len(changes.additions))  # line 314
        _.assertEqual(1, len(changes.deletions))  # line 315
        _.assertEqual(1, len(changes.modifications))  # line 316
        sos.commit("modified")  # line 317
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # no additional files, only mentions in metadata  # line 318
        try:  # expecting Exit due to no changes  # line 319
            sos.commit("nothing")  # expecting Exit due to no changes  # line 319
            _.fail()  # expecting Exit due to no changes  # line 319
        except:  # line 320
            pass  # line 320

    def testGetBranch(_):  # line 322
        m = sos.Metadata(os.getcwd())  # line 323
        m.branch = 1  # current branch  # line 324
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 325
        _.assertEqual(27, m.getBranchByName(27))  # line 326
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 327
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 328
        _.assertIsNone(m.getBranchByName("unknown"))  # line 329
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 330
        _.assertEqual(13, m.getRevisionByName("13"))  # line 331
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 332
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 333

    def testTagging(_):  # line 335
        m = sos.Metadata(os.getcwd())  # line 336
        sos.offline()  # line 337
        _.createFile(111)  # line 338
        sos.commit("tag", ["--tag"])  # line 339
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 340
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 341
        _.createFile(2)  # line 342
        try:  # line 343
            sos.commit("tag")  # line 343
            _.fail()  # line 343
        except:  # line 344
            pass  # line 344
        sos.commit("tag-2", ["--tag"])  # line 345
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 346
        _.assertIn("TAG tag", out)  # line 347

    def testSwitch(_):  # line 349
        _.createFile(1, "x" * 100)  # line 350
        _.createFile(2, "y")  # line 351
        sos.offline("test")  # file1-2  in initial branch commit  # line 352
        sos.branch("second")  # file1-2  switch, having same files  # line 353
        sos.switch("0")  # no change  switch back, no problem  # line 354
        sos.switch("second")  # no change  # switch back, no problem  # line 355
        _.createFile(3, "y")  # generate a file  # line 356
        try:  # uncommited changes detected  # line 357
            sos.switch("test")  # uncommited changes detected  # line 357
            _.fail()  # uncommited changes detected  # line 357
        except SystemExit as E:  # line 358
            _.assertEqual(1, E.code)  # line 358
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 359
        sos.changes()  # line 360
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 361
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 362
        _.createFile("XXX")  # line 363
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 364
        _.assertIn("File tree has changes", out)  # line 365
        _.assertNotIn("File tree is unchanged", out)  # line 366
        _.assertIn("  * b00   'test'", out)  # line 367
        _.assertIn("    b01 'second'", out)  # line 368
        _.assertIn("(dirty)", out)  # one branch has commits  # line 369
        _.assertIn("(in sync)", out)  # the other doesn't  # line 370
        _.createFile(4, "xy")  # generate a file  # line 371
        sos.switch("second", "--force")  # avoids warning on uncommited changes, but keeps file4  # line 372
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 373
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 374
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 375
        sos.switch("test", "--force")  # should restore file1 and remove file3  # line 376
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 377
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 378

    def testAutoDetectVCS(_):  # line 380
        os.mkdir(".git")  # line 381
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 382
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 383
            meta = fd.read()  # line 383
        _.assertTrue("\"master\"" in meta)  # line 384
        os.rmdir(".git")  # line 385

    def testUpdate(_):  # line 387
        sos.offline("trunk")  # create initial branch b0/r0  # line 388
        _.createFile(1, "x" * 100)  # line 389
        sos.commit("second")  # create b0/r1  # line 390

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 392
        _.assertFalse(_.existsFile(1))  # line 393

        sos.update("/1")  # recreate file1  # line 395
        _.assertTrue(_.existsFile(1))  # line 396

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 398
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2)))  # line 399
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2, file=sos.metaFile)))  # line 400
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # only meta data file, no differential files  # line 401

        sos.update("/1")  # do nothing, as nothing has changed  # line 403
        _.assertTrue(_.existsFile(1))  # line 404

        _.createFile(2, "y" * 100)  # line 406
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", ["--force"])  # automatically including file 2 (as we are in simple mode)  # line 409
        _.assertTrue(_.existsFile(2))  # line 410
        sos.update("trunk", ["--add"])  # only add stuff  # line 411
        _.assertTrue(_.existsFile(2))  # line 412
        sos.update("trunk")  # nothing to do  # line 413
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 414

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 416
        _.createFile(10, theirs)  # line 417
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 418
        _.createFile(11, mine)  # line 419
        _.assertEqual(b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 420
        _.assertEqual(b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 421

    def testUpdate2(_):  # line 423
        _.createFile("test.txt", "x" * 10)  # line 424
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 425
        sos.branch("mod")  # line 426
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 427
        time.sleep(FS_PRECISION)  # line 428
        sos.commit("mod")  # create b0/r1  # line 429
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 430
        with open("test.txt", "rb") as fd:  # line 431
            _.assertEqual(b"x" * 10, fd.read())  # line 431
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 432
        with open("test.txt", "rb") as fd:  # line 433
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 433
        _.createFile("test.txt", "x" * 10)  # line 434
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 435
        with open("test.txt", "rb") as fd:  # line 436
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 436
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 437
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 438
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 439
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 440
        with open("test.txt", "rb") as fd:  # line 441
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 441

    def testIsTextType(_):  # line 443
        m = sos.Metadata(".")  # line 444
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 445
        m.c.bintype = ["*.md.confluence"]  # line 446
        _.assertTrue(m.isTextType("ab.txt"))  # line 447
        _.assertTrue(m.isTextType("./ab.txt"))  # line 448
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 449
        _.assertFalse(m.isTextType("bc/ab."))  # line 450
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 451
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 452
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 453
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 454

    def testEolDet(_):  # line 456
        ''' Check correct end-of-line detection. '''  # line 457
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 458
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 459
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 460
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 461
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 462
        _.assertIsNone(sos.eoldet(b""))  # line 463
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 464

    def testMerge(_):  # line 466
        ''' Check merge results depending on user options. '''  # line 467
        a = b"a\nb\ncc\nd"  # type: bytes  # line 468
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 469
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT))  # one-line block replacement using lineMerge  # line 470
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT))  # means insert changes from a into b, but don't replace  # line 471
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE))  # means insert changes from a into b, but don't replace  # line 472
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE))  # one-line block replacement using lineMerge  # line 473
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE))  # line 474
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH))  # keeps any changes in b  # line 475
        a = b"a\nb\ncc\nd"  # line 476
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 477
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT))  # multi-line block replacement  # line 478
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE))  # line 479
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH))  # keeps any changes in b  # line 480
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT))  # line 482
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE))  # line 483
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 485
        b = b"a\nc\ne"  # line 486
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)))  # line 487
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)))  # line 488
        a = b"a\nb\ne"  # intra-line merge  # line 489
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)))  # line 490
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)))  # line 491

    def testMergeEol(_):  # line 493
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 494
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb"))  # when in doubt, use "mine" CR-LF  # line 495
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True))  # line 496

    def testPickyMode(_):  # line 498
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 499
        sos.offline("trunk", ["--picky"])  # line 500
        changes = sos.changes()  # line 501
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 502
        sos.add(".", "./file?", ["--force"])  # line 503
        _.createFile(1, "aa")  # line 504
        sos.commit("First")  # add one file  # line 505
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 506
        _.createFile(2, "b")  # line 507
        try:  # add nothing, because picky  # line 508
            sos.commit("Second")  # add nothing, because picky  # line 508
        except:  # line 509
            pass  # line 509
        sos.add(".", "./file?")  # line 510
        sos.commit("Third")  # line 511
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # line 512
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 513
        _.assertIn("  * r2", out)  # line 514
        _.createFile(3, prefix="sub")  # line 515
        sos.add("sub", "sub/file?")  # line 516
        changes = sos.changes()  # line 517
        _.assertEqual(1, len(changes.additions))  # line 518
        _.assertTrue("sub/file3" in changes.additions)  # line 519

    def testTrackedSubfolder(_):  # line 521
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 522
        os.mkdir("." + os.sep + "sub")  # line 523
        sos.offline("trunk", ["--track"])  # line 524
        _.createFile(1, "x")  # line 525
        _.createFile(1, "x", prefix="sub")  # line 526
        sos.add(".", "./file?")  # add glob pattern to track  # line 527
        sos.commit("First")  # line 528
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 529
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 530
        sos.commit("Second")  # one new file + meta  # line 531
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 532
        os.unlink("file1")  # remove from basefolder  # line 533
        _.createFile(2, "y")  # line 534
        sos.remove(".", "sub/file?")  # line 535
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 536
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 536
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 536
        except:  # line 537
            pass  # line 537
        sos.commit("Third")  # line 538
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta  # line 539
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 542
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 547
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 548
        _.createFile(1)  # line 549
        _.createFile("a123a")  # untracked file "a123a"  # line 550
        sos.add(".", "./file?")  # add glob tracking pattern  # line 551
        sos.commit("second")  # versions "file1"  # line 552
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 553
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 554
        _.assertIn("  | ./file?", out)  # line 555

        _.createFile(2)  # untracked file "file2"  # line 557
        sos.commit("third")  # versions "file2"  # line 558
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta file  # line 559

        os.mkdir("." + os.sep + "sub")  # line 561
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 562
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 563
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 3))))  # meta file only, no other tracked path/file  # line 564

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 566
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 567
        sos.add(".", "./a*a")  # add tracking pattern  # line 568
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 569
        _.assertEqual(0, len(changes.modifications))  # line 570
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 571
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 572

        sos.commit("Second_2")  # line 574
        _.assertEqual(2, len(os.listdir(sos.branchFolder(1, 1))))  # "a123a" + meta file  # line 575
        _.existsFile(1, b"x" * 10)  # line 576
        _.existsFile(2, b"x" * 10)  # line 577

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 579
        _.existsFile(1, b"x" * 10)  # line 580
        _.existsFile("a123a", b"x" * 10)  # line 581

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 583
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 584
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 585

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 587
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 588
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 589
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 590
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 591
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 592
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 593
# TODO test switch --meta

    def testLsTracked(_):  # line 596
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 597
        _.createFile(1)  # line 598
        _.createFile("foo")  # line 599
        sos.add(".", "./file*")  # capture one file  # line 600
        sos.ls()  # line 601
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 602
        _.assertInAny("TRK file1  (file*)", out)  # line 603
        _.assertNotInAny("... file1  (file*)", out)  # line 604
        _.assertInAny("... foo", out)  # line 605
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 606
        _.assertInAny("TRK file*", out)  # line 607
        _.createFile("a", prefix="sub")  # line 608
        sos.add("sub", "sub/a")  # line 609
        sos.ls("sub")  # line 610
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 611

    def testLineMerge(_):  # line 613
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 614
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 615
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 616
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 617

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 619
        _.createFile(1)  # line 620
        sos.offline("master", options=["--force"])  # line 621
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 622
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 623
        _.assertTrue(_.existsFile(sos.branchFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 624
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 625
        _.createFile(2)  # line 626
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 627
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 628
        _.assertTrue(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 629
        _.assertFalse(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 630

    def testLocalConfig(_):  # line 632
        sos.offline("bla", options=[])  # line 633
        try:  # line 634
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 634
        except SystemExit as E:  # line 635
            _.assertEqual(0, E.code)  # line 635
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 636

    def testConfigVariations(_):  # line 638
        def makeRepo():  # line 639
            try:  # line 640
                os.unlink("file1")  # line 640
            except:  # line 641
                pass  # line 641
            sos.offline("master", options=["--force"])  # line 642
            _.createFile(1)  # line 643
            sos.commit("Added file1")  # line 644
        try:  # line 645
            sos.config(["set", "strict", "on"])  # line 645
        except SystemExit as E:  # line 646
            _.assertEqual(0, E.code)  # line 646
        makeRepo()  # line 647
        _.assertTrue(checkRepoFlag("strict", True))  # line 648
        try:  # line 649
            sos.config(["set", "strict", "off"])  # line 649
        except SystemExit as E:  # line 650
            _.assertEqual(0, E.code)  # line 650
        makeRepo()  # line 651
        _.assertTrue(checkRepoFlag("strict", False))  # line 652
        try:  # line 653
            sos.config(["set", "strict", "yes"])  # line 653
        except SystemExit as E:  # line 654
            _.assertEqual(0, E.code)  # line 654
        makeRepo()  # line 655
        _.assertTrue(checkRepoFlag("strict", True))  # line 656
        try:  # line 657
            sos.config(["set", "strict", "no"])  # line 657
        except SystemExit as E:  # line 658
            _.assertEqual(0, E.code)  # line 658
        makeRepo()  # line 659
        _.assertTrue(checkRepoFlag("strict", False))  # line 660
        try:  # line 661
            sos.config(["set", "strict", "1"])  # line 661
        except SystemExit as E:  # line 662
            _.assertEqual(0, E.code)  # line 662
        makeRepo()  # line 663
        _.assertTrue(checkRepoFlag("strict", True))  # line 664
        try:  # line 665
            sos.config(["set", "strict", "0"])  # line 665
        except SystemExit as E:  # line 666
            _.assertEqual(0, E.code)  # line 666
        makeRepo()  # line 667
        _.assertTrue(checkRepoFlag("strict", False))  # line 668
        try:  # line 669
            sos.config(["set", "strict", "true"])  # line 669
        except SystemExit as E:  # line 670
            _.assertEqual(0, E.code)  # line 670
        makeRepo()  # line 671
        _.assertTrue(checkRepoFlag("strict", True))  # line 672
        try:  # line 673
            sos.config(["set", "strict", "false"])  # line 673
        except SystemExit as E:  # line 674
            _.assertEqual(0, E.code)  # line 674
        makeRepo()  # line 675
        _.assertTrue(checkRepoFlag("strict", False))  # line 676
        try:  # line 677
            sos.config(["set", "strict", "enable"])  # line 677
        except SystemExit as E:  # line 678
            _.assertEqual(0, E.code)  # line 678
        makeRepo()  # line 679
        _.assertTrue(checkRepoFlag("strict", True))  # line 680
        try:  # line 681
            sos.config(["set", "strict", "disable"])  # line 681
        except SystemExit as E:  # line 682
            _.assertEqual(0, E.code)  # line 682
        makeRepo()  # line 683
        _.assertTrue(checkRepoFlag("strict", False))  # line 684
        try:  # line 685
            sos.config(["set", "strict", "enabled"])  # line 685
        except SystemExit as E:  # line 686
            _.assertEqual(0, E.code)  # line 686
        makeRepo()  # line 687
        _.assertTrue(checkRepoFlag("strict", True))  # line 688
        try:  # line 689
            sos.config(["set", "strict", "disabled"])  # line 689
        except SystemExit as E:  # line 690
            _.assertEqual(0, E.code)  # line 690
        makeRepo()  # line 691
        _.assertTrue(checkRepoFlag("strict", False))  # line 692
        try:  # line 693
            sos.config(["set", "strict", "nope"])  # line 693
            _.fail()  # line 693
        except SystemExit as E:  # line 694
            _.assertEqual(1, E.code)  # line 694

    def testLsSimple(_):  # line 696
        _.createFile(1)  # line 697
        _.createFile("foo")  # line 698
        _.createFile("ign1")  # line 699
        _.createFile("ign2")  # line 700
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 701
        try:  # define an ignore pattern  # line 702
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 702
        except SystemExit as E:  # line 703
            _.assertEqual(0, E.code)  # line 703
        try:  # additional ignore pattern  # line 704
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 704
        except SystemExit as E:  # line 705
            _.assertEqual(0, E.code)  # line 705
        try:  # define a list of ignore patterns  # line 706
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 706
        except SystemExit as E:  # line 707
            _.assertEqual(0, E.code)  # line 707
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 708
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 709
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 710
        _.assertInAny('... file1', out)  # line 711
        _.assertInAny('... ign1', out)  # line 712
        _.assertInAny('... ign2', out)  # line 713
        try:  # line 714
            sos.config(["rm", "foo", "bar"])  # line 714
            _.fail()  # line 714
        except SystemExit as E:  # line 715
            _.assertEqual(1, E.code)  # line 715
        try:  # line 716
            sos.config(["rm", "ignores", "foo"])  # line 716
            _.fail()  # line 716
        except SystemExit as E:  # line 717
            _.assertEqual(1, E.code)  # line 717
        try:  # line 718
            sos.config(["rm", "ignores", "ign1"])  # line 718
        except SystemExit as E:  # line 719
            _.assertEqual(0, E.code)  # line 719
        try:  # remove ignore pattern  # line 720
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 720
        except SystemExit as E:  # line 721
            _.assertEqual(0, E.code)  # line 721
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 722
        _.assertInAny('... ign1', out)  # line 723
        _.assertInAny('IGN ign2', out)  # line 724
        _.assertNotInAny('... ign2', out)  # line 725

    def testWhitelist(_):  # line 727
# TODO test same for simple mode
        _.createFile(1)  # line 729
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 730
        sos.offline("xx", ["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 731
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 732
        sos.commit(options=["--force"])  # attempt to commit the file  # line 733
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 1))))  # only meta data, file1 was ignored  # line 734
        try:  # Exit because dirty  # line 735
            sos.online()  # Exit because dirty  # line 735
            _.fail()  # Exit because dirty  # line 735
        except:  # exception expected  # line 736
            pass  # exception expected  # line 736
        _.createFile("x2")  # add another change  # line 737
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 738
        try:  # force beyond dirty flag check  # line 739
            sos.online(["--force"])  # force beyond dirty flag check  # line 739
            _.fail()  # force beyond dirty flag check  # line 739
        except:  # line 740
            pass  # line 740
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 741
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 742

        _.createFile(1)  # line 744
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 745
        sos.offline("xx", ["--track"])  # line 746
        sos.add(".", "./file*")  # line 747
        sos.commit()  # should NOT ask for force here  # line 748
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 749

    def testRemove(_):  # line 751
        _.createFile(1, "x" * 100)  # line 752
        sos.offline("trunk")  # line 753
        try:  # line 754
            sos.delete("trunk")  # line 754
            _fail()  # line 754
        except:  # line 755
            pass  # line 755
        _.createFile(2, "y" * 10)  # line 756
        sos.branch("added")  # line 757
        sos.delete("trunk")  # line 758
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # meta data file and "b1"  # line 759
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 760
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 761
        sos.branch("next")  # line 762
        _.createFile(3, "y" * 10)  # make a change  # line 763
        sos.delete("added", "--force")  # should succeed  # line 764

    def testUsage(_):  # line 766
        try:  # TODO expect sys.exit(0)  # line 767
            sos.usage()  # TODO expect sys.exit(0)  # line 767
            _.fail()  # TODO expect sys.exit(0)  # line 767
        except:  # line 768
            pass  # line 768
        try:  # line 769
            sos.usage(short=True)  # line 769
            _.fail()  # line 769
        except:  # line 770
            pass  # line 770

    def testOnly(_):  # line 772
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 773
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 774
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 775
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 776
        sos.offline(os.getcwd(), ["--track", "--strict"])  # line 777
        _.createFile(1)  # line 778
        _.createFile(2)  # line 779
        sos.add(".", "./file1")  # line 780
        sos.add(".", "./file2")  # line 781
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 782
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # only meta and file1  # line 783
        sos.commit()  # adds also file2  # line 784
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # only meta and file1  # line 785
        _.createFile(1, "cc")  # modify both files  # line 786
        _.createFile(2, "dd")  # line 787
        try:  # line 788
            sos.config(["set", "texttype", "file2"])  # line 788
        except SystemExit as E:  # line 789
            _.assertEqual(0, E.code)  # line 789
        changes = sos.changes(excps=["./file1"])  # line 790
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 791
        _.assertTrue("./file2" in changes.modifications)  # line 792
        _.assertIn("DIF ./file2", wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 793
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 794

    def testDiff(_):  # line 796
        try:  # manually mark this file as "textual"  # line 797
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 797
        except SystemExit as E:  # line 798
            _.assertEqual(0, E.code)  # line 798
        sos.offline(options=["--strict"])  # line 799
        _.createFile(1)  # line 800
        _.createFile(2)  # line 801
        sos.commit()  # line 802
        _.createFile(1, "sdfsdgfsdf")  # line 803
        _.createFile(2, "12343")  # line 804
        sos.commit()  # line 805
        _.createFile(1, "foobar")  # line 806
        _.createFile(3)  # line 807
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 808
        _.assertIn("ADD ./file3", out)  # line 809
        _.assertAllIn(["MOD ./file2", "DIF ./file1", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 810
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 811

    def testReorderRenameActions(_):  # line 813
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 814
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 815
        try:  # line 816
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 816
            _.fail()  # line 816
        except:  # line 817
            pass  # line 817

    def testMove(_):  # line 819
        sos.offline(options=["--strict", "--track"])  # line 820
        _.createFile(1)  # line 821
        sos.add(".", "./file?")  # line 822
# test source folder missing
        try:  # line 824
            sos.move("sub", "sub/file?", ".", "?file")  # line 824
            _.fail()  # line 824
        except:  # line 825
            pass  # line 825
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 827
        _.assertTrue(os.path.exists("sub"))  # line 828
        _.assertTrue(os.path.exists("sub/file1"))  # line 829
        _.assertFalse(os.path.exists("file1"))  # line 830
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 832
        _.assertTrue(os.path.exists("1file"))  # line 833
        _.assertFalse(os.path.exists("sub/file1"))  # line 834
# test nothing matches source pattern
        try:  # line 836
            sos.move(".", "a*", ".", "b*")  # line 836
            _.fail()  # line 836
        except:  # line 837
            pass  # line 837
        sos.add(".", "*")  # anything pattern  # line 838
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 839
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 839
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 839
        except:  # line 840
            pass  # line 840
# test rename no conflict
        _.createFile(1)  # line 842
        _.createFile(2)  # line 843
        _.createFile(3)  # line 844
        sos.add(".", "./file*")  # line 845
        try:  # define an ignore pattern  # line 846
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 846
        except SystemExit as E:  # line 847
            _.assertEqual(0, E.code)  # line 847
        try:  # line 848
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 848
        except SystemExit as E:  # line 849
            _.assertEqual(0, E.code)  # line 849
        sos.move(".", "./file*", ".", "fi*le")  # line 850
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 851
        _.assertFalse(os.path.exists("fi4le"))  # line 852
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 854
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 858
        sos.add(".", "./?a?b", ["--force"])  # line 859
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 860
        _.createFile("1a2b")  # should not be tracked  # line 861
        _.createFile("a1b2")  # should be tracked  # line 862
        sos.commit()  # line 863
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 864
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 865
        _.createFile("1a1b1")  # line 866
        _.createFile("1a1b2")  # line 867
        sos.add(".", "?a?b*")  # line 868
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 869
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 873
        sos.offline()  # line 874
        _.createFile(1)  # line 875
        os.mkdir(sos.branchFolder(0, 1))  # line 876
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.branchFolder(0, 1))  # line 877
        _.createFile(1)  # line 878
        try:  # should exit with error due to collision detection  # line 879
            sos.commit()  # should exit with error due to collision detection  # line 879
            _.fail()  # should exit with error due to collision detection  # line 879
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 880
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 880

    def testFindBase(_):  # line 882
        old = os.getcwd()  # line 883
        try:  # line 884
            os.mkdir("." + os.sep + ".git")  # line 885
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 886
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 887
            os.chdir("a" + os.sep + "b")  # line 888
            s, vcs, cmd = sos.findSosVcsBase()  # line 889
            _.assertIsNotNone(s)  # line 890
            _.assertIsNotNone(vcs)  # line 891
            _.assertEqual("git", cmd)  # line 892
        finally:  # line 893
            os.chdir(old)  # line 893

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail


if __name__ == '__main__':  # line 899
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 900
    c = configr.Configr("sos")  # line 901
    c.loadSettings()  # line 902
    if len(c.keys()) > 0:  # line 903
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 903
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 904
