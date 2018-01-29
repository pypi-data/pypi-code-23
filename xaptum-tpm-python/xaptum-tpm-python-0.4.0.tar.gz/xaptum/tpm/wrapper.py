'''
Generated using ctypesgen
'''

__docformat__ =  'restructuredtext'

# Begin preamble

import ctypes, os, sys
from ctypes import *

_int_types = (c_int16, c_int32)
if hasattr(ctypes, 'c_int64'):
    # Some builds of ctypes apparently do not have c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (c_int64,)
for t in _int_types:
    if sizeof(t) == sizeof(c_size_t):
        c_ptrdiff_t = t
del t
del _int_types

class c_void(Structure):
    # c_void_p is a buggy return type, converting to int, so
    # POINTER(None) == c_void_p is actually written as
    # POINTER(c_void), so it can be treated as a real pointer.
    _fields_ = [('dummy', c_int)]

def POINTER(obj):
    p = ctypes.POINTER(obj)

    # Convert None to a real NULL pointer to work around bugs
    # in how ctypes handles None on 64-bit platforms
    if not isinstance(p.from_param, classmethod):
        def from_param(cls, x):
            if x is None:
                return cls()
            else:
                return x
        p.from_param = classmethod(from_param)

    return p

class UserString:
    def __init__(self, seq):
        if isinstance(seq, basestring):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq)
    def __str__(self): return str(self.data)
    def __repr__(self): return repr(self.data)
    def __int__(self): return int(self.data)
    def __long__(self): return long(self.data)
    def __float__(self): return float(self.data)
    def __complex__(self): return complex(self.data)
    def __hash__(self): return hash(self.data)

    def __cmp__(self, string):
        if isinstance(string, UserString):
            return cmp(self.data, string.data)
        else:
            return cmp(self.data, string)
    def __contains__(self, char):
        return char in self.data

    def __len__(self): return len(self.data)
    def __getitem__(self, index): return self.__class__(self.data[index])
    def __getslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, basestring):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other))
    def __radd__(self, other):
        if isinstance(other, basestring):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other) + self.data)
    def __mul__(self, n):
        return self.__class__(self.data*n)
    __rmul__ = __mul__
    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self): return self.__class__(self.data.capitalize())
    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))
    def count(self, sub, start=0, end=sys.maxint):
        return self.data.count(sub, start, end)
    def decode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())
    def encode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())
    def endswith(self, suffix, start=0, end=sys.maxint):
        return self.data.endswith(suffix, start, end)
    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))
    def find(self, sub, start=0, end=sys.maxint):
        return self.data.find(sub, start, end)
    def index(self, sub, start=0, end=sys.maxint):
        return self.data.index(sub, start, end)
    def isalpha(self): return self.data.isalpha()
    def isalnum(self): return self.data.isalnum()
    def isdecimal(self): return self.data.isdecimal()
    def isdigit(self): return self.data.isdigit()
    def islower(self): return self.data.islower()
    def isnumeric(self): return self.data.isnumeric()
    def isspace(self): return self.data.isspace()
    def istitle(self): return self.data.istitle()
    def isupper(self): return self.data.isupper()
    def join(self, seq): return self.data.join(seq)
    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))
    def lower(self): return self.__class__(self.data.lower())
    def lstrip(self, chars=None): return self.__class__(self.data.lstrip(chars))
    def partition(self, sep):
        return self.data.partition(sep)
    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))
    def rfind(self, sub, start=0, end=sys.maxint):
        return self.data.rfind(sub, start, end)
    def rindex(self, sub, start=0, end=sys.maxint):
        return self.data.rindex(sub, start, end)
    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))
    def rpartition(self, sep):
        return self.data.rpartition(sep)
    def rstrip(self, chars=None): return self.__class__(self.data.rstrip(chars))
    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)
    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)
    def splitlines(self, keepends=0): return self.data.splitlines(keepends)
    def startswith(self, prefix, start=0, end=sys.maxint):
        return self.data.startswith(prefix, start, end)
    def strip(self, chars=None): return self.__class__(self.data.strip(chars))
    def swapcase(self): return self.__class__(self.data.swapcase())
    def title(self): return self.__class__(self.data.title())
    def translate(self, *args):
        return self.__class__(self.data.translate(*args))
    def upper(self): return self.__class__(self.data.upper())
    def zfill(self, width): return self.__class__(self.data.zfill(width))

class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""
    def __init__(self, string=""):
        self.data = string
    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")
    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + sub + self.data[index+1:]
    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + self.data[index+1:]
    def __setslice__(self, start, end, sub):
        start = max(start, 0); end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start]+sub.data+self.data[end:]
        elif isinstance(sub, basestring):
            self.data = self.data[:start]+sub+self.data[end:]
        else:
            self.data =  self.data[:start]+str(sub)+self.data[end:]
    def __delslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]
    def immutable(self):
        return UserString(self.data)
    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, basestring):
            self.data += other
        else:
            self.data += str(other)
        return self
    def __imul__(self, n):
        self.data *= n
        return self

class String(MutableString, Union):

    _fields_ = [('raw', POINTER(c_char)),
                ('data', c_char_p)]

    def __init__(self, obj=""):
        if isinstance(obj, (str, unicode, UserString)):
            self.data = str(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(POINTER(c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj)

        # Convert from c_char_p
        elif isinstance(obj, c_char_p):
            return obj

        # Convert from POINTER(c_char)
        elif isinstance(obj, POINTER(c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(cast(obj, POINTER(c_char)))

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)
    from_param = classmethod(from_param)

def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)

# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to c_void_p.
def UNCHECKED(type):
    if (hasattr(type, "_type_") and isinstance(type._type_, str)
        and type._type_ != "P"):
        return type
    else:
        return c_void_p

# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self,func,restype,argtypes):
        self.func=func
        self.func.restype=restype
        self.argtypes=argtypes
    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func
    def __call__(self,*args):
        fixed_args=[]
        i=0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i+=1
        return self.func(*fixed_args+list(args[i:]))

# End preamble


# Begin loader

# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import os.path, re, sys, glob
import ctypes
import ctypes.util

def _environ_path(name):
    if name in os.environ:
        return os.environ[name].split(":")
    else:
        return []

class LibraryLoader(object):
    def __init__(self):
        self.other_dirs=[]

    def load_library(self,libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            if os.path.exists(path):
                return self.load(path)

        raise ImportError("%s not found." % libname)

    def load(self,path):
        """Given a path to a library, load it."""
        try:
            # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
            # of the default RTLD_LOCAL.  Without this, you end up with
            # libraries not being loadable, resulting in "Symbol not found"
            # errors
            if sys.platform == 'darwin':
                return ctypes.CDLL(path, ctypes.RTLD_GLOBAL)
            else:
                return ctypes.cdll.LoadLibrary(path)
        except OSError,e:
            raise ImportError(e)

    def getpaths(self,libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname

        else:
            for path in self.getplatformpaths(libname):
                yield path

            path = ctypes.util.find_library(libname)
            if path:
                yield path

    def getplatformpaths(self, libname):
        return []

# Darwin (Mac OS X)

class DarwinLibraryLoader(LibraryLoader):
    name_formats = ["lib%s.dylib", "lib%s.so", "lib%s.bundle", "%s.dylib",
                "%s.so", "%s.bundle", "%s"]

    def getplatformpaths(self,libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [format % libname for format in self.name_formats]

        for dir in self.getdirs(libname):
            for name in names:
                yield os.path.join(dir,name)

    def getdirs(self,libname):
        '''Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        '''

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [os.path.expanduser('~/lib'),
                                          '/usr/local/lib', '/usr/lib']

        dirs = []

        if '/' in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))

        dirs.extend(self.other_dirs)
        dirs.append(".")

        if hasattr(sys, 'frozen') and sys.frozen == 'macosx_app':
            dirs.append(os.path.join(
                os.environ['RESOURCEPATH'],
                '..',
                'Frameworks'))

        dirs.extend(dyld_fallback_library_path)

        return dirs

# Posix

class PosixLibraryLoader(LibraryLoader):
    _ld_so_cache = None

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = []
        for name in ("LD_LIBRARY_PATH",
                     "SHLIB_PATH", # HPUX
                     "LIBPATH", # OS/2, AIX
                     "LIBRARY_PATH", # BE/OS
                    ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))
        directories.extend(self.other_dirs)
        directories.append(".")

        try: directories.extend([dir.strip() for dir in open('/etc/ld.so.conf')])
        except IOError: pass

        directories.extend(['/lib', '/usr/lib', '/lib64', '/usr/lib64', '/usr/local/lib', '/usr/local/lib64'])

        cache = {}
        lib_re = re.compile(r'lib(.*)\.s[ol]')
        ext_re = re.compile(r'\.s[ol]$')
        for dir in directories:
            try:
                for path in glob.glob("%s/*.s[ol]*" % dir):
                    file = os.path.basename(path)

                    # Index by filename
                    if file not in cache:
                        cache[file] = path

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        if library not in cache:
                            cache[library] = path
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname)
        if result: yield result

        path = ctypes.util.find_library(libname)
        if path: yield os.path.join("/lib",path)

# Windows

class _WindowsLibrary(object):
    def __init__(self, path):
        self.cdll = ctypes.cdll.LoadLibrary(path)
        self.windll = ctypes.windll.LoadLibrary(path)

    def __getattr__(self, name):
        try: return getattr(self.cdll,name)
        except AttributeError:
            try: return getattr(self.windll,name)
            except AttributeError:
                raise

class WindowsLibraryLoader(LibraryLoader):
    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll"]

    def load_library(self, libname):
        try:
            result = LibraryLoader.load_library(self, libname)
        except ImportError:
            result = None
            if os.path.sep not in libname:
                for name in self.name_formats:
                    try:
                        result = getattr(ctypes.cdll, name % libname)
                        if result:
                            break
                    except WindowsError:
                        result = None
            if result is None:
                try:
                    result = getattr(ctypes.cdll, libname)
                except WindowsError:
                    result = None
            if result is None:
                raise ImportError("%s not found." % libname)
        return result

    def load(self, path):
        return _WindowsLibrary(path)

    def getplatformpaths(self, libname):
        if os.path.sep not in libname:
            for name in self.name_formats:
                dll_in_current_dir = os.path.abspath(name % libname)
                if os.path.exists(dll_in_current_dir):
                    yield dll_in_current_dir
                path = ctypes.util.find_library(name % libname)
                if path:
                    yield path

# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin":   DarwinLibraryLoader,
    "cygwin":   WindowsLibraryLoader,
    "win32":    WindowsLibraryLoader
}

loader = loaderclass.get(sys.platform, PosixLibraryLoader)()

def add_library_search_dirs(other_dirs):
    loader.other_dirs = other_dirs

load_library = loader.load_library

del loaderclass

# End loader

NULL = None # <built-in>

class struct_anon_1(Structure):
    pass

struct_anon_1.__slots__ = [
    'tssCreator',
    'tssFamily',
    'tssLevel',
    'tssVersion',
]
struct_anon_1._fields_ = [
    ('tssCreator', c_uint32),
    ('tssFamily', c_uint32),
    ('tssLevel', c_uint32),
    ('tssVersion', c_uint32),
]

TSS2_ABI_VERSION = struct_anon_1 

TSS2_RC = c_uint32 

TPM_ST = c_uint16 

TPMI_ST_COMMAND_TAG = TPM_ST 

TPM_HANDLE = c_uint32 

TPM_KEY_BITS = c_uint16 

TPM_CC = c_uint32 

TPMI_SH_AUTH_SESSION = TPM_HANDLE 

TPMI_DH_OBJECT = TPM_HANDLE 

TPMI_DH_PERSISTENT = TPM_HANDLE 

TPMI_RH_HIERARCHY = TPM_HANDLE 

TPMI_RH_PROVISION = TPM_HANDLE 

TPMI_RH_NV_INDEX = TPM_HANDLE 

TPMI_RH_NV_AUTH = TPM_HANDLE 

TPMI_RH_HIERARCHY_AUTH = TPM_HANDLE

TPMI_RH_CLEAR = TPM_HANDLE 

TPM_ALG_ID = c_uint16 

TPMI_ALG_PUBLIC = TPM_ALG_ID 

TPMI_ALG_HASH = TPM_ALG_ID 

TPMI_ALG_SYM_OBJECT = TPM_ALG_ID 

TPMI_ALG_ECC_SCHEME = TPM_ALG_ID 

TPMI_ALG_KDF = TPM_ALG_ID 

TPMI_ALG_SIG_SCHEME = TPM_ALG_ID 

TPMI_ALG_SYM_MODE = TPM_ALG_ID 

TPM_ECC_CURVE = c_uint16 

TPMI_ECC_CURVE = TPM_ECC_CURVE 

TPMA_LOCALITY = c_uint8 

class struct_anon_2(Structure):
    pass

struct_anon_2.__slots__ = [
    'hashAlg',
    'count',
]
struct_anon_2._fields_ = [
    ('hashAlg', TPMI_ALG_HASH),
    ('count', c_uint16),
]

TPMS_SCHEME_ECDAA = struct_anon_2 

TPMS_SIG_SCHEME_ECDAA = TPMS_SCHEME_ECDAA 

class union_anon_3(Union):
    pass

union_anon_3.__slots__ = [
    'ecdaa',
]
union_anon_3._fields_ = [
    ('ecdaa', TPMS_SCHEME_ECDAA),
]

TPMU_SIG_SCHEME = union_anon_3 

class struct_anon_4(Structure):
    pass

struct_anon_4.__slots__ = [
    'scheme',
    'details',
]
struct_anon_4._fields_ = [
    ('scheme', TPMI_ALG_SIG_SCHEME),
    ('details', TPMU_SIG_SCHEME),
]

TPMT_SIG_SCHEME = struct_anon_4 

class union_anon_5(Union):
    pass

union_anon_5.__slots__ = [
    'sha256',
    'sha512',
    'null',
]
union_anon_5._fields_ = [
    ('sha256', c_uint8 * 32),
    ('sha512', c_uint8 * 64),
    ('null', c_uint8),
]

TPMU_HA = union_anon_5 

class struct_anon_6(Structure):
    pass

struct_anon_6.__slots__ = [
    'hashAlg',
    'digest',
]
struct_anon_6._fields_ = [
    ('hashAlg', TPMI_ALG_HASH),
    ('digest', TPMU_HA),
]

TPMT_HA = struct_anon_6 

class struct_anon_7(Structure):
    pass

struct_anon_7.__slots__ = [
    'size',
    'buffer',
]
struct_anon_7._fields_ = [
    ('size', c_uint16),
    ('buffer', c_uint8 * sizeof(TPMU_HA)),
]

TPM2B_DIGEST = struct_anon_7 

TPM2B_NONCE = TPM2B_DIGEST 

TPM2B_AUTH = TPM2B_DIGEST 

class struct_anon_8(Structure):
    pass

struct_anon_8.__slots__ = [
    'continueSession',
    'auditExclusive',
    'auditReset',
    'Reserved',
    'decrypt',
    'encrypt',
    'audit',
]
struct_anon_8._fields_ = [
    ('continueSession', c_uint, 1),
    ('auditExclusive', c_uint, 1),
    ('auditReset', c_uint, 1),
    ('Reserved', c_uint, 2),
    ('decrypt', c_uint, 1),
    ('encrypt', c_uint, 1),
    ('audit', c_uint, 1),
]

TPMA_SESSION = struct_anon_8 

class struct_anon_9(Structure):
    pass

struct_anon_9.__slots__ = [
    'Reserved1',
    'fixedTPM',
    'stClear',
    'Reserved2',
    'fixedParent',
    'sensitiveDataOrigin',
    'userWithAuth',
    'adminWithPolicy',
    'Reserved3',
    'noDA',
    'encryptedDuplication',
    'Reserved4',
    'restricted',
    'decrypt',
    'sign',
    'Reserved5',
]
struct_anon_9._fields_ = [
    ('Reserved1', c_uint, 1),
    ('fixedTPM', c_uint, 1),
    ('stClear', c_uint, 1),
    ('Reserved2', c_uint, 1),
    ('fixedParent', c_uint, 1),
    ('sensitiveDataOrigin', c_uint, 1),
    ('userWithAuth', c_uint, 1),
    ('adminWithPolicy', c_uint, 1),
    ('Reserved3', c_uint, 2),
    ('noDA', c_uint, 1),
    ('encryptedDuplication', c_uint, 1),
    ('Reserved4', c_uint, 4),
    ('restricted', c_uint, 1),
    ('decrypt', c_uint, 1),
    ('sign', c_uint, 1),
    ('Reserved5', c_uint, 13),
]

TPMA_OBJECT = struct_anon_9 

class struct_anon_10(Structure):
    pass

struct_anon_10.__slots__ = [
    'sessionHandle',
    'nonce',
    'sessionAttributes',
    'hmac',
]
struct_anon_10._fields_ = [
    ('sessionHandle', TPMI_SH_AUTH_SESSION),
    ('nonce', TPM2B_NONCE),
    ('sessionAttributes', TPMA_SESSION),
    ('hmac', TPM2B_AUTH),
]

TPMS_AUTH_COMMAND = struct_anon_10 

class struct_anon_11(Structure):
    pass

struct_anon_11.__slots__ = [
    'nonce',
    'sessionAttributes',
    'hmac',
]
struct_anon_11._fields_ = [
    ('nonce', TPM2B_NONCE),
    ('sessionAttributes', TPMA_SESSION),
    ('hmac', TPM2B_AUTH),
]

TPMS_AUTH_RESPONSE = struct_anon_11 

class struct_anon_12(Structure):
    pass

struct_anon_12.__slots__ = [
    'size',
    'buffer',
]
struct_anon_12._fields_ = [
    ('size', c_uint16),
    ('buffer', c_uint8 * 128),
]

TPM2B_SENSITIVE_DATA = struct_anon_12 

class struct_anon_13(Structure):
    pass

struct_anon_13.__slots__ = [
    'userAuth',
    'data',
]
struct_anon_13._fields_ = [
    ('userAuth', TPM2B_AUTH),
    ('data', TPM2B_SENSITIVE_DATA),
]

TPMS_SENSITIVE_CREATE = struct_anon_13 

class struct_anon_14(Structure):
    pass

struct_anon_14.__slots__ = [
    'size',
    'sensitive',
]
struct_anon_14._fields_ = [
    ('size', c_uint16),
    ('sensitive', TPMS_SENSITIVE_CREATE),
]

TPM2B_SENSITIVE_CREATE = struct_anon_14 

class union_anon_15(Union):
    pass

union_anon_15.__slots__ = [
    'aes',
    'null',
]
union_anon_15._fields_ = [
    ('aes', TPM_KEY_BITS),
    ('null', c_uint8),
]

TPMU_SYM_KEY_BITS = union_anon_15 

class union_anon_16(Union):
    pass

union_anon_16.__slots__ = [
    'sym',
    'null',
]
union_anon_16._fields_ = [
    ('sym', TPMI_ALG_SYM_MODE),
    ('null', c_uint8),
]

TPMU_SYM_MODE = union_anon_16 

class union_anon_17(Union):
    pass

union_anon_17.__slots__ = [
    'null',
]
union_anon_17._fields_ = [
    ('null', c_uint8),
]

TPMU_SYM_DETAILS = union_anon_17 

class struct_anon_18(Structure):
    pass

struct_anon_18.__slots__ = [
    'algorithm',
    'keyBits',
    'mode',
    'details',
]
struct_anon_18._fields_ = [
    ('algorithm', TPMI_ALG_SYM_OBJECT),
    ('keyBits', TPMU_SYM_KEY_BITS),
    ('mode', TPMU_SYM_MODE),
    ('details', TPMU_SYM_DETAILS),
]

TPMT_SYM_DEF_OBJECT = struct_anon_18 

class union_anon_19(Union):
    pass

union_anon_19.__slots__ = [
    'ecdaa',
]
union_anon_19._fields_ = [
    ('ecdaa', TPMS_SIG_SCHEME_ECDAA),
]

TPMU_ASYM_SCHEME = union_anon_19 

class struct_anon_20(Structure):
    pass

struct_anon_20.__slots__ = [
    'scheme',
    'details',
]
struct_anon_20._fields_ = [
    ('scheme', TPMI_ALG_ECC_SCHEME),
    ('details', TPMU_ASYM_SCHEME),
]

TPMT_ECC_SCHEME = struct_anon_20 

class union_anon_21(Union):
    pass

union_anon_21.__slots__ = [
    'null',
]
union_anon_21._fields_ = [
    ('null', c_uint8),
]

TPMU_KDF_SCHEME = union_anon_21 

class struct_anon_22(Structure):
    pass

struct_anon_22.__slots__ = [
    'scheme',
    'details',
]
struct_anon_22._fields_ = [
    ('scheme', TPMI_ALG_KDF),
    ('details', TPMU_KDF_SCHEME),
]

TPMT_KDF_SCHEME = struct_anon_22 

class struct_anon_23(Structure):
    pass

struct_anon_23.__slots__ = [
    'symmetric',
    'scheme',
    'curveID',
    'kdf',
]
struct_anon_23._fields_ = [
    ('symmetric', TPMT_SYM_DEF_OBJECT),
    ('scheme', TPMT_ECC_SCHEME),
    ('curveID', TPMI_ECC_CURVE),
    ('kdf', TPMT_KDF_SCHEME),
]

TPMS_ECC_PARMS = struct_anon_23 

class union_anon_24(Union):
    pass

union_anon_24.__slots__ = [
    'eccDetail',
]
union_anon_24._fields_ = [
    ('eccDetail', TPMS_ECC_PARMS),
]

TPMU_PUBLIC_PARMS = union_anon_24 

class struct_anon_25(Structure):
    pass

struct_anon_25.__slots__ = [
    'size',
    'buffer',
]
struct_anon_25._fields_ = [
    ('size', c_uint16),
    ('buffer', c_uint8 * 32),
]

TPM2B_ECC_PARAMETER = struct_anon_25 

class struct_anon_26(Structure):
    pass

struct_anon_26.__slots__ = [
    'x',
    'y',
]
struct_anon_26._fields_ = [
    ('x', TPM2B_ECC_PARAMETER),
    ('y', TPM2B_ECC_PARAMETER),
]

TPMS_ECC_POINT = struct_anon_26 

class union_anon_27(Union):
    pass

union_anon_27.__slots__ = [
    'ecc',
]
union_anon_27._fields_ = [
    ('ecc', TPMS_ECC_POINT),
]

TPMU_PUBLIC_ID = union_anon_27 

class struct_anon_28(Structure):
    pass

struct_anon_28.__slots__ = [
    'size',
    'point',
]
struct_anon_28._fields_ = [
    ('size', c_uint16),
    ('point', TPMS_ECC_POINT),
]

TPM2B_ECC_POINT = struct_anon_28 

class struct_anon_29(Structure):
    pass

struct_anon_29.__slots__ = [
    'type',
    'nameAlg',
    'objectAttributes',
    'authPolicy',
    'parameters',
    'unique',
]
struct_anon_29._fields_ = [
    ('type', TPMI_ALG_PUBLIC),
    ('nameAlg', TPMI_ALG_HASH),
    ('objectAttributes', TPMA_OBJECT),
    ('authPolicy', TPM2B_DIGEST),
    ('parameters', TPMU_PUBLIC_PARMS),
    ('unique', TPMU_PUBLIC_ID),
]

TPMT_PUBLIC = struct_anon_29 

class struct_anon_30(Structure):
    pass

struct_anon_30.__slots__ = [
    'size',
    'publicArea',
]
struct_anon_30._fields_ = [
    ('size', c_uint16),
    ('publicArea', TPMT_PUBLIC),
]

TPM2B_PUBLIC = struct_anon_30 

class struct_anon_31(Structure):
    pass

struct_anon_31.__slots__ = [
    'size',
    'buffer',
]
struct_anon_31._fields_ = [
    ('size', c_uint16),
    ('buffer', c_uint8 * sizeof(TPMT_HA)),
]

TPM2B_DATA = struct_anon_31 

class struct_anon_32(Structure):
    pass

struct_anon_32.__slots__ = [
    'hash',
    'sizeofSelect',
    'pcrSelect',
]
struct_anon_32._fields_ = [
    ('hash', TPMI_ALG_HASH),
    ('sizeofSelect', c_uint8),
    ('pcrSelect', c_uint8 * 1),
]

TPMS_PCR_SELECTION = struct_anon_32 

class struct_anon_33(Structure):
    pass

struct_anon_33.__slots__ = [
    'count',
    'pcrSelections',
]
struct_anon_33._fields_ = [
    ('count', c_uint32),
    ('pcrSelections', TPMS_PCR_SELECTION * 1),
]

TPML_PCR_SELECTION = struct_anon_33 

class union_anon_34(Union):
    pass

union_anon_34.__slots__ = [
    'digest',
    'handle',
]
union_anon_34._fields_ = [
    ('digest', TPMT_HA),
    ('handle', TPM_HANDLE),
]

TPMU_NAME = union_anon_34 

class struct_anon_35(Structure):
    pass

struct_anon_35.__slots__ = [
    'size',
    'name',
]
struct_anon_35._fields_ = [
    ('size', c_uint16),
    ('name', c_uint8 * sizeof(TPMU_NAME)),
]

TPM2B_NAME = struct_anon_35 

class struct_anon_36(Structure):
    pass

struct_anon_36.__slots__ = [
    'pcrSelect',
    'pcrDigest',
    'locality',
    'parentNameAlg',
    'parentName',
    'parentQualifiedName',
    'outsideInfo',
]
struct_anon_36._fields_ = [
    ('pcrSelect', TPML_PCR_SELECTION),
    ('pcrDigest', TPM2B_DIGEST),
    ('locality', TPMA_LOCALITY),
    ('parentNameAlg', TPM_ALG_ID),
    ('parentName', TPM2B_NAME),
    ('parentQualifiedName', TPM2B_NAME),
    ('outsideInfo', TPM2B_DATA),
]

TPMS_CREATION_DATA = struct_anon_36 

class struct_anon_37(Structure):
    pass

struct_anon_37.__slots__ = [
    'size',
    'creationData',
]
struct_anon_37._fields_ = [
    ('size', c_uint16),
    ('creationData', TPMS_CREATION_DATA),
]

TPM2B_CREATION_DATA = struct_anon_37 

class struct_anon_38(Structure):
    pass

struct_anon_38.__slots__ = [
    'tag',
    'hierarchy',
    'digest',
]
struct_anon_38._fields_ = [
    ('tag', TPM_ST),
    ('hierarchy', TPMI_RH_HIERARCHY),
    ('digest', TPM2B_DIGEST),
]

TPMT_TK_CREATION = struct_anon_38 

class struct_anon_39(Structure):
    pass

struct_anon_39.__slots__ = [
    'tag',
    'hierarchy',
    'digest',
]
struct_anon_39._fields_ = [
    ('tag', TPM_ST),
    ('hierarchy', TPMI_RH_HIERARCHY),
    ('digest', TPM2B_DIGEST),
]

TPMT_TK_HASHCHECK = struct_anon_39 

class struct_anon_40(Structure):
    pass

struct_anon_40.__slots__ = [
    'hash',
    'signatureR',
    'signatureS',
]
struct_anon_40._fields_ = [
    ('hash', TPMI_ALG_HASH),
    ('signatureR', TPM2B_ECC_PARAMETER),
    ('signatureS', TPM2B_ECC_PARAMETER),
]

TPMS_SIGNATURE_ECC = struct_anon_40 

class union_anon_41(Union):
    pass

union_anon_41.__slots__ = [
    'ecdaa',
]
union_anon_41._fields_ = [
    ('ecdaa', TPMS_SIGNATURE_ECC),
]

TPMU_SIGNATURE = union_anon_41 

class struct_anon_42(Structure):
    pass

struct_anon_42.__slots__ = [
    'sigAlg',
    'signature',
]
struct_anon_42._fields_ = [
    ('sigAlg', TPMI_ALG_SIG_SCHEME),
    ('signature', TPMU_SIGNATURE),
]

TPMT_SIGNATURE = struct_anon_42 

TSS2_TCTI_POLL_HANDLE = None 

class struct_TSS2_TCTI_OPAQUE_CONTEXT_BLOB(Structure):
    pass

TSS2_TCTI_CONTEXT = struct_TSS2_TCTI_OPAQUE_CONTEXT_BLOB 

class struct_anon_43(Structure):
    pass

struct_anon_43.__slots__ = [
    'magic',
    'version',
]
struct_anon_43._fields_ = [
    ('magic', c_uint64),
    ('version', c_uint32),
]

TSS2_TCTI_CONTEXT_VERSION = struct_anon_43 

class struct_anon_44(Structure):
    pass

struct_anon_44.__slots__ = [
    'magic',
    'version',
    'transmit',
    'receive',
    'finalize',
    'cancel',
    'getPollHandles',
    'setLocality',
]
struct_anon_44._fields_ = [
    ('magic', c_uint64),
    ('version', c_uint32),
    ('transmit', CFUNCTYPE(UNCHECKED(TSS2_RC), POINTER(TSS2_TCTI_CONTEXT), c_size_t, POINTER(c_uint8))),
    ('receive', CFUNCTYPE(UNCHECKED(TSS2_RC), POINTER(TSS2_TCTI_CONTEXT), POINTER(c_size_t), POINTER(c_uint8), c_int32)),
    ('finalize', CFUNCTYPE(UNCHECKED(TSS2_RC), POINTER(TSS2_TCTI_CONTEXT))),
    ('cancel', CFUNCTYPE(UNCHECKED(TSS2_RC), POINTER(TSS2_TCTI_CONTEXT))),
    ('getPollHandles', CFUNCTYPE(UNCHECKED(TSS2_RC), POINTER(TSS2_TCTI_CONTEXT), POINTER(TSS2_TCTI_POLL_HANDLE), POINTER(c_size_t))),
    ('setLocality', CFUNCTYPE(UNCHECKED(TSS2_RC), POINTER(TSS2_TCTI_CONTEXT), c_uint8)),
]

TSS2_TCTI_CONTEXT_COMMON_V1 = struct_anon_44 

TSS2_TCTI_CONTEXT_COMMON_CURRENT = TSS2_TCTI_CONTEXT_COMMON_V1 

class struct__TSS2_SYS_OPAQUE_CONTEXT_BLOB(Structure):
    pass

TSS2_SYS_CONTEXT = struct__TSS2_SYS_OPAQUE_CONTEXT_BLOB 

class struct_anon_45(Structure):
    pass

struct_anon_45.__slots__ = [
    'cmdAuthsCount',
    'cmdAuths',
]
struct_anon_45._fields_ = [
    ('cmdAuthsCount', c_uint8),
    ('cmdAuths', POINTER(POINTER(TPMS_AUTH_COMMAND))),
]

TSS2_SYS_CMD_AUTHS = struct_anon_45 

class struct_anon_46(Structure):
    pass

struct_anon_46.__slots__ = [
    'rspAuthsCount',
    'rspAuths',
]
struct_anon_46._fields_ = [
    ('rspAuthsCount', c_uint8),
    ('rspAuths', POINTER(POINTER(TPMS_AUTH_RESPONSE))),
]

TSS2_SYS_RSP_AUTHS = struct_anon_46 

class struct_anon_47(Structure):
    pass

struct_anon_47.__slots__ = [
    'TPMA_NV_PPWRITE',
    'TPMA_OWNERWRITE',
    'TPMA_AUTHWRITE',
    'TPMA_POLICYWRITE',
    'TPMA_COUNTER',
    'TPMA_BITS',
    'TPMA_EXTEND',
    'Reserved1',
    'TPMA_POLICY_DELETE',
    'TPMA_WRITELOCKED',
    'TPMA_WRITEALL',
    'TPMA_WRITEDEFINE',
    'TPMA_WRITE_STCLEAR',
    'TPMA_GLOBALLOCK',
    'TPMA_PPREAD',
    'TPMA_OWNERREAD',
    'TPMA_AUTHREAD',
    'TPMA_POLICYREAD',
    'Reserved2',
    'TPMA_NO_DA',
    'TPMA_ORDERLY',
    'TPMA_CLEAR_STCLEAR',
    'TPMA_READLOCKED',
    'TPMA_WRITTEN',
    'TPMA_PLATFORMCREATE',
    'TPMA_READ_STCLEAR',
]
struct_anon_47._fields_ = [
    ('TPMA_NV_PPWRITE', c_uint, 1),
    ('TPMA_OWNERWRITE', c_uint, 1),
    ('TPMA_AUTHWRITE', c_uint, 1),
    ('TPMA_POLICYWRITE', c_uint, 1),
    ('TPMA_COUNTER', c_uint, 1),
    ('TPMA_BITS', c_uint, 1),
    ('TPMA_EXTEND', c_uint, 1),
    ('Reserved1', c_uint, 3),
    ('TPMA_POLICY_DELETE', c_uint, 1),
    ('TPMA_WRITELOCKED', c_uint, 1),
    ('TPMA_WRITEALL', c_uint, 1),
    ('TPMA_WRITEDEFINE', c_uint, 1),
    ('TPMA_WRITE_STCLEAR', c_uint, 1),
    ('TPMA_GLOBALLOCK', c_uint, 1),
    ('TPMA_PPREAD', c_uint, 1),
    ('TPMA_OWNERREAD', c_uint, 1),
    ('TPMA_AUTHREAD', c_uint, 1),
    ('TPMA_POLICYREAD', c_uint, 1),
    ('Reserved2', c_uint, 5),
    ('TPMA_NO_DA', c_uint, 1),
    ('TPMA_ORDERLY', c_uint, 1),
    ('TPMA_CLEAR_STCLEAR', c_uint, 1),
    ('TPMA_READLOCKED', c_uint, 1),
    ('TPMA_WRITTEN', c_uint, 1),
    ('TPMA_PLATFORMCREATE', c_uint, 1),
    ('TPMA_READ_STCLEAR', c_uint, 1),
]

TPMA_NV = struct_anon_47 


class struct_anon_48(Structure):
    pass

struct_anon_48.__slots__ = [
    'nvIndex',
    'nameAlg',
    'attributes',
    'authPolicy',
    'dataSize',
]
struct_anon_48._fields_ = [
    ('nvIndex', TPMI_RH_NV_INDEX),
    ('nameAlg', TPMI_ALG_HASH),
    ('attributes', TPMA_NV),
    ('authPolicy', TPM2B_DIGEST),
    ('dataSize', c_uint16),
]

TPMS_NV_PUBLIC = struct_anon_48 


class struct_anon_49(Structure):
    pass

struct_anon_49.__slots__ = [
    'size',
    'nvPublic',
]
struct_anon_49._fields_ = [
    ('size', c_uint16),
    ('nvPublic', TPMS_NV_PUBLIC),
]

TPM2B_NV_PUBLIC = struct_anon_49 


class struct_anon_50(Structure):
    pass

struct_anon_50.__slots__ = [
    'size',
    'buffer',
]
struct_anon_50._fields_ = [
    ('size', c_uint16),
    ('buffer', c_uint8 * 768),
]

TPM2B_MAX_NV_BUFFER = struct_anon_50 

class union_anon_51(Union):
    pass

union_anon_51.__slots__ = [
    'bits',
]
union_anon_51._fields_ = [
    ('bits', TPM2B_SENSITIVE_DATA),
]

TPMU_SENSITIVE_COMPOSITE = union_anon_51 

class struct_anon_52(Structure):
    pass

struct_anon_52.__slots__ = [
    'sensitiveType',
    'authValue',
    'seedValue',
    'sensitive',
]
struct_anon_52._fields_ = [
    ('sensitiveType', TPMI_ALG_PUBLIC),
    ('authValue', TPM2B_AUTH),
    ('seedValue', TPM2B_DIGEST),
    ('sensitive', TPMU_SENSITIVE_COMPOSITE),
]

TPMT_SENSITIVE = struct_anon_52 

class struct_anon_53(Structure):
    pass

struct_anon_53.__slots__ = [
    'size',
    'sensitiveArea',
]
struct_anon_53._fields_ = [
    ('size', c_uint16),
    ('sensitiveArea', TPMT_SENSITIVE),
]

TPM2B_SENSITIVE = struct_anon_53 

class struct_anon_54(Structure):
    pass

struct_anon_54.__slots__ = [
    'integrityOuter',
    'integrityInner',
    'sensitive',
]
struct_anon_54._fields_ = [
    ('integrityOuter', TPM2B_DIGEST),
    ('integrityInner', TPM2B_DIGEST),
    ('sensitive', TPM2B_SENSITIVE),
]

_PRIVATE = struct_anon_54 

class struct_anon_55(Structure):
    pass

struct_anon_55.__slots__ = [
    'size',
    'buffer',
]
struct_anon_55._fields_ = [
    ('size', c_uint16),
    ('buffer', c_uint8 * sizeof(_PRIVATE)),
]

TPM2B_PRIVATE = struct_anon_55 

try:
    TSS2_RC_SUCCESS = 0
except:
    pass

try:
    TSS2_RC_LEVEL_SHIFT = 16
except:
    pass

try:
    TSS2_BASE_RC_GENERAL_FAILURE = 1
except:
    pass

try:
    TSS2_BASE_RC_NOT_IMPLEMENTED = 2
except:
    pass

try:
    TSS2_BASE_RC_BAD_CONTEXT = 3
except:
    pass

try:
    TSS2_BASE_RC_ABI_MISMATCH = 4
except:
    pass

try:
    TSS2_BASE_RC_BAD_REFERENCE = 5
except:
    pass

try:
    TSS2_BASE_RC_INSUFFICIENT_BUFFER = 6
except:
    pass

try:
    TSS2_BASE_RC_BAD_SEQUENCE = 7
except:
    pass

try:
    TSS2_BASE_RC_NO_CONNECTION = 8
except:
    pass

try:
    TSS2_BASE_RC_TRY_AGAIN = 9
except:
    pass

try:
    TSS2_BASE_RC_IO_ERROR = 10
except:
    pass

try:
    TSS2_BASE_RC_BAD_VALUE = 11
except:
    pass

try:
    TSS2_BASE_RC_NOT_PERMITTED = 12
except:
    pass

try:
    TSS2_BASE_RC_INVALID_SESSIONS = 13
except:
    pass

try:
    TSS2_BASE_RC_NO_DECRYPT_PARAM = 14
except:
    pass

try:
    TSS2_BASE_RC_NO_ENCRYPT_PARAM = 15
except:
    pass

try:
    TSS2_BASE_RC_BAD_SIZE = 16
except:
    pass

try:
    TSS2_BASE_RC_MALFORMED_RESPONSE = 17
except:
    pass

try:
    TSS2_BASE_RC_INSUFFICIENT_CONTEXT = 18
except:
    pass

try:
    TSS2_BASE_RC_INSUFFICIENT_RESPONSE = 19
except:
    pass

try:
    TSS2_BASE_RC_INCOMPATIBLE_TCTI = 20
except:
    pass

try:
    TSS2_BASE_RC_NOT_SUPPORTED = 21
except:
    pass

try:
    TSS2_BASE_RC_BAD_TCTI_STRUCTURE = 21
except:
    pass

try:
    TSS2_TCTI_ERROR_LEVEL = (10 << TSS2_RC_LEVEL_SHIFT)
except:
    pass

try:
    TSS2_TCTI_RC_GENERAL_FAILURE = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_GENERAL_FAILURE)
except:
    pass

try:
    TSS2_TCTI_RC_NOT_IMPLEMENTED = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_NOT_IMPLEMENTED)
except:
    pass

try:
    TSS2_TCTI_RC_BAD_CONTEXT = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_BAD_CONTEXT)
except:
    pass

try:
    TSS2_TCTI_RC_ABI_MISMATCH = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_ABI_MISMATCH)
except:
    pass

try:
    TSS2_TCTI_RC_BAD_REFERENCE = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_BAD_REFERENCE)
except:
    pass

try:
    TSS2_TCTI_RC_INSUFFICIENT_BUFFER = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_INSUFFICIENT_BUFFER)
except:
    pass

try:
    TSS2_TCTI_RC_BAD_SEQUENCE = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_BAD_SEQUENCE)
except:
    pass

try:
    TSS2_TCTI_RC_NO_CONNECTION = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_NO_CONNECTION)
except:
    pass

try:
    TSS2_TCTI_RC_TRY_AGAIN = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_TRY_AGAIN)
except:
    pass

try:
    TSS2_TCTI_RC_IO_ERROR = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_IO_ERROR)
except:
    pass

try:
    TSS2_TCTI_RC_BAD_VALUE = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_BAD_VALUE)
except:
    pass

try:
    TSS2_TCTI_RC_NOT_PERMITTED = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_NOT_PERMITTED)
except:
    pass

try:
    TSS2_TCTI_RC_MALFORMED_RESPONSE = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_MALFORMED_RESPONSE)
except:
    pass

try:
    TSS2_TCTI_RC_NOT_SUPPORTED = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_NOT_SUPPORTED)
except:
    pass

try:
    TSS2_SYS_ERROR_LEVEL = (8 << TSS2_RC_LEVEL_SHIFT)
except:
    pass

try:
    TSS2_SYS_RC_GENERAL_FAILURE = (TSS2_TCTI_ERROR_LEVEL | TSS2_BASE_RC_GENERAL_FAILURE)
except:
    pass

try:
    TSS2_SYS_RC_ABI_MISMATCH = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_ABI_MISMATCH)
except:
    pass

try:
    TSS2_SYS_RC_BAD_REFERENCE = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_BAD_REFERENCE)
except:
    pass

try:
    TSS2_SYS_RC_INSUFFICIENT_BUFFER = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_INSUFFICIENT_BUFFER)
except:
    pass

try:
    TSS2_SYS_RC_BAD_SEQUENCE = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_BAD_SEQUENCE)
except:
    pass

try:
    TSS2_SYS_RC_BAD_VALUE = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_BAD_VALUE)
except:
    pass

try:
    TSS2_SYS_RC_INVALID_SESSIONS = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_INVALID_SESSIONS)
except:
    pass

try:
    TSS2_SYS_RC_NO_DECRYPT_PARAM = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_NO_DECRYPT_PARAM)
except:
    pass

try:
    TSS2_SYS_RC_NO_ENCRYPT_PARAM = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_NO_ENCRYPT_PARAM)
except:
    pass

try:
    TSS2_SYS_RC_BAD_SIZE = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_BAD_SIZE)
except:
    pass

try:
    TSS2_SYS_RC_MALFORMED_RESPONSE = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_MALFORMED_RESPONSE)
except:
    pass

try:
    TSS2_SYS_RC_INSUFFICIENT_CONTEXT = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_INSUFFICIENT_CONTEXT)
except:
    pass

try:
    TSS2_SYS_RC_INSUFFICIENT_RESPONSE = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_INSUFFICIENT_RESPONSE)
except:
    pass

try:
    TSS2_SYS_RC_INCOMPATIBLE_TCTI = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_INCOMPATIBLE_TCTI)
except:
    pass

try:
    TSS2_SYS_RC_BAD_TCTI_STRUCTURE = (TSS2_SYS_ERROR_LEVEL | TSS2_BASE_RC_BAD_TCTI_STRUCTURE)
except:
    pass

try:
    TSS2_SYS_PART2_RC_LEVEL = (9 << TSS2_RC_LEVEL_SHIFT)
except:
    pass

try:
    TSS2_TPM_RC_LEVEL = 0
except:
    pass

try:
    COMMANDRESPONSE_SIZE = 4096
except:
    pass

try:
    MAX_SYM_DATA = 128
except:
    pass

try:
    MAX_ECC_KEY_BYTES = 32
except:
    pass

try:
    MAX_NV_BUFFER_SIZE = 768
except:
    pass


try:
    HASH_COUNT = 1
except:
    pass

try:
    PCR_SELECT_MAX = 1
except:
    pass

try:
    SHA256_DIGEST_SIZE = 32
except:
    pass

try:
    SHA512_DIGEST_SIZE = 64
except:
    pass

try:
    TPM_ST_CREATION = 32801
except:
    pass

try:
    TPM_ST_HASHCHECK = 32804
except:
    pass

try:
    TPM_ST_NO_SESSIONS = 32769
except:
    pass

try:
    TPM_ST_SESSIONS = 32770
except:
    pass

try:
    TPM_CC_NV_UndefineSpace = 290
except:
    pass

try:
    TPM_CC_HierarchyChangeAuth = 297
except:
    pass
try:
    TPM_CC_NV_DefineSpace = 298
except:
    pass

try:
    TPM_CC_CreatePrimary = 305
except:
    pass

try:
    TPM_CC_NV_Write = 311
except:
    pass

try:
    TPM_CC_NV_Read = 334
except:
    pass

try:
    TPM_CC_Sign = 349
except:
    pass

try:
    TPM_CC_GetCapability = 378
except:
    pass

try:
    TPM_CC_Commit = 395
except:
    pass

try:
    TPM_RS_PW = 1073741833
except:
    pass

try:
    TPM_RH_OWNER = 1073741825
except:
    pass

try:
    TPM_RH_ENDORSEMENT = 1073741835
except:
    pass

try:
    TPM_RH_PLATFORM = 1073741836
except:
    pass

try:
    TPM_RH_NULL = 1073741831
except:
    pass

try:
    TPM_ALG_SHA256 = 11
except:
    pass

try:
    TPM_ALG_SHA512 = 13
except:
    pass

try:
    TPM_ALG_NULL = 16
except:
    pass

try:
    TPM_ALG_ECDAA = 26
except:
    pass

try:
    TPM_ALG_ECC = 35
except:
    pass

try:
    TPM_ECC_BN_P256 = 16
except:
    pass

try:
    TPM_LOC_ZERO = 1
except:
    pass

try:
    TPM_LOC_ONE = 2
except:
    pass

try:
    TPM_LOC_TWO = 4
except:
    pass

try:
    TPM_LOC_THREE = 8
except:
    pass

try:
    TPM_LOC_FOUR = 16
except:
    pass

try:
    TSS2_TCTI_TIMEOUT_BLOCK = (-1)
except:
    pass

try:
    TSS2_TCTI_TIMEOUT_NONE = 0
except:
    pass

try:
    TPM_CC_Create = 339
except:
    pass

try:
    TPM_CC_Load = 343
except:
    pass

try:
    TPM_CC_EvictControl = 288
except:
    pass

try:
    TPM_CC_Clear = 294
except:
    pass

try:
    TPM_CC_ClearControl = 295
except:
    pass

try:
    TPM_RH_LOCKOUT = 1073741834
except:
    pass

try:
    TPM_ALG_AES = 6
except:
    pass

try:
    TPM_ALG_KDF1_SP800_108 = 34
except:
    pass

try:
    TPM_ALG_CFB = 67
except:
    pass

try:
    TPM_ECC_NIST_P256 = 3
except:
    pass

def tss2_tcti_transmit(tctiContext, size, command):
    cast_pointer = cast(tctiContext, POINTER(TSS2_TCTI_CONTEXT_COMMON_V1))
    if tctiContext == NULL:
        return TSS2_TCTI_RC_BAD_CONTEXT
    elif (cast_pointer.contents.version < 1):
        return TSS2_TCTI_RC_ABI_MISMATCH
    elif (cast_pointer.contents.finalize == NULL):
        return TSS2_TCTI_RC_NOT_IMPLEMENTED
    else:
        return cast_pointer.contents.transmit(tctiContext, size, command)

def tss2_tcti_receive(tctiContext, size, response, timeout):
    cast_pointer = cast(tctiContext, POINTER(TSS2_TCTI_CONTEXT_COMMON_V1))
    if tctiContext == NULL:
        return TSS2_TCTI_RC_BAD_CONTEXT
    elif (cast_pointer.contents.version < 1):
        return TSS2_TCTI_RC_ABI_MISMATCH
    elif (cast_pointer.contents.finalize == NULL):
        return TSS2_TCTI_RC_NOT_IMPLEMENTED
    else:
        return cast_pointer.contents.receive(tctiContext, size, response, timeout)

def tss2_tcti_finalize(tctiContext):
    cast_pointer = cast(tctiContext, POINTER(TSS2_TCTI_CONTEXT_COMMON_V1))
    if tctiContext == NULL:
        return TSS2_TCTI_RC_BAD_CONTEXT
    elif (cast_pointer.contents.version < 1):
        return TSS2_TCTI_RC_ABI_MISMATCH
    elif (cast_pointer.contents.finalize == NULL):
        return TSS2_TCTI_RC_NOT_IMPLEMENTED
    else:
        return cast_pointer.contents.finalize(tctiContext)

def tss2_tcti_cancel(tctiContext):
    cast_pointer = cast(tctiContext, POINTER(TSS2_TCTI_CONTEXT_COMMON_V1))
    if tctiContext == NULL:
        return TSS2_TCTI_RC_BAD_CONTEXT
    elif (cast_pointer.contents.version < 1):
        return TSS2_TCTI_RC_ABI_MISMATCH
    elif (cast_pointer.contents.finalize == NULL):
        return TSS2_TCTI_RC_NOT_IMPLEMENTED
    else:
        return cast_pointer.contents.cancel(tctiContext)

def tss2_tcti_getPollHandles(tctiContext, handles, num_handles):
    cast_pointer = cast(tctiContext, POINTER(TSS2_TCTI_CONTEXT_COMMON_V1))
    if tctiContext == NULL:
        return TSS2_TCTI_RC_BAD_CONTEXT
    elif (cast_pointer.contents.version < 1):
        return TSS2_TCTI_RC_ABI_MISMATCH
    elif (cast_pointer.contents.finalize == NULL):
        return TSS2_TCTI_RC_NOT_IMPLEMENTED
    else:
        return cast_pointer.contents.getPollHandles(tctiContext, handles, num_handles)

def tss2_tcti_setLocality(tctiContext, locality):
    cast_pointer = cast(tctiContext, POINTER(TSS2_TCTI_CONTEXT_COMMON_V1))
    if tctiContext == NULL:
        return TSS2_TCTI_RC_BAD_CONTEXT
    elif (cast_pointer.contents.version < 1):
        return TSS2_TCTI_RC_ABI_MISMATCH
    elif (cast_pointer.contents.finalize == NULL):
        return TSS2_TCTI_RC_NOT_IMPLEMENTED
    else:
        return cast_pointer.contents.setLocality(tctiContext, locality)

TSS2_TCTI_OPAQUE_CONTEXT_BLOB = struct_TSS2_TCTI_OPAQUE_CONTEXT_BLOB 

_TSS2_SYS_OPAQUE_CONTEXT_BLOB = struct__TSS2_SYS_OPAQUE_CONTEXT_BLOB 

def set_functions_from_library(extra_lib_paths):
    add_library_search_dirs(extra_lib_paths)
    lib = load_library("xaptum-tpm")

    globals()['TSS2_ABI_CURRENT_VERSION'] = (TSS2_ABI_VERSION).in_dll(lib, 'TSS2_ABI_CURRENT_VERSION')

    global Tss2_Sys_GetContextSize
    Tss2_Sys_GetContextSize = lib.Tss2_Sys_GetContextSize
    Tss2_Sys_GetContextSize.argtypes = [c_size_t]
    Tss2_Sys_GetContextSize.restype = c_size_t

    global Tss2_Sys_Initialize
    Tss2_Sys_Initialize = lib.Tss2_Sys_Initialize
    Tss2_Sys_Initialize.argtypes = [POINTER(TSS2_SYS_CONTEXT), c_size_t, POINTER(TSS2_TCTI_CONTEXT), POINTER(TSS2_ABI_VERSION)]
    Tss2_Sys_Initialize.restype = TSS2_RC

    global Tss2_Sys_Finalize
    Tss2_Sys_Finalize = lib.Tss2_Sys_Finalize
    Tss2_Sys_Finalize.argtypes = [POINTER(TSS2_SYS_CONTEXT)]
    Tss2_Sys_Finalize.restype = TSS2_RC

    global Tss2_Sys_GetTctiContext
    Tss2_Sys_GetTctiContext = lib.Tss2_Sys_GetTctiContext
    Tss2_Sys_GetTctiContext.argtypes = [POINTER(TSS2_SYS_CONTEXT), POINTER(POINTER(TSS2_TCTI_CONTEXT))]
    Tss2_Sys_GetTctiContext.restype = TSS2_RC

    global Tss2_Sys_CreatePrimary
    Tss2_Sys_CreatePrimary = lib.Tss2_Sys_CreatePrimary
    Tss2_Sys_CreatePrimary.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_RH_HIERARCHY, POINTER(TSS2_SYS_CMD_AUTHS), POINTER(TPM2B_SENSITIVE_CREATE), POINTER(TPM2B_PUBLIC), POINTER(TPM2B_DATA), POINTER(TPML_PCR_SELECTION), POINTER(TPM_HANDLE), POINTER(TPM2B_PUBLIC), POINTER(TPM2B_CREATION_DATA), POINTER(TPM2B_DIGEST), POINTER(TPMT_TK_CREATION), POINTER(TPM2B_NAME), POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_CreatePrimary.restype = TSS2_RC

    global Tss2_Sys_Commit
    Tss2_Sys_Commit = lib.Tss2_Sys_Commit
    Tss2_Sys_Commit.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_DH_OBJECT, POINTER(TSS2_SYS_CMD_AUTHS), POINTER(TPM2B_ECC_POINT), POINTER(TPM2B_SENSITIVE_DATA), POINTER(TPM2B_ECC_PARAMETER), POINTER(TPM2B_ECC_POINT), POINTER(TPM2B_ECC_POINT), POINTER(TPM2B_ECC_POINT), POINTER(c_uint16), POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_Commit.restype = TSS2_RC

    global Tss2_Sys_Sign
    Tss2_Sys_Sign = lib.Tss2_Sys_Sign
    Tss2_Sys_Sign.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_DH_OBJECT, POINTER(TSS2_SYS_CMD_AUTHS), POINTER(TPM2B_DIGEST), POINTER(TPMT_SIG_SCHEME), POINTER(TPMT_TK_HASHCHECK), POINTER(TPMT_SIGNATURE), POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_Sign.restype = TSS2_RC

    global tss2_tcti_getsize_socket
    tss2_tcti_getsize_socket = lib.tss2_tcti_getsize_socket
    tss2_tcti_getsize_socket.argtypes = []
    tss2_tcti_getsize_socket.restype = c_size_t

    global tss2_tcti_init_socket
    tss2_tcti_init_socket = lib.tss2_tcti_init_socket
    tss2_tcti_init_socket.argtypes = [String, String, POINTER(TSS2_TCTI_CONTEXT)]
    tss2_tcti_init_socket.restype = TSS2_RC

    global Tss2_Sys_NV_DefineSpace
    Tss2_Sys_NV_DefineSpace = lib.Tss2_Sys_NV_DefineSpace
    Tss2_Sys_NV_DefineSpace.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_RH_PROVISION, POINTER(TSS2_SYS_CMD_AUTHS), POINTER(TPM2B_AUTH), POINTER(TPM2B_NV_PUBLIC), POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_NV_DefineSpace.restype = TSS2_RC

    global Tss2_Sys_NV_Write
    Tss2_Sys_NV_Write = lib.Tss2_Sys_NV_Write
    Tss2_Sys_NV_Write.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_RH_NV_AUTH, TPMI_RH_NV_INDEX, POINTER(TSS2_SYS_CMD_AUTHS), POINTER(TPM2B_MAX_NV_BUFFER), c_uint16, POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_NV_Write.restype = TSS2_RC

    global Tss2_Sys_NV_Read
    Tss2_Sys_NV_Read = lib.Tss2_Sys_NV_Read
    Tss2_Sys_NV_Read.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_RH_NV_AUTH, TPMI_RH_NV_INDEX, POINTER(TSS2_SYS_CMD_AUTHS), c_uint16, c_uint16, POINTER(TPM2B_MAX_NV_BUFFER), POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_NV_Read.restype = TSS2_RC

    global Tss2_Sys_NV_UndefineSpace
    Tss2_Sys_NV_UndefineSpace = lib.Tss2_Sys_NV_UndefineSpace
    Tss2_Sys_NV_UndefineSpace.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_RH_PROVISION, TPMI_RH_NV_INDEX, POINTER(TSS2_SYS_CMD_AUTHS), POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_NV_UndefineSpace.restype = TSS2_RC

    global Tss2_Sys_HierarchyChangeAuth
    Tss2_Sys_HierarchyChangeAuth = lib.Tss2_Sys_HierarchyChangeAuth
    Tss2_Sys_HierarchyChangeAuth.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_RH_HIERARCHY_AUTH, POINTER(TSS2_SYS_CMD_AUTHS), POINTER(TPM2B_AUTH), POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_HierarchyChangeAuth.restype = TSS2_RC

    global Tss2_Sys_Create
    Tss2_Sys_Create = lib.Tss2_Sys_Create
    Tss2_Sys_Create.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_DH_OBJECT, POINTER(TSS2_SYS_CMD_AUTHS), POINTER(TPM2B_SENSITIVE_CREATE), POINTER(TPM2B_PUBLIC), POINTER(TPM2B_DATA), POINTER(TPML_PCR_SELECTION), POINTER(TPM2B_PRIVATE), POINTER(TPM2B_PUBLIC), POINTER(TPM2B_CREATION_DATA), POINTER(TPM2B_DIGEST), POINTER(TPMT_TK_CREATION), POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_Create.restype = TSS2_RC

    global Tss2_Sys_Load
    Tss2_Sys_Load = lib.Tss2_Sys_Load
    Tss2_Sys_Load.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_DH_OBJECT, POINTER(TSS2_SYS_CMD_AUTHS), POINTER(TPM2B_PRIVATE), POINTER(TPM2B_PUBLIC), POINTER(TPM_HANDLE), POINTER(TPM2B_NAME), POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_Load.restype = TSS2_RC

    global Tss2_Sys_EvictControl
    Tss2_Sys_EvictControl = lib.Tss2_Sys_EvictControl
    Tss2_Sys_EvictControl.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_RH_PROVISION, TPMI_DH_OBJECT, POINTER(TSS2_SYS_CMD_AUTHS), TPMI_DH_PERSISTENT, POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_EvictControl.restype = TSS2_RC

    global Tss2_Sys_Clear
    Tss2_Sys_Clear = lib.Tss2_Sys_Clear
    Tss2_Sys_Clear.argtypes = [POINTER(TSS2_SYS_CONTEXT), TPMI_RH_CLEAR, POINTER(TSS2_SYS_CMD_AUTHS), POINTER(TSS2_SYS_RSP_AUTHS)]
    Tss2_Sys_Clear.restype = TSS2_RC
