#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xbb337918

# Compiled with Coconut version 1.3.1-post_dev20 [Dead Parrot]

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

# Utiliy functions
import bz2  # early time tracking  # line 5
import codecs  # early time tracking  # line 5
import difflib  # early time tracking  # line 5
import hashlib  # early time tracking  # line 5
import logging  # early time tracking  # line 5
import os  # early time tracking  # line 5
import re  # early time tracking  # line 5
sys = _coconut_sys  # early time tracking  # line 5
import time  # early time tracking  # line 5
START_TIME = time.time()  # early time tracking  # line 5
try:  # line 6
    import enum  # line 6
except:  # line 7
    raise Exception("Please install SOS via 'pip install -U sos-vcs[backport]' to get enum support for Python versions prior 3.4")  # line 7
from typing import Generic  # line 8
from typing import TypeVar  # line 8
Number = TypeVar("Number", int, float)  # line 9
try:  # line 10
    import wcwidth  # line 10
except:  # optional dependency  # line 11
    pass  # optional dependency  # line 11


verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 14

# Classes
class Accessor(dict):  # line 17
    ''' Dictionary with attribute access. Writing only supported via dictionary access. '''  # line 18
    def __init__(_, mapping: 'Dict[str, Any]'):  # line 19
        dict.__init__(_, mapping)  # line 19
    @_coconut_tco  # line 20
    def __getattribute__(_, name: 'str') -> 'Any':  # line 20
        try:  # line 21
            return _[name]  # line 21
        except:  # line 22
            return _coconut_tail_call(dict.__getattribute__, _, name)  # line 22

class Counter(Generic[Number]):  # line 24
    ''' A simple counter. Can be augmented to return the last value instead. '''  # line 25
    def __init__(_, initial: 'Number'=0):  # line 26
        _.value = initial  # type: Number  # line 26
    def inc(_, by: 'Number'=1) -> 'Number':  # line 27
        _.value += by  # line 27
        return _.value  # line 27

class ProgressIndicator(Counter):  # line 29
    ''' Manages a rotating progress indicator. '''  # line 30
    def __init__(_, symbols: 'str', callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None):  # line 31
        super(ProgressIndicator, _).__init__(-1)  # line 31
        _.symbols = symbols  # line 31
        _.timer = time.time()  # type: float  # line 31
        _.callback = callback  # type: Optional[_coconut.typing.Callable[[str], None]]  # line 31
    def getIndicator(_) -> '_coconut.typing.Optional[str]':  # line 32
        ''' Returns a value only if a certain time has passed. '''  # line 33
        newtime = time.time()  # line 34
        if newtime - _.timer < .1:  # line 35
            return None  # line 35
        _.timer = newtime  # line 36
        sign = _.symbols[int(_.inc() % len(_.symbols))]  # type: str  # line 37
        if _.callback:  # line 38
            _.callback(sign)  # line 38
        return sign  # line 39

class Logger:  # line 41
    ''' Logger that supports many items. '''  # line 42
    def __init__(_, log):  # line 43
        _._log = log  # line 43
    def debug(_, *s):  # line 44
        _._log.debug(sjoin(*s))  # line 44
    def info(_, *s):  # line 45
        _._log.info(sjoin(*s))  # line 45
    def warn(_, *s):  # line 46
        _._log.warning(sjoin(*s))  # line 46
    def error(_, *s):  # line 47
        _._log.error(sjoin(*s))  # line 47


# Constants
_log = Logger(logging.getLogger(__name__))  # line 51
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 51
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress", "useChangesCommand", "useUnicodeFont"]  # type: List[str]  # line 52
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # type: List[str]  # line 53
GLOBAL_LISTS = ["ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # type: List[str]  # line 54
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # type: List[str]  # all lower-case normalized  # line 55
FALSE_VALUES = ["false", "no", "off", "0", "disable", "disabled"]  # type: List[str]  # line 56
PROGRESS_MARKER = ["|/-\\", "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588\u2587\u2586\u2585\u2584\u2583\u2582", "\U0001f55b\U0001f550\U0001f551\U0001f552\U0001f553\U0001f554\U0001f555\U0001f556\U0001f557\U0001f558\U0001f559\U0001f55a\U0001f559\U0001f558\U0001f557\U0001f556\U0001f555\U0001f554\U0001f553\U0001f552\U0001f551\U0001f550"]  # type: List[str]  # line 57
BACKUP_SUFFIX = "_last"  # type: str  # line 58
metaFolder = ".sos"  # type: str  # line 59
DUMP_FILE = metaFolder + ".zip"  # type: str  # line 60
metaFile = ".meta"  # type: str  # line 61
metaBack = metaFile + BACKUP_SUFFIX  # type: str  # line 62
MEBI = 1 << 20  # type: int  # line 63
bufSize = MEBI  # type: int  # line 64
UTF8 = "utf_8"  # type: str  # early used constant, not defined in standard library  # line 65
SVN = "svn"  # type: str  # line 66
SLASH = "/"  # type: str  # line 67
DOT_SYMBOL = "\u00b7"  # type: str  # line 68
CROSS_SYMBOL = "\u2714"  # type: str  # line 69
CHECKMARK_SYMBOL = "\u2716"  # type: str  # line 70
PLUSMINUS_SYMBOL = "\u00b1"  # type: str  # line 71
FOLDER_SYMBOL = "\u21cc"  # type: str  # \U0001F5C0"  # HINT second one is very unlikely to be in any console font  # line 72
METADATA_FORMAT = 1  # type: int  # counter for incompatible consecutive formats  # line 73
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": "fossil", "_FOSSIL_": "fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 74
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 75
NL_NAMES = {None: "<No newline>", b"\r\n": "<CR+LF>", b"\n\r": "<LF+CR>", b"\n": "<LF>", b"\r": "<CR>"}  # type: Dict[bytes, str]  # line 76
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": False, "useChangesCommand": False, "useUnicodeFont": sys.platform != "win32", "texttype": ["*.md", "*.coco", "*.py", "*.pyi", "*.pth"], "bintype": [], "ignoreDirs": [".*", "__pycache__", ".mypy_cache"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout", "_FOSSIL_", "*%s" % DUMP_FILE], "ignoresWhitelist": []})  # type: Accessor  # line 77


# Enums
MergeOperation = enum.Enum("MergeOperation", {"INSERT": 1, "REMOVE": 2, "BOTH": 3, "ASK": 4})  # insert remote changes into current, remove remote deletions from current, do both (replicates remote state), or ask per block  # line 89
MergeBlockType = enum.Enum("MergeBlockType", "KEEP INSERT REMOVE REPLACE MOVE")  # modify = intra-line changes, replace = full block replacement  # line 90


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("inSync", 'bool'), ("tracked", 'List[str]'), ("untracked", 'List[str]'), ("parent", '_coconut.typing.Optional[int]'), ("revision", '_coconut.typing.Optional[int]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 94
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 94
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 94
    def __new__(_cls, number, ctime, name=None, inSync=False, tracked=[], untracked=[], parent=None, revision=None):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 94
        return _coconut.tuple.__new__(_cls, (number, ctime, name, inSync, tracked, untracked, parent, revision))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 94
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 95
    __slots__ = ()  # line 95
    __ne__ = _coconut.object.__ne__  # line 95
    def __new__(_cls, number, ctime, message=None):  # line 95
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 95

class PathInfo(_coconut_NamedTuple("PathInfo", [("nameHash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", '_coconut.typing.Optional[str]')])):  # size == None means deleted in this revision  # line 96
    __slots__ = ()  # size == None means deleted in this revision  # line 96
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 96
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]'), ("moves", 'Dict[str, Tuple[str, PathInfo]]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 97
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 97
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 97
class Range(_coconut_NamedTuple("Range", [("tipe", 'MergeBlockType'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 98
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 98
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 98
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'MergeBlockType'), ("lines", 'List[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 99
    __slots__ = ()  # line 99
    __ne__ = _coconut.object.__ne__  # line 99
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 99
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 99

class GlobBlock(_coconut_NamedTuple("GlobBlock", [("isLiteral", 'bool'), ("content", 'str'), ("index", 'int')])):  # for file pattern rename/move matching  # line 100
    __slots__ = ()  # for file pattern rename/move matching  # line 100
    __ne__ = _coconut.object.__ne__  # for file pattern rename/move matching  # line 100
class GlobBlock2(_coconut_NamedTuple("GlobBlock2", [("isLiteral", 'bool'), ("content", 'str'), ("matches", 'str')])):  # matching file pattern and input filename for translation  # line 101
    __slots__ = ()  # matching file pattern and input filename for translation  # line 101
    __ne__ = _coconut.object.__ne__  # matching file pattern and input filename for translation  # line 101
DataType = TypeVar("DataType", BranchInfo, ChangeSet, MergeBlock, PathInfo)  # line 102


# Functions
def printo(s: 'str'="", nl: 'str'="\n"):  # PEP528 compatibility  # line 106
    tryOrDefault(lambda: (lambda _coconut_none_coalesce_item: sys.stdout if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(sys.stdout.buffer), sys.stdout).write((s + nl).encode(sys.stdout.encoding, 'backslashreplace'))  # PEP528 compatibility  # line 106
    sys.stdout.flush()  # PEP528 compatibility  # line 106
def printe(s: 'str'="", nl: 'str'="\n"):  # line 107
    tryOrDefault(lambda: (lambda _coconut_none_coalesce_item: sys.stderr if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(sys.stderr.buffer), sys.stderr).write((s + nl).encode(sys.stderr.encoding, 'backslashreplace'))  # line 107
    sys.stderr.flush()  # line 107
@_coconut_tco  # for py->os access of writing filenames  # PEP 529 compatibility  # line 108
def encode(s: 'str') -> 'bytes':  # for py->os access of writing filenames  # PEP 529 compatibility  # line 108
    return _coconut_tail_call(os.fsencode, s)  # for py->os access of writing filenames  # PEP 529 compatibility  # line 108
@_coconut_tco  # for os->py access of reading filenames  # line 109
def decode(b: 'bytes') -> 'str':  # for os->py access of reading filenames  # line 109
    return _coconut_tail_call(os.fsdecode, b)  # for os->py access of reading filenames  # line 109
try:  # line 110
    import chardet  # https://github.com/chardet/chardet  # line 111
    def detectEncoding(binary: 'bytes') -> 'str':  # line 112
        return chardet.detect(binary)["encoding"]  # line 112
except:  # line 113
    def detectEncoding(binary: 'bytes') -> 'str':  # Guess the encoding  # line 114
        ''' Fallback if chardet library missing. '''  # line 115
        try:  # line 116
            binary.decode(UTF8)  # line 116
            return UTF8  # line 116
        except UnicodeError:  # line 117
            pass  # line 117
        try:  # line 118
            binary.decode("utf_16")  # line 118
            return "utf_16"  # line 118
        except UnicodeError:  # line 119
            pass  # line 119
        try:  # line 120
            binary.decode("cp1252")  # line 120
            return "cp1252"  # line 120
        except UnicodeError:  # line 121
            pass  # line 121
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 122

def tryOrDefault(func: '_coconut.typing.Callable[[], Any]', default: 'Any') -> 'Any':  # line 124
    try:  # line 125
        return func()  # line 125
    except:  # line 126
        return default  # line 126

def tryOrIgnore(func: '_coconut.typing.Callable[[], Any]') -> 'None':  # handle with care!  # line 128
    try:  # line 129
        func()  # line 129
    except:  # line 130
        pass  # line 130

@_coconut_tco  # line 132
def wcswidth(string: 'str') -> 'int':  # line 132
    l = 0  # type: int  # line 133
    try:  # line 134
        l = wcwidth.wcswitdh(string)  # line 135
        return len(string) if l < 0 else l  # line 136
    finally:  # line 137
        return _coconut_tail_call(len, string)  # line 137

def removePath(key: 'str', value: 'str') -> 'str':  # line 139
    ''' Cleanup of user-specified global file patterns. '''  # line 140
    return value if value in GLOBAL_LISTS or SLASH not in value else value[value.rindex(SLASH) + 1:]  # line 141

def conditionalIntersection(a: '_coconut.typing.Optional[FrozenSet[str]]', b: 'FrozenSet[str]') -> 'FrozenSet[str]':  # Used to match only arguments, or use only stored patterns  # line 143
    return a & b if a else b  # Used to match only arguments, or use only stored patterns  # line 143

def dictUpdate(dikt: 'Dict[Any, Any]', by: 'Dict[Any, Any]') -> 'Dict[Any, Any]':  # line 145
    d = {}  # line 145
    d.update(dikt)  # line 145
    d.update(by)  # line 145
    return d  # line 145

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO[bytes]':  # Abstraction for opening both compressed and plain files  # line 147
    return bz2.BZ2File(encode(file), mode) if compress else open(encode(file), mode + "b")  # Abstraction for opening both compressed and plain files  # line 147

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 149
    ''' Determine EOL style from a binary string. '''  # line 150
    lf = file.count(b"\n")  # type: int  # line 151
    cr = file.count(b"\r")  # type: int  # line 152
    crlf = file.count(b"\r\n")  # type: int  # line 153
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 154
        if lf != crlf or cr != crlf:  # line 155
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 155
        return b"\r\n"  # line 156
    if lf != 0 and cr != 0:  # line 157
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 157
    if lf > cr:  # Linux/Unix  # line 158
        return b"\n"  # Linux/Unix  # line 158
    if cr > lf:  # older 8-bit machines  # line 159
        return b"\r"  # older 8-bit machines  # line 159
    return None  # no new line contained, cannot determine  # line 160

try:  # line 162
    Splittable = TypeVar("Splittable", str, bytes)  # line 162
except:  # line 163
    pass  # line 163
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> 'List[Splittable]':  # line 164
    return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 164

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl: 'str'="") -> 'str':  # line 166
    return (sep + (nl + sep).join(seq)) if seq else ""  # line 166

@_coconut_tco  # line 168
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 168
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 168

@_coconut_tco  # line 170
def hashStr(datas: 'str') -> 'str':  # line 170
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 170

def modified(changes: 'ChangeSet', onlyBinary: 'bool'=False) -> 'bool':  # line 172
    return len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0 or len(changes.moves) > 0  # line 172

def listindex(lizt: 'Sequence[Any]', what: 'Any', index: 'int'=0) -> 'int':  # line 174
    return lizt[index:].index(what) + index  # line 174

def getTermWidth() -> 'int':  # line 176
    try:  # line 177
        import termwidth  # line 177
    except:  # line 178
        return 80  # line 178
    return termwidth.getTermWidth()[0]  # line 179

def branchFolder(branch: 'int', base: '_coconut.typing.Optional[str]'=None, file: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 181
    return os.path.join((os.getcwd() if base is None else base), metaFolder, "b%d" % branch) + ((os.sep + file) if file else "")  # line 181

def revisionFolder(branch: 'int', revision: 'int', base: '_coconut.typing.Optional[str]'=None, file: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 183
    return os.path.join(branchFolder(branch, base), "r%d" % revision) + ((os.sep + file) if file else "")  # line 183

def Exit(message: 'str'="", code=1):  # line 185
    printe("[EXIT%s]" % (" %.1fs" % (time.time() - START_TIME) if verbose else "") + (" " + message + "." if message != "" else ""))  # line 185
    sys.exit(code)  # line 185

def exception(E):  # line 187
    ''' Report an exception to the user to enable useful bug reporting. '''  # line 188
    printo(str(E))  # line 189
    import traceback  # line 190
    traceback.print_exc()  # line 191
    traceback.print_stack()  # line 192

def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None, callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None, symbols: 'str'=PROGRESS_MARKER[0]) -> 'Tuple[str, int]':  # line 194
    ''' Calculate hash of file contents, and return compressed sized, if in write mode, or zero. '''  # line 195
    indicator = ProgressIndicator(symbols, callback) if callback else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 196
    _hash = hashlib.sha256()  # line 197
    wsize = 0  # type: int  # line 198
    if saveTo and os.path.exists(encode(saveTo)):  # line 199
        Exit("Hash conflict. Leaving revision in inconsistent state. This should happen only once in a lifetime")  # line 199
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 200
    with open(encode(path), "rb") as fd:  # line 201
        while True:  # line 202
            buffer = fd.read(bufSize)  # type: bytes  # line 203
            _hash.update(buffer)  # line 204
            if to:  # line 205
                to.write(buffer)  # line 205
            if len(buffer) < bufSize:  # line 206
                break  # line 206
            if indicator:  # line 207
                indicator.getIndicator()  # line 207
        if to:  # line 208
            to.close()  # line 209
            wsize = os.stat(encode(saveTo)).st_size  # line 210
    return (_hash.hexdigest(), wsize)  # line 211

def getAnyOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 213
    ''' Utility to find any entries of a dictionary in a list to return the dictionaries value. '''  # line 214
    for k, v in map.items():  # line 215
        if k in params:  # line 216
            return v  # line 216
    return default  # line 217

@_coconut_tco  # line 219
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 219
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 219

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None, ignoreWhitespace: 'bool'=False) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 221
    lines = []  # type: _coconut.typing.Sequence[str]  # line 222
    if filename is not None:  # line 223
        with open(encode(filename), "rb") as fd:  # line 224
            content = fd.read()  # line 224
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detectEncoding(content))  # type: str  # line 225
    eol = eoldet(content)  # type: _coconut.typing.Optional[bytes]  # line 226
    if filename is not None:  # line 227
        with codecs.open(encode(filename), encoding=encoding) as fd2:  # line 228
            lines = safeSplit(fd2.read(), ((b"\n" if eol is None else eol)).decode(encoding))  # line 228
    elif content is not None:  # line 229
        lines = safeSplit(content.decode(encoding), ((b"\n" if eol is None else eol)).decode(encoding))  # line 230
    else:  # line 231
        return (sys.getdefaultencoding(), b"\n", [])  # line 231
    if ignoreWhitespace:  # line 232
        lines[:] = [line.replace("\t", "  ").strip() for line in lines]  # line 232
    return (encoding, eol, lines)  # line 233

@_coconut_tco  # line 235
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, byValue: 'bool'=False, **_kwargs) -> 'DataType':  # line 235
    ''' A better makedata() version. '''  # line 236
    r = _old._asdict()  # type: Dict[str, Any]  # line 237
    r.update({k: ([e for e in v] if byValue and isinstance(v, (list, tuple, set)) else v) for k, v in _kwargs.items()})  # copy by value if required  # line 238
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # TODO also offer copy-by-value here  # line 239

def detectMoves(changes: 'ChangeSet') -> 'Dict[str, PathInfo]':  # line 241
    ''' Compute renames/removes for a changeset. '''  # line 242
    moves = {}  # type: Dict[str, PathInfo]  # line 243
    for path, info in changes.additions.items():  # line 244
        for dpath, dinfo in changes.deletions.items():  # line 245
            if info.size == dinfo.size and info.mtime == dinfo.mtime and info.hash == dinfo.hash:  # was moved TODO check either mtime or hash?  # line 246
                moves[path] = (dpath, info)  # store new data and original name, but don't remove add/del  # line 247
                break  # deletions loop, continue with next addition  # line 248
    return moves  # line 249

def user_block_input(output: 'List[str]'):  # line 251
    sep = input("Enter end-of-text marker (default: <empty line>: ")  # type: str  # line 252
    line = sep  # type: str  # line 252
    while True:  # line 253
        line = input("> ")  # line 254
        if line == sep:  # line 255
            break  # line 255
        output.append(line)  # writes to caller-provided list reference  # line 256

def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation: 'MergeOperation'=MergeOperation.BOTH, charMergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False, eol: 'bool'=False, ignoreWhitespace: 'bool'=False) -> 'Tuple[Union[bytes, List[MergeBlock]], _coconut.typing.Optional[bytes]]':  # line 258
    ''' Merges other binary text contents 'file' (or reads file 'filename') into current text contents 'into' (or reads file 'intoname'), returning merged result.
      For update, the other version is assumed to be the "new/added" one, while for diff, the current changes are the ones "added".
      However, change direction markers are insert ("+") for elements only in into, and remove ("-") for elements only in other file (just like the diff marks +/-)
      diffOnly returns detected change blocks only, no text merging
      eol flag will use the other file's EOL marks
      in case of replace block and INSERT strategy, the change will be added **behind** the original
  '''  # line 273
    encoding = None  # type: str  # line 274
    othr = None  # type: _coconut.typing.Sequence[str]  # line 274
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 274
    curr = None  # type: _coconut.typing.Sequence[str]  # line 274
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 274
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 275
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file, ignoreWhitespace=ignoreWhitespace)  # line 276
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into, ignoreWhitespace=ignoreWhitespace)  # line 277
    except Exception as E:  # line 278
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 278
    if None not in [othreol, curreol] and othreol != curreol:  # line 279
        warn("Differing EOL-styles detected during merge. Using current file's style for merged output")  # line 279
    output = list(difflib.Differ().compare(othr, curr))  # type: List[str]  # from generator expression  # line 280
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 281
    tmp = []  # type: List[str]  # block lines  # line 282
    last = " "  # type: str  # line 283
    no = None  # type: int  # line 283
    line = None  # type: str  # line 283
    for no, line in enumerate(output + ["X"]):  # EOF marker (difflib's output will never be "X" alone)  # line 284
        if line[0] == last:  # continue filling current block, no matter what type of block it is  # line 285
            tmp.append(line[2:])  # continue filling current block, no matter what type of block it is  # line 285
            continue  # continue filling current block, no matter what type of block it is  # line 285
        if line == "X" and len(tmp) == 0:  # break if nothing left to do, otherwise perform operation for stored block  # line 286
            break  # break if nothing left to do, otherwise perform operation for stored block  # line 286
        if last == " ":  # block is same in both files  # line 287
            if len(tmp) > 0:  # avoid adding empty keep block  # line 288
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # avoid adding empty keep block  # line 288
        elif last == "-":  # may be a pure deletion or part of a replacement (with next block being "+")  # line 289
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 290
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.INSERT:  # line 291
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp) - 1, replaces=blocks[-2])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 292
                blocks.pop()  # line 293
        elif last == "+":  # may be insertion or replacement (with previous - block)  # line 294
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # first, assume simple insertion, then check for replacement  # line 295
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.REMOVE:  #  and len(blocks[-1].lines) == len(blocks[-2].lines):  # requires previous block and same number of lines TODO allow multiple intra-line merge for same-length blocks  # line 296
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, line=no - len(tmp) - 1, replaces=blocks[-1])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 297
                blocks.pop()  # remove TOS due to merging two blocks into replace or modify  # line 298
#    elif last == "?": pass # marker for intra-line change comment -> add to block info
        last = line[0]  # line 300
        tmp[:] = [line[2:]]  # only keep current line for next block  # line 301
# TODO add code to detect block moves here
    nl = othreol if eol else ((othreol if curreol is None else curreol))  # type: bytes  # no default newline, to mark "no newline"  # line 303
    debug("Diff blocks: " + repr(blocks))  # line 304
    if diffOnly:  # line 305
        return (blocks, nl)  # line 305

# now perform merge operations depending on detected blocks
    output[:] = []  # clean list of strings  # line 308
    for block in blocks:  # line 309
        if block.tipe == MergeBlockType.KEEP:  # line 310
            output.extend(block.lines)  # line 311
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value) or block.tipe == MergeBlockType.REMOVE and (mergeOperation.value & MergeOperation.INSERT.value):  # line 312
            output.extend(block.lines)  # line 314
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 315
            if len(block.lines) == len(block.replaces.lines) == 1:  # one-liner  # line 316
                output.append(lineMerge(block.lines[0], block.replaces.lines[0], mergeOperation=charMergeOperation))  # line 317
            elif mergeOperation == MergeOperation.ASK:  # more than one line: needs user input  # line 318
                printo(ajoin("- ", block.replaces.lines, nl="\n"))  # TODO check +/- in update mode, could be swapped  # line 319
                printo(ajoin("+ ", block.lines, nl="\n"))  # line 320
                while True:  # line 321
                    op = input(" Line replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 322
                    if op in "tb":  # line 323
                        output.extend(block.lines)  # line 323
                        break  # line 323
                    if op in "ib":  # line 324
                        output.extend(block.replaces.lines)  # line 324
                        break  # line 324
                    if op == "m":  # line 325
                        user_block_input(output)  # line 325
                        break  # line 325
            else:  # more than one line and not ask  # line 326
                if mergeOperation == MergeOperation.REMOVE:  # line 327
                    pass  # line 327
                elif mergeOperation == MergeOperation.BOTH:  # line 328
                    output.extend(block.lines)  # line 328
                elif mergeOperation == MergeOperation.INSERT:  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 329
                    output.extend(list(block.replaces.lines) + list(block.lines))  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 329
#  debug("Merge output: " + "; ".join(output))
    return (((b"\n" if nl is None else nl)).join([line.encode(encoding) for line in output]), nl)  # returning bytes  # line 331
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco  # line 334
def lineMerge(othr: 'str', into: 'str', mergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False) -> 'Union[str, List[MergeBlock]]':  # line 334
    ''' Merges string 'othr' into current string 'into'.
      change direction mark is insert for elements only in into, and remove for elements only in file (according to diff marks +/-)
  '''  # line 337
    out = list(difflib.Differ().compare(othr, into))  # type: List[str]  # line 338
    blocks = []  # type: List[MergeBlock]  # line 339
    for i, line in enumerate(out):  # line 340
        if line[0] == "+":  # line 341
            if i + 1 < len(out) and out[i + 1][0] == "+":  # block will continue  # line 342
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # middle of + block  # line 343
                    blocks[-1].lines.append(line[2])  # add one more character to the accumulating list  # line 344
                else:  # first + in block  # line 345
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 346
            else:  # last line of + block  # line 347
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # end of a block  # line 348
                    blocks[-1].lines.append(line[2])  # line 349
                else:  # single line  # line 350
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 351
                if i >= 1 and blocks[-2].tipe == MergeBlockType.REMOVE:  # previous - and now last in + block creates a replacement block  # line 352
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, i, replaces=blocks[-1])  # line 353
                    blocks.pop()  # line 353
        elif line[0] == "-":  # line 354
            if i > 0 and blocks[-1].tipe == MergeBlockType.REMOVE:  # part of - block  # line 355
                blocks[-1].lines.append(line[2])  # line 356
            else:  # first in block  # line 357
                blocks.append(MergeBlock(MergeBlockType.REMOVE, [line[2]], i))  # line 358
        elif line[0] == " ":  # line 359
            if i > 0 and blocks[-1].tipe == MergeBlockType.KEEP:  # part of block  # line 360
                blocks[-1].lines.append(line[2])  # line 361
            else:  # first in block  # line 362
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line[2]], i))  # line 363
        else:  # line 364
            raise Exception("Cannot parse diff line %r" % line)  # line 364
    blocks[:] = [dataCopy(MergeBlock, block, lines=["".join(block.lines)], replaces=dataCopy(MergeBlock, block.replaces, lines=["".join(block.replaces.lines)]) if block.replaces else None) for block in blocks]  # line 365
    if diffOnly:  # line 366
        return blocks  # line 366
    out[:] = []  # line 367
    for i, block in enumerate(blocks):  # line 368
        if block.tipe == MergeBlockType.KEEP:  # line 369
            out.extend(block.lines)  # line 369
        elif block.tipe == MergeBlockType.REPLACE:  # line 370
            if mergeOperation == MergeOperation.ASK:  # line 371
                printo(ajoin("- ", othr))  # line 372
                printo("- " + (" " * i) + block.replaces.lines[0])  # line 373
                printo("+ " + (" " * i) + block.lines[0])  # line 374
                printo(ajoin("+ ", into))  # line 375
                while True:  # line 376
                    op = input(" Character replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 377
                    if op in "tb":  # line 378
                        out.extend(block.lines)  # line 378
                        break  # line 378
                    if op in "ib":  # line 379
                        out.extend(block.replaces.lines)  # line 379
                        break  # line 379
                    if op == "m":  # line 380
                        user_block_input(out)  # line 380
                        break  # line 380
            else:  # non-interactive  # line 381
                if mergeOperation == MergeOperation.REMOVE:  # line 382
                    pass  # line 382
                elif mergeOperation == MergeOperation.BOTH:  # line 383
                    out.extend(block.lines)  # line 383
                elif mergeOperation == MergeOperation.INSERT:  # line 384
                    out.extend(list(block.replaces.lines) + list(block.lines))  # line 384
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value):  # line 385
            out.extend(block.lines)  # line 385
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation.value & MergeOperation.INSERT.value:  # line 386
            out.extend(block.lines)  # line 386
# TODO ask for insert or remove as well
    return _coconut_tail_call("".join, out)  # line 388

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 390
    ''' Attempts to find sos and legacy VCS base folders.
      Returns (SOS-repo root, VCS-repo root, VCS command)
  '''  # line 393
    debug("Detecting root folders...")  # line 394
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 395
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 396
    while not os.path.exists(encode(os.path.join(path, metaFolder))):  # line 397
        contents = set(os.listdir(path))  # type: Set[str]  # line 398
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 399
        choice = None  # type: _coconut.typing.Optional[str]  # line 400
        if len(vcss) > 1:  # line 401
            choice = SVN if SVN in vcss else vcss[0]  # line 402
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 403
        elif len(vcss) > 0:  # line 404
            choice = vcss[0]  # line 404
        if not vcs[0] and choice:  # memorize current repo root  # line 405
            vcs = (path, choice)  # memorize current repo root  # line 405
        new = os.path.dirname(path)  # get parent path  # line 406
        if new == path:  # avoid infinite loop  # line 407
            break  # avoid infinite loop  # line 407
        path = new  # line 408
    if os.path.exists(encode(os.path.join(path, metaFolder))):  # found something  # line 409
        if vcs[0]:  # already detected vcs base and command  # line 410
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 410
        sos = path  # line 411
        while True:  # continue search for VCS base  # line 412
            new = os.path.dirname(path)  # get parent path  # line 413
            if new == path:  # no VCS folder found  # line 414
                return (sos, None, None)  # no VCS folder found  # line 414
            path = new  # line 415
            contents = set(os.listdir(path))  # line 416
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 417
            choice = None  # line 418
            if len(vcss) > 1:  # line 419
                choice = SVN if SVN in vcss else vcss[0]  # line 420
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 421
            elif len(vcss) > 0:  # line 422
                choice = vcss[0]  # line 422
            if choice:  # line 423
                return (sos, path, choice)  # line 423
    return (None, vcs[0], vcs[1])  # line 424

def tokenizeGlobPattern(pattern: 'str') -> 'List[GlobBlock]':  # line 426
    index = 0  # type: int  # line 427
    out = []  # type: List[GlobBlock]  # literal = True, first index  # line 428
    while index < len(pattern):  # line 429
        if pattern[index:index + 3] in ("[?]", "[*]", "[[]", "[]]"):  # line 430
            out.append(GlobBlock(False, pattern[index:index + 3], index))  # line 430
            continue  # line 430
        if pattern[index] in "*?":  # line 431
            count = 1  # type: int  # line 432
            while index + count < len(pattern) and pattern[index] == "?" and pattern[index + count] == "?":  # line 433
                count += 1  # line 433
            out.append(GlobBlock(False, pattern[index:index + count], index))  # line 434
            index += count  # line 434
            continue  # line 434
        if pattern[index:index + 2] == "[!":  # line 435
            out.append(GlobBlock(False, pattern[index:pattern.index("]", index + 2) + 1], index))  # line 435
            index += len(out[-1][1])  # line 435
            continue  # line 435
        count = 1  # line 436
        while index + count < len(pattern) and pattern[index + count] not in "*?[":  # line 437
            count += 1  # line 437
        out.append(GlobBlock(True, pattern[index:index + count], index))  # line 438
        index += count  # line 438
    return out  # line 439

def tokenizeGlobPatterns(oldPattern: 'str', newPattern: 'str') -> 'Tuple[_coconut.typing.Sequence[GlobBlock], _coconut.typing.Sequence[GlobBlock]]':  # line 441
    ot = tokenizeGlobPattern(oldPattern)  # type: List[GlobBlock]  # line 442
    nt = tokenizeGlobPattern(newPattern)  # type: List[GlobBlock]  # line 443
#  if len(ot) != len(nt): Exit("Source and target patterns can't be translated due to differing number of parsed glob markers and literal strings")
    if len([o for o in ot if not o.isLiteral]) < len([n for n in nt if not n.isLiteral]):  # line 445
        Exit("Source and target file patterns contain differing number of glob markers and can't be translated")  # line 445
    if any((O.content != N.content for O, N in zip([o for o in ot if not o.isLiteral], [n for n in nt if not n.isLiteral]))):  # line 446
        Exit("Source and target file patterns differ in semantics")  # line 446
    return (ot, nt)  # line 447

def convertGlobFiles(filenames: '_coconut.typing.Sequence[str]', oldPattern: '_coconut.typing.Sequence[GlobBlock]', newPattern: '_coconut.typing.Sequence[GlobBlock]') -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 449
    ''' Converts given filename according to specified file patterns. No support for adjacent glob markers currently. '''  # line 450
    pairs = []  # type: List[Tuple[str, str]]  # line 451
    for filename in filenames:  # line 452
        literals = [l for l in oldPattern if l.isLiteral]  # type: List[GlobBlock]  # source literals  # line 453
        nextliteral = 0  # type: int  # line 454
        parsedOld = []  # type: List[GlobBlock2]  # line 455
        index = 0  # type: int  # line 456
        for part in oldPattern:  # match everything in the old filename  # line 457
            if part.isLiteral:  # line 458
                parsedOld.append(GlobBlock2(True, part.content, part.content))  # line 458
                index += len(part.content)  # line 458
                nextliteral += 1  # line 458
            elif part.content.startswith("?"):  # line 459
                parsedOld.append(GlobBlock2(False, part.content, filename[index:index + len(part.content)]))  # line 459
                index += len(part.content)  # line 459
            elif part.content.startswith("["):  # line 460
                parsedOld.append(GlobBlock2(False, part.content, filename[index]))  # line 460
                index += 1  # line 460
            elif part.content == "*":  # line 461
                if nextliteral >= len(literals):  # line 462
                    parsedOld.append(GlobBlock2(False, part.content, filename[index:]))  # line 462
                    break  # line 462
                nxt = filename.index(literals[nextliteral].content, index)  # type: int  # also matches empty string  # line 463
                parsedOld.append(GlobBlock2(False, part.content, filename[index:nxt]))  # line 464
                index = nxt  # line 464
            else:  # line 465
                Exit("Invalid file pattern specified for move/rename")  # line 465
        globs = [g for g in parsedOld if not g.isLiteral]  # type: List[GlobBlock2]  # line 466
        literals = [l for l in newPattern if l.isLiteral]  # target literals  # line 467
        nextliteral = 0  # line 468
        nextglob = 0  # type: int  # line 468
        outname = []  # type: List[str]  # line 469
        for part in newPattern:  # generate new filename  # line 470
            if part.isLiteral:  # line 471
                outname.append(literals[nextliteral].content)  # line 471
                nextliteral += 1  # line 471
            else:  # line 472
                outname.append(globs[nextglob].matches)  # line 472
                nextglob += 1  # line 472
        pairs.append((filename, "".join(outname)))  # line 473
    return pairs  # line 474

@_coconut_tco  # line 476
def reorderRenameActions(actions: '_coconut.typing.Sequence[Tuple[str, str]]', exitOnConflict: 'bool'=True) -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 476
    ''' Attempt to put all rename actions into an order that avoids target == source names.
      Note, that it's currently not really possible to specify patterns that make this work (swapping "*" elements with a reference).
      An alternative would be to always have one (or all) files renamed to a temporary name before renaming to target filename.
  '''  # line 480
    if not actions:  # line 481
        return []  # line 481
    sources = None  # type: List[str]  # line 482
    targets = None  # type: List[str]  # line 482
    sources, targets = [list(l) for l in zip(*actions)]  # line 483
    last = len(actions)  # type: int  # line 484
    while last > 1:  # line 485
        clean = True  # type: bool  # line 486
        for i in range(1, last):  # line 487
            try:  # line 488
                index = targets[:i].index(sources[i])  # type: int  # line 489
                sources.insert(index, sources.pop(i))  # bubble up the action right before conflict  # line 490
                targets.insert(index, targets.pop(i))  # line 491
                clean = False  # line 492
            except:  # target not found in sources: good!  # line 493
                continue  # target not found in sources: good!  # line 493
        if clean:  # line 494
            break  # line 494
        last -= 1  # we know that the last entry in the list has the least conflicts, so we can disregard it in the next iteration  # line 495
    if exitOnConflict:  # line 496
        for i in range(1, len(actions)):  # line 497
            if sources[i] in targets[:i]:  # line 498
                Exit("There is no order of renaming actions that avoids copying over not-yet renamed files: '%s' is contained in matching source filenames" % (targets[i]))  # line 498
    return _coconut_tail_call(list, zip(sources, targets))  # convert to list to avoid generators  # line 499

def relativize(root: 'str', filepath: 'str') -> 'Tuple[str, str]':  # line 501
    ''' Determine OS-independent relative folder path, and relative pattern path. '''  # line 502
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(filepath)), root).replace(os.sep, SLASH)  # line 503
    return relpath, os.path.join(relpath, os.path.basename(filepath)).replace(os.sep, SLASH)  # line 504

def parseOnlyOptions(root: 'str', options: 'List[str]') -> 'Tuple[_coconut.typing.Optional[FrozenSet[str]], _coconut.typing.Optional[FrozenSet[str]]]':  # line 506
    ''' Returns set of --only arguments, and set or --except arguments. '''  # line 507
    cwd = os.getcwd()  # type: str  # line 508
    onlys = []  # type: List[str]  # zero necessary as last start position  # line 509
    excps = []  # type: List[str]  # zero necessary as last start position  # line 509
    index = 0  # type: int  # zero necessary as last start position  # line 509
    while True:  # line 510
        try:  # line 511
            index = 1 + listindex(options, "--only", index)  # line 512
            onlys.append(options[index])  # line 513
            del options[index]  # line 514
            del options[index - 1]  # line 515
        except:  # line 516
            break  # line 516
    index = 0  # line 517
    while True:  # line 518
        try:  # line 519
            index = 1 + listindex(options, "--except", index)  # line 520
            excps.append(options[index])  # line 521
            del options[index]  # line 522
            del options[index - 1]  # line 523
        except:  # line 524
            break  # line 524
    return (frozenset((relativize(root, o)[1] for o in onlys)) if onlys else None, frozenset((relativize(root, e)[1] for e in excps)) if excps else None)  # line 525
