#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xab425ed3

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
        del repo["format"]  # simulate pre-1.4  # line 175
        repo["version"] = "0"  # line 176
        branches[:] = [branch[:-1] for branch in branches]  # line 177
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "w", encoding=sos.UTF8) as fd:  # line 178
            json.dump((repo, branches, config), fd, ensure_ascii=False)  # line 178
        out = wrapChannels(lambda: sos.status(options=["--repo"]))  # line 179
        _.assertAllIn(["Upgraded repository metadata to match SOS version '2018.1210.3028'", "Upgraded repository metadata to match SOS version '1.4'"], out)  # line 180

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
        m.computeSequentialPathSet(0, 4)  # line 260
        _.assertEqual(2, len(m.paths))  # line 261

    def testParseRevisionString(_):  # line 263
        m = sos.Metadata(os.getcwd())  # line 264
        m.branch = 1  # line 265
        m.commits = {0: 0, 1: 1, 2: 2}  # line 266
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 267
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 268
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 269
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 270
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 271
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 272
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 273

    def testOfflineEmpty(_):  # line 275
        os.mkdir("." + os.sep + sos.metaFolder)  # line 276
        try:  # line 277
            sos.offline("trunk")  # line 277
            _.fail()  # line 277
        except SystemExit as E:  # line 278
            _.assertEqual(1, E.code)  # line 278
        os.rmdir("." + os.sep + sos.metaFolder)  # line 279
        sos.offline("test")  # line 280
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 281
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 282
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 283
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 284
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 285
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file  # line 286

    def testOfflineWithFiles(_):  # line 288
        _.createFile(1, "x" * 100)  # line 289
        _.createFile(2)  # line 290
        sos.offline("test")  # line 291
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 292
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 293
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 294
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 295
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 296
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 297
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 0))))  # only meta data file plus branch base file copies  # line 298

    def testBranch(_):  # line 300
        _.createFile(1, "x" * 100)  # line 301
        _.createFile(2)  # line 302
        sos.offline("test")  # b0/r0  # line 303
        sos.branch("other")  # b1/r0  # line 304
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 305
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 306
        _.assertEqual(list(sorted(os.listdir(sos.branchFolder(0, 0)))), list(sorted(os.listdir(sos.branchFolder(1, 0)))))  # line 308
        _.createFile(1, "z")  # modify file  # line 310
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 311
        _.assertNotEqual(os.stat("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size, os.stat("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa").st_size)  # line 312
        _.createFile(3, "z")  # line 314
        sos.branch("from_last_revision", ["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 315
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 316
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 321
        _.createFile(1, "x" * 100)  # line 322
        _.createFile(2)  # line 323
        sos.offline("test")  # line 324
        changes = sos.changes()  # line 325
        _.assertEqual(0, len(changes.additions))  # line 326
        _.assertEqual(0, len(changes.deletions))  # line 327
        _.assertEqual(0, len(changes.modifications))  # line 328
        _.createFile(1, "z")  # size change  # line 329
        changes = sos.changes()  # line 330
        _.assertEqual(0, len(changes.additions))  # line 331
        _.assertEqual(0, len(changes.deletions))  # line 332
        _.assertEqual(1, len(changes.modifications))  # line 333
        sos.commit("message")  # line 334
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 335
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.branchFolder(0, 1)))  # line 336
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # no further files, only the modified one  # line 337
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 338
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 339
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 340
        os.unlink("file2")  # line 341
        changes = sos.changes()  # line 342
        _.assertEqual(0, len(changes.additions))  # line 343
        _.assertEqual(1, len(changes.deletions))  # line 344
        _.assertEqual(1, len(changes.modifications))  # line 345
        sos.commit("modified")  # line 346
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # no additional files, only mentions in metadata  # line 347
        try:  # expecting Exit due to no changes  # line 348
            sos.commit("nothing")  # expecting Exit due to no changes  # line 348
            _.fail()  # expecting Exit due to no changes  # line 348
        except:  # line 349
            pass  # line 349

    def testGetBranch(_):  # line 351
        m = sos.Metadata(os.getcwd())  # line 352
        m.branch = 1  # current branch  # line 353
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 354
        _.assertEqual(27, m.getBranchByName(27))  # line 355
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 356
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 357
        _.assertIsNone(m.getBranchByName("unknown"))  # line 358
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 359
        _.assertEqual(13, m.getRevisionByName("13"))  # line 360
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 361
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 362

    def testTagging(_):  # line 364
        m = sos.Metadata(os.getcwd())  # line 365
        sos.offline()  # line 366
        _.createFile(111)  # line 367
        sos.commit("tag", ["--tag"])  # line 368
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 369
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 370
        _.createFile(2)  # line 371
        try:  # line 372
            sos.commit("tag")  # line 372
            _.fail()  # line 372
        except:  # line 373
            pass  # line 373
        sos.commit("tag-2", ["--tag"])  # line 374
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 375
        _.assertIn("TAG tag", out)  # line 376

    def testSwitch(_):  # line 378
        _.createFile(1, "x" * 100)  # line 379
        _.createFile(2, "y")  # line 380
        sos.offline("test")  # file1-2  in initial branch commit  # line 381
        sos.branch("second")  # file1-2  switch, having same files  # line 382
        sos.switch("0")  # no change  switch back, no problem  # line 383
        sos.switch("second")  # no change  # switch back, no problem  # line 384
        _.createFile(3, "y")  # generate a file  # line 385
        try:  # uncommited changes detected  # line 386
            sos.switch("test")  # uncommited changes detected  # line 386
            _.fail()  # uncommited changes detected  # line 386
        except SystemExit as E:  # line 387
            _.assertEqual(1, E.code)  # line 387
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 388
        sos.changes()  # line 389
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 390
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 391
        _.createFile("XXX")  # line 392
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 393
        _.assertIn("File tree has changes", out)  # line 394
        _.assertNotIn("File tree is unchanged", out)  # line 395
        _.assertIn("  * b00   'test'", out)  # line 396
        _.assertIn("    b01 'second'", out)  # line 397
        _.assertIn("(dirty)", out)  # one branch has commits  # line 398
        _.assertIn("(in sync)", out)  # the other doesn't  # line 399
        _.createFile(4, "xy")  # generate a file  # line 400
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4  # line 401
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 402
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 403
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 404
        sos.switch("test", ["--force"])  # should restore file1 and remove file3  # line 405
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 406
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 407

    def testAutoDetectVCS(_):  # line 409
        os.mkdir(".git")  # line 410
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 411
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 412
            meta = fd.read()  # line 412
        _.assertTrue("\"master\"" in meta)  # line 413
        os.rmdir(".git")  # line 414

    def testUpdate(_):  # line 416
        sos.offline("trunk")  # create initial branch b0/r0  # line 417
        _.createFile(1, "x" * 100)  # line 418
        sos.commit("second")  # create b0/r1  # line 419

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 421
        _.assertFalse(_.existsFile(1))  # line 422

        sos.update("/1")  # recreate file1  # line 424
        _.assertTrue(_.existsFile(1))  # line 425

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 427
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2)))  # line 428
        _.assertTrue(os.path.exists(sos.branchFolder(0, 2, file=sos.metaFile)))  # line 429
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 2))))  # only meta data file, no differential files  # line 430

        sos.update("/1")  # do nothing, as nothing has changed  # line 432
        _.assertTrue(_.existsFile(1))  # line 433

        _.createFile(2, "y" * 100)  # line 435
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", ["--force"])  # automatically including file 2 (as we are in simple mode)  # line 438
        _.assertTrue(_.existsFile(2))  # line 439
        sos.update("trunk", ["--add"])  # only add stuff  # line 440
        _.assertTrue(_.existsFile(2))  # line 441
        sos.update("trunk")  # nothing to do  # line 442
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 443

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 445
        _.createFile(10, theirs)  # line 446
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 447
        _.createFile(11, mine)  # line 448
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 449
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 450

    def testUpdate2(_):  # line 452
        _.createFile("test.txt", "x" * 10)  # line 453
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 454
        sos.branch("mod")  # line 455
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 456
        time.sleep(FS_PRECISION)  # line 457
        sos.commit("mod")  # create b0/r1  # line 458
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 459
        with open("test.txt", "rb") as fd:  # line 460
            _.assertEqual(b"x" * 10, fd.read())  # line 460
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 461
        with open("test.txt", "rb") as fd:  # line 462
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 462
        _.createFile("test.txt", "x" * 10)  # line 463
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 464
        with open("test.txt", "rb") as fd:  # line 465
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 465
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 466
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 467
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 468
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 469
        with open("test.txt", "rb") as fd:  # line 470
            _.assertEqual(b"x" * 5 + b"y" * 5, fd.read())  # line 470

    def testIsTextType(_):  # line 472
        m = sos.Metadata(".")  # line 473
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 474
        m.c.bintype = ["*.md.confluence"]  # line 475
        _.assertTrue(m.isTextType("ab.txt"))  # line 476
        _.assertTrue(m.isTextType("./ab.txt"))  # line 477
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 478
        _.assertFalse(m.isTextType("bc/ab."))  # line 479
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 480
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 481
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 482
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 483

    def testEolDet(_):  # line 485
        ''' Check correct end-of-line detection. '''  # line 486
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 487
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 488
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 489
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 490
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 491
        _.assertIsNone(sos.eoldet(b""))  # line 492
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 493

    def testMerge(_):  # line 495
        ''' Check merge results depending on user options. '''  # line 496
        a = b"a\nb\ncc\nd"  # type: bytes  # line 497
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 498
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge  # line 499
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace  # line 500
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace  # line 501
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge  # line 502
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 503
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 504
        a = b"a\nb\ncc\nd"  # line 505
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 506
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement  # line 507
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # line 508
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 509
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])  # line 511
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 512
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 514
        b = b"a\nc\ne"  # line 515
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 516
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 517
        a = b"a\nb\ne"  # intra-line merge  # line 518
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 519
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 520

    def testMergeEol(_):  # line 522
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])  # line 523
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 524
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF  # line 525
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])  # line 526
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])  # line 527

    def testPickyMode(_):  # line 529
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 530
        sos.offline("trunk", ["--picky"])  # line 531
        changes = sos.changes()  # line 532
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 533
        sos.add(".", "./file?", ["--force"])  # line 534
        _.createFile(1, "aa")  # line 535
        sos.commit("First")  # add one file  # line 536
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 537
        _.createFile(2, "b")  # line 538
        try:  # add nothing, because picky  # line 539
            sos.commit("Second")  # add nothing, because picky  # line 539
        except:  # line 540
            pass  # line 540
        sos.add(".", "./file?")  # line 541
        sos.commit("Third")  # line 542
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # line 543
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 544
        _.assertIn("  * r2", out)  # line 545
        _.createFile(3, prefix="sub")  # line 546
        sos.add("sub", "sub/file?")  # line 547
        changes = sos.changes()  # line 548
        _.assertEqual(1, len(changes.additions))  # line 549
        _.assertTrue("sub/file3" in changes.additions)  # line 550

    def testTrackedSubfolder(_):  # line 552
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 553
        os.mkdir("." + os.sep + "sub")  # line 554
        sos.offline("trunk", ["--track"])  # line 555
        _.createFile(1, "x")  # line 556
        _.createFile(1, "x", prefix="sub")  # line 557
        sos.add(".", "./file?")  # add glob pattern to track  # line 558
        sos.commit("First")  # line 559
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 560
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 561
        sos.commit("Second")  # one new file + meta  # line 562
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 563
        os.unlink("file1")  # remove from basefolder  # line 564
        _.createFile(2, "y")  # line 565
        sos.remove(".", "sub/file?")  # line 566
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 567
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 567
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 567
        except:  # line 568
            pass  # line 568
        sos.commit("Third")  # line 569
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta  # line 570
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 573
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 578
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 579
        _.createFile(1)  # line 580
        _.createFile("a123a")  # untracked file "a123a"  # line 581
        sos.add(".", "./file?")  # add glob tracking pattern  # line 582
        sos.commit("second")  # versions "file1"  # line 583
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # one new file + meta file  # line 584
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 585
        _.assertIn("  | ./file?", out)  # line 586

        _.createFile(2)  # untracked file "file2"  # line 588
        sos.commit("third")  # versions "file2"  # line 589
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # one new file + meta file  # line 590

        os.mkdir("." + os.sep + "sub")  # line 592
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 593
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 594
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 3))))  # meta file only, no other tracked path/file  # line 595

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 597
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 598
        sos.add(".", "./a*a")  # add tracking pattern  # line 599
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 600
        _.assertEqual(0, len(changes.modifications))  # line 601
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 602
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 603

        sos.commit("Second_2")  # line 605
        _.assertEqual(2, len(os.listdir(sos.branchFolder(1, 1))))  # "a123a" + meta file  # line 606
        _.existsFile(1, b"x" * 10)  # line 607
        _.existsFile(2, b"x" * 10)  # line 608

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 610
        _.existsFile(1, b"x" * 10)  # line 611
        _.existsFile("a123a", b"x" * 10)  # line 612

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 614
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 615
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 616

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 618
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 619
        _.assertEqual(3, len(os.listdir(sos.branchFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 620
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 621
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 622
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 623
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 624
# TODO test switch --meta

    def testLsTracked(_):  # line 627
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 628
        _.createFile(1)  # line 629
        _.createFile("foo")  # line 630
        sos.add(".", "./file*")  # capture one file  # line 631
        sos.ls()  # line 632
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 633
        _.assertInAny("TRK file1  (file*)", out)  # line 634
        _.assertNotInAny("... file1  (file*)", out)  # line 635
        _.assertInAny("··· foo", out)  # line 636
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 637
        _.assertInAny("TRK file*", out)  # line 638
        _.createFile("a", prefix="sub")  # line 639
        sos.add("sub", "sub/a")  # line 640
        sos.ls("sub")  # line 641
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 642

    def testLineMerge(_):  # line 644
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 645
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 646
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 647
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 648

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 650
        _.createFile(1)  # line 651
        sos.offline("master", options=["--force"])  # line 652
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 653
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 654
        _.assertTrue(_.existsFile(sos.branchFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 655
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 656
        _.createFile(2)  # line 657
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 658
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 659
        _.assertTrue(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 660
        _.assertFalse(_.existsFile(sos.branchFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 661

    def testLocalConfig(_):  # line 663
        sos.offline("bla", options=[])  # line 664
        try:  # line 665
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 665
        except SystemExit as E:  # line 666
            _.assertEqual(0, E.code)  # line 666
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 667

    def testConfigVariations(_):  # line 669
        def makeRepo():  # line 670
            try:  # line 671
                os.unlink("file1")  # line 671
            except:  # line 672
                pass  # line 672
            sos.offline("master", options=["--force"])  # line 673
            _.createFile(1)  # line 674
            sos.commit("Added file1")  # line 675
        try:  # line 676
            sos.config(["set", "strict", "on"])  # line 676
        except SystemExit as E:  # line 677
            _.assertEqual(0, E.code)  # line 677
        makeRepo()  # line 678
        _.assertTrue(checkRepoFlag("strict", True))  # line 679
        try:  # line 680
            sos.config(["set", "strict", "off"])  # line 680
        except SystemExit as E:  # line 681
            _.assertEqual(0, E.code)  # line 681
        makeRepo()  # line 682
        _.assertTrue(checkRepoFlag("strict", False))  # line 683
        try:  # line 684
            sos.config(["set", "strict", "yes"])  # line 684
        except SystemExit as E:  # line 685
            _.assertEqual(0, E.code)  # line 685
        makeRepo()  # line 686
        _.assertTrue(checkRepoFlag("strict", True))  # line 687
        try:  # line 688
            sos.config(["set", "strict", "no"])  # line 688
        except SystemExit as E:  # line 689
            _.assertEqual(0, E.code)  # line 689
        makeRepo()  # line 690
        _.assertTrue(checkRepoFlag("strict", False))  # line 691
        try:  # line 692
            sos.config(["set", "strict", "1"])  # line 692
        except SystemExit as E:  # line 693
            _.assertEqual(0, E.code)  # line 693
        makeRepo()  # line 694
        _.assertTrue(checkRepoFlag("strict", True))  # line 695
        try:  # line 696
            sos.config(["set", "strict", "0"])  # line 696
        except SystemExit as E:  # line 697
            _.assertEqual(0, E.code)  # line 697
        makeRepo()  # line 698
        _.assertTrue(checkRepoFlag("strict", False))  # line 699
        try:  # line 700
            sos.config(["set", "strict", "true"])  # line 700
        except SystemExit as E:  # line 701
            _.assertEqual(0, E.code)  # line 701
        makeRepo()  # line 702
        _.assertTrue(checkRepoFlag("strict", True))  # line 703
        try:  # line 704
            sos.config(["set", "strict", "false"])  # line 704
        except SystemExit as E:  # line 705
            _.assertEqual(0, E.code)  # line 705
        makeRepo()  # line 706
        _.assertTrue(checkRepoFlag("strict", False))  # line 707
        try:  # line 708
            sos.config(["set", "strict", "enable"])  # line 708
        except SystemExit as E:  # line 709
            _.assertEqual(0, E.code)  # line 709
        makeRepo()  # line 710
        _.assertTrue(checkRepoFlag("strict", True))  # line 711
        try:  # line 712
            sos.config(["set", "strict", "disable"])  # line 712
        except SystemExit as E:  # line 713
            _.assertEqual(0, E.code)  # line 713
        makeRepo()  # line 714
        _.assertTrue(checkRepoFlag("strict", False))  # line 715
        try:  # line 716
            sos.config(["set", "strict", "enabled"])  # line 716
        except SystemExit as E:  # line 717
            _.assertEqual(0, E.code)  # line 717
        makeRepo()  # line 718
        _.assertTrue(checkRepoFlag("strict", True))  # line 719
        try:  # line 720
            sos.config(["set", "strict", "disabled"])  # line 720
        except SystemExit as E:  # line 721
            _.assertEqual(0, E.code)  # line 721
        makeRepo()  # line 722
        _.assertTrue(checkRepoFlag("strict", False))  # line 723
        try:  # line 724
            sos.config(["set", "strict", "nope"])  # line 724
            _.fail()  # line 724
        except SystemExit as E:  # line 725
            _.assertEqual(1, E.code)  # line 725

    def testLsSimple(_):  # line 727
        _.createFile(1)  # line 728
        _.createFile("foo")  # line 729
        _.createFile("ign1")  # line 730
        _.createFile("ign2")  # line 731
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 732
        try:  # define an ignore pattern  # line 733
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 733
        except SystemExit as E:  # line 734
            _.assertEqual(0, E.code)  # line 734
        try:  # additional ignore pattern  # line 735
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 735
        except SystemExit as E:  # line 736
            _.assertEqual(0, E.code)  # line 736
        try:  # define a list of ignore patterns  # line 737
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 737
        except SystemExit as E:  # line 738
            _.assertEqual(0, E.code)  # line 738
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 739
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 740
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 741
        _.assertInAny('··· file1', out)  # line 742
        _.assertInAny('··· ign1', out)  # line 743
        _.assertInAny('··· ign2', out)  # line 744
        try:  # line 745
            sos.config(["rm", "foo", "bar"])  # line 745
            _.fail()  # line 745
        except SystemExit as E:  # line 746
            _.assertEqual(1, E.code)  # line 746
        try:  # line 747
            sos.config(["rm", "ignores", "foo"])  # line 747
            _.fail()  # line 747
        except SystemExit as E:  # line 748
            _.assertEqual(1, E.code)  # line 748
        try:  # line 749
            sos.config(["rm", "ignores", "ign1"])  # line 749
        except SystemExit as E:  # line 750
            _.assertEqual(0, E.code)  # line 750
        try:  # remove ignore pattern  # line 751
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 751
        except SystemExit as E:  # line 752
            _.assertEqual(0, E.code)  # line 752
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 753
        _.assertInAny('··· ign1', out)  # line 754
        _.assertInAny('IGN ign2', out)  # line 755
        _.assertNotInAny('··· ign2', out)  # line 756

    def testWhitelist(_):  # line 758
# TODO test same for simple mode
        _.createFile(1)  # line 760
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 761
        sos.offline("xx", ["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 762
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 763
        sos.commit(options=["--force"])  # attempt to commit the file  # line 764
        _.assertEqual(1, len(os.listdir(sos.branchFolder(0, 1))))  # only meta data, file1 was ignored  # line 765
        try:  # Exit because dirty  # line 766
            sos.online()  # Exit because dirty  # line 766
            _.fail()  # Exit because dirty  # line 766
        except:  # exception expected  # line 767
            pass  # exception expected  # line 767
        _.createFile("x2")  # add another change  # line 768
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 769
        try:  # force beyond dirty flag check  # line 770
            sos.online(["--force"])  # force beyond dirty flag check  # line 770
            _.fail()  # force beyond dirty flag check  # line 770
        except:  # line 771
            pass  # line 771
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 772
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 773

        _.createFile(1)  # line 775
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 776
        sos.offline("xx", ["--track"])  # line 777
        sos.add(".", "./file*")  # line 778
        sos.commit()  # should NOT ask for force here  # line 779
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 780

    def testRemove(_):  # line 782
        _.createFile(1, "x" * 100)  # line 783
        sos.offline("trunk")  # line 784
        try:  # line 785
            sos.delete("trunk")  # line 785
            _fail()  # line 785
        except:  # line 786
            pass  # line 786
        _.createFile(2, "y" * 10)  # line 787
        sos.branch("added")  # creates new branch, writes repo metadata, and therefore creates backup copy  # line 788
        sos.delete("trunk")  # line 789
        _.assertEqual(3, len(os.listdir("." + os.sep + sos.metaFolder)))  # meta data file, backup and "b1"  # line 790
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 791
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 792
        sos.branch("next")  # line 793
        _.createFile(3, "y" * 10)  # make a change  # line 794
        sos.delete("added", "--force")  # should succeed  # line 795

    def testUsage(_):  # line 797
        try:  # TODO expect sys.exit(0)  # line 798
            sos.usage()  # TODO expect sys.exit(0)  # line 798
            _.fail()  # TODO expect sys.exit(0)  # line 798
        except:  # line 799
            pass  # line 799
        try:  # line 800
            sos.usage(short=True)  # line 800
            _.fail()  # line 800
        except:  # line 801
            pass  # line 801

    def testOnlyExcept(_):  # line 803
        ''' Test blacklist glob rules. '''  # line 804
        sos.offline(options=["--track"])  # line 805
        _.createFile("a.1")  # line 806
        _.createFile("a.2")  # line 807
        _.createFile("b.1")  # line 808
        _.createFile("b.2")  # line 809
        sos.add(".", "./a.?")  # line 810
        sos.add(".", "./?.1", negative=True)  # line 811
        out = wrapChannels(lambda: sos.commit())  # line 812
        _.assertIn("ADD ./a.2", out)  # line 813
        _.assertNotIn("ADD ./a.1", out)  # line 814
        _.assertNotIn("ADD ./b.1", out)  # line 815
        _.assertNotIn("ADD ./b.2", out)  # line 816

    def testOnly(_):  # line 818
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 819
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 820
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 821
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 822
        sos.offline(options=["--track", "--strict"])  # line 823
        _.createFile(1)  # line 824
        _.createFile(2)  # line 825
        sos.add(".", "./file1")  # line 826
        sos.add(".", "./file2")  # line 827
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 828
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # only meta and file1  # line 829
        sos.commit()  # adds also file2  # line 830
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 2))))  # only meta and file1  # line 831
        _.createFile(1, "cc")  # modify both files  # line 832
        _.createFile(2, "dd")  # line 833
        try:  # line 834
            sos.config(["set", "texttype", "file2"])  # line 834
        except SystemExit as E:  # line 835
            _.assertEqual(0, E.code)  # line 835
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))  # line 836
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 837
        _.assertTrue("./file2" in changes.modifications)  # line 838
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 839
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 840

    def testDiff(_):  # line 842
        try:  # manually mark this file as "textual"  # line 843
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 843
        except SystemExit as E:  # line 844
            _.assertEqual(0, E.code)  # line 844
        sos.offline(options=["--strict"])  # line 845
        _.createFile(1)  # line 846
        _.createFile(2)  # line 847
        sos.commit()  # line 848
        _.createFile(1, "sdfsdgfsdf")  # line 849
        _.createFile(2, "12343")  # line 850
        sos.commit()  # line 851
        _.createFile(1, "foobar")  # line 852
        _.createFile(3)  # line 853
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 854
        _.assertIn("ADD ./file3", out)  # line 855
        _.assertAllIn(["MOD ./file2", "DIF ./file1  <No newline>", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 856
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 857

    def testReorderRenameActions(_):  # line 859
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 860
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 861
        try:  # line 862
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 862
            _.fail()  # line 862
        except:  # line 863
            pass  # line 863

    def testMove(_):  # line 865
        sos.offline(options=["--strict", "--track"])  # line 866
        _.createFile(1)  # line 867
        sos.add(".", "./file?")  # line 868
# test source folder missing
        try:  # line 870
            sos.move("sub", "sub/file?", ".", "?file")  # line 870
            _.fail()  # line 870
        except:  # line 871
            pass  # line 871
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 873
        _.assertTrue(os.path.exists("sub"))  # line 874
        _.assertTrue(os.path.exists("sub/file1"))  # line 875
        _.assertFalse(os.path.exists("file1"))  # line 876
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 878
        _.assertTrue(os.path.exists("1file"))  # line 879
        _.assertFalse(os.path.exists("sub/file1"))  # line 880
# test nothing matches source pattern
        try:  # line 882
            sos.move(".", "a*", ".", "b*")  # line 882
            _.fail()  # line 882
        except:  # line 883
            pass  # line 883
        sos.add(".", "*")  # anything pattern  # line 884
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 885
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 885
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 885
        except:  # line 886
            pass  # line 886
# test rename no conflict
        _.createFile(1)  # line 888
        _.createFile(2)  # line 889
        _.createFile(3)  # line 890
        sos.add(".", "./file*")  # line 891
        try:  # define an ignore pattern  # line 892
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 892
        except SystemExit as E:  # line 893
            _.assertEqual(0, E.code)  # line 893
        try:  # line 894
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 894
        except SystemExit as E:  # line 895
            _.assertEqual(0, E.code)  # line 895
        sos.move(".", "./file*", ".", "fi*le")  # line 896
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 897
        _.assertFalse(os.path.exists("fi4le"))  # line 898
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 900
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 904
        sos.add(".", "./?a?b", ["--force"])  # line 905
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 906
        _.createFile("1a2b")  # should not be tracked  # line 907
        _.createFile("a1b2")  # should be tracked  # line 908
        sos.commit()  # line 909
        _.assertEqual(2, len(os.listdir(sos.branchFolder(0, 1))))  # line 910
        _.assertTrue(os.path.exists(sos.branchFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 911
        _.createFile("1a1b1")  # line 912
        _.createFile("1a1b2")  # line 913
        sos.add(".", "?a?b*")  # line 914
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 915
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 919
        sos.offline()  # line 920
        _.createFile(1)  # line 921
        os.mkdir(sos.branchFolder(0, 1))  # line 922
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.branchFolder(0, 1))  # line 923
        _.createFile(1)  # line 924
        try:  # should exit with error due to collision detection  # line 925
            sos.commit()  # should exit with error due to collision detection  # line 925
            _.fail()  # should exit with error due to collision detection  # line 925
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 926
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 926

    def testFindBase(_):  # line 928
        old = os.getcwd()  # line 929
        try:  # line 930
            os.mkdir("." + os.sep + ".git")  # line 931
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 932
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 933
            os.chdir("a" + os.sep + "b")  # line 934
            s, vcs, cmd = sos.findSosVcsBase()  # line 935
            _.assertIsNotNone(s)  # line 936
            _.assertIsNotNone(vcs)  # line 937
            _.assertEqual("git", cmd)  # line 938
        finally:  # line 939
            os.chdir(old)  # line 939

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail

# TODO test +++ --- in diff
# TODO test +01/-02/*..

if __name__ == '__main__':  # line 947
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 948
    c = configr.Configr("sos")  # line 949
    c.loadSettings()  # line 950
    if len(c.keys()) > 0:  # line 951
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 951
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 952
