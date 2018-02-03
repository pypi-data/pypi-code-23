#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x438c8471

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
        def addError(self, test, err):  # called before tearDown()  # line 47
            traceback.print_exception(*err)  # line 48
            post_mortem(err[2])  # line 49
            super(DebugTestResult, self).addError(test, err)  # line 50
        def addFailure(self, test, err):  # line 51
            traceback.print_exception(*err)  # line 52
            post_mortem(err[2])  # line 53
            super(DebugTestResult, self).addFailure(test, err)  # line 54
    return _coconut_tail_call(unittest.TextTestRunner, resultclass=DebugTestResult)  # line 55

@_coconut_tco  # line 57
def wrapChannels(func: '_coconut.typing.Callable[..., Any]'):  # line 57
    ''' Wrap function call to capture and return strings emitted on stdout and stderr. '''  # line 58
    oldv, oldo, olde = sys.argv, sys.stdout, sys.stderr  # line 59
    buf = StringIO()  # type: StringIO  # line 60
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
    sys.argv, sys.stdout, sys.stderr = oldv, oldo, olde  # line 68
    return _coconut_tail_call(buf.getvalue)  # line 69

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


    def assertAllIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]'):  # line 94
        for w in what:  # line 95
            _.assertIn(w, where)  # line 95

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
        try:  # line 132
            sos.config(["set", "ignores", "*.cfg;*.cfg.bak"])  # line 132
        except SystemExit as E:  # line 133
            _.assertEqual(0, E.code)  # line 133
        m = sos.Metadata(os.getcwd())  # reload from file system  # line 134
        m.loadBranches()  # line 135
        _.createFile(1, "1")  # line 136
        m.createBranch(0)  # line 137
        _.assertEqual(1, len(m.paths))  # line 138
        time.sleep(FS_PRECISION)  # time required by filesystem time resolution issues  # line 139
        _.createFile(1, "2")  # modify existing file  # line 140
        _.createFile(2, "2")  # add another file  # line 141
        m.loadCommit(0, 0)  # line 142
        changes = m.findChanges()  # detect time skew  # line 143
        _.assertEqual(1, len(changes.additions))  # line 144
        _.assertEqual(0, len(changes.deletions))  # line 145
        _.assertEqual(1, len(changes.modifications))  # line 146
        m.integrateChangeset(changes)  # line 147
        _.createFile(2, "12")  # modify file again  # line 148
        changes = m.findChanges(0, 1)  # by size, creating new commit  # line 149
        _.assertEqual(0, len(changes.additions))  # line 150
        _.assertEqual(0, len(changes.deletions))  # line 151
        _.assertEqual(1, len(changes.modifications))  # line 152
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1)))  # line 153
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # line 154

    def testDiffFunc(_):  # line 156
        a = {"./a": sos.PathInfo("", 0, 0, "")}  # line 157
        b = {"./a": sos.PathInfo("", 0, 0, "")}  # line 158
        changes = sos.diffPathSets(a, b)  # line 159
        _.assertEqual(0, len(changes.additions))  # line 160
        _.assertEqual(0, len(changes.deletions))  # line 161
        _.assertEqual(0, len(changes.modifications))  # line 162
        b = {"./a": sos.PathInfo("", 1, 0, "")}  # line 163
        changes = sos.diffPathSets(a, b)  # line 164
        _.assertEqual(0, len(changes.additions))  # line 165
        _.assertEqual(0, len(changes.deletions))  # line 166
        _.assertEqual(1, len(changes.modifications))  # line 167
        b = {}  # diff contains no entries -> no change  # line 168
        changes = sos.diffPathSets(a, b)  # line 169
        _.assertEqual(0, len(changes.additions))  # line 170
        _.assertEqual(0, len(changes.deletions))  # line 171
        _.assertEqual(0, len(changes.modifications))  # line 172
        b = {"./a": sos.PathInfo("", None, 1, "")}  # in diff marked as deleted  # line 173
        changes = sos.diffPathSets(a, b)  # line 174
        _.assertEqual(0, len(changes.additions))  # line 175
        _.assertEqual(1, len(changes.deletions))  # line 176
        _.assertEqual(0, len(changes.modifications))  # line 177
        b = {"./b": sos.PathInfo("", 1, 1, "")}  # line 178
        changes = sos.diffPathSets(a, b)  # line 179
        _.assertEqual(1, len(changes.additions))  # line 180
        _.assertEqual(0, len(changes.deletions))  # line 181
        _.assertEqual(0, len(changes.modifications))  # line 182
        a = {"./a": sos.PathInfo("", None, 0, "")}  # mark as deleted  # line 183
        b = {"./a": sos.PathInfo("", 1, 0, "")}  # re-added  # line 184
        changes = sos.diffPathSets(a, b)  # line 185
        _.assertEqual(1, len(changes.additions))  # line 186
        _.assertEqual(0, len(changes.deletions))  # line 187
        _.assertEqual(0, len(changes.modifications))  # line 188
        changes = sos.diffPathSets(b, a)  # line 189
        _.assertEqual(0, len(changes.additions))  # line 190
        _.assertEqual(1, len(changes.deletions))  # line 191
        _.assertEqual(0, len(changes.modifications))  # line 192

    def testPatternPaths(_):  # line 194
        sos.offline(options=["--track"])  # line 195
        os.mkdir("sub")  # line 196
        _.createFile("sub" + os.sep + "file1", "sdfsdf")  # line 197
        sos.add("sub", "sub/file?")  # line 198
        sos.commit("test")  # should pick up sub/file1 pattern  # line 199
        _.assertEqual(2, len(os.listdir(os.path.join(sos.metaFolder, "b0", "r1"))))  # sub/file1 was added  # line 200
        _.createFile(1)  # line 201
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 202
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 202
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 202
        except:  # line 203
            pass  # line 203

    def testTokenizeGlobPattern(_):  # line 205
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 206
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 207
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 208
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 209
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 210
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 211

    def testTokenizeGlobPatterns(_):  # line 213
        try:  # because number of literal strings differs  # line 214
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 214
            _.fail()  # because number of literal strings differs  # line 214
        except:  # line 215
            pass  # line 215
        try:  # because glob patterns differ  # line 216
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 216
            _.fail()  # because glob patterns differ  # line 216
        except:  # line 217
            pass  # line 217
        try:  # glob patterns differ, regardless of position  # line 218
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 218
            _.fail()  # glob patterns differ, regardless of position  # line 218
        except:  # line 219
            pass  # line 219
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 220
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 221
        try:  # succeeds, because glob patterns match (differ only in position)  # line 222
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 222
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 222
        except:  # line 223
            pass  # line 223

    def testConvertGlobFiles(_):  # line 225
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 226
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 227

    def testFolderRemove(_):  # line 229
        m = sos.Metadata(os.getcwd())  # line 230
        _.createFile(1)  # line 231
        _.createFile("a", prefix="sub")  # line 232
        sos.offline()  # line 233
        _.createFile(2)  # line 234
        os.unlink("sub" + os.sep + "a")  # line 235
        os.rmdir("sub")  # line 236
        changes = sos.changes()  # line 237
        _.assertEqual(1, len(changes.additions))  # line 238
        _.assertEqual(0, len(changes.modifications))  # line 239
        _.assertEqual(1, len(changes.deletions))  # line 240
        _.createFile("a", prefix="sub")  # line 241
        changes = sos.changes()  # line 242
        _.assertEqual(0, len(changes.deletions))  # line 243

    def testComputeSequentialPathSet(_):  # line 245
        os.makedirs(sos.branchFolder(0, 0))  # line 246
        os.makedirs(sos.branchFolder(0, 1))  # line 247
        os.makedirs(sos.branchFolder(0, 2))  # line 248
        os.makedirs(sos.branchFolder(0, 3))  # line 249
        os.makedirs(sos.branchFolder(0, 4))  # line 250
        m = sos.Metadata(os.getcwd())  # line 251
        m.branch = 0  # line 252
        m.commit = 2  # line 253
        m.saveBranches()  # line 254
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 255
        m.saveCommit(0, 0)  # initial  # line 256
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 257
        m.saveCommit(0, 1)  # mod  # line 258
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 259
        m.saveCommit(0, 2)  # add  # line 260
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 261
        m.saveCommit(0, 3)  # del  # line 262
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 263
        m.saveCommit(0, 4)  # readd  # line 264
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 265
        m.saveBranch(0)  # line 266
        m.computeSequentialPathSet(0, 4)  # line 267
        _.assertEqual(2, len(m.paths))  # line 268

    def testParseRevisionString(_):  # line 270
        m = sos.Metadata(os.getcwd())  # line 271
        m.branch = 1  # line 272
        m.commits = {0: 0, 1: 1, 2: 2}  # line 273
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 274
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 275
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 276
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 277
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 278
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 279
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 280

    def testOfflineEmpty(_):  # line 282
        os.mkdir("." + os.sep + sos.metaFolder)  # line 283
        try:  # line 284
            sos.offline("trunk")  # line 284
            _.fail()  # line 284
        except SystemExit as E:  # line 285
            _.assertEqual(1, E.code)  # line 285
        os.rmdir("." + os.sep + sos.metaFolder)  # line 286
        sos.offline("test")  # line 287
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 288
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 289
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 290
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 291
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 292
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file  # line 293

    def testOfflineWithFiles(_):  # line 295
        _.createFile(1, "x" * 100)  # line 296
        _.createFile(2)  # line 297
        sos.offline("test")  # line 298
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 299
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 300
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 301
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 302
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 303
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 304
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file plus branch base file copies  # line 305

    def testBranch(_):  # line 307
        _.createFile(1, "x" * 100)  # line 308
        _.createFile(2)  # line 309
        sos.offline("test")  # b0/r0  # line 310
        sos.branch("other")  # b1/r0  # line 311
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 312
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 313
        _.assertEqual(list(sorted(os.listdir(sos.branchFolder(0, 0)))), list(sorted(os.listdir(sos.branchFolder(1, 0)))))  # line 315
        _.createFile(1, "z")  # modify file  # line 317
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 318
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 319
        _.createFile(3, "z")  # line 321
        sos.branch("from_last_revision", ["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 322
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 323
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 328
        _.createFile(1, "x" * 100)  # line 329
        _.createFile(2)  # line 330
        sos.offline("test")  # line 331
        changes = sos.changes()  # line 332
        _.assertEqual(0, len(changes.additions))  # line 333
        _.assertEqual(0, len(changes.deletions))  # line 334
        _.assertEqual(0, len(changes.modifications))  # line 335
        _.createFile(1, "z")  # size change  # line 336
        changes = sos.changes()  # line 337
        _.assertEqual(0, len(changes.additions))  # line 338
        _.assertEqual(0, len(changes.deletions))  # line 339
        _.assertEqual(1, len(changes.modifications))  # line 340
        sos.commit("message")  # line 341
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 342
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.branchFolder(0, 1)))  # line 343
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # no further files, only the modified one  # line 344
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 345
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 346
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 347
        os.unlink("file2")  # line 348
        changes = sos.changes()  # line 349
        _.assertEqual(0, len(changes.additions))  # line 350
        _.assertEqual(1, len(changes.deletions))  # line 351
        _.assertEqual(1, len(changes.modifications))  # line 352
        sos.commit("modified")  # line 353
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # no additional files, only mentions in metadata  # line 354
        try:  # expecting Exit due to no changes  # line 355
            sos.commit("nothing")  # expecting Exit due to no changes  # line 355
            _.fail()  # expecting Exit due to no changes  # line 355
        except:  # line 356
            pass  # line 356

    def testGetBranch(_):  # line 358
        m = sos.Metadata(os.getcwd())  # line 359
        m.branch = 1  # current branch  # line 360
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 361
        _.assertEqual(27, m.getBranchByName(27))  # line 362
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 363
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 364
        _.assertIsNone(m.getBranchByName("unknown"))  # line 365
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 366
        _.assertEqual(13, m.getRevisionByName("13"))  # line 367
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 368
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 369

    def testTagging(_):  # line 371
        m = sos.Metadata(os.getcwd())  # line 372
        sos.offline()  # line 373
        _.createFile(111)  # line 374
        sos.commit("tag", ["--tag"])  # line 375
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 376
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 377
        _.createFile(2)  # line 378
        try:  # line 379
            sos.commit("tag")  # line 379
            _.fail()  # line 379
        except:  # line 380
            pass  # line 380
        sos.commit("tag-2", ["--tag"])  # line 381
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 382
        _.assertIn("TAG tag", out)  # line 383

    def testSwitch(_):  # line 385
        _.createFile(1, "x" * 100)  # line 386
        _.createFile(2, "y")  # line 387
        sos.offline("test")  # file1-2  in initial branch commit  # line 388
        sos.branch("second")  # file1-2  switch, having same files  # line 389
        sos.switch("0")  # no change  switch back, no problem  # line 390
        sos.switch("second")  # no change  # switch back, no problem  # line 391
        _.createFile(3, "y")  # generate a file  # line 392
        try:  # uncommited changes detected  # line 393
            sos.switch("test")  # uncommited changes detected  # line 393
            _.fail()  # uncommited changes detected  # line 393
        except SystemExit as E:  # line 394
            _.assertEqual(1, E.code)  # line 394
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 395
        sos.changes()  # line 396
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 397
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 398
        _.createFile("XXX")  # line 399
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 400
        _.assertIn("File tree has changes", out)  # line 401
        _.assertNotIn("File tree is unchanged", out)  # line 402
        _.assertIn("  * b00   'test'", out)  # line 403
        _.assertIn("    b01 'second'", out)  # line 404
        _.assertIn("(dirty)", out)  # one branch has commits  # line 405
        _.assertIn("(in sync)", out)  # the other doesn't  # line 406
        _.createFile(4, "xy")  # generate a file  # line 407
        sos.switch("second", "--force")  # avoids warning on uncommited changes, but keeps file4  # line 408
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 409
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 410
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 411
        sos.switch("test", "--force")  # should restore file1 and remove file3  # line 412
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 413
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 414

    def testAutoDetectVCS(_):  # line 416
        os.mkdir(".git")  # line 417
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 418
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 419
            meta = fd.read()  # line 419
        _.assertTrue("\"master\"" in meta)  # line 420
        os.rmdir(".git")  # line 421

    def testUpdate(_):  # line 423
        sos.offline("trunk")  # create initial branch b0/r0  # line 424
        _.createFile(1, "x" * 100)  # line 425
        sos.commit("second")  # create b0/r1  # line 426

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 428
        _.assertFalse(_.existsFile(1))  # line 429

        sos.update("/1")  # recreate file1  # line 431
        _.assertTrue(_.existsFile(1))  # line 432

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 434
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2)))  # line 435
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2, file=sos.metaFile)))  # line 436
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # only meta data file, no differential files  # line 437

        sos.update("/1")  # do nothing, as nothing has changed  # line 439
        _.assertTrue(_.existsFile(1))  # line 440

        _.createFile(2, "y" * 100)  # line 442
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", ["--force"])  # automatically including file 2 (as we are in simple mode)  # line 445
        _.assertTrue(_.existsFile(2))  # line 446
        sos.update("trunk", ["--add"])  # only add stuff  # line 447
        _.assertTrue(_.existsFile(2))  # line 448
        sos.update("trunk")  # nothing to do  # line 449
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 450

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 452
        _.createFile(10, theirs)  # line 453
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 454
        _.createFile(11, mine)  # line 455
        _.assertEqual(b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 456
        _.assertEqual(b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 457

    def testUpdate2(_):  # line 459
        _.createFile("test.txt", "x" * 10)  # line 460
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 461
        sos.branch("mod")  # line 462
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 463
        time.sleep(FS_PRECISION)  # line 464
        sos.commit("mod")  # create b0/r1  # line 465
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 466
        with open("test.txt", "rb") as fd:  # line 467
            _.assertEqual(b"x" * 10, fd.read())  # line 467
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 468
        with open("test.txt", "rb") as fd:  # line 469
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 469
        _.createFile("test.txt", "x" * 10)  # line 470
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 471
        with open("test.txt", "rb") as fd:  # line 472
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 472
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 473
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 474
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 475
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 476
        with open("test.txt", "rb") as fd:  # line 477
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 477

    def testIsTextType(_):  # line 479
        m = sos.Metadata(".")  # line 480
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 481
        m.c.bintype = ["*.md.confluence"]  # line 482
        _.assertTrue(m.isTextType("ab.txt"))  # line 483
        _.assertTrue(m.isTextType("./ab.txt"))  # line 484
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 485
        _.assertFalse(m.isTextType("bc/ab."))  # line 486
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 487
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 488
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 489
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 490

    def testEolDet(_):  # line 492
        ''' Check correct end-of-line detection. '''  # line 493
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 494
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 495
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 496
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 497
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 498
        _.assertIsNone(sos.eoldet(b""))  # line 499
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 500

    def testMerge(_):  # line 502
        ''' Check merge results depending on user options. '''  # line 503
        a = b"a\nb\ncc\nd"  # type: bytes  # line 504
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 505
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT))  # one-line block replacement using lineMerge  # line 506
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT))  # means insert changes from a into b, but don't replace  # line 507
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE))  # means insert changes from a into b, but don't replace  # line 508
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE))  # one-line block replacement using lineMerge  # line 509
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE))  # line 510
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH))  # keeps any changes in b  # line 511
        a = b"a\nb\ncc\nd"  # line 512
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 513
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT))  # multi-line block replacement  # line 514
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE))  # line 515
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH))  # keeps any changes in b  # line 516
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT))  # line 518
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE))  # line 519
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 521
        b = b"a\nc\ne"  # line 522
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)))  # line 523
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)))  # line 524
        a = b"a\nb\ne"  # intra-line merge  # line 525
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)))  # line 526
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)))  # line 527

    def testMergeEol(_):  # line 529
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 530
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb"))  # when in doubt, use "mine" CR-LF  # line 531
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True))  # line 532

    def testPickyMode(_):  # line 534
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 535
        sos.offline("trunk", ["--picky"])  # line 536
        changes = sos.changes()  # line 537
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 538
        sos.add(".", "./file?", ["--force"])  # line 539
        _.createFile(1, "aa")  # line 540
        sos.commit("First")  # add one file  # line 541
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 542
        _.createFile(2, "b")  # line 543
        try:  # add nothing, because picky  # line 544
            sos.commit("Second")  # add nothing, because picky  # line 544
        except:  # line 545
            pass  # line 545
        sos.add(".", "./file?")  # line 546
        sos.commit("Third")  # line 547
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # line 548
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 549
        _.assertIn("  * r2", out)  # line 550
        _.createFile(3, prefix="sub")  # line 551
        sos.add("sub", "sub/file?")  # line 552
        changes = sos.changes()  # line 553
        _.assertEqual(1, len(changes.additions))  # line 554
        _.assertTrue("sub/file3" in changes.additions)  # line 555

    def testTrackedSubfolder(_):  # line 557
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 558
        os.mkdir("." + os.sep + "sub")  # line 559
        sos.offline("trunk", ["--track"])  # line 560
        _.createFile(1, "x")  # line 561
        _.createFile(1, "x", prefix="sub")  # line 562
        sos.add(".", "./file?")  # add glob pattern to track  # line 563
        sos.commit("First")  # line 564
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 565
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 566
        sos.commit("Second")  # one new file + meta  # line 567
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 568
        os.unlink("file1")  # remove from basefolder  # line 569
        _.createFile(2, "y")  # line 570
        sos.remove(".", "sub/file?")  # line 571
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 572
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 572
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 572
        except:  # line 573
            pass  # line 573
        sos.commit("Third")  # line 574
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta  # line 575
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 578
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 583
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 584
        _.createFile(1)  # line 585
        _.createFile("a123a")  # untracked file "a123a"  # line 586
        sos.add(".", "./file?")  # add glob tracking pattern  # line 587
        sos.commit("second")  # versions "file1"  # line 588
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 589
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 590
        _.assertIn("  | ./file?", out)  # line 591

        _.createFile(2)  # untracked file "file2"  # line 593
        sos.commit("third")  # versions "file2"  # line 594
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta file  # line 595

        os.mkdir("." + os.sep + "sub")  # line 597
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 598
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 599
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 3))))  # meta file only, no other tracked path/file  # line 600

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 602
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 603
        sos.add(".", "./a*a")  # add tracking pattern  # line 604
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 605
        _.assertEqual(0, len(changes.modifications))  # line 606
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 607
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 608

        sos.commit("Second_2")  # line 610
        _.assertEqual(2, len(os.listdir(sos.branchFolder(1, 1))))  # "a123a" + meta file  # line 611
        _.existsFile(1, b"x" * 10)  # line 612
        _.existsFile(2, b"x" * 10)  # line 613

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 615
        _.existsFile(1, b"x" * 10)  # line 616
        _.existsFile("a123a", b"x" * 10)  # line 617

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 619
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 620
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 621

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 623
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 624
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 625
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 626
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 627
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 628
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 629
# TODO test switch --meta

    def testLsTracked(_):  # line 632
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 633
        _.createFile(1)  # line 634
        _.createFile("foo")  # line 635
        sos.add(".", "./file*")  # capture one file  # line 636
        sos.ls()  # line 637
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 638
        _.assertInAny("TRK file1  (file*)", out)  # line 639
        _.assertNotInAny("... file1  (file*)", out)  # line 640
        _.assertInAny("... foo", out)  # line 641
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 642
        _.assertInAny("TRK file*", out)  # line 643
        _.createFile("a", prefix="sub")  # line 644
        sos.add("sub", "sub/a")  # line 645
        sos.ls("sub")  # line 646
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 647

    def testLineMerge(_):  # line 649
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 650
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 651
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 652
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 653

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 655
        _.createFile(1)  # line 656
        sos.offline("master", options=["--force"])  # line 657
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 658
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 659
        _.assertTrue(_.existsFile(sos.branchFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 660
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 661
        _.createFile(2)  # line 662
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # without progress, the output goes to stderr via debug()  # line 663
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 664
        sos.commit("Added file2")  # line 665
        _.assertTrue(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 666
        _.assertFalse(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 667

    def testLocalConfig(_):  # line 669
        sos.offline("bla", options=[])  # line 670
        try:  # line 671
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 671
        except SystemExit as E:  # line 672
            _.assertEqual(0, E.code)  # line 672
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 673

    def testConfigVariations(_):  # line 675
        def makeRepo():  # line 676
            try:  # line 677
                os.unlink("file1")  # line 677
            except:  # line 678
                pass  # line 678
            sos.offline("master", options=["--force"])  # line 679
            _.createFile(1)  # line 680
            sos.commit("Added file1")  # line 681
        try:  # line 682
            sos.config(["set", "strict", "on"])  # line 682
        except SystemExit as E:  # line 683
            _.assertEqual(0, E.code)  # line 683
        makeRepo()  # line 684
        _.assertTrue(checkRepoFlag("strict", True))  # line 685
        try:  # line 686
            sos.config(["set", "strict", "off"])  # line 686
        except SystemExit as E:  # line 687
            _.assertEqual(0, E.code)  # line 687
        makeRepo()  # line 688
        _.assertTrue(checkRepoFlag("strict", False))  # line 689
        try:  # line 690
            sos.config(["set", "strict", "yes"])  # line 690
        except SystemExit as E:  # line 691
            _.assertEqual(0, E.code)  # line 691
        makeRepo()  # line 692
        _.assertTrue(checkRepoFlag("strict", True))  # line 693
        try:  # line 694
            sos.config(["set", "strict", "no"])  # line 694
        except SystemExit as E:  # line 695
            _.assertEqual(0, E.code)  # line 695
        makeRepo()  # line 696
        _.assertTrue(checkRepoFlag("strict", False))  # line 697
        try:  # line 698
            sos.config(["set", "strict", "1"])  # line 698
        except SystemExit as E:  # line 699
            _.assertEqual(0, E.code)  # line 699
        makeRepo()  # line 700
        _.assertTrue(checkRepoFlag("strict", True))  # line 701
        try:  # line 702
            sos.config(["set", "strict", "0"])  # line 702
        except SystemExit as E:  # line 703
            _.assertEqual(0, E.code)  # line 703
        makeRepo()  # line 704
        _.assertTrue(checkRepoFlag("strict", False))  # line 705
        try:  # line 706
            sos.config(["set", "strict", "true"])  # line 706
        except SystemExit as E:  # line 707
            _.assertEqual(0, E.code)  # line 707
        makeRepo()  # line 708
        _.assertTrue(checkRepoFlag("strict", True))  # line 709
        try:  # line 710
            sos.config(["set", "strict", "false"])  # line 710
        except SystemExit as E:  # line 711
            _.assertEqual(0, E.code)  # line 711
        makeRepo()  # line 712
        _.assertTrue(checkRepoFlag("strict", False))  # line 713
        try:  # line 714
            sos.config(["set", "strict", "enable"])  # line 714
        except SystemExit as E:  # line 715
            _.assertEqual(0, E.code)  # line 715
        makeRepo()  # line 716
        _.assertTrue(checkRepoFlag("strict", True))  # line 717
        try:  # line 718
            sos.config(["set", "strict", "disable"])  # line 718
        except SystemExit as E:  # line 719
            _.assertEqual(0, E.code)  # line 719
        makeRepo()  # line 720
        _.assertTrue(checkRepoFlag("strict", False))  # line 721
        try:  # line 722
            sos.config(["set", "strict", "enabled"])  # line 722
        except SystemExit as E:  # line 723
            _.assertEqual(0, E.code)  # line 723
        makeRepo()  # line 724
        _.assertTrue(checkRepoFlag("strict", True))  # line 725
        try:  # line 726
            sos.config(["set", "strict", "disabled"])  # line 726
        except SystemExit as E:  # line 727
            _.assertEqual(0, E.code)  # line 727
        makeRepo()  # line 728
        _.assertTrue(checkRepoFlag("strict", False))  # line 729
        try:  # line 730
            sos.config(["set", "strict", "nope"])  # line 730
            _.fail()  # line 730
        except SystemExit as E:  # line 731
            _.assertEqual(1, E.code)  # line 731

    def testLsSimple(_):  # line 733
        _.createFile(1)  # line 734
        _.createFile("foo")  # line 735
        _.createFile("ign1")  # line 736
        _.createFile("ign2")  # line 737
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 738
        try:  # define an ignore pattern  # line 739
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 739
        except SystemExit as E:  # line 740
            _.assertEqual(0, E.code)  # line 740
        try:  # additional ignore pattern  # line 741
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 741
        except SystemExit as E:  # line 742
            _.assertEqual(0, E.code)  # line 742
        try:  # define a list of ignore patterns  # line 743
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 743
        except SystemExit as E:  # line 744
            _.assertEqual(0, E.code)  # line 744
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 745
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 746
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 747
        _.assertInAny('... file1', out)  # line 748
        _.assertInAny('... ign1', out)  # line 749
        _.assertInAny('... ign2', out)  # line 750
        try:  # line 751
            sos.config(["rm", "foo", "bar"])  # line 751
            _.fail()  # line 751
        except SystemExit as E:  # line 752
            _.assertEqual(1, E.code)  # line 752
        try:  # line 753
            sos.config(["rm", "ignores", "foo"])  # line 753
            _.fail()  # line 753
        except SystemExit as E:  # line 754
            _.assertEqual(1, E.code)  # line 754
        try:  # line 755
            sos.config(["rm", "ignores", "ign1"])  # line 755
        except SystemExit as E:  # line 756
            _.assertEqual(0, E.code)  # line 756
        try:  # remove ignore pattern  # line 757
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 757
        except SystemExit as E:  # line 758
            _.assertEqual(0, E.code)  # line 758
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 759
        _.assertInAny('... ign1', out)  # line 760
        _.assertInAny('IGN ign2', out)  # line 761
        _.assertNotInAny('... ign2', out)  # line 762

    def testWhitelist(_):  # line 764
# TODO test same for simple mode
        _.createFile(1)  # line 766
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 767
        sos.offline("xx", ["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 768
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 769
        sos.commit(options=["--force"])  # attempt to commit the file  # line 770
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 1))))  # only meta data, file1 was ignored  # line 771
        try:  # Exit because dirty  # line 772
            sos.online()  # Exit because dirty  # line 772
            _.fail()  # Exit because dirty  # line 772
        except:  # exception expected  # line 773
            pass  # exception expected  # line 773
        _.createFile("x2")  # add another change  # line 774
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 775
        try:  # force beyond dirty flag check  # line 776
            sos.online(["--force"])  # force beyond dirty flag check  # line 776
            _.fail()  # force beyond dirty flag check  # line 776
        except:  # line 777
            pass  # line 777
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 778
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 779

        _.createFile(1)  # line 781
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 782
        sos.offline("xx", ["--track"])  # line 783
        sos.add(".", "./file*")  # line 784
        sos.commit()  # should NOT ask for force here  # line 785
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 786

    def testRemove(_):  # line 788
        _.createFile(1, "x" * 100)  # line 789
        sos.offline("trunk")  # line 790
        try:  # line 791
            sos.delete("trunk")  # line 791
            _fail()  # line 791
        except:  # line 792
            pass  # line 792
        _.createFile(2, "y" * 10)  # line 793
        sos.branch("added")  # line 794
        sos.delete("trunk")  # line 795
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # meta data file and "b1"  # line 796
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 797
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 798
        sos.branch("next")  # line 799
        _.createFile(3, "y" * 10)  # make a change  # line 800
        sos.delete("added", "--force")  # should succeed  # line 801

    def testUsage(_):  # line 803
        try:  # TODO expect sys.exit(0)  # line 804
            sos.usage()  # TODO expect sys.exit(0)  # line 804
            _.fail()  # TODO expect sys.exit(0)  # line 804
        except:  # line 805
            pass  # line 805
        try:  # line 806
            sos.usage(short=True)  # line 806
            _.fail()  # line 806
        except:  # line 807
            pass  # line 807

    def testOnly(_):  # line 809
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 810
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 811
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 812
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 813
        sos.offline(os.getcwd(), ["--track", "--strict"])  # line 814
        _.createFile(1)  # line 815
        _.createFile(2)  # line 816
        sos.add(".", "./file1")  # line 817
        sos.add(".", "./file2")  # line 818
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 819
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # only meta and file1  # line 820
        sos.commit()  # adds also file2  # line 821
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # only meta and file1  # line 822
        _.createFile(1, "cc")  # modify both files  # line 823
        _.createFile(2, "dd")  # line 824
        try:  # line 825
            sos.config(["set", "texttype", "file2"])  # line 825
        except SystemExit as E:  # line 826
            _.assertEqual(0, E.code)  # line 826
        changes = sos.changes(excps=["./file1"])  # line 827
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 828
        _.assertTrue("./file2" in changes.modifications)  # line 829
        _.assertIn("DIF ./file2", wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 830
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 831

    def testDiff(_):  # line 833
        try:  # manually mark this file as "textual"  # line 834
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 834
        except SystemExit as E:  # line 835
            _.assertEqual(0, E.code)  # line 835
        sos.offline(options=["--strict"])  # line 836
        _.createFile(1)  # line 837
        _.createFile(2)  # line 838
        sos.commit()  # line 839
        _.createFile(1, "sdfsdgfsdf")  # line 840
        _.createFile(2, "12343")  # line 841
        sos.commit()  # line 842
        _.createFile(1, "foobar")  # line 843
        _.createFile(3)  # line 844
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 845
        _.assertIn("ADD ./file3", out)  # line 846
        _.assertAllIn(["MOD ./file2", "DIF ./file1", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 847
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 848

    def testReorderRenameActions(_):  # line 850
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 851
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 852
        try:  # line 853
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 853
            _.fail()  # line 853
        except:  # line 854
            pass  # line 854

    def testMove(_):  # line 856
        sos.offline(options=["--strict", "--track"])  # line 857
        _.createFile(1)  # line 858
        sos.add(".", "./file?")  # line 859
# test source folder missing
        try:  # line 861
            sos.move("sub", "sub/file?", ".", "?file")  # line 861
            _.fail()  # line 861
        except:  # line 862
            pass  # line 862
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 864
        _.assertTrue(os.path.exists("sub"))  # line 865
        _.assertTrue(os.path.exists("sub/file1"))  # line 866
        _.assertFalse(os.path.exists("file1"))  # line 867
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 869
        _.assertTrue(os.path.exists("1file"))  # line 870
        _.assertFalse(os.path.exists("sub/file1"))  # line 871
# test nothing matches source pattern
        try:  # line 873
            sos.move(".", "a*", ".", "b*")  # line 873
            _.fail()  # line 873
        except:  # line 874
            pass  # line 874
        sos.add(".", "*")  # anything pattern  # line 875
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 876
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 876
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 876
        except:  # line 877
            pass  # line 877
# test rename no conflict
        _.createFile(1)  # line 879
        _.createFile(2)  # line 880
        _.createFile(3)  # line 881
        sos.add(".", "./file*")  # line 882
        try:  # define an ignore pattern  # line 883
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 883
        except SystemExit as E:  # line 884
            _.assertEqual(0, E.code)  # line 884
        try:  # line 885
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 885
        except SystemExit as E:  # line 886
            _.assertEqual(0, E.code)  # line 886
        sos.move(".", "./file*", ".", "fi*le")  # line 887
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 888
        _.assertFalse(os.path.exists("fi4le"))  # line 889
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 891
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 895
        sos.add(".", "./?a?b", ["--force"])  # line 896
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 897
        _.createFile("1a2b")  # should not be tracked  # line 898
        _.createFile("a1b2")  # should be tracked  # line 899
        sos.commit()  # line 900
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 901
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 902
        _.createFile("1a1b1")  # line 903
        _.createFile("1a1b2")  # line 904
        sos.add(".", "?a?b*")  # line 905
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 906
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 910
        sos.offline()  # line 911
        _.createFile(1)  # line 912
        os.mkdir(sos.branchFolder(0, 1))  # line 913
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.branchFolder(0, 1))  # line 914
        _.createFile(1)  # line 915
        try:  # should exit with error due to collision detection  # line 916
            sos.commit()  # should exit with error due to collision detection  # line 916
            _.fail()  # should exit with error due to collision detection  # line 916
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 917
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 917

    def testFindBase(_):  # line 919
        old = os.getcwd()  # line 920
        try:  # line 921
            os.mkdir("." + os.sep + ".git")  # line 922
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 923
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 924
            os.chdir("a" + os.sep + "b")  # line 925
            s, vcs, cmd = sos.findSosVcsBase()  # line 926
            _.assertIsNotNone(s)  # line 927
            _.assertIsNotNone(vcs)  # line 928
            _.assertEqual("git", cmd)  # line 929
        finally:  # line 930
            os.chdir(old)  # line 930

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail


if __name__ == '__main__':  # line 936
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 937
    c = configr.Configr("sos")  # line 938
    c.loadSettings()  # line 939
    if len(c.keys()) > 0:  # line 940
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 940
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 941
