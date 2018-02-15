#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xfc47e440

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
try:  # TODO remove as soon as Coconut supports it  # line 8
    from typing import Any  # only required for mypy  # line 9
    from typing import Callable  # only required for mypy  # line 9
    from typing import Dict  # only required for mypy  # line 9
    from typing import FrozenSet  # only required for mypy  # line 9
    from typing import Generic  # only required for mypy  # line 9
    from typing import IO  # only required for mypy  # line 9
    from typing import List  # only required for mypy  # line 9
    from typing import Sequence  # only required for mypy  # line 9
    from typing import Set  # only required for mypy  # line 9
    from typing import Tuple  # only required for mypy  # line 9
    from typing import Type  # only required for mypy  # line 9
    from typing import TypeVar  # only required for mypy  # line 9
    from typing import Union  # only required for mypy  # line 9
    Number = TypeVar("Number", int, float)  # line 10
    DataType = TypeVar("DataType", BranchInfo, ChangeSet, MergeBlock, PathInfo)  # line 11
except:  # typing not available (prior to Python 3.5)  # line 12
    pass  # typing not available (prior to Python 3.5)  # line 12
try:  # line 13
    import wcwidth  # line 13
except:  # optional dependency  # line 14
    pass  # optional dependency  # line 14


verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 17

# Classes
class Accessor(dict):  # line 20
    ''' Dictionary with attribute access. Writing only supported via dictionary access. '''  # line 21
    def __init__(_, mapping: 'Dict[str, Any]'):  # line 22
        dict.__init__(_, mapping)  # line 22
    @_coconut_tco  # line 23
    def __getattribute__(_, name: 'str') -> 'Any':  # line 23
        try:  # line 24
            return _[name]  # line 24
        except:  # line 25
            return _coconut_tail_call(dict.__getattribute__, _, name)  # line 25

class Counter(Generic[Number]):  # line 27
    ''' A simple counter. Can be augmented to return the last value instead. '''  # line 28
    def __init__(_, initial: 'Number'=0):  # line 29
        _.value = initial  # type: Number  # line 29
    def inc(_, by: 'Number'=1) -> 'Number':  # line 30
        _.value += by  # line 30
        return _.value  # line 30

class ProgressIndicator(Counter):  # line 32
    ''' Manages a rotating progress indicator. '''  # line 33
    def __init__(_, callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None):  # line 34
        super(ProgressIndicator, _).__init__(-1)  # line 34
        _.timer = time.time()  # type: float  # line 34
        _.callback = callback  # type: Optional[_coconut.typing.Callable[[str], None]]  # line 34
    def getIndicator(_) -> '_coconut.typing.Optional[str]':  # line 35
        newtime = time.time()  # line 36
        if newtime - _.timer < .1:  # line 37
            return None  # line 37
        _.timer = newtime  # line 38
        sign = PROGRESS_MARKER[int(_.inc() % 4)]  # type: str  # line 39
        if _.callback:  # line 40
            _.callback(sign)  # line 40
        return sign  # line 41

class Logger:  # line 43
    ''' Logger that supports many items. '''  # line 44
    def __init__(_, log):  # line 45
        _._log = log  # line 45
    def debug(_, *s):  # line 46
        _._log.debug(sjoin(*s))  # line 46
    def info(_, *s):  # line 47
        _._log.info(sjoin(*s))  # line 47
    def warn(_, *s):  # line 48
        _._log.warning(sjoin(*s))  # line 48
    def error(_, *s):  # line 49
        _._log.error(sjoin(*s))  # line 49


# Constants
_log = Logger(logging.getLogger(__name__))  # line 53
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 53
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress"]  # type: List[str]  # line 54
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # type: List[str]  # line 55
GLOBAL_LISTS = ["ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # type: List[str]  # line 56
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # type: List[str]  # all lower-case normalized  # line 57
FALSE_VALUES = ["false", "no", "off", "0", "disable", "disabled"]  # type: List[str]  # line 58
PROGRESS_MARKER = ["|", "/", "-", "\\"]  # type: List[str]  # line 59
BACKUP_SUFFIX = "_last"  # type: str  # line 60
metaFolder = ".sos"  # type: str  # line 61
metaFile = ".meta"  # type: str  # line 62
metaBack = metaFile + BACKUP_SUFFIX  # type: str  # line 63
MEBI = 1 << 20  # type: int  # line 64
bufSize = MEBI  # type: int  # line 65
UTF8 = "utf_8"  # type: str  # early used constant, not defined in standard library  # line 66
SVN = "svn"  # type: str  # line 67
SLASH = "/"  # type: str  # line 68
METADATA_FORMAT = 1  # type: int  # counter for incompatible consecutive formats  # line 69
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": "fossil", "_FOSSIL_": "fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 70
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 71
NL_NAMES = {None: "<No newline>", b"\r\n": "<CR+LF>", b"\n\r": "<LF+CR>", b"\n": "<LF>", b"\r": "<CR>"}  # type: Dict[bytes, str]  # line 72
lateBinding = Accessor({"verbose": False, "start": 0})  # type: Accessor  # line 73


# Enums
MergeOperation = enum.Enum("MergeOperation", {"INSERT": 1, "REMOVE": 2, "BOTH": 3, "ASK": 4})  # insert remote changes into current, remove remote deletions from current, do both (replicates remote state), or ask per block  # line 77
MergeBlockType = enum.Enum("MergeBlockType", "KEEP INSERT REMOVE REPLACE MOVE")  # modify = intra-line changes, replace = full block replacement  # line 78


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("inSync", 'bool'), ("tracked", 'List[str]'), ("untracked", 'List[str]'), ("parent", '_coconut.typing.Optional[int]'), ("revision", '_coconut.typing.Optional[int]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 82
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 82
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 82
    def __new__(_cls, number, ctime, name=None, inSync=False, tracked=[], untracked=[], parent=None, revision=None):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 82
        return _coconut.tuple.__new__(_cls, (number, ctime, name, inSync, tracked, untracked, parent, revision))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 82
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 83
    __slots__ = ()  # line 83
    __ne__ = _coconut.object.__ne__  # line 83
    def __new__(_cls, number, ctime, message=None):  # line 83
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 83

class PathInfo(_coconut_NamedTuple("PathInfo", [("nameHash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", '_coconut.typing.Optional[str]')])):  # size == None means deleted in this revision  # line 84
    __slots__ = ()  # size == None means deleted in this revision  # line 84
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 84
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]'), ("moves", 'Dict[str, Tuple[str, PathInfo]]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 85
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 85
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 85
class Range(_coconut_NamedTuple("Range", [("tipe", 'MergeBlockType'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 86
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 86
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 86
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'MergeBlockType'), ("lines", 'List[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 87
    __slots__ = ()  # line 87
    __ne__ = _coconut.object.__ne__  # line 87
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 87
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 87

class GlobBlock(_coconut_NamedTuple("GlobBlock", [("isLiteral", 'bool'), ("content", 'str'), ("index", 'int')])):  # for file pattern rename/move matching  # line 88
    __slots__ = ()  # for file pattern rename/move matching  # line 88
    __ne__ = _coconut.object.__ne__  # for file pattern rename/move matching  # line 88
class GlobBlock2(_coconut_NamedTuple("GlobBlock2", [("isLiteral", 'bool'), ("content", 'str'), ("matches", 'str')])):  # matching file pattern and input filename for translation  # line 89
    __slots__ = ()  # matching file pattern and input filename for translation  # line 89
    __ne__ = _coconut.object.__ne__  # matching file pattern and input filename for translation  # line 89


# Functions
def printo(s: 'str'="", nl: 'str'="\n"):  # PEP528 compatibility  # line 93
    sys.stdout.buffer.write((s + nl).encode(sys.stdout.encoding, 'backslashreplace'))  # PEP528 compatibility  # line 93
    sys.stdout.flush()  # PEP528 compatibility  # line 93
def printe(s: 'str'="", nl: 'str'="\n"):  # line 94
    sys.stderr.buffer.write((s + nl).encode(sys.stderr.encoding, 'backslashreplace'))  # line 94
    sys.stderr.flush()  # line 94
@_coconut_tco  # for py->os access of writing filenames  # PEP 529 compatibility  # line 95
def encode(s: 'str') -> 'bytes':  # for py->os access of writing filenames  # PEP 529 compatibility  # line 95
    return _coconut_tail_call(os.fsencode, s)  # for py->os access of writing filenames  # PEP 529 compatibility  # line 95
@_coconut_tco  # for os->py access of reading filenames  # line 96
def decode(b: 'bytes') -> 'str':  # for os->py access of reading filenames  # line 96
    return _coconut_tail_call(os.fsdecode, b)  # for os->py access of reading filenames  # line 96
try:  # line 97
    import chardet  # https://github.com/chardet/chardet  # line 98
    def detectEncoding(binary: 'bytes') -> 'str':  # line 99
        return chardet.detect(binary)["encoding"]  # line 99
except:  # line 100
    def detectEncoding(binary: 'bytes') -> 'str':  # Guess the encoding  # line 101
        ''' Fallback if chardet library missing. '''  # line 102
        try:  # line 103
            binary.decode(UTF8)  # line 103
            return UTF8  # line 103
        except UnicodeError:  # line 104
            pass  # line 104
        try:  # line 105
            binary.decode("utf_16")  # line 105
            return "utf_16"  # line 105
        except UnicodeError:  # line 106
            pass  # line 106
        try:  # line 107
            binary.decode("cp1252")  # line 107
            return "cp1252"  # line 107
        except UnicodeError:  # line 108
            pass  # line 108
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 109

def tryOrDefault(func: '_coconut.typing.Callable[[], Any]', default: 'Any') -> 'Any':  # line 111
    try:  # line 112
        return func()  # line 112
    except:  # line 113
        return default  # line 113

def tryOrIgnore(func: '_coconut.typing.Callable[[], Any]') -> 'None':  # handle with care!  # line 115
    try:  # line 116
        func()  # line 116
    except:  # line 117
        pass  # line 117

@_coconut_tco  # line 119
def wcswidth(string: 'str') -> 'int':  # line 119
    l = 0  # type: int  # line 120
    try:  # line 121
        l = wcwidth.wcswitdh(string)  # line 122
        return len(string) if l < 0 else l  # line 123
    finally:  # line 124
        return _coconut_tail_call(len, string)  # line 124

def removePath(key: 'str', value: 'str') -> 'str':  # line 126
    ''' Cleanup of user-specified global file patterns. '''  # line 127
    return value if value in GLOBAL_LISTS or SLASH not in value else value[value.rindex(SLASH) + 1:]  # line 128

def conditionalIntersection(a: '_coconut.typing.Optional[FrozenSet[str]]', b: 'FrozenSet[str]') -> 'FrozenSet[str]':  # Used to match only arguments, or use only stored patterns  # line 130
    return a & b if a else b  # Used to match only arguments, or use only stored patterns  # line 130

def dictUpdate(dikt: 'Dict[Any, Any]', by: 'Dict[Any, Any]') -> 'Dict[Any, Any]':  # line 132
    d = {}  # line 132
    d.update(dikt)  # line 132
    d.update(by)  # line 132
    return d  # line 132

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO[bytes]':  # Abstraction for opening both compressed and plain files  # line 134
    return bz2.BZ2File(encode(file), mode) if compress else open(encode(file), mode + "b")  # Abstraction for opening both compressed and plain files  # line 134

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 136
    ''' Determine EOL style from a binary string. '''  # line 137
    lf = file.count(b"\n")  # type: int  # line 138
    cr = file.count(b"\r")  # type: int  # line 139
    crlf = file.count(b"\r\n")  # type: int  # line 140
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 141
        if lf != crlf or cr != crlf:  # line 142
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 142
        return b"\r\n"  # line 143
    if lf != 0 and cr != 0:  # line 144
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 144
    if lf > cr:  # Linux/Unix  # line 145
        return b"\n"  # Linux/Unix  # line 145
    if cr > lf:  # older 8-bit machines  # line 146
        return b"\r"  # older 8-bit machines  # line 146
    return None  # no new line contained, cannot determine  # line 147

try:  # line 149
    Splittable = TypeVar("Splittable", str, bytes)  # line 149
except:  # line 150
    pass  # line 150
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> 'List[Splittable]':  # line 151
    return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 151

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl: 'str'="") -> 'str':  # line 153
    return (sep + (nl + sep).join(seq)) if seq else ""  # line 153

@_coconut_tco  # line 155
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 155
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 155

@_coconut_tco  # line 157
def hashStr(datas: 'str') -> 'str':  # line 157
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 157

def modified(changes: 'ChangeSet', onlyBinary: 'bool'=False) -> 'bool':  # line 159
    return len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0 or len(changes.moves) > 0  # line 159

def listindex(lizt: 'Sequence[Any]', what: 'Any', index: 'int'=0) -> 'int':  # line 161
    return lizt[index:].index(what) + index  # line 161

def getTermWidth() -> 'int':  # line 163
    try:  # line 164
        import termwidth  # line 164
    except:  # line 165
        return 80  # line 165
    return termwidth.getTermWidth()[0]  # line 166

def branchFolder(branch: 'int', revision: 'int', base=".", file=None) -> 'str':  # line 168
    return os.path.join(base, metaFolder, "b%d" % branch, "r%d" % revision) + ((os.sep + file) if file else "")  # line 168

def Exit(message: 'str'="", code=1):  # line 170
    printe("[EXIT%s]" % (" %.1fs" % (time.time() - START_TIME) if verbose else "") + (" " + message + "." if message != "" else ""))  # line 170
    sys.exit(code)  # line 170

def exception(E):  # line 172
    ''' Report an exception. '''  # line 173
    printo(str(E))  # line 174
    import traceback  # line 175
    traceback.print_exc()  # line 176
    traceback.print_stack()  # line 177

def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None, callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None) -> 'Tuple[str, int]':  # line 179
    ''' Calculate hash of file contents, and return compressed sized, if in write mode, or zero. '''  # line 180
    indicator = ProgressIndicator(callback) if callback else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 181
    _hash = hashlib.sha256()  # line 182
    wsize = 0  # type: int  # line 183
    if saveTo and os.path.exists(encode(saveTo)):  # line 184
        Exit("Hash conflict. Leaving revision in inconsistent state. This should happen only once in a lifetime.")  # line 184
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 185
    with open(encode(path), "rb") as fd:  # line 186
        while True:  # line 187
            buffer = fd.read(bufSize)  # type: bytes  # line 188
            _hash.update(buffer)  # line 189
            if to:  # line 190
                to.write(buffer)  # line 190
            if len(buffer) < bufSize:  # line 191
                break  # line 191
            if indicator:  # line 192
                indicator.getIndicator()  # line 192
        if to:  # line 193
            to.close()  # line 194
            wsize = os.stat(encode(saveTo)).st_size  # line 195
    return (_hash.hexdigest(), wsize)  # line 196

def getAnyOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 198
    ''' Utility. '''  # line 199
    for k, v in map.items():  # line 200
        if k in params:  # line 201
            return v  # line 201
    return default  # line 202

@_coconut_tco  # line 204
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 204
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 204

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None, ignoreWhitespace: 'bool'=False) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 206
    encoding = None  # type: str  # line 207
    eol = None  # type: _coconut.typing.Optional[bytes]  # line 207
    lines = []  # type: _coconut.typing.Sequence[str]  # line 207
    if filename is not None:  # line 208
        with open(encode(filename), "rb") as fd:  # line 209
            content = fd.read()  # line 209
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detectEncoding(content))  # line 210
    eol = eoldet(content)  # line 211
    if filename is not None:  # line 212
        with codecs.open(encode(filename), encoding=encoding) as fd2:  # line 213
            lines = safeSplit(fd2.read(), ((b"\n" if eol is None else eol)).decode(encoding))  # line 213
    elif content is not None:  # line 214
        lines = safeSplit(content.decode(encoding), ((b"\n" if eol is None else eol)).decode(encoding))  # line 215
    else:  # line 216
        return (sys.getdefaultencoding(), b"\n", [])  # line 216
    if ignoreWhitespace:  # line 217
        lines[:] = [line.replace("\t", "  ").strip() for line in lines]  # line 217
    return (encoding, eol, lines)  # line 218

@_coconut_tco  # line 220
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, **_kwargs) -> 'DataType':  # line 220
    r = _old._asdict()  # line 220
    r.update(**_kwargs)  # line 220
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # line 220

def user_block_input(output: 'List[str]'):  # line 222
    sep = input("Enter end-of-text marker (default: <empty line>: ")  # type: str  # line 223
    line = sep  # type: str  # line 223
    while True:  # line 224
        line = input("> ")  # line 225
        if line == sep:  # line 226
            break  # line 226
        output.append(line)  # line 227

def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation: 'MergeOperation'=MergeOperation.BOTH, charMergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False, eol: 'bool'=False, ignoreWhitespace: 'bool'=False) -> 'Tuple[Union[bytes, List[MergeBlock]], _coconut.typing.Optional[bytes]]':  # line 229
    ''' Merges other binary text contents 'file' (or reads file 'filename') into current text contents 'into' (or reads file 'intoname'), returning merged result.
      For update, the other version is assumed to be the "new/added" one, while for diff, the current changes are the ones "added".
      However, change direction markers are insert ("+") for elements only in into, and remove ("-") for elements only in other file (just like the diff marks +/-)
      diffOnly returns detected change blocks only, no text merging
      eol flag will use the other file's EOL marks
      in case of replace block and INSERT strategy, the change will be added **behind** the original
  '''  # line 244
    encoding = None  # type: str  # line 245
    othr = None  # type: _coconut.typing.Sequence[str]  # line 245
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 245
    curr = None  # type: _coconut.typing.Sequence[str]  # line 245
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 245
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 246
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file, ignoreWhitespace=ignoreWhitespace)  # line 247
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into, ignoreWhitespace=ignoreWhitespace)  # line 248
    except Exception as E:  # line 249
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 249
    if None not in [othreol, curreol] and othreol != curreol:  # line 250
        warn("Differing EOL-styles detected during merge. Using current file's style for merged output")  # line 250
    output = list(difflib.Differ().compare(othr, curr))  # type: List[str]  # from generator expression  # line 251
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 252
    tmp = []  # type: List[str]  # block lines  # line 253
    last = " "  # type: str  # line 254
    no = None  # type: int  # line 254
    line = None  # type: str  # line 254
    for no, line in enumerate(output + ["X"]):  # EOF marker (difflib's output will never be "X" alone)  # line 255
        if line[0] == last:  # continue filling current block, no matter what type of block it is  # line 256
            tmp.append(line[2:])  # continue filling current block, no matter what type of block it is  # line 256
            continue  # continue filling current block, no matter what type of block it is  # line 256
        if line == "X" and len(tmp) == 0:  # break if nothing left to do, otherwise perform operation for stored block  # line 257
            break  # break if nothing left to do, otherwise perform operation for stored block  # line 257
        if last == " ":  # block is same in both files  # line 258
            if len(tmp) > 0:  # avoid adding empty keep block  # line 259
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # avoid adding empty keep block  # line 259
        elif last == "-":  # may be a pure deletion or part of a replacement (with next block being "+")  # line 260
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 261
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.INSERT:  # line 262
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp) - 1, replaces=blocks[-2])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 263
                blocks.pop()  # line 264
        elif last == "+":  # may be insertion or replacement (with previous - block)  # line 265
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # first, assume simple insertion, then check for replacement  # line 266
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.REMOVE:  #  and len(blocks[-1].lines) == len(blocks[-2].lines):  # requires previous block and same number of lines TODO allow multiple intra-line merge for same-length blocks  # line 267
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, line=no - len(tmp) - 1, replaces=blocks[-1])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 268
                blocks.pop()  # remove TOS due to merging two blocks into replace or modify  # line 269
        elif last == "?":  # marker for intra-line change comment -> add to block info  # line 270
            ilm = getIntraLineMarkers(tmp[0])  # type: Range  # TODO still true? "? " line includes a trailing \n for some reason  # line 271
            blocks[-1] = dataCopy(MergeBlock, blocks[-1], changes=ilm)  # line 272
        last = line[0]  # line 273
        tmp[:] = [line[2:]]  # only keep current line for next block  # line 274
# TODO add code to detect block moves here
    nl = othreol if eol else ((othreol if curreol is None else curreol))  # type: bytes  # no default newline, to mark "no newline"  # line 276
    debug("Diff blocks: " + repr(blocks))  # line 277
    if diffOnly:  # line 278
        return (blocks, nl)  # line 278

# now perform merge operations depending on detected blocks
    output[:] = []  # clean list of strings  # line 281
    for block in blocks:  # line 282
        if block.tipe == MergeBlockType.KEEP:  # line 283
            output.extend(block.lines)  # line 284
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value) or block.tipe == MergeBlockType.REMOVE and (mergeOperation.value & MergeOperation.INSERT.value):  # line 285
            output.extend(block.lines)  # line 287
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 288
            if len(block.lines) == len(block.replaces.lines) == 1:  # one-liner  # line 289
                output.append(lineMerge(block.lines[0], block.replaces.lines[0], mergeOperation=charMergeOperation))  # line 290
            elif mergeOperation == MergeOperation.ASK:  # more than one line: needs user input  # line 291
                printo(ajoin("- ", block.replaces.lines, nl="\n"))  # TODO check +/- in update mode, could be swapped  # line 292
                printo(ajoin("+ ", block.lines, nl="\n"))  # line 293
                while True:  # line 294
                    op = input(" Line replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 295
                    if op in "tb":  # line 296
                        output.extend(block.lines)  # line 296
                        break  # line 296
                    if op in "ib":  # line 297
                        output.extend(block.replaces.lines)  # line 297
                        break  # line 297
                    if op == "m":  # line 298
                        user_block_input(output)  # line 298
                        break  # line 298
            else:  # more than one line and not ask  # line 299
                if mergeOperation == MergeOperation.REMOVE:  # line 300
                    pass  # line 300
                elif mergeOperation == MergeOperation.BOTH:  # line 301
                    output.extend(block.lines)  # line 301
                elif mergeOperation == MergeOperation.INSERT:  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 302
                    output.extend(list(block.replaces.lines) + list(block.lines))  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 302
#  debug("Merge output: " + "; ".join(output))
    return (((b"\n" if nl is None else nl)).join([line.encode(encoding) for line in output]), nl)  # returning bytes  # line 304
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco  # line 307
def lineMerge(othr: 'str', into: 'str', mergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False) -> 'Union[str, List[MergeBlock]]':  # line 307
    ''' Merges string 'othr' into current string 'into'.
      change direction mark is insert for elements only in into, and remove for elements only in file (according to diff marks +/-)
  '''  # line 310
    out = list(difflib.Differ().compare(othr, into))  # type: List[str]  # line 311
    blocks = []  # type: List[MergeBlock]  # line 312
    for i, line in enumerate(out):  # line 313
        if line[0] == "+":  # line 314
            if i + 1 < len(out) and out[i + 1][0] == "+":  # block will continue  # line 315
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # middle of + block  # line 316
                    blocks[-1].lines.append(line[2])  # add one more character to the accumulating list  # line 317
                else:  # first + in block  # line 318
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 319
            else:  # last line of + block  # line 320
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # end of a block  # line 321
                    blocks[-1].lines.append(line[2])  # line 322
                else:  # single line  # line 323
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 324
                if i >= 1 and blocks[-2].tipe == MergeBlockType.REMOVE:  # previous - and now last in + block creates a replacement block  # line 325
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, i, replaces=blocks[-1])  # line 326
                    blocks.pop()  # line 326
        elif line[0] == "-":  # line 327
            if i > 0 and blocks[-1].tipe == MergeBlockType.REMOVE:  # part of - block  # line 328
                blocks[-1].lines.append(line[2])  # line 329
            else:  # first in block  # line 330
                blocks.append(MergeBlock(MergeBlockType.REMOVE, [line[2]], i))  # line 331
        elif line[0] == " ":  # line 332
            if i > 0 and blocks[-1].tipe == MergeBlockType.KEEP:  # part of block  # line 333
                blocks[-1].lines.append(line[2])  # line 334
            else:  # first in block  # line 335
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line[2]], i))  # line 336
        else:  # line 337
            raise Exception("Cannot parse diff line %r" % line)  # line 337
    blocks[:] = [dataCopy(MergeBlock, block, lines=["".join(block.lines)], replaces=dataCopy(MergeBlock, block.replaces, lines=["".join(block.replaces.lines)]) if block.replaces else None) for block in blocks]  # line 338
    if diffOnly:  # line 339
        return blocks  # line 339
    out[:] = []  # line 340
    for i, block in enumerate(blocks):  # line 341
        if block.tipe == MergeBlockType.KEEP:  # line 342
            out.extend(block.lines)  # line 342
        elif block.tipe == MergeBlockType.REPLACE:  # line 343
            if mergeOperation == MergeOperation.ASK:  # line 344
                printo(ajoin("- ", othr))  # line 345
                printo("- " + (" " * i) + block.replaces.lines[0])  # line 346
                printo("+ " + (" " * i) + block.lines[0])  # line 347
                printo(ajoin("+ ", into))  # line 348
                while True:  # line 349
                    op = input(" Character replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 350
                    if op in "tb":  # line 351
                        out.extend(block.lines)  # line 351
                        break  # line 351
                    if op in "ib":  # line 352
                        out.extend(block.replaces.lines)  # line 352
                        break  # line 352
                    if op == "m":  # line 353
                        user_block_input(out)  # line 353
                        break  # line 353
            else:  # non-interactive  # line 354
                if mergeOperation == MergeOperation.REMOVE:  # line 355
                    pass  # line 355
                elif mergeOperation == MergeOperation.BOTH:  # line 356
                    out.extend(block.lines)  # line 356
                elif mergeOperation == MergeOperation.INSERT:  # line 357
                    out.extend(list(block.replaces.lines) + list(block.lines))  # line 357
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value):  # line 358
            out.extend(block.lines)  # line 358
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation.value & MergeOperation.INSERT.value:  # line 359
            out.extend(block.lines)  # line 359
# TODO ask for insert or remove as well
    return _coconut_tail_call("".join, out)  # line 361

@_coconut_tco  # line 363
def getIntraLineMarkers(line: 'str') -> 'Range':  # line 363
    ''' Return (type, [affected indices]) of "? "-line diff markers ("? " prefix must be removed). difflib never returns mixed markers per line. '''  # line 364
    if "^" in line:  # TODO wrong, needs removal anyway  # line 365
        return _coconut_tail_call(Range, MergeBlockType.REPLACE, [i for i, c in enumerate(line) if c == "^"])  # TODO wrong, needs removal anyway  # line 365
    if "+" in line:  # line 366
        return _coconut_tail_call(Range, MergeBlockType.INSERT, [i for i, c in enumerate(line) if c == "+"])  # line 366
    if "-" in line:  # line 367
        return _coconut_tail_call(Range, MergeBlockType.REMOVE, [i for i, c in enumerate(line) if c == "-"])  # line 367
    return _coconut_tail_call(Range, MergeBlockType.KEEP, [])  # line 368

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 370
    ''' Attempts to find sos and legacy VCS base folders. '''  # line 371
    debug("Detecting root folders...")  # line 372
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 373
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 374
    while not os.path.exists(encode(os.path.join(path, metaFolder))):  # line 375
        contents = set(os.listdir(path))  # type: Set[str]  # line 376
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 377
        choice = None  # type: _coconut.typing.Optional[str]  # line 378
        if len(vcss) > 1:  # line 379
            choice = SVN if SVN in vcss else vcss[0]  # line 380
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 381
        elif len(vcss) > 0:  # line 382
            choice = vcss[0]  # line 382
        if not vcs[0] and choice:  # memorize current repo root  # line 383
            vcs = (path, choice)  # memorize current repo root  # line 383
        new = os.path.dirname(path)  # get parent path  # line 384
        if new == path:  # avoid infinite loop  # line 385
            break  # avoid infinite loop  # line 385
        path = new  # line 386
    if os.path.exists(encode(os.path.join(path, metaFolder))):  # found something  # line 387
        if vcs[0]:  # already detected vcs base and command  # line 388
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 388
        sos = path  # line 389
        while True:  # continue search for VCS base  # line 390
            new = os.path.dirname(path)  # get parent path  # line 391
            if new == path:  # no VCS folder found  # line 392
                return (sos, None, None)  # no VCS folder found  # line 392
            path = new  # line 393
            contents = set(os.listdir(path))  # line 394
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 395
            choice = None  # line 396
            if len(vcss) > 1:  # line 397
                choice = SVN if SVN in vcss else vcss[0]  # line 398
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 399
            elif len(vcss) > 0:  # line 400
                choice = vcss[0]  # line 400
            if choice:  # line 401
                return (sos, path, choice)  # line 401
    return (None, vcs[0], vcs[1])  # line 402

def tokenizeGlobPattern(pattern: 'str') -> 'List[GlobBlock]':  # line 404
    index = 0  # type: int  # line 405
    out = []  # type: List[GlobBlock]  # literal = True, first index  # line 406
    while index < len(pattern):  # line 407
        if pattern[index:index + 3] in ("[?]", "[*]", "[[]", "[]]"):  # line 408
            out.append(GlobBlock(False, pattern[index:index + 3], index))  # line 408
            continue  # line 408
        if pattern[index] in "*?":  # line 409
            count = 1  # type: int  # line 410
            while index + count < len(pattern) and pattern[index] == "?" and pattern[index + count] == "?":  # line 411
                count += 1  # line 411
            out.append(GlobBlock(False, pattern[index:index + count], index))  # line 412
            index += count  # line 412
            continue  # line 412
        if pattern[index:index + 2] == "[!":  # line 413
            out.append(GlobBlock(False, pattern[index:pattern.index("]", index + 2) + 1], index))  # line 413
            index += len(out[-1][1])  # line 413
            continue  # line 413
        count = 1  # line 414
        while index + count < len(pattern) and pattern[index + count] not in "*?[":  # line 415
            count += 1  # line 415
        out.append(GlobBlock(True, pattern[index:index + count], index))  # line 416
        index += count  # line 416
    return out  # line 417

def tokenizeGlobPatterns(oldPattern: 'str', newPattern: 'str') -> 'Tuple[_coconut.typing.Sequence[GlobBlock], _coconut.typing.Sequence[GlobBlock]]':  # line 419
    ot = tokenizeGlobPattern(oldPattern)  # type: List[GlobBlock]  # line 420
    nt = tokenizeGlobPattern(newPattern)  # type: List[GlobBlock]  # line 421
#  if len(ot) != len(nt): Exit("Source and target patterns can't be translated due to differing number of parsed glob markers and literal strings")
    if len([o for o in ot if not o.isLiteral]) < len([n for n in nt if not n.isLiteral]):  # line 423
        Exit("Source and target file patterns contain differing number of glob markers and can't be translated")  # line 423
    if any((O.content != N.content for O, N in zip([o for o in ot if not o.isLiteral], [n for n in nt if not n.isLiteral]))):  # line 424
        Exit("Source and target file patterns differ in semantics")  # line 424
    return (ot, nt)  # line 425

def convertGlobFiles(filenames: '_coconut.typing.Sequence[str]', oldPattern: '_coconut.typing.Sequence[GlobBlock]', newPattern: '_coconut.typing.Sequence[GlobBlock]') -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 427
    ''' Converts given filename according to specified file patterns. No support for adjacent glob markers currently. '''  # line 428
    pairs = []  # type: List[Tuple[str, str]]  # line 429
    for filename in filenames:  # line 430
        literals = [l for l in oldPattern if l.isLiteral]  # type: List[GlobBlock]  # source literals  # line 431
        nextliteral = 0  # type: int  # line 432
        parsedOld = []  # type: List[GlobBlock2]  # line 433
        index = 0  # type: int  # line 434
        for part in oldPattern:  # match everything in the old filename  # line 435
            if part.isLiteral:  # line 436
                parsedOld.append(GlobBlock2(True, part.content, part.content))  # line 436
                index += len(part.content)  # line 436
                nextliteral += 1  # line 436
            elif part.content.startswith("?"):  # line 437
                parsedOld.append(GlobBlock2(False, part.content, filename[index:index + len(part.content)]))  # line 437
                index += len(part.content)  # line 437
            elif part.content.startswith("["):  # line 438
                parsedOld.append(GlobBlock2(False, part.content, filename[index]))  # line 438
                index += 1  # line 438
            elif part.content == "*":  # line 439
                if nextliteral >= len(literals):  # line 440
                    parsedOld.append(GlobBlock2(False, part.content, filename[index:]))  # line 440
                    break  # line 440
                nxt = filename.index(literals[nextliteral].content, index)  # type: int  # also matches empty string  # line 441
                parsedOld.append(GlobBlock2(False, part.content, filename[index:nxt]))  # line 442
                index = nxt  # line 442
            else:  # line 443
                Exit("Invalid file pattern specified for move/rename")  # line 443
        globs = [g for g in parsedOld if not g.isLiteral]  # type: List[GlobBlock2]  # line 444
        literals = [l for l in newPattern if l.isLiteral]  # target literals  # line 445
        nextliteral = 0  # line 446
        nextglob = 0  # type: int  # line 446
        outname = []  # type: List[str]  # line 447
        for part in newPattern:  # generate new filename  # line 448
            if part.isLiteral:  # line 449
                outname.append(literals[nextliteral].content)  # line 449
                nextliteral += 1  # line 449
            else:  # line 450
                outname.append(globs[nextglob].matches)  # line 450
                nextglob += 1  # line 450
        pairs.append((filename, "".join(outname)))  # line 451
    return pairs  # line 452

@_coconut_tco  # line 454
def reorderRenameActions(actions: '_coconut.typing.Sequence[Tuple[str, str]]', exitOnConflict: 'bool'=True) -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 454
    ''' Attempt to put all rename actions into an order that avoids target == source names.
      Note, that it's currently not really possible to specify patterns that make this work (swapping "*" elements with a reference).
      An alternative would be to always have one (or all) files renamed to a temporary name before renaming to target filename.
  '''  # line 458
    if not actions:  # line 459
        return []  # line 459
    sources = None  # type: List[str]  # line 460
    targets = None  # type: List[str]  # line 460
    sources, targets = [list(l) for l in zip(*actions)]  # line 461
    last = len(actions)  # type: int  # line 462
    while last > 1:  # line 463
        clean = True  # type: bool  # line 464
        for i in range(1, last):  # line 465
            try:  # line 466
                index = targets[:i].index(sources[i])  # type: int  # line 467
                sources.insert(index, sources.pop(i))  # bubble up the action right before conflict  # line 468
                targets.insert(index, targets.pop(i))  # line 469
                clean = False  # line 470
            except:  # target not found in sources: good!  # line 471
                continue  # target not found in sources: good!  # line 471
        if clean:  # line 472
            break  # line 472
        last -= 1  # we know that the last entry in the list has the least conflicts, so we can disregard it in the next iteration  # line 473
    if exitOnConflict:  # line 474
        for i in range(1, len(actions)):  # line 475
            if sources[i] in targets[:i]:  # line 476
                Exit("There is no order of renaming actions that avoids copying over not-yet renamed files: '%s' is contained in matching source filenames" % (targets[i]))  # line 476
    return _coconut_tail_call(list, zip(sources, targets))  # line 477

def relativize(root: 'str', filepath: 'str') -> 'Tuple[str, str]':  # line 479
    ''' Determine OS-independent relative folder path, and relative pattern path. '''  # line 480
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(filepath)), root).replace(os.sep, SLASH)  # line 481
    return relpath, os.path.join(relpath, os.path.basename(filepath)).replace(os.sep, SLASH)  # line 482

def parseOnlyOptions(root: 'str', options: '_coconut.typing.Sequence[str]') -> 'Tuple[_coconut.typing.Optional[FrozenSet[str]], _coconut.typing.Optional[FrozenSet[str]]]':  # line 484
    ''' Returns set of --only arguments, and set or --except arguments. '''  # line 485
    cwd = os.getcwd()  # type: str  # line 486
    onlys = []  # type: List[str]  # line 487
    excps = []  # type: List[str]  # line 487
    index = 0  # type: int  # line 487
    while True:  # line 488
        try:  # line 489
            index = 1 + listindex(options, "--only", index)  # line 490
            onlys.append(options[index])  # line 491
        except:  # line 492
            break  # line 492
    index = 0  # line 493
    while True:  # line 494
        try:  # line 495
            index = 1 + listindex(options, "--except", index)  # line 496
            excps.append(options[index])  # line 497
        except:  # line 498
            break  # line 498
    return (frozenset((relativize(root, o)[1] for o in onlys)) if onlys else None, frozenset((relativize(root, e)[1] for e in excps)) if excps else None)  # line 499
