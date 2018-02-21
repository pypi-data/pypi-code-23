#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x85d324fc

# Compiled with Coconut version 1.3.1-post_dev19 [Dead Parrot]

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
    def __init__(_, callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None):  # line 31
        super(ProgressIndicator, _).__init__(-1)  # line 31
        _.timer = time.time()  # type: float  # line 31
        _.callback = callback  # type: Optional[_coconut.typing.Callable[[str], None]]  # line 31
    def getIndicator(_) -> '_coconut.typing.Optional[str]':  # line 32
        ''' Returns a value only if a certain time has passed. '''  # line 33
        newtime = time.time()  # line 34
        if newtime - _.timer < .1:  # line 35
            return None  # line 35
        _.timer = newtime  # line 36
        sign = PROGRESS_MARKER[int(_.inc() % 4)]  # type: str  # line 37
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
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress", "useChangesCommand"]  # type: List[str]  # line 52
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # type: List[str]  # line 53
GLOBAL_LISTS = ["ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # type: List[str]  # line 54
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # type: List[str]  # all lower-case normalized  # line 55
FALSE_VALUES = ["false", "no", "off", "0", "disable", "disabled"]  # type: List[str]  # line 56
PROGRESS_MARKER = ["|", "/", "-", "\\"]  # type: List[str]  # line 57
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
PLUSMINUS_SYMBOL = "\u00b1"  # line 68
FOLDER_SYMBOL = "\U0001F5C0"  # type: str  # line 69
METADATA_FORMAT = 1  # type: int  # counter for incompatible consecutive formats  # line 70
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": "fossil", "_FOSSIL_": "fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 71
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 72
NL_NAMES = {None: "<No newline>", b"\r\n": "<CR+LF>", b"\n\r": "<LF+CR>", b"\n": "<LF>", b"\r": "<CR>"}  # type: Dict[bytes, str]  # line 73
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": False, "useChangesCommand": False, "texttype": ["*.md", "*.coco", "*.py", "*.pyi", "*.pth"], "bintype": [], "ignoreDirs": [".*", "__pycache__", ".mypy_cache"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout", "_FOSSIL_", "*%s" % DUMP_FILE], "ignoresWhitelist": []})  # type: Accessor  # line 74


# Enums
MergeOperation = enum.Enum("MergeOperation", {"INSERT": 1, "REMOVE": 2, "BOTH": 3, "ASK": 4})  # insert remote changes into current, remove remote deletions from current, do both (replicates remote state), or ask per block  # line 86
MergeBlockType = enum.Enum("MergeBlockType", "KEEP INSERT REMOVE REPLACE MOVE")  # modify = intra-line changes, replace = full block replacement  # line 87


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("inSync", 'bool'), ("tracked", 'List[str]'), ("untracked", 'List[str]'), ("parent", '_coconut.typing.Optional[int]'), ("revision", '_coconut.typing.Optional[int]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 91
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 91
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 91
    def __new__(_cls, number, ctime, name=None, inSync=False, tracked=[], untracked=[], parent=None, revision=None):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 91
        return _coconut.tuple.__new__(_cls, (number, ctime, name, inSync, tracked, untracked, parent, revision))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 91
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 92
    __slots__ = ()  # line 92
    __ne__ = _coconut.object.__ne__  # line 92
    def __new__(_cls, number, ctime, message=None):  # line 92
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 92

class PathInfo(_coconut_NamedTuple("PathInfo", [("nameHash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", '_coconut.typing.Optional[str]')])):  # size == None means deleted in this revision  # line 93
    __slots__ = ()  # size == None means deleted in this revision  # line 93
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 93
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]'), ("moves", 'Dict[str, Tuple[str, PathInfo]]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 94
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 94
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 94
class Range(_coconut_NamedTuple("Range", [("tipe", 'MergeBlockType'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 95
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 95
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 95
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'MergeBlockType'), ("lines", 'List[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 96
    __slots__ = ()  # line 96
    __ne__ = _coconut.object.__ne__  # line 96
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 96
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 96

class GlobBlock(_coconut_NamedTuple("GlobBlock", [("isLiteral", 'bool'), ("content", 'str'), ("index", 'int')])):  # for file pattern rename/move matching  # line 97
    __slots__ = ()  # for file pattern rename/move matching  # line 97
    __ne__ = _coconut.object.__ne__  # for file pattern rename/move matching  # line 97
class GlobBlock2(_coconut_NamedTuple("GlobBlock2", [("isLiteral", 'bool'), ("content", 'str'), ("matches", 'str')])):  # matching file pattern and input filename for translation  # line 98
    __slots__ = ()  # matching file pattern and input filename for translation  # line 98
    __ne__ = _coconut.object.__ne__  # matching file pattern and input filename for translation  # line 98
DataType = TypeVar("DataType", BranchInfo, ChangeSet, MergeBlock, PathInfo)  # line 99


# Functions
def printo(s: 'str'="", nl: 'str'="\n"):  # PEP528 compatibility  # line 103
    sys.stdout.buffer.write((s + nl).encode(sys.stdout.encoding, 'backslashreplace'))  # PEP528 compatibility  # line 103
    sys.stdout.flush()  # PEP528 compatibility  # line 103
def printe(s: 'str'="", nl: 'str'="\n"):  # line 104
    sys.stderr.buffer.write((s + nl).encode(sys.stderr.encoding, 'backslashreplace'))  # line 104
    sys.stderr.flush()  # line 104
@_coconut_tco  # for py->os access of writing filenames  # PEP 529 compatibility  # line 105
def encode(s: 'str') -> 'bytes':  # for py->os access of writing filenames  # PEP 529 compatibility  # line 105
    return _coconut_tail_call(os.fsencode, s)  # for py->os access of writing filenames  # PEP 529 compatibility  # line 105
@_coconut_tco  # for os->py access of reading filenames  # line 106
def decode(b: 'bytes') -> 'str':  # for os->py access of reading filenames  # line 106
    return _coconut_tail_call(os.fsdecode, b)  # for os->py access of reading filenames  # line 106
try:  # line 107
    import chardet  # https://github.com/chardet/chardet  # line 108
    def detectEncoding(binary: 'bytes') -> 'str':  # line 109
        return chardet.detect(binary)["encoding"]  # line 109
except:  # line 110
    def detectEncoding(binary: 'bytes') -> 'str':  # Guess the encoding  # line 111
        ''' Fallback if chardet library missing. '''  # line 112
        try:  # line 113
            binary.decode(UTF8)  # line 113
            return UTF8  # line 113
        except UnicodeError:  # line 114
            pass  # line 114
        try:  # line 115
            binary.decode("utf_16")  # line 115
            return "utf_16"  # line 115
        except UnicodeError:  # line 116
            pass  # line 116
        try:  # line 117
            binary.decode("cp1252")  # line 117
            return "cp1252"  # line 117
        except UnicodeError:  # line 118
            pass  # line 118
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 119

def tryOrDefault(func: '_coconut.typing.Callable[[], Any]', default: 'Any') -> 'Any':  # line 121
    try:  # line 122
        return func()  # line 122
    except:  # line 123
        return default  # line 123

def tryOrIgnore(func: '_coconut.typing.Callable[[], Any]') -> 'None':  # handle with care!  # line 125
    try:  # line 126
        func()  # line 126
    except:  # line 127
        pass  # line 127

@_coconut_tco  # line 129
def wcswidth(string: 'str') -> 'int':  # line 129
    l = 0  # type: int  # line 130
    try:  # line 131
        l = wcwidth.wcswitdh(string)  # line 132
        return len(string) if l < 0 else l  # line 133
    finally:  # line 134
        return _coconut_tail_call(len, string)  # line 134

def removePath(key: 'str', value: 'str') -> 'str':  # line 136
    ''' Cleanup of user-specified global file patterns. '''  # line 137
    return value if value in GLOBAL_LISTS or SLASH not in value else value[value.rindex(SLASH) + 1:]  # line 138

def conditionalIntersection(a: '_coconut.typing.Optional[FrozenSet[str]]', b: 'FrozenSet[str]') -> 'FrozenSet[str]':  # Used to match only arguments, or use only stored patterns  # line 140
    return a & b if a else b  # Used to match only arguments, or use only stored patterns  # line 140

def dictUpdate(dikt: 'Dict[Any, Any]', by: 'Dict[Any, Any]') -> 'Dict[Any, Any]':  # line 142
    d = {}  # line 142
    d.update(dikt)  # line 142
    d.update(by)  # line 142
    return d  # line 142

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO[bytes]':  # Abstraction for opening both compressed and plain files  # line 144
    return bz2.BZ2File(encode(file), mode) if compress else open(encode(file), mode + "b")  # Abstraction for opening both compressed and plain files  # line 144

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 146
    ''' Determine EOL style from a binary string. '''  # line 147
    lf = file.count(b"\n")  # type: int  # line 148
    cr = file.count(b"\r")  # type: int  # line 149
    crlf = file.count(b"\r\n")  # type: int  # line 150
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 151
        if lf != crlf or cr != crlf:  # line 152
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 152
        return b"\r\n"  # line 153
    if lf != 0 and cr != 0:  # line 154
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 154
    if lf > cr:  # Linux/Unix  # line 155
        return b"\n"  # Linux/Unix  # line 155
    if cr > lf:  # older 8-bit machines  # line 156
        return b"\r"  # older 8-bit machines  # line 156
    return None  # no new line contained, cannot determine  # line 157

try:  # line 159
    Splittable = TypeVar("Splittable", str, bytes)  # line 159
except:  # line 160
    pass  # line 160
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> 'List[Splittable]':  # line 161
    return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 161

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl: 'str'="") -> 'str':  # line 163
    return (sep + (nl + sep).join(seq)) if seq else ""  # line 163

@_coconut_tco  # line 165
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 165
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 165

@_coconut_tco  # line 167
def hashStr(datas: 'str') -> 'str':  # line 167
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 167

def modified(changes: 'ChangeSet', onlyBinary: 'bool'=False) -> 'bool':  # line 169
    return len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0 or len(changes.moves) > 0  # line 169

def listindex(lizt: 'Sequence[Any]', what: 'Any', index: 'int'=0) -> 'int':  # line 171
    return lizt[index:].index(what) + index  # line 171

def getTermWidth() -> 'int':  # line 173
    try:  # line 174
        import termwidth  # line 174
    except:  # line 175
        return 80  # line 175
    return termwidth.getTermWidth()[0]  # line 176

def branchFolder(branch: 'int', base: '_coconut.typing.Optional[str]'=None, file: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 178
    return os.path.join((os.getcwd() if base is None else base), metaFolder, "b%d" % branch) + ((os.sep + file) if file else "")  # line 178

def revisionFolder(branch: 'int', revision: 'int', base: '_coconut.typing.Optional[str]'=None, file: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 180
    return os.path.join(branchFolder(branch, base), "r%d" % revision) + ((os.sep + file) if file else "")  # line 180

def Exit(message: 'str'="", code=1):  # line 182
    printe("[EXIT%s]" % (" %.1fs" % (time.time() - START_TIME) if verbose else "") + (" " + message + "." if message != "" else ""))  # line 182
    sys.exit(code)  # line 182

def exception(E):  # line 184
    ''' Report an exception to the user to enable useful bug reporting. '''  # line 185
    printo(str(E))  # line 186
    import traceback  # line 187
    traceback.print_exc()  # line 188
    traceback.print_stack()  # line 189

def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None, callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None) -> 'Tuple[str, int]':  # line 191
    ''' Calculate hash of file contents, and return compressed sized, if in write mode, or zero. '''  # line 192
    indicator = ProgressIndicator(callback) if callback else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 193
    _hash = hashlib.sha256()  # line 194
    wsize = 0  # type: int  # line 195
    if saveTo and os.path.exists(encode(saveTo)):  # line 196
        Exit("Hash conflict. Leaving revision in inconsistent state. This should happen only once in a lifetime")  # line 196
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 197
    with open(encode(path), "rb") as fd:  # line 198
        while True:  # line 199
            buffer = fd.read(bufSize)  # type: bytes  # line 200
            _hash.update(buffer)  # line 201
            if to:  # line 202
                to.write(buffer)  # line 202
            if len(buffer) < bufSize:  # line 203
                break  # line 203
            if indicator:  # line 204
                indicator.getIndicator()  # line 204
        if to:  # line 205
            to.close()  # line 206
            wsize = os.stat(encode(saveTo)).st_size  # line 207
    return (_hash.hexdigest(), wsize)  # line 208

def getAnyOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 210
    ''' Utility to find any entries of a dictionary in a list to return the dictionaries value. '''  # line 211
    for k, v in map.items():  # line 212
        if k in params:  # line 213
            return v  # line 213
    return default  # line 214

@_coconut_tco  # line 216
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 216
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 216

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None, ignoreWhitespace: 'bool'=False) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 218
    lines = []  # type: _coconut.typing.Sequence[str]  # line 219
    if filename is not None:  # line 220
        with open(encode(filename), "rb") as fd:  # line 221
            content = fd.read()  # line 221
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detectEncoding(content))  # type: str  # line 222
    eol = eoldet(content)  # type: _coconut.typing.Optional[bytes]  # line 223
    if filename is not None:  # line 224
        with codecs.open(encode(filename), encoding=encoding) as fd2:  # line 225
            lines = safeSplit(fd2.read(), ((b"\n" if eol is None else eol)).decode(encoding))  # line 225
    elif content is not None:  # line 226
        lines = safeSplit(content.decode(encoding), ((b"\n" if eol is None else eol)).decode(encoding))  # line 227
    else:  # line 228
        return (sys.getdefaultencoding(), b"\n", [])  # line 228
    if ignoreWhitespace:  # line 229
        lines[:] = [line.replace("\t", "  ").strip() for line in lines]  # line 229
    return (encoding, eol, lines)  # line 230

@_coconut_tco  # line 232
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, byValue: 'bool'=False, **_kwargs) -> 'DataType':  # line 232
    ''' A better makedata() version. '''  # line 233
    r = _old._asdict()  # type: Dict[str, Any]  # line 234
    r.update({k: ([e for e in v] if byValue and isinstance(v, (list, tuple, set)) else v) for k, v in _kwargs.items()})  # copy by value if required  # line 235
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # TODO also offer copy-by-value here  # line 236

def detectMoves(changes: 'ChangeSet') -> 'Dict[str, PathInfo]':  # line 238
    ''' Compute renames/removes for a changeset. '''  # line 239
    moves = {}  # type: Dict[str, PathInfo]  # line 240
    for path, info in changes.additions.items():  # line 241
        for dpath, dinfo in changes.deletions.items():  # line 242
            if info.size == dinfo.size and info.mtime == dinfo.mtime and info.hash == dinfo.hash:  # was moved TODO check either mtime or hash?  # line 243
                moves[path] = (dpath, info)  # store new data and original name, but don't remove add/del  # line 244
                break  # deletions loop, continue with next addition  # line 245
    return moves  # line 246

def user_block_input(output: 'List[str]'):  # line 248
    sep = input("Enter end-of-text marker (default: <empty line>: ")  # type: str  # line 249
    line = sep  # type: str  # line 249
    while True:  # line 250
        line = input("> ")  # line 251
        if line == sep:  # line 252
            break  # line 252
        output.append(line)  # writes to caller-provided list reference  # line 253

def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation: 'MergeOperation'=MergeOperation.BOTH, charMergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False, eol: 'bool'=False, ignoreWhitespace: 'bool'=False) -> 'Tuple[Union[bytes, List[MergeBlock]], _coconut.typing.Optional[bytes]]':  # line 255
    ''' Merges other binary text contents 'file' (or reads file 'filename') into current text contents 'into' (or reads file 'intoname'), returning merged result.
      For update, the other version is assumed to be the "new/added" one, while for diff, the current changes are the ones "added".
      However, change direction markers are insert ("+") for elements only in into, and remove ("-") for elements only in other file (just like the diff marks +/-)
      diffOnly returns detected change blocks only, no text merging
      eol flag will use the other file's EOL marks
      in case of replace block and INSERT strategy, the change will be added **behind** the original
  '''  # line 270
    encoding = None  # type: str  # line 271
    othr = None  # type: _coconut.typing.Sequence[str]  # line 271
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 271
    curr = None  # type: _coconut.typing.Sequence[str]  # line 271
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 271
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 272
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file, ignoreWhitespace=ignoreWhitespace)  # line 273
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into, ignoreWhitespace=ignoreWhitespace)  # line 274
    except Exception as E:  # line 275
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 275
    if None not in [othreol, curreol] and othreol != curreol:  # line 276
        warn("Differing EOL-styles detected during merge. Using current file's style for merged output")  # line 276
    output = list(difflib.Differ().compare(othr, curr))  # type: List[str]  # from generator expression  # line 277
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 278
    tmp = []  # type: List[str]  # block lines  # line 279
    last = " "  # type: str  # line 280
    no = None  # type: int  # line 280
    line = None  # type: str  # line 280
    for no, line in enumerate(output + ["X"]):  # EOF marker (difflib's output will never be "X" alone)  # line 281
        if line[0] == last:  # continue filling current block, no matter what type of block it is  # line 282
            tmp.append(line[2:])  # continue filling current block, no matter what type of block it is  # line 282
            continue  # continue filling current block, no matter what type of block it is  # line 282
        if line == "X" and len(tmp) == 0:  # break if nothing left to do, otherwise perform operation for stored block  # line 283
            break  # break if nothing left to do, otherwise perform operation for stored block  # line 283
        if last == " ":  # block is same in both files  # line 284
            if len(tmp) > 0:  # avoid adding empty keep block  # line 285
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # avoid adding empty keep block  # line 285
        elif last == "-":  # may be a pure deletion or part of a replacement (with next block being "+")  # line 286
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 287
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.INSERT:  # line 288
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp) - 1, replaces=blocks[-2])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 289
                blocks.pop()  # line 290
        elif last == "+":  # may be insertion or replacement (with previous - block)  # line 291
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # first, assume simple insertion, then check for replacement  # line 292
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.REMOVE:  #  and len(blocks[-1].lines) == len(blocks[-2].lines):  # requires previous block and same number of lines TODO allow multiple intra-line merge for same-length blocks  # line 293
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, line=no - len(tmp) - 1, replaces=blocks[-1])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 294
                blocks.pop()  # remove TOS due to merging two blocks into replace or modify  # line 295
#    elif last == "?": pass # marker for intra-line change comment -> add to block info
        last = line[0]  # line 297
        tmp[:] = [line[2:]]  # only keep current line for next block  # line 298
# TODO add code to detect block moves here
    nl = othreol if eol else ((othreol if curreol is None else curreol))  # type: bytes  # no default newline, to mark "no newline"  # line 300
    debug("Diff blocks: " + repr(blocks))  # line 301
    if diffOnly:  # line 302
        return (blocks, nl)  # line 302

# now perform merge operations depending on detected blocks
    output[:] = []  # clean list of strings  # line 305
    for block in blocks:  # line 306
        if block.tipe == MergeBlockType.KEEP:  # line 307
            output.extend(block.lines)  # line 308
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value) or block.tipe == MergeBlockType.REMOVE and (mergeOperation.value & MergeOperation.INSERT.value):  # line 309
            output.extend(block.lines)  # line 311
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 312
            if len(block.lines) == len(block.replaces.lines) == 1:  # one-liner  # line 313
                output.append(lineMerge(block.lines[0], block.replaces.lines[0], mergeOperation=charMergeOperation))  # line 314
            elif mergeOperation == MergeOperation.ASK:  # more than one line: needs user input  # line 315
                printo(ajoin("- ", block.replaces.lines, nl="\n"))  # TODO check +/- in update mode, could be swapped  # line 316
                printo(ajoin("+ ", block.lines, nl="\n"))  # line 317
                while True:  # line 318
                    op = input(" Line replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 319
                    if op in "tb":  # line 320
                        output.extend(block.lines)  # line 320
                        break  # line 320
                    if op in "ib":  # line 321
                        output.extend(block.replaces.lines)  # line 321
                        break  # line 321
                    if op == "m":  # line 322
                        user_block_input(output)  # line 322
                        break  # line 322
            else:  # more than one line and not ask  # line 323
                if mergeOperation == MergeOperation.REMOVE:  # line 324
                    pass  # line 324
                elif mergeOperation == MergeOperation.BOTH:  # line 325
                    output.extend(block.lines)  # line 325
                elif mergeOperation == MergeOperation.INSERT:  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 326
                    output.extend(list(block.replaces.lines) + list(block.lines))  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 326
#  debug("Merge output: " + "; ".join(output))
    return (((b"\n" if nl is None else nl)).join([line.encode(encoding) for line in output]), nl)  # returning bytes  # line 328
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco  # line 331
def lineMerge(othr: 'str', into: 'str', mergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False) -> 'Union[str, List[MergeBlock]]':  # line 331
    ''' Merges string 'othr' into current string 'into'.
      change direction mark is insert for elements only in into, and remove for elements only in file (according to diff marks +/-)
  '''  # line 334
    out = list(difflib.Differ().compare(othr, into))  # type: List[str]  # line 335
    blocks = []  # type: List[MergeBlock]  # line 336
    for i, line in enumerate(out):  # line 337
        if line[0] == "+":  # line 338
            if i + 1 < len(out) and out[i + 1][0] == "+":  # block will continue  # line 339
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # middle of + block  # line 340
                    blocks[-1].lines.append(line[2])  # add one more character to the accumulating list  # line 341
                else:  # first + in block  # line 342
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 343
            else:  # last line of + block  # line 344
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # end of a block  # line 345
                    blocks[-1].lines.append(line[2])  # line 346
                else:  # single line  # line 347
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 348
                if i >= 1 and blocks[-2].tipe == MergeBlockType.REMOVE:  # previous - and now last in + block creates a replacement block  # line 349
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, i, replaces=blocks[-1])  # line 350
                    blocks.pop()  # line 350
        elif line[0] == "-":  # line 351
            if i > 0 and blocks[-1].tipe == MergeBlockType.REMOVE:  # part of - block  # line 352
                blocks[-1].lines.append(line[2])  # line 353
            else:  # first in block  # line 354
                blocks.append(MergeBlock(MergeBlockType.REMOVE, [line[2]], i))  # line 355
        elif line[0] == " ":  # line 356
            if i > 0 and blocks[-1].tipe == MergeBlockType.KEEP:  # part of block  # line 357
                blocks[-1].lines.append(line[2])  # line 358
            else:  # first in block  # line 359
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line[2]], i))  # line 360
        else:  # line 361
            raise Exception("Cannot parse diff line %r" % line)  # line 361
    blocks[:] = [dataCopy(MergeBlock, block, lines=["".join(block.lines)], replaces=dataCopy(MergeBlock, block.replaces, lines=["".join(block.replaces.lines)]) if block.replaces else None) for block in blocks]  # line 362
    if diffOnly:  # line 363
        return blocks  # line 363
    out[:] = []  # line 364
    for i, block in enumerate(blocks):  # line 365
        if block.tipe == MergeBlockType.KEEP:  # line 366
            out.extend(block.lines)  # line 366
        elif block.tipe == MergeBlockType.REPLACE:  # line 367
            if mergeOperation == MergeOperation.ASK:  # line 368
                printo(ajoin("- ", othr))  # line 369
                printo("- " + (" " * i) + block.replaces.lines[0])  # line 370
                printo("+ " + (" " * i) + block.lines[0])  # line 371
                printo(ajoin("+ ", into))  # line 372
                while True:  # line 373
                    op = input(" Character replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 374
                    if op in "tb":  # line 375
                        out.extend(block.lines)  # line 375
                        break  # line 375
                    if op in "ib":  # line 376
                        out.extend(block.replaces.lines)  # line 376
                        break  # line 376
                    if op == "m":  # line 377
                        user_block_input(out)  # line 377
                        break  # line 377
            else:  # non-interactive  # line 378
                if mergeOperation == MergeOperation.REMOVE:  # line 379
                    pass  # line 379
                elif mergeOperation == MergeOperation.BOTH:  # line 380
                    out.extend(block.lines)  # line 380
                elif mergeOperation == MergeOperation.INSERT:  # line 381
                    out.extend(list(block.replaces.lines) + list(block.lines))  # line 381
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value):  # line 382
            out.extend(block.lines)  # line 382
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation.value & MergeOperation.INSERT.value:  # line 383
            out.extend(block.lines)  # line 383
# TODO ask for insert or remove as well
    return _coconut_tail_call("".join, out)  # line 385

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 387
    ''' Attempts to find sos and legacy VCS base folders.
      Returns (SOS-repo root, VCS-repo root, VCS command)
  '''  # line 390
    debug("Detecting root folders...")  # line 391
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 392
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 393
    while not os.path.exists(encode(os.path.join(path, metaFolder))):  # line 394
        contents = set(os.listdir(path))  # type: Set[str]  # line 395
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 396
        choice = None  # type: _coconut.typing.Optional[str]  # line 397
        if len(vcss) > 1:  # line 398
            choice = SVN if SVN in vcss else vcss[0]  # line 399
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 400
        elif len(vcss) > 0:  # line 401
            choice = vcss[0]  # line 401
        if not vcs[0] and choice:  # memorize current repo root  # line 402
            vcs = (path, choice)  # memorize current repo root  # line 402
        new = os.path.dirname(path)  # get parent path  # line 403
        if new == path:  # avoid infinite loop  # line 404
            break  # avoid infinite loop  # line 404
        path = new  # line 405
    if os.path.exists(encode(os.path.join(path, metaFolder))):  # found something  # line 406
        if vcs[0]:  # already detected vcs base and command  # line 407
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 407
        sos = path  # line 408
        while True:  # continue search for VCS base  # line 409
            new = os.path.dirname(path)  # get parent path  # line 410
            if new == path:  # no VCS folder found  # line 411
                return (sos, None, None)  # no VCS folder found  # line 411
            path = new  # line 412
            contents = set(os.listdir(path))  # line 413
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 414
            choice = None  # line 415
            if len(vcss) > 1:  # line 416
                choice = SVN if SVN in vcss else vcss[0]  # line 417
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 418
            elif len(vcss) > 0:  # line 419
                choice = vcss[0]  # line 419
            if choice:  # line 420
                return (sos, path, choice)  # line 420
    return (None, vcs[0], vcs[1])  # line 421

def tokenizeGlobPattern(pattern: 'str') -> 'List[GlobBlock]':  # line 423
    index = 0  # type: int  # line 424
    out = []  # type: List[GlobBlock]  # literal = True, first index  # line 425
    while index < len(pattern):  # line 426
        if pattern[index:index + 3] in ("[?]", "[*]", "[[]", "[]]"):  # line 427
            out.append(GlobBlock(False, pattern[index:index + 3], index))  # line 427
            continue  # line 427
        if pattern[index] in "*?":  # line 428
            count = 1  # type: int  # line 429
            while index + count < len(pattern) and pattern[index] == "?" and pattern[index + count] == "?":  # line 430
                count += 1  # line 430
            out.append(GlobBlock(False, pattern[index:index + count], index))  # line 431
            index += count  # line 431
            continue  # line 431
        if pattern[index:index + 2] == "[!":  # line 432
            out.append(GlobBlock(False, pattern[index:pattern.index("]", index + 2) + 1], index))  # line 432
            index += len(out[-1][1])  # line 432
            continue  # line 432
        count = 1  # line 433
        while index + count < len(pattern) and pattern[index + count] not in "*?[":  # line 434
            count += 1  # line 434
        out.append(GlobBlock(True, pattern[index:index + count], index))  # line 435
        index += count  # line 435
    return out  # line 436

def tokenizeGlobPatterns(oldPattern: 'str', newPattern: 'str') -> 'Tuple[_coconut.typing.Sequence[GlobBlock], _coconut.typing.Sequence[GlobBlock]]':  # line 438
    ot = tokenizeGlobPattern(oldPattern)  # type: List[GlobBlock]  # line 439
    nt = tokenizeGlobPattern(newPattern)  # type: List[GlobBlock]  # line 440
#  if len(ot) != len(nt): Exit("Source and target patterns can't be translated due to differing number of parsed glob markers and literal strings")
    if len([o for o in ot if not o.isLiteral]) < len([n for n in nt if not n.isLiteral]):  # line 442
        Exit("Source and target file patterns contain differing number of glob markers and can't be translated")  # line 442
    if any((O.content != N.content for O, N in zip([o for o in ot if not o.isLiteral], [n for n in nt if not n.isLiteral]))):  # line 443
        Exit("Source and target file patterns differ in semantics")  # line 443
    return (ot, nt)  # line 444

def convertGlobFiles(filenames: '_coconut.typing.Sequence[str]', oldPattern: '_coconut.typing.Sequence[GlobBlock]', newPattern: '_coconut.typing.Sequence[GlobBlock]') -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 446
    ''' Converts given filename according to specified file patterns. No support for adjacent glob markers currently. '''  # line 447
    pairs = []  # type: List[Tuple[str, str]]  # line 448
    for filename in filenames:  # line 449
        literals = [l for l in oldPattern if l.isLiteral]  # type: List[GlobBlock]  # source literals  # line 450
        nextliteral = 0  # type: int  # line 451
        parsedOld = []  # type: List[GlobBlock2]  # line 452
        index = 0  # type: int  # line 453
        for part in oldPattern:  # match everything in the old filename  # line 454
            if part.isLiteral:  # line 455
                parsedOld.append(GlobBlock2(True, part.content, part.content))  # line 455
                index += len(part.content)  # line 455
                nextliteral += 1  # line 455
            elif part.content.startswith("?"):  # line 456
                parsedOld.append(GlobBlock2(False, part.content, filename[index:index + len(part.content)]))  # line 456
                index += len(part.content)  # line 456
            elif part.content.startswith("["):  # line 457
                parsedOld.append(GlobBlock2(False, part.content, filename[index]))  # line 457
                index += 1  # line 457
            elif part.content == "*":  # line 458
                if nextliteral >= len(literals):  # line 459
                    parsedOld.append(GlobBlock2(False, part.content, filename[index:]))  # line 459
                    break  # line 459
                nxt = filename.index(literals[nextliteral].content, index)  # type: int  # also matches empty string  # line 460
                parsedOld.append(GlobBlock2(False, part.content, filename[index:nxt]))  # line 461
                index = nxt  # line 461
            else:  # line 462
                Exit("Invalid file pattern specified for move/rename")  # line 462
        globs = [g for g in parsedOld if not g.isLiteral]  # type: List[GlobBlock2]  # line 463
        literals = [l for l in newPattern if l.isLiteral]  # target literals  # line 464
        nextliteral = 0  # line 465
        nextglob = 0  # type: int  # line 465
        outname = []  # type: List[str]  # line 466
        for part in newPattern:  # generate new filename  # line 467
            if part.isLiteral:  # line 468
                outname.append(literals[nextliteral].content)  # line 468
                nextliteral += 1  # line 468
            else:  # line 469
                outname.append(globs[nextglob].matches)  # line 469
                nextglob += 1  # line 469
        pairs.append((filename, "".join(outname)))  # line 470
    return pairs  # line 471

@_coconut_tco  # line 473
def reorderRenameActions(actions: '_coconut.typing.Sequence[Tuple[str, str]]', exitOnConflict: 'bool'=True) -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 473
    ''' Attempt to put all rename actions into an order that avoids target == source names.
      Note, that it's currently not really possible to specify patterns that make this work (swapping "*" elements with a reference).
      An alternative would be to always have one (or all) files renamed to a temporary name before renaming to target filename.
  '''  # line 477
    if not actions:  # line 478
        return []  # line 478
    sources = None  # type: List[str]  # line 479
    targets = None  # type: List[str]  # line 479
    sources, targets = [list(l) for l in zip(*actions)]  # line 480
    last = len(actions)  # type: int  # line 481
    while last > 1:  # line 482
        clean = True  # type: bool  # line 483
        for i in range(1, last):  # line 484
            try:  # line 485
                index = targets[:i].index(sources[i])  # type: int  # line 486
                sources.insert(index, sources.pop(i))  # bubble up the action right before conflict  # line 487
                targets.insert(index, targets.pop(i))  # line 488
                clean = False  # line 489
            except:  # target not found in sources: good!  # line 490
                continue  # target not found in sources: good!  # line 490
        if clean:  # line 491
            break  # line 491
        last -= 1  # we know that the last entry in the list has the least conflicts, so we can disregard it in the next iteration  # line 492
    if exitOnConflict:  # line 493
        for i in range(1, len(actions)):  # line 494
            if sources[i] in targets[:i]:  # line 495
                Exit("There is no order of renaming actions that avoids copying over not-yet renamed files: '%s' is contained in matching source filenames" % (targets[i]))  # line 495
    return _coconut_tail_call(list, zip(sources, targets))  # convert to list to avoid generators  # line 496

def relativize(root: 'str', filepath: 'str') -> 'Tuple[str, str]':  # line 498
    ''' Determine OS-independent relative folder path, and relative pattern path. '''  # line 499
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(filepath)), root).replace(os.sep, SLASH)  # line 500
    return relpath, os.path.join(relpath, os.path.basename(filepath)).replace(os.sep, SLASH)  # line 501

def parseOnlyOptions(root: 'str', options: 'List[str]') -> 'Tuple[_coconut.typing.Optional[FrozenSet[str]], _coconut.typing.Optional[FrozenSet[str]]]':  # line 503
    ''' Returns set of --only arguments, and set or --except arguments. '''  # line 504
    cwd = os.getcwd()  # type: str  # line 505
    onlys = []  # type: List[str]  # zero necessary as last start position  # line 506
    excps = []  # type: List[str]  # zero necessary as last start position  # line 506
    index = 0  # type: int  # zero necessary as last start position  # line 506
    while True:  # line 507
        try:  # line 508
            index = 1 + listindex(options, "--only", index)  # line 509
            onlys.append(options[index])  # line 510
            del options[index]  # line 511
            del options[index - 1]  # line 512
        except:  # line 513
            break  # line 513
    index = 0  # line 514
    while True:  # line 515
        try:  # line 516
            index = 1 + listindex(options, "--except", index)  # line 517
            excps.append(options[index])  # line 518
            del options[index]  # line 519
            del options[index - 1]  # line 520
        except:  # line 521
            break  # line 521
    return (frozenset((relativize(root, o)[1] for o in onlys)) if onlys else None, frozenset((relativize(root, e)[1] for e in excps)) if excps else None)  # line 522
