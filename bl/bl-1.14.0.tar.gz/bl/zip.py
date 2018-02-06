# zip.py - class for handling ZIP files

from zipfile import ZipFile, ZIP_DEFLATED
import os, sys
from bl.dict import Dict

class ZIP(Dict):
    """zipfile wrapper"""

    def __init__(self, fn=None, mode='r', compression=ZIP_DEFLATED, **args):
        Dict.__init__(self, fn=fn, mode=mode, compression=compression, **args)
        if fn is not None:
            self.zipfile = ZipFile(self.fn, mode=mode, compression=compression)

    def read(self, src):
        """return file data from within the docx file"""
        return self.zipfile.read(src)

    def write(self, fn=None):
        """copy the zip file from its filename to the given filename."""
        fn = fn or self.fn
        if not os.path.exists(os.path.dirname(fn)):
            os.makedirs(os.path.dirname(fn))
        f = open(self.fn, 'rb'); b = f.read(); f.close()
        f = open(fn, 'wb'); f.write(b); f.close()

    def unzip(self, path=None, members=None, pwd=None):
        if path is None: path = os.path.splitext(self.fn)[0]
        if not os.path.exists(path): os.makedirs(path)
        self.zipfile.extractall(path=path, members=members, pwd=pwd)
        return path

    def close(self):
        self.zipfile.close()

    @classmethod
    def zip_path(CLASS, path, fn=None, exclude=[], mode='w'):
        if fn is None:
            fn = path+'.zip'
        zipf = CLASS(fn, mode=mode).zipfile
        for walk_tuple in os.walk(path):
            dirfn = walk_tuple[0]
            for fp in walk_tuple[-1]:
                walkfn = os.path.join(dirfn, fp)
                if os.path.relpath(walkfn, path) not in exclude:
                    zipf.write(walkfn, os.path.relpath(walkfn, path))
        zipf.close()
        return fn

if __name__=='__main__':
    if sys.argv[1]=='unzip':
        for fn in sys.argv[2:]:
            print(ZIP(fn=fn).unzip())
    elif sys.argv[1]=='zip':
        for path in sys.argv[2:]:
            print(ZIP.zip_path(path))
    else:
        for path in sys.argv[1:]:
            print(ZIP.zip_path(path))
