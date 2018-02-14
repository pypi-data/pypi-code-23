#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x21f720ec

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
UTF8 = "utf_8"  # early used constant, not defined in standard library  # line 54
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress"]  # line 55
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # line 56
GLOBAL_LISTS = ["ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # line 57
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # all lower-case normalized  # line 58
FALSE_VALUES = ["false", "no", "off", "0", "disable", "disabled"]  # line 59
PROGRESS_MARKER = ["|", "/", "-", "\\"]  # line 60
BACKUP_SUFFIX = "_last"  # line 61
metaFolder = ".sos"  # type: str  # line 62
metaFile = ".meta"  # type: str  # line 63
metaBack = metaFile + BACKUP_SUFFIX  # type: str  # line 64
bufSize = 1 << 20  # type: int  # 1 MiB  # line 65
SVN = "svn"  # line 66
SLASH = "/"  # line 67
MEBI = 1 << 20  # line 68
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": "fossil", "_FOSSIL_": "fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 69
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 70
NL_NAMES = {None: "<No newline>", b"\r\n": "<CR+LF>", b"\n\r": "<LF+CR>", b"\n": "<LF>", b"\r": "<CR>"}  # type: Dict[bytes, str]  # line 71
lateBinding = Accessor({"verbose": False, "start": 0})  # type: Accessor  # line 72


# Enums
MergeOperation = enum.Enum("MergeOperation", {"INSERT": 1, "REMOVE": 2, "BOTH": 3, "ASK": 4})  # insert remote changes into current, remove remote deletions from current, do both (replicates remote state), or ask per block  # line 76
MergeBlockType = enum.Enum("MergeBlockType", "KEEP INSERT REMOVE REPLACE MOVE")  # modify = intra-line changes, replace = full block replacement  # line 77


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("inSync", 'bool'), ("tracked", 'List[str]'), ("untracked", 'List[str]'), ("parent", '_coconut.typing.Optional[int]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 81
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 81
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 81
    def __new__(_cls, number, ctime, name=None, inSync=False, tracked=[], untracked=[], parent=None):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 81
        return _coconut.tuple.__new__(_cls, (number, ctime, name, inSync, tracked, untracked, parent))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 81
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 82
    __slots__ = ()  # line 82
    __ne__ = _coconut.object.__ne__  # line 82
    def __new__(_cls, number, ctime, message=None):  # line 82
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 82

class PathInfo(_coconut_NamedTuple("PathInfo", [("nameHash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", '_coconut.typing.Optional[str]')])):  # size == None means deleted in this revision  # line 83
    __slots__ = ()  # size == None means deleted in this revision  # line 83
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 83
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]'), ("moves", 'Dict[str, Tuple[str, PathInfo]]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 84
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 84
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 84
class Range(_coconut_NamedTuple("Range", [("tipe", 'MergeBlockType'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 85
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 85
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 85
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'MergeBlockType'), ("lines", 'List[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 86
    __slots__ = ()  # line 86
    __ne__ = _coconut.object.__ne__  # line 86
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 86
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 86

class GlobBlock(_coconut_NamedTuple("GlobBlock", [("isLiteral", 'bool'), ("content", 'str'), ("index", 'int')])):  # for file pattern rename/move matching  # line 87
    __slots__ = ()  # for file pattern rename/move matching  # line 87
    __ne__ = _coconut.object.__ne__  # for file pattern rename/move matching  # line 87
class GlobBlock2(_coconut_NamedTuple("GlobBlock2", [("isLiteral", 'bool'), ("content", 'str'), ("matches", 'str')])):  # matching file pattern and input filename for translation  # line 88
    __slots__ = ()  # matching file pattern and input filename for translation  # line 88
    __ne__ = _coconut.object.__ne__  # matching file pattern and input filename for translation  # line 88


# Functions
def printo(s: 'str', nl: 'str'="\n"):  # PEP528 compatibility  # line 92
    sys.stdout.buffer.write((s + nl).encode(sys.stdout.encoding, 'backslashreplace'))  # PEP528 compatibility  # line 92
    sys.stdout.flush()  # PEP528 compatibility  # line 92
def printe(s: 'str', nl: 'str'="\n"):  # line 93
    sys.stderr.buffer.write((s + nl).encode(sys.stderr.encoding, 'backslashreplace'))  # line 93
    sys.stderr.flush()  # line 93
@_coconut_tco  # for py->os access of writing filenames  # PEP 529 compatibility  # line 94
def encode(s: 'str') -> 'bytes':  # for py->os access of writing filenames  # PEP 529 compatibility  # line 94
    return _coconut_tail_call(os.fsencode, s)  # for py->os access of writing filenames  # PEP 529 compatibility  # line 94
@_coconut_tco  # for os->py access of reading filenames  # line 95
def decode(b: 'bytes') -> 'str':  # for os->py access of reading filenames  # line 95
    return _coconut_tail_call(os.fsdecode, b)  # for os->py access of reading filenames  # line 95
try:  # line 96
    import chardet  # https://github.com/chardet/chardet  # line 97
    def detectEncoding(binary: 'bytes') -> 'str':  # line 98
        return chardet.detect(binary)["encoding"]  # line 98
except:  # line 99
    def detectEncoding(binary: 'bytes') -> 'str':  # Guess the encoding  # line 100
        ''' Fallback if chardet library missing. '''  # line 101
        try:  # line 102
            binary.decode(UTF8)  # line 102
            return UTF8  # line 102
        except UnicodeError:  # line 103
            pass  # line 103
        try:  # line 104
            binary.decode("utf_16")  # line 104
            return "utf_16"  # line 104
        except UnicodeError:  # line 105
            pass  # line 105
        try:  # line 106
            binary.decode("cp1252")  # line 106
            return "cp1252"  # line 106
        except UnicodeError:  # line 107
            pass  # line 107
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 108

def tryOrDefault(func: '_coconut.typing.Callable[[], Any]', default: 'Any') -> 'Any':  # line 110
    try:  # line 111
        return func()  # line 111
    except:  # line 112
        return default  # line 112

def tryOrIgnore(func: '_coconut.typing.Callable[[], Any]') -> 'None':  # handle with care!  # line 114
    try:  # line 115
        func()  # line 115
    except:  # line 116
        pass  # line 116

@_coconut_tco  # line 118
def wcswidth(string: 'str') -> 'int':  # line 118
    l = 0  # type: int  # line 119
    try:  # line 120
        l = wcwidth.wcswitdh(string)  # line 121
        return len(string) if l < 0 else l  # line 122
    finally:  # line 123
        return _coconut_tail_call(len, string)  # line 123

def removePath(key: 'str', value: 'str') -> 'str':  # line 125
    ''' Cleanup of user-specified global file patterns. '''  # line 126
    return value if value in GLOBAL_LISTS or SLASH not in value else value[value.rindex(SLASH) + 1:]  # line 127

def conditionalIntersection(a: '_coconut.typing.Optional[FrozenSet[str]]', b: 'FrozenSet[str]') -> 'FrozenSet[str]':  # Used to match only arguments, or use only stored patterns  # line 129
    return a & b if a else b  # Used to match only arguments, or use only stored patterns  # line 129

def dictUpdate(dikt: 'Dict[Any, Any]', by: 'Dict[Any, Any]') -> 'Dict[Any, Any]':  # line 131
    d = {}  # line 131
    d.update(dikt)  # line 131
    d.update(by)  # line 131
    return d  # line 131

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO[bytes]':  # Abstraction for opening both compressed and plain files  # line 133
    return bz2.BZ2File(encode(file), mode) if compress else open(encode(file), mode + "b")  # Abstraction for opening both compressed and plain files  # line 133

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 135
    ''' Determine EOL style from a binary string. '''  # line 136
    lf = file.count(b"\n")  # type: int  # line 137
    cr = file.count(b"\r")  # type: int  # line 138
    crlf = file.count(b"\r\n")  # type: int  # line 139
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 140
        if lf != crlf or cr != crlf:  # line 141
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 141
        return b"\r\n"  # line 142
    if lf != 0 and cr != 0:  # line 143
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 143
    if lf > cr:  # Linux/Unix  # line 144
        return b"\n"  # Linux/Unix  # line 144
    if cr > lf:  # older 8-bit machines  # line 145
        return b"\r"  # older 8-bit machines  # line 145
    return None  # no new line contained, cannot determine  # line 146

try:  # line 148
    Splittable = TypeVar("Splittable", str, bytes)  # line 148
except:  # line 149
    pass  # line 149
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> 'List[Splittable]':  # line 150
    return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 150

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl: 'str'="") -> 'str':  # line 152
    return (sep + (nl + sep).join(seq)) if seq else ""  # line 152

@_coconut_tco  # line 154
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 154
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 154

@_coconut_tco  # line 156
def hashStr(datas: 'str') -> 'str':  # line 156
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 156

def modified(changes: 'ChangeSet', onlyBinary: 'bool'=False) -> 'bool':  # line 158
    return len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0 or len(changes.moves) > 0  # line 158

def listindex(lizt: 'Sequence[Any]', what: 'Any', index: 'int'=0) -> 'int':  # line 160
    return lizt[index:].index(what) + index  # line 160

def getTermWidth() -> 'int':  # line 162
    try:  # line 163
        import termwidth  # line 163
    except:  # line 164
        return 80  # line 164
    return termwidth.getTermWidth()[0]  # line 165

def branchFolder(branch: 'int', revision: 'int', base=".", file=None) -> 'str':  # line 167
    return os.path.join(base, metaFolder, "b%d" % branch, "r%d" % revision) + ((os.sep + file) if file else "")  # line 167

def Exit(message: 'str'="", code=1):  # line 169
    printe("[EXIT%s]" % (" %.1fs" % (time.time() - START_TIME) if verbose else "") + (" " + message + "." if message != "" else ""))  # line 169
    sys.exit(code)  # line 169

def exception(E):  # line 171
    ''' Report an exception. '''  # line 172
    printo(str(E))  # line 173
    import traceback  # line 174
    traceback.print_exc()  # line 175
    traceback.print_stack()  # line 176

def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None, callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None) -> 'Tuple[str, int]':  # line 178
    ''' Calculate hash of file contents, and return compressed sized, if in write mode, or zero. '''  # line 179
    indicator = ProgressIndicator(callback) if callback else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 180
    _hash = hashlib.sha256()  # line 181
    wsize = 0  # type: int  # line 182
    if saveTo and os.path.exists(encode(saveTo)):  # line 183
        Exit("Hash conflict. Leaving revision in inconsistent state. This should happen only once in a lifetime.")  # line 183
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 184
    with open(encode(path), "rb") as fd:  # line 185
        while True:  # line 186
            buffer = fd.read(bufSize)  # type: bytes  # line 187
            _hash.update(buffer)  # line 188
            if to:  # line 189
                to.write(buffer)  # line 189
            if len(buffer) < bufSize:  # line 190
                break  # line 190
            if indicator:  # line 191
                indicator.getIndicator()  # line 191
        if to:  # line 192
            to.close()  # line 193
            wsize = os.stat(encode(saveTo)).st_size  # line 194
    return (_hash.hexdigest(), wsize)  # line 195

def getAnyOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 197
    ''' Utility. '''  # line 198
    for k, v in map.items():  # line 199
        if k in params:  # line 200
            return v  # line 200
    return default  # line 201

@_coconut_tco  # line 203
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 203
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 203

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 205
    encoding = None  # type: str  # line 206
    eol = None  # type: _coconut.typing.Optional[bytes]  # line 206
    lines = []  # type: _coconut.typing.Sequence[str]  # line 206
    if filename is not None:  # line 207
        with open(encode(filename), "rb") as fd:  # line 208
            content = fd.read()  # line 208
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detectEncoding(content))  # line 209
    eol = eoldet(content)  # line 210
    if filename is not None:  # line 211
        with codecs.open(encode(filename), encoding=encoding) as fd2:  # line 212
            lines = safeSplit(fd2.read(), ((b"\n" if eol is None else eol)).decode(encoding))  # line 212
    elif content is not None:  # line 213
        lines = safeSplit(content.decode(encoding), ((b"\n" if eol is None else eol)).decode(encoding))  # line 214
    else:  # line 215
        return (sys.getdefaultencoding(), b"\n", [])  # line 215
    return (encoding, eol, lines)  # line 216

@_coconut_tco  # line 218
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, **_kwargs) -> 'DataType':  # line 218
    r = _old._asdict()  # line 218
    r.update(**_kwargs)  # line 218
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # line 218

def user_block_input(output: 'List[str]'):  # line 220
    sep = input("Enter end-of-text marker (default: <empty line>: ")  # type: str  # line 221
    line = sep  # type: str  # line 221
    while True:  # line 222
        line = input("> ")  # line 223
        if line == sep:  # line 224
            break  # line 224
        output.append(line)  # line 225

def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation: 'MergeOperation'=MergeOperation.BOTH, charMergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False, eol: 'bool'=False) -> 'Tuple[Union[bytes, List[MergeBlock]], _coconut.typing.Optional[bytes]]':  # line 227
    ''' Merges other binary text contents 'file' (or reads file 'filename') into current text contents 'into' (or reads file 'intoname'), returning merged result.
      For update, the other version is assumed to be the "new/added" one, while for diff, the current changes are the ones "added".
      However, change direction markers are insert ("+") for elements only in into, and remove ("-") for elements only in other file (just like the diff marks +/-)
      diffOnly returns detected change blocks only, no text merging
      eol flag will use the other file's EOL marks
      in case of replace block and INSERT strategy, the change will be added **behind** the original
  '''  # line 241
    encoding = None  # type: str  # line 242
    othr = None  # type: _coconut.typing.Sequence[str]  # line 242
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 242
    curr = None  # type: _coconut.typing.Sequence[str]  # line 242
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 242
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 243
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file)  # line 244
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into)  # line 245
    except Exception as E:  # line 246
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 246
    if None not in [othreol, curreol] and othreol != curreol:  # line 247
        warn("Differing EOL-styles detected during merge. Using current file's style for merged output")  # line 247
    output = list(difflib.Differ().compare(othr, curr))  # type: List[str]  # from generator expression  # line 248
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 249
    tmp = []  # type: List[str]  # block lines  # line 250
    last = " "  # type: str  # line 251
    no = None  # type: int  # line 251
    line = None  # type: str  # line 251
    for no, line in enumerate(output + ["X"]):  # EOF marker (difflib's output will never be "X" alone)  # line 252
        if line[0] == last:  # continue filling current block, no matter what type of block it is  # line 253
            tmp.append(line[2:])  # continue filling current block, no matter what type of block it is  # line 253
            continue  # continue filling current block, no matter what type of block it is  # line 253
        if line == "X" and len(tmp) == 0:  # break if nothing left to do, otherwise perform operation for stored block  # line 254
            break  # break if nothing left to do, otherwise perform operation for stored block  # line 254
        if last == " ":  # block is same in both files  # line 255
            if len(tmp) > 0:  # avoid adding empty keep block  # line 256
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # avoid adding empty keep block  # line 256
        elif last == "-":  # may be a pure deletion or part of a replacement (with next block being "+")  # line 257
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 258
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.INSERT:  # line 259
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp) - 1, replaces=blocks[-2])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 260
                blocks.pop()  # line 261
        elif last == "+":  # may be insertion or replacement (with previous - block)  # line 262
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # first, assume simple insertion, then check for replacement  # line 263
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.REMOVE:  #  and len(blocks[-1].lines) == len(blocks[-2].lines):  # requires previous block and same number of lines TODO allow multiple intra-line merge for same-length blocks  # line 264
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, line=no - len(tmp) - 1, replaces=blocks[-1])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 265
                blocks.pop()  # remove TOS due to merging two blocks into replace or modify  # line 266
        elif last == "?":  # marker for intra-line change comment -> add to block info  # line 267
            ilm = getIntraLineMarkers(tmp[0])  # type: Range  # TODO still true? "? " line includes a trailing \n for some reason  # line 268
            blocks[-1] = dataCopy(MergeBlock, blocks[-1], changes=ilm)  # line 269
        last = line[0]  # line 270
        tmp[:] = [line[2:]]  # only keep current line for next block  # line 271
# TODO add code to detect block moves here
    nl = othreol if eol else ((othreol if curreol is None else curreol))  # type: bytes  # no default newline, to mark "no newline"  # line 273
    debug("Diff blocks: " + repr(blocks))  # line 274
    if diffOnly:  # line 275
        return (blocks, nl)  # line 275

# now perform merge operations depending on detected blocks
    output[:] = []  # clean list of strings  # line 278
    for block in blocks:  # line 279
        if block.tipe == MergeBlockType.KEEP:  # line 280
            output.extend(block.lines)  # line 281
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value) or block.tipe == MergeBlockType.REMOVE and (mergeOperation.value & MergeOperation.INSERT.value):  # line 282
            output.extend(block.lines)  # line 284
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 285
            if len(block.lines) == len(block.replaces.lines) == 1:  # one-liner  # line 286
                output.append(lineMerge(block.lines[0], block.replaces.lines[0], mergeOperation=charMergeOperation))  # line 287
            elif mergeOperation == MergeOperation.ASK:  # more than one line: needs user input  # line 288
                printo(ajoin("- ", block.replaces.lines, nl="\n"))  # TODO check +/- in update mode, could be swapped  # line 289
                printo(ajoin("+ ", block.lines, nl="\n"))  # line 290
                while True:  # line 291
                    op = input(" Line replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 292
                    if op in "tb":  # line 293
                        output.extend(block.lines)  # line 293
                        break  # line 293
                    if op in "ib":  # line 294
                        output.extend(block.replaces.lines)  # line 294
                        break  # line 294
                    if op == "m":  # line 295
                        user_block_input(output)  # line 295
                        break  # line 295
            else:  # more than one line and not ask  # line 296
                if mergeOperation == MergeOperation.REMOVE:  # line 297
                    pass  # line 297
                elif mergeOperation == MergeOperation.BOTH:  # line 298
                    output.extend(block.lines)  # line 298
                elif mergeOperation == MergeOperation.INSERT:  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 299
                    output.extend(list(block.replaces.lines) + list(block.lines))  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 299
#  debug("Merge output: " + "; ".join(output))
    return (((b"\n" if nl is None else nl)).join([line.encode(encoding) for line in output]), nl)  # returning bytes  # line 301
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco  # line 304
def lineMerge(othr: 'str', into: 'str', mergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False) -> 'Union[str, List[MergeBlock]]':  # line 304
    ''' Merges string 'othr' into current string 'into'.
      change direction mark is insert for elements only in into, and remove for elements only in file (according to diff marks +/-)
  '''  # line 307
    out = list(difflib.Differ().compare(othr, into))  # type: List[str]  # line 308
    blocks = []  # type: List[MergeBlock]  # line 309
    for i, line in enumerate(out):  # line 310
        if line[0] == "+":  # line 311
            if i + 1 < len(out) and out[i + 1][0] == "+":  # block will continue  # line 312
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # middle of + block  # line 313
                    blocks[-1].lines.append(line[2])  # add one more character to the accumulating list  # line 314
                else:  # first + in block  # line 315
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 316
            else:  # last line of + block  # line 317
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # end of a block  # line 318
                    blocks[-1].lines.append(line[2])  # line 319
                else:  # single line  # line 320
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 321
                if i >= 1 and blocks[-2].tipe == MergeBlockType.REMOVE:  # previous - and now last in + block creates a replacement block  # line 322
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, i, replaces=blocks[-1])  # line 323
                    blocks.pop()  # line 323
        elif line[0] == "-":  # line 324
            if i > 0 and blocks[-1].tipe == MergeBlockType.REMOVE:  # part of - block  # line 325
                blocks[-1].lines.append(line[2])  # line 326
            else:  # first in block  # line 327
                blocks.append(MergeBlock(MergeBlockType.REMOVE, [line[2]], i))  # line 328
        elif line[0] == " ":  # line 329
            if i > 0 and blocks[-1].tipe == MergeBlockType.KEEP:  # part of block  # line 330
                blocks[-1].lines.append(line[2])  # line 331
            else:  # first in block  # line 332
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line[2]], i))  # line 333
        else:  # line 334
            raise Exception("Cannot parse diff line %r" % line)  # line 334
    blocks[:] = [dataCopy(MergeBlock, block, lines=["".join(block.lines)], replaces=dataCopy(MergeBlock, block.replaces, lines=["".join(block.replaces.lines)]) if block.replaces else None) for block in blocks]  # line 335
    if diffOnly:  # line 336
        return blocks  # line 336
    out[:] = []  # line 337
    for i, block in enumerate(blocks):  # line 338
        if block.tipe == MergeBlockType.KEEP:  # line 339
            out.extend(block.lines)  # line 339
        elif block.tipe == MergeBlockType.REPLACE:  # line 340
            if mergeOperation == MergeOperation.ASK:  # line 341
                printo(ajoin("- ", othr))  # line 342
                printo("- " + (" " * i) + block.replaces.lines[0])  # line 343
                printo("+ " + (" " * i) + block.lines[0])  # line 344
                printo(ajoin("+ ", into))  # line 345
                while True:  # line 346
                    op = input(" Character replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 347
                    if op in "tb":  # line 348
                        out.extend(block.lines)  # line 348
                        break  # line 348
                    if op in "ib":  # line 349
                        out.extend(block.replaces.lines)  # line 349
                        break  # line 349
                    if op == "m":  # line 350
                        user_block_input(out)  # line 350
                        break  # line 350
            else:  # non-interactive  # line 351
                if mergeOperation == MergeOperation.REMOVE:  # line 352
                    pass  # line 352
                elif mergeOperation == MergeOperation.BOTH:  # line 353
                    out.extend(block.lines)  # line 353
                elif mergeOperation == MergeOperation.INSERT:  # line 354
                    out.extend(list(block.replaces.lines) + list(block.lines))  # line 354
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value):  # line 355
            out.extend(block.lines)  # line 355
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation.value & MergeOperation.INSERT.value:  # line 356
            out.extend(block.lines)  # line 356
# TODO ask for insert or remove as well
    return _coconut_tail_call("".join, out)  # line 358

@_coconut_tco  # line 360
def getIntraLineMarkers(line: 'str') -> 'Range':  # line 360
    ''' Return (type, [affected indices]) of "? "-line diff markers ("? " prefix must be removed). difflib never returns mixed markers per line. '''  # line 361
    if "^" in line:  # TODO wrong, needs removal anyway  # line 362
        return _coconut_tail_call(Range, MergeBlockType.REPLACE, [i for i, c in enumerate(line) if c == "^"])  # TODO wrong, needs removal anyway  # line 362
    if "+" in line:  # line 363
        return _coconut_tail_call(Range, MergeBlockType.INSERT, [i for i, c in enumerate(line) if c == "+"])  # line 363
    if "-" in line:  # line 364
        return _coconut_tail_call(Range, MergeBlockType.REMOVE, [i for i, c in enumerate(line) if c == "-"])  # line 364
    return _coconut_tail_call(Range, MergeBlockType.KEEP, [])  # line 365

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 367
    ''' Attempts to find sos and legacy VCS base folders. '''  # line 368
    debug("Detecting root folders...")  # line 369
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 370
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 371
    while not os.path.exists(encode(os.path.join(path, metaFolder))):  # line 372
        contents = set(os.listdir(path))  # type: Set[str]  # line 373
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 374
        choice = None  # type: _coconut.typing.Optional[str]  # line 375
        if len(vcss) > 1:  # line 376
            choice = SVN if SVN in vcss else vcss[0]  # line 377
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 378
        elif len(vcss) > 0:  # line 379
            choice = vcss[0]  # line 379
        if not vcs[0] and choice:  # memorize current repo root  # line 380
            vcs = (path, choice)  # memorize current repo root  # line 380
        new = os.path.dirname(path)  # get parent path  # line 381
        if new == path:  # avoid infinite loop  # line 382
            break  # avoid infinite loop  # line 382
        path = new  # line 383
    if os.path.exists(encode(os.path.join(path, metaFolder))):  # found something  # line 384
        if vcs[0]:  # already detected vcs base and command  # line 385
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 385
        sos = path  # line 386
        while True:  # continue search for VCS base  # line 387
            new = os.path.dirname(path)  # get parent path  # line 388
            if new == path:  # no VCS folder found  # line 389
                return (sos, None, None)  # no VCS folder found  # line 389
            path = new  # line 390
            contents = set(os.listdir(path))  # line 391
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 392
            choice = None  # line 393
            if len(vcss) > 1:  # line 394
                choice = SVN if SVN in vcss else vcss[0]  # line 395
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 396
            elif len(vcss) > 0:  # line 397
                choice = vcss[0]  # line 397
            if choice:  # line 398
                return (sos, path, choice)  # line 398
    return (None, vcs[0], vcs[1])  # line 399

def tokenizeGlobPattern(pattern: 'str') -> 'List[GlobBlock]':  # line 401
    index = 0  # type: int  # line 402
    out = []  # type: List[GlobBlock]  # literal = True, first index  # line 403
    while index < len(pattern):  # line 404
        if pattern[index:index + 3] in ("[?]", "[*]", "[[]", "[]]"):  # line 405
            out.append(GlobBlock(False, pattern[index:index + 3], index))  # line 405
            continue  # line 405
        if pattern[index] in "*?":  # line 406
            count = 1  # type: int  # line 407
            while index + count < len(pattern) and pattern[index] == "?" and pattern[index + count] == "?":  # line 408
                count += 1  # line 408
            out.append(GlobBlock(False, pattern[index:index + count], index))  # line 409
            index += count  # line 409
            continue  # line 409
        if pattern[index:index + 2] == "[!":  # line 410
            out.append(GlobBlock(False, pattern[index:pattern.index("]", index + 2) + 1], index))  # line 410
            index += len(out[-1][1])  # line 410
            continue  # line 410
        count = 1  # line 411
        while index + count < len(pattern) and pattern[index + count] not in "*?[":  # line 412
            count += 1  # line 412
        out.append(GlobBlock(True, pattern[index:index + count], index))  # line 413
        index += count  # line 413
    return out  # line 414

def tokenizeGlobPatterns(oldPattern: 'str', newPattern: 'str') -> 'Tuple[_coconut.typing.Sequence[GlobBlock], _coconut.typing.Sequence[GlobBlock]]':  # line 416
    ot = tokenizeGlobPattern(oldPattern)  # type: List[GlobBlock]  # line 417
    nt = tokenizeGlobPattern(newPattern)  # type: List[GlobBlock]  # line 418
#  if len(ot) != len(nt): Exit("Source and target patterns can't be translated due to differing number of parsed glob markers and literal strings")
    if len([o for o in ot if not o.isLiteral]) < len([n for n in nt if not n.isLiteral]):  # line 420
        Exit("Source and target file patterns contain differing number of glob markers and can't be translated")  # line 420
    if any((O.content != N.content for O, N in zip([o for o in ot if not o.isLiteral], [n for n in nt if not n.isLiteral]))):  # line 421
        Exit("Source and target file patterns differ in semantics")  # line 421
    return (ot, nt)  # line 422

def convertGlobFiles(filenames: '_coconut.typing.Sequence[str]', oldPattern: '_coconut.typing.Sequence[GlobBlock]', newPattern: '_coconut.typing.Sequence[GlobBlock]') -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 424
    ''' Converts given filename according to specified file patterns. No support for adjacent glob markers currently. '''  # line 425
    pairs = []  # type: List[Tuple[str, str]]  # line 426
    for filename in filenames:  # line 427
        literals = [l for l in oldPattern if l.isLiteral]  # type: List[GlobBlock]  # source literals  # line 428
        nextliteral = 0  # type: int  # line 429
        parsedOld = []  # type: List[GlobBlock2]  # line 430
        index = 0  # type: int  # line 431
        for part in oldPattern:  # match everything in the old filename  # line 432
            if part.isLiteral:  # line 433
                parsedOld.append(GlobBlock2(True, part.content, part.content))  # line 433
                index += len(part.content)  # line 433
                nextliteral += 1  # line 433
            elif part.content.startswith("?"):  # line 434
                parsedOld.append(GlobBlock2(False, part.content, filename[index:index + len(part.content)]))  # line 434
                index += len(part.content)  # line 434
            elif part.content.startswith("["):  # line 435
                parsedOld.append(GlobBlock2(False, part.content, filename[index]))  # line 435
                index += 1  # line 435
            elif part.content == "*":  # line 436
                if nextliteral >= len(literals):  # line 437
                    parsedOld.append(GlobBlock2(False, part.content, filename[index:]))  # line 437
                    break  # line 437
                nxt = filename.index(literals[nextliteral].content, index)  # type: int  # also matches empty string  # line 438
                parsedOld.append(GlobBlock2(False, part.content, filename[index:nxt]))  # line 439
                index = nxt  # line 439
            else:  # line 440
                Exit("Invalid file pattern specified for move/rename")  # line 440
        globs = [g for g in parsedOld if not g.isLiteral]  # type: List[GlobBlock2]  # line 441
        literals = [l for l in newPattern if l.isLiteral]  # target literals  # line 442
        nextliteral = 0  # line 443
        nextglob = 0  # type: int  # line 443
        outname = []  # type: List[str]  # line 444
        for part in newPattern:  # generate new filename  # line 445
            if part.isLiteral:  # line 446
                outname.append(literals[nextliteral].content)  # line 446
                nextliteral += 1  # line 446
            else:  # line 447
                outname.append(globs[nextglob].matches)  # line 447
                nextglob += 1  # line 447
        pairs.append((filename, "".join(outname)))  # line 448
    return pairs  # line 449

@_coconut_tco  # line 451
def reorderRenameActions(actions: '_coconut.typing.Sequence[Tuple[str, str]]', exitOnConflict: 'bool'=True) -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 451
    ''' Attempt to put all rename actions into an order that avoids target == source names.
      Note, that it's currently not really possible to specify patterns that make this work (swapping "*" elements with a reference).
      An alternative would be to always have one (or all) files renamed to a temporary name before renaming to target filename.
  '''  # line 455
    if not actions:  # line 456
        return []  # line 456
    sources = None  # type: List[str]  # line 457
    targets = None  # type: List[str]  # line 457
    sources, targets = [list(l) for l in zip(*actions)]  # line 458
    last = len(actions)  # type: int  # line 459
    while last > 1:  # line 460
        clean = True  # type: bool  # line 461
        for i in range(1, last):  # line 462
            try:  # line 463
                index = targets[:i].index(sources[i])  # type: int  # line 464
                sources.insert(index, sources.pop(i))  # bubble up the action right before conflict  # line 465
                targets.insert(index, targets.pop(i))  # line 466
                clean = False  # line 467
            except:  # target not found in sources: good!  # line 468
                continue  # target not found in sources: good!  # line 468
        if clean:  # line 469
            break  # line 469
        last -= 1  # we know that the last entry in the list has the least conflicts, so we can disregard it in the next iteration  # line 470
    if exitOnConflict:  # line 471
        for i in range(1, len(actions)):  # line 472
            if sources[i] in targets[:i]:  # line 473
                Exit("There is no order of renaming actions that avoids copying over not-yet renamed files: '%s' is contained in matching source filenames" % (targets[i]))  # line 473
    return _coconut_tail_call(list, zip(sources, targets))  # line 474

def relativize(root: 'str', filepath: 'str') -> 'Tuple[str, str]':  # line 476
    ''' Determine OS-independent relative folder path, and relative pattern path. '''  # line 477
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(filepath)), root).replace(os.sep, SLASH)  # line 478
    return relpath, os.path.join(relpath, os.path.basename(filepath)).replace(os.sep, SLASH)  # line 479

def parseOnlyOptions(root: 'str', options: '_coconut.typing.Sequence[str]') -> 'Tuple[_coconut.typing.Optional[FrozenSet[str]], _coconut.typing.Optional[FrozenSet[str]]]':  # line 481
    ''' Returns set of --only arguments, and set or --except arguments. '''  # line 482
    cwd = os.getcwd()  # type: str  # line 483
    onlys = []  # type: List[str]  # line 484
    excps = []  # type: List[str]  # line 484
    index = 0  # type: int  # line 484
    while True:  # line 485
        try:  # line 486
            index = 1 + listindex(options, "--only", index)  # line 487
            onlys.append(options[index])  # line 488
        except:  # line 489
            break  # line 489
    index = 0  # line 490
    while True:  # line 491
        try:  # line 492
            index = 1 + listindex(options, "--except", index)  # line 493
            excps.append(options[index])  # line 494
        except:  # line 495
            break  # line 495
    return (frozenset((relativize(root, o)[1] for o in onlys)) if onlys else None, frozenset((relativize(root, e)[1] for e in excps)) if excps else None)  # line 496
