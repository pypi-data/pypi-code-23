#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xfadb70d7

# Compiled with Coconut version 1.3.1-post_dev25 [Dead Parrot]

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
import math  # early time tracking  # line 5
import os  # early time tracking  # line 5
import re  # early time tracking  # line 5
sys = _coconut_sys  # early time tracking  # line 5
import time  # early time tracking  # line 5
START_TIME = time.time()  # early time tracking  # line 5

try:  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import Any  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import Dict  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import FrozenSet  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import Generic  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import IO  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import Iterator  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import List  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import Optional  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import Sequence  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import Set  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import Tuple  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import Type  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import TypeVar  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import Union  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
except:  # line 8
    pass  # line 8
from coconut.convenience import version as _coco_version  # Compute version-number for version-dependent features  # line 9
_coco_ver = _coco_version("num").split(".")[:4]  # type: List[str]  # line 10
coco_version = (int(_coco_ver[0]), int(_coco_ver[1]), int(_coco_ver[2].split("-")[0] if "-" in _coco_ver[2] else _coco_ver[2]), int(_coco_ver[2].split("-")[1].split("_dev")[1]) if "-" in _coco_ver[2] else 0)  # type: Tuple[int, int, int, int]  # line 11

try:  # line 13
    import enum  # line 13
except:  # line 14
    raise Exception("SOS requires the enum module (Python 3.4+). You may try to manually install it via 'pip install enum34' or use 'pip install -U sos-vcs[backport]'")  # line 14
if coco_version < (1, 3, 1, 23):  # line 15
    TYPE_CHECKING = False  # type: bool  # line 15
try:  # optional dependency for unicode support  # line 16
    import wcwidth  # optional dependency for unicode support  # line 16
except:  # line 17
    pass  # line 17

verbose = '--verbose' in sys.argv or '-v' in sys.argv  # type: bool  # line 19
debug_ = os.environ.get("DEBUG", "False").lower() == "true" or '--debug' in sys.argv  # type: bool  # line 20


# Classes
class Accessor(dict):  # line 24
    ''' Dictionary with attribute access. Writing only supported via dictionary access. '''  # line 25
    def __init__(_, mapping: 'Dict[str, Any]') -> 'None':  # TODO remove -> None when fixed in Coconut stub  # line 26
        dict.__init__(_, mapping)  # TODO remove -> None when fixed in Coconut stub  # line 26
    @_coconut_tco  # line 27
    def __getattribute__(_, name: 'str') -> 'Any':  # line 27
        try:  # line 28
            return _[name]  # line 28
        except:  # line 29
            return _coconut_tail_call(dict.__getattribute__, _, name)  # line 29

if TYPE_CHECKING:  # line 31
    Number = TypeVar("Number", int, float)  # line 32
    class Counter(Generic[Number]):  # line 33
        ''' A simple counter. Can be augmented to return the last value instead. '''  # line 34
        def __init__(_, initial: 'Number'=0) -> 'None':  # line 35
            _.value = initial  # type: Number  # line 35
        def inc(_, by: 'Number'=1) -> 'Number':  # line 36
            _.value += by  # line 36
            return _.value  # line 36
else:  # line 37
    class Counter:  # line 38
        def __init__(_, initial=0) -> 'None':  # line 39
            _.value = initial  # line 39
        def inc(_, by=1):  # line 40
            _.value += by  # line 40
            return _.value  # line 40

class ProgressIndicator(Counter):  # line 42
    ''' Manages a rotating progress indicator. '''  # line 43
    def __init__(_, symbols: 'str', callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None) -> 'None':  # line 44
        super(ProgressIndicator, _).__init__(-1)  # line 44
        _.symbols = symbols  # line 44
        _.timer = time.time()  # type: float  # line 44
        _.callback = callback  # type: Optional[_coconut.typing.Callable[[str], None]]  # line 44
    def getIndicator(_) -> '_coconut.typing.Optional[str]':  # line 45
        ''' Returns a value only if a certain time has passed. '''  # line 46
        newtime = time.time()  # type: float  # line 47
        if newtime - _.timer < .1:  # line 48
            return None  # line 48
        _.timer = newtime  # line 49
        sign = _.symbols[int(_.inc() % len(_.symbols))]  # type: str  # line 50
        if _.callback:  # line 51
            _.callback(sign)  # line 51
        return sign  # line 52

class Logger:  # line 54
    ''' Logger that supports joining many items. '''  # line 55
    def __init__(_, log) -> 'None':  # line 56
        _._log = log  # line 56
    def debug(_, *s):  # line 57
        _._log.debug(sjoin(*s))  # line 57
    def info(_, *s):  # line 58
        _._log.info(sjoin(*s))  # line 58
    def warn(_, *s):  # line 59
        _._log.warning(sjoin(*s))  # line 59
    def error(_, *s):  # line 60
        _._log.error(sjoin(*s))  # line 60


# Constants
_log = Logger(logging.getLogger(__name__))  # line 64
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 64
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress", "useChangesCommand", "useUnicodeFont"]  # type: List[str]  # line 65
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # type: List[str]  # line 66
GLOBAL_LISTS = ["ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # type: List[str]  # line 67
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # type: List[str]  # all lower-case normalized  # line 68
FALSE_VALUES = ["false", "no", "off", "0", "disable", "disabled"]  # type: List[str]  # line 69
PROGRESS_MARKER = ["|/-\\", "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588\u2587\u2586\u2585\u2584\u2583\u2582", "\U0001f55b\U0001f550\U0001f551\U0001f552\U0001f553\U0001f554\U0001f555\U0001f556\U0001f557\U0001f558\U0001f559\U0001f55a\U0001f559\U0001f558\U0001f557\U0001f556\U0001f555\U0001f554\U0001f553\U0001f552\U0001f551\U0001f550"]  # type: List[str]  # line 70
BACKUP_SUFFIX = "_last"  # type: str  # line 71
metaFolder = ".sos"  # type: str  # line 72
DUMP_FILE = metaFolder + ".zip"  # type: str  # line 73
metaFile = ".meta"  # type: str  # line 74
metaBack = metaFile + BACKUP_SUFFIX  # type: str  # line 75
KIBI = 1 << 10  # type: int  # line 76
MEBI = 1 << 20  # type: int  # line 77
bufSize = MEBI  # type: int  # line 78
UTF8 = "utf_8"  # type: str  # early used constant, not defined in standard library  # line 79
SVN = "svn"  # type: str  # line 80
SLASH = "/"  # type: str  # line 81
DOT_SYMBOL = "\u00b7"  # type: str  # line 82
CROSS_SYMBOL = "\u2716"  # type: str  # line 83
CHECKMARK_SYMBOL = "\u2714"  # type: str  # line 84
PLUSMINUS_SYMBOL = "\u00b1"  # type: str  # line 85
MOVE_SYMBOL = "\u21cc"  # type: str  # \U0001F5C0"  # HINT second one is very unlikely to be in any console font  # line 86
METADATA_FORMAT = 1  # type: int  # counter for incompatible consecutive formats  # line 87
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": "fossil", "_FOSSIL_": "fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 88
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 89
NL_NAMES = {None: "<No newline>", b"\r\n": "<CR+LF>", b"\n\r": "<LF+CR>", b"\n": "<LF>", b"\r": "<CR>"}  # type: Dict[bytes, str]  # line 90
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": False, "useChangesCommand": False, "useUnicodeFont": sys.platform != "win32", "texttype": ["*.md", "*.coco", "*.py", "*.pyi", "*.pth"], "bintype": [], "ignoreDirs": [".*", "__pycache__", ".mypy_cache"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout", "_FOSSIL_", "*%s" % DUMP_FILE], "ignoresWhitelist": []})  # type: Accessor  # line 91


# Enums
MergeOperation = enum.Enum("MergeOperation", {"INSERT": 1, "REMOVE": 2, "BOTH": 3, "ASK": 4})  # insert remote changes into current, remove remote deletions from current, do both (replicates remote state), or ask per block  # line 103
MergeBlockType = enum.Enum("MergeBlockType", "KEEP INSERT REMOVE REPLACE MOVE")  # modify = intra-line changes, replace = full block replacement  # line 104


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("inSync", 'bool'), ("tracked", 'List[str]'), ("untracked", 'List[str]'), ("parent", '_coconut.typing.Optional[int]'), ("revision", '_coconut.typing.Optional[int]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 108
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 108
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 108
    def __new__(_cls, number, ctime, name=None, inSync=False, tracked=[], untracked=[], parent=None, revision=None):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 108
        return _coconut.tuple.__new__(_cls, (number, ctime, name, inSync, tracked, untracked, parent, revision))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 108
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 109
    __slots__ = ()  # line 109
    __ne__ = _coconut.object.__ne__  # line 109
    def __new__(_cls, number, ctime, message=None):  # line 109
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 109

class PathInfo(_coconut_NamedTuple("PathInfo", [("nameHash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", '_coconut.typing.Optional[str]')])):  # size == None means deleted in this revision  # line 110
    __slots__ = ()  # size == None means deleted in this revision  # line 110
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 110
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]'), ("moves", 'Dict[str, Tuple[str, PathInfo]]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 111
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 111
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 111
class Range(_coconut_NamedTuple("Range", [("tipe", 'MergeBlockType'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 112
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 112
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 112
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'MergeBlockType'), ("lines", 'List[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 113
    __slots__ = ()  # line 113
    __ne__ = _coconut.object.__ne__  # line 113
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 113
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 113

class GlobBlock(_coconut_NamedTuple("GlobBlock", [("isLiteral", 'bool'), ("content", 'str'), ("index", 'int')])):  # for file pattern rename/move matching  # line 114
    __slots__ = ()  # for file pattern rename/move matching  # line 114
    __ne__ = _coconut.object.__ne__  # for file pattern rename/move matching  # line 114
class GlobBlock2(_coconut_NamedTuple("GlobBlock2", [("isLiteral", 'bool'), ("content", 'str'), ("matches", 'str')])):  # matching file pattern and input filename for translation  # line 115
    __slots__ = ()  # matching file pattern and input filename for translation  # line 115
    __ne__ = _coconut.object.__ne__  # matching file pattern and input filename for translation  # line 115


# Functions
def printo(s: 'str'="", nl: 'str'="\n"):  # PEP528 compatibility  # line 119
    tryOrDefault(lambda: (lambda _coconut_none_coalesce_item: sys.stdout if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(sys.stdout.buffer), sys.stdout).write((s + nl).encode(sys.stdout.encoding, 'backslashreplace'))  # PEP528 compatibility  # line 119
    sys.stdout.flush()  # PEP528 compatibility  # line 119
def printe(s: 'str'="", nl: 'str'="\n"):  # line 120
    tryOrDefault(lambda: (lambda _coconut_none_coalesce_item: sys.stderr if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(sys.stderr.buffer), sys.stderr).write((s + nl).encode(sys.stderr.encoding, 'backslashreplace'))  # line 120
    sys.stderr.flush()  # line 120
@_coconut_tco  # for py->os access of writing filenames  # PEP 529 compatibility  # line 121
def encode(s: 'str') -> 'bytes':  # for py->os access of writing filenames  # PEP 529 compatibility  # line 121
    return _coconut_tail_call(os.fsencode, s)  # for py->os access of writing filenames  # PEP 529 compatibility  # line 121
@_coconut_tco  # for os->py access of reading filenames  # line 122
def decode(b: 'bytes') -> 'str':  # for os->py access of reading filenames  # line 122
    return _coconut_tail_call(os.fsdecode, b)  # for os->py access of reading filenames  # line 122
try:  # line 123
    import chardet  # https://github.com/chardet/chardet  # line 124
    def detectEncoding(binary: 'bytes') -> 'str':  # line 125
        return chardet.detect(binary)["encoding"]  # line 125
except:  # line 126
    def detectEncoding(binary: 'bytes') -> 'str':  # Guess the encoding  # line 127
        ''' Fallback if chardet library missing. '''  # line 128
        try:  # line 129
            binary.decode(UTF8)  # line 129
            return UTF8  # line 129
        except UnicodeError:  # line 130
            pass  # line 130
        try:  # line 131
            binary.decode("utf_16")  # line 131
            return "utf_16"  # line 131
        except UnicodeError:  # line 132
            pass  # line 132
        try:  # line 133
            binary.decode("cp1252")  # line 133
            return "cp1252"  # line 133
        except UnicodeError:  # line 134
            pass  # line 134
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 135

def tryOrDefault(func: '_coconut.typing.Callable[[], Any]', default: 'Any') -> 'Any':  # line 137
    try:  # line 138
        return func()  # line 138
    except:  # line 139
        return default  # line 139

def tryOrIgnore(func: '_coconut.typing.Callable[[], Any]') -> 'None':  # handle with care!  # line 141
    try:  # line 142
        func()  # line 142
    except:  # line 143
        pass  # line 143

def requiredDecimalDigits(number: 'int') -> 'int':  # line 145
    return 1 if number <= 0 else int(math.floor(round(math.log(number, 10), 6)) + 1)  # line 146

def removePath(key: 'str', value: 'str') -> 'str':  # line 148
    ''' Cleanup of user-specified global file patterns. '''  # line 149
    return value if value in GLOBAL_LISTS or SLASH not in value else value[value.rindex(SLASH) + 1:]  # line 150

def conditionalIntersection(a: '_coconut.typing.Optional[FrozenSet[str]]', b: 'FrozenSet[str]') -> 'FrozenSet[str]':  # Used to match only arguments, or use only stored patterns  # line 152
    return a & b if a else b  # Used to match only arguments, or use only stored patterns  # line 152

def dictUpdate(dikt: 'Dict[Any, Any]', by: 'Dict[Any, Any]') -> 'Dict[Any, Any]':  # line 154
    d = {}  # line 154
    d.update(dikt)  # line 154
    d.update(by)  # line 154
    return d  # line 154

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO[bytes]':  # Abstraction for opening both compressed and plain files  # line 156
    return bz2.BZ2File(encode(file), mode) if compress else open(encode(file), mode + "b")  # Abstraction for opening both compressed and plain files  # line 156

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 158
    ''' Determine EOL style from a binary string. '''  # line 159
    lf = file.count(b"\n")  # type: int  # line 160
    cr = file.count(b"\r")  # type: int  # line 161
    crlf = file.count(b"\r\n")  # type: int  # line 162
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 163
        if lf != crlf or cr != crlf:  # line 164
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 164
        return b"\r\n"  # line 165
    if lf != 0 and cr != 0:  # line 166
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 166
    if lf > cr:  # Linux/Unix  # line 167
        return b"\n"  # Linux/Unix  # line 167
    if cr > lf:  # older 8-bit machines  # line 168
        return b"\r"  # older 8-bit machines  # line 168
    return None  # no new line contained, cannot determine  # line 169

if TYPE_CHECKING:  # line 171
    Splittable = TypeVar("Splittable", str, bytes)  # TODO isn't that the same as AnyStr?  # line 172
    def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> 'List[Splittable]':  # line 173
        return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 173
else:  # line 174
    def safeSplit(s, d=None):  # line 175
        return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 175

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl: 'str'="") -> 'str':  # line 177
    return (sep + (nl + sep).join(seq)) if seq else ""  # line 177

@_coconut_tco  # line 179
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 179
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 179

@_coconut_tco  # line 181
def hashStr(datas: 'str') -> 'str':  # line 181
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 181

def modified(changes: 'ChangeSet', onlyBinary: 'bool'=False) -> 'bool':  # line 183
    return len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0 or len(changes.moves) > 0  # line 183

def listindex(lizt: 'Sequence[Any]', what: 'Any', index: 'int'=0) -> 'int':  # line 185
    return lizt[index:].index(what) + index  # line 185

def getTermWidth() -> 'int':  # line 187
    try:  # line 188
        import termwidth  # line 188
    except:  # line 189
        return 80  # line 189
    return termwidth.getTermWidth()[0]  # line 190
termWidth = getTermWidth() - 1  # uses curses or returns conservative default of 80  # line 191

@_coconut_tco  # TODO currently unused!  # line 193
def wcswidth(string: 'str') -> 'int':  # TODO currently unused!  # line 193
    try:  # line 194
        l = wcwidth.wcswitdh(string)  # type: int  # line 195
        return len(string) if l < 0 else l  # line 196
    except:  # line 197
        return _coconut_tail_call(len, string)  # line 197

def ljust(string: 'str', width: 'int'=termWidth) -> 'str':  # line 199
    assert width > 0  # line 200
    return string + " " * max(0, width - wcswidth(string))  # line 201

def branchFolder(branch: 'int', base: '_coconut.typing.Optional[str]'=None, file: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 203
    return os.path.join((os.getcwd() if base is None else base), metaFolder, "b%d" % branch) + ((os.sep + file) if file else "")  # line 203

def revisionFolder(branch: 'int', revision: 'int', base: '_coconut.typing.Optional[str]'=None, file: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 205
    return os.path.join(branchFolder(branch, base), "r%d" % revision) + ((os.sep + file) if file else "")  # line 205

def Exit(message: 'str'="", code=1):  # line 207
    printe("[EXIT%s]" % (" %.1fs" % (time.time() - START_TIME) if verbose else "") + (" " + message + "." if message != "" else ""))  # line 207
    sys.exit(code)  # line 207

def exception(E):  # line 209
    ''' Report an exception to the user to enable useful bug reporting. '''  # line 210
    printo(str(E))  # line 211
    import traceback  # line 212
    traceback.print_exc()  # line 213
    traceback.print_stack()  # line 214

def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None, callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None, symbols: 'str'=PROGRESS_MARKER[0]) -> 'Tuple[str, int]':  # line 216
    ''' Calculate hash of file contents, and return compressed sized, if in write mode, or zero. '''  # line 217
    indicator = ProgressIndicator(symbols, callback) if callback else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 218
    _hash = hashlib.sha256()  # line 219
    wsize = 0  # type: int  # line 220
    if saveTo and os.path.exists(encode(saveTo)):  # line 221
        Exit("Hash conflict. Leaving revision in inconsistent state. This should happen only once in a lifetime")  # line 221
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 222
    with open(encode(path), "rb") as fd:  # line 223
        while True:  # line 224
            buffer = fd.read(bufSize)  # type: bytes  # line 225
            _hash.update(buffer)  # line 226
            if to:  # line 227
                to.write(buffer)  # line 227
            if len(buffer) < bufSize:  # line 228
                break  # line 228
            if indicator:  # line 229
                indicator.getIndicator()  # line 229
        if to:  # line 230
            to.close()  # line 231
            wsize = os.stat(encode(saveTo)).st_size  # line 232
    return (_hash.hexdigest(), wsize)  # line 233

def getAnyOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 235
    ''' Utility to find any entries of a dictionary in a list to return the dictionaries value. '''  # line 236
    for k, v in map.items():  # line 237
        if k in params:  # line 238
            return v  # line 238
    return default  # line 239

@_coconut_tco  # line 241
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 241
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 241

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None, ignoreWhitespace: 'bool'=False) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 243
    lines = []  # type: _coconut.typing.Sequence[str]  # line 244
    if filename is not None:  # line 245
        with open(encode(filename), "rb") as fd:  # line 246
            content = fd.read()  # line 246
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detectEncoding(content))  # type: str  # line 247
    eol = eoldet(content)  # type: _coconut.typing.Optional[bytes]  # line 248
    if filename is not None:  # line 249
        with codecs.open(encode(filename), encoding=encoding) as fd2:  # line 250
            lines = safeSplit(fd2.read(), ((b"\n" if eol is None else eol)).decode(encoding))  # line 250
    elif content is not None:  # line 251
        lines = safeSplit(content.decode(encoding), ((b"\n" if eol is None else eol)).decode(encoding))  # line 252
    else:  # line 253
        return (sys.getdefaultencoding(), b"\n", [])  # line 253
    if ignoreWhitespace:  # line 254
        lines[:] = [line.replace("\t", "  ").strip() for line in lines]  # line 254
    return (encoding, eol, lines)  # line 255

if TYPE_CHECKING:  # line 257
    DataType = TypeVar("DataType", BranchInfo, ChangeSet, MergeBlock, PathInfo)  # line 258
    @_coconut_tco  # line 259
    def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, byValue: 'bool'=False, **_kwargs) -> 'DataType':  # line 259
        ''' A better makedata() version. '''  # line 260
        r = _old._asdict()  # type: Dict[str, Any]  # line 261
        r.update({k: ([e for e in v] if byValue and isinstance(v, (list, tuple, set)) else v) for k, v in _kwargs.items()})  # copy by value if required  # line 262
        return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # TODO also offer copy-by-value here  # line 263
else:  # line 264
    @_coconut_tco  # line 265
    def dataCopy(_tipe, _old, *_args, byValue=False, **_kwargs) -> 'DataType':  # line 265
        ''' A better makedata() version. '''  # line 266
        r = _old._asdict()  # line 267
        r.update({k: ([e for e in v] if byValue and isinstance(v, (list, tuple, set)) else v) for k, v in _kwargs.items()})  # copy by value if required  # line 268
        return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # TODO also offer copy-by-value here  # line 269

def detectMoves(changes: 'ChangeSet') -> 'Dict[str, Tuple[str, PathInfo]]':  # line 271
    ''' Compute renames/removes for a changeset. '''  # line 272
    moves = {}  # type: Dict[str, Tuple[str, PathInfo]]  # line 273
    for path, info in changes.additions.items():  # line 274
        for dpath, dinfo in changes.deletions.items():  # line 275
            if info.size == dinfo.size and info.mtime == dinfo.mtime and info.hash == dinfo.hash:  # was moved TODO check either mtime or hash?  # line 276
                moves[path] = (dpath, info)  # store new data and original name, but don't remove add/del  # line 277
                break  # deletions loop, continue with next addition  # line 278
    return moves  # line 279

def user_block_input(output: 'List[str]'):  # line 281
    sep = input("Enter end-of-text marker (default: <empty line>: ")  # type: str  # line 282
    line = sep  # type: str  # line 282
    while True:  # line 283
        line = input("> ")  # line 284
        if line == sep:  # line 285
            break  # line 285
        output.append(line)  # writes to caller-provided list reference  # line 286

def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation: 'MergeOperation'=MergeOperation.BOTH, charMergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False, eol: 'bool'=False, ignoreWhitespace: 'bool'=False) -> 'Tuple[Union[bytes, List[MergeBlock]], _coconut.typing.Optional[bytes]]':  # line 288
    ''' Merges other binary text contents 'file' (or reads file 'filename') into current text contents 'into' (or reads file 'intoname'), returning merged result.
      For update, the other version is assumed to be the "new/added" one, while for diff, the current changes are the ones "added".
      However, change direction markers are insert ("+") for elements only in into, and remove ("-") for elements only in other file (just like the diff marks +/-)
      diffOnly returns detected change blocks only, no text merging
      eol flag will use the other file's EOL marks
      in case of replace block and INSERT strategy, the change will be added **behind** the original
  '''  # line 303
    encoding = None  # type: str  # line 304
    othr = None  # type: _coconut.typing.Sequence[str]  # line 304
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 304
    curr = None  # type: _coconut.typing.Sequence[str]  # line 304
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 304
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 305
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file, ignoreWhitespace=ignoreWhitespace)  # line 306
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into, ignoreWhitespace=ignoreWhitespace)  # line 307
    except Exception as E:  # line 308
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 308
    if None not in [othreol, curreol] and othreol != curreol:  # line 309
        warn("Differing EOL-styles detected during merge. Using current file's style for merged output")  # line 309
    output = list(difflib.Differ().compare(othr, curr))  # type: List[str]  # from generator expression  # line 310
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 311
    tmp = []  # type: List[str]  # block lines  # line 312
    last = " "  # type: str  # line 313
    no = None  # type: int  # line 313
    line = None  # type: str  # line 313
    offset = 0  # type: int  # into file offset for remark lines  # line 314
    for no, line in enumerate(output + ["X"]):  # EOF marker (difflib's output will never be "X" alone)  # line 315
        if line[0] == last:  # continue filling current block, no matter what type of block it is  # line 316
            tmp.append(line[2:])  # continue filling current block, no matter what type of block it is  # line 316
            continue  # continue filling current block, no matter what type of block it is  # line 316
        if line == "X" and len(tmp) == 0:  # break if nothing left to do, otherwise perform operation for stored block  # line 317
            break  # break if nothing left to do, otherwise perform operation for stored block  # line 317
        if last == " ":  # block is same in both files  # line 318
            if len(tmp) > 0:  # avoid adding empty keep block  # line 319
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - offset - len(tmp)))  # avoid adding empty keep block  # line 319
        elif last == "-":  # may be a pure deletion or part of a replacement (with next block being "+")  # line 320
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - offset - len(tmp)))  # line 321
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.INSERT:  # line 322
                offset += len(blocks[-2].lines)  # line 323
                blocks[-2] = dataCopy(MergeBlock, blocks[-1], tipe=MergeBlockType.REPLACE, replaces=dataCopy(MergeBlock, blocks[-2], line=blocks[-1].line))  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 324
                blocks.pop()  # line 325
        elif last == "+":  # may be insertion or replacement (with previous - block)  # line 326
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - offset - len(tmp)))  # first, assume simple insertion, then check for replacement  # line 327
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.REMOVE:  #  and len(blocks[-1].lines) == len(blocks[-2].lines):  # requires previous block and same number of lines TODO allow multiple intra-line merge for same-length blocks  # line 328
                offset += len(blocks[-1].lines)  # line 329
                blocks[-2] = dataCopy(MergeBlock, blocks[-2], tipe=MergeBlockType.REPLACE, replaces=dataCopy(MergeBlock, blocks[-1], line=blocks[-2].line))  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 330
                blocks.pop()  # remove TOS due to merging two blocks into replace or modify  # line 331
        elif last == "?":  # marker for intra-line change comment HINT was earlier part of the MergeBlock  # line 332
            offset += 1  # marker for intra-line change comment HINT was earlier part of the MergeBlock  # line 332
        last = line[0]  # line 333
        tmp[:] = [line[2:]]  # only keep current line for next block  # line 334
# TODO add code to detect block moves here
    nl = othreol if eol else ((othreol if curreol is None else curreol))  # type: bytes  # no default newline, to mark "no newline"  # line 336
    debug("Diff blocks: " + repr(blocks))  # line 337
    if diffOnly:  # line 338
        return (blocks, nl)  # line 338

# now perform merge operations depending on detected blocks
    output[:] = []  # clean list of strings  # line 341
    for block in blocks:  # line 342
        if block.tipe == MergeBlockType.KEEP:  # line 343
            output.extend(block.lines)  # line 344
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value) or block.tipe == MergeBlockType.REMOVE and (mergeOperation.value & MergeOperation.INSERT.value):  # line 345
            output.extend(block.lines)  # line 347
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 348
            if len(block.lines) == len(block.replaces.lines) == 1:  # one-liner  # line 349
                output.append(lineMerge(block.lines[0], block.replaces.lines[0], mergeOperation=charMergeOperation))  # line 350
            elif mergeOperation == MergeOperation.ASK:  # more than one line: needs user input  # line 351
                printo(ajoin("- ", block.lines, nl="\n"))  # TODO check +/- in update mode, could be swapped  # line 352
                printo(ajoin("+ ", block.replaces.lines, nl="\n"))  # line 353
                while True:  # line 354
                    op = input(" Line replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()[:1]  # type: str  # line 355
                    if op in "tb":  # line 356
                        output.extend(block.lines)  # line 356
                    if op in "ib":  # line 357
                        output.extend(block.replaces.lines)  # line 357
                    if op == "u":  # line 358
                        user_block_input(output)  # line 358
                    if op in "tbiu":  # line 359
                        break  # line 359
            else:  # more than one line and not ask  # line 360
                if mergeOperation == MergeOperation.REMOVE:  # line 361
                    pass  # line 361
                elif mergeOperation == MergeOperation.BOTH:  # line 362
                    output.extend(block.lines)  # line 362
                elif mergeOperation == MergeOperation.INSERT:  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 363
                    output.extend(list(block.replaces.lines) + list(block.lines))  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 363
    debug("Merge output: " + "; ".join(output))  # line 364
    return (((b"\n" if nl is None else nl)).join([line.encode(encoding) for line in output]), nl)  # returning bytes  # line 365
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco  # line 368
def lineMerge(othr: 'str', into: 'str', mergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False) -> 'Union[str, List[MergeBlock]]':  # line 368
    ''' Merges string 'othr' into current string 'into'.
      change direction mark is insert for elements only in into, and remove for elements only in file (according to diff marks +/-)
  '''  # line 371
    out = list(difflib.Differ().compare(othr, into))  # type: List[str]  # line 372
    blocks = []  # type: List[MergeBlock]  # line 373
    for i, line in enumerate(out):  # line 374
        if line[0] == "+":  # line 375
            if i + 1 < len(out) and out[i + 1][0] == "+":  # block will continue  # line 376
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # middle of + block  # line 377
                    blocks[-1].lines.append(line[2])  # add one more character to the accumulating list  # line 378
                else:  # first + in block  # line 379
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 380
            else:  # last line of + block  # line 381
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # end of a block  # line 382
                    blocks[-1].lines.append(line[2])  # line 383
                else:  # single line  # line 384
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 385
                if i >= 1 and blocks[-2].tipe == MergeBlockType.REMOVE:  # previous - and now last in + block creates a replacement block  # line 386
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, i, replaces=blocks[-1])  # line 387
                    blocks.pop()  # line 387
        elif line[0] == "-":  # line 388
            if i > 0 and blocks[-1].tipe == MergeBlockType.REMOVE:  # part of - block  # line 389
                blocks[-1].lines.append(line[2])  # line 390
            else:  # first in block  # line 391
                blocks.append(MergeBlock(MergeBlockType.REMOVE, [line[2]], i))  # line 392
        elif line[0] == " ":  # line 393
            if i > 0 and blocks[-1].tipe == MergeBlockType.KEEP:  # part of block  # line 394
                blocks[-1].lines.append(line[2])  # line 395
            else:  # first in block  # line 396
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line[2]], i))  # line 397
        else:  # line 398
            raise Exception("Cannot parse diff line %r" % line)  # line 398
    blocks[:] = [dataCopy(MergeBlock, block, lines=["".join(block.lines)], replaces=dataCopy(MergeBlock, block.replaces, lines=["".join(block.replaces.lines)]) if block.replaces else None) for block in blocks]  # line 399
    if diffOnly:  # line 400
        return blocks  # line 400
    out[:] = []  # line 401
    for i, block in enumerate(blocks):  # line 402
        if block.tipe == MergeBlockType.KEEP:  # line 403
            out.extend(block.lines)  # line 403
        elif block.tipe == MergeBlockType.REPLACE:  # line 404
            if mergeOperation == MergeOperation.ASK:  # line 405
                printo(ajoin("- ", othr))  # line 406
                printo("- " + (" " * i) + block.replaces.lines[0])  # line 407
                printo("+ " + (" " * i) + block.lines[0])  # line 408
                printo(ajoin("+ ", into))  # line 409
                while True:  # line 410
                    op = input(" Character replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()[:1]  # type: str  # line 411
                    if op in "tb":  # line 412
                        out.extend(block.lines)  # line 412
                        break  # line 412
                    if op in "ib":  # line 413
                        out.extend(block.replaces.lines)  # line 413
                        break  # line 413
                    if op == "m":  # line 414
                        user_block_input(out)  # line 414
                        break  # line 414
            else:  # non-interactive  # line 415
                if mergeOperation == MergeOperation.REMOVE:  # line 416
                    pass  # line 416
                elif mergeOperation == MergeOperation.BOTH:  # line 417
                    out.extend(block.lines)  # line 417
                elif mergeOperation == MergeOperation.INSERT:  # line 418
                    out.extend(list(block.replaces.lines) + list(block.lines))  # line 418
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value):  # line 419
            out.extend(block.lines)  # line 419
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation.value & MergeOperation.INSERT.value:  # line 420
            out.extend(block.lines)  # line 420
# TODO ask for insert or remove as well
    return _coconut_tail_call("".join, out)  # line 422

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 424
    ''' Attempts to find sos and legacy VCS base folders.
      Returns (SOS-repo root, VCS-repo root, VCS command)
  '''  # line 427
    debug("Detecting root folders...")  # line 428
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 429
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 430
    while not os.path.exists(encode(os.path.join(path, metaFolder))):  # line 431
        contents = set(os.listdir(path))  # type: Set[str]  # line 432
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 433
        choice = None  # type: _coconut.typing.Optional[str]  # line 434
        if len(vcss) > 1:  # line 435
            choice = SVN if SVN in vcss else vcss[0]  # line 436
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 437
        elif len(vcss) > 0:  # line 438
            choice = vcss[0]  # line 438
        if not vcs[0] and choice:  # memorize current repo root  # line 439
            vcs = (path, choice)  # memorize current repo root  # line 439
        new = os.path.dirname(path)  # get parent path  # line 440
        if new == path:  # avoid infinite loop  # line 441
            break  # avoid infinite loop  # line 441
        path = new  # line 442
    if os.path.exists(encode(os.path.join(path, metaFolder))):  # found something  # line 443
        if vcs[0]:  # already detected vcs base and command  # line 444
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 444
        sos = path  # line 445
        while True:  # continue search for VCS base  # line 446
            new = os.path.dirname(path)  # get parent path  # line 447
            if new == path:  # no VCS folder found  # line 448
                return (sos, None, None)  # no VCS folder found  # line 448
            path = new  # line 449
            contents = set(os.listdir(path))  # line 450
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 451
            choice = None  # line 452
            if len(vcss) > 1:  # line 453
                choice = SVN if SVN in vcss else vcss[0]  # line 454
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 455
            elif len(vcss) > 0:  # line 456
                choice = vcss[0]  # line 456
            if choice:  # line 457
                return (sos, path, choice)  # line 457
    return (None, vcs[0], vcs[1])  # line 458

def tokenizeGlobPattern(pattern: 'str') -> 'List[GlobBlock]':  # line 460
    index = 0  # type: int  # line 461
    out = []  # type: List[GlobBlock]  # literal = True, first index  # line 462
    while index < len(pattern):  # line 463
        if pattern[index:index + 3] in ("[?]", "[*]", "[[]", "[]]"):  # line 464
            out.append(GlobBlock(False, pattern[index:index + 3], index))  # line 464
            continue  # line 464
        if pattern[index] in "*?":  # line 465
            count = 1  # type: int  # line 466
            while index + count < len(pattern) and pattern[index] == "?" and pattern[index + count] == "?":  # line 467
                count += 1  # line 467
            out.append(GlobBlock(False, pattern[index:index + count], index))  # line 468
            index += count  # line 468
            continue  # line 468
        if pattern[index:index + 2] == "[!":  # line 469
            out.append(GlobBlock(False, pattern[index:pattern.index("]", index + 2) + 1], index))  # line 469
            index += len(out[-1][1])  # line 469
            continue  # line 469
        count = 1  # line 470
        while index + count < len(pattern) and pattern[index + count] not in "*?[":  # line 471
            count += 1  # line 471
        out.append(GlobBlock(True, pattern[index:index + count], index))  # line 472
        index += count  # line 472
    return out  # line 473

def tokenizeGlobPatterns(oldPattern: 'str', newPattern: 'str') -> 'Tuple[_coconut.typing.Sequence[GlobBlock], _coconut.typing.Sequence[GlobBlock]]':  # line 475
    ot = tokenizeGlobPattern(oldPattern)  # type: List[GlobBlock]  # line 476
    nt = tokenizeGlobPattern(newPattern)  # type: List[GlobBlock]  # line 477
#  if len(ot) != len(nt): Exit("Source and target patterns can't be translated due to differing number of parsed glob markers and literal strings")
    if len([o for o in ot if not o.isLiteral]) < len([n for n in nt if not n.isLiteral]):  # line 479
        Exit("Source and target file patterns contain differing number of glob markers and can't be translated")  # line 479
    if any((O.content != N.content for O, N in zip([o for o in ot if not o.isLiteral], [n for n in nt if not n.isLiteral]))):  # line 480
        Exit("Source and target file patterns differ in semantics")  # line 480
    return (ot, nt)  # line 481

def convertGlobFiles(filenames: '_coconut.typing.Sequence[str]', oldPattern: '_coconut.typing.Sequence[GlobBlock]', newPattern: '_coconut.typing.Sequence[GlobBlock]') -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 483
    ''' Converts given filename according to specified file patterns. No support for adjacent glob markers currently. '''  # line 484
    pairs = []  # type: List[Tuple[str, str]]  # line 485
    for filename in filenames:  # line 486
        literals = [l for l in oldPattern if l.isLiteral]  # type: List[GlobBlock]  # source literals  # line 487
        nextliteral = 0  # type: int  # line 488
        parsedOld = []  # type: List[GlobBlock2]  # line 489
        index = 0  # type: int  # line 490
        for part in oldPattern:  # match everything in the old filename  # line 491
            if part.isLiteral:  # line 492
                parsedOld.append(GlobBlock2(True, part.content, part.content))  # line 492
                index += len(part.content)  # line 492
                nextliteral += 1  # line 492
            elif part.content.startswith("?"):  # line 493
                parsedOld.append(GlobBlock2(False, part.content, filename[index:index + len(part.content)]))  # line 493
                index += len(part.content)  # line 493
            elif part.content.startswith("["):  # line 494
                parsedOld.append(GlobBlock2(False, part.content, filename[index]))  # line 494
                index += 1  # line 494
            elif part.content == "*":  # line 495
                if nextliteral >= len(literals):  # line 496
                    parsedOld.append(GlobBlock2(False, part.content, filename[index:]))  # line 496
                    break  # line 496
                nxt = filename.index(literals[nextliteral].content, index)  # type: int  # also matches empty string  # line 497
                parsedOld.append(GlobBlock2(False, part.content, filename[index:nxt]))  # line 498
                index = nxt  # line 498
            else:  # line 499
                Exit("Invalid file pattern specified for move/rename")  # line 499
        globs = [g for g in parsedOld if not g.isLiteral]  # type: List[GlobBlock2]  # line 500
        literals = [l for l in newPattern if l.isLiteral]  # target literals  # line 501
        nextliteral = 0  # line 502
        nextglob = 0  # type: int  # line 502
        outname = []  # type: List[str]  # line 503
        for part in newPattern:  # generate new filename  # line 504
            if part.isLiteral:  # line 505
                outname.append(literals[nextliteral].content)  # line 505
                nextliteral += 1  # line 505
            else:  # line 506
                outname.append(globs[nextglob].matches)  # line 506
                nextglob += 1  # line 506
        pairs.append((filename, "".join(outname)))  # line 507
    return pairs  # line 508

@_coconut_tco  # line 510
def reorderRenameActions(actions: '_coconut.typing.Sequence[Tuple[str, str]]', exitOnConflict: 'bool'=True) -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 510
    ''' Attempt to put all rename actions into an order that avoids target == source names.
      Note, that it's currently not really possible to specify patterns that make this work (swapping "*" elements with a reference).
      An alternative would be to always have one (or all) files renamed to a temporary name before renaming to target filename.
  '''  # line 514
    if not actions:  # line 515
        return []  # line 515
    sources = None  # type: List[str]  # line 516
    targets = None  # type: List[str]  # line 516
    sources, targets = [list(l) for l in zip(*actions)]  # line 517
    last = len(actions)  # type: int  # line 518
    while last > 1:  # line 519
        clean = True  # type: bool  # line 520
        for i in range(1, last):  # line 521
            try:  # line 522
                index = targets[:i].index(sources[i])  # type: int  # line 523
                sources.insert(index, sources.pop(i))  # bubble up the action right before conflict  # line 524
                targets.insert(index, targets.pop(i))  # line 525
                clean = False  # line 526
            except:  # target not found in sources: good!  # line 527
                continue  # target not found in sources: good!  # line 527
        if clean:  # line 528
            break  # line 528
        last -= 1  # we know that the last entry in the list has the least conflicts, so we can disregard it in the next iteration  # line 529
    if exitOnConflict:  # line 530
        for i in range(1, len(actions)):  # line 531
            if sources[i] in targets[:i]:  # line 532
                Exit("There is no order of renaming actions that avoids copying over not-yet renamed files: '%s' is contained in matching source filenames" % (targets[i]))  # line 532
    return _coconut_tail_call(list, zip(sources, targets))  # convert to list to avoid generators  # line 533

def relativize(root: 'str', filepath: 'str') -> 'Tuple[str, str]':  # line 535
    ''' Determine OS-independent relative folder path, and relative pattern path. '''  # line 536
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(filepath)), root).replace(os.sep, SLASH)  # line 537
    return relpath, os.path.join(relpath, os.path.basename(filepath)).replace(os.sep, SLASH)  # line 538

def parseOnlyOptions(root: 'str', options: 'List[str]') -> 'Tuple[_coconut.typing.Optional[FrozenSet[str]], _coconut.typing.Optional[FrozenSet[str]]]':  # line 540
    ''' Returns set of --only arguments, and set or --except arguments. '''  # line 541
    cwd = os.getcwd()  # type: str  # line 542
    onlys = []  # type: List[str]  # zero necessary as last start position  # line 543
    excps = []  # type: List[str]  # zero necessary as last start position  # line 543
    index = 0  # type: int  # zero necessary as last start position  # line 543
    while True:  # line 544
        try:  # line 545
            index = 1 + listindex(options, "--only", index)  # line 546
            onlys.append(options[index])  # line 547
            del options[index]  # line 548
            del options[index - 1]  # line 549
        except:  # line 550
            break  # line 550
    index = 0  # line 551
    while True:  # line 552
        try:  # line 553
            index = 1 + listindex(options, "--except", index)  # line 554
            excps.append(options[index])  # line 555
            del options[index]  # line 556
            del options[index - 1]  # line 557
        except:  # line 558
            break  # line 558
    return (frozenset((relativize(root, o)[1] for o in onlys)) if onlys else None, frozenset((relativize(root, e)[1] for e in excps)) if excps else None)  # line 559
