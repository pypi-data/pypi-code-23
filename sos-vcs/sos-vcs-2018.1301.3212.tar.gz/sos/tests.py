#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xda9257d3

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
#  time.sleep(FS_PRECISION)


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
    logging.getLogger().addHandler(handler)  # line 75
    try:  # capture output into buf  # line 76
        func()  # capture output into buf  # line 76
    except Exception as E:  # line 77
        buf.write(str(E) + "\n")  # line 77
        traceback.print_exc(file=buf)  # line 77
    except SystemExit as F:  # line 78
        buf.write("EXIT CODE %s" % F.code + "\n")  # line 78
        traceback.print_exc(file=buf)  # line 78
    logging.getLogger().removeHandler(handler)  # line 79
    sys.argv, sys.stdout, sys.stderr = oldv, sys.__stdout__, sys.__stderr__  # TODO when run using pythonw.exe and/or no console, these could be None  # line 80
    buf.seek(0)  # line 81
    return _coconut_tail_call(buf.read)  # line 82

def mockInput(datas: '_coconut.typing.Sequence[str]', func: '_coconut.typing.Callable[..., Any]') -> 'Any':  # line 84
    if sos.coco_version < (1, 3, 1, 21):  # line 85
        import builtins  # line 86
        with mock.patch("builtins.input", side_effect=datas):  # line 87
            return func()  # line 87
    else:  # line 88
        with mock.patch("sos._utility.input", side_effect=datas):  # line 89
            return func()  # line 89

def setRepoFlag(name: 'str', value: 'bool'):  # line 91
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 92
        flags, branches, config = json.loads(fd.read())  # line 92
    flags[name] = value  # line 93
    with open(sos.metaFolder + os.sep + sos.metaFile, "w") as fd:  # line 94
        fd.write(json.dumps((flags, branches, config)))  # line 94

def checkRepoFlag(name: 'str', flag: '_coconut.typing.Optional[bool]'=None, value: '_coconut.typing.Optional[Any]'=None) -> 'bool':  # line 96
    with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 97
        flags, branches, config = json.loads(fd.read())  # line 97
    return (name in flags and flags[name] == flag) if flag is not None else (name in config and config[name] == value)  # line 98


class Tests(unittest.TestCase):  # line 101
    ''' Entire test suite. '''  # line 102

    def setUp(_):  # line 104
        logging.getLogger().setLevel(logging.DEBUG)  # allowing to capture debug output  # line 105
        sos.Metadata.singleton = None  # line 106
        for entry in os.listdir(testFolder):  # cannot remove testFolder on Windows when using TortoiseSVN as VCS  # line 107
            resource = os.path.join(testFolder, entry)  # line 108
            shutil.rmtree(sos.encode(resource)) if os.path.isdir(sos.encode(resource)) else os.unlink(sos.encode(resource))  # line 109
        os.chdir(testFolder)  # line 110


    def assertAllIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]', only: 'bool'=False):  # line 113
        for w in what:  # line 114
            _.assertIn(w, where)  # line 114
        if only:  # line 115
            _.assertEqual(len(what), len(where))  # line 115

    def assertAllNotIn(_, what: '_coconut.typing.Sequence[str]', where: 'Union[str, List[str]]'):  # line 117
        for w in what:  # line 118
            _.assertNotIn(w, where)  # line 118

    def assertInAll(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 120
        for w in where:  # line 121
            _.assertIn(what, w)  # line 121

    def assertInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 123
        _.assertTrue(any((what in w for w in where)))  # line 123

    def assertNotInAny(_, what: 'str', where: '_coconut.typing.Sequence[str]'):  # line 125
        _.assertFalse(any((what in w for w in where)))  # line 125

    def createFile(_, number: 'Union[int, str]', contents: 'str'="x" * 10, prefix: '_coconut.typing.Optional[str]'=None):  # line 127
        if prefix and not os.path.exists(prefix):  # line 128
            os.makedirs(prefix)  # line 128
        with open(("." if prefix is None else prefix) + os.sep + (("file%d" % number) if isinstance(number, int) else number), "wb") as fd:  # line 129
            fd.write(contents if isinstance(contents, bytes) else contents.encode("cp1252"))  # line 129
        sync()  # line 130

    def existsFile(_, number: 'Union[int, str]', expectedContents: 'bytes'=None) -> 'bool':  # line 132
        sync()  # line 133
        if not os.path.exists(("." + os.sep + "file%d" % number) if isinstance(number, int) else number):  # line 134
            return False  # line 134
        if expectedContents is None:  # line 135
            return True  # line 135
        with open(("." + os.sep + "file%d" % number) if isinstance(number, int) else number, "rb") as fd:  # line 136
            return fd.read() == expectedContents  # line 136

    def testAccessor(_):  # line 138
        a = sos.Accessor({"a": 1})  # line 139
        _.assertEqual((1, 1), (a["a"], a.a))  # line 140

    def testRestoreFile(_):  # line 142
        m = sos.Metadata()  # line 143
        os.makedirs(sos.revisionFolder(0, 0))  # line 144
        _.createFile("hashed_file", "content", sos.revisionFolder(0, 0))  # line 145
        m.restoreFile(relPath="restored", branch=0, revision=0, pinfo=sos.PathInfo("hashed_file", 0, (time.time() - 2000) * 1000, "content hash"))  # line 146
        _.assertTrue(_.existsFile("restored", b""))  # line 147

    def testGetAnyOfmap(_):  # line 149
        _.assertEqual(2, sos.getAnyOfMap({"a": 1, "b": 2}, ["x", "b"]))  # line 150
        _.assertIsNone(sos.getAnyOfMap({"a": 1, "b": 2}, []))  # line 151

    def testAjoin(_):  # line 153
        _.assertEqual("a1a2", sos.ajoin("a", ["1", "2"]))  # line 154
        _.assertEqual("* a\n* b", sos.ajoin("* ", ["a", "b"], "\n"))  # line 155

    def testFindChanges(_):  # line 157
        m = sos.Metadata(os.getcwd())  # line 158
        try:  # line 159
            sos.config(["set", "texttype", "*"])  # line 159
        except SystemExit as E:  # line 160
            _.assertEqual(0, E.code)  # line 160
        try:  # will be stripped from leading paths anyway  # line 161
            sos.config(["set", "ignores", "test/*.cfg;D:\\apps\\*.cfg.bak"])  # will be stripped from leading paths anyway  # line 161
        except SystemExit as E:  # line 162
            _.assertEqual(0, E.code)  # line 162
        m = sos.Metadata(os.getcwd())  # reload from file system  # line 163
        for file in [f for f in os.listdir() if f.endswith(".bak")]:  # remove configuration file  # line 164
            os.unlink(file)  # remove configuration file  # line 164
        _.createFile(1, "1")  # line 165
        m.createBranch(0)  # line 166
        _.assertEqual(1, len(m.paths))  # line 167
        time.sleep(FS_PRECISION)  # time required by filesystem time resolution issues  # line 168
        _.createFile(1, "2")  # modify existing file  # line 169
        _.createFile(2, "2")  # add another file  # line 170
        m.loadCommit(0, 0)  # line 171
        changes, msg = m.findChanges()  # detect time skew  # line 172
        _.assertEqual(1, len(changes.additions))  # line 173
        _.assertEqual(0, len(changes.deletions))  # line 174
        _.assertEqual(1, len(changes.modifications))  # line 175
        _.assertEqual(0, len(changes.moves))  # line 176
        m.paths.update(changes.additions)  # line 177
        m.paths.update(changes.modifications)  # line 178
        _.createFile(2, "12")  # modify file again  # line 179
        changes, msg = m.findChanges(0, 1)  # by size, creating new commit  # line 180
        _.assertEqual(0, len(changes.additions))  # line 181
        _.assertEqual(0, len(changes.deletions))  # line 182
        _.assertEqual(1, len(changes.modifications))  # line 183
        _.assertEqual(0, len(changes.moves))  # line 184
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1)))  # line 185
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # line 186
# TODO test moves

    def testMoves(_):  # line 189
        _.createFile(1, "1")  # line 190
        _.createFile(2, "2", "sub")  # line 191
        sos.offline(options=["--strict", "--compress"])  # TODO move compress flag to own test function and check if it actually works  # line 192
        os.renames(sos.encode("." + os.sep + "file1"), sos.encode("sub" + os.sep + "file1"))  # line 193
        os.renames(sos.encode("sub" + os.sep + "file2"), sos.encode("." + os.sep + "file2"))  # line 194
        out = wrapChannels(lambda: sos.changes())  # type: str  # line 195
        _.assertIn("MOV ./file2  <-  sub/file2", out)  # line 196
        _.assertIn("MOV sub/file1  <-  ./file1", out)  # line 197
        out = wrapChannels(lambda: sos.commit())  # line 198
        _.assertIn("MOV ./file2  <-  sub/file2", out)  # line 199
        _.assertIn("MOV sub/file1  <-  ./file1", out)  # line 200
        _.assertIn("Created new revision r01 (+00/-00/~00/#02)", out)  # TODO why is this not captured?  # line 201

    def testPatternPaths(_):  # line 203
        sos.offline(options=["--track"])  # line 204
        os.mkdir("sub")  # line 205
        _.createFile("sub" + os.sep + "file1", "sdfsdf")  # line 206
        sos.add("sub", "sub/file?")  # line 207
        sos.commit("test")  # should pick up sub/file1 pattern  # line 208
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # sub/file1 was added  # line 209
        _.createFile(1)  # line 210
        try:  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 211
            sos.commit("nothing")  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 211
            _.fail()  # should not commit anything, as the file in base folder doesn't match the tracked pattern  # line 211
        except:  # line 212
            pass  # line 212

    def testNoArgs(_):  # line 214
        pass  # call "sos" without arguments should simply show help or info about missing arguments  # line 215

    def testAutoUpgrade(_):  # line 217
        sos.offline()  # line 218
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "r", encoding=sos.UTF8) as fd:  # line 219
            repo, branches, config = json.load(fd)  # line 219
        repo["version"] = None  # lower than any pip version  # line 220
        branches[:] = [branch[:5] for branch in branches]  # simulate some older state  # line 221
        del repo["format"]  # simulate pre-1.3.5  # line 222
        with codecs.open(sos.encode(os.path.join(sos.metaFolder, sos.metaFile)), "w", encoding=sos.UTF8) as fd:  # line 223
            json.dump((repo, branches, config), fd, ensure_ascii=False)  # line 223
        out = wrapChannels(lambda: sos.status(options=["--repo"]))  # line 224
        _.assertAllIn(["pre-1.2", "Upgraded repository metadata to match SOS version '2018.1210.3028'", "Upgraded repository metadata to match SOS version '1.3.5'"], out)  # line 225

    def testFastBranching(_):  # line 227
        _.createFile(1)  # line 228
        sos.offline(options=["--strict"])  # b0/r0 = ./file1  # line 229
        _.createFile(2)  # line 230
        os.unlink("file1")  # line 231
        sos.commit()  # b0/r1 = ./file2  # line 232
        sos.branch(options=["--fast", "--last"])  # branch b1 from b0/1 TODO modify once --fast becomes the new normal  # line 233
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0", "b1"], os.listdir(sos.metaFolder), only=True)  # line 234
        _.createFile(3)  # line 235
        sos.commit()  # b1/r2 = ./file2, ./file3  # line 236
        _.assertAllIn([sos.metaFile, "r2"], os.listdir(sos.branchFolder(1)), only=True)  # line 237
        sos.branch(options=["--fast", "--last"])  # branch b2 from b1/2  # line 238
        sos.destroy("0")  # remove parent of b1 and transitive parent of b2  # line 239
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1", "b2"], os.listdir(sos.metaFolder), only=True)  # branch 0 was removed  # line 240
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(1)), only=True)  # revisions were copied to branch 1  # line 241
        _.assertAllIn([sos.metaFile, "r0", "r1", "r2"], os.listdir(sos.branchFolder(2)), only=True)  # revisions were copied to branch 1  # line 242
# TODO test also other functions like status --repo, log

    def testGetParentBranch(_):  # line 245
        m = sos.Accessor({"branches": {0: sos.Accessor({"parent": None, "revision": None}), 1: sos.Accessor({"parent": 0, "revision": 1})}})  # line 246
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 0))  # line 247
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 1, 1))  # line 248
        _.assertEqual(1, sos.Metadata.getParentBranch(m, 1, 2))  # line 249
        _.assertEqual(0, sos.Metadata.getParentBranch(m, 0, 10))  # line 250

    def testTokenizeGlobPattern(_):  # line 252
        _.assertEqual([], sos.tokenizeGlobPattern(""))  # line 253
        _.assertEqual([sos.GlobBlock(False, "*", 0)], sos.tokenizeGlobPattern("*"))  # line 254
        _.assertEqual([sos.GlobBlock(False, "*", 0), sos.GlobBlock(False, "???", 1)], sos.tokenizeGlobPattern("*???"))  # line 255
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(True, "x", 2)], sos.tokenizeGlobPattern("x*x"))  # line 256
        _.assertEqual([sos.GlobBlock(True, "x", 0), sos.GlobBlock(False, "*", 1), sos.GlobBlock(False, "??", 2), sos.GlobBlock(False, "*", 4), sos.GlobBlock(True, "x", 5)], sos.tokenizeGlobPattern("x*??*x"))  # line 257
        _.assertEqual([sos.GlobBlock(False, "?", 0), sos.GlobBlock(True, "abc", 1), sos.GlobBlock(False, "*", 4)], sos.tokenizeGlobPattern("?abc*"))  # line 258

    def testTokenizeGlobPatterns(_):  # line 260
        try:  # because number of literal strings differs  # line 261
            sos.tokenizeGlobPatterns("x*x", "x*")  # because number of literal strings differs  # line 261
            _.fail()  # because number of literal strings differs  # line 261
        except:  # line 262
            pass  # line 262
        try:  # because glob patterns differ  # line 263
            sos.tokenizeGlobPatterns("x*", "x?")  # because glob patterns differ  # line 263
            _.fail()  # because glob patterns differ  # line 263
        except:  # line 264
            pass  # line 264
        try:  # glob patterns differ, regardless of position  # line 265
            sos.tokenizeGlobPatterns("x*", "?x")  # glob patterns differ, regardless of position  # line 265
            _.fail()  # glob patterns differ, regardless of position  # line 265
        except:  # line 266
            pass  # line 266
        sos.tokenizeGlobPatterns("x*", "*x")  # succeeds, because glob patterns match (differ only in position)  # line 267
        sos.tokenizeGlobPatterns("*xb?c", "*x?bc")  # succeeds, because glob patterns match (differ only in position)  # line 268
        try:  # succeeds, because glob patterns match (differ only in position)  # line 269
            sos.tokenizeGlobPatterns("a???b*", "ab???*")  # succeeds, because glob patterns match (differ only in position)  # line 269
            _.fail()  # succeeds, because glob patterns match (differ only in position)  # line 269
        except:  # line 270
            pass  # line 270

    def testConvertGlobFiles(_):  # line 272
        _.assertEqual(["xxayb", "aacb"], [r[1] for r in sos.convertGlobFiles(["axxby", "aabc"], *sos.tokenizeGlobPatterns("a*b?", "*a?b"))])  # line 273
        _.assertEqual(["1qq2ww3", "1abcbx2xbabc3"], [r[1] for r in sos.convertGlobFiles(["qqxbww", "abcbxxbxbabc"], *sos.tokenizeGlobPatterns("*xb*", "1*2*3"))])  # line 274

    def testFolderRemove(_):  # line 276
        m = sos.Metadata(os.getcwd())  # line 277
        _.createFile(1)  # line 278
        _.createFile("a", prefix="sub")  # line 279
        sos.offline()  # line 280
        _.createFile(2)  # line 281
        os.unlink("sub" + os.sep + "a")  # line 282
        os.rmdir("sub")  # line 283
        changes = sos.changes()  # TODO replace by output check  # line 284
        _.assertEqual(1, len(changes.additions))  # line 285
        _.assertEqual(0, len(changes.modifications))  # line 286
        _.assertEqual(1, len(changes.deletions))  # line 287
        _.createFile("a", prefix="sub")  # line 288
        changes = sos.changes()  # line 289
        _.assertEqual(0, len(changes.deletions))  # line 290

    def testSwitchConflict(_):  # line 292
        sos.offline(options=["--strict"])  # (r0)  # line 293
        _.createFile(1)  # line 294
        sos.commit()  # add file (r1)  # line 295
        os.unlink("file1")  # line 296
        sos.commit()  # remove (r2)  # line 297
        _.createFile(1, "something else")  # line 298
        sos.commit()  # (r3)  # line 299
        sos.switch("/1")  # updates file1 - marked as MOD, because mtime was changed  # line 300
        _.existsFile(1, "x" * 10)  # line 301
        sos.switch("/2", ["--force"])  # remove file1 requires --force, because size/content (or mtime in non-strict mode) is different to head of branch  # line 302
        sos.switch("/0")  # do nothing, as file1 is already removed  # line 303
        sos.switch("/1")  # add file1 back  # line 304
        sos.switch("/", ["--force"])  # requires force because changed vs. head of branch  # line 305
        _.existsFile(1, "something else")  # line 306

    def testComputeSequentialPathSet(_):  # line 308
        os.makedirs(sos.revisionFolder(0, 0))  # line 309
        os.makedirs(sos.revisionFolder(0, 1))  # line 310
        os.makedirs(sos.revisionFolder(0, 2))  # line 311
        os.makedirs(sos.revisionFolder(0, 3))  # line 312
        os.makedirs(sos.revisionFolder(0, 4))  # line 313
        m = sos.Metadata(os.getcwd())  # line 314
        m.branch = 0  # line 315
        m.commit = 2  # line 316
        m.saveBranches()  # line 317
        m.paths = {"./a": sos.PathInfo("", 0, 0, "")}  # line 318
        m.saveCommit(0, 0)  # initial  # line 319
        m.paths["./a"] = sos.PathInfo("", 1, 0, "")  # line 320
        m.saveCommit(0, 1)  # mod  # line 321
        m.paths["./b"] = sos.PathInfo("", 0, 0, "")  # line 322
        m.saveCommit(0, 2)  # add  # line 323
        m.paths["./a"] = sos.PathInfo("", None, 0, "")  # line 324
        m.saveCommit(0, 3)  # del  # line 325
        m.paths["./a"] = sos.PathInfo("", 2, 0, "")  # line 326
        m.saveCommit(0, 4)  # readd  # line 327
        m.commits = {i: sos.CommitInfo(i, 0, None) for i in range(5)}  # line 328
        m.saveBranch(0)  # line 329
        m.branches = {0: sos.BranchInfo(0, 0), 1: sos.BranchInfo(1, 0)}  # line 330
        m.saveBranches()  # line 331
        m.computeSequentialPathSet(0, 4)  # line 332
        _.assertEqual(2, len(m.paths))  # line 333

    def testParseRevisionString(_):  # line 335
        m = sos.Metadata(os.getcwd())  # line 336
        m.branch = 1  # line 337
        m.commits = {0: 0, 1: 1, 2: 2}  # line 338
        _.assertEqual((1, 3), m.parseRevisionString("3"))  # line 339
        _.assertEqual((2, 3), m.parseRevisionString("2/3"))  # line 340
        _.assertEqual((1, -1), m.parseRevisionString(None))  # line 341
        _.assertEqual((1, -1), m.parseRevisionString(""))  # line 342
        _.assertEqual((2, -1), m.parseRevisionString("2/"))  # line 343
        _.assertEqual((1, -2), m.parseRevisionString("/-2"))  # line 344
        _.assertEqual((1, -1), m.parseRevisionString("/"))  # line 345

    def testOfflineEmpty(_):  # line 347
        os.mkdir("." + os.sep + sos.metaFolder)  # line 348
        try:  # line 349
            sos.offline("trunk")  # line 349
            _.fail()  # line 349
        except SystemExit as E:  # line 350
            _.assertEqual(1, E.code)  # line 350
        os.rmdir("." + os.sep + sos.metaFolder)  # line 351
        sos.offline("test")  # line 352
        _.assertIn(sos.metaFolder, os.listdir("."))  # line 353
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 354
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 355
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 356
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 357
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file  # line 358

    def testOfflineWithFiles(_):  # line 360
        _.createFile(1, "x" * 100)  # line 361
        _.createFile(2)  # line 362
        sos.offline("test")  # line 363
        _.assertAllIn(["file1", "file2", sos.metaFolder], os.listdir("."))  # line 364
        _.assertAllIn(["b0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 365
        _.assertAllIn(["r0", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 366
        _.assertAllIn([sos.metaFile, "03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2", "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0" + os.sep + "r0"))  # line 367
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder)))  # only branch folder and meta data file  # line 368
        _.assertEqual(2, len(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0")))  # only commit folder and meta data file  # line 369
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 0))))  # only meta data file plus branch base file copies  # line 370

    def testBranch(_):  # line 372
        _.createFile(1, "x" * 100)  # line 373
        _.createFile(2)  # line 374
        sos.offline("test")  # b0/r0  # line 375
        sos.branch("other")  # b1/r0  # line 376
        _.assertAllIn(["b0", "b1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder))  # line 377
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b1"))))  # line 378
        _.assertEqual(list(sorted(os.listdir(sos.revisionFolder(0, 0)))), list(sorted(os.listdir(sos.revisionFolder(1, 0)))))  # line 380
        _.createFile(1, "z")  # modify file  # line 382
        sos.branch()  # b2/r0  branch to unnamed branch with modified file tree contents  # line 383
        _.assertNotEqual(os.stat(sos.encode("." + os.sep + sos.metaFolder + os.sep + "b1" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa")).st_size, os.stat(sos.encode("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0" + os.sep + "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa")).st_size)  # line 384
        _.createFile(3, "z")  # line 386
        sos.branch("from_last_revision", options=["--last", "--stay"])  # b3/r0 create copy of other file1,file2 and don't switch  # line 387
        _.assertEqual(list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b3" + os.sep + "r0"))), list(sorted(os.listdir("." + os.sep + sos.metaFolder + os.sep + "b2" + os.sep + "r0"))))  # line 388
# Check sos.status output which branch is marked


    def testComittingAndChanges(_):  # line 393
        _.createFile(1, "x" * 100)  # line 394
        _.createFile(2)  # line 395
        sos.offline("test")  # line 396
        changes = sos.changes()  # line 397
        _.assertEqual(0, len(changes.additions))  # line 398
        _.assertEqual(0, len(changes.deletions))  # line 399
        _.assertEqual(0, len(changes.modifications))  # line 400
        _.createFile(1, "z")  # size change  # line 401
        changes = sos.changes()  # line 402
        _.assertEqual(0, len(changes.additions))  # line 403
        _.assertEqual(0, len(changes.deletions))  # line 404
        _.assertEqual(1, len(changes.modifications))  # line 405
        sos.commit("message")  # line 406
        _.assertAllIn(["r0", "r1", sos.metaFile], os.listdir("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 407
        _.assertAllIn([sos.metaFile, "b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"], os.listdir(sos.revisionFolder(0, 1)))  # line 408
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # no further files, only the modified one  # line 409
        _.assertEqual(1, len(sos.changes("/0").modifications))  # vs. explicit revision on current branch  # line 410
        _.assertEqual(1, len(sos.changes("0/0").modifications))  # vs. explicit branch/revision  # line 411
        _.createFile(1, "")  # modify to empty file, mentioned in meta data, but not stored as own file  # line 412
        os.unlink("file2")  # line 413
        changes = sos.changes()  # line 414
        _.assertEqual(0, len(changes.additions))  # line 415
        _.assertEqual(1, len(changes.deletions))  # line 416
        _.assertEqual(1, len(changes.modifications))  # line 417
        sos.commit("modified")  # line 418
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # no additional files, only mentions in metadata  # line 419
        try:  # expecting Exit due to no changes  # line 420
            sos.commit("nothing")  # expecting Exit due to no changes  # line 420
            _.fail()  # expecting Exit due to no changes  # line 420
        except:  # line 421
            pass  # line 421

    def testGetBranch(_):  # line 423
        m = sos.Metadata(os.getcwd())  # line 424
        m.branch = 1  # current branch  # line 425
        m.branches = {0: sos.BranchInfo(0, 0, "trunk")}  # line 426
        _.assertEqual(27, m.getBranchByName(27))  # line 427
        _.assertEqual(0, m.getBranchByName("trunk"))  # line 428
        _.assertEqual(1, m.getBranchByName(""))  # split from "/"  # line 429
        _.assertIsNone(m.getBranchByName("unknown"))  # line 430
        m.commits = {0: sos.CommitInfo(0, 0, "bla")}  # line 431
        _.assertEqual(13, m.getRevisionByName("13"))  # line 432
        _.assertEqual(0, m.getRevisionByName("bla"))  # line 433
        _.assertEqual(-1, m.getRevisionByName(""))  # split from "/"  # line 434

    def testTagging(_):  # line 436
        m = sos.Metadata(os.getcwd())  # line 437
        sos.offline()  # line 438
        _.createFile(111)  # line 439
        sos.commit("tag", ["--tag"])  # line 440
        out = wrapChannels(lambda: sos.log()).replace("\r", "").split("\n")  # line 441
        _.assertTrue(any(("|tag" in line and line.endswith("|TAG") for line in out)))  # line 442
        _.createFile(2)  # line 443
        try:  # line 444
            sos.commit("tag")  # line 444
            _.fail()  # line 444
        except:  # line 445
            pass  # line 445
        sos.commit("tag-2", ["--tag"])  # line 446
        out = wrapChannels(lambda: sos.ls(options=["--tags"])).replace("\r", "")  # line 447
        _.assertIn("TAG tag", out)  # line 448

    def testSwitch(_):  # line 450
        _.createFile(1, "x" * 100)  # line 451
        _.createFile(2, "y")  # line 452
        sos.offline("test")  # file1-2  in initial branch commit  # line 453
        sos.branch("second")  # file1-2  switch, having same files  # line 454
        sos.switch("0")  # no change  switch back, no problem  # line 455
        sos.switch("second")  # no change  # switch back, no problem  # line 456
        _.createFile(3, "y")  # generate a file  # line 457
        try:  # uncommited changes detected  # line 458
            sos.switch("test")  # uncommited changes detected  # line 458
            _.fail()  # uncommited changes detected  # line 458
        except SystemExit as E:  # line 459
            _.assertEqual(1, E.code)  # line 459
        sos.commit("Finish")  # file1-3  commit third file into branch second  # line 460
        sos.changes()  # line 461
        sos.switch("test")  # file1-2, remove file3 from file tree  # line 462
        _.assertFalse(_.existsFile(3))  # removed when switching back to test  # line 463
        _.createFile("XXX")  # line 464
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 465
        _.assertIn("File tree has changes", out)  # line 466
        _.assertNotIn("File tree is unchanged", out)  # line 467
        _.assertIn("  * b00   'test'", out)  # line 468
        _.assertIn("    b01 'second'", out)  # line 469
        _.assertIn("(dirty)", out)  # one branch has commits  # line 470
        _.assertIn("(in sync)", out)  # the other doesn't  # line 471
        sos.defaults["useChangesCommand"] = False  # because sos.main() is never called  # line 472
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # trigger repo info  # line 473
        _.assertAllIn(["Metadata format", "Content checking:    deactivated", "Data compression:    deactivated", "Repository mode:     simple", "Number of branches:  2"], out)  # line 474
        sos.defaults["useChangesCommand"] = True  # because sos.main() is never called  # line 475
        _.createFile(4, "xy")  # generate a file  # line 476
        sos.switch("second", ["--force"])  # avoids warning on uncommited changes, but keeps file4  # line 477
        _.assertFalse(_.existsFile(4))  # removed when forcedly switching back to test  # line 478
        _.assertTrue(_.existsFile(3))  # was restored from branch's revision r1  # line 479
        os.unlink("." + os.sep + "file1")  # remove old file1  # line 480
        sos.switch("test", ["--force"])  # should restore file1 and remove file3  # line 481
        _.assertTrue(_.existsFile(1))  # was restored from branch's revision r1  # line 482
        _.assertFalse(_.existsFile(3))  # was restored from branch's revision r1  # line 483
        out = wrapChannels(lambda: sos.dump("dumped.sos.zip", options=["--skip-backup", "--full"])).replace("\r", "")  # line 484
        _.assertAllIn(["Dumping revisions"], out)  # line 485
        _.assertNotIn("Creating backup", out)  # line 486
        out = wrapChannels(lambda: sos.dump("dumped.sos.zip", options=["--skip-backup"])).replace("\r", "")  # line 487
        _.assertIn("Dumping revisions", out)  # line 488
        _.assertNotIn("Creating backup", out)  # line 489
        out = wrapChannels(lambda: sos.dump("dumped.sos.zip", options=["--full"])).replace("\r", "")  # line 490
        _.assertAllIn(["Creating backup"], out)  # line 491
        _.assertIn("Dumping revisions", out)  # line 492

    def testAutoDetectVCS(_):  # line 494
        os.mkdir(".git")  # line 495
        sos.offline(sos.vcsBranches[sos.findSosVcsBase()[2]])  # create initial branch  # line 496
        with open(sos.metaFolder + os.sep + sos.metaFile, "r") as fd:  # line 497
            meta = fd.read()  # line 497
        _.assertTrue("\"master\"" in meta)  # line 498
        os.rmdir(".git")  # line 499

    def testUpdate(_):  # line 501
        sos.offline("trunk")  # create initial branch b0/r0  # line 502
        _.createFile(1, "x" * 100)  # line 503
        sos.commit("second")  # create b0/r1  # line 504

        sos.switch("/0")  # go back to b0/r0 - deletes file1  # line 506
        _.assertFalse(_.existsFile(1))  # line 507

        sos.update("/1")  # recreate file1  # line 509
        _.assertTrue(_.existsFile(1))  # line 510

        sos.commit("third", ["--force"])  # force because nothing to commit. should create r2 with same contents as r1, but as differential from r1, not from r0 (= no changes in meta folder)  # line 512
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2)))  # line 513
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 2, file=sos.metaFile)))  # line 514
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta data file, no differential files  # line 515

        sos.update("/1")  # do nothing, as nothing has changed  # line 517
        _.assertTrue(_.existsFile(1))  # line 518

        _.createFile(2, "y" * 100)  # line 520
#    out = wrapChannels(() -> sos.branch("other"))  # won't comply as there are changes
#    _.assertIn("--force", out)
        sos.branch("other", options=["--force"])  # automatically including file 2 (as we are in simple mode)  # line 523
        _.assertTrue(_.existsFile(2))  # line 524
        sos.update("trunk", ["--add"])  # only add stuff  # line 525
        _.assertTrue(_.existsFile(2))  # line 526
        sos.update("trunk")  # nothing to do  # line 527
        _.assertFalse(_.existsFile(2))  # removes file not present in original branch  # line 528

        theirs = b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk"  # line 530
        _.createFile(10, theirs)  # line 531
        mine = b"a\nc\nd\ne\ng\nf\nx\nh\ny\ny\nj"  # missing "b", inserted g, modified g->x, replace x/x -> y/y, removed k  # line 532
        _.createFile(11, mine)  # line 533
        _.assertEqual((b"a\nb\nc\nd\ne\nf\ng\nh\nx\nx\nj\nk", b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.BOTH))  # completely recreated other file  # line 534
        _.assertEqual((b'a\nb\nc\nd\ne\ng\nf\ng\nh\ny\ny\nx\nx\nj\nk', b"\n"), sos.merge(filename="." + os.sep + "file10", intoname="." + os.sep + "file11", mergeOperation=sos.MergeOperation.INSERT))  # line 535

    def testUpdate2(_):  # line 537
        _.createFile("test.txt", "x" * 10)  # line 538
        sos.offline("trunk", ["--strict"])  # use strict mode, as timestamp differences are too small for testing  # line 539
        sync()  # line 540
        sos.branch("mod")  # line 541
        _.createFile("test.txt", "x" * 5 + "y" * 5)  # line 542
        sos.commit("mod")  # create b0/r1  # line 543
        sos.switch("trunk", ["--force"])  # should replace contents, force in case some other files were modified (e.g. during working on the code) TODO investigate more  # line 544
        _.assertTrue(_.existsFile("test.txt", b"x" * 10))  # line 545
        sos.update("mod")  # integrate changes TODO same with ask -> theirs  # line 546
        _.existsFile("test.txt", b"x" * 5 + b"y" * 5)  # line 547
        _.createFile("test.txt", "x" * 10)  # line 548
        mockInput(["t"], lambda: sos.update("mod", ["--ask-lines"]))  # line 549
        sync()  # line 550
        _.assertTrue(_.existsFile("test.txt", b"x" * 5 + b"y" * 5))  # line 551
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 552
        sos.update("mod")  # auto-insert/removes (no intra-line conflict)  # line 553
        _.createFile("test.txt", "x" * 5 + "z" + "y" * 4)  # line 554
        sync()  # line 555
        mockInput(["t"], lambda: sos.update("mod", ["--ask"]))  # same as above with interaction -> use theirs (overwrite current file state)  # line 556
        _.assertTrue(_.existsFile("test.txt", b"x" * 5 + b"y" * 5))  # line 557

    def testIsTextType(_):  # line 559
        m = sos.Metadata(".")  # line 560
        m.c.texttype = ["*.x", "*.md", "*.md.*"]  # line 561
        m.c.bintype = ["*.md.confluence"]  # line 562
        _.assertTrue(m.isTextType("ab.txt"))  # line 563
        _.assertTrue(m.isTextType("./ab.txt"))  # line 564
        _.assertTrue(m.isTextType("bc/ab.txt"))  # line 565
        _.assertFalse(m.isTextType("bc/ab."))  # line 566
        _.assertTrue(m.isTextType("23_3.x.x"))  # line 567
        _.assertTrue(m.isTextType("dfg/dfglkjdf7/test.md"))  # line 568
        _.assertTrue(m.isTextType("./test.md.pdf"))  # line 569
        _.assertFalse(m.isTextType("./test_a.md.confluence"))  # line 570

    def testEolDet(_):  # line 572
        ''' Check correct end-of-line detection. '''  # line 573
        _.assertEqual(b"\n", sos.eoldet(b"a\nb"))  # line 574
        _.assertEqual(b"\r\n", sos.eoldet(b"a\r\nb\r\n"))  # line 575
        _.assertEqual(b"\r", sos.eoldet(b"\ra\rb"))  # line 576
        _.assertAllIn(["Inconsistent", "with "], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\r\na\r\nb\n"))))  # line 577
        _.assertAllIn(["Inconsistent", "without"], wrapChannels(lambda: _.assertEqual(b"\n", sos.eoldet(b"\ra\nnb\n"))))  # line 578
        _.assertIsNone(sos.eoldet(b""))  # line 579
        _.assertIsNone(sos.eoldet(b"sdf"))  # line 580

    def testMerge(_):  # line 582
        ''' Check merge results depending on user options. '''  # line 583
        a = b"a\nb\ncc\nd"  # type: bytes  # line 584
        b = b"a\nb\nee\nd"  # type: bytes  # replaces cc by ee  # line 585
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # one-line block replacement using lineMerge  # line 586
        _.assertEqual(b"a\nb\neecc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.INSERT)[0])  # means insert changes from a into b, but don't replace  # line 587
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # means insert changes from a into b, but don't replace  # line 588
        _.assertEqual(b"a\nb\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # one-line block replacement using lineMerge  # line 589
        _.assertEqual(b"a\nb\n\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE, charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 590
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 591
        a = b"a\nb\ncc\nd"  # line 592
        b = b"a\nb\nee\nf\nd"  # replaces cc by block of two lines ee, f  # line 593
        _.assertEqual(b"a\nb\nee\nf\ncc\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.INSERT)[0])  # multi-line block replacement  # line 594
        _.assertEqual(b"a\nb\nd", sos.merge(a, b, mergeOperation=sos.MergeOperation.REMOVE)[0])  # line 595
        _.assertEqual(a, sos.merge(a, b, mergeOperation=sos.MergeOperation.BOTH)[0])  # keeps any changes in b  # line 596
# Test with change + insert
        _.assertEqual(b"a\nb fdcd d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.INSERT)[0])  # line 598
        _.assertEqual(b"a\nb d d\ne", sos.merge(b"a\nb cd d\ne", b"a\nb fdd d\ne", charMergeOperation=sos.MergeOperation.REMOVE)[0])  # line 599
# Test interactive merge
        a = b"a\nb\nb\ne"  # block-wise replacement  # line 601
        b = b"a\nc\ne"  # line 602
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 603
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, mergeOperation=sos.MergeOperation.ASK)[0]))  # line 604
        a = b"a\nb\ne"  # intra-line merge  # line 605
        _.assertEqual(b, mockInput(["i"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 606
        _.assertEqual(a, mockInput(["t"], lambda: sos.merge(a, b, charMergeOperation=sos.MergeOperation.ASK)[0]))  # line 607

    def testMergeEol(_):  # line 609
        _.assertEqual(b"\r\n", sos.merge(b"a\nb", b"a\r\nb")[1])  # line 610
        _.assertIn("Differing EOL-styles", wrapChannels(lambda: sos.merge(b"a\nb", b"a\r\nb")))  # expects a warning  # line 611
        _.assertIn(b"a\r\nb", sos.merge(b"a\nb", b"a\r\nb")[0])  # when in doubt, use "mine" CR-LF  # line 612
        _.assertIn(b"a\nb", sos.merge(b"a\nb", b"a\r\nb", eol=True)[0])  # line 613
        _.assertEqual(b"\n", sos.merge(b"a\nb", b"a\r\nb", eol=True)[1])  # line 614

    def testPickyMode(_):  # line 616
        ''' Confirm that picky mode reset tracked patterns after commits. '''  # line 617
        sos.offline("trunk", None, ["--picky"])  # line 618
        changes = sos.changes()  # line 619
        _.assertEqual(0, len(changes.additions))  # do not list any existing file as an addition  # line 620
        sos.add(".", "./file?", ["--force"])  # line 621
        _.createFile(1, "aa")  # line 622
        sos.commit("First")  # add one file  # line 623
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 624
        _.createFile(2, "b")  # line 625
        try:  # add nothing, because picky  # line 626
            sos.commit("Second")  # add nothing, because picky  # line 626
        except:  # line 627
            pass  # line 627
        sos.add(".", "./file?")  # line 628
        sos.commit("Third")  # line 629
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # line 630
        out = wrapChannels(lambda: sos.log([])).replace("\r", "")  # line 631
        _.assertIn("  * r2", out)  # line 632
        _.createFile(3, prefix="sub")  # line 633
        sos.add("sub", "sub/file?")  # line 634
        changes = sos.changes()  # line 635
        _.assertEqual(1, len(changes.additions))  # line 636
        _.assertTrue("sub/file3" in changes.additions)  # line 637

    def testTrackedSubfolder(_):  # line 639
        ''' See if patterns for files in sub folders are picked up correctly. '''  # line 640
        os.mkdir("." + os.sep + "sub")  # line 641
        sos.offline("trunk", None, ["--track"])  # line 642
        _.createFile(1, "x")  # line 643
        _.createFile(1, "x", prefix="sub")  # line 644
        sos.add(".", "./file?")  # add glob pattern to track  # line 645
        sos.commit("First")  # line 646
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 647
        sos.add(".", "sub/file?")  # add glob pattern to track  # line 648
        sos.commit("Second")  # one new file + meta  # line 649
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 650
        os.unlink("file1")  # remove from basefolder  # line 651
        _.createFile(2, "y")  # line 652
        sos.remove(".", "sub/file?")  # line 653
        try:  # raises Exit. TODO test the "suggest a pattern" case  # line 654
            sos.remove(".", "sub/bla")  # raises Exit. TODO test the "suggest a pattern" case  # line 654
            _.fail()  # raises Exit. TODO test the "suggest a pattern" case  # line 654
        except:  # line 655
            pass  # line 655
        sos.commit("Third")  # line 656
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta  # line 657
# TODO also check if /file1 and sub/file1 were removed from index

    def testTrackedMode(_):  # line 660
        ''' Difference in semantics vs simple mode:
          - For remote/other branch we can only know and consider tracked files, thus ignoring all complexity stemming from handling addition of untracked files.
          - For current branch, we can take into account tracked and untracked ones, in theory, but it doesn't make sense.
        In conclusion, using the union of tracking patterns from both sides to find affected files makes sense, but disallow deleting files not present in remote branch.
    '''  # line 665
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 666
        _.createFile(1)  # line 667
        _.createFile("a123a")  # untracked file "a123a"  # line 668
        sos.add(".", "./file?")  # add glob tracking pattern  # line 669
        sos.commit("second")  # versions "file1"  # line 670
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # one new file + meta file  # line 671
        out = wrapChannels(lambda: sos.status()).replace("\r", "")  # line 672
        _.assertIn("  | ./file?", out)  # line 673

        _.createFile(2)  # untracked file "file2"  # line 675
        sos.commit("third")  # versions "file2"  # line 676
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # one new file + meta file  # line 677

        os.mkdir("." + os.sep + "sub")  # line 679
        _.createFile(3, prefix="sub")  # untracked file "sub/file3"  # line 680
        sos.commit("fourth", ["--force"])  # no tracking pattern matches the subfolder  # line 681
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 3))))  # meta file only, no other tracked path/file  # line 682

        sos.branch("Other")  # second branch containing file1 and file2 tracked by "./file?"  # line 684
        sos.remove(".", "./file?")  # remove tracking pattern, but don't touch previously created and versioned files  # line 685
        sos.add(".", "./a*a")  # add tracking pattern  # line 686
        changes = sos.changes()  # should pick up addition only, because tracked, but not the deletion, as not tracked anymore  # line 687
        _.assertEqual(0, len(changes.modifications))  # line 688
        _.assertEqual(0, len(changes.deletions))  # not tracked anymore, but contained in version history and not removed  # line 689
        _.assertEqual(1, len(changes.additions))  # detected one addition "a123a", but won't recognize untracking files as deletion  # line 690

        sos.commit("Second_2")  # line 692
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(1, 1))))  # "a123a" + meta file  # line 693
        _.existsFile(1, b"x" * 10)  # line 694
        _.existsFile(2, b"x" * 10)  # line 695

        sos.switch("test")  # go back to first branch - tracks only "file?", but not "a*a"  # line 697
        _.existsFile(1, b"x" * 10)  # line 698
        _.existsFile("a123a", b"x" * 10)  # line 699

        sos.update("Other")  # integrate tracked files and tracking pattern from second branch into working state of master branch  # line 701
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 702
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 703

        _.createFile("axxxa")  # new file that should be tracked on "test" now that we integrated "Other"  # line 705
        sos.commit("fifth")  # create new revision after integrating updates from second branch  # line 706
        _.assertEqual(3, len(os.listdir(sos.revisionFolder(0, 4))))  # one new file from other branch + one new in current folder + meta file  # line 707
        sos.switch("Other")  # switch back to just integrated branch that tracks only "a*a" - shouldn't do anything  # line 708
        _.assertTrue(os.path.exists("." + os.sep + "file1"))  # line 709
        _.assertTrue(os.path.exists("." + os.sep + "a123a"))  # line 710
        _.assertFalse(os.path.exists("." + os.sep + "axxxa"))  # because tracked in both branches, but not present in other -> delete in file tree  # line 711
# TODO test switch --meta

    def testLsTracked(_):  # line 714
        sos.offline("test", options=["--track"])  # set up repo in tracking mode (SVN- or gitless-style)  # line 715
        _.createFile(1)  # line 716
        _.createFile("foo")  # line 717
        sos.add(".", "./file*")  # capture one file  # line 718
        sos.ls()  # line 719
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 720
        _.assertInAny("TRK file1  (file*)", out)  # line 721
        _.assertNotInAny("... file1  (file*)", out)  # line 722
        _.assertInAny("··· foo", out)  # line 723
        out = sos.safeSplit(wrapChannels(lambda: sos.ls(options=["--patterns"])).replace("\r", ""), "\n")  # line 724
        _.assertInAny("TRK file*", out)  # line 725
        _.createFile("a", prefix="sub")  # line 726
        sos.add("sub", "sub/a")  # line 727
        sos.ls("sub")  # line 728
        _.assertIn("TRK a  (a)", sos.safeSplit(wrapChannels(lambda: sos.ls("sub")).replace("\r", ""), "\n"))  # line 729

    def testLineMerge(_):  # line 731
        _.assertEqual("xabc", sos.lineMerge("xabc", "a bd"))  # line 732
        _.assertEqual("xabxxc", sos.lineMerge("xabxxc", "a bd"))  # line 733
        _.assertEqual("xa bdc", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.INSERT))  # line 734
        _.assertEqual("ab", sos.lineMerge("xabc", "a bd", mergeOperation=sos.MergeOperation.REMOVE))  # line 735

    def testCompression(_):  # TODO test output ratio/advantage, also depending on compress flag set or not  # line 737
        _.createFile(1)  # line 738
        sos.offline("master", options=["--force"])  # line 739
        out = wrapChannels(lambda: sos.changes(options=['--progress'])).replace("\r", "").split("\n")  # line 740
        _.assertFalse(any(("Compression advantage" in line for line in out)))  # simple mode should always print this to stdout  # line 741
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 0, file="b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa"), b"x" * 10))  # line 742
        setRepoFlag("compress", True)  # was plain = uncompressed before  # line 743
        _.createFile(2)  # line 744
        out = wrapChannels(lambda: sos.commit("Added file2", options=['--progress'])).replace("\r", "").split("\n")  # line 745
        _.assertTrue(any(("Compression advantage" in line for line in out)))  # line 746
        _.assertTrue(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2")))  # exists  # line 747
        _.assertFalse(_.existsFile(sos.revisionFolder(0, 1, file="03b69bc801ae11f1ff2a71a50f165996d0ad681b4f822df13329a27e53f0fcd2"), b"x" * 10))  # but is compressed instead  # line 748

    def testLocalConfig(_):  # line 750
        sos.offline("bla", options=[])  # line 751
        try:  # line 752
            sos.config(["set", "ignores", "one;two"], options=["--local"])  # line 752
        except SystemExit as E:  # line 753
            _.assertEqual(0, E.code)  # line 753
        _.assertTrue(checkRepoFlag("ignores", value=["one", "two"]))  # line 754

    def testConfigVariations(_):  # line 756
        def makeRepo():  # line 757
            try:  # line 758
                os.unlink("file1")  # line 758
            except:  # line 759
                pass  # line 759
            sos.offline("master", options=["--force"])  # line 760
            _.createFile(1)  # line 761
            sos.commit("Added file1")  # line 762
        try:  # line 763
            sos.config(["set", "strict", "on"])  # line 763
        except SystemExit as E:  # line 764
            _.assertEqual(0, E.code)  # line 764
        makeRepo()  # line 765
        _.assertTrue(checkRepoFlag("strict", True))  # line 766
        try:  # line 767
            sos.config(["set", "strict", "off"])  # line 767
        except SystemExit as E:  # line 768
            _.assertEqual(0, E.code)  # line 768
        makeRepo()  # line 769
        _.assertTrue(checkRepoFlag("strict", False))  # line 770
        try:  # line 771
            sos.config(["set", "strict", "yes"])  # line 771
        except SystemExit as E:  # line 772
            _.assertEqual(0, E.code)  # line 772
        makeRepo()  # line 773
        _.assertTrue(checkRepoFlag("strict", True))  # line 774
        try:  # line 775
            sos.config(["set", "strict", "no"])  # line 775
        except SystemExit as E:  # line 776
            _.assertEqual(0, E.code)  # line 776
        makeRepo()  # line 777
        _.assertTrue(checkRepoFlag("strict", False))  # line 778
        try:  # line 779
            sos.config(["set", "strict", "1"])  # line 779
        except SystemExit as E:  # line 780
            _.assertEqual(0, E.code)  # line 780
        makeRepo()  # line 781
        _.assertTrue(checkRepoFlag("strict", True))  # line 782
        try:  # line 783
            sos.config(["set", "strict", "0"])  # line 783
        except SystemExit as E:  # line 784
            _.assertEqual(0, E.code)  # line 784
        makeRepo()  # line 785
        _.assertTrue(checkRepoFlag("strict", False))  # line 786
        try:  # line 787
            sos.config(["set", "strict", "true"])  # line 787
        except SystemExit as E:  # line 788
            _.assertEqual(0, E.code)  # line 788
        makeRepo()  # line 789
        _.assertTrue(checkRepoFlag("strict", True))  # line 790
        try:  # line 791
            sos.config(["set", "strict", "false"])  # line 791
        except SystemExit as E:  # line 792
            _.assertEqual(0, E.code)  # line 792
        makeRepo()  # line 793
        _.assertTrue(checkRepoFlag("strict", False))  # line 794
        try:  # line 795
            sos.config(["set", "strict", "enable"])  # line 795
        except SystemExit as E:  # line 796
            _.assertEqual(0, E.code)  # line 796
        makeRepo()  # line 797
        _.assertTrue(checkRepoFlag("strict", True))  # line 798
        try:  # line 799
            sos.config(["set", "strict", "disable"])  # line 799
        except SystemExit as E:  # line 800
            _.assertEqual(0, E.code)  # line 800
        makeRepo()  # line 801
        _.assertTrue(checkRepoFlag("strict", False))  # line 802
        try:  # line 803
            sos.config(["set", "strict", "enabled"])  # line 803
        except SystemExit as E:  # line 804
            _.assertEqual(0, E.code)  # line 804
        makeRepo()  # line 805
        _.assertTrue(checkRepoFlag("strict", True))  # line 806
        try:  # line 807
            sos.config(["set", "strict", "disabled"])  # line 807
        except SystemExit as E:  # line 808
            _.assertEqual(0, E.code)  # line 808
        makeRepo()  # line 809
        _.assertTrue(checkRepoFlag("strict", False))  # line 810
        try:  # line 811
            sos.config(["set", "strict", "nope"])  # line 811
            _.fail()  # line 811
        except SystemExit as E:  # line 812
            _.assertEqual(1, E.code)  # line 812

    def testLsSimple(_):  # line 814
        _.createFile(1)  # line 815
        _.createFile("foo")  # line 816
        _.createFile("ign1")  # line 817
        _.createFile("ign2")  # line 818
        sos.offline("test")  # set up repo in tracking mode (SVN- or gitless-style)  # line 819
        try:  # define an ignore pattern  # line 820
            sos.config(["set", "ignores", "ign1"])  # define an ignore pattern  # line 820
        except SystemExit as E:  # line 821
            _.assertEqual(0, E.code)  # line 821
        try:  # additional ignore pattern  # line 822
            sos.config(["add", "ignores", "ign2"])  # additional ignore pattern  # line 822
        except SystemExit as E:  # line 823
            _.assertEqual(0, E.code)  # line 823
        try:  # define a list of ignore patterns  # line 824
            sos.config(["set", "ignoresWhitelist", "ign1;ign2"])  # define a list of ignore patterns  # line 824
        except SystemExit as E:  # line 825
            _.assertEqual(0, E.code)  # line 825
        out = wrapChannels(lambda: sos.config(["show"])).replace("\r", "")  # line 826
        _.assertIn("             ignores [global]  ['ign1', 'ign2']", out)  # line 827
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 828
        _.assertInAny('··· file1', out)  # line 829
        _.assertInAny('··· ign1', out)  # line 830
        _.assertInAny('··· ign2', out)  # line 831
        try:  # line 832
            sos.config(["rm", "foo", "bar"])  # line 832
            _.fail()  # line 832
        except SystemExit as E:  # line 833
            _.assertEqual(1, E.code)  # line 833
        try:  # line 834
            sos.config(["rm", "ignores", "foo"])  # line 834
            _.fail()  # line 834
        except SystemExit as E:  # line 835
            _.assertEqual(1, E.code)  # line 835
        try:  # line 836
            sos.config(["rm", "ignores", "ign1"])  # line 836
        except SystemExit as E:  # line 837
            _.assertEqual(0, E.code)  # line 837
        try:  # remove ignore pattern  # line 838
            sos.config(["unset", "ignoresWhitelist"])  # remove ignore pattern  # line 838
        except SystemExit as E:  # line 839
            _.assertEqual(0, E.code)  # line 839
        out = sos.safeSplit(wrapChannels(lambda: sos.ls()).replace("\r", ""), "\n")  # line 840
        _.assertInAny('··· ign1', out)  # line 841
        _.assertInAny('IGN ign2', out)  # line 842
        _.assertNotInAny('··· ign2', out)  # line 843

    def testWhitelist(_):  # line 845
# TODO test same for simple mode
        _.createFile(1)  # line 847
        sos.defaults.ignores[:] = ["file*"]  # replace in-place  # line 848
        sos.offline("xx", options=["--track", "--strict"])  # because nothing to commit due to ignore pattern  # line 849
        sos.add(".", "./file*")  # add tracking pattern for "file1"  # line 850
        sos.commit(options=["--force"])  # attempt to commit the file  # line 851
        _.assertEqual(1, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta data, file1 was ignored  # line 852
        try:  # Exit because dirty  # line 853
            sos.online()  # Exit because dirty  # line 853
            _.fail()  # Exit because dirty  # line 853
        except:  # exception expected  # line 854
            pass  # exception expected  # line 854
        _.createFile("x2")  # add another change  # line 855
        sos.add(".", "./x?")  # add tracking pattern for "file1"  # line 856
        try:  # force beyond dirty flag check  # line 857
            sos.online(["--force"])  # force beyond dirty flag check  # line 857
            _.fail()  # force beyond dirty flag check  # line 857
        except:  # line 858
            pass  # line 858
        sos.online(["--force", "--force"])  # force beyond file tree modifications check  # line 859
        _.assertFalse(os.path.exists(sos.metaFolder))  # line 860

        _.createFile(1)  # line 862
        sos.defaults.ignoresWhitelist[:] = ["file*"]  # line 863
        sos.offline("xx", None, ["--track"])  # line 864
        sos.add(".", "./file*")  # line 865
        sos.commit()  # should NOT ask for force here  # line 866
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # meta data and "file1", file1 was whitelisted  # line 867

    def testRemove(_):  # line 869
        _.createFile(1, "x" * 100)  # line 870
        sos.offline("trunk")  # line 871
        try:  # line 872
            sos.destroy("trunk")  # line 872
            _fail()  # line 872
        except:  # line 873
            pass  # line 873
        _.createFile(2, "y" * 10)  # line 874
        sos.branch("added")  # creates new branch, writes repo metadata, and therefore creates backup copy  # line 875
        sos.destroy("trunk")  # line 876
        _.assertAllIn([sos.metaFile, sos.metaBack, "b0_last", "b1"], os.listdir("." + os.sep + sos.metaFolder))  # line 877
        _.assertTrue(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b1"))  # line 878
        _.assertFalse(os.path.exists("." + os.sep + sos.metaFolder + os.sep + "b0"))  # line 879
        sos.branch("next")  # line 880
        _.createFile(3, "y" * 10)  # make a change  # line 881
        sos.destroy("added", "--force")  # should succeed  # line 882

    def testUsage(_):  # line 884
        try:  # TODO expect sys.exit(0)  # line 885
            sos.usage()  # TODO expect sys.exit(0)  # line 885
            _.fail()  # TODO expect sys.exit(0)  # line 885
        except:  # line 886
            pass  # line 886
        try:  # line 887
            sos.usage(short=True)  # line 887
            _.fail()  # line 887
        except:  # line 888
            pass  # line 888

    def testOnlyExcept(_):  # line 890
        ''' Test blacklist glob rules. '''  # line 891
        sos.offline(options=["--track"])  # line 892
        _.createFile("a.1")  # line 893
        _.createFile("a.2")  # line 894
        _.createFile("b.1")  # line 895
        _.createFile("b.2")  # line 896
        sos.add(".", "./a.?")  # line 897
        sos.add(".", "./?.1", negative=True)  # line 898
        out = wrapChannels(lambda: sos.commit())  # line 899
        _.assertIn("ADD ./a.2", out)  # line 900
        _.assertNotIn("ADD ./a.1", out)  # line 901
        _.assertNotIn("ADD ./b.1", out)  # line 902
        _.assertNotIn("ADD ./b.2", out)  # line 903

    def testOnly(_):  # line 905
        _.assertEqual((_coconut.frozenset(("./A", "x/B")), _coconut.frozenset(("./C",))), sos.parseOnlyOptions(".", ["abc", "def", "--only", "A", "--x", "--only", "x/B", "--except", "C", "--only"]))  # line 906
        _.assertEqual(_coconut.frozenset(("B",)), sos.conditionalIntersection(_coconut.frozenset(("A", "B", "C")), _coconut.frozenset(("B", "D"))))  # line 907
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(_coconut.frozenset(), _coconut.frozenset(("B", "D"))))  # line 908
        _.assertEqual(_coconut.frozenset(("B", "D")), sos.conditionalIntersection(None, _coconut.frozenset(("B", "D"))))  # line 909
        sos.offline(options=["--track", "--strict"])  # line 910
        _.createFile(1)  # line 911
        _.createFile(2)  # line 912
        sos.add(".", "./file1")  # line 913
        sos.add(".", "./file2")  # line 914
        sos.commit(onlys=_coconut.frozenset(("./file1",)))  # line 915
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # only meta and file1  # line 916
        sos.commit()  # adds also file2  # line 917
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 2))))  # only meta and file1  # line 918
        _.createFile(1, "cc")  # modify both files  # line 919
        _.createFile(2, "dd")  # line 920
        try:  # line 921
            sos.config(["set", "texttype", "file2"])  # line 921
        except SystemExit as E:  # line 922
            _.assertEqual(0, E.code)  # line 922
        changes = sos.changes(excps=_coconut.frozenset(("./file1",)))  # line 923
        _.assertEqual(1, len(changes.modifications))  # only file2  # line 924
        _.assertTrue("./file2" in changes.modifications)  # line 925
        _.assertAllIn(["DIF ./file2", "<No newline>"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 926
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1", "MOD ./file2"], wrapChannels(lambda: sos.diff(onlys=_coconut.frozenset(("./file2",)))))  # line 927

    def testDiff(_):  # line 929
        try:  # manually mark this file as "textual"  # line 930
            sos.config(["set", "texttype", "file1"])  # manually mark this file as "textual"  # line 930
        except SystemExit as E:  # line 931
            _.assertEqual(0, E.code)  # line 931
        sos.offline(options=["--strict"])  # line 932
        _.createFile(1)  # line 933
        _.createFile(2)  # line 934
        sos.commit()  # line 935
        _.createFile(1, "sdfsdgfsdf")  # line 936
        _.createFile(2, "12343")  # line 937
        sos.commit()  # line 938
        _.createFile(1, "foobar")  # line 939
        _.createFile(3)  # line 940
        out = wrapChannels(lambda: sos.diff("/-2"))  # compare with r1 (second counting from last which is r2)  # line 941
        _.assertIn("ADD ./file3", out)  # line 942
        _.assertAllIn(["MOD ./file2", "DIF ./file1  <No newline>", "- | 0 |xxxxxxxxxx|", "+ | 0 |foobar|"], out)  # line 943
        _.assertAllNotIn(["MOD ./file1", "DIF ./file1"], wrapChannels(lambda: sos.diff("/-2", onlys=_coconut.frozenset(("./file2",)))))  # line 944

    def testReorderRenameActions(_):  # line 946
        result = sos.reorderRenameActions([("123", "312"), ("312", "132"), ("321", "123")], exitOnConflict=False)  # type: Tuple[str, str]  # line 947
        _.assertEqual([("312", "132"), ("123", "312"), ("321", "123")], result)  # line 948
        try:  # line 949
            sos.reorderRenameActions([("123", "312"), ("312", "123")], exitOnConflict=True)  # line 949
            _.fail()  # line 949
        except:  # line 950
            pass  # line 950

    def testMove(_):  # line 952
        sos.offline(options=["--strict", "--track"])  # line 953
        _.createFile(1)  # line 954
        sos.add(".", "./file?")  # line 955
# test source folder missing
        try:  # line 957
            sos.move("sub", "sub/file?", ".", "?file")  # line 957
            _.fail()  # line 957
        except:  # line 958
            pass  # line 958
# test target folder missing: create it
        sos.move(".", "./file?", "sub", "sub/file?")  # line 960
        _.assertTrue(os.path.exists("sub"))  # line 961
        _.assertTrue(os.path.exists("sub/file1"))  # line 962
        _.assertFalse(os.path.exists("file1"))  # line 963
# test move
        sos.move("sub", "sub/file?", ".", "./?file")  # line 965
        _.assertTrue(os.path.exists("1file"))  # line 966
        _.assertFalse(os.path.exists("sub/file1"))  # line 967
# test nothing matches source pattern
        try:  # line 969
            sos.move(".", "a*", ".", "b*")  # line 969
            _.fail()  # line 969
        except:  # line 970
            pass  # line 970
        sos.add(".", "*")  # anything pattern  # line 971
        try:  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 972
            sos.move(".", "a*", ".", "b*")  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 972
            _.fail()  # TODO check that alternative pattern "*" was suggested (1 hit)  # line 972
        except:  # line 973
            pass  # line 973
# test rename no conflict
        _.createFile(1)  # line 975
        _.createFile(2)  # line 976
        _.createFile(3)  # line 977
        sos.add(".", "./file*")  # line 978
        try:  # define an ignore pattern  # line 979
            sos.config(["set", "ignores", "file3;file4"])  # define an ignore pattern  # line 979
        except SystemExit as E:  # line 980
            _.assertEqual(0, E.code)  # line 980
        try:  # line 981
            sos.config(["set", "ignoresWhitelist", "file3"])  # line 981
        except SystemExit as E:  # line 982
            _.assertEqual(0, E.code)  # line 982
        sos.move(".", "./file*", ".", "fi*le")  # line 983
        _.assertTrue(all((os.path.exists("fi%dle" % i) for i in range(1, 4))))  # line 984
        _.assertFalse(os.path.exists("fi4le"))  # line 985
# test rename solvable conflicts
        [_.createFile("%s-%s-%s" % tuple((c for c in n))) for n in ["312", "321", "123", "231"]]  # line 987
#    sos.move("?-?-?")
# test rename unsolvable conflicts
# test --soft option
        sos.remove(".", "./?file")  # was renamed before  # line 991
        sos.add(".", "./?a?b", ["--force"])  # line 992
        sos.move(".", "./?a?b", ".", "./a?b?", ["--force", "--soft"])  # line 993
        _.createFile("1a2b")  # should not be tracked  # line 994
        _.createFile("a1b2")  # should be tracked  # line 995
        sos.commit()  # line 996
        _.assertEqual(2, len(os.listdir(sos.revisionFolder(0, 1))))  # line 997
        _.assertTrue(os.path.exists(sos.revisionFolder(0, 1, file="93b38f90892eb5c57779ca9c0b6fbdf6774daeee3342f56f3e78eb2fe5336c50")))  # a1b2  # line 998
        _.createFile("1a1b1")  # line 999
        _.createFile("1a1b2")  # line 1000
        sos.add(".", "?a?b*")  # line 1001
        _.assertIn("not unique", wrapChannels(lambda: sos.move(".", "?a?b*", ".", "z?z?")))  # should raise error due to same target name  # line 1002
# TODO only rename if actually any files are versioned? or simply what is alife?
# TODO add test if two single question marks will be moved into adjacent characters

    def testHashCollision(_):  # line 1006
        sos.offline()  # line 1007
        _.createFile(1)  # line 1008
        os.mkdir(sos.revisionFolder(0, 1))  # line 1009
        _.createFile("b9ee10a87f612e299a6eb208210bc0898092a64c48091327cc2aaeee9b764ffa", prefix=sos.revisionFolder(0, 1))  # line 1010
        _.createFile(1)  # line 1011
        try:  # should exit with error due to collision detection  # line 1012
            sos.commit()  # should exit with error due to collision detection  # line 1012
            _.fail()  # should exit with error due to collision detection  # line 1012
        except SystemExit as E:  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 1013
            _.assertEqual(1, E.code)  # TODO will capture exit(0) which is wrong, change to check code in all places  # line 1013

    def testFindBase(_):  # line 1015
        old = os.getcwd()  # line 1016
        try:  # line 1017
            os.mkdir("." + os.sep + ".git")  # line 1018
            os.makedirs("." + os.sep + "a" + os.sep + sos.metaFolder)  # line 1019
            os.makedirs("." + os.sep + "a" + os.sep + "b")  # line 1020
            os.chdir("a" + os.sep + "b")  # line 1021
            s, vcs, cmd = sos.findSosVcsBase()  # line 1022
            _.assertIsNotNone(s)  # line 1023
            _.assertIsNotNone(vcs)  # line 1024
            _.assertEqual("git", cmd)  # line 1025
        finally:  # line 1026
            os.chdir(old)  # line 1026

# TODO test command line operation --sos vs. --vcs
# check exact output instead of only expected exception/fail

# TODO test +++ --- in diff
# TODO test +01/-02/*..
# TODO tests for loadcommit redirection
# TODO test wrong branch/revision after fast branching, would raise exception for -1 otherwise

if __name__ == '__main__':  # line 1036
    logging.basicConfig(level=logging.DEBUG if '-v' in sys.argv or "true" in [os.getenv("DEBUG", "false").strip().lower(), os.getenv("CI", "false").strip().lower()] else logging.INFO, stream=sys.stderr, format="%(asctime)-23s %(levelname)-8s %(name)s:%(lineno)d | %(message)s" if '-v' in sys.argv or os.getenv("DEBUG", "false") == "true" else "%(message)s")  # line 1037
    c = configr.Configr("sos")  # line 1038
    c.loadSettings()  # line 1039
    if len(c.keys()) > 0:  # line 1040
        sos.Exit("Cannot run test suite with existing local SOS user configuration (would affect results)")  # line 1040
    unittest.main(testRunner=debugTestRunner() if '-v' in sys.argv and not os.getenv("CI", "false").lower() == "true" else None)  # warnings = "ignore")  # line 1041
