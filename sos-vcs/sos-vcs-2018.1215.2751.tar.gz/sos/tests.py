#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xf8251dfe

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
    buf = TextIOWrapper(BufferedRandom(BytesIO(b"")), encoding=sos.UTF8)  # line 60
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

    def testAutoUpgrade(_):  # line 172
        sos.offline()  # line 173
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "r", encoding=sos.UTF8) as fd:  # line 174
            repo, branches, config = json.load(fd)  # line 174
        del repo["format"]  # simulate pre-1.3.5  # line 175
        repo["version"] = "0"  # lower than any pip version  # line 176
        branches[:] = [branch[:6] for branch in branches]  # line 177
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "w", encoding=sos.UTF8) as fd:  # line 178
            json.dump((repo, branches, config), fd, ensure_ascii=False)  # line 178
        out = wrapChannels(lambda: sos.status(options=["--repo"]))  # line 179
        _.assertAllIn(["Upgraded repository metadata to match SOS version '2018.1210.3028'", "Upgraded repository metadata to match SOS version '1.3.5'"], out)  # line 180

    def testTokenizeGlobPattern(_):  # line 182
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 183
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 184
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 185
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 186
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 187
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 188

    def testTokenizeGlobPatterns(_):  # line 190
        try:  # because number of literal strings differs  # line 191
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 191
            _.fail()  # because number of literal strings differs  # line 191
        except:  # line 192
            pass  # line 192
        try:  # because glob patterns differ  # line 193
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 193
            _.fail()  # because glob patterns differ  # line 193
        except:  # line 194
            pass  # line 194
        try:  # glob patterns differ, regardless of position  # line 195
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 195
            _.fail()  # glob patterns differ, regardless of position  # line 195
        except:  # line 196
            pass  # line 196
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 197
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 198
        try:  # succeeds, because glob patterns match (differ only in position)  # line 199
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 199
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 199
        except:  # line 200
            pass  # line 200

    def testConvertGlobFiles(_):  # line 202
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 203
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 204

    def testFolderRemove(_):  # line 206
        m = sos.Metadata(os.getcwd())  # line 207
        _.createFile(1)  # line 208
        _.createFile("a", prefix="sub")  # line 209
        sos.offline()  # line 210
        _.createFile(2)  # line 211
        os.unlink("sub" + os.sep + "a")  # line 212
        os.rmdir("sub")  # line 213
        changes = sos.changes()  # TODO replace by output check  # line 214
        _.assertEqual(1, len(changes.additions))  # line 215
        _.assertEqual(0, len(changes.modifications))  # line 216
        _.assertEqual(1, len(changes.deletions))  # line 217
        _.createFile("a", prefix="sub")  # line 218
        changes = sos.changes()  # line 219
        _.assertEqual(0, len(changes.deletions))  # line 220

    def testSwitchConflict(_):  # line 222
        sos.offline(options=["--strict"])  # (r0)  # line 223
        _.createFile(1)  # line 224
        sos.commit()  # add file (r1)  # line 225
        os.unlink("file1")  # line 226
        sos.commit()  # remove (r2)  # line 227
        _.createFile(1, "something else")  # line 228
        sos.commit()  # (r3)  # line 229
        sos.switch("/1")  # updates file1 - marked as MOD, because mtime was changed  # line 230
        _.existsFile(1, "x" * 10)  # line 231
        sos.switch("/2", ["--force"])  # remove file1 requires --force, because size/content (or mtime in non-strict mode) is different to head of branch  # line 232
        sos.switch("/0")  # do nothing, as file1 is already removed  # line 233
        sos.switch("/1")  # add file1 back  # line 234
        sos.switch("/", ["--force"])  # requires force because changed vs. head of branch  # line 235
        _.existsFile(1, "something else")  # line 236

    def testComputeSequentialPathSet(_):  # line 238
        os.makedirs(sos.branchFolder(0, 0))  # line 239
        os.makedirs(sos.branchFolder(0, 1))  # line 240
        os.makedirs(sos.branchFolder(0, 2))  # line 241
        os.makedirs(sos.branchFolder(0, 3))  # line 242
        os.makedirs(sos.branchFolder(0, 4))  # line 243
        m = sos.Metadata(os.getcwd())  # line 244
        m.branch = 0  # line 245
        m.commit = 2  # line 246
        m.saveBranches()  # line 247
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 248
        m.saveCommit(0, 0)  # initial  # line 249
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 250
        m.saveCommit(0, 1)  # mod  # line 251
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 252
        m.saveCommit(0, 2)  # add  # line 253
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 254
        m.saveCommit(0, 3)  # del  # line 255
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")  # line 256
        m.saveCommit(0, 4)  # readd  # line 257
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 258
        m.saveBranch(0)  # line 259
        m.branches = {0: sos.BranchInfo(0, 0), 1: sos.BranchInfo(1, 0)}  # line 260
        m.saveBranches()  # line 261
        m.computeSequentialPathSet(0, 4)  # line 262
        _.assertEqual(2, len(m.paths))  # line 263

    def testParseRevisionString(_):  # line 265
        m = sos.Metadata(os.getcwd())  # line 266
        m.branch = 1  # line 267
        m.commits = {0: 0, 1: 1, 2: 2}  # line 268
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 269
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 270
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 271
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 272
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 273
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 274
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 275

    def testOfflineEmpty(_):  # line 277
        os.mkdir("." + os.sep + sos.metaFolder)  # line 278
        try:  # line 279
            sos.offline("trunk")  # line 279
            _.fail()  # line 279
        except SystemExit as E:  # line 280
            _.assertEqual(1, E.code)  # line 280
        os.rmdir("." + os.sep + sos.metaFolder)  # line 281
        sos.offline("test")  # line 282
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 283
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 284
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 285
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 286
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 287
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file  # line 288

    def testOfflineWithFiles(_):  # line 290
        _.createFile(1, "x" * 100)  # line 291
        _.createFile(2)  # line 292
        sos.offline("test")  # line 293
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 294
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 295
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 296
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 297
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 298
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 299
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file plus branch base file copies  # line 300

    def testBranch(_):  # line 302
        _.createFile(1, "x" * 100)  # line 303
        _.createFile(2)  # line 304
        sos.offline("test")  # b0/r0  # line 305
        sos.branch("other")  # b1/r0  # line 306
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 307
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 308
        _.assertEqual(list(sorted(os.listdir(sos.branchFolder(0, 0)))), list(sorted(os.listdir(sos.branchFolder(1, 0)))))  # line 310
        _.createFile(1, "z")  # modify file  # line 312
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 313
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 314
        _.createFile(3, "z")  # line 316
        sos.branch("from_last_revision", ["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 317
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 318
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 323
        _.createFile(1, "x" * 100)  # line 324
        _.createFile(2)  # line 325
        sos.offline("test")  # line 326
        changes = sos.changes()  # line 327
        _.assertEqual(0, len(changes.additions))  # line 328
        _.assertEqual(0, len(changes.deletions))  # line 329
        _.assertEqual(0, len(changes.modifications))  # line 330
        _.createFile(1, "z")  # size change  # line 331
        changes = sos.changes()  # line 332
        _.assertEqual(0, len(changes.additions))  # line 333
        _.assertEqual(0, len(changes.deletions))  # line 334
        _.assertEqual(1, len(changes.modifications))  # line 335
        sos.commit("message")  # line 336
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 337
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.branchFolder(0, 1)))  # line 338
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # no further files, only the modified one  # line 339
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 340
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 341
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 342
        os.unlink("file2")  # line 343
        changes = sos.changes()  # line 344
        _.assertEqual(0, len(changes.additions))  # line 345
        _.assertEqual(1, len(changes.deletions))  # line 346
        _.assertEqual(1, len(changes.modifications))  # line 347
        sos.commit("modified")  # line 348
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # no additional files, only mentions in metadata  # line 349
        try:  # expecting Exit due to no changes  # line 350
            sos.commit("nothing")  # expecting Exit due to no changes  # line 350
            _.fail()  # expecting Exit due to no changes  # line 350
        except:  # line 351
            pass  # line 351

    def testGetBranch(_):  # line 353
        m = sos.Metadata(os.getcwd())  # line 354
        m.branch = 1  # current branch  # line 355
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 356
        _.assertEqual(27, m.getBranchByName(27))  # line 357
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 358
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 359
        _.assertIsNone(m.getBranchByName("unknown"))  # line 360
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 361
        _.assertEqual(13, m.getRevisionByName("13"))  # line 362
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 363
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 364

    def testTagging(_):  # line 366
        m = sos.Metadata(os.getcwd())  # line 367
        sos.offline()  # line 368
        _.createFile(111)  # line 369
        sos.commit("tag", ["--tag"])  # line 370
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 371
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 372
        _.createFile(2)  # line 373
        try:  # line 374
            sos.commit("tag")  # line 374
            _.fail()  # line 374
        except:  # line 375
            pass  # line 375
        sos.commit("tag-2", ["--tag"])  # line 376
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 377
        _.assertIn("TAG tag", out)  # line 378

    def testSwitch(_):  # line 380
        _.createFile(1, "x" * 100)  # line 381
        _.createFile(2, "y")  # line 382
        sos.offline("test")  # file1-2  in initial branch commit  # line 383
        sos.branch("second")  # file1-2  switch, having same files  # line 384
        sos.switch("0")  # no change  switch back, no problem  # line 385
        sos.switch("second")  # no change  # switch back, no problem  # line 386
        _.createFile(3, "y")  # generate a file  # line 387
        try:  # uncommited changes detected  # line 388
            sos.switch("test")  # uncommited changes detected  # line 388
            _.fail()  # uncommited changes detected  # line 388
        except SystemExit as E:  # line 389
            _.assertEqual(1, E.code)  # line 389
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 390
        sos.changes()  # line 391
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 392
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 393
        _.createFile("XXX")  # line 394
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 395
        _.assertIn("File tree has changes", out)  # line 396
        _.assertNotIn("File tree is unchanged", out)  # line 397
        _.assertIn("  * b00   'test'", out)  # line 398
        _.assertIn("    b01 'second'", out)  # line 399
        _.assertIn("(dirty)", out)  # one branch has commits  # line 400
        _.assertIn("(in sync)", out)  # the other doesn't  # line 401
        _.createFile(4, "xy")  # generate a file  # line 402
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4  # line 403
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 404
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 405
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 406
        sos.switch("test", ["--force"])  # should restore file1 and remove file3  # line 407
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 408
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 409

    def testAutoDetectVCS(_):  # line 411
        os.mkdir(".git")  # line 412
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 413
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 414
            meta = fd.read()  # line 414
        _.assertTrue("\"master\"" in meta)  # line 415
        os.rmdir(".git")  # line 416

    def testUpdate(_):  # line 418
        sos.offline("trunk")  # create initial branch b0/r0  # line 419
        _.createFile(1, "x" * 100)  # line 420
        sos.commit("second")  # create b0/r1  # line 421

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 423
        _.assertFalse(_.existsFile(1))  # line 424

        sos.update("/1")  # recreate file1  # line 426
        _.assertTrue(_.existsFile(1))  # line 427

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 429
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2)))  # line 430
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2, file=sos.metaFile)))  # line 431
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # only meta data file, no differential files  # line 432

        sos.update("/1")  # do nothing, as nothing has changed  # line 434
        _.assertTrue(_.existsFile(1))  # line 435

        _.createFile(2, "y" * 100)  # line 437
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", ["--force"])  # automatically including file 2 (as we are in simple mode)  # line 440
        _.assertTrue(_.existsFile(2))  # line 441
        sos.update("trunk", ["--add"])  # only add stuff  # line 442
        _.assertTrue(_.existsFile(2))  # line 443
        sos.update("trunk")  # nothing to do  # line 444
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 445

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 447
        _.createFile(10, theirs)  # line 448
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 449
        _.createFile(11, mine)  # line 450
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 451
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 452

    def testUpdate2(_):  # line 454
        _.createFile("test.txt", "x" * 10)  # line 455
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 456
        sos.branch("mod")  # line 457
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 458
        time.sleep(FS_PRECISION)  # line 459
        sos.commit("mod")  # create b0/r1  # line 460
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 461
        with open("test.txt", "rb") as fd:  # line 462
            _.assertEqual(b"x" * 10, fd.read())  # line 462
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 463
        with open("test.txt", "rb") as fd:  # line 464
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 464
        _.createFile("test.txt", "x" * 10)  # line 465
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 466
        with open("test.txt", "rb") as fd:  # line 467
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 467
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 468
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 469
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 470
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 471
        with open("test.txt", "rb") as fd:  # line 472
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 472

    def testIsTextType(_):  # line 474
        m = sos.Metadata(".")  # line 475
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 476
        m.c.bintype = ["*.md.confluence"]  # line 477
        _.assertTrue(m.isTextType("ab.txt"))  # line 478
        _.assertTrue(m.isTextType("./ab.txt"))  # line 479
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 480
        _.assertFalse(m.isTextType("bc/ab."))  # line 481
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 482
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 483
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 484
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 485

    def testEolDet(_):  # line 487
        ''' Check correct end-of-line detection. '''  # line 488
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 489
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 490
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 491
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 492
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 493
        _.assertIsNone(sos.eoldet(b""))  # line 494
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 495

    def testMerge(_):  # line 497
        ''' Check merge results depending on user options. '''  # line 498
        a = b"a\nb\ncc\nd"  # type: bytes  # line 499
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 500
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge  # line 501
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace  # line 502
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace  # line 503
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge  # line 504
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 505
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 506
        a = b"a\nb\ncc\nd"  # line 507
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 508
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement  # line 509
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # line 510
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 511
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])  # line 513
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 514
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 516
        b = b"a\nc\ne"  # line 517
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 518
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 519
        a = b"a\nb\ne"  # intra-line merge  # line 520
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 521
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 522

    def testMergeEol(_):  # line 524
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])  # line 525
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 526
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF  # line 527
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])  # line 528
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])  # line 529

    def testPickyMode(_):  # line 531
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 532
        sos.offline("trunk", ["--picky"])  # line 533
        changes = sos.changes()  # line 534
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 535
        sos.add(".", "./file?", ["--force"])  # line 536
        _.createFile(1, "aa")  # line 537
        sos.commit("First")  # add one file  # line 538
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 539
        _.createFile(2, "b")  # line 540
        try:  # add nothing, because picky  # line 541
            sos.commit("Second")  # add nothing, because picky  # line 541
        except:  # line 542
            pass  # line 542
        sos.add(".", "./file?")  # line 543
        sos.commit("Third")  # line 544
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # line 545
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 546
        _.assertIn("  * r2", out)  # line 547
        _.createFile(3, prefix="sub")  # line 548
        sos.add("sub", "sub/file?")  # line 549
        changes = sos.changes()  # line 550
        _.assertEqual(1, len(changes.additions))  # line 551
        _.assertTrue("sub/file3" in changes.additions)  # line 552

    def testTrackedSubfolder(_):  # line 554
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 555
        os.mkdir("." + os.sep + "sub")  # line 556
        sos.offline("trunk", ["--track"])  # line 557
        _.createFile(1, "x")  # line 558
        _.createFile(1, "x", prefix="sub")  # line 559
        sos.add(".", "./file?")  # add glob pattern to track  # line 560
        sos.commit("First")  # line 561
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 562
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 563
        sos.commit("Second")  # one new file + meta  # line 564
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 565
        os.unlink("file1")  # remove from basefolder  # line 566
        _.createFile(2, "y")  # line 567
        sos.remove(".", "sub/file?")  # line 568
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 569
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 569
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 569
        except:  # line 570
            pass  # line 570
        sos.commit("Third")  # line 571
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta  # line 572
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 575
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 580
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 581
        _.createFile(1)  # line 582
        _.createFile("a123a")  # untracked file "a123a"  # line 583
        sos.add(".", "./file?")  # add glob tracking pattern  # line 584
        sos.commit("second")  # versions "file1"  # line 585
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 586
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 587
        _.assertIn("  | ./file?", out)  # line 588

        _.createFile(2)  # untracked file "file2"  # line 590
        sos.commit("third")  # versions "file2"  # line 591
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta file  # line 592

        os.mkdir("." + os.sep + "sub")  # line 594
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 595
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 596
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 3))))  # meta file only, no other tracked path/file  # line 597

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 599
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 600
        sos.add(".", "./a*a")  # add tracking pattern  # line 601
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 602
        _.assertEqual(0, len(changes.modifications))  # line 603
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 604
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 605

        sos.commit("Second_2")  # line 607
        _.assertEqual(2, len(os.listdir(sos.branchFolder(1, 1))))  # "a123a" + meta file  # line 608
        _.existsFile(1, b"x" * 10)  # line 609
        _.existsFile(2, b"x" * 10)  # line 610

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 612
        _.existsFile(1, b"x" * 10)  # line 613
        _.existsFile("a123a", b"x" * 10)  # line 614

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 616
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 617
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 618

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 620
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 621
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 622
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 623
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 624
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 625
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 626
# TODO test switch --meta

    def testLsTracked(_):  # line 629
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 630
        _.createFile(1)  # line 631
        _.createFile("foo")  # line 632
        sos.add(".", "./file*")  # capture one file  # line 633
        sos.ls()  # line 634
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 635
        _.assertInAny("TRK file1  (file*)", out)  # line 636
        _.assertNotInAny("... file1  (file*)", out)  # line 637
        _.assertInAny("··· foo", out)  # line 638
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 639
        _.assertInAny("TRK file*", out)  # line 640
        _.createFile("a", prefix="sub")  # line 641
        sos.add("sub", "sub/a")  # line 642
        sos.ls("sub")  # line 643
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 644

    def testLineMerge(_):  # line 646
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 647
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 648
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 649
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 650

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 652
        _.createFile(1)  # line 653
        sos.offline("master", options=["--force"])  # line 654
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 655
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 656
        _.assertTrue(_.existsFile(sos.branchFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 657
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 658
        _.createFile(2)  # line 659
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 660
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 661
        _.assertTrue(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 662
        _.assertFalse(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 663

    def testLocalConfig(_):  # line 665
        sos.offline("bla", options=[])  # line 666
        try:  # line 667
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 667
        except SystemExit as E:  # line 668
            _.assertEqual(0, E.code)  # line 668
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 669

    def testConfigVariations(_):  # line 671
        def makeRepo():  # line 672
            try:  # line 673
                os.unlink("file1")  # line 673
            except:  # line 674
                pass  # line 674
            sos.offline("master", options=["--force"])  # line 675
            _.createFile(1)  # line 676
            sos.commit("Added file1")  # line 677
        try:  # line 678
            sos.config(["set", "strict", "on"])  # line 678
        except SystemExit as E:  # line 679
            _.assertEqual(0, E.code)  # line 679
        makeRepo()  # line 680
        _.assertTrue(checkRepoFlag("strict", True))  # line 681
        try:  # line 682
            sos.config(["set", "strict", "off"])  # line 682
        except SystemExit as E:  # line 683
            _.assertEqual(0, E.code)  # line 683
        makeRepo()  # line 684
        _.assertTrue(checkRepoFlag("strict", False))  # line 685
        try:  # line 686
            sos.config(["set", "strict", "yes"])  # line 686
        except SystemExit as E:  # line 687
            _.assertEqual(0, E.code)  # line 687
        makeRepo()  # line 688
        _.assertTrue(checkRepoFlag("strict", True))  # line 689
        try:  # line 690
            sos.config(["set", "strict", "no"])  # line 690
        except SystemExit as E:  # line 691
            _.assertEqual(0, E.code)  # line 691
        makeRepo()  # line 692
        _.assertTrue(checkRepoFlag("strict", False))  # line 693
        try:  # line 694
            sos.config(["set", "strict", "1"])  # line 694
        except SystemExit as E:  # line 695
            _.assertEqual(0, E.code)  # line 695
        makeRepo()  # line 696
        _.assertTrue(checkRepoFlag("strict", True))  # line 697
        try:  # line 698
            sos.config(["set", "strict", "0"])  # line 698
        except SystemExit as E:  # line 699
            _.assertEqual(0, E.code)  # line 699
        makeRepo()  # line 700
        _.assertTrue(checkRepoFlag("strict", False))  # line 701
        try:  # line 702
            sos.config(["set", "strict", "true"])  # line 702
        except SystemExit as E:  # line 703
            _.assertEqual(0, E.code)  # line 703
        makeRepo()  # line 704
        _.assertTrue(checkRepoFlag("strict", True))  # line 705
        try:  # line 706
            sos.config(["set", "strict", "false"])  # line 706
        except SystemExit as E:  # line 707
            _.assertEqual(0, E.code)  # line 707
        makeRepo()  # line 708
        _.assertTrue(checkRepoFlag("strict", False))  # line 709
        try:  # line 710
            sos.config(["set", "strict", "enable"])  # line 710
        except SystemExit as E:  # line 711
            _.assertEqual(0, E.code)  # line 711
        makeRepo()  # line 712
        _.assertTrue(checkRepoFlag("strict", True))  # line 713
        try:  # line 714
            sos.config(["set", "strict", "disable"])  # line 714
        except SystemExit as E:  # line 715
            _.assertEqual(0, E.code)  # line 715
        makeRepo()  # line 716
        _.assertTrue(checkRepoFlag("strict", False))  # line 717
        try:  # line 718
            sos.config(["set", "strict", "enabled"])  # line 718
        except SystemExit as E:  # line 719
            _.assertEqual(0, E.code)  # line 719
        makeRepo()  # line 720
        _.assertTrue(checkRepoFlag("strict", True))  # line 721
        try:  # line 722
            sos.config(["set", "strict", "disabled"])  # line 722
        except SystemExit as E:  # line 723
            _.assertEqual(0, E.code)  # line 723
        makeRepo()  # line 724
        _.assertTrue(checkRepoFlag("strict", False))  # line 725
        try:  # line 726
            sos.config(["set", "strict", "nope"])  # line 726
            _.fail()  # line 726
        except SystemExit as E:  # line 727
            _.assertEqual(1, E.code)  # line 727

    def testLsSimple(_):  # line 729
        _.createFile(1)  # line 730
        _.createFile("foo")  # line 731
        _.createFile("ign1")  # line 732
        _.createFile("ign2")  # line 733
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 734
        try:  # define an ignore pattern  # line 735
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 735
        except SystemExit as E:  # line 736
            _.assertEqual(0, E.code)  # line 736
        try:  # additional ignore pattern  # line 737
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 737
        except SystemExit as E:  # line 738
            _.assertEqual(0, E.code)  # line 738
        try:  # define a list of ignore patterns  # line 739
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 739
        except SystemExit as E:  # line 740
            _.assertEqual(0, E.code)  # line 740
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 741
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 742
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 743
        _.assertInAny('··· file1', out)  # line 744
        _.assertInAny('··· ign1', out)  # line 745
        _.assertInAny('··· ign2', out)  # line 746
        try:  # line 747
            sos.config(["rm", "foo", "bar"])  # line 747
            _.fail()  # line 747
        except SystemExit as E:  # line 748
            _.assertEqual(1, E.code)  # line 748
        try:  # line 749
            sos.config(["rm", "ignores", "foo"])  # line 749
            _.fail()  # line 749
        except SystemExit as E:  # line 750
            _.assertEqual(1, E.code)  # line 750
        try:  # line 751
            sos.config(["rm", "ignores", "ign1"])  # line 751
        except SystemExit as E:  # line 752
            _.assertEqual(0, E.code)  # line 752
        try:  # remove ignore pattern  # line 753
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 753
        except SystemExit as E:  # line 754
            _.assertEqual(0, E.code)  # line 754
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 755
        _.assertInAny('··· ign1', out)  # line 756
        _.assertInAny('IGN ign2', out)  # line 757
        _.assertNotInAny('··· ign2', out)  # line 758

    def testWhitelist(_):  # line 760
# TODO test same for simple mode
        _.createFile(1)  # line 762
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 763
        sos.offline("xx", ["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 764
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 765
        sos.commit(options=["--force"])  # attempt to commit the file  # line 766
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 1))))  # only meta data, file1 was ignored  # line 767
        try:  # Exit because dirty  # line 768
            sos.online()  # Exit because dirty  # line 768
            _.fail()  # Exit because dirty  # line 768
        except:  # exception expected  # line 769
            pass  # exception expected  # line 769
        _.createFile("x2")  # add another change  # line 770
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 771
        try:  # force beyond dirty flag check  # line 772
            sos.online(["--force"])  # force beyond dirty flag check  # line 772
            _.fail()  # force beyond dirty flag check  # line 772
        except:  # line 773
            pass  # line 773
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 774
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 775

        _.createFile(1)  # line 777
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 778
        sos.offline("xx", ["--track"])  # line 779
        sos.add(".", "./file*")  # line 780
        sos.commit()  # should NOT ask for force here  # line 781
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 782

    def testRemove(_):  # line 784
        _.createFile(1, "x" * 100)  # line 785
        sos.offline("trunk")  # line 786
        try:  # line 787
            sos.delete("trunk")  # line 787
            _fail()  # line 787
        except:  # line 788
            pass  # line 788
        _.createFile(2, "y" * 10)  # line 789
        sos.branch("added")  # creates new branch, writes repo metadata, and therefore creates backup copy  # line 790
        sos.delete("trunk")  # line 791
        _.assertEqual(3, len(os.listdir("." + os.sep + sos.metaFolder)))  # meta data file, backup and "b1"  # line 792
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 793
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 794
        sos.branch("next")  # line 795
        _.createFile(3, "y" * 10)  # make a change  # line 796
        sos.delete("added", "--force")  # should succeed  # line 797

    def testUsage(_):  # line 799
        try:  # TODO expect sys.exit(0)  # line 800
            sos.usage()  # TODO expect sys.exit(0)  # line 800
            _.fail()  # TODO expect sys.exit(0)  # line 800
        except:  # line 801
            pass  # line 801
        try:  # line 802
            sos.usage(short=True)  # line 802
            _.fail()  # line 802
        except:  # line 803
            pass  # line 803

    def testOnlyExcept(_):  # line 805
        ''' Test blacklist glob rules. '''  # line 806
        sos.offline(options=["--track"])  # line 807
        _.createFile("a.1")  # line 808
        _.createFile("a.2")  # line 809
        _.createFile("b.1")  # line 810
        _.createFile("b.2")  # line 811
        sos.add(".", "./a.?")  # line 812
        sos.add(".", "./?.1", negative=True)  # line 813
        out = wrapChannels(lambda: sos.commit())  # line 814
        _.assertIn("ADD ./a.2", out)  # line 815
        _.assertNotIn("ADD ./a.1", out)  # line 816
        _.assertNotIn("ADD ./b.1", out)  # line 817
        _.assertNotIn("ADD ./b.2", out)  # line 818

    def testOnly(_):  # line 820
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 821
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 822
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 823
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 824
        sos.offline(options=["--track", "--strict"])  # line 825
        _.createFile(1)  # line 826
        _.createFile(2)  # line 827
        sos.add(".", "./file1")  # line 828
        sos.add(".", "./file2")  # line 829
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 830
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # only meta and file1  # line 831
        sos.commit()  # adds also file2  # line 832
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # only meta and file1  # line 833
        _.createFile(1, "cc")  # modify both files  # line 834
        _.createFile(2, "dd")  # line 835
        try:  # line 836
            sos.config(["set", "texttype", "file2"])  # line 836
        except SystemExit as E:  # line 837
            _.assertEqual(0, E.code)  # line 837
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))  # line 838
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 839
        _.assertTrue("./file2" in changes.modifications)  # line 840
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 841
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 842

    def testDiff(_):  # line 844
        try:  # manually mark this file as "textual"  # line 845
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 845
        except SystemExit as E:  # line 846
            _.assertEqual(0, E.code)  # line 846
        sos.offline(options=["--strict"])  # line 847
        _.createFile(1)  # line 848
        _.createFile(2)  # line 849
        sos.commit()  # line 850
        _.createFile(1, "sdfsdgfsdf")  # line 851
        _.createFile(2, "12343")  # line 852
        sos.commit()  # line 853
        _.createFile(1, "foobar")  # line 854
        _.createFile(3)  # line 855
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 856
        _.assertIn("ADD ./file3", out)  # line 857
        _.assertAllIn(["MOD ./file2", "DIF ./file1  <No newline>", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 858
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 859

    def testReorderRenameActions(_):  # line 861
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 862
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 863
        try:  # line 864
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 864
            _.fail()  # line 864
        except:  # line 865
            pass  # line 865

    def testMove(_):  # line 867
        sos.offline(options=["--strict", "--track"])  # line 868
        _.createFile(1)  # line 869
        sos.add(".", "./file?")  # line 870
# test source folder missing
        try:  # line 872
            sos.move("sub", "sub/file?", ".", "?file")  # line 872
            _.fail()  # line 872
        except:  # line 873
            pass  # line 873
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 875
        _.assertTrue(os.path.exists("sub"))  # line 876
        _.assertTrue(os.path.exists("sub/file1"))  # line 877
        _.assertFalse(os.path.exists("file1"))  # line 878
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 880
        _.assertTrue(os.path.exists("1file"))  # line 881
        _.assertFalse(os.path.exists("sub/file1"))  # line 882
# test nothing matches source pattern
        try:  # line 884
            sos.move(".", "a*", ".", "b*")  # line 884
            _.fail()  # line 884
        except:  # line 885
            pass  # line 885
        sos.add(".", "*")  # anything pattern  # line 886
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 887
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 887
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 887
        except:  # line 888
            pass  # line 888
# test rename no conflict
        _.createFile(1)  # line 890
        _.createFile(2)  # line 891
        _.createFile(3)  # line 892
        sos.add(".", "./file*")  # line 893
        try:  # define an ignore pattern  # line 894
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 894
        except SystemExit as E:  # line 895
            _.assertEqual(0, E.code)  # line 895
        try:  # line 896
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 896
        except SystemExit as E:  # line 897
            _.assertEqual(0, E.code)  # line 897
        sos.move(".", "./file*", ".", "fi*le")  # line 898
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 899
        _.assertFalse(os.path.exists("fi4le"))  # line 900
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 902
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 906
        sos.add(".", "./?a?b", ["--force"])  # line 907
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 908
        _.createFile("1a2b")  # should not be tracked  # line 909
        _.createFile("a1b2")  # should be tracked  # line 910
        sos.commit()  # line 911
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 912
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 913
        _.createFile("1a1b1")  # line 914
        _.createFile("1a1b2")  # line 915
        sos.add(".", "?a?b*")  # line 916
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 917
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 921
        sos.offline()  # line 922
        _.createFile(1)  # line 923
        os.mkdir(sos.branchFolder(0, 1))  # line 924
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.branchFolder(0, 1))  # line 925
        _.createFile(1)  # line 926
        try:  # should exit with error due to collision detection  # line 927
            sos.commit()  # should exit with error due to collision detection  # line 927
            _.fail()  # should exit with error due to collision detection  # line 927
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 928
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 928

    def testFindBase(_):  # line 930
        old = os.getcwd()  # line 931
        try:  # line 932
            os.mkdir("." + os.sep + ".git")  # line 933
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 934
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 935
            os.chdir("a" + os.sep + "b")  # line 936
            s, vcs, cmd = sos.findSosVcsBase()  # line 937
            _.assertIsNotNone(s)  # line 938
            _.assertIsNotNone(vcs)  # line 939
            _.assertEqual("git", cmd)  # line 940
        finally:  # line 941
            os.chdir(old)  # line 941

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail

# TODO test +++ --- in diff
# TODO test +01/-02/*..
# TODO tests for loadcommit redirection

if __name__ == '__main__':  # line 950
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 951
    c = configr.Configr("sos")  # line 952
    c.loadSettings()  # line 953
    if len(c.keys()) > 0:  # line 954
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 954
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 955
