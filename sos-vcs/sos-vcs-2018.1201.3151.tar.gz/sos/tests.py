#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xe1c07b28

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
from io import StringIO  # line 5
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
try:  # line 12
    import configr  # optional dependency  # line 13
    os.environ["TEST"] = testFolder  # needed to mock configr library calls in sos  # line 14
except:  # declare as undefined  # line 15
    configr = None  # declare as undefined  # line 15
import sos  # import of package, not file  # line 16
sos.defaults["defaultbranch"] = "trunk"  # because sos.main() is never called  # line 17

def sync() -> 'None':  # line 19
    if sys.version_info[:2] >= (3, 3):  # line 20
        os.sync()  # line 20


def determineFilesystemTimeResolution() -> 'float':  # line 23
    name = str(uuid.uuid4())  # type: str  # line 24
    with open(name, "w") as fd:  # create temporary file  # line 25
        fd.write("x")  # create temporary file  # line 25
    mt = os.stat(name).st_mtime  # type: float  # get current timestamp  # line 26
    while os.stat(name).st_mtime == mt:  # wait until timestamp modified  # line 27
        time.sleep(0.05)  # to avoid 0.00s bugs (came up some time for unknown reasons)  # line 28
        with open(name, "w") as fd:  # line 29
            fd.write("x")  # line 29
    mt, start, _count = os.stat(name).st_mtime, time.time(), 0  # line 30
    while os.stat(name).st_mtime == mt:  # now cound and measure time until modified again  # line 31
        time.sleep(0.05)  # line 32
        _count += 1  # line 33
        with open(name, "w") as fd:  # line 34
            fd.write("x")  # line 34
    os.unlink(name)  # line 35
    fsprecision = round(time.time() - start, 2)  # type: float  # line 36
    print("File system timestamp precision is %.2fs; wrote to the file %d times during that time" % (fsprecision, _count))  # line 37
    return fsprecision  # line 38


FS_PRECISION = determineFilesystemTimeResolution() * 1.05  # line 41


@_coconut_tco  # line 44
def debugTestRunner(post_mortem=None):  # line 44
    ''' Unittest runner doing post mortem debugging on failing tests. '''  # line 45
    import pdb  # line 46
    if post_mortem is None:  # line 47
        post_mortem = pdb.post_mortem  # line 47
    class DebugTestResult(unittest.TextTestResult):  # line 48
        def addError(self, test, err):  # called before tearDown()  # line 49
            traceback.print_exception(*err)  # line 50
            post_mortem(err[2])  # line 51
            super(DebugTestResult, self).addError(test, err)  # line 52
        def addFailure(self, test, err):  # line 53
            traceback.print_exception(*err)  # line 54
            post_mortem(err[2])  # line 55
            super(DebugTestResult, self).addFailure(test, err)  # line 56
    return _coconut_tail_call(unittest.TextTestRunner, resultclass=DebugTestResult)  # line 57

@_coconut_tco  # line 59
def wrapChannels(func: '_coconut.typing.Callable[..., Any]'):  # line 59
    ''' Wrap function call to capture and return strings emitted on stdout and stderr. '''  # line 60
    oldv, oldo, olde = sys.argv, sys.stdout, sys.stderr  # line 61
    buf = StringIO()  # line 62
    sys.stdout = sys.stderr = buf  # line 63
    handler = logging.StreamHandler(buf)  # line 64
    logging.getLogger().addHandler(handler)  # line 65
    try:  # capture output into buf  # line 66
        func()  # capture output into buf  # line 66
    except Exception as E:  # line 67
        buf.write(str(E) + "\n")  # line 67
        traceback.print_exc(file=buf)  # line 67
    except SystemExit as F:  # line 68
        buf.write("EXIT CODE %s" % F.code + "\n")  # line 68
        traceback.print_exc(file=buf)  # line 68
    logging.getLogger().removeHandler(handler)  # line 69
    sys.argv, sys.stdout, sys.stderr = oldv, oldo, olde  # line 70
    return _coconut_tail_call(buf.getvalue)  # line 71

def mockInput(datas: '_coconut.typing.Sequence[str]', func) -> 'Any':  # line 73
    with mock.patch("builtins.input", side_effect=datas):  # line 74
        return func()  # line 74

def setRepoFlag(name: 'str', value: 'bool') -> 'None':  # line 76
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 77
        flags, branches = json.loads(fd.read())  # line 77
    flags[name] = value  # line 78
    with open(sos.metaFolder + os.sep + sos.metaFile, "w") as fd:  # line 79
        fd.write(json.dumps((flags, branches)))  # line 79

def checkRepoFlag(name: 'str', flag: 'bool') -> 'bool':  # line 81
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 82
        flags, branches = json.loads(fd.read())  # line 82
    return name in flags and flags[name] == flag  # line 83


class Tests(unittest.TestCase):  # line 86
    ''' Entire test suite. '''  # line 87

    def setUp(_):  # line 89
        for entry in os.listdir(testFolder):  # cannot remove testFolder on Windows when using TortoiseSVN as VCS  # line 90
            resource = os.path.join(testFolder, entry)  # line 91
            shutil.rmtree(resource) if os.path.isdir(resource) else os.unlink(resource)  # line 92
        os.chdir(testFolder)  # line 93

    def assertAllIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]') -> 'None':  # line 95
        [_.assertIn(w, where) for w in what]  # line 95

    def assertAllNotIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]') -> 'None':  # line 97
        [_.assertNotIn(w, where) for w in what]  # line 97

    def assertInAll(_, what: 'str', where: '_coconut.typing.Sequence[str]') -> 'None':  # line 99
        [_.assertIn(what, w) for w in where]  # line 99

    def assertInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]') -> 'None':  # line 101
        _.assertTrue(any((what in w for w in where)))  # line 101

    def assertNotInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]') -> 'None':  # line 103
        _.assertFalse(any((what in w for w in where)))  # line 103

    def createFile(_, number: 'Union[int, str]', contents: 'str'="x" * 10, prefix: '_coconut.typing.Optional[str]'=None) -> 'None':  # line 105
        if prefix and not os.path.exists(prefix):  # line 106
            os.makedirs(prefix)  # line 106
        with open(("." if prefix is None else prefix) + os.sep + (("file%d" % number) if isinstance(number, int) else number), "wb") as fd:  # line 107
            fd.write(contents if isinstance(contents, bytes) else contents.encode("cp1252"))  # line 107

    def existsFile(_, number: 'Union[int, str]', expectedContents: 'bytes'=None) -> 'bool':  # line 109
        if not os.path.exists(("." + os.sep + "file%d" % number) if isinstance(number, int) else number):  # line 110
            return False  # line 110
        if expectedContents is None:  # line 111
            return True  # line 111
        with open(("." + os.sep + "file%d" % number) if isinstance(number, int) else number, "rb") as fd:  # line 112
            return fd.read() == expectedContents  # line 112

    def testAccessor(_):  # line 114
        a = sos.Accessor({"a": 1})  # line 115
        _.assertEqual((1, 1), (a["a"], a.a))  # line 116

    def testGetAnyOfmap(_):  # line 118
        _.assertEqual(2, sos.getAnyOfMap({"a": 1, "b": 2}, ["x", "b"]))  # line 119
        _.assertIsNone(sos.getAnyOfMap({"a": 1, "b": 2}, []))  # line 120

    def testAjoin(_):  # line 122
        _.assertEqual("a1a2", sos.ajoin("a", ["1", "2"]))  # line 123
        _.assertEqual("* a\n* b", sos.ajoin("* ", ["a", "b"], "\n"))  # line 124

    def testFindChanges(_):  # line 126
        m = sos.Metadata(os.getcwd())  # line 127
        try:  # line 128
            sos.config("set", ["texttype", "*"])  # line 128
        except SystemExit as E:  # line 129
            _.assertEqual(0, E.code)  # line 129
        try:  # line 130
            sos.config("set", ["ignores", "*.cfg;*.cfg.bak"])  # line 130
        except SystemExit as E:  # line 131
            _.assertEqual(0, E.code)  # line 131
        m = sos.Metadata(os.getcwd())  # reload from file system  # line 132
        m.loadBranches()  # line 133
        _.createFile(1, "1")  # line 134
        m.createBranch(0)  # line 135
        _.assertEqual(1, len(m.paths))  # line 136
        time.sleep(FS_PRECISION)  # time required by filesystem time resolution issues  # line 137
        _.createFile(1, "2")  # modify existing file  # line 138
        _.createFile(2, "2")  # add another file  # line 139
        m.loadCommit(0, 0)  # line 140
        changes = m.findChanges()  # detect time skew  # line 141
        _.assertEqual(1, len(changes.additions))  # line 142
        _.assertEqual(0, len(changes.deletions))  # line 143
        _.assertEqual(1, len(changes.modifications))  # line 144
        m.integrateChangeset(changes)  # line 145
        _.createFile(2, "12")  # modify file again  # line 146
        changes = m.findChanges(0, 1)  # by size, creating new commit  # line 147
        _.assertEqual(0, len(changes.additions))  # line 148
        _.assertEqual(0, len(changes.deletions))  # line 149
        _.assertEqual(1, len(changes.modifications))  # line 150
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1)))  # line 151
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # line 152

    def testDiffFunc(_):  # line 154
        a = {"./a": sos.PathInfo("", 0, 0, "")}  # line 155
        b = {"./a": sos.PathInfo("", 0, 0, "")}  # line 156
        changes = sos.diffPathSets(a, b)  # line 157
        _.assertEqual(0, len(changes.additions))  # line 158
        _.assertEqual(0, len(changes.deletions))  # line 159
        _.assertEqual(0, len(changes.modifications))  # line 160
        b = {"./a": sos.PathInfo("", 1, 0, "")}  # line 161
        changes = sos.diffPathSets(a, b)  # line 162
        _.assertEqual(0, len(changes.additions))  # line 163
        _.assertEqual(0, len(changes.deletions))  # line 164
        _.assertEqual(1, len(changes.modifications))  # line 165
        b = {}  # diff contains no entries -> no change  # line 166
        changes = sos.diffPathSets(a, b)  # line 167
        _.assertEqual(0, len(changes.additions))  # line 168
        _.assertEqual(0, len(changes.deletions))  # line 169
        _.assertEqual(0, len(changes.modifications))  # line 170
        b = {"./a": sos.PathInfo("", None, 1, "")}  # in diff marked as deleted  # line 171
        changes = sos.diffPathSets(a, b)  # line 172
        _.assertEqual(0, len(changes.additions))  # line 173
        _.assertEqual(1, len(changes.deletions))  # line 174
        _.assertEqual(0, len(changes.modifications))  # line 175
        b = {"./b": sos.PathInfo("", 1, 1, "")}  # line 176
        changes = sos.diffPathSets(a, b)  # line 177
        _.assertEqual(1, len(changes.additions))  # line 178
        _.assertEqual(0, len(changes.deletions))  # line 179
        _.assertEqual(0, len(changes.modifications))  # line 180
        a = {"./a": sos.PathInfo("", None, 0, "")}  # mark as deleted  # line 181
        b = {"./a": sos.PathInfo("", 1, 0, "")}  # re-added  # line 182
        changes = sos.diffPathSets(a, b)  # line 183
        _.assertEqual(1, len(changes.additions))  # line 184
        _.assertEqual(0, len(changes.deletions))  # line 185
        _.assertEqual(0, len(changes.modifications))  # line 186
        changes = sos.diffPathSets(b, a)  # line 187
        _.assertEqual(0, len(changes.additions))  # line 188
        _.assertEqual(1, len(changes.deletions))  # line 189
        _.assertEqual(0, len(changes.modifications))  # line 190

    def testPatternPaths(_):  # line 192
        sos.offline(options=["--track"])  # line 193
        os.mkdir("sub")  # line 194
        _.createFile("sub" + os.sep + "file1", "sdfsdf")  # line 195
        sos.add("sub", "sub/file?")  # line 196
        sos.commit("test")  # should pick up sub/file1 pattern  # line 197
        _.assertEqual(2, len(os.listdir(os.path.join(sos.metaFolder, "b0", "r1"))))  # sub/file1 was added  # line 198
        _.createFile(1)  # line 199
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 200
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 200
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 200
        except:  # line 201
            pass  # line 201

    def testTokenizeGlobPattern(_):  # line 203
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 204
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 205
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 206
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 207
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 208
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 209

    def testTokenizeGlobPatterns(_):  # line 211
        try:  # because number of literal strings differs  # line 212
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 212
            _.fail()  # because number of literal strings differs  # line 212
        except:  # line 213
            pass  # line 213
        try:  # because glob patterns differ  # line 214
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 214
            _.fail()  # because glob patterns differ  # line 214
        except:  # line 215
            pass  # line 215
        try:  # glob patterns differ, regardless of position  # line 216
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 216
            _.fail()  # glob patterns differ, regardless of position  # line 216
        except:  # line 217
            pass  # line 217
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 218
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 219
        try:  # succeeds, because glob patterns match (differ only in position)  # line 220
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 220
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 220
        except:  # line 221
            pass  # line 221

    def testConvertGlobFiles(_):  # line 223
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 224
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 225

    def testFolderRemove(_):  # line 227
        m = sos.Metadata(os.getcwd())  # line 228
        _.createFile(1)  # line 229
        _.createFile("a", prefix="sub")  # line 230
        sos.offline()  # line 231
        _.createFile(2)  # line 232
        os.unlink("sub" + os.sep + "a")  # line 233
        os.rmdir("sub")  # line 234
        changes = sos.changes()  # line 235
        _.assertEqual(1, len(changes.additions))  # line 236
        _.assertEqual(0, len(changes.modifications))  # line 237
        _.assertEqual(1, len(changes.deletions))  # line 238
        _.createFile("a", prefix="sub")  # line 239
        changes = sos.changes()  # line 240
        _.assertEqual(0, len(changes.deletions))  # line 241

    def testComputeSequentialPathSet(_):  # line 243
        os.makedirs(sos.branchFolder(0, 0))  # line 244
        os.makedirs(sos.branchFolder(0, 1))  # line 245
        os.makedirs(sos.branchFolder(0, 2))  # line 246
        os.makedirs(sos.branchFolder(0, 3))  # line 247
        os.makedirs(sos.branchFolder(0, 4))  # line 248
        m = sos.Metadata(os.getcwd())  # line 249
        m.branch = 0  # line 250
        m.commit = 2  # line 251
        m.saveBranches()  # line 252
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 253
        m.saveCommit(0, 0)  # initial  # line 254
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 255
        m.saveCommit(0, 1)  # mod  # line 256
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 257
        m.saveCommit(0, 2)  # add  # line 258
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 259
        m.saveCommit(0, 3)  # del  # line 260
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 261
        m.saveCommit(0, 4)  # readd  # line 262
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 263
        m.saveBranch(0)  # line 264
        m.computeSequentialPathSet(0, 4)  # line 265
        _.assertEqual(2, len(m.paths))  # line 266

    def testParseRevisionString(_):  # line 268
        m = sos.Metadata(os.getcwd())  # line 269
        m.branch = 1  # line 270
        m.commits = {0: 0, 1: 1, 2: 2}  # line 271
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 272
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 273
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 274
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 275
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 276
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 277
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 278

    def testOfflineEmpty(_):  # line 280
        os.mkdir("." + os.sep + sos.metaFolder)  # line 281
        try:  # line 282
            sos.offline("trunk")  # line 282
            _.fail()  # line 282
        except SystemExit as E:  # line 283
            _.assertEqual(1, E.code)  # line 283
        os.rmdir("." + os.sep + sos.metaFolder)  # line 284
        sos.offline("test")  # line 285
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 286
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 287
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 288
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 289
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 290
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file  # line 291

    def testOfflineWithFiles(_):  # line 293
        _.createFile(1, "x" * 100)  # line 294
        _.createFile(2)  # line 295
        sos.offline("test")  # line 296
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 297
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 298
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 299
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 300
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 301
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 302
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file plus branch base file copies  # line 303

    def testBranch(_):  # line 305
        _.createFile(1, "x" * 100)  # line 306
        _.createFile(2)  # line 307
        sos.offline("test")  # b0/r0  # line 308
        sos.branch("other")  # b1/r0  # line 309
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 310
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 311
        _.assertEqual(list(sorted(os.listdir(sos.branchFolder(0, 0)))), list(sorted(os.listdir(sos.branchFolder(1, 0)))))  # line 313
        _.createFile(1, "z")  # modify file  # line 315
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 316
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 317
        _.createFile(3, "z")  # line 319
        sos.branch("from_last_revision", ["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 320
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 321
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 326
        _.createFile(1, "x" * 100)  # line 327
        _.createFile(2)  # line 328
        sos.offline("test")  # line 329
        changes = sos.changes()  # line 330
        _.assertEqual(0, len(changes.additions))  # line 331
        _.assertEqual(0, len(changes.deletions))  # line 332
        _.assertEqual(0, len(changes.modifications))  # line 333
        _.createFile(1, "z")  # size change  # line 334
        changes = sos.changes()  # line 335
        _.assertEqual(0, len(changes.additions))  # line 336
        _.assertEqual(0, len(changes.deletions))  # line 337
        _.assertEqual(1, len(changes.modifications))  # line 338
        sos.commit("message")  # line 339
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 340
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.branchFolder(0, 1)))  # line 341
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # no further files, only the modified one  # line 342
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 343
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 344
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 345
        os.unlink("file2")  # line 346
        changes = sos.changes()  # line 347
        _.assertEqual(0, len(changes.additions))  # line 348
        _.assertEqual(1, len(changes.deletions))  # line 349
        _.assertEqual(1, len(changes.modifications))  # line 350
        sos.commit("modified")  # line 351
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # no additional files, only mentions in metadata  # line 352
        try:  # expecting Exit due to no changes  # line 353
            sos.commit("nothing")  # expecting Exit due to no changes  # line 353
            _.fail()  # expecting Exit due to no changes  # line 353
        except:  # line 354
            pass  # line 354

    def testGetBranch(_):  # line 356
        m = sos.Metadata(os.getcwd())  # line 357
        m.branch = 1  # current branch  # line 358
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 359
        _.assertEqual(27, m.getBranchByName(27))  # line 360
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 361
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 362
        _.assertIsNone(m.getBranchByName("unknown"))  # line 363
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 364
        _.assertEqual(13, m.getRevisionByName("13"))  # line 365
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 366
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 367

    def testTagging(_):  # line 369
        m = sos.Metadata(os.getcwd())  # line 370
        sos.offline()  # line 371
        _.createFile(111)  # line 372
        sos.commit("tag", ["--tag"])  # line 373
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 374
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 375
        _.createFile(2)  # line 376
        try:  # line 377
            sos.commit("tag")  # line 377
            _.fail()  # line 377
        except:  # line 378
            pass  # line 378
        sos.commit("tag-2", ["--tag"])  # line 379
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 380
        _.assertIn("TAG tag", out)  # line 381

    def testSwitch(_):  # line 383
        _.createFile(1, "x" * 100)  # line 384
        _.createFile(2, "y")  # line 385
        sos.offline("test")  # file1-2  in initial branch commit  # line 386
        sos.branch("second")  # file1-2  switch, having same files  # line 387
        sos.switch("0")  # no change  switch back, no problem  # line 388
        sos.switch("second")  # no change  # switch back, no problem  # line 389
        _.createFile(3, "y")  # generate a file  # line 390
        try:  # uncommited changes detected  # line 391
            sos.switch("test")  # uncommited changes detected  # line 391
            _.fail()  # uncommited changes detected  # line 391
        except SystemExit as E:  # line 392
            _.assertEqual(1, E.code)  # line 392
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 393
        sos.changes()  # line 394
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 395
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 396
        _.createFile("XXX")  # line 397
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 398
        _.assertIn("File tree has changes", out)  # line 399
        _.assertNotIn("File tree is unchanged", out)  # line 400
        _.assertIn("  * b00   'test'", out)  # line 401
        _.assertIn("    b01 'second'", out)  # line 402
        _.assertIn("(dirty)", out)  # one branch has commits  # line 403
        _.assertIn("(in sync)", out)  # the other doesn't  # line 404
        _.createFile(4, "xy")  # generate a file  # line 405
        sos.switch("second", "--force")  # avoids warning on uncommited changes, but keeps file4  # line 406
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 407
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 408
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 409
        sos.switch("test", "--force")  # should restore file1 and remove file3  # line 410
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 411
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 412

    def testAutoDetectVCS(_):  # line 414
        os.mkdir(".git")  # line 415
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 416
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 417
            meta = fd.read()  # line 417
        _.assertTrue("\"master\"" in meta)  # line 418
        os.rmdir(".git")  # line 419

    def testUpdate(_):  # line 421
        sos.offline("trunk")  # create initial branch b0/r0  # line 422
        _.createFile(1, "x" * 100)  # line 423
        sos.commit("second")  # create b0/r1  # line 424

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 426
        _.assertFalse(_.existsFile(1))  # line 427

        sos.update("/1")  # recreate file1  # line 429
        _.assertTrue(_.existsFile(1))  # line 430

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 432
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2)))  # line 433
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2, file=sos.metaFile)))  # line 434
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # only meta data file, no differential files  # line 435

        sos.update("/1")  # do nothing, as nothing has changed  # line 437
        _.assertTrue(_.existsFile(1))  # line 438

        _.createFile(2, "y" * 100)  # line 440
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", ["--force"])  # automatically including file 2 (as we are in simple mode)  # line 443
        _.assertTrue(_.existsFile(2))  # line 444
        sos.update("trunk", ["--add"])  # only add stuff  # line 445
        _.assertTrue(_.existsFile(2))  # line 446
        sos.update("trunk")  # nothing to do  # line 447
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 448

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 450
        _.createFile(10, theirs)  # line 451
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 452
        _.createFile(11, mine)  # line 453
        _.assertEqual(b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 454
        _.assertEqual(b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 455

    def testUpdate2(_):  # line 457
        _.createFile("test.txt", "x" * 10)  # line 458
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 459
        sos.branch("mod")  # line 460
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 461
        time.sleep(FS_PRECISION)  # line 462
        sos.commit("mod")  # create b0/r1  # line 463
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 464
        with open("test.txt", "rb") as fd:  # line 465
            _.assertEqual(b"x" * 10, fd.read())  # line 465
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 466
        with open("test.txt", "rb") as fd:  # line 467
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 467
        _.createFile("test.txt", "x" * 10)  # line 468
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 469
        with open("test.txt", "rb") as fd:  # line 470
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 470
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 471
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 472
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 473
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 474
        with open("test.txt", "rb") as fd:  # line 475
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 475

    def testIsTextType(_):  # line 477
        m = sos.Metadata(".")  # line 478
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 479
        m.c.bintype = ["*.md.confluence"]  # line 480
        _.assertTrue(m.isTextType("ab.txt"))  # line 481
        _.assertTrue(m.isTextType("./ab.txt"))  # line 482
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 483
        _.assertFalse(m.isTextType("bc/ab."))  # line 484
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 485
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 486
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 487
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 488

    def testEolDet(_):  # line 490
        ''' Check correct end-of-line detection. '''  # line 491
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 492
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 493
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 494
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 495
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 496
        _.assertIsNone(sos.eoldet(b""))  # line 497
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 498

    def testMerge(_):  # line 500
        ''' Check merge results depending on user options. '''  # line 501
        a = b"a\nb\ncc\nd"  # type: bytes  # line 502
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 503
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT))  # one-line block replacement using lineMerge  # line 504
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT))  # means insert changes from a into b, but don't replace  # line 505
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE))  # means insert changes from a into b, but don't replace  # line 506
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE))  # one-line block replacement using lineMerge  # line 507
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE))  # line 508
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH))  # keeps any changes in b  # line 509
        a = b"a\nb\ncc\nd"  # line 510
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 511
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT))  # multi-line block replacement  # line 512
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE))  # line 513
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH))  # keeps any changes in b  # line 514
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT))  # line 516
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE))  # line 517
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 519
        b = b"a\nc\ne"  # line 520
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)))  # line 521
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)))  # line 522
        a = b"a\nb\ne"  # intra-line merge  # line 523
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)))  # line 524
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)))  # line 525

    def testMergeEol(_):  # line 527
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 528
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb"))  # when in doubt, use "mine" CR-LF  # line 529
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True))  # line 530

    def testPickyMode(_):  # line 532
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 533
        sos.offline("trunk", ["--picky"])  # line 534
        changes = sos.changes()  # line 535
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 536
        sos.add(".", "./file?", ["--force"])  # line 537
        _.createFile(1, "aa")  # line 538
        sos.commit("First")  # add one file  # line 539
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 540
        _.createFile(2, "b")  # line 541
        try:  # add nothing, because picky  # line 542
            sos.commit("Second")  # add nothing, because picky  # line 542
        except:  # line 543
            pass  # line 543
        sos.add(".", "./file?")  # line 544
        sos.commit("Third")  # line 545
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # line 546
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 547
        _.assertIn("  * r2", out)  # line 548
        _.createFile(3, prefix="sub")  # line 549
        sos.add("sub", "sub/file?")  # line 550
        changes = sos.changes()  # line 551
        _.assertEqual(1, len(changes.additions))  # line 552
        _.assertTrue("sub/file3" in changes.additions)  # line 553

    def testTrackedSubfolder(_):  # line 555
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 556
        os.mkdir("." + os.sep + "sub")  # line 557
        sos.offline("trunk", ["--track"])  # line 558
        _.createFile(1, "x")  # line 559
        _.createFile(1, "x", prefix="sub")  # line 560
        sos.add(".", "./file?")  # add glob pattern to track  # line 561
        sos.commit("First")  # line 562
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 563
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 564
        sos.commit("Second")  # one new file + meta  # line 565
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 566
        os.unlink("file1")  # remove from basefolder  # line 567
        _.createFile(2, "y")  # line 568
        sos.remove(".", "sub/file?")  # line 569
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 570
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 570
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 570
        except:  # line 571
            pass  # line 571
        sos.commit("Third")  # line 572
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta  # line 573
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 576
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 581
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 582
        _.createFile(1)  # line 583
        _.createFile("a123a")  # untracked file "a123a"  # line 584
        sos.add(".", "./file?")  # add glob tracking pattern  # line 585
        sos.commit("second")  # versions "file1"  # line 586
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 587
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 588
        _.assertIn("  | ./file?", out)  # line 589

        _.createFile(2)  # untracked file "file2"  # line 591
        sos.commit("third")  # versions "file2"  # line 592
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta file  # line 593

        os.mkdir("." + os.sep + "sub")  # line 595
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 596
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 597
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 3))))  # meta file only, no other tracked path/file  # line 598

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 600
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 601
        sos.add(".", "./a*a")  # add tracking pattern  # line 602
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 603
        _.assertEqual(0, len(changes.modifications))  # line 604
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 605
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 606

        sos.commit("Second_2")  # line 608
        _.assertEqual(2, len(os.listdir(sos.branchFolder(1, 1))))  # "a123a" + meta file  # line 609
        _.existsFile(1, b"x" * 10)  # line 610
        _.existsFile(2, b"x" * 10)  # line 611

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 613
        _.existsFile(1, b"x" * 10)  # line 614
        _.existsFile("a123a", b"x" * 10)  # line 615

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 617
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 618
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 619

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 621
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 622
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 623
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 624
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 625
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 626
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 627
# TODO test switch --meta

    def testLsTracked(_):  # line 630
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 631
        _.createFile(1)  # line 632
        _.createFile("foo")  # line 633
        sos.add(".", "./file*")  # capture one file  # line 634
        sos.ls()  # line 635
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 636
        _.assertInAny("TRK file1  (file*)", out)  # line 637
        _.assertNotInAny("... file1  (file*)", out)  # line 638
        _.assertInAny("... foo", out)  # line 639
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 640
        _.assertInAny("TRK file*", out)  # line 641
        _.createFile("a", prefix="sub")  # line 642
        sos.add("sub", "sub/a")  # line 643
        sos.ls("sub")  # line 644
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 645

    def testLineMerge(_):  # line 647
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 648
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 649
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 650
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 651

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 653
        _.createFile(1)  # line 654
        sos.offline("master", options=["--force"])  # line 655
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 656
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 657
        _.assertTrue(_.existsFile(sos.branchFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 658
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 659
        _.createFile(2)  # line 660
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # without progress, the output goes to stderr via debug()  # line 661
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 662
        sos.commit("Added file2")  # line 663
        _.assertTrue(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 664
        _.assertFalse(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 665

    def testConfigVariations(_):  # line 667
        def makeRepo():  # line 668
            try:  # line 669
                os.unlink("file1")  # line 669
            except:  # line 670
                pass  # line 670
            sos.offline("master", options=["--plain", "--force"])  # line 671
            _.createFile(1)  # line 672
            sos.commit("Added file1")  # line 673
        try:  # line 674
            sos.config("set", ["strict", "on"])  # line 674
        except SystemExit as E:  # line 675
            _.assertEqual(0, E.code)  # line 675
        makeRepo()  # line 676
        _.assertTrue(checkRepoFlag("strict", True))  # line 677
        try:  # line 678
            sos.config("set", ["strict", "off"])  # line 678
        except SystemExit as E:  # line 679
            _.assertEqual(0, E.code)  # line 679
        makeRepo()  # line 680
        _.assertTrue(checkRepoFlag("strict", False))  # line 681
        try:  # line 682
            sos.config("set", ["strict", "yes"])  # line 682
        except SystemExit as E:  # line 683
            _.assertEqual(0, E.code)  # line 683
        makeRepo()  # line 684
        _.assertTrue(checkRepoFlag("strict", True))  # line 685
        try:  # line 686
            sos.config("set", ["strict", "no"])  # line 686
        except SystemExit as E:  # line 687
            _.assertEqual(0, E.code)  # line 687
        makeRepo()  # line 688
        _.assertTrue(checkRepoFlag("strict", False))  # line 689
        try:  # line 690
            sos.config("set", ["strict", "1"])  # line 690
        except SystemExit as E:  # line 691
            _.assertEqual(0, E.code)  # line 691
        makeRepo()  # line 692
        _.assertTrue(checkRepoFlag("strict", True))  # line 693
        try:  # line 694
            sos.config("set", ["strict", "0"])  # line 694
        except SystemExit as E:  # line 695
            _.assertEqual(0, E.code)  # line 695
        makeRepo()  # line 696
        _.assertTrue(checkRepoFlag("strict", False))  # line 697
        try:  # line 698
            sos.config("set", ["strict", "true"])  # line 698
        except SystemExit as E:  # line 699
            _.assertEqual(0, E.code)  # line 699
        makeRepo()  # line 700
        _.assertTrue(checkRepoFlag("strict", True))  # line 701
        try:  # line 702
            sos.config("set", ["strict", "false"])  # line 702
        except SystemExit as E:  # line 703
            _.assertEqual(0, E.code)  # line 703
        makeRepo()  # line 704
        _.assertTrue(checkRepoFlag("strict", False))  # line 705
        try:  # line 706
            sos.config("set", ["strict", "enable"])  # line 706
        except SystemExit as E:  # line 707
            _.assertEqual(0, E.code)  # line 707
        makeRepo()  # line 708
        _.assertTrue(checkRepoFlag("strict", True))  # line 709
        try:  # line 710
            sos.config("set", ["strict", "disable"])  # line 710
        except SystemExit as E:  # line 711
            _.assertEqual(0, E.code)  # line 711
        makeRepo()  # line 712
        _.assertTrue(checkRepoFlag("strict", False))  # line 713
        try:  # line 714
            sos.config("set", ["strict", "enabled"])  # line 714
        except SystemExit as E:  # line 715
            _.assertEqual(0, E.code)  # line 715
        makeRepo()  # line 716
        _.assertTrue(checkRepoFlag("strict", True))  # line 717
        try:  # line 718
            sos.config("set", ["strict", "disabled"])  # line 718
        except SystemExit as E:  # line 719
            _.assertEqual(0, E.code)  # line 719
        makeRepo()  # line 720
        _.assertTrue(checkRepoFlag("strict", False))  # line 721
        try:  # line 722
            sos.config("set", ["strict", "nope"])  # line 722
            _.fail()  # line 722
        except SystemExit as E:  # line 723
            _.assertEqual(1, E.code)  # line 723

    def testLsSimple(_):  # line 725
        _.createFile(1)  # line 726
        _.createFile("foo")  # line 727
        _.createFile("ign1")  # line 728
        _.createFile("ign2")  # line 729
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 730
        try:  # define an ignore pattern  # line 731
            sos.config("set", ["ignores", "ign1"])  # define an ignore pattern  # line 731
        except SystemExit as E:  # line 732
            _.assertEqual(0, E.code)  # line 732
        try:  # additional ignore pattern  # line 733
            sos.config("add", ["ignores", "ign2"])  # additional ignore pattern  # line 733
        except SystemExit as E:  # line 734
            _.assertEqual(0, E.code)  # line 734
        try:  # define a list of ignore patterns  # line 735
            sos.config("set", ["ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 735
        except SystemExit as E:  # line 736
            _.assertEqual(0, E.code)  # line 736
        out = wrapChannels(lambda: sos.config("show")).replace("\r", "")  # line 737
        _.assertIn("             ignores [user]    ['ign1', 'ign2']", out)  # line 738
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 739
        _.assertInAny('... file1', out)  # line 740
        _.assertInAny('... ign1', out)  # line 741
        _.assertInAny('... ign2', out)  # line 742
        try:  # line 743
            sos.config("rm", ["foo", "bar"])  # line 743
            _.fail()  # line 743
        except SystemExit as E:  # line 744
            _.assertEqual(1, E.code)  # line 744
        try:  # line 745
            sos.config("rm", ["ignores", "foo"])  # line 745
            _.fail()  # line 745
        except SystemExit as E:  # line 746
            _.assertEqual(1, E.code)  # line 746
        try:  # line 747
            sos.config("rm", ["ignores", "ign1"])  # line 747
        except SystemExit as E:  # line 748
            _.assertEqual(0, E.code)  # line 748
        try:  # remove ignore pattern  # line 749
            sos.config("unset", ["ignoresWhitelist"])  # remove ignore pattern  # line 749
        except SystemExit as E:  # line 750
            _.assertEqual(0, E.code)  # line 750
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 751
        _.assertInAny('... ign1', out)  # line 752
        _.assertInAny('IGN ign2', out)  # line 753
        _.assertNotInAny('... ign2', out)  # line 754

    def testWhitelist(_):  # line 756
# TODO test same for simple mode
        _.createFile(1)  # line 758
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 759
        sos.offline("xx", ["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 760
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 761
        sos.commit(options=["--force"])  # attempt to commit the file  # line 762
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 1))))  # only meta data, file1 was ignored  # line 763
        try:  # Exit because dirty  # line 764
            sos.online()  # Exit because dirty  # line 764
            _.fail()  # Exit because dirty  # line 764
        except:  # exception expected  # line 765
            pass  # exception expected  # line 765
        _.createFile("x2")  # add another change  # line 766
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 767
        try:  # force beyond dirty flag check  # line 768
            sos.online(["--force"])  # force beyond dirty flag check  # line 768
            _.fail()  # force beyond dirty flag check  # line 768
        except:  # line 769
            pass  # line 769
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 770
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 771

        _.createFile(1)  # line 773
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 774
        sos.offline("xx", ["--track"])  # line 775
        sos.add(".", "./file*")  # line 776
        sos.commit()  # should NOT ask for force here  # line 777
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 778

    def testRemove(_):  # line 780
        _.createFile(1, "x" * 100)  # line 781
        sos.offline("trunk")  # line 782
        try:  # line 783
            sos.delete("trunk")  # line 783
            _fail()  # line 783
        except:  # line 784
            pass  # line 784
        _.createFile(2, "y" * 10)  # line 785
        sos.branch("added")  # line 786
        sos.delete("trunk")  # line 787
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # meta data file and "b1"  # line 788
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 789
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 790
        sos.branch("next")  # line 791
        _.createFile(3, "y" * 10)  # make a change  # line 792
        sos.delete("added", "--force")  # should succeed  # line 793

    def testUsage(_):  # line 795
        try:  # TODO expect sys.exit(0)  # line 796
            sos.usage()  # TODO expect sys.exit(0)  # line 796
            _.fail()  # TODO expect sys.exit(0)  # line 796
        except:  # line 797
            pass  # line 797
        try:  # line 798
            sos.usage(short=True)  # line 798
            _.fail()  # line 798
        except:  # line 799
            pass  # line 799

    def testOnly(_):  # line 801
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 802
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 803
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 804
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 805
        sos.offline(os.getcwd(), ["--track", "--strict"])  # line 806
        _.createFile(1)  # line 807
        _.createFile(2)  # line 808
        sos.add(".", "./file1")  # line 809
        sos.add(".", "./file2")  # line 810
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 811
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # only meta and file1  # line 812
        sos.commit()  # adds also file2  # line 813
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # only meta and file1  # line 814
        _.createFile(1, "cc")  # modify both files  # line 815
        _.createFile(2, "dd")  # line 816
        try:  # line 817
            sos.config("set", ["texttype", "file2"])  # line 817
        except SystemExit as E:  # line 818
            _.assertEqual(0, E.code)  # line 818
        changes = sos.changes(excps=["./file1"])  # line 819
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 820
        _.assertTrue("./file2" in changes.modifications)  # line 821
        _.assertIn("DIF ./file2", wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 822
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 823

    def testDiff(_):  # line 825
        try:  # manually mark this file as "textual"  # line 826
            sos.config("set", ["texttype", "file1"])  # manually mark this file as "textual"  # line 826
        except SystemExit as E:  # line 827
            _.assertEqual(0, E.code)  # line 827
        sos.offline(options=["--strict"])  # line 828
        _.createFile(1)  # line 829
        _.createFile(2)  # line 830
        sos.commit()  # line 831
        _.createFile(1, "sdfsdgfsdf")  # line 832
        _.createFile(2, "12343")  # line 833
        sos.commit()  # line 834
        _.createFile(1, "foobar")  # line 835
        _.createFile(3)  # line 836
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 837
        _.assertIn("ADD ./file3", out)  # line 838
        _.assertAllIn(["MOD ./file2", "DIF ./file1", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 839
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 840

    def testReorderRenameActions(_):  # line 842
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 843
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 844
        try:  # line 845
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 845
            _.fail()  # line 845
        except:  # line 846
            pass  # line 846

    def testMove(_):  # line 848
        sos.offline(options=["--strict", "--track"])  # line 849
        _.createFile(1)  # line 850
        sos.add(".", "./file?")  # line 851
# test source folder missing
        try:  # line 853
            sos.move("sub", "sub/file?", ".", "?file")  # line 853
            _.fail()  # line 853
        except:  # line 854
            pass  # line 854
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 856
        _.assertTrue(os.path.exists("sub"))  # line 857
        _.assertTrue(os.path.exists("sub/file1"))  # line 858
        _.assertFalse(os.path.exists("file1"))  # line 859
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 861
        _.assertTrue(os.path.exists("1file"))  # line 862
        _.assertFalse(os.path.exists("sub/file1"))  # line 863
# test nothing matches source pattern
        try:  # line 865
            sos.move(".", "a*", ".", "b*")  # line 865
            _.fail()  # line 865
        except:  # line 866
            pass  # line 866
        sos.add(".", "*")  # anything pattern  # line 867
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 868
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 868
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 868
        except:  # line 869
            pass  # line 869
# test rename no conflict
        _.createFile(1)  # line 871
        _.createFile(2)  # line 872
        _.createFile(3)  # line 873
        sos.add(".", "./file*")  # line 874
        try:  # define an ignore pattern  # line 875
            sos.config("set", ["ignores", "file3;file4"])  # define an ignore pattern  # line 875
        except SystemExit as E:  # line 876
            _.assertEqual(0, E.code)  # line 876
        try:  # line 877
            sos.config("set", ["ignoresWhitelist", "file3"])  # line 877
        except SystemExit as E:  # line 878
            _.assertEqual(0, E.code)  # line 878
        sos.move(".", "./file*", ".", "fi*le")  # line 879
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 880
        _.assertFalse(os.path.exists("fi4le"))  # line 881
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 883
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 887
        sos.add(".", "./?a?b", ["--force"])  # line 888
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 889
        _.createFile("1a2b")  # should not be tracked  # line 890
        _.createFile("a1b2")  # should be tracked  # line 891
        sos.commit()  # line 892
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 893
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 894
        _.createFile("1a1b1")  # line 895
        _.createFile("1a1b2")  # line 896
        sos.add(".", "?a?b*")  # line 897
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 898
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 902
        sos.offline()  # line 903
        _.createFile(1)  # line 904
        os.mkdir(sos.branchFolder(0, 1))  # line 905
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.branchFolder(0, 1))  # line 906
        _.createFile(1)  # line 907
        try:  # should exit with error due to collision detection  # line 908
            sos.commit()  # should exit with error due to collision detection  # line 908
            _.fail()  # should exit with error due to collision detection  # line 908
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 909
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 909

    def testFindBase(_):  # line 911
        old = os.getcwd()  # line 912
        try:  # line 913
            os.mkdir("." + os.sep + ".git")  # line 914
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 915
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 916
            os.chdir("a" + os.sep + "b")  # line 917
            s, vcs, cmd = sos.findSosVcsBase()  # line 918
            _.assertIsNotNone(s)  # line 919
            _.assertIsNotNone(vcs)  # line 920
            _.assertEqual("git", cmd)  # line 921
        finally:  # line 922
            os.chdir(old)  # line 922

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail


if __name__ == '__main__':  # line 928
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 929
    if configr:  # line 931
        c = configr.Configr("sos")  # line 932
        c.loadSettings()  # line 932
        if len(c.keys()) > 0:  # line 933
            sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 933
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 934
