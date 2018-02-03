#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xec16e51a

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
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # all lower-case normalized  # line 45
FALSE_VALUES = ["false", "no", "off", "0", "disable", "disabled"]  # line 46
PROGRESS_MARKER = ["|", "/", "-", "\\"]  # line 47
metaFolder = ".sos"  # type: str  # line 48
metaFile = ".meta"  # type: str  # line 49
bufSize = 1 << 20  # type: int  # 1 MiB  # line 50
SVN = "svn"  # line 51
SLASH = "/"  # line 52
MEBI = 1 << 20  # line 53
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": "fossil", "_FOSSIL_": "fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 54
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 55
lateBinding = Accessor({"verbose": False, "start": 0})  # type: Accessor  # line 56


# Enums
MergeOperation = enum.Enum("MergeOperation", {"INSERT": 1, "REMOVE": 2, "BOTH": 3, "ASK": 4})  # insert remote changes into current, remove remote deletions from current, do both (replicates remote state), or ask per block  # line 60
MergeBlockType = enum.Enum("MergeBlockType", "KEEP INSERT REMOVE REPLACE MOVE")  # modify = intra-line changes, replace = full block replacement  # line 61


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("inSync", 'bool'), ("tracked", 'List[str]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 65
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 65
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 65
    def __new__(_cls, number, ctime, name=None, inSync=False, tracked=[]):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 65
        return _coconut.tuple.__new__(_cls, (number, ctime, name, inSync, tracked))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 65
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 66
    __slots__ = ()  # line 66
    __ne__ = _coconut.object.__ne__  # line 66
    def __new__(_cls, number, ctime, message=None):  # line 66
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 66

class PathInfo(_coconut_NamedTuple("PathInfo", [("nameHash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", '_coconut.typing.Optional[str]')])):  # size == None means deleted in this revision  # line 67
    __slots__ = ()  # size == None means deleted in this revision  # line 67
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 67
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 68
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 68
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 68
class Range(_coconut_NamedTuple("Range", [("tipe", 'MergeBlockType'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 69
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 69
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 69
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'MergeBlockType'), ("lines", 'List[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 70
    __slots__ = ()  # line 70
    __ne__ = _coconut.object.__ne__  # line 70
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 70
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 70

class GlobBlock(_coconut_NamedTuple("GlobBlock", [("isLiteral", 'bool'), ("content", 'str'), ("index", 'int')])):  # for file pattern rename/move matching  # line 71
    __slots__ = ()  # for file pattern rename/move matching  # line 71
    __ne__ = _coconut.object.__ne__  # for file pattern rename/move matching  # line 71
class GlobBlock2(_coconut_NamedTuple("GlobBlock2", [("isLiteral", 'bool'), ("content", 'str'), ("matches", 'str')])):  # matching file pattern and input filename for translation  # line 72
    __slots__ = ()  # matching file pattern and input filename for translation  # line 72
    __ne__ = _coconut.object.__ne__  # matching file pattern and input filename for translation  # line 72


# Functions
try:  # line 76
    import chardet  # https://github.com/chardet/chardet  # line 77
    def detectEncoding(binary: 'bytes') -> 'str':  # line 78
        return chardet.detect(binary)["encoding"]  # line 78
except:  # line 79
    def detectEncoding(binary: 'bytes') -> 'str':  # Guess the encoding  # line 80
        ''' Fallback if chardet library missing. '''  # line 81
        try:  # line 82
            binary.decode(UTF8)  # line 82
            return UTF8  # line 82
        except UnicodeError:  # line 83
            pass  # line 83
        try:  # line 84
            binary.decode("utf_16")  # line 84
            return "utf_16"  # line 84
        except UnicodeError:  # line 85
            pass  # line 85
        try:  # line 86
            binary.decode("cp1252")  # line 86
            return "cp1252"  # line 86
        except UnicodeError:  # line 87
            pass  # line 87
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 88

@_coconut_tco  # line 90
def wcswidth(string: 'str') -> 'int':  # line 90
    l = 0  # type: int  # line 91
    try:  # line 92
        l = wcwidth.wcswitdh(string)  # line 93
        return len(string) if l < 0 else l  # line 94
    finally:  # line 95
        return _coconut_tail_call(len, string)  # line 95

def conditionalIntersection(a: '_coconut.typing.Optional[FrozenSet[str]]', b: 'FrozenSet[str]') -> 'FrozenSet[str]':  # line 97
    return a & b if a else b  # line 97

def dictUpdate(dikt: 'Dict[Any, Any]', by: 'Dict[Any, Any]') -> 'Dict[Any, Any]':  # line 99
    d = {}  # line 99
    d.update(dikt)  # line 99
    d.update(by)  # line 99
    return d  # line 99

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO[bytes]':  # Abstraction for opening both compressed and plain files  # line 101
    return bz2.BZ2File(file, mode) if compress else open(file, mode + "b")  # Abstraction for opening both compressed and plain files  # line 101

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 103
    ''' Determine EOL style from a binary string. '''  # line 104
    lf = file.count(b"\n")  # type: int  # line 105
    cr = file.count(b"\r")  # type: int  # line 106
    crlf = file.count(b"\r\n")  # type: int  # line 107
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 108
        if lf != crlf or cr != crlf:  # line 109
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 109
        return b"\r\n"  # line 110
    if lf != 0 and cr != 0:  # line 111
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 111
    if lf > cr:  # Linux/Unix  # line 112
        return b"\n"  # Linux/Unix  # line 112
    if cr > lf:  # older 8-bit machines  # line 113
        return b"\r"  # older 8-bit machines  # line 113
    return None  # no new line contained, cannot determine  # line 114

try:  # line 116
    Splittable = TypeVar("Splittable", str, bytes)  # line 116
except:  # line 117
    pass  # line 117
def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> 'List[Splittable]':  # line 118
    return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 118

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl: 'str'="") -> 'str':  # line 120
    return (sep + (nl + sep).join(seq)) if seq else ""  # line 120

@_coconut_tco  # line 122
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 122
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 122

@_coconut_tco  # line 124
def hashStr(datas: 'str') -> 'str':  # line 124
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 124

def modified(changes: 'ChangeSet', onlyBinary: 'bool'=False) -> 'bool':  # line 126
    return len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0  # line 126

def listindex(lizt: 'Sequence[Any]', what: 'Any', index: 'int'=0) -> 'int':  # line 128
    return lizt[index:].index(what) + index  # line 128

def getTermWidth() -> 'int':  # line 130
    try:  # line 131
        import termwidth  # line 131
    except:  # line 132
        return 80  # line 132
    return termwidth.getTermWidth()[0]  # line 133

def branchFolder(branch: 'int', revision: 'int', base=".", file=None) -> 'str':  # line 135
    return os.path.join(base, metaFolder, "b%d" % branch, "r%d" % revision) + ((os.sep + file) if file else "")  # line 135

def Exit(message: 'str'="", code=1):  # line 137
    print("[EXIT%s]" % (" %.1fs" % (time.time() - START_TIME) if verbose else "") + (" " + message + "." if message != "" else ""), file=sys.stderr)  # line 137
    sys.exit(code)  # line 137

def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None) -> 'Tuple[str, int]':  # line 139
    ''' Calculate hash of file contents, and return compressed sized, if in write mode, or zero. '''  # line 140
    _hash = hashlib.sha256()  # line 141
    wsize = 0  # type: int  # line 142
    if saveTo and os.path.exists(saveTo):  # line 143
        Exit("Hash conflict. Leaving revision in inconsistent state. This should happen only once in a lifetime.")  # line 143
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 144
    with open(path, "rb") as fd:  # line 145
        while True:  # line 146
            buffer = fd.read(bufSize)  # line 147
            _hash.update(buffer)  # line 148
            if to:  # line 149
                to.write(buffer)  # line 149
            if len(buffer) < bufSize:  # line 150
                break  # line 150
        if to:  # line 151
            to.close()  # line 152
            wsize = os.stat(saveTo).st_size  # line 153
    return (_hash.hexdigest(), wsize)  # line 154

def getAnyOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 156
    ''' Utility. '''  # line 157
    for k, v in map.items():  # line 158
        if k in params:  # line 159
            return v  # line 159
    return default  # line 160

@_coconut_tco  # line 162
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 162
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 162

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 164
    encoding = None  # type: str  # line 165
    eol = None  # type: bytes  # line 165
    lines = []  # type: _coconut.typing.Sequence[str]  # line 165
    if filename is not None:  # line 166
        with open(filename, "rb") as fd:  # line 167
            content = fd.read()  # line 167
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detectEncoding(content))  # line 168
    eol = eoldet(content)  # line 169
    if filename is not None:  # line 170
        with codecs.open(filename, encoding=encoding) as fd2:  # line 171
            lines = safeSplit(fd2.read(), ((b"\n" if eol is None else eol)).decode(encoding))  # line 171
    elif content is not None:  # line 172
        lines = safeSplit(content.decode(encoding), ((b"\n" if eol is None else eol)).decode(encoding))  # line 173
    else:  # line 174
        return (sys.getdefaultencoding(), b"\n", [])  # line 174
    return (encoding, eol, lines)  # line 175

def diffPathSets(last: 'Dict[str, PathInfo]', diff: 'Dict[str, PathInfo]') -> 'ChangeSet':  # line 177
    ''' Computes a changeset between in-memory and on-disk file lists.
      Additions contains PathInfo for entries in diff
      Deletions contains PathInfo for entries not anymore in diff
      Modifications contains PathInfo for entries changed from last to diff (new state)
  '''  # line 182
    changes = ChangeSet({}, {}, {})  # type: ChangeSet  # line 183
    for path, pinfo in last.items():  # line 184
        if path not in diff:  # now change  changes.deletions[path] = pinfo; continue  # line 185
            continue  # now change  changes.deletions[path] = pinfo; continue  # line 185
        vs = diff[path]  # reference to potentially changed path set  # line 186
        if vs.size is None:  # marked for deletion  # line 187
            changes.deletions[path] = pinfo  # marked for deletion  # line 187
            continue  # marked for deletion  # line 187
        if pinfo.size == None:  # re-added  # line 188
            changes.additions[path] = pinfo  # re-added  # line 188
            continue  # re-added  # line 188
        if pinfo.size != vs.size or pinfo.mtime != vs.mtime or pinfo.hash != vs.hash:  # not need to make hash comparison optional here  # line 189
            changes.modifications[path] = vs  # not need to make hash comparison optional here  # line 189
    for path, pinfo in diff.items():  # added loop  # line 190
        if path not in last:  # line 191
            changes.additions[path] = pinfo  # line 191
    assert not any([path in changes.deletions for path in changes.additions])  # invariant checks  # line 192
    assert not any([path in changes.additions for path in changes.deletions])  # line 193
    return changes  # line 194

try:  # line 196
    DataType = TypeVar("DataType", ChangeSet, MergeBlock, BranchInfo)  # line 196
except:  # line 197
    pass  # line 197

@_coconut_tco  # line 199
def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, **_kwargs) -> 'DataType':  # line 199
    r = _old._asdict()  # line 199
    r.update(**_kwargs)  # line 199
    return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # line 199

def user_block_input(output: 'List[str]'):  # line 201
    sep = input("Enter end-of-text marker (default: <empty line>: ")  # type: str  # line 202
    line = sep  # type: str  # line 202
    while True:  # line 203
        line = input("> ")  # line 204
        if line == sep:  # line 205
            break  # line 205
        output.append(line)  # line 206

@_coconut_tco  # line 208
def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation: 'MergeOperation'=MergeOperation.BOTH, charMergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False, eol: 'bool'=False) -> 'Union[bytes, List[MergeBlock]]':  # line 208
    ''' Merges other binary text contents 'file' (or reads file 'filename') into current text contents 'into' (or reads file 'intoname'), returning merged result.
      For update, the other version is assumed to be the "new/added" one, while for diff, the current changes are the ones "added".
      However, change direction markers are insert ("+") for elements only in into, and remove ("-") for elements only in other file (just like the diff marks +/-)
      diffOnly returns detected change blocks only, no text merging
      eol flag will use the other file's EOL marks
      in case of replace block and INSERT strategy, the change will be added **behind** the original
  '''  # line 222
    encoding = None  # type: str  # line 223
    othr = None  # type: _coconut.typing.Sequence[str]  # line 223
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 223
    curr = None  # type: _coconut.typing.Sequence[str]  # line 223
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 223
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 224
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file)  # line 225
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into)  # line 226
    except Exception as E:  # line 227
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 227
    if None not in [othreol, curreol] and othreol != curreol:  # line 228
        warn("Differing EOL-styles detected during merge. Using current file's style for merged output")  # line 228
    output = list(difflib.Differ().compare(othr, curr))  # type: List[str]  # from generator expression  # line 229
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 230
    tmp = []  # type: List[str]  # block lines  # line 231
    last = " "  # type: str  # line 232
    no = None  # type: int  # line 232
    line = None  # type: str  # line 232
    for no, line in enumerate(output + ["X"]):  # EOF marker (difflib's output will never be "X" alone)  # line 233
        if line[0] == last:  # continue filling current block, no matter what type of block it is  # line 234
            tmp.append(line[2:])  # continue filling current block, no matter what type of block it is  # line 234
            continue  # continue filling current block, no matter what type of block it is  # line 234
        if line == "X" and len(tmp) == 0:  # break if nothing left to do, otherwise perform operation for stored block  # line 235
            break  # break if nothing left to do, otherwise perform operation for stored block  # line 235
        if last == " ":  # block is same in both files  # line 236
            if len(tmp) > 0:  # avoid adding empty keep block  # line 237
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # avoid adding empty keep block  # line 237
        elif last == "-":  # may be a pure deletion or part of a replacement (with next block being "+")  # line 238
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 239
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.INSERT:  # line 240
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp) - 1, replaces=blocks[-2])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 241
                blocks.pop()  # line 242
        elif last == "+":  # may be insertion or replacement (with previous - block)  # line 243
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # first, assume simple insertion, then check for replacement  # line 244
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.REMOVE:  #  and len(blocks[-1].lines) == len(blocks[-2].lines):  # requires previous block and same number of lines TODO allow multiple intra-line merge for same-length blocks  # line 245
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, line=no - len(tmp) - 1, replaces=blocks[-1])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 246
                blocks.pop()  # remove TOS due to merging two blocks into replace or modify  # line 247
        elif last == "?":  # marker for intra-line change comment -> add to block info  # line 248
            ilm = getIntraLineMarkers(tmp[0])  # type: Range  # TODO still true? "? " line includes a trailing \n for some reason  # line 249
            blocks[-1] = dataCopy(MergeBlock, blocks[-1], changes=ilm)  # line 250
        last = line[0]  # line 251
        tmp[:] = [line[2:]]  # only keep current line for next block  # line 252
# TODO add code to detect block moves here
    debug("Diff blocks: " + repr(blocks))  # line 254
    if diffOnly:  # line 255
        return blocks  # line 255

# now perform merge operations depending on detected blocks
    output[:] = []  # clean list of strings  # line 258
    for block in blocks:  # line 259
        if block.tipe == MergeBlockType.KEEP:  # line 260
            output.extend(block.lines)  # line 261
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value) or block.tipe == MergeBlockType.REMOVE and (mergeOperation.value & MergeOperation.INSERT.value):  # line 262
            output.extend(block.lines)  # line 264
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 265
            if len(block.lines) == len(block.replaces.lines) == 1:  # one-liner  # line 266
                output.append(lineMerge(block.lines[0], block.replaces.lines[0], mergeOperation=charMergeOperation))  # line 267
            elif mergeOperation == MergeOperation.ASK:  # more than one line: needs user input  # line 268
                print(ajoin("- ", block.replaces.lines, nl="\n"))  # TODO check +/- in update mode, could be swapped  # line 269
                print(ajoin("+ ", block.lines, nl="\n"))  # line 270
                while True:  # line 271
                    op = input(" Line replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 272
                    if op in "tb":  # line 273
                        output.extend(block.lines)  # line 273
                        break  # line 273
                    if op in "ib":  # line 274
                        output.extend(block.replaces.lines)  # line 274
                        break  # line 274
                    if op == "m":  # line 275
                        user_block_input(output)  # line 275
                        break  # line 275
            else:  # more than one line and not ask  # line 276
                if mergeOperation == MergeOperation.REMOVE:  # line 277
                    pass  # line 277
                elif mergeOperation == MergeOperation.BOTH:  # line 278
                    output.extend(block.lines)  # line 278
                elif mergeOperation == MergeOperation.INSERT:  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 279
                    output.extend(list(block.replaces.lines) + list(block.lines))  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 279
#  debug("Merge output: " + "; ".join(output))
    nl = othreol if eol else (((b"\n" if othreol is None else othreol) if curreol is None else curreol))  # type: bytes  # line 281
    return _coconut_tail_call(nl.join, [line.encode(encoding) for line in output])  # returning bytes  # line 282
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco  # line 285
def lineMerge(othr: 'str', into: 'str', mergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False) -> 'Union[str, List[MergeBlock]]':  # line 285
    ''' Merges string 'othr' into current string 'into'.
      change direction mark is insert for elements only in into, and remove for elements only in file (according to diff marks +/-)
  '''  # line 288
    out = list(difflib.Differ().compare(othr, into))  # type: List[str]  # line 289
    blocks = []  # type: List[MergeBlock]  # line 290
    for i, line in enumerate(out):  # line 291
        if line[0] == "+":  # line 292
            if i + 1 < len(out) and out[i + 1][0] == "+":  # block will continue  # line 293
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # middle of + block  # line 294
                    blocks[-1].lines.append(line[2])  # add one more character to the accumulating list  # line 295
                else:  # first + in block  # line 296
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 297
            else:  # last line of + block  # line 298
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # end of a block  # line 299
                    blocks[-1].lines.append(line[2])  # line 300
                else:  # single line  # line 301
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 302
                if i >= 1 and blocks[-2].tipe == MergeBlockType.REMOVE:  # previous - and now last in + block creates a replacement block  # line 303
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, i, replaces=blocks[-1])  # line 304
                    blocks.pop()  # line 304
        elif line[0] == "-":  # line 305
            if i > 0 and blocks[-1].tipe == MergeBlockType.REMOVE:  # part of - block  # line 306
                blocks[-1].lines.append(line[2])  # line 307
            else:  # first in block  # line 308
                blocks.append(MergeBlock(MergeBlockType.REMOVE, [line[2]], i))  # line 309
        elif line[0] == " ":  # line 310
            if i > 0 and blocks[-1].tipe == MergeBlockType.KEEP:  # part of block  # line 311
                blocks[-1].lines.append(line[2])  # line 312
            else:  # first in block  # line 313
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line[2]], i))  # line 314
        else:  # line 315
            raise Exception("Cannot parse diff line %r" % line)  # line 315
    blocks[:] = [dataCopy(MergeBlock, block, lines=["".join(block.lines)], replaces=dataCopy(MergeBlock, block.replaces, lines=["".join(block.replaces.lines)]) if block.replaces else None) for block in blocks]  # line 316
    if diffOnly:  # line 317
        return blocks  # line 317
    out[:] = []  # line 318
    for i, block in enumerate(blocks):  # line 319
        if block.tipe == MergeBlockType.KEEP:  # line 320
            out.extend(block.lines)  # line 320
        elif block.tipe == MergeBlockType.REPLACE:  # line 321
            if mergeOperation == MergeOperation.ASK:  # line 322
                print(ajoin("- ", othr))  # line 323
                print("- " + (" " * i) + block.replaces.lines[0])  # line 324
                print("+ " + (" " * i) + block.lines[0])  # line 325
                print(ajoin("+ ", into))  # line 326
                while True:  # line 327
                    op = input(" Character replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 328
                    if op in "tb":  # line 329
                        out.extend(block.lines)  # line 329
                        break  # line 329
                    if op in "ib":  # line 330
                        out.extend(block.replaces.lines)  # line 330
                        break  # line 330
                    if op == "m":  # line 331
                        user_block_input(out)  # line 331
                        break  # line 331
            else:  # non-interactive  # line 332
                if mergeOperation == MergeOperation.REMOVE:  # line 333
                    pass  # line 333
                elif mergeOperation == MergeOperation.BOTH:  # line 334
                    out.extend(block.lines)  # line 334
                elif mergeOperation == MergeOperation.INSERT:  # line 335
                    out.extend(list(block.replaces.lines) + list(block.lines))  # line 335
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value):  # line 336
            out.extend(block.lines)  # line 336
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation.value & MergeOperation.INSERT.value:  # line 337
            out.extend(block.lines)  # line 337
# TODO ask for insert or remove as well
    return _coconut_tail_call("".join, out)  # line 339

@_coconut_tco  # line 341
def getIntraLineMarkers(line: 'str') -> 'Range':  # line 341
    ''' Return (type, [affected indices]) of "? "-line diff markers ("? " prefix must be removed). difflib never returns mixed markers per line. '''  # line 342
    if "^" in line:  # TODO wrong, needs removal anyway  # line 343
        return _coconut_tail_call(Range, MergeBlockType.REPLACE, [i for i, c in enumerate(line) if c == "^"])  # TODO wrong, needs removal anyway  # line 343
    if "+" in line:  # line 344
        return _coconut_tail_call(Range, MergeBlockType.INSERT, [i for i, c in enumerate(line) if c == "+"])  # line 344
    if "-" in line:  # line 345
        return _coconut_tail_call(Range, MergeBlockType.REMOVE, [i for i, c in enumerate(line) if c == "-"])  # line 345
    return _coconut_tail_call(Range, MergeBlockType.KEEP, [])  # line 346

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 348
    ''' Attempts to find sos and legacy VCS base folders. '''  # line 349
    debug("Detecting root folders...")  # line 350
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 351
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 352
    while not os.path.exists(os.path.join(path, metaFolder)):  # line 353
        contents = set(os.listdir(path))  # line 354
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 355
        choice = None  # type: _coconut.typing.Optional[str]  # line 356
        if len(vcss) > 1:  # line 357
            choice = SVN if SVN in vcss else vcss[0]  # line 358
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 359
        elif len(vcss) > 0:  # line 360
            choice = vcss[0]  # line 360
        if not vcs[0] and choice:  # memorize current repo root  # line 361
            vcs = (path, choice)  # memorize current repo root  # line 361
        new = os.path.dirname(path)  # get parent path  # line 362
        if new == path:  # avoid infinite loop  # line 363
            break  # avoid infinite loop  # line 363
        path = new  # line 364
    if os.path.exists(os.path.join(path, metaFolder)):  # found something  # line 365
        if vcs[0]:  # already detected vcs base and command  # line 366
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 366
        sos = path  # line 367
        while True:  # continue search for VCS base  # line 368
            new = os.path.dirname(path)  # get parent path  # line 369
            if new == path:  # no VCS folder found  # line 370
                return (sos, None, None)  # no VCS folder found  # line 370
            path = new  # line 371
            contents = set(os.listdir(path))  # line 372
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 373
            choice = None  # line 374
            if len(vcss) > 1:  # line 375
                choice = SVN if SVN in vcss else vcss[0]  # line 376
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 377
            elif len(vcss) > 0:  # line 378
                choice = vcss[0]  # line 378
            if choice:  # line 379
                return (sos, path, choice)  # line 379
    return (None, vcs[0], vcs[1])  # line 380

def tokenizeGlobPattern(pattern: 'str') -> 'List[GlobBlock]':  # line 382
    index = 0  # type: int  # line 383
    out = []  # type: List[GlobBlock]  # literal = True, first index  # line 384
    while index < len(pattern):  # line 385
        if pattern[index:index + 3] in ("[?]", "[*]", "[[]", "[]]"):  # line 386
            out.append(GlobBlock(False, pattern[index:index + 3], index))  # line 386
            continue  # line 386
        if pattern[index] in "*?":  # line 387
            count = 1  # type: int  # line 388
            while index + count < len(pattern) and pattern[index] == "?" and pattern[index + count] == "?":  # line 389
                count += 1  # line 389
            out.append(GlobBlock(False, pattern[index:index + count], index))  # line 390
            index += count  # line 390
            continue  # line 390
        if pattern[index:index + 2] == "[!":  # line 391
            out.append(GlobBlock(False, pattern[index:pattern.index("]", index + 2) + 1], index))  # line 391
            index += len(out[-1][1])  # line 391
            continue  # line 391
        count = 1  # line 392
        while index + count < len(pattern) and pattern[index + count] not in "*?[":  # line 393
            count += 1  # line 393
        out.append(GlobBlock(True, pattern[index:index + count], index))  # line 394
        index += count  # line 394
    return out  # line 395

def tokenizeGlobPatterns(oldPattern: 'str', newPattern: 'str') -> 'Tuple[_coconut.typing.Sequence[GlobBlock], _coconut.typing.Sequence[GlobBlock]]':  # line 397
    ot = tokenizeGlobPattern(oldPattern)  # type: List[GlobBlock]  # line 398
    nt = tokenizeGlobPattern(newPattern)  # type: List[GlobBlock]  # line 399
#  if len(ot) != len(nt): Exit("Source and target patterns can't be translated due to differing number of parsed glob markers and literal strings")
    if len([o for o in ot if not o.isLiteral]) < len([n for n in nt if not n.isLiteral]):  # line 401
        Exit("Source and target file patterns contain differing number of glob markers and can't be translated")  # line 401
    if any((O.content != N.content for O, N in zip([o for o in ot if not o.isLiteral], [n for n in nt if not n.isLiteral]))):  # line 402
        Exit("Source and target file patterns differ in semantics")  # line 402
    return (ot, nt)  # line 403

def convertGlobFiles(filenames: '_coconut.typing.Sequence[str]', oldPattern: '_coconut.typing.Sequence[GlobBlock]', newPattern: '_coconut.typing.Sequence[GlobBlock]') -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 405
    ''' Converts given filename according to specified file patterns. No support for adjacent glob markers currently. '''  # line 406
    pairs = []  # type: List[Tuple[str, str]]  # line 407
    for filename in filenames:  # line 408
        literals = [l for l in oldPattern if l.isLiteral]  # type: List[GlobBlock]  # source literals  # line 409
        nextliteral = 0  # type: int  # line 410
        parsedOld = []  # type: List[GlobBlock2]  # line 411
        index = 0  # type: int  # line 412
        for part in oldPattern:  # match everything in the old filename  # line 413
            if part.isLiteral:  # line 414
                parsedOld.append(GlobBlock2(True, part.content, part.content))  # line 414
                index += len(part.content)  # line 414
                nextliteral += 1  # line 414
            elif part.content.startswith("?"):  # line 415
                parsedOld.append(GlobBlock2(False, part.content, filename[index:index + len(part.content)]))  # line 415
                index += len(part.content)  # line 415
            elif part.content.startswith("["):  # line 416
                parsedOld.append(GlobBlock2(False, part.content, filename[index]))  # line 416
                index += 1  # line 416
            elif part.content == "*":  # line 417
                if nextliteral >= len(literals):  # line 418
                    parsedOld.append(GlobBlock2(False, part.content, filename[index:]))  # line 418
                    break  # line 418
                nxt = filename.index(literals[nextliteral].content, index)  # type: int  # also matches empty string  # line 419
                parsedOld.append(GlobBlock2(False, part.content, filename[index:nxt]))  # line 420
                index = nxt  # line 420
            else:  # line 421
                Exit("Invalid file pattern specified for move/rename")  # line 421
        globs = [g for g in parsedOld if not g.isLiteral]  # type: List[GlobBlock2]  # line 422
        literals = [l for l in newPattern if l.isLiteral]  # target literals  # line 423
        nextliteral = 0  # line 424
        nextglob = 0  # type: int  # line 424
        outname = []  # type: List[str]  # line 425
        for part in newPattern:  # generate new filename  # line 426
            if part.isLiteral:  # line 427
                outname.append(literals[nextliteral].content)  # line 427
                nextliteral += 1  # line 427
            else:  # line 428
                outname.append(globs[nextglob].matches)  # line 428
                nextglob += 1  # line 428
        pairs.append((filename, "".join(outname)))  # line 429
    return pairs  # line 430

@_coconut_tco  # line 432
def reorderRenameActions(actions: '_coconut.typing.Sequence[Tuple[str, str]]', exitOnConflict: 'bool'=True) -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 432
    ''' Attempt to put all rename actions into an order that avoids target == source names.
      Note, that it's currently not really possible to specify patterns that make this work (swapping "*" elements with a reference).
      An alternative would be to always have one (or all) files renamed to a temporary name before renaming to target filename.
  '''  # line 436
    if not actions:  # line 437
        return []  # line 437
    sources = None  # type: List[str]  # line 438
    targets = None  # type: List[str]  # line 438
    sources, targets = [list(l) for l in zip(*actions)]  # line 439
    last = len(actions)  # type: int  # line 440
    while last > 1:  # line 441
        clean = True  # type: bool  # line 442
        for i in range(1, last):  # line 443
            try:  # line 444
                index = targets[:i].index(sources[i])  # type: int  # line 445
                sources.insert(index, sources.pop(i))  # bubble up the action right before conflict  # line 446
                targets.insert(index, targets.pop(i))  # line 447
                clean = False  # line 448
            except:  # target not found in sources: good!  # line 449
                continue  # target not found in sources: good!  # line 449
        if clean:  # line 450
            break  # line 450
        last -= 1  # we know that the last entry in the list has the least conflicts, so we can disregard it in the next iteration  # line 451
    if exitOnConflict:  # line 452
        for i in range(1, len(actions)):  # line 453
            if sources[i] in targets[:i]:  # line 454
                Exit("There is no order of renaming actions that avoids copying over not-yet renamed files: '%s' is contained in matching source filenames" % (targets[i]))  # line 454
    return _coconut_tail_call(list, zip(sources, targets))  # line 455

def relativize(root: 'str', path: 'str') -> 'Tuple[str, str]':  # line 457
    ''' Determine OS-independent relative folder path, and relative pattern path. '''  # line 458
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(path)), root).replace(os.sep, SLASH)  # line 459
    return relpath, os.path.join(relpath, os.path.basename(path)).replace(os.sep, SLASH)  # line 460

def parseOnlyOptions(root: 'str', options: '_coconut.typing.Sequence[str]') -> 'Tuple[_coconut.typing.Optional[FrozenSet[str]], _coconut.typing.Optional[FrozenSet[str]]]':  # line 462
    ''' Returns set of --only arguments, and set or --except arguments. '''  # line 463
    cwd = os.getcwd()  # type: str  # line 464
    onlys = []  # type: List[str]  # line 465
    excps = []  # type: List[str]  # line 465
    index = 0  # type: int  # line 465
    while True:  # line 466
        try:  # line 467
            index = 1 + listindex(options, "--only", index)  # line 468
            onlys.append(options[index])  # line 469
        except:  # line 470
            break  # line 470
    index = 0  # line 471
    while True:  # line 472
        try:  # line 473
            index = 1 + listindex(options, "--except", index)  # line 474
            excps.append(options[index])  # line 475
        except:  # line 476
            break  # line 476
    return (frozenset((relativize(root, o)[1] for o in onlys)) if onlys else None, frozenset((relativize(root, e)[1] for e in excps)) if excps else None)  # line 477
