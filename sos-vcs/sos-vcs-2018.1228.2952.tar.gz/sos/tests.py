#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x7f845d34

# Compiled with Coconut version 1.3.1-post_dev23 [Dead Parrot]

# Coconut Header: -------------------------------------------------------------

import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_cached_module = _coconut_sys.modules.get("__coconut__")
if _coconut_cached_module is not None and _coconut_os_path.dirname(_coconut_cached_module.__file__) != _coconut_file_path:
    del _coconut_sys.modules["__coconut__"]
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_NamedTuple, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_pipe, _coconut_star_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: -----------------------------------------------------------

# Copyright Arne Bachmann
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

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

try:  # line 7
    if TYPE_CHECKING:  # true only during compilation/mypy run  # line 8
        from typing import *  # line 9
        mock = None  # type: Any  # to avoid mypy complaint  # line 10
except:  # line 11
    pass  # line 11

try:  # Python 3  # line 13
    from unittest import mock  # Python 3  # line 13
except:  # installed via pip  # line 14
    import mock  # installed via pip  # line 14

testFolder = os.path.abspath(os.path.join(os.getcwd(), "test"))  # this needs to be set before the configr and sos imports  # line 16
os.environ["TEST"] = testFolder  # needed to mock configr library calls in sos  # line 17

import configr  # line 19
import sos  # import of package, not file  # line 20

sos.defaults["defaultbranch"] = "trunk"  # because sos.main() is never called  # line 22
sos.defaults["useChangesCommand"] = True  # because sos.main() is never called  # line 23
sos.defaults["useUnicodeFont"] = False  # because sos.main() is never called  # line 24


def determineFilesystemTimeResolution() -> 'float':  # line 27
    name = str(uuid.uuid4())  # type: str  # line 28
    with open(name, "w") as fd:  # create temporary file  # line 29
        fd.write("x")  # create temporary file  # line 29
    mt = os.stat(sos.encode(name)).st_mtime  # type: float  # get current timestamp  # line 30
    while os.stat(sos.encode(name)).st_mtime == mt:  # wait until timestamp modified  # line 31
        time.sleep(0.05)  # to avoid 0.00s bugs (came up some time for unknown reasons)  # line 32
        with open(name, "w") as fd:  # line 33
            fd.write("x")  # line 33
    mt, start, _count = os.stat(sos.encode(name)).st_mtime, time.time(), 0  # line 34
    while os.stat(sos.encode(name)).st_mtime == mt:  # now cound and measure time until modified again  # line 35
        time.sleep(0.05)  # line 36
        _count += 1  # line 37
        with open(name, "w") as fd:  # line 38
            fd.write("x")  # line 38
    os.unlink(name)  # line 39
    fsprecision = round(time.time() - start, 2)  # type: float  # line 40
    print("File system timestamp precision is %s%.2fs; wrote to the file %d times during that time" % ("probably even higher than " if fsprecision == 0.05 else "", fsprecision, _count))  # line 41
    return fsprecision  # line 42


FS_PRECISION = determineFilesystemTimeResolution() * 1.55  # line 45

def sync():  # line 47
    if sys.version_info[:2] >= (3, 3):  # line 48
        try:  # only Linux  # line 49
            os.sync()  # only Linux  # line 49
        except:  # line 50
            pass  # line 50
    time.sleep(FS_PRECISION)  # line 51


@_coconut_tco  # line 54
def debugTestRunner(post_mortem=None):  # line 54
    ''' Unittest runner doing post mortem debugging on failing tests. '''  # line 55
    import pdb  # line 56
    if post_mortem is None:  # line 57
        post_mortem = pdb.post_mortem  # line 57
    class DebugTestResult(unittest.TextTestResult):  # line 58
        def addError(_, test, err):  # called before tearDown()  # line 59
            traceback.print_exception(*err)  # line 60
            post_mortem(err[2])  # line 61
            super(DebugTestResult, _).addError(test, err)  # line 62
        def addFailure(_, test, err):  # line 63
            traceback.print_exception(*err)  # line 64
            post_mortem(err[2])  # line 65
            super(DebugTestResult, _).addFailure(test, err)  # line 66
    return _coconut_tail_call(unittest.TextTestRunner, resultclass=DebugTestResult)  # line 67

@_coconut_tco  # line 69
def wrapChannels(func: '_coconut.typing.Callable[..., Any]') -> 'str':  # line 69
    ''' Wrap function call to capture and return strings emitted on stdout and stderr. '''  # line 70
    oldv = sys.argv  # line 71
    buf = TextIOWrapper(BufferedRandom(BytesIO(b"")), encoding=sos.UTF8)  # line 72
    handler = logging.StreamHandler(buf)  # TODO doesn't seem to be captured  # line 73
    sys.stdout = sys.stderr = buf  # line 74
    logging.getLogger().setLevel(logging.DEBUG)  # line 75
    logging.getLogger().addHandler(handler)  # line 76
    try:  # capture output into buf  # line 77
        func()  # capture output into buf  # line 77
    except Exception as E:  # line 78
        buf.write(str(E) + "\n")  # line 78
        traceback.print_exc(file=buf)  # line 78
    except SystemExit as F:  # line 79
        buf.write("EXIT CODE %s" % F.code + "\n")  # line 79
        traceback.print_exc(file=buf)  # line 79
    logging.getLogger().setLevel(logging.INFO)  # line 80
    logging.getLogger().removeHandler(handler)  # line 81
    sys.argv, sys.stdout, sys.stderr = oldv, sys.__stdout__, sys.__stderr__  # TODO when run using pythonw.exe and/or no console, these could be None  # line 82
    buf.seek(0)  # line 83
    return _coconut_tail_call(buf.read)  # line 84

def mockInput(datas: '_coconut.typing.Sequence[str]', func: '_coconut.typing.Callable[..., Any]') -> 'Any':  # line 86
    if sos.coco_version < (1, 3, 1, 21):  # line 87
        import builtins  # line 88
        with mock.patch("builtins.input", side_effect=datas):  # line 89
            return func()  # line 89
    else:  # line 90
        with mock.patch("sos._utility.input", side_effect=datas):  # line 91
            return func()  # line 91

def setRepoFlag(name: 'str', value: 'bool'):  # line 93
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 94
        flags, branches, config = json.loads(fd.read())  # line 94
    flags[name] = value  # line 95
    with open(sos.metaFolder + os.sep + sos.metaFile, "w") as fd:  # line 96
        fd.write(json.dumps((flags, branches, config)))  # line 96

def checkRepoFlag(name: 'str', flag: '_coconut.typing.Optional[bool]'=None, value: '_coconut.typing.Optional[Any]'=None) -> 'bool':  # line 98
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 99
        flags, branches, config = json.loads(fd.read())  # line 99
    return (name in flags and flags[name] == flag) if flag is not None else (name in config and config[name] == value)  # line 100


class Tests(unittest.TestCase):  # line 103
    ''' Entire test suite. '''  # line 104

    def setUp(_):  # line 106
        sos.Metadata.singleton = None  # line 107
        for entry in os.listdir(testFolder):  # cannot remove testFolder on Windows when using TortoiseSVN as VCS  # line 108
            resource = os.path.join(testFolder, entry)  # line 109
            shutil.rmtree(sos.encode(resource)) if os.path.isdir(sos.encode(resource)) else os.unlink(sos.encode(resource))  # line 110
        os.chdir(testFolder)  # line 111


    def assertAllIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]', only: 'bool'=False):  # line 114
        for w in what:  # line 115
            _.assertIn(w, where)  # line 115
        if only:  # line 116
            _.assertEqual(len(what), len(where))  # line 116

    def assertAllNotIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]'):  # line 118
        for w in what:  # line 119
            _.assertNotIn(w, where)  # line 119

    def assertInAll(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 121
        for w in where:  # line 122
            _.assertIn(what, w)  # line 122

    def assertInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 124
        _.assertTrue(any((what in w for w in where)))  # line 124

    def assertNotInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 126
        _.assertFalse(any((what in w for w in where)))  # line 126

    def createFile(_, number: 'Union[int, str]', contents: 'str'="x" * 10, prefix: '_coconut.typing.Optional[str]'=None):  # line 128
        if prefix and not os.path.exists(prefix):  # line 129
            os.makedirs(prefix)  # line 129
        with open(("." if prefix is None else prefix) + os.sep + (("file%d" % number) if isinstance(number, int) else number), "wb") as fd:  # line 130
            fd.write(contents if isinstance(contents, bytes) else contents.encode("cp1252"))  # line 130
        sync()  # line 131

    def existsFile(_, number: 'Union[int, str]', expectedContents: 'bytes'=None) -> 'bool':  # line 133
        sync()  # line 134
        if not os.path.exists(("." + os.sep + "file%d" % number) if isinstance(number, int) else number):  # line 135
            return False  # line 135
        if expectedContents is None:  # line 136
            return True  # line 136
        with open(("." + os.sep + "file%d" % number) if isinstance(number, int) else number, "rb") as fd:  # line 137
            return fd.read() == expectedContents  # line 137

    def testAccessor(_):  # line 139
        a = sos.Accessor({"a": 1})  # line 140
        _.assertEqual((1, 1), (a["a"], a.a))  # line 141

    def testRestoreFile(_):  # line 143
        m = sos.Metadata()  # line 144
        os.makedirs(sos.revisionFolder(0, 0))  # line 145
        _.createFile("hashed_file", "content", sos.revisionFolder(0, 0))  # line 146
        m.restoreFile(relPath="restored", branch=0, revision=0, pinfo=sos.PathInfo("hashed_file", 0, (time.time() - 2000) * 1000, "content hash"))  # line 147
        _.assertTrue(_.existsFile("restored", b""))  # line 148

    def testGetAnyOfmap(_):  # line 150
        _.assertEqual(2, sos.getAnyOfMap({"a": 1, "b": 2}, ["x", "b"]))  # line 151
        _.assertIsNone(sos.getAnyOfMap({"a": 1, "b": 2}, []))  # line 152

    def testAjoin(_):  # line 154
        _.assertEqual("a1a2", sos.ajoin("a", ["1", "2"]))  # line 155
        _.assertEqual("* a\n* b", sos.ajoin("* ", ["a", "b"], "\n"))  # line 156

    def testFindChanges(_):  # line 158
        m = sos.Metadata(os.getcwd())  # line 159
        try:  # line 160
            sos.config(["set", "texttype", "*"])  # line 160
        except SystemExit as E:  # line 161
            _.assertEqual(0, E.code)  # line 161
        try:  # will be stripped from leading paths anyway  # line 162
            sos.config(["set", "ignores", "test/*.cfg;D:\\apps\\*.cfg.bak"])  # will be stripped from leading paths anyway  # line 162
        except SystemExit as E:  # line 163
            _.assertEqual(0, E.code)  # line 163
        m = sos.Metadata(os.getcwd())  # reload from file system  # line 164
        for file in [f for f in os.listdir() if f.endswith(".bak")]:  # remove configuration file  # line 165
            os.unlink(file)  # remove configuration file  # line 165
        _.createFile(1, "1")  # line 166
        m.createBranch(0)  # line 167
        _.assertEqual(1, len(m.paths))  # line 168
        time.sleep(FS_PRECISION)  # time required by filesystem time resolution issues  # line 169
        _.createFile(1, "2")  # modify existing file  # line 170
        _.createFile(2, "2")  # add another file  # line 171
        m.loadCommit(0, 0)  # line 172
        changes, msg = m.findChanges()  # detect time skew  # line 173
        _.assertEqual(1, len(changes.additions))  # line 174
        _.assertEqual(0, len(changes.deletions))  # line 175
        _.assertEqual(1, len(changes.modifications))  # line 176
        _.assertEqual(0, len(changes.moves))  # line 177
        m.paths.update(changes.additions)  # line 178
        m.paths.update(changes.modifications)  # line 179
        _.createFile(2, "12")  # modify file again  # line 180
        changes, msg = m.findChanges(0, 1)  # by size, creating new commit  # line 181
        _.assertEqual(0, len(changes.additions))  # line 182
        _.assertEqual(0, len(changes.deletions))  # line 183
        _.assertEqual(1, len(changes.modifications))  # line 184
        _.assertEqual(0, len(changes.moves))  # line 185
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1)))  # line 186
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # line 187
# TODO test moves

    def testMoves(_):  # line 190
        _.createFile(1, "1")  # line 191
        _.createFile(2, "2", "sub")  # line 192
        sos.offline(options=["--strict", "--compress"])  # TODO move compress flag to own test function and check if it actually works  # line 193
        os.renames(sos.encode("." + os.sep + "file1"), sos.encode("sub" + os.sep + "file1"))  # line 194
        os.renames(sos.encode("sub" + os.sep + "file2"), sos.encode("." + os.sep + "file2"))  # line 195
        out = wrapChannels(lambda: sos.changes())  # type: str  # line 196
        _.assertIn("MOV ./file2  <-  sub/file2", out)  # line 197
        _.assertIn("MOV sub/file1  <-  ./file1", out)  # line 198
        out = wrapChannels(lambda: sos.commit())  # line 199
        _.assertIn("MOV ./file2  <-  sub/file2", out)  # line 200
        _.assertIn("MOV sub/file1  <-  ./file1", out)  # line 201
        _.assertIn("Created new revision r01 (+00/-00/~00/#02)", out)  # TODO why is this not captured?  # line 202

    def testPatternPaths(_):  # line 204
        sos.offline(options=["--track"])  # line 205
        os.mkdir("sub")  # line 206
        _.createFile("sub" + os.sep + "file1", "sdfsdf")  # line 207
        sos.add("sub", "sub/file?")  # line 208
        sos.commit("test")  # should pick up sub/file1 pattern  # line 209
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # sub/file1 was added  # line 210
        _.createFile(1)  # line 211
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 212
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 212
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 212
        except:  # line 213
            pass  # line 213

    def testNoArgs(_):  # line 215
        pass  # call "sos" without arguments should simply show help or info about missing arguments  # line 216

    def testAutoUpgrade(_):  # line 218
        sos.offline()  # line 219
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "r", encoding=sos.UTF8) as fd:  # line 220
            repo, branches, config = json.load(fd)  # line 220
        repo["version"] = None  # lower than any pip version  # line 221
        branches[:] = [branch[:5] for branch in branches]  # simulate some older state  # line 222
        del repo["format"]  # simulate pre-1.3.5  # line 223
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "w", encoding=sos.UTF8) as fd:  # line 224
            json.dump((repo, branches, config), fd, ensure_ascii=False)  # line 224
        out = wrapChannels(lambda: sos.status(options=["--repo"]))  # line 225
        _.assertAllIn(["pre-1.2", "Upgraded repository metadata to match SOS version '2018.1210.3028'", "Upgraded repository metadata to match SOS version '1.3.5'"], out)  # line 226

    def testFastBranching(_):  # line 228
        _.createFile(1)  # line 229
        sos.offline(options=["--strict"])  # b0/r0 = ./file1  # line 230
        _.createFile(2)  # line 231
        os.unlink("file1")  # line 232
        sos.commit()  # b0/r1 = ./file2  # line 233
        sos.branch(options=["--fast", "--last"])  # branch b1 from b0/1 TODO modify once --fast becomes the new normal  # line 234
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0", "b1"], os.listdir(sos.metaFolder), only=True)  # line 235
        _.createFile(3)  # line 236
        sos.commit()  # b1/r2 = ./file2, ./file3  # line 237
        _.assertAllIn([sos.metaFile, "r2"], os.listdir(sos.branchFolder(1)), only=True)  # line 238
        sos.branch(options=["--fast", "--last"])  # branch b2 from b1/2  # line 239
        sos.destroy("0")  # remove parent of b1 and transitive parent of b2  # line 240
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1", "b2"], os.listdir(sos.metaFolder), only=True)  # branch 0 was removed  # line 241
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(1)), only=True)  # revisions were copied to branch 1  # line 242
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(2)), only=True)  # revisions were copied to branch 1  # line 243
# TODO test also other functions like status --repo, log

    def testGetParentBranch(_):  # line 246
        m = sos.Accessor({"branches": {0: sos.Accessor({"parent": None, "revision": None}), 1: sos.Accessor({"parent": 0, "revision": 1})}})  # line 247
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 0))  # line 248
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 1))  # line 249
        _.assertEqual(1, sos.Metadata.getParentBranch(m, 1, 2))  # line 250
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 0, 10))  # line 251

    def testTokenizeGlobPattern(_):  # line 253
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 254
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 255
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 256
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 257
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 258
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 259

    def testTokenizeGlobPatterns(_):  # line 261
        try:  # because number of literal strings differs  # line 262
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 262
            _.fail()  # because number of literal strings differs  # line 262
        except:  # line 263
            pass  # line 263
        try:  # because glob patterns differ  # line 264
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 264
            _.fail()  # because glob patterns differ  # line 264
        except:  # line 265
            pass  # line 265
        try:  # glob patterns differ, regardless of position  # line 266
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 266
            _.fail()  # glob patterns differ, regardless of position  # line 266
        except:  # line 267
            pass  # line 267
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 268
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 269
        try:  # succeeds, because glob patterns match (differ only in position)  # line 270
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 270
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 270
        except:  # line 271
            pass  # line 271

    def testConvertGlobFiles(_):  # line 273
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 274
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 275

    def testFolderRemove(_):  # line 277
        m = sos.Metadata(os.getcwd())  # line 278
        _.createFile(1)  # line 279
        _.createFile("a", prefix="sub")  # line 280
        sos.offline()  # line 281
        _.createFile(2)  # line 282
        os.unlink("sub" + os.sep + "a")  # line 283
        os.rmdir("sub")  # line 284
        changes = sos.changes()  # TODO replace by output check  # line 285
        _.assertEqual(1, len(changes.additions))  # line 286
        _.assertEqual(0, len(changes.modifications))  # line 287
        _.assertEqual(1, len(changes.deletions))  # line 288
        _.createFile("a", prefix="sub")  # line 289
        changes = sos.changes()  # line 290
        _.assertEqual(0, len(changes.deletions))  # line 291

    def testSwitchConflict(_):  # line 293
        sos.offline(options=["--strict"])  # (r0)  # line 294
        _.createFile(1)  # line 295
        sos.commit()  # add file (r1)  # line 296
        os.unlink("file1")  # line 297
        sos.commit()  # remove (r2)  # line 298
        _.createFile(1, "something else")  # line 299
        sos.commit()  # (r3)  # line 300
        sos.switch("/1")  # updates file1 - marked as MOD, because mtime was changed  # line 301
        _.existsFile(1, "x" * 10)  # line 302
        sos.switch("/2", ["--force"])  # remove file1 requires --force, because size/content (or mtime in non-strict mode) is different to head of branch  # line 303
        sos.switch("/0")  # do nothing, as file1 is already removed  # line 304
        sos.switch("/1")  # add file1 back  # line 305
        sos.switch("/", ["--force"])  # requires force because changed vs. head of branch  # line 306
        _.existsFile(1, "something else")  # line 307

    def testComputeSequentialPathSet(_):  # line 309
        os.makedirs(sos.revisionFolder(0, 0))  # line 310
        os.makedirs(sos.revisionFolder(0, 1))  # line 311
        os.makedirs(sos.revisionFolder(0, 2))  # line 312
        os.makedirs(sos.revisionFolder(0, 3))  # line 313
        os.makedirs(sos.revisionFolder(0, 4))  # line 314
        m = sos.Metadata(os.getcwd())  # line 315
        m.branch = 0  # line 316
        m.commit = 2  # line 317
        m.saveBranches()  # line 318
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 319
        m.saveCommit(0, 0)  # initial  # line 320
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 321
        m.saveCommit(0, 1)  # mod  # line 322
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 323
        m.saveCommit(0, 2)  # add  # line 324
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 325
        m.saveCommit(0, 3)  # del  # line 326
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")  # line 327
        m.saveCommit(0, 4)  # readd  # line 328
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 329
        m.saveBranch(0)  # line 330
        m.branches = {0: sos.BranchInfo(0, 0), 1: sos.BranchInfo(1, 0)}  # line 331
        m.saveBranches()  # line 332
        m.computeSequentialPathSet(0, 4)  # line 333
        _.assertEqual(2, len(m.paths))  # line 334

    def testParseRevisionString(_):  # line 336
        m = sos.Metadata(os.getcwd())  # line 337
        m.branch = 1  # line 338
        m.commits = {0: 0, 1: 1, 2: 2}  # line 339
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 340
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 341
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 342
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 343
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 344
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 345
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 346

    def testOfflineEmpty(_):  # line 348
        os.mkdir("." + os.sep + sos.metaFolder)  # line 349
        try:  # line 350
            sos.offline("trunk")  # line 350
            _.fail()  # line 350
        except SystemExit as E:  # line 351
            _.assertEqual(1, E.code)  # line 351
        os.rmdir("." + os.sep + sos.metaFolder)  # line 352
        sos.offline("test")  # line 353
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 354
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 355
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 356
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 357
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 358
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file  # line 359

    def testOfflineWithFiles(_):  # line 361
        _.createFile(1, "x" * 100)  # line 362
        _.createFile(2)  # line 363
        sos.offline("test")  # line 364
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 365
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 366
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 367
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 368
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 369
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 370
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file plus branch base file copies  # line 371

    def testBranch(_):  # line 373
        _.createFile(1, "x" * 100)  # line 374
        _.createFile(2)  # line 375
        sos.offline("test")  # b0/r0  # line 376
        sos.branch("other")  # b1/r0  # line 377
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 378
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 379
        _.assertEqual(list(sorted(os.listdir(sos.revisionFolder(0, 0)))), list(sorted(os.listdir(sos.revisionFolder(1, 0)))))  # line 381
        _.createFile(1, "z")  # modify file  # line 383
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 384
        _.assertNotEqual(os.stat(sos.encode("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa")).st_size, os.stat(sos.encode("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa")).st_size)  # line 385
        _.createFile(3, "z")  # line 387
        sos.branch("from_last_revision", options=["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 388
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 389
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 394
        _.createFile(1, "x" * 100)  # line 395
        _.createFile(2)  # line 396
        sos.offline("test")  # line 397
        changes = sos.changes()  # line 398
        _.assertEqual(0, len(changes.additions))  # line 399
        _.assertEqual(0, len(changes.deletions))  # line 400
        _.assertEqual(0, len(changes.modifications))  # line 401
        _.createFile(1, "z")  # size change  # line 402
        changes = sos.changes()  # line 403
        _.assertEqual(0, len(changes.additions))  # line 404
        _.assertEqual(0, len(changes.deletions))  # line 405
        _.assertEqual(1, len(changes.modifications))  # line 406
        sos.commit("message")  # line 407
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 408
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.revisionFolder(0, 1)))  # line 409
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # no further files, only the modified one  # line 410
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 411
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 412
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 413
        os.unlink("file2")  # line 414
        changes = sos.changes()  # line 415
        _.assertEqual(0, len(changes.additions))  # line 416
        _.assertEqual(1, len(changes.deletions))  # line 417
        _.assertEqual(1, len(changes.modifications))  # line 418
        sos.commit("modified")  # line 419
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # no additional files, only mentions in metadata  # line 420
        try:  # expecting Exit due to no changes  # line 421
            sos.commit("nothing")  # expecting Exit due to no changes  # line 421
            _.fail()  # expecting Exit due to no changes  # line 421
        except:  # line 422
            pass  # line 422

    def testGetBranch(_):  # line 424
        m = sos.Metadata(os.getcwd())  # line 425
        m.branch = 1  # current branch  # line 426
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 427
        _.assertEqual(27, m.getBranchByName(27))  # line 428
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 429
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 430
        _.assertIsNone(m.getBranchByName("unknown"))  # line 431
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 432
        _.assertEqual(13, m.getRevisionByName("13"))  # line 433
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 434
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 435

    def testTagging(_):  # line 437
        m = sos.Metadata(os.getcwd())  # line 438
        sos.offline()  # line 439
        _.createFile(111)  # line 440
        sos.commit("tag", ["--tag"])  # line 441
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 442
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 443
        _.createFile(2)  # line 444
        try:  # line 445
            sos.commit("tag")  # line 445
            _.fail()  # line 445
        except:  # line 446
            pass  # line 446
        sos.commit("tag-2", ["--tag"])  # line 447
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 448
        _.assertIn("TAG tag", out)  # line 449

    def testSwitch(_):  # line 451
        _.createFile(1, "x" * 100)  # line 452
        _.createFile(2, "y")  # line 453
        sos.offline("test")  # file1-2  in initial branch commit  # line 454
        sos.branch("second")  # file1-2  switch, having same files  # line 455
        sos.switch("0")  # no change  switch back, no problem  # line 456
        sos.switch("second")  # no change  # switch back, no problem  # line 457
        _.createFile(3, "y")  # generate a file  # line 458
        try:  # uncommited changes detected  # line 459
            sos.switch("test")  # uncommited changes detected  # line 459
            _.fail()  # uncommited changes detected  # line 459
        except SystemExit as E:  # line 460
            _.assertEqual(1, E.code)  # line 460
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 461
        sos.changes()  # line 462
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 463
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 464
        _.createFile("XXX")  # line 465
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 466
        _.assertIn("File tree has changes", out)  # line 467
        _.assertNotIn("File tree is unchanged", out)  # line 468
        _.assertIn("  * b00   'test'", out)  # line 469
        _.assertIn("    b01 'second'", out)  # line 470
        _.assertIn("(dirty)", out)  # one branch has commits  # line 471
        _.assertIn("(in sync)", out)  # the other doesn't  # line 472
        sos.defaults["useChangesCommand"] = False  # because sos.main() is never called  # line 473
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # trigger repo info  # line 474
        _.assertAllIn(["Metadata format", "Content checking:    deactivated", "Data compression:    deactivated", "Repository mode:     simple", "Number of branches:  2"], out)  # line 475
        sos.defaults["useChangesCommand"] = True  # because sos.main() is never called  # line 476
        _.createFile(4, "xy")  # generate a file  # line 477
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4  # line 478
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 479
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 480
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 481
        sos.switch("test", ["--force"])  # should restore file1 and remove file3  # line 482
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 483
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 484
        out = wrapChannels(lambda: sos.dump("dumped.sos.zip", options=["--skip-backup", "--full"])).replace("\r", "")  # line 485
        _.assertAllIn(["Dumping revisions"], out)  # line 486
        _.assertNotIn("Creating backup", out)  # line 487
        out = wrapChannels(lambda: sos.dump("dumped.sos.zip", options=["--skip-backup"])).replace("\r", "")  # line 488
        _.assertIn("Dumping revisions", out)  # line 489
        _.assertNotIn("Creating backup", out)  # line 490
        out = wrapChannels(lambda: sos.dump("dumped.sos.zip", options=["--full"])).replace("\r", "")  # line 491
        _.assertAllIn(["Creating backup"], out)  # line 492
        _.assertIn("Dumping revisions", out)  # line 493

    def testAutoDetectVCS(_):  # line 495
        os.mkdir(".git")  # line 496
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 497
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 498
            meta = fd.read()  # line 498
        _.assertTrue("\"master\"" in meta)  # line 499
        os.rmdir(".git")  # line 500

    def testUpdate(_):  # line 502
        sos.offline("trunk")  # create initial branch b0/r0  # line 503
        _.createFile(1, "x" * 100)  # line 504
        sos.commit("second")  # create b0/r1  # line 505

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 507
        _.assertFalse(_.existsFile(1))  # line 508

        sos.update("/1")  # recreate file1  # line 510
        _.assertTrue(_.existsFile(1))  # line 511

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 513
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2)))  # line 514
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2, file=sos.metaFile)))  # line 515
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta data file, no differential files  # line 516

        sos.update("/1")  # do nothing, as nothing has changed  # line 518
        _.assertTrue(_.existsFile(1))  # line 519

        _.createFile(2, "y" * 100)  # line 521
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", options=["--force"])  # automatically including file 2 (as we are in simple mode)  # line 524
        _.assertTrue(_.existsFile(2))  # line 525
        sos.update("trunk", ["--add"])  # only add stuff  # line 526
        _.assertTrue(_.existsFile(2))  # line 527
        sos.update("trunk")  # nothing to do  # line 528
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 529

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 531
        _.createFile(10, theirs)  # line 532
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 533
        _.createFile(11, mine)  # line 534
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 535
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 536

    def testUpdate2(_):  # line 538
        _.createFile("test.txt", "x" * 10)  # line 539
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 540
        sync()  # line 541
        sos.branch("mod")  # line 542
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 543
        sos.commit("mod")  # create b0/r1  # line 544
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 545
        _.assertTrue(_.existsFile("test.txt", b"x" * 10))  # line 546
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 547
        _.existsFile("test.txt", b"x" * 5 + b"y" * 5)  # line 548
        _.createFile("test.txt", "x" * 10)  # line 549
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 550
        sync()  # line 551
        _.assertTrue(_.existsFile("test.txt", b"x" * 5 + b"y" * 5))  # line 552
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 553
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 554
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 555
        sync()  # line 556
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 557
        _.assertTrue(_.existsFile("test.txt", b"x" * 5 + b"y" * 5))  # line 558

    def testIsTextType(_):  # line 560
        m = sos.Metadata(".")  # line 561
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 562
        m.c.bintype = ["*.md.confluence"]  # line 563
        _.assertTrue(m.isTextType("ab.txt"))  # line 564
        _.assertTrue(m.isTextType("./ab.txt"))  # line 565
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 566
        _.assertFalse(m.isTextType("bc/ab."))  # line 567
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 568
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 569
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 570
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 571

    def testEolDet(_):  # line 573
        ''' Check correct end-of-line detection. '''  # line 574
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 575
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 576
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 577
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 578
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 579
        _.assertIsNone(sos.eoldet(b""))  # line 580
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 581

    def testMerge(_):  # line 583
        ''' Check merge results depending on user options. '''  # line 584
        a = b"a\nb\ncc\nd"  # type: bytes  # line 585
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 586
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge  # line 587
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace  # line 588
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace  # line 589
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge  # line 590
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 591
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 592
        a = b"a\nb\ncc\nd"  # line 593
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 594
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement  # line 595
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # line 596
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 597
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])  # line 599
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 600
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 602
        b = b"a\nc\ne"  # line 603
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 604
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 605
        a = b"a\nb\ne"  # intra-line merge  # line 606
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 607
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 608

    def testMergeEol(_):  # line 610
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])  # line 611
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 612
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF  # line 613
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])  # line 614
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])  # line 615

    def testPickyMode(_):  # line 617
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 618
        sos.offline("trunk", None, ["--picky"])  # line 619
        changes = sos.changes()  # line 620
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 621
        sos.add(".", "./file?", ["--force"])  # line 622
        _.createFile(1, "aa")  # line 623
        sos.commit("First")  # add one file  # line 624
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 625
        _.createFile(2, "b")  # line 626
        try:  # add nothing, because picky  # line 627
            sos.commit("Second")  # add nothing, because picky  # line 627
        except:  # line 628
            pass  # line 628
        sos.add(".", "./file?")  # line 629
        sos.commit("Third")  # line 630
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # line 631
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 632
        _.assertIn("  * r2", out)  # line 633
        _.createFile(3, prefix="sub")  # line 634
        sos.add("sub", "sub/file?")  # line 635
        changes = sos.changes()  # line 636
        _.assertEqual(1, len(changes.additions))  # line 637
        _.assertTrue("sub/file3" in changes.additions)  # line 638

    def testTrackedSubfolder(_):  # line 640
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 641
        os.mkdir("." + os.sep + "sub")  # line 642
        sos.offline("trunk", None, ["--track"])  # line 643
        _.createFile(1, "x")  # line 644
        _.createFile(1, "x", prefix="sub")  # line 645
        sos.add(".", "./file?")  # add glob pattern to track  # line 646
        sos.commit("First")  # line 647
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 648
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 649
        sos.commit("Second")  # one new file + meta  # line 650
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 651
        os.unlink("file1")  # remove from basefolder  # line 652
        _.createFile(2, "y")  # line 653
        sos.remove(".", "sub/file?")  # line 654
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 655
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 655
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 655
        except:  # line 656
            pass  # line 656
        sos.commit("Third")  # line 657
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta  # line 658
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 661
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 666
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 667
        _.createFile(1)  # line 668
        _.createFile("a123a")  # untracked file "a123a"  # line 669
        sos.add(".", "./file?")  # add glob tracking pattern  # line 670
        sos.commit("second")  # versions "file1"  # line 671
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 672
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 673
        _.assertIn("  | ./file?", out)  # line 674

        _.createFile(2)  # untracked file "file2"  # line 676
        sos.commit("third")  # versions "file2"  # line 677
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta file  # line 678

        os.mkdir("." + os.sep + "sub")  # line 680
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 681
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 682
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 3))))  # meta file only, no other tracked path/file  # line 683

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 685
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 686
        sos.add(".", "./a*a")  # add tracking pattern  # line 687
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 688
        _.assertEqual(0, len(changes.modifications))  # line 689
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 690
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 691

        sos.commit("Second_2")  # line 693
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(1, 1))))  # "a123a" + meta file  # line 694
        _.existsFile(1, b"x" * 10)  # line 695
        _.existsFile(2, b"x" * 10)  # line 696

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 698
        _.existsFile(1, b"x" * 10)  # line 699
        _.existsFile("a123a", b"x" * 10)  # line 700

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 702
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 703
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 704

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 706
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 707
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 708
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 709
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 710
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 711
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 712
# TODO test switch --meta

    def testLsTracked(_):  # line 715
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 716
        _.createFile(1)  # line 717
        _.createFile("foo")  # line 718
        sos.add(".", "./file*")  # capture one file  # line 719
        sos.ls()  # line 720
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 721
        _.assertInAny("TRK file1  (file*)", out)  # line 722
        _.assertNotInAny("... file1  (file*)", out)  # line 723
        _.assertInAny("··· foo", out)  # line 724
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 725
        _.assertInAny("TRK file*", out)  # line 726
        _.createFile("a", prefix="sub")  # line 727
        sos.add("sub", "sub/a")  # line 728
        sos.ls("sub")  # line 729
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 730

    def testLineMerge(_):  # line 732
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 733
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 734
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 735
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 736

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 738
        _.createFile(1)  # line 739
        sos.offline("master", options=["--force"])  # line 740
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 741
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 742
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 743
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 744
        _.createFile(2)  # line 745
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 746
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 747
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 748
        _.assertFalse(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 749

    def testLocalConfig(_):  # line 751
        sos.offline("bla", options=[])  # line 752
        try:  # line 753
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 753
        except SystemExit as E:  # line 754
            _.assertEqual(0, E.code)  # line 754
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 755

    def testConfigVariations(_):  # line 757
        def makeRepo():  # line 758
            try:  # line 759
                os.unlink("file1")  # line 759
            except:  # line 760
                pass  # line 760
            sos.offline("master", options=["--force"])  # line 761
            _.createFile(1)  # line 762
            sos.commit("Added file1")  # line 763
        try:  # line 764
            sos.config(["set", "strict", "on"])  # line 764
        except SystemExit as E:  # line 765
            _.assertEqual(0, E.code)  # line 765
        makeRepo()  # line 766
        _.assertTrue(checkRepoFlag("strict", True))  # line 767
        try:  # line 768
            sos.config(["set", "strict", "off"])  # line 768
        except SystemExit as E:  # line 769
            _.assertEqual(0, E.code)  # line 769
        makeRepo()  # line 770
        _.assertTrue(checkRepoFlag("strict", False))  # line 771
        try:  # line 772
            sos.config(["set", "strict", "yes"])  # line 772
        except SystemExit as E:  # line 773
            _.assertEqual(0, E.code)  # line 773
        makeRepo()  # line 774
        _.assertTrue(checkRepoFlag("strict", True))  # line 775
        try:  # line 776
            sos.config(["set", "strict", "no"])  # line 776
        except SystemExit as E:  # line 777
            _.assertEqual(0, E.code)  # line 777
        makeRepo()  # line 778
        _.assertTrue(checkRepoFlag("strict", False))  # line 779
        try:  # line 780
            sos.config(["set", "strict", "1"])  # line 780
        except SystemExit as E:  # line 781
            _.assertEqual(0, E.code)  # line 781
        makeRepo()  # line 782
        _.assertTrue(checkRepoFlag("strict", True))  # line 783
        try:  # line 784
            sos.config(["set", "strict", "0"])  # line 784
        except SystemExit as E:  # line 785
            _.assertEqual(0, E.code)  # line 785
        makeRepo()  # line 786
        _.assertTrue(checkRepoFlag("strict", False))  # line 787
        try:  # line 788
            sos.config(["set", "strict", "true"])  # line 788
        except SystemExit as E:  # line 789
            _.assertEqual(0, E.code)  # line 789
        makeRepo()  # line 790
        _.assertTrue(checkRepoFlag("strict", True))  # line 791
        try:  # line 792
            sos.config(["set", "strict", "false"])  # line 792
        except SystemExit as E:  # line 793
            _.assertEqual(0, E.code)  # line 793
        makeRepo()  # line 794
        _.assertTrue(checkRepoFlag("strict", False))  # line 795
        try:  # line 796
            sos.config(["set", "strict", "enable"])  # line 796
        except SystemExit as E:  # line 797
            _.assertEqual(0, E.code)  # line 797
        makeRepo()  # line 798
        _.assertTrue(checkRepoFlag("strict", True))  # line 799
        try:  # line 800
            sos.config(["set", "strict", "disable"])  # line 800
        except SystemExit as E:  # line 801
            _.assertEqual(0, E.code)  # line 801
        makeRepo()  # line 802
        _.assertTrue(checkRepoFlag("strict", False))  # line 803
        try:  # line 804
            sos.config(["set", "strict", "enabled"])  # line 804
        except SystemExit as E:  # line 805
            _.assertEqual(0, E.code)  # line 805
        makeRepo()  # line 806
        _.assertTrue(checkRepoFlag("strict", True))  # line 807
        try:  # line 808
            sos.config(["set", "strict", "disabled"])  # line 808
        except SystemExit as E:  # line 809
            _.assertEqual(0, E.code)  # line 809
        makeRepo()  # line 810
        _.assertTrue(checkRepoFlag("strict", False))  # line 811
        try:  # line 812
            sos.config(["set", "strict", "nope"])  # line 812
            _.fail()  # line 812
        except SystemExit as E:  # line 813
            _.assertEqual(1, E.code)  # line 813

    def testLsSimple(_):  # line 815
        _.createFile(1)  # line 816
        _.createFile("foo")  # line 817
        _.createFile("ign1")  # line 818
        _.createFile("ign2")  # line 819
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 820
        try:  # define an ignore pattern  # line 821
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 821
        except SystemExit as E:  # line 822
            _.assertEqual(0, E.code)  # line 822
        try:  # additional ignore pattern  # line 823
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 823
        except SystemExit as E:  # line 824
            _.assertEqual(0, E.code)  # line 824
        try:  # define a list of ignore patterns  # line 825
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 825
        except SystemExit as E:  # line 826
            _.assertEqual(0, E.code)  # line 826
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 827
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 828
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 829
        _.assertInAny('··· file1', out)  # line 830
        _.assertInAny('··· ign1', out)  # line 831
        _.assertInAny('··· ign2', out)  # line 832
        try:  # line 833
            sos.config(["rm", "foo", "bar"])  # line 833
            _.fail()  # line 833
        except SystemExit as E:  # line 834
            _.assertEqual(1, E.code)  # line 834
        try:  # line 835
            sos.config(["rm", "ignores", "foo"])  # line 835
            _.fail()  # line 835
        except SystemExit as E:  # line 836
            _.assertEqual(1, E.code)  # line 836
        try:  # line 837
            sos.config(["rm", "ignores", "ign1"])  # line 837
        except SystemExit as E:  # line 838
            _.assertEqual(0, E.code)  # line 838
        try:  # remove ignore pattern  # line 839
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 839
        except SystemExit as E:  # line 840
            _.assertEqual(0, E.code)  # line 840
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 841
        _.assertInAny('··· ign1', out)  # line 842
        _.assertInAny('IGN ign2', out)  # line 843
        _.assertNotInAny('··· ign2', out)  # line 844

    def testWhitelist(_):  # line 846
# TODO test same for simple mode
        _.createFile(1)  # line 848
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 849
        sos.offline("xx", options=["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 850
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 851
        sos.commit(options=["--force"])  # attempt to commit the file  # line 852
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta data, file1 was ignored  # line 853
        try:  # Exit because dirty  # line 854
            sos.online()  # Exit because dirty  # line 854
            _.fail()  # Exit because dirty  # line 854
        except:  # exception expected  # line 855
            pass  # exception expected  # line 855
        _.createFile("x2")  # add another change  # line 856
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 857
        try:  # force beyond dirty flag check  # line 858
            sos.online(["--force"])  # force beyond dirty flag check  # line 858
            _.fail()  # force beyond dirty flag check  # line 858
        except:  # line 859
            pass  # line 859
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 860
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 861

        _.createFile(1)  # line 863
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 864
        sos.offline("xx", None, ["--track"])  # line 865
        sos.add(".", "./file*")  # line 866
        sos.commit()  # should NOT ask for force here  # line 867
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 868

    def testRemove(_):  # line 870
        _.createFile(1, "x" * 100)  # line 871
        sos.offline("trunk")  # line 872
        try:  # line 873
            sos.destroy("trunk")  # line 873
            _fail()  # line 873
        except:  # line 874
            pass  # line 874
        _.createFile(2, "y" * 10)  # line 875
        sos.branch("added")  # creates new branch, writes repo metadata, and therefore creates backup copy  # line 876
        sos.destroy("trunk")  # line 877
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1"], os.listdir("." + os.sep + sos.metaFolder))  # line 878
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 879
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 880
        sos.branch("next")  # line 881
        _.createFile(3, "y" * 10)  # make a change  # line 882
        sos.destroy("added", "--force")  # should succeed  # line 883

    def testUsage(_):  # line 885
        try:  # TODO expect sys.exit(0)  # line 886
            sos.usage()  # TODO expect sys.exit(0)  # line 886
            _.fail()  # TODO expect sys.exit(0)  # line 886
        except:  # line 887
            pass  # line 887
        try:  # line 888
            sos.usage(short=True)  # line 888
            _.fail()  # line 888
        except:  # line 889
            pass  # line 889

    def testOnlyExcept(_):  # line 891
        ''' Test blacklist glob rules. '''  # line 892
        sos.offline(options=["--track"])  # line 893
        _.createFile("a.1")  # line 894
        _.createFile("a.2")  # line 895
        _.createFile("b.1")  # line 896
        _.createFile("b.2")  # line 897
        sos.add(".", "./a.?")  # line 898
        sos.add(".", "./?.1", negative=True)  # line 899
        out = wrapChannels(lambda: sos.commit())  # line 900
        _.assertIn("ADD ./a.2", out)  # line 901
        _.assertNotIn("ADD ./a.1", out)  # line 902
        _.assertNotIn("ADD ./b.1", out)  # line 903
        _.assertNotIn("ADD ./b.2", out)  # line 904

    def testOnly(_):  # line 906
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 907
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 908
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 909
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 910
        sos.offline(options=["--track", "--strict"])  # line 911
        _.createFile(1)  # line 912
        _.createFile(2)  # line 913
        sos.add(".", "./file1")  # line 914
        sos.add(".", "./file2")  # line 915
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 916
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta and file1  # line 917
        sos.commit()  # adds also file2  # line 918
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta and file1  # line 919
        _.createFile(1, "cc")  # modify both files  # line 920
        _.createFile(2, "dd")  # line 921
        try:  # line 922
            sos.config(["set", "texttype", "file2"])  # line 922
        except SystemExit as E:  # line 923
            _.assertEqual(0, E.code)  # line 923
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))  # line 924
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 925
        _.assertTrue("./file2" in changes.modifications)  # line 926
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 927
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 928

    def testDiff(_):  # line 930
        try:  # manually mark this file as "textual"  # line 931
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 931
        except SystemExit as E:  # line 932
            _.assertEqual(0, E.code)  # line 932
        sos.offline(options=["--strict"])  # line 933
        _.createFile(1)  # line 934
        _.createFile(2)  # line 935
        sos.commit()  # line 936
        _.createFile(1, "sdfsdgfsdf")  # line 937
        _.createFile(2, "12343")  # line 938
        sos.commit()  # line 939
        _.createFile(1, "foobar")  # line 940
        _.createFile(3)  # line 941
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 942
        _.assertIn("ADD ./file3", out)  # line 943
        _.assertAllIn(["MOD ./file2", "DIF ./file1  <No newline>", "- | 0001 |xxxxxxxxxx|", "+ | 0000 |foobar|"], out)  # line 944
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 945

    def testReorderRenameActions(_):  # line 947
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 948
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 949
        try:  # line 950
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 950
            _.fail()  # line 950
        except:  # line 951
            pass  # line 951

    def testMove(_):  # line 953
        sos.offline(options=["--strict", "--track"])  # line 954
        _.createFile(1)  # line 955
        sos.add(".", "./file?")  # line 956
# test source folder missing
        try:  # line 958
            sos.move("sub", "sub/file?", ".", "?file")  # line 958
            _.fail()  # line 958
        except:  # line 959
            pass  # line 959
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 961
        _.assertTrue(os.path.exists("sub"))  # line 962
        _.assertTrue(os.path.exists("sub/file1"))  # line 963
        _.assertFalse(os.path.exists("file1"))  # line 964
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 966
        _.assertTrue(os.path.exists("1file"))  # line 967
        _.assertFalse(os.path.exists("sub/file1"))  # line 968
# test nothing matches source pattern
        try:  # line 970
            sos.move(".", "a*", ".", "b*")  # line 970
            _.fail()  # line 970
        except:  # line 971
            pass  # line 971
        sos.add(".", "*")  # anything pattern  # line 972
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 973
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 973
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 973
        except:  # line 974
            pass  # line 974
# test rename no conflict
        _.createFile(1)  # line 976
        _.createFile(2)  # line 977
        _.createFile(3)  # line 978
        sos.add(".", "./file*")  # line 979
        try:  # define an ignore pattern  # line 980
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 980
        except SystemExit as E:  # line 981
            _.assertEqual(0, E.code)  # line 981
        try:  # line 982
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 982
        except SystemExit as E:  # line 983
            _.assertEqual(0, E.code)  # line 983
        sos.move(".", "./file*", ".", "fi*le")  # line 984
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 985
        _.assertFalse(os.path.exists("fi4le"))  # line 986
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 988
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 992
        sos.add(".", "./?a?b", ["--force"])  # line 993
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 994
        _.createFile("1a2b")  # should not be tracked  # line 995
        _.createFile("a1b2")  # should be tracked  # line 996
        sos.commit()  # line 997
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 998
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 999
        _.createFile("1a1b1")  # line 1000
        _.createFile("1a1b2")  # line 1001
        sos.add(".", "?a?b*")  # line 1002
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 1003
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 1007
        sos.offline()  # line 1008
        _.createFile(1)  # line 1009
        os.mkdir(sos.revisionFolder(0, 1))  # line 1010
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.revisionFolder(0, 1))  # line 1011
        _.createFile(1)  # line 1012
        try:  # should exit with error due to collision detection  # line 1013
            sos.commit()  # should exit with error due to collision detection  # line 1013
            _.fail()  # should exit with error due to collision detection  # line 1013
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 1014
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 1014

    def testFindBase(_):  # line 1016
        old = os.getcwd()  # line 1017
        try:  # line 1018
            os.mkdir("." + os.sep + ".git")  # line 1019
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 1020
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 1021
            os.chdir("a" + os.sep + "b")  # line 1022
            s, vcs, cmd = sos.findSosVcsBase()  # line 1023
            _.assertIsNotNone(s)  # line 1024
            _.assertIsNotNone(vcs)  # line 1025
            _.assertEqual("git", cmd)  # line 1026
        finally:  # line 1027
            os.chdir(old)  # line 1027

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail

# TODO test +++ --- in diff
# TODO test +01/-02/*..
# TODO tests for loadcommit redirection
# TODO test wrong branch/revision after fast branching, would raise exception for -1 otherwise

if __name__ == '__main__':  # line 1037
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 1038
    c = configr.Configr("sos")  # line 1039
    c.loadSettings()  # line 1040
    if len(c.keys()) > 0:  # line 1041
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 1041
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 1042
