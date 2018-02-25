#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x49ec33ea

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

try:  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
    from typing import *  # we cannot delay this import, since we need to type-check the Coconut version-detection, which again is required to know if we actually can type-check...  # line 7
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

verbose = os.environ.get("DEBUG", "False").lower() == "true" or '--verbose' in sys.argv or '-v' in sys.argv  # imported from utility, and only modified here  # line 19


# Classes
class Accessor(dict):  # line 23
    ''' Dictionary with attribute access. Writing only supported via dictionary access. '''  # line 24
    def __init__(_, mapping: 'Dict[str, Any]'):  # line 25
        dict.__init__(_, mapping)  # line 25
    @_coconut_tco  # line 26
    def __getattribute__(_, name: 'str') -> 'Any':  # line 26
        try:  # line 27
            return _[name]  # line 27
        except:  # line 28
            return _coconut_tail_call(dict.__getattribute__, _, name)  # line 28

if TYPE_CHECKING:  # line 30
    Number = TypeVar("Number", int, float)  # line 31
    class Counter(Generic[Number]):  # line 32
        ''' A simple counter. Can be augmented to return the last value instead. '''  # line 33
        def __init__(_, initial: 'Number'=0):  # line 34
            _.value = initial  # type: Number  # line 34
        def inc(_, by: 'Number'=1) -> 'Number':  # line 35
            _.value += by  # line 35
            return _.value  # line 35
else:  # line 36
    class Counter:  # line 37
        def __init__(_, initial=0):  # line 38
            _.value = initial  # line 38
        def inc(_, by=1):  # line 39
            _.value += by  # line 39
            return _.value  # line 39

class ProgressIndicator(Counter):  # line 41
    ''' Manages a rotating progress indicator. '''  # line 42
    def __init__(_, symbols: 'str', callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None):  # line 43
        super(ProgressIndicator, _).__init__(-1)  # line 43
        _.symbols = symbols  # line 43
        _.timer = time.time()  # type: float  # line 43
        _.callback = callback  # type: Optional[_coconut.typing.Callable[[str], None]]  # line 43
    def getIndicator(_) -> '_coconut.typing.Optional[str]':  # line 44
        ''' Returns a value only if a certain time has passed. '''  # line 45
        newtime = time.time()  # line 46
        if newtime - _.timer < .1:  # line 47
            return None  # line 47
        _.timer = newtime  # line 48
        sign = _.symbols[int(_.inc() % len(_.symbols))]  # type: str  # line 49
        if _.callback:  # line 50
            _.callback(sign)  # line 50
        return sign  # line 51

class Logger:  # line 53
    ''' Logger that supports many items. '''  # line 54
    def __init__(_, log):  # line 55
        _._log = log  # line 55
    def debug(_, *s):  # line 56
        _._log.debug(sjoin(*s))  # line 56
    def info(_, *s):  # line 57
        _._log.info(sjoin(*s))  # line 57
    def warn(_, *s):  # line 58
        _._log.warning(sjoin(*s))  # line 58
    def error(_, *s):  # line 59
        _._log.error(sjoin(*s))  # line 59


# Constants
_log = Logger(logging.getLogger(__name__))  # line 63
debug, info, warn, error = _log.debug, _log.info, _log.warn, _log.error  # line 63
CONFIGURABLE_FLAGS = ["strict", "track", "picky", "compress", "useChangesCommand", "useUnicodeFont"]  # type: List[str]  # line 64
CONFIGURABLE_LISTS = ["texttype", "bintype", "ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # type: List[str]  # line 65
GLOBAL_LISTS = ["ignores", "ignoreDirs", "ignoresWhitelist", "ignoreDirsWhitelist"]  # type: List[str]  # line 66
TRUTH_VALUES = ["true", "yes", "on", "1", "enable", "enabled"]  # type: List[str]  # all lower-case normalized  # line 67
FALSE_VALUES = ["false", "no", "off", "0", "disable", "disabled"]  # type: List[str]  # line 68
PROGRESS_MARKER = ["|/-\\", "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588\u2587\u2586\u2585\u2584\u2583\u2582", "\U0001f55b\U0001f550\U0001f551\U0001f552\U0001f553\U0001f554\U0001f555\U0001f556\U0001f557\U0001f558\U0001f559\U0001f55a\U0001f559\U0001f558\U0001f557\U0001f556\U0001f555\U0001f554\U0001f553\U0001f552\U0001f551\U0001f550"]  # type: List[str]  # line 69
BACKUP_SUFFIX = "_last"  # type: str  # line 70
metaFolder = ".sos"  # type: str  # line 71
DUMP_FILE = metaFolder + ".zip"  # type: str  # line 72
metaFile = ".meta"  # type: str  # line 73
metaBack = metaFile + BACKUP_SUFFIX  # type: str  # line 74
MEBI = 1 << 20  # type: int  # line 75
bufSize = MEBI  # type: int  # line 76
UTF8 = "utf_8"  # type: str  # early used constant, not defined in standard library  # line 77
SVN = "svn"  # type: str  # line 78
SLASH = "/"  # type: str  # line 79
DOT_SYMBOL = "\u00b7"  # type: str  # line 80
CROSS_SYMBOL = "\u2714"  # type: str  # line 81
CHECKMARK_SYMBOL = "\u2716"  # type: str  # line 82
PLUSMINUS_SYMBOL = "\u00b1"  # type: str  # line 83
FOLDER_SYMBOL = "\u21cc"  # type: str  # \U0001F5C0"  # HINT second one is very unlikely to be in any console font  # line 84
METADATA_FORMAT = 1  # type: int  # counter for incompatible consecutive formats  # line 85
vcsFolders = {".svn": SVN, ".git": "git", ".bzr": "bzr", ".hg": "hg", ".fslckout": "fossil", "_FOSSIL_": "fossil", ".CVS": "cvs"}  # type: Dict[str, str]  # line 86
vcsBranches = {SVN: "trunk", "git": "master", "bzr": "trunk", "hg": "default", "fossil": None, "cvs": None}  # type: Dict[str, _coconut.typing.Optional[str]]  # line 87
NL_NAMES = {None: "<No newline>", b"\r\n": "<CR+LF>", b"\n\r": "<LF+CR>", b"\n": "<LF>", b"\r": "<CR>"}  # type: Dict[bytes, str]  # line 88
defaults = Accessor({"strict": False, "track": False, "picky": False, "compress": False, "useChangesCommand": False, "useUnicodeFont": sys.platform != "win32", "texttype": ["*.md", "*.coco", "*.py", "*.pyi", "*.pth"], "bintype": [], "ignoreDirs": [".*", "__pycache__", ".mypy_cache"], "ignoreDirsWhitelist": [], "ignores": ["__coconut__.py", "*.bak", "*.py[cdo]", "*.class", ".fslckout", "_FOSSIL_", "*%s" % DUMP_FILE], "ignoresWhitelist": []})  # type: Accessor  # line 89


# Enums
MergeOperation = enum.Enum("MergeOperation", {"INSERT": 1, "REMOVE": 2, "BOTH": 3, "ASK": 4})  # insert remote changes into current, remove remote deletions from current, do both (replicates remote state), or ask per block  # line 101
MergeBlockType = enum.Enum("MergeBlockType", "KEEP INSERT REMOVE REPLACE MOVE")  # modify = intra-line changes, replace = full block replacement  # line 102


# Value types
class BranchInfo(_coconut_NamedTuple("BranchInfo", [("number", 'int'), ("ctime", 'int'), ("name", '_coconut.typing.Optional[str]'), ("inSync", 'bool'), ("tracked", 'List[str]'), ("untracked", 'List[str]'), ("parent", '_coconut.typing.Optional[int]'), ("revision", '_coconut.typing.Optional[int]')])):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 106
    __slots__ = ()  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 106
    __ne__ = _coconut.object.__ne__  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 106
    def __new__(_cls, number, ctime, name=None, inSync=False, tracked=[], untracked=[], parent=None, revision=None):  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 106
        return _coconut.tuple.__new__(_cls, (number, ctime, name, inSync, tracked, untracked, parent, revision))  # tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place  # line 106
# tracked is a list on purpose, as serialization to JSON needs effort and frequent access is not taking place
class CommitInfo(_coconut_NamedTuple("CommitInfo", [("number", 'int'), ("ctime", 'int'), ("message", '_coconut.typing.Optional[str]')])):  # line 107
    __slots__ = ()  # line 107
    __ne__ = _coconut.object.__ne__  # line 107
    def __new__(_cls, number, ctime, message=None):  # line 107
        return _coconut.tuple.__new__(_cls, (number, ctime, message))  # line 107

class PathInfo(_coconut_NamedTuple("PathInfo", [("nameHash", 'str'), ("size", '_coconut.typing.Optional[int]'), ("mtime", 'int'), ("hash", '_coconut.typing.Optional[str]')])):  # size == None means deleted in this revision  # line 108
    __slots__ = ()  # size == None means deleted in this revision  # line 108
    __ne__ = _coconut.object.__ne__  # size == None means deleted in this revision  # line 108
class ChangeSet(_coconut_NamedTuple("ChangeSet", [("additions", 'Dict[str, PathInfo]'), ("deletions", 'Dict[str, PathInfo]'), ("modifications", 'Dict[str, PathInfo]'), ("moves", 'Dict[str, Tuple[str, PathInfo]]')])):  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 109
    __slots__ = ()  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 109
    __ne__ = _coconut.object.__ne__  # avoid default assignment of {} as it leads to runtime errors (contains data on init for unknown reason)  # line 109
class Range(_coconut_NamedTuple("Range", [("tipe", 'MergeBlockType'), ("indexes", '_coconut.typing.Sequence[int]')])):  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 110
    __slots__ = ()  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 110
    __ne__ = _coconut.object.__ne__  # MergeBlockType[1,2,4], line number, length  # TODO use enum  # line 110
class MergeBlock(_coconut_NamedTuple("MergeBlock", [("tipe", 'MergeBlockType'), ("lines", 'List[str]'), ("line", 'int'), ("replaces", '_coconut.typing.Optional[MergeBlock]'), ("changes", '_coconut.typing.Optional[Range]')])):  # line 111
    __slots__ = ()  # line 111
    __ne__ = _coconut.object.__ne__  # line 111
    def __new__(_cls, tipe, lines, line, replaces=None, changes=None):  # line 111
        return _coconut.tuple.__new__(_cls, (tipe, lines, line, replaces, changes))  # line 111

class GlobBlock(_coconut_NamedTuple("GlobBlock", [("isLiteral", 'bool'), ("content", 'str'), ("index", 'int')])):  # for file pattern rename/move matching  # line 112
    __slots__ = ()  # for file pattern rename/move matching  # line 112
    __ne__ = _coconut.object.__ne__  # for file pattern rename/move matching  # line 112
class GlobBlock2(_coconut_NamedTuple("GlobBlock2", [("isLiteral", 'bool'), ("content", 'str'), ("matches", 'str')])):  # matching file pattern and input filename for translation  # line 113
    __slots__ = ()  # matching file pattern and input filename for translation  # line 113
    __ne__ = _coconut.object.__ne__  # matching file pattern and input filename for translation  # line 113


# Functions
def printo(s: 'str'="", nl: 'str'="\n"):  # PEP528 compatibility  # line 117
    tryOrDefault(lambda: (lambda _coconut_none_coalesce_item: sys.stdout if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(sys.stdout.buffer), sys.stdout).write((s + nl).encode(sys.stdout.encoding, 'backslashreplace'))  # PEP528 compatibility  # line 117
    sys.stdout.flush()  # PEP528 compatibility  # line 117
def printe(s: 'str'="", nl: 'str'="\n"):  # line 118
    tryOrDefault(lambda: (lambda _coconut_none_coalesce_item: sys.stderr if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(sys.stderr.buffer), sys.stderr).write((s + nl).encode(sys.stderr.encoding, 'backslashreplace'))  # line 118
    sys.stderr.flush()  # line 118
@_coconut_tco  # for py->os access of writing filenames  # PEP 529 compatibility  # line 119
def encode(s: 'str') -> 'bytes':  # for py->os access of writing filenames  # PEP 529 compatibility  # line 119
    return _coconut_tail_call(os.fsencode, s)  # for py->os access of writing filenames  # PEP 529 compatibility  # line 119
@_coconut_tco  # for os->py access of reading filenames  # line 120
def decode(b: 'bytes') -> 'str':  # for os->py access of reading filenames  # line 120
    return _coconut_tail_call(os.fsdecode, b)  # for os->py access of reading filenames  # line 120
try:  # line 121
    import chardet  # https://github.com/chardet/chardet  # line 122
    def detectEncoding(binary: 'bytes') -> 'str':  # line 123
        return chardet.detect(binary)["encoding"]  # line 123
except:  # line 124
    def detectEncoding(binary: 'bytes') -> 'str':  # Guess the encoding  # line 125
        ''' Fallback if chardet library missing. '''  # line 126
        try:  # line 127
            binary.decode(UTF8)  # line 127
            return UTF8  # line 127
        except UnicodeError:  # line 128
            pass  # line 128
        try:  # line 129
            binary.decode("utf_16")  # line 129
            return "utf_16"  # line 129
        except UnicodeError:  # line 130
            pass  # line 130
        try:  # line 131
            binary.decode("cp1252")  # line 131
            return "cp1252"  # line 131
        except UnicodeError:  # line 132
            pass  # line 132
        return "ascii"  # this code will never be reached, as above is an 8-bit charset that always matches  # line 133

def tryOrDefault(func: '_coconut.typing.Callable[[], Any]', default: 'Any') -> 'Any':  # line 135
    try:  # line 136
        return func()  # line 136
    except:  # line 137
        return default  # line 137

def tryOrIgnore(func: '_coconut.typing.Callable[[], Any]') -> 'None':  # handle with care!  # line 139
    try:  # line 140
        func()  # line 140
    except:  # line 141
        pass  # line 141

def removePath(key: 'str', value: 'str') -> 'str':  # line 143
    ''' Cleanup of user-specified global file patterns. '''  # line 144
    return value if value in GLOBAL_LISTS or SLASH not in value else value[value.rindex(SLASH) + 1:]  # line 145

def conditionalIntersection(a: '_coconut.typing.Optional[FrozenSet[str]]', b: 'FrozenSet[str]') -> 'FrozenSet[str]':  # Used to match only arguments, or use only stored patterns  # line 147
    return a & b if a else b  # Used to match only arguments, or use only stored patterns  # line 147

def dictUpdate(dikt: 'Dict[Any, Any]', by: 'Dict[Any, Any]') -> 'Dict[Any, Any]':  # line 149
    d = {}  # line 149
    d.update(dikt)  # line 149
    d.update(by)  # line 149
    return d  # line 149

def openIt(file: 'str', mode: 'str', compress: 'bool'=False) -> 'IO[bytes]':  # Abstraction for opening both compressed and plain files  # line 151
    return bz2.BZ2File(encode(file), mode) if compress else open(encode(file), mode + "b")  # Abstraction for opening both compressed and plain files  # line 151

def eoldet(file: 'bytes') -> '_coconut.typing.Optional[bytes]':  # line 153
    ''' Determine EOL style from a binary string. '''  # line 154
    lf = file.count(b"\n")  # type: int  # line 155
    cr = file.count(b"\r")  # type: int  # line 156
    crlf = file.count(b"\r\n")  # type: int  # line 157
    if crlf > 0:  # DOS/Windows/Symbian etc.  # line 158
        if lf != crlf or cr != crlf:  # line 159
            warn("Inconsistent CR/NL count with CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 159
        return b"\r\n"  # line 160
    if lf != 0 and cr != 0:  # line 161
        warn("Inconsistent CR/NL count without CR+NL. Mixed EOL style detected, may cause problems during merge")  # line 161
    if lf > cr:  # Linux/Unix  # line 162
        return b"\n"  # Linux/Unix  # line 162
    if cr > lf:  # older 8-bit machines  # line 163
        return b"\r"  # older 8-bit machines  # line 163
    return None  # no new line contained, cannot determine  # line 164

if TYPE_CHECKING:  # line 166
    Splittable = TypeVar("Splittable", str, bytes)  # TODO isn't that the same as AnyStr?  # line 167
    def safeSplit(s: 'Splittable', d: '_coconut.typing.Optional[Splittable]'=None) -> 'List[Splittable]':  # line 168
        return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 168
else:  # line 169
    def safeSplit(s, d=None):  # line 170
        return s.split((("\n" if isinstance(s, str) else b"\n") if d is None else d)) if len(s) > 0 else []  # line 170

def ajoin(sep: 'str', seq: '_coconut.typing.Sequence[str]', nl: 'str'="") -> 'str':  # line 172
    return (sep + (nl + sep).join(seq)) if seq else ""  # line 172

@_coconut_tco  # line 174
def sjoin(*s: 'Tuple[Any]') -> 'str':  # line 174
    return _coconut_tail_call(" ".join, [str(e) for e in s if e != ''])  # line 174

@_coconut_tco  # line 176
def hashStr(datas: 'str') -> 'str':  # line 176
    return _coconut_tail_call(hashlib.sha256(datas.encode(UTF8)).hexdigest)  # line 176

def modified(changes: 'ChangeSet', onlyBinary: 'bool'=False) -> 'bool':  # line 178
    return len(changes.additions) > 0 or len(changes.deletions) > 0 or len(changes.modifications) > 0 or len(changes.moves) > 0  # line 178

def listindex(lizt: 'Sequence[Any]', what: 'Any', index: 'int'=0) -> 'int':  # line 180
    return lizt[index:].index(what) + index  # line 180

def getTermWidth() -> 'int':  # line 182
    try:  # line 183
        import termwidth  # line 183
    except:  # line 184
        return 80  # line 184
    return termwidth.getTermWidth()[0]  # line 185
termWidth = getTermWidth() - 1  # uses curses or returns conservative default of 80  # line 186

@_coconut_tco  # TODO currently unused!  # line 188
def wcswidth(string: 'str') -> 'int':  # TODO currently unused!  # line 188
    try:  # line 189
        l = wcwidth.wcswitdh(string)  # type: int  # line 190
        return len(string) if l < 0 else l  # line 191
    except:  # line 192
        return _coconut_tail_call(len, string)  # line 192

def ljust(string: 'str', width: 'int'=termWidth) -> 'str':  # line 194
    assert width > 0  # line 195
    return string + " " * max(0, width - wcswidth(string))  # line 196

def branchFolder(branch: 'int', base: '_coconut.typing.Optional[str]'=None, file: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 198
    return os.path.join((os.getcwd() if base is None else base), metaFolder, "b%d" % branch) + ((os.sep + file) if file else "")  # line 198

def revisionFolder(branch: 'int', revision: 'int', base: '_coconut.typing.Optional[str]'=None, file: '_coconut.typing.Optional[str]'=None) -> 'str':  # line 200
    return os.path.join(branchFolder(branch, base), "r%d" % revision) + ((os.sep + file) if file else "")  # line 200

def Exit(message: 'str'="", code=1):  # line 202
    printe("[EXIT%s]" % (" %.1fs" % (time.time() - START_TIME) if verbose else "") + (" " + message + "." if message != "" else ""))  # line 202
    sys.exit(code)  # line 202

def exception(E):  # line 204
    ''' Report an exception to the user to enable useful bug reporting. '''  # line 205
    printo(str(E))  # line 206
    import traceback  # line 207
    traceback.print_exc()  # line 208
    traceback.print_stack()  # line 209

def hashFile(path: 'str', compress: 'bool', saveTo: '_coconut.typing.Optional[str]'=None, callback: 'Optional[_coconut.typing.Callable[[str], None]]'=None, symbols: 'str'=PROGRESS_MARKER[0]) -> 'Tuple[str, int]':  # line 211
    ''' Calculate hash of file contents, and return compressed sized, if in write mode, or zero. '''  # line 212
    indicator = ProgressIndicator(symbols, callback) if callback else None  # type: _coconut.typing.Optional[ProgressIndicator]  # line 213
    _hash = hashlib.sha256()  # line 214
    wsize = 0  # type: int  # line 215
    if saveTo and os.path.exists(encode(saveTo)):  # line 216
        Exit("Hash conflict. Leaving revision in inconsistent state. This should happen only once in a lifetime")  # line 216
    to = openIt(saveTo, "w", compress) if saveTo else None  # line 217
    with open(encode(path), "rb") as fd:  # line 218
        while True:  # line 219
            buffer = fd.read(bufSize)  # type: bytes  # line 220
            _hash.update(buffer)  # line 221
            if to:  # line 222
                to.write(buffer)  # line 222
            if len(buffer) < bufSize:  # line 223
                break  # line 223
            if indicator:  # line 224
                indicator.getIndicator()  # line 224
        if to:  # line 225
            to.close()  # line 226
            wsize = os.stat(encode(saveTo)).st_size  # line 227
    return (_hash.hexdigest(), wsize)  # line 228

def getAnyOfMap(map: 'Dict[str, Any]', params: '_coconut.typing.Sequence[str]', default: 'Any'=None) -> 'Any':  # line 230
    ''' Utility to find any entries of a dictionary in a list to return the dictionaries value. '''  # line 231
    for k, v in map.items():  # line 232
        if k in params:  # line 233
            return v  # line 233
    return default  # line 234

@_coconut_tco  # line 236
def strftime(timestamp: '_coconut.typing.Optional[int]'=None) -> 'str':  # line 236
    return _coconut_tail_call(time.strftime, "%Y-%m-%d %H:%M:%S", time.localtime(timestamp / 1000. if timestamp is not None else None))  # line 236

def detectAndLoad(filename: '_coconut.typing.Optional[str]'=None, content: '_coconut.typing.Optional[bytes]'=None, ignoreWhitespace: 'bool'=False) -> 'Tuple[str, bytes, _coconut.typing.Sequence[str]]':  # line 238
    lines = []  # type: _coconut.typing.Sequence[str]  # line 239
    if filename is not None:  # line 240
        with open(encode(filename), "rb") as fd:  # line 241
            content = fd.read()  # line 241
    encoding = (lambda _coconut_none_coalesce_item: sys.getdefaultencoding() if _coconut_none_coalesce_item is None else _coconut_none_coalesce_item)(detectEncoding(content))  # type: str  # line 242
    eol = eoldet(content)  # type: _coconut.typing.Optional[bytes]  # line 243
    if filename is not None:  # line 244
        with codecs.open(encode(filename), encoding=encoding) as fd2:  # line 245
            lines = safeSplit(fd2.read(), ((b"\n" if eol is None else eol)).decode(encoding))  # line 245
    elif content is not None:  # line 246
        lines = safeSplit(content.decode(encoding), ((b"\n" if eol is None else eol)).decode(encoding))  # line 247
    else:  # line 248
        return (sys.getdefaultencoding(), b"\n", [])  # line 248
    if ignoreWhitespace:  # line 249
        lines[:] = [line.replace("\t", "  ").strip() for line in lines]  # line 249
    return (encoding, eol, lines)  # line 250

if TYPE_CHECKING:  # line 252
    DataType = TypeVar("DataType", BranchInfo, ChangeSet, MergeBlock, PathInfo)  # line 253
    @_coconut_tco  # line 254
    def dataCopy(_tipe: 'Type[DataType]', _old: 'DataType', *_args, byValue: 'bool'=False, **_kwargs) -> 'DataType':  # line 254
        ''' A better makedata() version. '''  # line 255
        r = _old._asdict()  # type: Dict[str, Any]  # line 256
        r.update({k: ([e for e in v] if byValue and isinstance(v, (list, tuple, set)) else v) for k, v in _kwargs.items()})  # copy by value if required  # line 257
        return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # TODO also offer copy-by-value here  # line 258
else:  # line 259
    @_coconut_tco  # line 260
    def dataCopy(_tipe, _old, *_args, byValue=False, **_kwargs) -> 'DataType':  # line 260
        ''' A better makedata() version. '''  # line 261
        r = _old._asdict()  # line 262
        r.update({k: ([e for e in v] if byValue and isinstance(v, (list, tuple, set)) else v) for k, v in _kwargs.items()})  # copy by value if required  # line 263
        return _coconut_tail_call(makedata, _tipe, *(list(_args) + [r[field] for field in _old._fields]))  # TODO also offer copy-by-value here  # line 264

def detectMoves(changes: 'ChangeSet') -> 'Dict[str, Tuple[str, PathInfo]]':  # line 266
    ''' Compute renames/removes for a changeset. '''  # line 267
    moves = {}  # type: Dict[str, Tuple[str, PathInfo]]  # line 268
    for path, info in changes.additions.items():  # line 269
        for dpath, dinfo in changes.deletions.items():  # line 270
            if info.size == dinfo.size and info.mtime == dinfo.mtime and info.hash == dinfo.hash:  # was moved TODO check either mtime or hash?  # line 271
                moves[path] = (dpath, info)  # store new data and original name, but don't remove add/del  # line 272
                break  # deletions loop, continue with next addition  # line 273
    return moves  # line 274

def user_block_input(output: 'List[str]'):  # line 276
    sep = input("Enter end-of-text marker (default: <empty line>: ")  # type: str  # line 277
    line = sep  # type: str  # line 277
    while True:  # line 278
        line = input("> ")  # line 279
        if line == sep:  # line 280
            break  # line 280
        output.append(line)  # writes to caller-provided list reference  # line 281

def merge(file: '_coconut.typing.Optional[bytes]'=None, into: '_coconut.typing.Optional[bytes]'=None, filename: '_coconut.typing.Optional[str]'=None, intoname: '_coconut.typing.Optional[str]'=None, mergeOperation: 'MergeOperation'=MergeOperation.BOTH, charMergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False, eol: 'bool'=False, ignoreWhitespace: 'bool'=False) -> 'Tuple[Union[bytes, List[MergeBlock]], _coconut.typing.Optional[bytes]]':  # line 283
    ''' Merges other binary text contents 'file' (or reads file 'filename') into current text contents 'into' (or reads file 'intoname'), returning merged result.
      For update, the other version is assumed to be the "new/added" one, while for diff, the current changes are the ones "added".
      However, change direction markers are insert ("+") for elements only in into, and remove ("-") for elements only in other file (just like the diff marks +/-)
      diffOnly returns detected change blocks only, no text merging
      eol flag will use the other file's EOL marks
      in case of replace block and INSERT strategy, the change will be added **behind** the original
  '''  # line 298
    encoding = None  # type: str  # line 299
    othr = None  # type: _coconut.typing.Sequence[str]  # line 299
    othreol = None  # type: _coconut.typing.Optional[bytes]  # line 299
    curr = None  # type: _coconut.typing.Sequence[str]  # line 299
    curreol = None  # type: _coconut.typing.Optional[bytes]  # line 299
    try:  # load files line-wise and normalize line endings (keep the one of the current file) TODO document  # line 300
        encoding, othreol, othr = detectAndLoad(filename=filename, content=file, ignoreWhitespace=ignoreWhitespace)  # line 301
        encoding, curreol, curr = detectAndLoad(filename=intoname, content=into, ignoreWhitespace=ignoreWhitespace)  # line 302
    except Exception as E:  # line 303
        Exit("Cannot merge '%s' into '%s': %r" % (filename, intoname, E))  # line 303
    if None not in [othreol, curreol] and othreol != curreol:  # line 304
        warn("Differing EOL-styles detected during merge. Using current file's style for merged output")  # line 304
    output = list(difflib.Differ().compare(othr, curr))  # type: List[str]  # from generator expression  # line 305
    blocks = []  # type: List[MergeBlock]  # merged result in blocks  # line 306
    tmp = []  # type: List[str]  # block lines  # line 307
    last = " "  # type: str  # line 308
    no = None  # type: int  # line 308
    line = None  # type: str  # line 308
    for no, line in enumerate(output + ["X"]):  # EOF marker (difflib's output will never be "X" alone)  # line 309
        if line[0] == last:  # continue filling current block, no matter what type of block it is  # line 310
            tmp.append(line[2:])  # continue filling current block, no matter what type of block it is  # line 310
            continue  # continue filling current block, no matter what type of block it is  # line 310
        if line == "X" and len(tmp) == 0:  # break if nothing left to do, otherwise perform operation for stored block  # line 311
            break  # break if nothing left to do, otherwise perform operation for stored block  # line 311
        if last == " ":  # block is same in both files  # line 312
            if len(tmp) > 0:  # avoid adding empty keep block  # line 313
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line for line in tmp], line=no - len(tmp)))  # avoid adding empty keep block  # line 313
        elif last == "-":  # may be a pure deletion or part of a replacement (with next block being "+")  # line 314
            blocks.append(MergeBlock(MergeBlockType.REMOVE, [line for line in tmp], line=no - len(tmp)))  # line 315
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.INSERT:  # line 316
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-1].lines, line=no - len(tmp) - 1, replaces=blocks[-2])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 317
                blocks.pop()  # line 318
        elif last == "+":  # may be insertion or replacement (with previous - block)  # line 319
            blocks.append(MergeBlock(MergeBlockType.INSERT, [line for line in tmp], line=no - len(tmp)))  # first, assume simple insertion, then check for replacement  # line 320
            if len(blocks) >= 2 and blocks[-2].tipe == MergeBlockType.REMOVE:  #  and len(blocks[-1].lines) == len(blocks[-2].lines):  # requires previous block and same number of lines TODO allow multiple intra-line merge for same-length blocks  # line 321
                blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, line=no - len(tmp) - 1, replaces=blocks[-1])  # remember replaced stuff with reference to other merge block TODO why -1 necessary?  # line 322
                blocks.pop()  # remove TOS due to merging two blocks into replace or modify  # line 323
#    elif last == "?": pass # marker for intra-line change comment -> add to block info
        last = line[0]  # line 325
        tmp[:] = [line[2:]]  # only keep current line for next block  # line 326
# TODO add code to detect block moves here
    nl = othreol if eol else ((othreol if curreol is None else curreol))  # type: bytes  # no default newline, to mark "no newline"  # line 328
    debug("Diff blocks: " + repr(blocks))  # line 329
    if diffOnly:  # line 330
        return (blocks, nl)  # line 330

# now perform merge operations depending on detected blocks
    output[:] = []  # clean list of strings  # line 333
    for block in blocks:  # line 334
        if block.tipe == MergeBlockType.KEEP:  # line 335
            output.extend(block.lines)  # line 336
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value) or block.tipe == MergeBlockType.REMOVE and (mergeOperation.value & MergeOperation.INSERT.value):  # line 337
            output.extend(block.lines)  # line 339
        elif block.tipe == MergeBlockType.REPLACE:  # complete block replacement  # line 340
            if len(block.lines) == len(block.replaces.lines) == 1:  # one-liner  # line 341
                output.append(lineMerge(block.lines[0], block.replaces.lines[0], mergeOperation=charMergeOperation))  # line 342
            elif mergeOperation == MergeOperation.ASK:  # more than one line: needs user input  # line 343
                printo(ajoin("- ", block.replaces.lines, nl="\n"))  # TODO check +/- in update mode, could be swapped  # line 344
                printo(ajoin("+ ", block.lines, nl="\n"))  # line 345
                while True:  # line 346
                    op = input(" Line replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 347
                    if op in "tb":  # line 348
                        output.extend(block.lines)  # line 348
                        break  # line 348
                    if op in "ib":  # line 349
                        output.extend(block.replaces.lines)  # line 349
                        break  # line 349
                    if op == "m":  # line 350
                        user_block_input(output)  # line 350
                        break  # line 350
            else:  # more than one line and not ask  # line 351
                if mergeOperation == MergeOperation.REMOVE:  # line 352
                    pass  # line 352
                elif mergeOperation == MergeOperation.BOTH:  # line 353
                    output.extend(block.lines)  # line 353
                elif mergeOperation == MergeOperation.INSERT:  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 354
                    output.extend(list(block.replaces.lines) + list(block.lines))  # TODO optionally allow insertion BEFORE or AFTER original (order of these both lines)  # line 354
#  debug("Merge output: " + "; ".join(output))
    return (((b"\n" if nl is None else nl)).join([line.encode(encoding) for line in output]), nl)  # returning bytes  # line 356
# TODO handle check for more/less lines in found -/+ blocks to find common section and splitting prefix/suffix out

@_coconut_tco  # line 359
def lineMerge(othr: 'str', into: 'str', mergeOperation: 'MergeOperation'=MergeOperation.BOTH, diffOnly: 'bool'=False) -> 'Union[str, List[MergeBlock]]':  # line 359
    ''' Merges string 'othr' into current string 'into'.
      change direction mark is insert for elements only in into, and remove for elements only in file (according to diff marks +/-)
  '''  # line 362
    out = list(difflib.Differ().compare(othr, into))  # type: List[str]  # line 363
    blocks = []  # type: List[MergeBlock]  # line 364
    for i, line in enumerate(out):  # line 365
        if line[0] == "+":  # line 366
            if i + 1 < len(out) and out[i + 1][0] == "+":  # block will continue  # line 367
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # middle of + block  # line 368
                    blocks[-1].lines.append(line[2])  # add one more character to the accumulating list  # line 369
                else:  # first + in block  # line 370
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 371
            else:  # last line of + block  # line 372
                if i > 0 and blocks[-1].tipe == MergeBlockType.INSERT:  # end of a block  # line 373
                    blocks[-1].lines.append(line[2])  # line 374
                else:  # single line  # line 375
                    blocks.append(MergeBlock(MergeBlockType.INSERT, [line[2]], i))  # line 376
                if i >= 1 and blocks[-2].tipe == MergeBlockType.REMOVE:  # previous - and now last in + block creates a replacement block  # line 377
                    blocks[-2] = MergeBlock(MergeBlockType.REPLACE, blocks[-2].lines, i, replaces=blocks[-1])  # line 378
                    blocks.pop()  # line 378
        elif line[0] == "-":  # line 379
            if i > 0 and blocks[-1].tipe == MergeBlockType.REMOVE:  # part of - block  # line 380
                blocks[-1].lines.append(line[2])  # line 381
            else:  # first in block  # line 382
                blocks.append(MergeBlock(MergeBlockType.REMOVE, [line[2]], i))  # line 383
        elif line[0] == " ":  # line 384
            if i > 0 and blocks[-1].tipe == MergeBlockType.KEEP:  # part of block  # line 385
                blocks[-1].lines.append(line[2])  # line 386
            else:  # first in block  # line 387
                blocks.append(MergeBlock(MergeBlockType.KEEP, [line[2]], i))  # line 388
        else:  # line 389
            raise Exception("Cannot parse diff line %r" % line)  # line 389
    blocks[:] = [dataCopy(MergeBlock, block, lines=["".join(block.lines)], replaces=dataCopy(MergeBlock, block.replaces, lines=["".join(block.replaces.lines)]) if block.replaces else None) for block in blocks]  # line 390
    if diffOnly:  # line 391
        return blocks  # line 391
    out[:] = []  # line 392
    for i, block in enumerate(blocks):  # line 393
        if block.tipe == MergeBlockType.KEEP:  # line 394
            out.extend(block.lines)  # line 394
        elif block.tipe == MergeBlockType.REPLACE:  # line 395
            if mergeOperation == MergeOperation.ASK:  # line 396
                printo(ajoin("- ", othr))  # line 397
                printo("- " + (" " * i) + block.replaces.lines[0])  # line 398
                printo("+ " + (" " * i) + block.lines[0])  # line 399
                printo(ajoin("+ ", into))  # line 400
                while True:  # line 401
                    op = input(" Character replacement: *M[I]ne (+), [T]heirs (-), [B]oth, [U]ser input: ").strip().lower()  # type: str  # line 402
                    if op in "tb":  # line 403
                        out.extend(block.lines)  # line 403
                        break  # line 403
                    if op in "ib":  # line 404
                        out.extend(block.replaces.lines)  # line 404
                        break  # line 404
                    if op == "m":  # line 405
                        user_block_input(out)  # line 405
                        break  # line 405
            else:  # non-interactive  # line 406
                if mergeOperation == MergeOperation.REMOVE:  # line 407
                    pass  # line 407
                elif mergeOperation == MergeOperation.BOTH:  # line 408
                    out.extend(block.lines)  # line 408
                elif mergeOperation == MergeOperation.INSERT:  # line 409
                    out.extend(list(block.replaces.lines) + list(block.lines))  # line 409
        elif block.tipe == MergeBlockType.INSERT and not (mergeOperation.value & MergeOperation.REMOVE.value):  # line 410
            out.extend(block.lines)  # line 410
        elif block.tipe == MergeBlockType.REMOVE and mergeOperation.value & MergeOperation.INSERT.value:  # line 411
            out.extend(block.lines)  # line 411
# TODO ask for insert or remove as well
    return _coconut_tail_call("".join, out)  # line 413

def findSosVcsBase() -> 'Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str], _coconut.typing.Optional[str]]':  # line 415
    ''' Attempts to find sos and legacy VCS base folders.
      Returns (SOS-repo root, VCS-repo root, VCS command)
  '''  # line 418
    debug("Detecting root folders...")  # line 419
    path = os.getcwd()  # type: str  # start in current folder, check parent until found or stopped  # line 420
    vcs = (None, None)  # type: Tuple[_coconut.typing.Optional[str], _coconut.typing.Optional[str]]  # line 421
    while not os.path.exists(encode(os.path.join(path, metaFolder))):  # line 422
        contents = set(os.listdir(path))  # type: Set[str]  # line 423
        vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # type: _coconut.typing.Sequence[str]  # determine VCS type from dot folder  # line 424
        choice = None  # type: _coconut.typing.Optional[str]  # line 425
        if len(vcss) > 1:  # line 426
            choice = SVN if SVN in vcss else vcss[0]  # line 427
            warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 428
        elif len(vcss) > 0:  # line 429
            choice = vcss[0]  # line 429
        if not vcs[0] and choice:  # memorize current repo root  # line 430
            vcs = (path, choice)  # memorize current repo root  # line 430
        new = os.path.dirname(path)  # get parent path  # line 431
        if new == path:  # avoid infinite loop  # line 432
            break  # avoid infinite loop  # line 432
        path = new  # line 433
    if os.path.exists(encode(os.path.join(path, metaFolder))):  # found something  # line 434
        if vcs[0]:  # already detected vcs base and command  # line 435
            return (path, vcs[0], vcs[1])  # already detected vcs base and command  # line 435
        sos = path  # line 436
        while True:  # continue search for VCS base  # line 437
            new = os.path.dirname(path)  # get parent path  # line 438
            if new == path:  # no VCS folder found  # line 439
                return (sos, None, None)  # no VCS folder found  # line 439
            path = new  # line 440
            contents = set(os.listdir(path))  # line 441
            vcss = [executable for folder, executable in vcsFolders.items() if folder in contents]  # determine VCS type  # line 442
            choice = None  # line 443
            if len(vcss) > 1:  # line 444
                choice = SVN if SVN in vcss else vcss[0]  # line 445
                warn("Detected more than one parallel VCS checkouts %r. Falling back to '%s'" % (vcss, choice))  # line 446
            elif len(vcss) > 0:  # line 447
                choice = vcss[0]  # line 447
            if choice:  # line 448
                return (sos, path, choice)  # line 448
    return (None, vcs[0], vcs[1])  # line 449

def tokenizeGlobPattern(pattern: 'str') -> 'List[GlobBlock]':  # line 451
    index = 0  # type: int  # line 452
    out = []  # type: List[GlobBlock]  # literal = True, first index  # line 453
    while index < len(pattern):  # line 454
        if pattern[index:index + 3] in ("[?]", "[*]", "[[]", "[]]"):  # line 455
            out.append(GlobBlock(False, pattern[index:index + 3], index))  # line 455
            continue  # line 455
        if pattern[index] in "*?":  # line 456
            count = 1  # type: int  # line 457
            while index + count < len(pattern) and pattern[index] == "?" and pattern[index + count] == "?":  # line 458
                count += 1  # line 458
            out.append(GlobBlock(False, pattern[index:index + count], index))  # line 459
            index += count  # line 459
            continue  # line 459
        if pattern[index:index + 2] == "[!":  # line 460
            out.append(GlobBlock(False, pattern[index:pattern.index("]", index + 2) + 1], index))  # line 460
            index += len(out[-1][1])  # line 460
            continue  # line 460
        count = 1  # line 461
        while index + count < len(pattern) and pattern[index + count] not in "*?[":  # line 462
            count += 1  # line 462
        out.append(GlobBlock(True, pattern[index:index + count], index))  # line 463
        index += count  # line 463
    return out  # line 464

def tokenizeGlobPatterns(oldPattern: 'str', newPattern: 'str') -> 'Tuple[_coconut.typing.Sequence[GlobBlock], _coconut.typing.Sequence[GlobBlock]]':  # line 466
    ot = tokenizeGlobPattern(oldPattern)  # type: List[GlobBlock]  # line 467
    nt = tokenizeGlobPattern(newPattern)  # type: List[GlobBlock]  # line 468
#  if len(ot) != len(nt): Exit("Source and target patterns can't be translated due to differing number of parsed glob markers and literal strings")
    if len([o for o in ot if not o.isLiteral]) < len([n for n in nt if not n.isLiteral]):  # line 470
        Exit("Source and target file patterns contain differing number of glob markers and can't be translated")  # line 470
    if any((O.content != N.content for O, N in zip([o for o in ot if not o.isLiteral], [n for n in nt if not n.isLiteral]))):  # line 471
        Exit("Source and target file patterns differ in semantics")  # line 471
    return (ot, nt)  # line 472

def convertGlobFiles(filenames: '_coconut.typing.Sequence[str]', oldPattern: '_coconut.typing.Sequence[GlobBlock]', newPattern: '_coconut.typing.Sequence[GlobBlock]') -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 474
    ''' Converts given filename according to specified file patterns. No support for adjacent glob markers currently. '''  # line 475
    pairs = []  # type: List[Tuple[str, str]]  # line 476
    for filename in filenames:  # line 477
        literals = [l for l in oldPattern if l.isLiteral]  # type: List[GlobBlock]  # source literals  # line 478
        nextliteral = 0  # type: int  # line 479
        parsedOld = []  # type: List[GlobBlock2]  # line 480
        index = 0  # type: int  # line 481
        for part in oldPattern:  # match everything in the old filename  # line 482
            if part.isLiteral:  # line 483
                parsedOld.append(GlobBlock2(True, part.content, part.content))  # line 483
                index += len(part.content)  # line 483
                nextliteral += 1  # line 483
            elif part.content.startswith("?"):  # line 484
                parsedOld.append(GlobBlock2(False, part.content, filename[index:index + len(part.content)]))  # line 484
                index += len(part.content)  # line 484
            elif part.content.startswith("["):  # line 485
                parsedOld.append(GlobBlock2(False, part.content, filename[index]))  # line 485
                index += 1  # line 485
            elif part.content == "*":  # line 486
                if nextliteral >= len(literals):  # line 487
                    parsedOld.append(GlobBlock2(False, part.content, filename[index:]))  # line 487
                    break  # line 487
                nxt = filename.index(literals[nextliteral].content, index)  # type: int  # also matches empty string  # line 488
                parsedOld.append(GlobBlock2(False, part.content, filename[index:nxt]))  # line 489
                index = nxt  # line 489
            else:  # line 490
                Exit("Invalid file pattern specified for move/rename")  # line 490
        globs = [g for g in parsedOld if not g.isLiteral]  # type: List[GlobBlock2]  # line 491
        literals = [l for l in newPattern if l.isLiteral]  # target literals  # line 492
        nextliteral = 0  # line 493
        nextglob = 0  # type: int  # line 493
        outname = []  # type: List[str]  # line 494
        for part in newPattern:  # generate new filename  # line 495
            if part.isLiteral:  # line 496
                outname.append(literals[nextliteral].content)  # line 496
                nextliteral += 1  # line 496
            else:  # line 497
                outname.append(globs[nextglob].matches)  # line 497
                nextglob += 1  # line 497
        pairs.append((filename, "".join(outname)))  # line 498
    return pairs  # line 499

@_coconut_tco  # line 501
def reorderRenameActions(actions: '_coconut.typing.Sequence[Tuple[str, str]]', exitOnConflict: 'bool'=True) -> '_coconut.typing.Sequence[Tuple[str, str]]':  # line 501
    ''' Attempt to put all rename actions into an order that avoids target == source names.
      Note, that it's currently not really possible to specify patterns that make this work (swapping "*" elements with a reference).
      An alternative would be to always have one (or all) files renamed to a temporary name before renaming to target filename.
  '''  # line 505
    if not actions:  # line 506
        return []  # line 506
    sources = None  # type: List[str]  # line 507
    targets = None  # type: List[str]  # line 507
    sources, targets = [list(l) for l in zip(*actions)]  # line 508
    last = len(actions)  # type: int  # line 509
    while last > 1:  # line 510
        clean = True  # type: bool  # line 511
        for i in range(1, last):  # line 512
            try:  # line 513
                index = targets[:i].index(sources[i])  # type: int  # line 514
                sources.insert(index, sources.pop(i))  # bubble up the action right before conflict  # line 515
                targets.insert(index, targets.pop(i))  # line 516
                clean = False  # line 517
            except:  # target not found in sources: good!  # line 518
                continue  # target not found in sources: good!  # line 518
        if clean:  # line 519
            break  # line 519
        last -= 1  # we know that the last entry in the list has the least conflicts, so we can disregard it in the next iteration  # line 520
    if exitOnConflict:  # line 521
        for i in range(1, len(actions)):  # line 522
            if sources[i] in targets[:i]:  # line 523
                Exit("There is no order of renaming actions that avoids copying over not-yet renamed files: '%s' is contained in matching source filenames" % (targets[i]))  # line 523
    return _coconut_tail_call(list, zip(sources, targets))  # convert to list to avoid generators  # line 524

def relativize(root: 'str', filepath: 'str') -> 'Tuple[str, str]':  # line 526
    ''' Determine OS-independent relative folder path, and relative pattern path. '''  # line 527
    relpath = os.path.relpath(os.path.dirname(os.path.abspath(filepath)), root).replace(os.sep, SLASH)  # line 528
    return relpath, os.path.join(relpath, os.path.basename(filepath)).replace(os.sep, SLASH)  # line 529

def parseOnlyOptions(root: 'str', options: 'List[str]') -> 'Tuple[_coconut.typing.Optional[FrozenSet[str]], _coconut.typing.Optional[FrozenSet[str]]]':  # line 531
    ''' Returns set of --only arguments, and set or --except arguments. '''  # line 532
    cwd = os.getcwd()  # type: str  # line 533
    onlys = []  # type: List[str]  # zero necessary as last start position  # line 534
    excps = []  # type: List[str]  # zero necessary as last start position  # line 534
    index = 0  # type: int  # zero necessary as last start position  # line 534
    while True:  # line 535
        try:  # line 536
            index = 1 + listindex(options, "--only", index)  # line 537
            onlys.append(options[index])  # line 538
            del options[index]  # line 539
            del options[index - 1]  # line 540
        except:  # line 541
            break  # line 541
    index = 0  # line 542
    while True:  # line 543
        try:  # line 544
            index = 1 + listindex(options, "--except", index)  # line 545
            excps.append(options[index])  # line 546
            del options[index]  # line 547
            del options[index - 1]  # line 548
        except:  # line 549
            break  # line 549
    return (frozenset((relativize(root, o)[1] for o in onlys)) if onlys else None, frozenset((relativize(root, e)[1] for e in excps)) if excps else None)  # line 550
