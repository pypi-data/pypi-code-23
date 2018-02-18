# encoding=utf-8

from __future__ import print_function
from collections import namedtuple as nt
import os
import sys
import shutil
from glob import glob
from subprocess import Popen, PIPE
import re
import time

class PTuple(tuple):
    def __floordiv__(self, pat):
        return self.flatmap(lambda _: _//pat)
    def flatmap(self, func):
        res = []
        for _ in self:
            res.extend(func(_))
        return PTuple(res)
    
if sys.version_info >= (3, 0):
    unicode_base = str
else:
    unicode_base = unicode

class Path(unicode_base):
    @staticmethod
    def mktemp():
        import tempfile
        _, path = tempfile.mkstemp(prefix='tmpquickfiles')
        os.close(_)
        result = p(path)
        result.rm()
        return result
    @property
    def realpath(self): return os.path.realpath(self)
    def __truediv__(self, next):
        return self.__div__(next)
    def __div__(self, next):
        return p(self.realpath + os.path.sep + unicode_base(next))
    def __str__(self): 
        slash = os.path.sep if self.endswith(os.path.sep) or self.endswith('/') else ''
        return self.realpath + slash
    def __repr__(self): return self.__str__()
    def __add__(self, x): 
        slash = os.path.sep if self.endswith(os.path.sep) or self.endswith('/') else ''
        return p(self.realpath + slash + x)
    @property
    def exists(self): return os.path.exists(self)
    def against(self, where): return './' + os.path.relpath(self, p(where))
    def relpath(self, against): return os.path.relpath(self, p(against))
    def replant(self, src, dst): return p(dst) / self.against(src)
    def indir(self, dst): return self.replant(self.dir, dst)
    @property
    def isdir(self): return os.path.isdir(self)
    def chext(self, old, new):
        assert self.endswith(old)
        return p(self[:-len(old)] + new)
    def setext(self, new):
        prefix = re.sub(r'\.[^\.\/]*$', '', self)
        return p(prefix + new)
    def transform_name(self, f): return self.dir/f(self.name)
    @property
    def name(self): return os.path.split(os.path.realpath(self))[1]
    @property
    def dir(self):
        if os.path.isdir(self): return self
        else: return p(os.path.split(os.path.realpath(self))[0])
    def make_parents(self): self.dir.makedir()
    def mkdir(self): return self.makedir()
    def mkdirs(self): return self.makedir()
    def makedir(self):
        try:
            os.makedirs(self)
        except OSError as e:
            if e.errno != 17: raise e
    @property
    def name(self):
        return os.path.split(os.path.realpath(self))[1]
    @property
    def realpath(self):
        return os.path.realpath(self)
    def __floordiv__(self, pat):
        if pat == '**':
            dirs = []
            def see(_, dir, __):
                dirs.append(p(dir))
            os.path.walk(self, see, None)
            return PTuple(sorted(dirs))
        elif pat == '***':
            dir_stack = [self]
            result = [ ]
            while len(dir_stack) > 0:
                top = dir_stack[-1]
                del dir_stack[-1]
                result.append(top)
                for next in top//'*':
                    if next.isdir:
                        dir_stack.append(next)
            return PTuple(sorted(result))
        else:
            files = PTuple(p(_) for _ in glob(self + '/' + pat))
            return PTuple(sorted(files, key=lambda _: _.name))
    def __mod__(self, how):
        if isinstance(how, RAND):
            import tempfile
            self.makedir()
            _, path = tempfile.mkstemp(dir=self, prefix=how.prefix, suffix=how.suffix)
            return p(path)
        elif isinstance(how, COUNTER):
            candidates = (_ for _ in os.listdir(self) if _.startswith(how.prefix))
            number_strs = (c[len(how.prefix):] for c in candidates)
            numbers = [ ]
            for s in number_strs:
                try: numbers.append(int(s))
                except ValueError: pass
            now = max(numbers) + 1 if len(numbers)>0 else 1
            return self/(how.prefix + unicode_base(now))
        else:
            raise TypeError(how, 'should be one of', [RAND, COUNTER])
    
    def rm(self):
        if self.isdir:
            shutil.rmtree(self)
        else:
            os.unlink(self)
    def rmf(self):
        try:
            self.rm()
        except:
            pass
    def set(self, wth):
        self.make_parents()
        with open(self, 'w') as h:
            h.write(wth)
    def clear(self):
        self.set('')
    def setas(self, wth):
        self.make_parents()
        wth(open(self, 'w'))
    def append(self, wth):
        self.make_parents()
        open(self, 'a').write(wth)
    def open(self):
        return open(self, 'r')
    def read(self):
        return self.open().read()
    @property
    def content(self):
        return self.read()
    def cp(self, dest):
        dest = p(dest)
        if dest.isdir:
            dest = dest / self.name
        if self.isdir:
            shutil.copytree(self, unicode_base(dest))
        else:
            shutil.copy2(self, unicode_base(dest))
    def delete_at_exit(self):
        import atexit
        def f():
            try:
                os.unlink(self)
            except:
                pass
        atexit.register(f)
    
class COUNTER(nt('COUNTER', ['prefix'])): pass
_RAND = nt('RAND', ['prefix', 'suffix'])
class RAND(_RAND):
    @staticmethod
    def __new__(_cls, prefix='', suffix=''):
        return _RAND.__new__(_cls, prefix, suffix)

def p(s):
    try:
        isstring = isinstance(s, basestring)
    except NameError:
        isstring = isinstance(s, str)
        
    if isinstance(s, Path): return s
    elif isstring: 
        if isinstance(s, unicode_base):
            u = s
        else:
            u = unicode_base(s, 'utf-8')
        slash = os.path.sep if u.endswith(os.path.sep) or u.endswith('/') else ''
        return Path(os.path.normpath(os.path.realpath(u)) + slash)
    else: raise TypeError
_p = p

def dirof(s): return p(s).dir

t = tuple
def tt(*things): return tuple(things)

def adict(**things):
    return things
    
def struct(**things):
    return nt('Struct', things.keys())(**things)
    
def nstruct(name):
    return struct(
        of = lambda **things: nt(name, things.keys())(**things)
    )
    
def sink_to_temp(content, key):
    import tempfile
    import atexit
    import hashlib
    path = p(tempfile.gettempdir()) / hashlib.sha1(key).hexdigest()
    atexit.register(lambda: os.unlink(str(path)))
    open(str(path), 'w').write(content)
    return p(path)

def sink_to_temp_no_delete(content, key):
    import tempfile
    import atexit
    import hashlib
    path = p(tempfile.gettempdir()) / hashlib.sha1(key).hexdigest()
    print('Writing ' + str(path))
    print('setting content to ' + str(len(content)) + ' chars')
    path.set(content)
    return path
    
def fileof(content):
    import tempfile
    import atexit
    _, path = tempfile.mkstemp()
    atexit.register(lambda: os.unlink(path))
    open(path, 'w').write(content)
    return p(path)
    
