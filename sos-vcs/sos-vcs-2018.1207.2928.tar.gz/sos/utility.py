#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xf6664e10

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
try:  # line 8
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

class Logger:  # line 32
    ''' Logger that supports many items. '''  # line 33
    def __init__(_, log):  # line 34
        _._log = log  # line 34
    def debug(_, *s):  # line 35
        _._log.debug(sjoin(*s))  # line 35
    def info(_, *s):  # line 36
        _._log.info(sjoin(*s))  # line 36
    def warn(_, *s):  # line 37
        _._log.warning(sjoin(*s))  # line 37
    def error(_, *s):  # line 38
        _._log.error(sjoin(*s))  # line 38


# Constants
_log = Logger(logging.getLogger(__name__))  # line 42
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 42
UTF8 = "utf_8"  # early used constant, not defined in standard library  # line 43
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress"]  # line 44
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # line 45
GLOBAL_LISTS = ["ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # line 46
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # all lower-case normalized  # line 47
FALSE_VALUES = ["false", "no", "off", "0", "disable", "disabled"]  # line 48
PROGRESS_MARKER = ["|", "/", "-", "\\"]  # line 49
metaFolder = ".sos"  # type: str  # line 50
metaFile = ".meta"  # type: str  # line 51
bufSize = 1 << 20  # type: int  # 1 MiB  # line 52
SVN = "svn"  # line 53
SLASH = "/"  # line 54
MEBI = 1 << 20  # line 55
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": "fossil", "_FOSSIL_": "fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 56
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 57
lateBinding = Accessor({"verbose": False, "start": 0})  # type: Accessor  # line 58


# Enums
MergeOperation = enum.Enum("MergeOperation", {"INSERT": 1, "REMOVE": 2, "BOTH": 3, "ASK": 4})  # insert remote changes into current, remove remote deletions from current, do both (replicates remote state), or ask per block  # line 62
MergeBlockType = enum.Enum("MergeBlockType", "KEEP INSERT REMOVE REPLACE MOVE")  # modify = intra-line changes, replace = full block replacement  # line 63


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("inSync", 'bool'), ("tracked", 'List[str]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 67
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 67
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 67
    def __new__(_cls, number, ctime, name=None, inSync=False, tracked=[]):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 67
        return _coconut.tuple.__new__(_cls, (number, ctime, name, inSync, tracked))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 67
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 68
    __slots__ = ()  # line 68
    __ne__ = _coconut.object.__ne__  # line 68
    def __new__(_cls, number, ctime, message=None):  # line 68
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 68

class PathInfo(_coconut_NamedTuple("PathInfo", [("nameHash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", '_coconut.typing.Optional[str]')])):  # size == None means deleted in this revision  # line 69
    __slots__ = ()  # size == None means deleted in this revision  # line 69
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 69
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 70
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 70
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 70
class Range(_coconut_NamedTuple("Range", [("tipe", 'MergeBlockType'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 71
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 71
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 71
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'MergeBlockType'), ("lines", 'List[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 72
    __slots__ = ()  # line 72
    __ne__ = _coconut.object.__ne__  # line 72
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 72
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 72

class GlobBlock(_coconut_NamedTuple("GlobBlock", [("isLiteral", 'bool'), ("content", 'str'), ("index", 'int')])):  # for file pattern rename/move matching  # line 73
    __slots__ = ()  # for file pattern rename/move matching  # line 73
    __ne__ = _coconut.object.__ne__  # for file pattern rename/move matching  # line 73
class GlobBlock2(_coconut_NamedTuple("GlobBlock2", [("isLiteral", 'bool'), ("content", 'str'), ("matches", 'str')])):  # matching file pattern and input filename for translation  # line 74
    __slots__ = ()  # matching file pattern and input filename for translation  # line 74
    __ne__ = _coconut.object.__ne__  # matching file pattern and input filename for translation  # line 74


# Functions
def printo(s: 'str', nl: 'str'="\n"):  # PEP528 compatibility  # line 78
    sys.stdout.buffer.write((s + nl).encode(sys.stdout.encoding, 'backslashreplace'))  # PEP528 compatibility  # line 78
    sys.stdout.flush()  # PEP528 compatibility  # line 78
def printe(s: 'str', nl: 'str'="\n"):  # line 79
    sys.stderr.buffer.write((s + nl).encode(sys.stderr.encoding, 'backslashreplace'))  # line 79
    sys.stderr.flush()  # line 79
@_coconut_tco  # for py->os access of writing filenames  # PEP 529 compatibility  # line 80
def encode(s: 'str') -> 'bytes':  # for py->os access of writing filenames  # PEP 529 compatibility  # line 80
    return _coconut_tail_call(os.fsencode, s)  # for py->os access of writing filenames  # PEP 529 compatibility  # line 80
@_coconut_tco  # for os->py access of reading filenames  # line 81
def decode(b: 'bytes') -> 'str':  # for os->py access of reading filenames  # line 81
    return _coconut_tail_call(os.fsdecode, b)  # for os->py access of reading filenames  # line 81
try:  # line 82
    import chardet  # https://github.com/chardet/chardet  # line 83
    def detectEncoding(binary: 'bytes') -> 'str':  # line 84
        return chardet.detect(binary)["encoding"]  # line 84
except:  # line 85
    def detectEncoding(binary: 'bytes') -> 'str':  # Guess the encoding  # line 86
        ''' Fallback if chardet library missing. '''  # line 87
        try:  # line 88
            binary.decode(UTF8)  # line 88
            return UTF8  # line 88
        except UnicodeError:  # line 89
            pass  # line 89
        try:  # line 90
            binary.decode("utf_16")  # line 90
            return "utf_16"  # line 90
        except UnicodeError:  # line 91
            pass  # line 91
        try:  # line 92
            binary.decode("cp1252")  # line 92
            return "cp1252"  # line 92
        except UnicodeError:  # line 93
            pass  # line 93
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 94

@_coconut_tco  # line 96
def wcswidth(string: 'str') -> 'int':  # line 96
    l = 0  # type: int  # line 97
    try:  # line 98
        l = wcwidth.wcswitdh(string)  # line 99
        return len(string) if l < 0 else l  # line 100
    finally:  # line 101
        return _coconut_tail_call(len, string)  # line 101

def removePath(key: 'str', value: 'str') -> 'str':  # line 103
    ''' Cleanup of user-specified global file patterns. '''  # line 104
    return value if value in GLOBAL_LISTS or SLASH not in value else value[value.rindex(SLASH) + 1:]  # line 105

def conditionalIntersection(a: '_coconut.typing.Optional[FrozenSet[str]]', b: 'FrozenSet[str]') -> 'FrozenSet[str]':  # line 107
    return a & b if a else b  # line 107

def dictUpdate(dikt: 'Dict[Any, Any]', by: 'Dict[Any, Any]') -> 'Dict[Any, Any]':  # line 109
    d = {}  # line 109
    d.update(dikt)  # line 109
    d.update(by)  # line 109
    return d  # line 109

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO[bytes]':  # Abstraction for opening both compressed and plain files  # line 111
    return bz2.BZ2File(encode(file), mode) if compress else open(encode(file), mode + "b")  # Abstraction for opening both compressed and plain files  # line 111

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 113
    ''' Determine EOL style from a binary string. '''  # line 114
    lf = file.count(b"\n")  # type: int  # line 115
    cr = file.count(b"\r")  # type: int  # line 116
    crlf = file.count(b"\r\n")  # type: int  # line 117
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 118
        if lf != crlf or cr != crlf:  # line 119
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 119
        return b"\r\n"  # line 120
    if lf != 0 and cr != 0:  # line 121
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 121
    if lf > cr:  # Linux/Unix  # line 122
        return b"\n"  # Linux/Unix  # line 122
    if cr > lf:  # older 8-bit machines  # line 123
        return b"\r"  # older 8-bit machines  # line 123
    return None  # no new line contained, cannot determine  # line 124

try:  # line 126
    Splittable = TypeVar("Splittable", str, bytes)  # line 126
except:  # line 127
    pass  # line 127
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> 'List[Splittable]':  # line 128
    return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 128

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl: 'str'="") -> 'str':  # line 130
    return (sep + (nl + sep).join(seq)) if seq else ""  # line 130

@_coconut_tco  # line 132
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 132
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 132

@_coconut_tco  # line 134
def hashStr(datas: 'str') -> 'str':  # line 134
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 134

def modified(changes: 'ChangeSet', onlyBinary: 'bool'=False) -> 'bool':  # line 136
    return len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0  # line 136

def listindex(lizt: 'Sequence[Any]', what: 'Any', index: 'int'=0) -> 'int':  # line 138
    return lizt[index:].index(what) + index  # line 138

def getTermWidth() -> 'int':  # line 140
    try:  # line 141
        import termwidth  # line 141
    except:  # line 142
        return 80  # line 142
    return termwidth.getTermWidth()[0]  # line 143

def branchFolder(branch: 'int', revision: 'int', base=".", file=None) -> 'str':  # line 145
    return os.path.join(base, metaFolder, "b%d" % branch, "r%d" % revision) + ((os.sep + file) if file else "")  # line 145

def Exit(message: 'str'="", code=1):  # line 147
    printe("[EXIT%s]" % (" %.1fs" % (time.time() - START_TIME) if verbose else "") + (" " + message + "." if message != "" else ""))  # line 147
    sys.exit(code)  # line 147

def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None) -> 'Tuple[str, int]':  # line 149
    ''' Calculate hash of file contents, and return compressed sized, if in write mode, or zero. '''  # line 150
    _hash = hashlib.sha256()  # line 151
    wsize = 0  # type: int  # line 152
    if saveTo and os.path.exists(encode(saveTo)):  # line 153
        Exit("Hash conflict. Leaving revision in inconsistent state. This should happen only once in a lifetime.")  # line 153
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 154
    with open(encode(path), "rb") as fd:  # line 155
        while True:  # line 156
            buffer = fd.read(bufSize)  # type: bytes  # line 157
            _hash.update(buffer)  # line 158
            if to:  # line 159
                to.write(buffer)  # line 159
            if len(buffer) < bufSize:  # line 160
                break  # line 160
        if to:  # line 161
            to.close()  # line 162
            wsize = os.stat(encode(saveTo)).st_size  # line 163
    return (_hash.hexdigest(), wsize)  # line 164

def getAnyOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 166
    ''' Utility. '''  # line 167
    for k, v in map.items():  # line 168
        if k in params:  # line 169
            return v  # line 169
    return default  # line 170

@_coconut_tco  # line 172
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 172
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 172

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 174
    encoding = None  # type: str  # line 175
    eol = None  # type: bytes  # line 175
    lines = []  # type: _coconut.typing.Sequence[str]  # line 175
    if filename is not None:  # line 176
        with open(encode(filename), "rb") as fd:  # line 177
            content = fd.read()  # line 177
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detectEncoding(content))  # line 178
    eol = eoldet(content)  # line 179
    if filename is not None:  # line 180
        with codecs.open(encode(filename), encoding=encoding) as fd2:  # line 181
            lines = safeSplit(fd2.read(), ((b"\n" if eol is None else eol)).decode(encoding))  # line 181
    elif content is not None:  # line 182
        lines = safeSplit(content.decode(encoding), ((b"\n" if eol is None else eol)).decode(encoding))  # line 183
    else:  # line 184
        return (sys.getdefaultencoding(), b"\n", [])  # line 184
    return (encoding, eol, lines)  # line 185

@_coconut_tco  # line 187
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, **_kwargs) -> 'DataType':  # line 187
    r = _old._asdict()  # line 187
    r.update(**_kwargs)  # line 187
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # line 187

def user_block_input(output: 'List[str]'):  # line 189
    sep = input("Enter end-of-text marker (default: <empty line>: ")  # type: str  # line 190
    line = sep  # type: str  # line 190
    while True:  # line 191
        line = input("> ")  # line 192
        if line == sep:  # line 193
            break  # line 193
        output.append(line)  # line 194

@_coconut_tco  # line 196
def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation: 'MergeOperation'=MergeOperation.BOTH, charMergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False, eol: 'bool'=False) -> 'Union[bytes, List[MergeBlock]]':  # line 196
    ''' Merges other binary text contents 'file' (or reads file 'filename') into current text contents 'into' (or reads file 'intoname'), returning merged result.
      For update, the other version is assumed to be the "new/added" one, while for diff, the current changes are the ones "added".
      However, change direction markers are insert ("+") for elements only in into, and remove ("-") for elements only in other file (just like the diff marks +/-)
      diffOnly returns detected change blocks only, no text merging
      eol flag will use the other file's EOL marks
      in case of replace block and INSERT strategy, the change will be added **behind** the original
  '''  # line 210
    encoding = None  # type: str  # line 211
    othr = None  # type: _coconut.typing.Sequence[str]  # line 211
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 211
    curr = None  # type: _coconut.typing.Sequence[str]  # line 211
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 211
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 212
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file)  # line 213
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into)  # line 214
    except Exception as E:  # line 215
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 215
    if None not in [othreol, curreol] and othreol != curreol:  # line 216
        warn("Differing EOL-styles detected during merge. Using current file's style for merged output")  # line 216
    output = list(difflib.Differ().compare(othr, curr))  # type: List[str]  # from generator expression  # line 217
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 218
    tmp = []  # type: List[str]  # block lines  # line 219
    last = " "  # type: str  # line 220
    no = None  # type: int  # line 220
    line = None  # type: str  # line 220
    for no, line in enumerate(output + ["X"]):  # EOF marker (difflib's output will never be "X" alone)  # line 221
        if line[0] == last:  # continue filling current block, no matter what type of block it is  # line 222
            tmp.append(line[2:])  # continue filling current block, no matter what type of block it is  # line 222
            continue  # continue filling current block, no matter what type of block it is  # line 222
        if line == "X" and len(tmp) == 0:  # break if nothing left to do, otherwise perform operation for stored block  # line 223
            break  # break if nothing left to do, otherwise perform operation for stored block  # line 223
        if last == " ":  # block is same in both files  # line 224
            if len(tmp) > 0:  # avoid adding empty keep block  # line 225
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # avoid adding empty keep block  # line 225
        elif last == "-":  # may be a pure deletion or part of a replacement (with next block being "+")  # line 226
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 227
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.INSERT:  # line 228
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp) - 1, replaces=blocks[-2])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 229
                blocks.pop()  # line 230
        elif last == "+":  # may be insertion or replacement (with previous - block)  # line 231
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # first, assume simple insertion, then check for replacement  # line 232
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.REMOVE:  #  and len(blocks[-1].lines) == len(blocks[-2].lines):  # requires previous block and same number of lines TODO allow multiple intra-line merge for same-length blocks  # line 233
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, line=no - len(tmp) - 1, replaces=blocks[-1])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 234
                blocks.pop()  # remove TOS due to merging two blocks into replace or modify  # line 235
        elif last == "?":  # marker for intra-line change comment -> add to block info  # line 236
            ilm = getIntraLineMarkers(tmp[0])  # type: Range  # TODO still true? "? " line includes a trailing \n for some reason  # line 237
            blocks[-1] = dataCopy(MergeBlock, blocks[-1], changes=ilm)  # line 238
        last = line[0]  # line 239
        tmp[:] = [line[2:]]  # only keep current line for next block  # line 240
# TODO add code to detect block moves here
    debug("Diff blocks: " + repr(blocks))  # line 242
    if diffOnly:  # line 243
        return blocks  # line 243

# now perform merge operations depending on detected blocks
    output[:] = []  # clean list of strings  # line 246
    for block in blocks:  # line 247
        if block.tipe == MergeBlockType.KEEP:  # line 248
            output.extend(block.lines)  # line 249
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value) or block.tipe == MergeBlockType.REMOVE and (mergeOperation.value & MergeOperation.INSERT.value):  # line 250
            output.extend(block.lines)  # line 252
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 253
            if len(block.lines) == len(block.replaces.lines) == 1:  # one-liner  # line 254
                output.append(lineMerge(block.lines[0], block.replaces.lines[0], mergeOperation=charMergeOperation))  # line 255
            elif mergeOperation == MergeOperation.ASK:  # more than one line: needs user input  # line 256
                printo(ajoin("- ", block.replaces.lines, nl="\n"))  # TODO check +/- in update mode, could be swapped  # line 257
                printo(ajoin("+ ", block.lines, nl="\n"))  # line 258
                while True:  # line 259
                    op = input(" Line replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 260
                    if op in "tb":  # line 261
                        output.extend(block.lines)  # line 261
                        break  # line 261
                    if op in "ib":  # line 262
                        output.extend(block.replaces.lines)  # line 262
                        break  # line 262
                    if op == "m":  # line 263
                        user_block_input(output)  # line 263
                        break  # line 263
            else:  # more than one line and not ask  # line 264
                if mergeOperation == MergeOperation.REMOVE:  # line 265
                    pass  # line 265
                elif mergeOperation == MergeOperation.BOTH:  # line 266
                    output.extend(block.lines)  # line 266
                elif mergeOperation == MergeOperation.INSERT:  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 267
                    output.extend(list(block.replaces.lines) + list(block.lines))  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 267
#  debug("Merge output: " + "; ".join(output))
    nl = othreol if eol else (((b"\n" if othreol is None else othreol) if curreol is None else curreol))  # type: bytes  # line 269
    return _coconut_tail_call(nl.join, [line.encode(encoding) for line in output])  # returning bytes  # line 270
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco  # line 273
def lineMerge(othr: 'str', into: 'str', mergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False) -> 'Union[str, List[MergeBlock]]':  # line 273
    ''' Merges string 'othr' into current string 'into'.
      change direction mark is insert for elements only in into, and remove for elements only in file (according to diff marks +/-)
  '''  # line 276
    out = list(difflib.Differ().compare(othr, into))  # type: List[str]  # line 277
    blocks = []  # type: List[MergeBlock]  # line 278
    for i, line in enumerate(out):  # line 279
        if line[0] == "+":  # line 280
            if i + 1 < len(out) and out[i + 1][0] == "+":  # block will continue  # line 281
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # middle of + block  # line 282
                    blocks[-1].lines.append(line[2])  # add one more character to the accumulating list  # line 283
                else:  # first + in block  # line 284
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 285
            else:  # last line of + block  # line 286
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # end of a block  # line 287
                    blocks[-1].lines.append(line[2])  # line 288
                else:  # single line  # line 289
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 290
                if i >= 1 and blocks[-2].tipe == MergeBlockType.REMOVE:  # previous - and now last in + block creates a replacement block  # line 291
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, i, replaces=blocks[-1])  # line 292
                    blocks.pop()  # line 292
        elif line[0] == "-":  # line 293
            if i > 0 and blocks[-1].tipe == MergeBlockType.REMOVE:  # part of - block  # line 294
                blocks[-1].lines.append(line[2])  # line 295
            else:  # first in block  # line 296
                blocks.append(MergeBlock(MergeBlockType.REMOVE, [line[2]], i))  # line 297
        elif line[0] == " ":  # line 298
            if i > 0 and blocks[-1].tipe == MergeBlockType.KEEP:  # part of block  # line 299
                blocks[-1].lines.append(line[2])  # line 300
            else:  # first in block  # line 301
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line[2]], i))  # line 302
        else:  # line 303
            raise Exception("Cannot parse diff line %r" % line)  # line 303
    blocks[:] = [dataCopy(MergeBlock, block, lines=["".join(block.lines)], replaces=dataCopy(MergeBlock, block.replaces, lines=["".join(block.replaces.lines)]) if block.replaces else None) for block in blocks]  # line 304
    if diffOnly:  # line 305
        return blocks  # line 305
    out[:] = []  # line 306
    for i, block in enumerate(blocks):  # line 307
        if block.tipe == MergeBlockType.KEEP:  # line 308
            out.extend(block.lines)  # line 308
        elif block.tipe == MergeBlockType.REPLACE:  # line 309
            if mergeOperation == MergeOperation.ASK:  # line 310
                printo(ajoin("- ", othr))  # line 311
                printo("- " + (" " * i) + block.replaces.lines[0])  # line 312
                printo("+ " + (" " * i) + block.lines[0])  # line 313
                printo(ajoin("+ ", into))  # line 314
                while True:  # line 315
                    op = input(" Character replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 316
                    if op in "tb":  # line 317
                        out.extend(block.lines)  # line 317
                        break  # line 317
                    if op in "ib":  # line 318
                        out.extend(block.replaces.lines)  # line 318
                        break  # line 318
                    if op == "m":  # line 319
                        user_block_input(out)  # line 319
                        break  # line 319
            else:  # non-interactive  # line 320
                if mergeOperation == MergeOperation.REMOVE:  # line 321
                    pass  # line 321
                elif mergeOperation == MergeOperation.BOTH:  # line 322
                    out.extend(block.lines)  # line 322
                elif mergeOperation == MergeOperation.INSERT:  # line 323
                    out.extend(list(block.replaces.lines) + list(block.lines))  # line 323
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value):  # line 324
            out.extend(block.lines)  # line 324
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation.value & MergeOperation.INSERT.value:  # line 325
            out.extend(block.lines)  # line 325
# TODO ask for insert or remove as well
    return _coconut_tail_call("".join, out)  # line 327

@_coconut_tco  # line 329
def getIntraLineMarkers(line: 'str') -> 'Range':  # line 329
    ''' Return (type, [affected indices]) of "? "-line diff markers ("? " prefix must be removed). difflib never returns mixed markers per line. '''  # line 330
    if "^" in line:  # TODO wrong, needs removal anyway  # line 331
        return _coconut_tail_call(Range, MergeBlockType.REPLACE, [i for i, c in enumerate(line) if c == "^"])  # TODO wrong, needs removal anyway  # line 331
    if "+" in line:  # line 332
        return _coconut_tail_call(Range, MergeBlockType.INSERT, [i for i, c in enumerate(line) if c == "+"])  # line 332
    if "-" in line:  # line 333
        return _coconut_tail_call(Range, MergeBlockType.REMOVE, [i for i, c in enumerate(line) if c == "-"])  # line 333
    return _coconut_tail_call(Range, MergeBlockType.KEEP, [])  # line 334

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 336
    ''' Attempts to find sos and legacy VCS base folders. '''  # line 337
    debug("Detecting root folders...")  # line 338
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 339
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 340
    while not os.path.exists(encode(os.path.join(path, metaFolder))):  # line 341
        contents = set(os.listdir(path))  # type: Set[str]  # line 342
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 343
        choice = None  # type: _coconut.typing.Optional[str]  # line 344
        if len(vcss) > 1:  # line 345
            choice = SVN if SVN in vcss else vcss[0]  # line 346
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 347
        elif len(vcss) > 0:  # line 348
            choice = vcss[0]  # line 348
        if not vcs[0] and choice:  # memorize current repo root  # line 349
            vcs = (path, choice)  # memorize current repo root  # line 349
        new = os.path.dirname(path)  # get parent path  # line 350
        if new == path:  # avoid infinite loop  # line 351
            break  # avoid infinite loop  # line 351
        path = new  # line 352
    if os.path.exists(encode(os.path.join(path, metaFolder))):  # found something  # line 353
        if vcs[0]:  # already detected vcs base and command  # line 354
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 354
        sos = path  # line 355
        while True:  # continue search for VCS base  # line 356
            new = os.path.dirname(path)  # get parent path  # line 357
            if new == path:  # no VCS folder found  # line 358
                return (sos, None, None)  # no VCS folder found  # line 358
            path = new  # line 359
            contents = set(os.listdir(path))  # line 360
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 361
            choice = None  # line 362
            if len(vcss) > 1:  # line 363
                choice = SVN if SVN in vcss else vcss[0]  # line 364
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 365
            elif len(vcss) > 0:  # line 366
                choice = vcss[0]  # line 366
            if choice:  # line 367
                return (sos, path, choice)  # line 367
    return (None, vcs[0], vcs[1])  # line 368

def tokenizeGlobPattern(pattern: 'str') -> 'List[GlobBlock]':  # line 370
    index = 0  # type: int  # line 371
    out = []  # type: List[GlobBlock]  # literal = True, first index  # line 372
    while index < len(pattern):  # line 373
        if pattern[index:index + 3] in ("[?]", "[*]", "[[]", "[]]"):  # line 374
            out.append(GlobBlock(False, pattern[index:index + 3], index))  # line 374
            continue  # line 374
        if pattern[index] in "*?":  # line 375
            count = 1  # type: int  # line 376
            while index + count < len(pattern) and pattern[index] == "?" and pattern[index + count] == "?":  # line 377
                count += 1  # line 377
            out.append(GlobBlock(False, pattern[index:index + count], index))  # line 378
            index += count  # line 378
            continue  # line 378
        if pattern[index:index + 2] == "[!":  # line 379
            out.append(GlobBlock(False, pattern[index:pattern.index("]", index + 2) + 1], index))  # line 379
            index += len(out[-1][1])  # line 379
            continue  # line 379
        count = 1  # line 380
        while index + count < len(pattern) and pattern[index + count] not in "*?[":  # line 381
            count += 1  # line 381
        out.append(GlobBlock(True, pattern[index:index + count], index))  # line 382
        index += count  # line 382
    return out  # line 383

def tokenizeGlobPatterns(oldPattern: 'str', newPattern: 'str') -> 'Tuple[_coconut.typing.Sequence[GlobBlock], _coconut.typing.Sequence[GlobBlock]]':  # line 385
    ot = tokenizeGlobPattern(oldPattern)  # type: List[GlobBlock]  # line 386
    nt = tokenizeGlobPattern(newPattern)  # type: List[GlobBlock]  # line 387
#  if len(ot) != len(nt): Exit("Source and target patterns can't be translated due to differing number of parsed glob markers and literal strings")
    if len([o for o in ot if not o.isLiteral]) < len([n for n in nt if not n.isLiteral]):  # line 389
        Exit("Source and target file patterns contain differing number of glob markers and can't be translated")  # line 389
    if any((O.content != N.content for O, N in zip([o for o in ot if not o.isLiteral], [n for n in nt if not n.isLiteral]))):  # line 390
        Exit("Source and target file patterns differ in semantics")  # line 390
    return (ot, nt)  # line 391

def convertGlobFiles(filenames: '_coconut.typing.Sequence[str]', oldPattern: '_coconut.typing.Sequence[GlobBlock]', newPattern: '_coconut.typing.Sequence[GlobBlock]') -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 393
    ''' Converts given filename according to specified file patterns. No support for adjacent glob markers currently. '''  # line 394
    pairs = []  # type: List[Tuple[str, str]]  # line 395
    for filename in filenames:  # line 396
        literals = [l for l in oldPattern if l.isLiteral]  # type: List[GlobBlock]  # source literals  # line 397
        nextliteral = 0  # type: int  # line 398
        parsedOld = []  # type: List[GlobBlock2]  # line 399
        index = 0  # type: int  # line 400
        for part in oldPattern:  # match everything in the old filename  # line 401
            if part.isLiteral:  # line 402
                parsedOld.append(GlobBlock2(True, part.content, part.content))  # line 402
                index += len(part.content)  # line 402
                nextliteral += 1  # line 402
            elif part.content.startswith("?"):  # line 403
                parsedOld.append(GlobBlock2(False, part.content, filename[index:index + len(part.content)]))  # line 403
                index += len(part.content)  # line 403
            elif part.content.startswith("["):  # line 404
                parsedOld.append(GlobBlock2(False, part.content, filename[index]))  # line 404
                index += 1  # line 404
            elif part.content == "*":  # line 405
                if nextliteral >= len(literals):  # line 406
                    parsedOld.append(GlobBlock2(False, part.content, filename[index:]))  # line 406
                    break  # line 406
                nxt = filename.index(literals[nextliteral].content, index)  # type: int  # also matches empty string  # line 407
                parsedOld.append(GlobBlock2(False, part.content, filename[index:nxt]))  # line 408
                index = nxt  # line 408
            else:  # line 409
                Exit("Invalid file pattern specified for move/rename")  # line 409
        globs = [g for g in parsedOld if not g.isLiteral]  # type: List[GlobBlock2]  # line 410
        literals = [l for l in newPattern if l.isLiteral]  # target literals  # line 411
        nextliteral = 0  # line 412
        nextglob = 0  # type: int  # line 412
        outname = []  # type: List[str]  # line 413
        for part in newPattern:  # generate new filename  # line 414
            if part.isLiteral:  # line 415
                outname.append(literals[nextliteral].content)  # line 415
                nextliteral += 1  # line 415
            else:  # line 416
                outname.append(globs[nextglob].matches)  # line 416
                nextglob += 1  # line 416
        pairs.append((filename, "".join(outname)))  # line 417
    return pairs  # line 418

@_coconut_tco  # line 420
def reorderRenameActions(actions: '_coconut.typing.Sequence[Tuple[str, str]]', exitOnConflict: 'bool'=True) -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 420
    ''' Attempt to put all rename actions into an order that avoids target == source names.
      Note, that it's currently not really possible to specify patterns that make this work (swapping "*" elements with a reference).
      An alternative would be to always have one (or all) files renamed to a temporary name before renaming to target filename.
  '''  # line 424
    if not actions:  # line 425
        return []  # line 425
    sources = None  # type: List[str]  # line 426
    targets = None  # type: List[str]  # line 426
    sources, targets = [list(l) for l in zip(*actions)]  # line 427
    last = len(actions)  # type: int  # line 428
    while last > 1:  # line 429
        clean = True  # type: bool  # line 430
        for i in range(1, last):  # line 431
            try:  # line 432
                index = targets[:i].index(sources[i])  # type: int  # line 433
                sources.insert(index, sources.pop(i))  # bubble up the action right before conflict  # line 434
                targets.insert(index, targets.pop(i))  # line 435
                clean = False  # line 436
            except:  # target not found in sources: good!  # line 437
                continue  # target not found in sources: good!  # line 437
        if clean:  # line 438
            break  # line 438
        last -= 1  # we know that the last entry in the list has the least conflicts, so we can disregard it in the next iteration  # line 439
    if exitOnConflict:  # line 440
        for i in range(1, len(actions)):  # line 441
            if sources[i] in targets[:i]:  # line 442
                Exit("There is no order of renaming actions that avoids copying over not-yet renamed files: '%s' is contained in matching source filenames" % (targets[i]))  # line 442
    return _coconut_tail_call(list, zip(sources, targets))  # line 443

def relativize(root: 'str', path: 'str') -> 'Tuple[str, str]':  # line 445
    ''' Determine OS-independent relative folder path, and relative pattern path. '''  # line 446
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(path)), root).replace(os.sep, SLASH)  # line 447
    return relpath, os.path.join(relpath, os.path.basename(path)).replace(os.sep, SLASH)  # line 448

def parseOnlyOptions(root: 'str', options: '_coconut.typing.Sequence[str]') -> 'Tuple[_coconut.typing.Optional[FrozenSet[str]], _coconut.typing.Optional[FrozenSet[str]]]':  # line 450
    ''' Returns set of --only arguments, and set or --except arguments. '''  # line 451
    cwd = os.getcwd()  # type: str  # line 452
    onlys = []  # type: List[str]  # line 453
    excps = []  # type: List[str]  # line 453
    index = 0  # type: int  # line 453
    while True:  # line 454
        try:  # line 455
            index = 1 + listindex(options, "--only", index)  # line 456
            onlys.append(options[index])  # line 457
        except:  # line 458
            break  # line 458
    index = 0  # line 459
    while True:  # line 460
        try:  # line 461
            index = 1 + listindex(options, "--except", index)  # line 462
            excps.append(options[index])  # line 463
        except:  # line 464
            break  # line 464
    return (frozenset((relativize(root, o)[1] for o in onlys)) if onlys else None, frozenset((relativize(root, e)[1] for e in excps)) if excps else None)  # line 465
