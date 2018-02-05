#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x7fe9f0be

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
except:  # typing not available (prior Python 3.5)  # line 11
    pass  # typing not available (prior Python 3.5)  # line 11
try:  # line 12
    import wcwidth  # line 12
except:  # optional dependency  # line 13
    pass  # optional dependency  # line 13


verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 16

# Classes
class Accessor(dict):  # line 19
    ''' Dictionary with attribute access. Writing only supported via dictionary access. '''  # line 20
    def __init__(_, mapping: 'Dict[str, Any]'):  # line 21
        dict.__init__(_, mapping)  # line 21
    @_coconut_tco  # line 22
    def __getattribute__(_, name: 'str') -> 'Any':  # line 22
        try:  # line 23
            return _[name]  # line 23
        except:  # line 24
            return _coconut_tail_call(dict.__getattribute__, _, name)  # line 24

class Counter(Generic[Number]):  # line 26
    ''' A simple counter. Can be augmented to return the last value instead. '''  # line 27
    def __init__(_, initial: 'Number'=0):  # line 28
        _.value = initial  # type: Number  # line 28
    def inc(_, by: 'Number'=1) -> 'Number':  # line 29
        _.value += by  # line 29
        return _.value  # line 29

class Logger:  # line 31
    ''' Logger that supports many items. '''  # line 32
    def __init__(_, log):  # line 33
        _._log = log  # line 33
    def debug(_, *s):  # line 34
        _._log.debug(sjoin(*s))  # line 34
    def info(_, *s):  # line 35
        _._log.info(sjoin(*s))  # line 35
    def warn(_, *s):  # line 36
        _._log.warning(sjoin(*s))  # line 36
    def error(_, *s):  # line 37
        _._log.error(sjoin(*s))  # line 37


# Constants
_log = Logger(logging.getLogger(__name__))  # line 41
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 41
UTF8 = "utf_8"  # early used constant, not defined in standard library  # line 42
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress"]  # line 43
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # line 44
GLOBAL_LISTS = ["ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # line 45
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # all lower-case normalized  # line 46
FALSE_VALUES = ["false", "no", "off", "0", "disable", "disabled"]  # line 47
PROGRESS_MARKER = ["|", "/", "-", "\\"]  # line 48
metaFolder = ".sos"  # type: str  # line 49
metaFile = ".meta"  # type: str  # line 50
bufSize = 1 << 20  # type: int  # 1 MiB  # line 51
SVN = "svn"  # line 52
SLASH = "/"  # line 53
MEBI = 1 << 20  # line 54
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": "fossil", "_FOSSIL_": "fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 55
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 56
lateBinding = Accessor({"verbose": False, "start": 0})  # type: Accessor  # line 57


# Enums
MergeOperation = enum.Enum("MergeOperation", {"INSERT": 1, "REMOVE": 2, "BOTH": 3, "ASK": 4})  # insert remote changes into current, remove remote deletions from current, do both (replicates remote state), or ask per block  # line 61
MergeBlockType = enum.Enum("MergeBlockType", "KEEP INSERT REMOVE REPLACE MOVE")  # modify = intra-line changes, replace = full block replacement  # line 62


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("inSync", 'bool'), ("tracked", 'List[str]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 66
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 66
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 66
    def __new__(_cls, number, ctime, name=None, inSync=False, tracked=[]):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 66
        return _coconut.tuple.__new__(_cls, (number, ctime, name, inSync, tracked))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 66
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 67
    __slots__ = ()  # line 67
    __ne__ = _coconut.object.__ne__  # line 67
    def __new__(_cls, number, ctime, message=None):  # line 67
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 67

class PathInfo(_coconut_NamedTuple("PathInfo", [("nameHash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", '_coconut.typing.Optional[str]')])):  # size == None means deleted in this revision  # line 68
    __slots__ = ()  # size == None means deleted in this revision  # line 68
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 68
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 69
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 69
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 69
class Range(_coconut_NamedTuple("Range", [("tipe", 'MergeBlockType'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 70
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 70
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 70
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'MergeBlockType'), ("lines", 'List[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 71
    __slots__ = ()  # line 71
    __ne__ = _coconut.object.__ne__  # line 71
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 71
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 71

class GlobBlock(_coconut_NamedTuple("GlobBlock", [("isLiteral", 'bool'), ("content", 'str'), ("index", 'int')])):  # for file pattern rename/move matching  # line 72
    __slots__ = ()  # for file pattern rename/move matching  # line 72
    __ne__ = _coconut.object.__ne__  # for file pattern rename/move matching  # line 72
class GlobBlock2(_coconut_NamedTuple("GlobBlock2", [("isLiteral", 'bool'), ("content", 'str'), ("matches", 'str')])):  # matching file pattern and input filename for translation  # line 73
    __slots__ = ()  # matching file pattern and input filename for translation  # line 73
    __ne__ = _coconut.object.__ne__  # matching file pattern and input filename for translation  # line 73


# Functions
def printo(s: 'str', nl: 'str'="\n"):  # PEP528 compatibility  # line 77
    sys.stdout.buffer.write((s + nl).encode(sys.stdout.encoding, 'backslashreplace'))  # PEP528 compatibility  # line 77
    sys.stdout.flush()  # PEP528 compatibility  # line 77
def printe(s: 'str', nl: 'str'="\n"):  # line 78
    sys.stderr.buffer.write((s + nl).encode(sys.stderr.encoding, 'backslashreplace'))  # line 78
    sys.stderr.flush()  # line 78
@_coconut_tco  # for py->os access of writing filenames  # PEP 529 compatibility  # line 79
def encode(s: 'str') -> 'bytes':  # for py->os access of writing filenames  # PEP 529 compatibility  # line 79
    return _coconut_tail_call(os.fsencode, s)  # for py->os access of writing filenames  # PEP 529 compatibility  # line 79
@_coconut_tco  # for os->py access of reading filenames  # line 80
def decode(b: 'bytes') -> 'str':  # for os->py access of reading filenames  # line 80
    return _coconut_tail_call(os.fsdecode, b)  # for os->py access of reading filenames  # line 80
try:  # line 81
    import chardet  # https://github.com/chardet/chardet  # line 82
    def detectEncoding(binary: 'bytes') -> 'str':  # line 83
        return chardet.detect(binary)["encoding"]  # line 83
except:  # line 84
    def detectEncoding(binary: 'bytes') -> 'str':  # Guess the encoding  # line 85
        ''' Fallback if chardet library missing. '''  # line 86
        try:  # line 87
            binary.decode(UTF8)  # line 87
            return UTF8  # line 87
        except UnicodeError:  # line 88
            pass  # line 88
        try:  # line 89
            binary.decode("utf_16")  # line 89
            return "utf_16"  # line 89
        except UnicodeError:  # line 90
            pass  # line 90
        try:  # line 91
            binary.decode("cp1252")  # line 91
            return "cp1252"  # line 91
        except UnicodeError:  # line 92
            pass  # line 92
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 93

@_coconut_tco  # line 95
def wcswidth(string: 'str') -> 'int':  # line 95
    l = 0  # type: int  # line 96
    try:  # line 97
        l = wcwidth.wcswitdh(string)  # line 98
        return len(string) if l < 0 else l  # line 99
    finally:  # line 100
        return _coconut_tail_call(len, string)  # line 100

def removePath(key: 'str', value: 'str') -> 'str':  # line 102
    ''' Cleanup of user-specified global file patterns. '''  # line 103
    return value if value in GLOBAL_LISTS or SLASH not in value else value[value.rindex(SLASH) + 1:]  # line 104

def conditionalIntersection(a: '_coconut.typing.Optional[FrozenSet[str]]', b: 'FrozenSet[str]') -> 'FrozenSet[str]':  # line 106
    return a & b if a else b  # line 106

def dictUpdate(dikt: 'Dict[Any, Any]', by: 'Dict[Any, Any]') -> 'Dict[Any, Any]':  # line 108
    d = {}  # line 108
    d.update(dikt)  # line 108
    d.update(by)  # line 108
    return d  # line 108

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO[bytes]':  # Abstraction for opening both compressed and plain files  # line 110
    return bz2.BZ2File(encode(file), mode) if compress else open(encode(file), mode + "b")  # Abstraction for opening both compressed and plain files  # line 110

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 112
    ''' Determine EOL style from a binary string. '''  # line 113
    lf = file.count(b"\n")  # type: int  # line 114
    cr = file.count(b"\r")  # type: int  # line 115
    crlf = file.count(b"\r\n")  # type: int  # line 116
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 117
        if lf != crlf or cr != crlf:  # line 118
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 118
        return b"\r\n"  # line 119
    if lf != 0 and cr != 0:  # line 120
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 120
    if lf > cr:  # Linux/Unix  # line 121
        return b"\n"  # Linux/Unix  # line 121
    if cr > lf:  # older 8-bit machines  # line 122
        return b"\r"  # older 8-bit machines  # line 122
    return None  # no new line contained, cannot determine  # line 123

try:  # line 125
    Splittable = TypeVar("Splittable", str, bytes)  # line 125
except:  # line 126
    pass  # line 126
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> 'List[Splittable]':  # line 127
    return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 127

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl: 'str'="") -> 'str':  # line 129
    return (sep + (nl + sep).join(seq)) if seq else ""  # line 129

@_coconut_tco  # line 131
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 131
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 131

@_coconut_tco  # line 133
def hashStr(datas: 'str') -> 'str':  # line 133
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 133

def modified(changes: 'ChangeSet', onlyBinary: 'bool'=False) -> 'bool':  # line 135
    return len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0  # line 135

def listindex(lizt: 'Sequence[Any]', what: 'Any', index: 'int'=0) -> 'int':  # line 137
    return lizt[index:].index(what) + index  # line 137

def getTermWidth() -> 'int':  # line 139
    try:  # line 140
        import termwidth  # line 140
    except:  # line 141
        return 80  # line 141
    return termwidth.getTermWidth()[0]  # line 142

def branchFolder(branch: 'int', revision: 'int', base=".", file=None) -> 'str':  # line 144
    return os.path.join(base, metaFolder, "b%d" % branch, "r%d" % revision) + ((os.sep + file) if file else "")  # line 144

def Exit(message: 'str'="", code=1):  # line 146
    printe("[EXIT%s]" % (" %.1fs" % (time.time() - START_TIME) if verbose else "") + (" " + message + "." if message != "" else ""))  # line 146
    sys.exit(code)  # line 146

def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None) -> 'Tuple[str, int]':  # line 148
    ''' Calculate hash of file contents, and return compressed sized, if in write mode, or zero. '''  # line 149
    _hash = hashlib.sha256()  # line 150
    wsize = 0  # type: int  # line 151
    if saveTo and os.path.exists(encode(saveTo)):  # line 152
        Exit("Hash conflict. Leaving revision in inconsistent state. This should happen only once in a lifetime.")  # line 152
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 153
    with open(encode(path), "rb") as fd:  # line 154
        while True:  # line 155
            buffer = fd.read(bufSize)  # type: bytes  # line 156
            _hash.update(buffer)  # line 157
            if to:  # line 158
                to.write(buffer)  # line 158
            if len(buffer) < bufSize:  # line 159
                break  # line 159
        if to:  # line 160
            to.close()  # line 161
            wsize = os.stat(encode(saveTo)).st_size  # line 162
    return (_hash.hexdigest(), wsize)  # line 163

def getAnyOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 165
    ''' Utility. '''  # line 166
    for k, v in map.items():  # line 167
        if k in params:  # line 168
            return v  # line 168
    return default  # line 169

@_coconut_tco  # line 171
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 171
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 171

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 173
    encoding = None  # type: str  # line 174
    eol = None  # type: bytes  # line 174
    lines = []  # type: _coconut.typing.Sequence[str]  # line 174
    if filename is not None:  # line 175
        with open(encode(filename), "rb") as fd:  # line 176
            content = fd.read()  # line 176
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detectEncoding(content))  # line 177
    eol = eoldet(content)  # line 178
    if filename is not None:  # line 179
        with codecs.open(encode(filename), encoding=encoding) as fd2:  # line 180
            lines = safeSplit(fd2.read(), ((b"\n" if eol is None else eol)).decode(encoding))  # line 180
    elif content is not None:  # line 181
        lines = safeSplit(content.decode(encoding), ((b"\n" if eol is None else eol)).decode(encoding))  # line 182
    else:  # line 183
        return (sys.getdefaultencoding(), b"\n", [])  # line 183
    return (encoding, eol, lines)  # line 184

def diffPathSets(last: 'Dict[str, PathInfo]', diff: 'Dict[str, PathInfo]') -> 'ChangeSet':  # line 186
    ''' Computes a changeset between in-memory and on-disk file lists.
      Additions contains PathInfo for entries in diff
      Deletions contains PathInfo for entries not anymore in diff
      Modifications contains PathInfo for entries changed from last to diff (new state)
  '''  # line 191
    changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 192
    for path, pinfo in last.items():  # line 193
        if path not in diff:  # now change  changes.deletions[path] = pinfo; continue  # line 194
            continue  # now change  changes.deletions[path] = pinfo; continue  # line 194
        vs = diff[path]  # reference to potentially changed path set  # line 195
        if vs.size is None:  # marked for deletion  # line 196
            changes.deletions[path] = pinfo  # marked for deletion  # line 196
            continue  # marked for deletion  # line 196
        if pinfo.size == None:  # re-added  # line 197
            changes.additions[path] = pinfo  # re-added  # line 197
            continue  # re-added  # line 197
        if pinfo.size != vs.size or pinfo.mtime != vs.mtime or pinfo.hash != vs.hash:  # not need to make hash comparison optional here  # line 198
            changes.modifications[path] = vs  # not need to make hash comparison optional here  # line 198
    for path, pinfo in diff.items():  # added loop  # line 199
        if path not in last:  # line 200
            changes.additions[path] = pinfo  # line 200
    assert not any([path in changes.deletions for path in changes.additions])  # invariant checks  # line 201
    assert not any([path in changes.additions for path in changes.deletions])  # line 202
    return changes  # line 203

try:  # line 205
    DataType = TypeVar("DataType", ChangeSet, MergeBlock, BranchInfo)  # line 205
except:  # line 206
    pass  # line 206

@_coconut_tco  # line 208
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, **_kwargs) -> 'DataType':  # line 208
    r = _old._asdict()  # line 208
    r.update(**_kwargs)  # line 208
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # line 208

def user_block_input(output: 'List[str]'):  # line 210
    sep = input("Enter end-of-text marker (default: <empty line>: ")  # type: str  # line 211
    line = sep  # type: str  # line 211
    while True:  # line 212
        line = input("> ")  # line 213
        if line == sep:  # line 214
            break  # line 214
        output.append(line)  # line 215

@_coconut_tco  # line 217
def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation: 'MergeOperation'=MergeOperation.BOTH, charMergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False, eol: 'bool'=False) -> 'Union[bytes, List[MergeBlock]]':  # line 217
    ''' Merges other binary text contents 'file' (or reads file 'filename') into current text contents 'into' (or reads file 'intoname'), returning merged result.
      For update, the other version is assumed to be the "new/added" one, while for diff, the current changes are the ones "added".
      However, change direction markers are insert ("+") for elements only in into, and remove ("-") for elements only in other file (just like the diff marks +/-)
      diffOnly returns detected change blocks only, no text merging
      eol flag will use the other file's EOL marks
      in case of replace block and INSERT strategy, the change will be added **behind** the original
  '''  # line 231
    encoding = None  # type: str  # line 232
    othr = None  # type: _coconut.typing.Sequence[str]  # line 232
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 232
    curr = None  # type: _coconut.typing.Sequence[str]  # line 232
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 232
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 233
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file)  # line 234
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into)  # line 235
    except Exception as E:  # line 236
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 236
    if None not in [othreol, curreol] and othreol != curreol:  # line 237
        warn("Differing EOL-styles detected during merge. Using current file's style for merged output")  # line 237
    output = list(difflib.Differ().compare(othr, curr))  # type: List[str]  # from generator expression  # line 238
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 239
    tmp = []  # type: List[str]  # block lines  # line 240
    last = " "  # type: str  # line 241
    no = None  # type: int  # line 241
    line = None  # type: str  # line 241
    for no, line in enumerate(output + ["X"]):  # EOF marker (difflib's output will never be "X" alone)  # line 242
        if line[0] == last:  # continue filling current block, no matter what type of block it is  # line 243
            tmp.append(line[2:])  # continue filling current block, no matter what type of block it is  # line 243
            continue  # continue filling current block, no matter what type of block it is  # line 243
        if line == "X" and len(tmp) == 0:  # break if nothing left to do, otherwise perform operation for stored block  # line 244
            break  # break if nothing left to do, otherwise perform operation for stored block  # line 244
        if last == " ":  # block is same in both files  # line 245
            if len(tmp) > 0:  # avoid adding empty keep block  # line 246
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # avoid adding empty keep block  # line 246
        elif last == "-":  # may be a pure deletion or part of a replacement (with next block being "+")  # line 247
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 248
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.INSERT:  # line 249
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp) - 1, replaces=blocks[-2])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 250
                blocks.pop()  # line 251
        elif last == "+":  # may be insertion or replacement (with previous - block)  # line 252
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # first, assume simple insertion, then check for replacement  # line 253
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.REMOVE:  #  and len(blocks[-1].lines) == len(blocks[-2].lines):  # requires previous block and same number of lines TODO allow multiple intra-line merge for same-length blocks  # line 254
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, line=no - len(tmp) - 1, replaces=blocks[-1])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 255
                blocks.pop()  # remove TOS due to merging two blocks into replace or modify  # line 256
        elif last == "?":  # marker for intra-line change comment -> add to block info  # line 257
            ilm = getIntraLineMarkers(tmp[0])  # type: Range  # TODO still true? "? " line includes a trailing \n for some reason  # line 258
            blocks[-1] = dataCopy(MergeBlock, blocks[-1], changes=ilm)  # line 259
        last = line[0]  # line 260
        tmp[:] = [line[2:]]  # only keep current line for next block  # line 261
# TODO add code to detect block moves here
    debug("Diff blocks: " + repr(blocks))  # line 263
    if diffOnly:  # line 264
        return blocks  # line 264

# now perform merge operations depending on detected blocks
    output[:] = []  # clean list of strings  # line 267
    for block in blocks:  # line 268
        if block.tipe == MergeBlockType.KEEP:  # line 269
            output.extend(block.lines)  # line 270
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value) or block.tipe == MergeBlockType.REMOVE and (mergeOperation.value & MergeOperation.INSERT.value):  # line 271
            output.extend(block.lines)  # line 273
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 274
            if len(block.lines) == len(block.replaces.lines) == 1:  # one-liner  # line 275
                output.append(lineMerge(block.lines[0], block.replaces.lines[0], mergeOperation=charMergeOperation))  # line 276
            elif mergeOperation == MergeOperation.ASK:  # more than one line: needs user input  # line 277
                printo(ajoin("- ", block.replaces.lines, nl="\n"))  # TODO check +/- in update mode, could be swapped  # line 278
                printo(ajoin("+ ", block.lines, nl="\n"))  # line 279
                while True:  # line 280
                    op = input(" Line replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 281
                    if op in "tb":  # line 282
                        output.extend(block.lines)  # line 282
                        break  # line 282
                    if op in "ib":  # line 283
                        output.extend(block.replaces.lines)  # line 283
                        break  # line 283
                    if op == "m":  # line 284
                        user_block_input(output)  # line 284
                        break  # line 284
            else:  # more than one line and not ask  # line 285
                if mergeOperation == MergeOperation.REMOVE:  # line 286
                    pass  # line 286
                elif mergeOperation == MergeOperation.BOTH:  # line 287
                    output.extend(block.lines)  # line 287
                elif mergeOperation == MergeOperation.INSERT:  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 288
                    output.extend(list(block.replaces.lines) + list(block.lines))  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 288
#  debug("Merge output: " + "; ".join(output))
    nl = othreol if eol else (((b"\n" if othreol is None else othreol) if curreol is None else curreol))  # type: bytes  # line 290
    return _coconut_tail_call(nl.join, [line.encode(encoding) for line in output])  # returning bytes  # line 291
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco  # line 294
def lineMerge(othr: 'str', into: 'str', mergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False) -> 'Union[str, List[MergeBlock]]':  # line 294
    ''' Merges string 'othr' into current string 'into'.
      change direction mark is insert for elements only in into, and remove for elements only in file (according to diff marks +/-)
  '''  # line 297
    out = list(difflib.Differ().compare(othr, into))  # type: List[str]  # line 298
    blocks = []  # type: List[MergeBlock]  # line 299
    for i, line in enumerate(out):  # line 300
        if line[0] == "+":  # line 301
            if i + 1 < len(out) and out[i + 1][0] == "+":  # block will continue  # line 302
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # middle of + block  # line 303
                    blocks[-1].lines.append(line[2])  # add one more character to the accumulating list  # line 304
                else:  # first + in block  # line 305
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 306
            else:  # last line of + block  # line 307
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # end of a block  # line 308
                    blocks[-1].lines.append(line[2])  # line 309
                else:  # single line  # line 310
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 311
                if i >= 1 and blocks[-2].tipe == MergeBlockType.REMOVE:  # previous - and now last in + block creates a replacement block  # line 312
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, i, replaces=blocks[-1])  # line 313
                    blocks.pop()  # line 313
        elif line[0] == "-":  # line 314
            if i > 0 and blocks[-1].tipe == MergeBlockType.REMOVE:  # part of - block  # line 315
                blocks[-1].lines.append(line[2])  # line 316
            else:  # first in block  # line 317
                blocks.append(MergeBlock(MergeBlockType.REMOVE, [line[2]], i))  # line 318
        elif line[0] == " ":  # line 319
            if i > 0 and blocks[-1].tipe == MergeBlockType.KEEP:  # part of block  # line 320
                blocks[-1].lines.append(line[2])  # line 321
            else:  # first in block  # line 322
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line[2]], i))  # line 323
        else:  # line 324
            raise Exception("Cannot parse diff line %r" % line)  # line 324
    blocks[:] = [dataCopy(MergeBlock, block, lines=["".join(block.lines)], replaces=dataCopy(MergeBlock, block.replaces, lines=["".join(block.replaces.lines)]) if block.replaces else None) for block in blocks]  # line 325
    if diffOnly:  # line 326
        return blocks  # line 326
    out[:] = []  # line 327
    for i, block in enumerate(blocks):  # line 328
        if block.tipe == MergeBlockType.KEEP:  # line 329
            out.extend(block.lines)  # line 329
        elif block.tipe == MergeBlockType.REPLACE:  # line 330
            if mergeOperation == MergeOperation.ASK:  # line 331
                printo(ajoin("- ", othr))  # line 332
                printo("- " + (" " * i) + block.replaces.lines[0])  # line 333
                printo("+ " + (" " * i) + block.lines[0])  # line 334
                printo(ajoin("+ ", into))  # line 335
                while True:  # line 336
                    op = input(" Character replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 337
                    if op in "tb":  # line 338
                        out.extend(block.lines)  # line 338
                        break  # line 338
                    if op in "ib":  # line 339
                        out.extend(block.replaces.lines)  # line 339
                        break  # line 339
                    if op == "m":  # line 340
                        user_block_input(out)  # line 340
                        break  # line 340
            else:  # non-interactive  # line 341
                if mergeOperation == MergeOperation.REMOVE:  # line 342
                    pass  # line 342
                elif mergeOperation == MergeOperation.BOTH:  # line 343
                    out.extend(block.lines)  # line 343
                elif mergeOperation == MergeOperation.INSERT:  # line 344
                    out.extend(list(block.replaces.lines) + list(block.lines))  # line 344
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value):  # line 345
            out.extend(block.lines)  # line 345
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation.value & MergeOperation.INSERT.value:  # line 346
            out.extend(block.lines)  # line 346
# TODO ask for insert or remove as well
    return _coconut_tail_call("".join, out)  # line 348

@_coconut_tco  # line 350
def getIntraLineMarkers(line: 'str') -> 'Range':  # line 350
    ''' Return (type, [affected indices]) of "? "-line diff markers ("? " prefix must be removed). difflib never returns mixed markers per line. '''  # line 351
    if "^" in line:  # TODO wrong, needs removal anyway  # line 352
        return _coconut_tail_call(Range, MergeBlockType.REPLACE, [i for i, c in enumerate(line) if c == "^"])  # TODO wrong, needs removal anyway  # line 352
    if "+" in line:  # line 353
        return _coconut_tail_call(Range, MergeBlockType.INSERT, [i for i, c in enumerate(line) if c == "+"])  # line 353
    if "-" in line:  # line 354
        return _coconut_tail_call(Range, MergeBlockType.REMOVE, [i for i, c in enumerate(line) if c == "-"])  # line 354
    return _coconut_tail_call(Range, MergeBlockType.KEEP, [])  # line 355

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 357
    ''' Attempts to find sos and legacy VCS base folders. '''  # line 358
    debug("Detecting root folders...")  # line 359
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 360
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 361
    while not os.path.exists(encode(os.path.join(path, metaFolder))):  # line 362
        contents = set(os.listdir(path))  # type: Set[str]  # line 363
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 364
        choice = None  # type: _coconut.typing.Optional[str]  # line 365
        if len(vcss) > 1:  # line 366
            choice = SVN if SVN in vcss else vcss[0]  # line 367
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 368
        elif len(vcss) > 0:  # line 369
            choice = vcss[0]  # line 369
        if not vcs[0] and choice:  # memorize current repo root  # line 370
            vcs = (path, choice)  # memorize current repo root  # line 370
        new = os.path.dirname(path)  # get parent path  # line 371
        if new == path:  # avoid infinite loop  # line 372
            break  # avoid infinite loop  # line 372
        path = new  # line 373
    if os.path.exists(encode(os.path.join(path, metaFolder))):  # found something  # line 374
        if vcs[0]:  # already detected vcs base and command  # line 375
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 375
        sos = path  # line 376
        while True:  # continue search for VCS base  # line 377
            new = os.path.dirname(path)  # get parent path  # line 378
            if new == path:  # no VCS folder found  # line 379
                return (sos, None, None)  # no VCS folder found  # line 379
            path = new  # line 380
            contents = set(os.listdir(path))  # line 381
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 382
            choice = None  # line 383
            if len(vcss) > 1:  # line 384
                choice = SVN if SVN in vcss else vcss[0]  # line 385
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 386
            elif len(vcss) > 0:  # line 387
                choice = vcss[0]  # line 387
            if choice:  # line 388
                return (sos, path, choice)  # line 388
    return (None, vcs[0], vcs[1])  # line 389

def tokenizeGlobPattern(pattern: 'str') -> 'List[GlobBlock]':  # line 391
    index = 0  # type: int  # line 392
    out = []  # type: List[GlobBlock]  # literal = True, first index  # line 393
    while index < len(pattern):  # line 394
        if pattern[index:index + 3] in ("[?]", "[*]", "[[]", "[]]"):  # line 395
            out.append(GlobBlock(False, pattern[index:index + 3], index))  # line 395
            continue  # line 395
        if pattern[index] in "*?":  # line 396
            count = 1  # type: int  # line 397
            while index + count < len(pattern) and pattern[index] == "?" and pattern[index + count] == "?":  # line 398
                count += 1  # line 398
            out.append(GlobBlock(False, pattern[index:index + count], index))  # line 399
            index += count  # line 399
            continue  # line 399
        if pattern[index:index + 2] == "[!":  # line 400
            out.append(GlobBlock(False, pattern[index:pattern.index("]", index + 2) + 1], index))  # line 400
            index += len(out[-1][1])  # line 400
            continue  # line 400
        count = 1  # line 401
        while index + count < len(pattern) and pattern[index + count] not in "*?[":  # line 402
            count += 1  # line 402
        out.append(GlobBlock(True, pattern[index:index + count], index))  # line 403
        index += count  # line 403
    return out  # line 404

def tokenizeGlobPatterns(oldPattern: 'str', newPattern: 'str') -> 'Tuple[_coconut.typing.Sequence[GlobBlock], _coconut.typing.Sequence[GlobBlock]]':  # line 406
    ot = tokenizeGlobPattern(oldPattern)  # type: List[GlobBlock]  # line 407
    nt = tokenizeGlobPattern(newPattern)  # type: List[GlobBlock]  # line 408
#  if len(ot) != len(nt): Exit("Source and target patterns can't be translated due to differing number of parsed glob markers and literal strings")
    if len([o for o in ot if not o.isLiteral]) < len([n for n in nt if not n.isLiteral]):  # line 410
        Exit("Source and target file patterns contain differing number of glob markers and can't be translated")  # line 410
    if any((O.content != N.content for O, N in zip([o for o in ot if not o.isLiteral], [n for n in nt if not n.isLiteral]))):  # line 411
        Exit("Source and target file patterns differ in semantics")  # line 411
    return (ot, nt)  # line 412

def convertGlobFiles(filenames: '_coconut.typing.Sequence[str]', oldPattern: '_coconut.typing.Sequence[GlobBlock]', newPattern: '_coconut.typing.Sequence[GlobBlock]') -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 414
    ''' Converts given filename according to specified file patterns. No support for adjacent glob markers currently. '''  # line 415
    pairs = []  # type: List[Tuple[str, str]]  # line 416
    for filename in filenames:  # line 417
        literals = [l for l in oldPattern if l.isLiteral]  # type: List[GlobBlock]  # source literals  # line 418
        nextliteral = 0  # type: int  # line 419
        parsedOld = []  # type: List[GlobBlock2]  # line 420
        index = 0  # type: int  # line 421
        for part in oldPattern:  # match everything in the old filename  # line 422
            if part.isLiteral:  # line 423
                parsedOld.append(GlobBlock2(True, part.content, part.content))  # line 423
                index += len(part.content)  # line 423
                nextliteral += 1  # line 423
            elif part.content.startswith("?"):  # line 424
                parsedOld.append(GlobBlock2(False, part.content, filename[index:index + len(part.content)]))  # line 424
                index += len(part.content)  # line 424
            elif part.content.startswith("["):  # line 425
                parsedOld.append(GlobBlock2(False, part.content, filename[index]))  # line 425
                index += 1  # line 425
            elif part.content == "*":  # line 426
                if nextliteral >= len(literals):  # line 427
                    parsedOld.append(GlobBlock2(False, part.content, filename[index:]))  # line 427
                    break  # line 427
                nxt = filename.index(literals[nextliteral].content, index)  # type: int  # also matches empty string  # line 428
                parsedOld.append(GlobBlock2(False, part.content, filename[index:nxt]))  # line 429
                index = nxt  # line 429
            else:  # line 430
                Exit("Invalid file pattern specified for move/rename")  # line 430
        globs = [g for g in parsedOld if not g.isLiteral]  # type: List[GlobBlock2]  # line 431
        literals = [l for l in newPattern if l.isLiteral]  # target literals  # line 432
        nextliteral = 0  # line 433
        nextglob = 0  # type: int  # line 433
        outname = []  # type: List[str]  # line 434
        for part in newPattern:  # generate new filename  # line 435
            if part.isLiteral:  # line 436
                outname.append(literals[nextliteral].content)  # line 436
                nextliteral += 1  # line 436
            else:  # line 437
                outname.append(globs[nextglob].matches)  # line 437
                nextglob += 1  # line 437
        pairs.append((filename, "".join(outname)))  # line 438
    return pairs  # line 439

@_coconut_tco  # line 441
def reorderRenameActions(actions: '_coconut.typing.Sequence[Tuple[str, str]]', exitOnConflict: 'bool'=True) -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 441
    ''' Attempt to put all rename actions into an order that avoids target == source names.
      Note, that it's currently not really possible to specify patterns that make this work (swapping "*" elements with a reference).
      An alternative would be to always have one (or all) files renamed to a temporary name before renaming to target filename.
  '''  # line 445
    if not actions:  # line 446
        return []  # line 446
    sources = None  # type: List[str]  # line 447
    targets = None  # type: List[str]  # line 447
    sources, targets = [list(l) for l in zip(*actions)]  # line 448
    last = len(actions)  # type: int  # line 449
    while last > 1:  # line 450
        clean = True  # type: bool  # line 451
        for i in range(1, last):  # line 452
            try:  # line 453
                index = targets[:i].index(sources[i])  # type: int  # line 454
                sources.insert(index, sources.pop(i))  # bubble up the action right before conflict  # line 455
                targets.insert(index, targets.pop(i))  # line 456
                clean = False  # line 457
            except:  # target not found in sources: good!  # line 458
                continue  # target not found in sources: good!  # line 458
        if clean:  # line 459
            break  # line 459
        last -= 1  # we know that the last entry in the list has the least conflicts, so we can disregard it in the next iteration  # line 460
    if exitOnConflict:  # line 461
        for i in range(1, len(actions)):  # line 462
            if sources[i] in targets[:i]:  # line 463
                Exit("There is no order of renaming actions that avoids copying over not-yet renamed files: '%s' is contained in matching source filenames" % (targets[i]))  # line 463
    return _coconut_tail_call(list, zip(sources, targets))  # line 464

def relativize(root: 'str', path: 'str') -> 'Tuple[str, str]':  # line 466
    ''' Determine OS-independent relative folder path, and relative pattern path. '''  # line 467
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(path)), root).replace(os.sep, SLASH)  # line 468
    return relpath, os.path.join(relpath, os.path.basename(path)).replace(os.sep, SLASH)  # line 469

def parseOnlyOptions(root: 'str', options: '_coconut.typing.Sequence[str]') -> 'Tuple[_coconut.typing.Optional[FrozenSet[str]], _coconut.typing.Optional[FrozenSet[str]]]':  # line 471
    ''' Returns set of --only arguments, and set or --except arguments. '''  # line 472
    cwd = os.getcwd()  # type: str  # line 473
    onlys = []  # type: List[str]  # line 474
    excps = []  # type: List[str]  # line 474
    index = 0  # type: int  # line 474
    while True:  # line 475
        try:  # line 476
            index = 1 + listindex(options, "--only", index)  # line 477
            onlys.append(options[index])  # line 478
        except:  # line 479
            break  # line 479
    index = 0  # line 480
    while True:  # line 481
        try:  # line 482
            index = 1 + listindex(options, "--except", index)  # line 483
            excps.append(options[index])  # line 484
        except:  # line 485
            break  # line 485
    return (frozenset((relativize(root, o)[1] for o in onlys)) if onlys else None, frozenset((relativize(root, e)[1] for e in excps)) if excps else None)  # line 486
