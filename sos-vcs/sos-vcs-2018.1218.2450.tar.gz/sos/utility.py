#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x27964731

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

# Utiliy functions
import bz2  # line 5
import codecs  # line 5
import difflib  # line 5
import hashlib  # line 5
import logging  # line 5
import os  # line 5
import re  # line 5
sys = _coconut_sys  # line 5
import time  # line 5
START_TIME = time.time()  # line 5
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
METADATA_FORMAT = 1  # type: int  # counter for incompatible consecutive formats  # line 68
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": "fossil", "_FOSSIL_": "fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 69
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 70
NL_NAMES = {None: "<No newline>", b"\r\n": "<CR+LF>", b"\n\r": "<LF+CR>", b"\n": "<LF>", b"\r": "<CR>"}  # type: Dict[bytes, str]  # line 71
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": False, "useChangesCommand": False, "texttype": ["*.md", "*.coco", "*.py", "*.pyi", "*.pth"], "bintype": [], "ignoreDirs": [".*", "__pycache__", ".mypy_cache"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout", "_FOSSIL_", "*%s" % DUMP_FILE], "ignoresWhitelist": []})  # type: Accessor  # line 72


# Enums
MergeOperation = enum.Enum("MergeOperation", {"INSERT": 1, "REMOVE": 2, "BOTH": 3, "ASK": 4})  # insert remote changes into current, remove remote deletions from current, do both (replicates remote state), or ask per block  # line 84
MergeBlockType = enum.Enum("MergeBlockType", "KEEP INSERT REMOVE REPLACE MOVE")  # modify = intra-line changes, replace = full block replacement  # line 85


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("inSync", 'bool'), ("tracked", 'List[str]'), ("untracked", 'List[str]'), ("parent", '_coconut.typing.Optional[int]'), ("revision", '_coconut.typing.Optional[int]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 89
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 89
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 89
    def __new__(_cls, number, ctime, name=None, inSync=False, tracked=[], untracked=[], parent=None, revision=None):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 89
        return _coconut.tuple.__new__(_cls, (number, ctime, name, inSync, tracked, untracked, parent, revision))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 89
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 90
    __slots__ = ()  # line 90
    __ne__ = _coconut.object.__ne__  # line 90
    def __new__(_cls, number, ctime, message=None):  # line 90
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 90

class PathInfo(_coconut_NamedTuple("PathInfo", [("nameHash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", '_coconut.typing.Optional[str]')])):  # size == None means deleted in this revision  # line 91
    __slots__ = ()  # size == None means deleted in this revision  # line 91
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 91
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]'), ("moves", 'Dict[str, Tuple[str, PathInfo]]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 92
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 92
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 92
class Range(_coconut_NamedTuple("Range", [("tipe", 'MergeBlockType'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 93
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 93
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 93
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'MergeBlockType'), ("lines", 'List[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 94
    __slots__ = ()  # line 94
    __ne__ = _coconut.object.__ne__  # line 94
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 94
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 94

class GlobBlock(_coconut_NamedTuple("GlobBlock", [("isLiteral", 'bool'), ("content", 'str'), ("index", 'int')])):  # for file pattern rename/move matching  # line 95
    __slots__ = ()  # for file pattern rename/move matching  # line 95
    __ne__ = _coconut.object.__ne__  # for file pattern rename/move matching  # line 95
class GlobBlock2(_coconut_NamedTuple("GlobBlock2", [("isLiteral", 'bool'), ("content", 'str'), ("matches", 'str')])):  # matching file pattern and input filename for translation  # line 96
    __slots__ = ()  # matching file pattern and input filename for translation  # line 96
    __ne__ = _coconut.object.__ne__  # matching file pattern and input filename for translation  # line 96
DataType = TypeVar("DataType", BranchInfo, ChangeSet, MergeBlock, PathInfo)  # line 97


# Functions
def printo(s: 'str'="", nl: 'str'="\n"):  # PEP528 compatibility  # line 101
    sys.stdout.buffer.write((s + nl).encode(sys.stdout.encoding, 'backslashreplace'))  # PEP528 compatibility  # line 101
    sys.stdout.flush()  # PEP528 compatibility  # line 101
def printe(s: 'str'="", nl: 'str'="\n"):  # line 102
    sys.stderr.buffer.write((s + nl).encode(sys.stderr.encoding, 'backslashreplace'))  # line 102
    sys.stderr.flush()  # line 102
@_coconut_tco  # for py->os access of writing filenames  # PEP 529 compatibility  # line 103
def encode(s: 'str') -> 'bytes':  # for py->os access of writing filenames  # PEP 529 compatibility  # line 103
    return _coconut_tail_call(os.fsencode, s)  # for py->os access of writing filenames  # PEP 529 compatibility  # line 103
@_coconut_tco  # for os->py access of reading filenames  # line 104
def decode(b: 'bytes') -> 'str':  # for os->py access of reading filenames  # line 104
    return _coconut_tail_call(os.fsdecode, b)  # for os->py access of reading filenames  # line 104
try:  # line 105
    import chardet  # https://github.com/chardet/chardet  # line 106
    def detectEncoding(binary: 'bytes') -> 'str':  # line 107
        return chardet.detect(binary)["encoding"]  # line 107
except:  # line 108
    def detectEncoding(binary: 'bytes') -> 'str':  # Guess the encoding  # line 109
        ''' Fallback if chardet library missing. '''  # line 110
        try:  # line 111
            binary.decode(UTF8)  # line 111
            return UTF8  # line 111
        except UnicodeError:  # line 112
            pass  # line 112
        try:  # line 113
            binary.decode("utf_16")  # line 113
            return "utf_16"  # line 113
        except UnicodeError:  # line 114
            pass  # line 114
        try:  # line 115
            binary.decode("cp1252")  # line 115
            return "cp1252"  # line 115
        except UnicodeError:  # line 116
            pass  # line 116
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 117

def tryOrDefault(func: '_coconut.typing.Callable[[], Any]', default: 'Any') -> 'Any':  # line 119
    try:  # line 120
        return func()  # line 120
    except:  # line 121
        return default  # line 121

def tryOrIgnore(func: '_coconut.typing.Callable[[], Any]') -> 'None':  # handle with care!  # line 123
    try:  # line 124
        func()  # line 124
    except:  # line 125
        pass  # line 125

@_coconut_tco  # line 127
def wcswidth(string: 'str') -> 'int':  # line 127
    l = 0  # type: int  # line 128
    try:  # line 129
        l = wcwidth.wcswitdh(string)  # line 130
        return len(string) if l < 0 else l  # line 131
    finally:  # line 132
        return _coconut_tail_call(len, string)  # line 132

def removePath(key: 'str', value: 'str') -> 'str':  # line 134
    ''' Cleanup of user-specified global file patterns. '''  # line 135
    return value if value in GLOBAL_LISTS or SLASH not in value else value[value.rindex(SLASH) + 1:]  # line 136

def conditionalIntersection(a: '_coconut.typing.Optional[FrozenSet[str]]', b: 'FrozenSet[str]') -> 'FrozenSet[str]':  # Used to match only arguments, or use only stored patterns  # line 138
    return a & b if a else b  # Used to match only arguments, or use only stored patterns  # line 138

def dictUpdate(dikt: 'Dict[Any, Any]', by: 'Dict[Any, Any]') -> 'Dict[Any, Any]':  # line 140
    d = {}  # line 140
    d.update(dikt)  # line 140
    d.update(by)  # line 140
    return d  # line 140

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO[bytes]':  # Abstraction for opening both compressed and plain files  # line 142
    return bz2.BZ2File(encode(file), mode) if compress else open(encode(file), mode + "b")  # Abstraction for opening both compressed and plain files  # line 142

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 144
    ''' Determine EOL style from a binary string. '''  # line 145
    lf = file.count(b"\n")  # type: int  # line 146
    cr = file.count(b"\r")  # type: int  # line 147
    crlf = file.count(b"\r\n")  # type: int  # line 148
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 149
        if lf != crlf or cr != crlf:  # line 150
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 150
        return b"\r\n"  # line 151
    if lf != 0 and cr != 0:  # line 152
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 152
    if lf > cr:  # Linux/Unix  # line 153
        return b"\n"  # Linux/Unix  # line 153
    if cr > lf:  # older 8-bit machines  # line 154
        return b"\r"  # older 8-bit machines  # line 154
    return None  # no new line contained, cannot determine  # line 155

try:  # line 157
    Splittable = TypeVar("Splittable", str, bytes)  # line 157
except:  # line 158
    pass  # line 158
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> 'List[Splittable]':  # line 159
    return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 159

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl: 'str'="") -> 'str':  # line 161
    return (sep + (nl + sep).join(seq)) if seq else ""  # line 161

@_coconut_tco  # line 163
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 163
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 163

@_coconut_tco  # line 165
def hashStr(datas: 'str') -> 'str':  # line 165
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 165

def modified(changes: 'ChangeSet', onlyBinary: 'bool'=False) -> 'bool':  # line 167
    return len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0 or len(changes.moves) > 0  # line 167

def listindex(lizt: 'Sequence[Any]', what: 'Any', index: 'int'=0) -> 'int':  # line 169
    return lizt[index:].index(what) + index  # line 169

def getTermWidth() -> 'int':  # line 171
    try:  # line 172
        import termwidth  # line 172
    except:  # line 173
        return 80  # line 173
    return termwidth.getTermWidth()[0]  # line 174

def branchFolder(branch: 'int', base: '_coconut.typing.Optional[str]'=None, file: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 176
    return os.path.join((os.getcwd() if base is None else base), metaFolder, "b%d" % branch) + ((os.sep + file) if file else "")  # line 176

def revisionFolder(branch: 'int', revision: 'int', base: '_coconut.typing.Optional[str]'=None, file: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 178
    return os.path.join(branchFolder(branch, base), "r%d" % revision) + ((os.sep + file) if file else "")  # line 178

def Exit(message: 'str'="", code=1):  # line 180
    printe("[EXIT%s]" % (" %.1fs" % (time.time() - START_TIME) if verbose else "") + (" " + message + "." if message != "" else ""))  # line 180
    sys.exit(code)  # line 180

def exception(E):  # line 182
    ''' Report an exception. '''  # line 183
    printo(str(E))  # line 184
    import traceback  # line 185
    traceback.print_exc()  # line 186
    traceback.print_stack()  # line 187

def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None, callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None) -> 'Tuple[str, int]':  # line 189
    ''' Calculate hash of file contents, and return compressed sized, if in write mode, or zero. '''  # line 190
    indicator = ProgressIndicator(callback) if callback else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 191
    _hash = hashlib.sha256()  # line 192
    wsize = 0  # type: int  # line 193
    if saveTo and os.path.exists(encode(saveTo)):  # line 194
        Exit("Hash conflict. Leaving revision in inconsistent state. This should happen only once in a lifetime.")  # line 194
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 195
    with open(encode(path), "rb") as fd:  # line 196
        while True:  # line 197
            buffer = fd.read(bufSize)  # type: bytes  # line 198
            _hash.update(buffer)  # line 199
            if to:  # line 200
                to.write(buffer)  # line 200
            if len(buffer) < bufSize:  # line 201
                break  # line 201
            if indicator:  # line 202
                indicator.getIndicator()  # line 202
        if to:  # line 203
            to.close()  # line 204
            wsize = os.stat(encode(saveTo)).st_size  # line 205
    return (_hash.hexdigest(), wsize)  # line 206

def getAnyOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 208
    ''' Utility to find any entries of a dictionary in a list to return the dictionaries value. '''  # line 209
    for k, v in map.items():  # line 210
        if k in params:  # line 211
            return v  # line 211
    return default  # line 212

@_coconut_tco  # line 214
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 214
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 214

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None, ignoreWhitespace: 'bool'=False) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 216
    lines = []  # type: _coconut.typing.Sequence[str]  # line 217
    if filename is not None:  # line 218
        with open(encode(filename), "rb") as fd:  # line 219
            content = fd.read()  # line 219
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detectEncoding(content))  # type: str  # line 220
    eol = eoldet(content)  # type: _coconut.typing.Optional[bytes]  # line 221
    if filename is not None:  # line 222
        with codecs.open(encode(filename), encoding=encoding) as fd2:  # line 223
            lines = safeSplit(fd2.read(), ((b"\n" if eol is None else eol)).decode(encoding))  # line 223
    elif content is not None:  # line 224
        lines = safeSplit(content.decode(encoding), ((b"\n" if eol is None else eol)).decode(encoding))  # line 225
    else:  # line 226
        return (sys.getdefaultencoding(), b"\n", [])  # line 226
    if ignoreWhitespace:  # line 227
        lines[:] = [line.replace("\t", "  ").strip() for line in lines]  # line 227
    return (encoding, eol, lines)  # line 228

@_coconut_tco  # line 230
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, byValue: 'bool'=False, **_kwargs) -> 'DataType':  # line 230
    ''' A better makedata() version. '''  # line 231
    r = _old._asdict()  # type: Dict[str, Any]  # line 232
    r.update({k: ([e for e in v] if byValue and isinstance(v, (list, tuple, set)) else v) for k, v in _kwargs.items()})  # copy by value if required  # line 233
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # TODO also offer copy-by-value here  # line 234

def user_block_input(output: 'List[str]'):  # line 236
    sep = input("Enter end-of-text marker (default: <empty line>: ")  # type: str  # line 237
    line = sep  # type: str  # line 237
    while True:  # line 238
        line = input("> ")  # line 239
        if line == sep:  # line 240
            break  # line 240
        output.append(line)  # writes to caller-provided list reference  # line 241

def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation: 'MergeOperation'=MergeOperation.BOTH, charMergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False, eol: 'bool'=False, ignoreWhitespace: 'bool'=False) -> 'Tuple[Union[bytes, List[MergeBlock]], _coconut.typing.Optional[bytes]]':  # line 243
    ''' Merges other binary text contents 'file' (or reads file 'filename') into current text contents 'into' (or reads file 'intoname'), returning merged result.
      For update, the other version is assumed to be the "new/added" one, while for diff, the current changes are the ones "added".
      However, change direction markers are insert ("+") for elements only in into, and remove ("-") for elements only in other file (just like the diff marks +/-)
      diffOnly returns detected change blocks only, no text merging
      eol flag will use the other file's EOL marks
      in case of replace block and INSERT strategy, the change will be added **behind** the original
  '''  # line 258
    encoding = None  # type: str  # line 259
    othr = None  # type: _coconut.typing.Sequence[str]  # line 259
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 259
    curr = None  # type: _coconut.typing.Sequence[str]  # line 259
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 259
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 260
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file, ignoreWhitespace=ignoreWhitespace)  # line 261
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into, ignoreWhitespace=ignoreWhitespace)  # line 262
    except Exception as E:  # line 263
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 263
    if None not in [othreol, curreol] and othreol != curreol:  # line 264
        warn("Differing EOL-styles detected during merge. Using current file's style for merged output")  # line 264
    output = list(difflib.Differ().compare(othr, curr))  # type: List[str]  # from generator expression  # line 265
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 266
    tmp = []  # type: List[str]  # block lines  # line 267
    last = " "  # type: str  # line 268
    no = None  # type: int  # line 268
    line = None  # type: str  # line 268
    for no, line in enumerate(output + ["X"]):  # EOF marker (difflib's output will never be "X" alone)  # line 269
        if line[0] == last:  # continue filling current block, no matter what type of block it is  # line 270
            tmp.append(line[2:])  # continue filling current block, no matter what type of block it is  # line 270
            continue  # continue filling current block, no matter what type of block it is  # line 270
        if line == "X" and len(tmp) == 0:  # break if nothing left to do, otherwise perform operation for stored block  # line 271
            break  # break if nothing left to do, otherwise perform operation for stored block  # line 271
        if last == " ":  # block is same in both files  # line 272
            if len(tmp) > 0:  # avoid adding empty keep block  # line 273
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # avoid adding empty keep block  # line 273
        elif last == "-":  # may be a pure deletion or part of a replacement (with next block being "+")  # line 274
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 275
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.INSERT:  # line 276
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp) - 1, replaces=blocks[-2])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 277
                blocks.pop()  # line 278
        elif last == "+":  # may be insertion or replacement (with previous - block)  # line 279
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # first, assume simple insertion, then check for replacement  # line 280
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.REMOVE:  #  and len(blocks[-1].lines) == len(blocks[-2].lines):  # requires previous block and same number of lines TODO allow multiple intra-line merge for same-length blocks  # line 281
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, line=no - len(tmp) - 1, replaces=blocks[-1])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 282
                blocks.pop()  # remove TOS due to merging two blocks into replace or modify  # line 283
#    elif last == "?": pass # marker for intra-line change comment -> add to block info
        last = line[0]  # line 285
        tmp[:] = [line[2:]]  # only keep current line for next block  # line 286
# TODO add code to detect block moves here
    nl = othreol if eol else ((othreol if curreol is None else curreol))  # type: bytes  # no default newline, to mark "no newline"  # line 288
    debug("Diff blocks: " + repr(blocks))  # line 289
    if diffOnly:  # line 290
        return (blocks, nl)  # line 290

# now perform merge operations depending on detected blocks
    output[:] = []  # clean list of strings  # line 293
    for block in blocks:  # line 294
        if block.tipe == MergeBlockType.KEEP:  # line 295
            output.extend(block.lines)  # line 296
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value) or block.tipe == MergeBlockType.REMOVE and (mergeOperation.value & MergeOperation.INSERT.value):  # line 297
            output.extend(block.lines)  # line 299
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 300
            if len(block.lines) == len(block.replaces.lines) == 1:  # one-liner  # line 301
                output.append(lineMerge(block.lines[0], block.replaces.lines[0], mergeOperation=charMergeOperation))  # line 302
            elif mergeOperation == MergeOperation.ASK:  # more than one line: needs user input  # line 303
                printo(ajoin("- ", block.replaces.lines, nl="\n"))  # TODO check +/- in update mode, could be swapped  # line 304
                printo(ajoin("+ ", block.lines, nl="\n"))  # line 305
                while True:  # line 306
                    op = input(" Line replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 307
                    if op in "tb":  # line 308
                        output.extend(block.lines)  # line 308
                        break  # line 308
                    if op in "ib":  # line 309
                        output.extend(block.replaces.lines)  # line 309
                        break  # line 309
                    if op == "m":  # line 310
                        user_block_input(output)  # line 310
                        break  # line 310
            else:  # more than one line and not ask  # line 311
                if mergeOperation == MergeOperation.REMOVE:  # line 312
                    pass  # line 312
                elif mergeOperation == MergeOperation.BOTH:  # line 313
                    output.extend(block.lines)  # line 313
                elif mergeOperation == MergeOperation.INSERT:  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 314
                    output.extend(list(block.replaces.lines) + list(block.lines))  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 314
#  debug("Merge output: " + "; ".join(output))
    return (((b"\n" if nl is None else nl)).join([line.encode(encoding) for line in output]), nl)  # returning bytes  # line 316
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco  # line 319
def lineMerge(othr: 'str', into: 'str', mergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False) -> 'Union[str, List[MergeBlock]]':  # line 319
    ''' Merges string 'othr' into current string 'into'.
      change direction mark is insert for elements only in into, and remove for elements only in file (according to diff marks +/-)
  '''  # line 322
    out = list(difflib.Differ().compare(othr, into))  # type: List[str]  # line 323
    blocks = []  # type: List[MergeBlock]  # line 324
    for i, line in enumerate(out):  # line 325
        if line[0] == "+":  # line 326
            if i + 1 < len(out) and out[i + 1][0] == "+":  # block will continue  # line 327
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # middle of + block  # line 328
                    blocks[-1].lines.append(line[2])  # add one more character to the accumulating list  # line 329
                else:  # first + in block  # line 330
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 331
            else:  # last line of + block  # line 332
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # end of a block  # line 333
                    blocks[-1].lines.append(line[2])  # line 334
                else:  # single line  # line 335
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 336
                if i >= 1 and blocks[-2].tipe == MergeBlockType.REMOVE:  # previous - and now last in + block creates a replacement block  # line 337
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, i, replaces=blocks[-1])  # line 338
                    blocks.pop()  # line 338
        elif line[0] == "-":  # line 339
            if i > 0 and blocks[-1].tipe == MergeBlockType.REMOVE:  # part of - block  # line 340
                blocks[-1].lines.append(line[2])  # line 341
            else:  # first in block  # line 342
                blocks.append(MergeBlock(MergeBlockType.REMOVE, [line[2]], i))  # line 343
        elif line[0] == " ":  # line 344
            if i > 0 and blocks[-1].tipe == MergeBlockType.KEEP:  # part of block  # line 345
                blocks[-1].lines.append(line[2])  # line 346
            else:  # first in block  # line 347
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line[2]], i))  # line 348
        else:  # line 349
            raise Exception("Cannot parse diff line %r" % line)  # line 349
    blocks[:] = [dataCopy(MergeBlock, block, lines=["".join(block.lines)], replaces=dataCopy(MergeBlock, block.replaces, lines=["".join(block.replaces.lines)]) if block.replaces else None) for block in blocks]  # line 350
    if diffOnly:  # line 351
        return blocks  # line 351
    out[:] = []  # line 352
    for i, block in enumerate(blocks):  # line 353
        if block.tipe == MergeBlockType.KEEP:  # line 354
            out.extend(block.lines)  # line 354
        elif block.tipe == MergeBlockType.REPLACE:  # line 355
            if mergeOperation == MergeOperation.ASK:  # line 356
                printo(ajoin("- ", othr))  # line 357
                printo("- " + (" " * i) + block.replaces.lines[0])  # line 358
                printo("+ " + (" " * i) + block.lines[0])  # line 359
                printo(ajoin("+ ", into))  # line 360
                while True:  # line 361
                    op = input(" Character replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 362
                    if op in "tb":  # line 363
                        out.extend(block.lines)  # line 363
                        break  # line 363
                    if op in "ib":  # line 364
                        out.extend(block.replaces.lines)  # line 364
                        break  # line 364
                    if op == "m":  # line 365
                        user_block_input(out)  # line 365
                        break  # line 365
            else:  # non-interactive  # line 366
                if mergeOperation == MergeOperation.REMOVE:  # line 367
                    pass  # line 367
                elif mergeOperation == MergeOperation.BOTH:  # line 368
                    out.extend(block.lines)  # line 368
                elif mergeOperation == MergeOperation.INSERT:  # line 369
                    out.extend(list(block.replaces.lines) + list(block.lines))  # line 369
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value):  # line 370
            out.extend(block.lines)  # line 370
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation.value & MergeOperation.INSERT.value:  # line 371
            out.extend(block.lines)  # line 371
# TODO ask for insert or remove as well
    return _coconut_tail_call("".join, out)  # line 373

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 375
    ''' Attempts to find sos and legacy VCS base folders.
      Returns (SOS-repo root, VCS-repo root, VCS command)
  '''  # line 378
    debug("Detecting root folders...")  # line 379
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 380
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 381
    while not os.path.exists(encode(os.path.join(path, metaFolder))):  # line 382
        contents = set(os.listdir(path))  # type: Set[str]  # line 383
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 384
        choice = None  # type: _coconut.typing.Optional[str]  # line 385
        if len(vcss) > 1:  # line 386
            choice = SVN if SVN in vcss else vcss[0]  # line 387
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 388
        elif len(vcss) > 0:  # line 389
            choice = vcss[0]  # line 389
        if not vcs[0] and choice:  # memorize current repo root  # line 390
            vcs = (path, choice)  # memorize current repo root  # line 390
        new = os.path.dirname(path)  # get parent path  # line 391
        if new == path:  # avoid infinite loop  # line 392
            break  # avoid infinite loop  # line 392
        path = new  # line 393
    if os.path.exists(encode(os.path.join(path, metaFolder))):  # found something  # line 394
        if vcs[0]:  # already detected vcs base and command  # line 395
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 395
        sos = path  # line 396
        while True:  # continue search for VCS base  # line 397
            new = os.path.dirname(path)  # get parent path  # line 398
            if new == path:  # no VCS folder found  # line 399
                return (sos, None, None)  # no VCS folder found  # line 399
            path = new  # line 400
            contents = set(os.listdir(path))  # line 401
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 402
            choice = None  # line 403
            if len(vcss) > 1:  # line 404
                choice = SVN if SVN in vcss else vcss[0]  # line 405
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 406
            elif len(vcss) > 0:  # line 407
                choice = vcss[0]  # line 407
            if choice:  # line 408
                return (sos, path, choice)  # line 408
    return (None, vcs[0], vcs[1])  # line 409

def tokenizeGlobPattern(pattern: 'str') -> 'List[GlobBlock]':  # line 411
    index = 0  # type: int  # line 412
    out = []  # type: List[GlobBlock]  # literal = True, first index  # line 413
    while index < len(pattern):  # line 414
        if pattern[index:index + 3] in ("[?]", "[*]", "[[]", "[]]"):  # line 415
            out.append(GlobBlock(False, pattern[index:index + 3], index))  # line 415
            continue  # line 415
        if pattern[index] in "*?":  # line 416
            count = 1  # type: int  # line 417
            while index + count < len(pattern) and pattern[index] == "?" and pattern[index + count] == "?":  # line 418
                count += 1  # line 418
            out.append(GlobBlock(False, pattern[index:index + count], index))  # line 419
            index += count  # line 419
            continue  # line 419
        if pattern[index:index + 2] == "[!":  # line 420
            out.append(GlobBlock(False, pattern[index:pattern.index("]", index + 2) + 1], index))  # line 420
            index += len(out[-1][1])  # line 420
            continue  # line 420
        count = 1  # line 421
        while index + count < len(pattern) and pattern[index + count] not in "*?[":  # line 422
            count += 1  # line 422
        out.append(GlobBlock(True, pattern[index:index + count], index))  # line 423
        index += count  # line 423
    return out  # line 424

def tokenizeGlobPatterns(oldPattern: 'str', newPattern: 'str') -> 'Tuple[_coconut.typing.Sequence[GlobBlock], _coconut.typing.Sequence[GlobBlock]]':  # line 426
    ot = tokenizeGlobPattern(oldPattern)  # type: List[GlobBlock]  # line 427
    nt = tokenizeGlobPattern(newPattern)  # type: List[GlobBlock]  # line 428
#  if len(ot) != len(nt): Exit("Source and target patterns can't be translated due to differing number of parsed glob markers and literal strings")
    if len([o for o in ot if not o.isLiteral]) < len([n for n in nt if not n.isLiteral]):  # line 430
        Exit("Source and target file patterns contain differing number of glob markers and can't be translated")  # line 430
    if any((O.content != N.content for O, N in zip([o for o in ot if not o.isLiteral], [n for n in nt if not n.isLiteral]))):  # line 431
        Exit("Source and target file patterns differ in semantics")  # line 431
    return (ot, nt)  # line 432

def convertGlobFiles(filenames: '_coconut.typing.Sequence[str]', oldPattern: '_coconut.typing.Sequence[GlobBlock]', newPattern: '_coconut.typing.Sequence[GlobBlock]') -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 434
    ''' Converts given filename according to specified file patterns. No support for adjacent glob markers currently. '''  # line 435
    pairs = []  # type: List[Tuple[str, str]]  # line 436
    for filename in filenames:  # line 437
        literals = [l for l in oldPattern if l.isLiteral]  # type: List[GlobBlock]  # source literals  # line 438
        nextliteral = 0  # type: int  # line 439
        parsedOld = []  # type: List[GlobBlock2]  # line 440
        index = 0  # type: int  # line 441
        for part in oldPattern:  # match everything in the old filename  # line 442
            if part.isLiteral:  # line 443
                parsedOld.append(GlobBlock2(True, part.content, part.content))  # line 443
                index += len(part.content)  # line 443
                nextliteral += 1  # line 443
            elif part.content.startswith("?"):  # line 444
                parsedOld.append(GlobBlock2(False, part.content, filename[index:index + len(part.content)]))  # line 444
                index += len(part.content)  # line 444
            elif part.content.startswith("["):  # line 445
                parsedOld.append(GlobBlock2(False, part.content, filename[index]))  # line 445
                index += 1  # line 445
            elif part.content == "*":  # line 446
                if nextliteral >= len(literals):  # line 447
                    parsedOld.append(GlobBlock2(False, part.content, filename[index:]))  # line 447
                    break  # line 447
                nxt = filename.index(literals[nextliteral].content, index)  # type: int  # also matches empty string  # line 448
                parsedOld.append(GlobBlock2(False, part.content, filename[index:nxt]))  # line 449
                index = nxt  # line 449
            else:  # line 450
                Exit("Invalid file pattern specified for move/rename")  # line 450
        globs = [g for g in parsedOld if not g.isLiteral]  # type: List[GlobBlock2]  # line 451
        literals = [l for l in newPattern if l.isLiteral]  # target literals  # line 452
        nextliteral = 0  # line 453
        nextglob = 0  # type: int  # line 453
        outname = []  # type: List[str]  # line 454
        for part in newPattern:  # generate new filename  # line 455
            if part.isLiteral:  # line 456
                outname.append(literals[nextliteral].content)  # line 456
                nextliteral += 1  # line 456
            else:  # line 457
                outname.append(globs[nextglob].matches)  # line 457
                nextglob += 1  # line 457
        pairs.append((filename, "".join(outname)))  # line 458
    return pairs  # line 459

@_coconut_tco  # line 461
def reorderRenameActions(actions: '_coconut.typing.Sequence[Tuple[str, str]]', exitOnConflict: 'bool'=True) -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 461
    ''' Attempt to put all rename actions into an order that avoids target == source names.
      Note, that it's currently not really possible to specify patterns that make this work (swapping "*" elements with a reference).
      An alternative would be to always have one (or all) files renamed to a temporary name before renaming to target filename.
  '''  # line 465
    if not actions:  # line 466
        return []  # line 466
    sources = None  # type: List[str]  # line 467
    targets = None  # type: List[str]  # line 467
    sources, targets = [list(l) for l in zip(*actions)]  # line 468
    last = len(actions)  # type: int  # line 469
    while last > 1:  # line 470
        clean = True  # type: bool  # line 471
        for i in range(1, last):  # line 472
            try:  # line 473
                index = targets[:i].index(sources[i])  # type: int  # line 474
                sources.insert(index, sources.pop(i))  # bubble up the action right before conflict  # line 475
                targets.insert(index, targets.pop(i))  # line 476
                clean = False  # line 477
            except:  # target not found in sources: good!  # line 478
                continue  # target not found in sources: good!  # line 478
        if clean:  # line 479
            break  # line 479
        last -= 1  # we know that the last entry in the list has the least conflicts, so we can disregard it in the next iteration  # line 480
    if exitOnConflict:  # line 481
        for i in range(1, len(actions)):  # line 482
            if sources[i] in targets[:i]:  # line 483
                Exit("There is no order of renaming actions that avoids copying over not-yet renamed files: '%s' is contained in matching source filenames" % (targets[i]))  # line 483
    return _coconut_tail_call(list, zip(sources, targets))  # convert to list to avoid generators  # line 484

def relativize(root: 'str', filepath: 'str') -> 'Tuple[str, str]':  # line 486
    ''' Determine OS-independent relative folder path, and relative pattern path. '''  # line 487
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(filepath)), root).replace(os.sep, SLASH)  # line 488
    return relpath, os.path.join(relpath, os.path.basename(filepath)).replace(os.sep, SLASH)  # line 489

def parseOnlyOptions(root: 'str', options: '_coconut.typing.Sequence[str]') -> 'Tuple[_coconut.typing.Optional[FrozenSet[str]], _coconut.typing.Optional[FrozenSet[str]]]':  # line 491
    ''' Returns set of --only arguments, and set or --except arguments. '''  # line 492
    cwd = os.getcwd()  # type: str  # line 493
    onlys = []  # type: List[str]  # line 494
    excps = []  # type: List[str]  # line 494
    index = 0  # type: int  # line 494
    while True:  # line 495
        try:  # line 496
            index = 1 + listindex(options, "--only", index)  # line 497
            onlys.append(options[index])  # line 498
        except:  # line 499
            break  # line 499
    index = 0  # line 500
    while True:  # line 501
        try:  # line 502
            index = 1 + listindex(options, "--except", index)  # line 503
            excps.append(options[index])  # line 504
        except:  # line 505
            break  # line 505
    return (frozenset((relativize(root, o)[1] for o in onlys)) if onlys else None, frozenset((relativize(root, e)[1] for e in excps)) if excps else None)  # line 506
