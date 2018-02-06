
import os, shutil, tempfile
from bl.file import File
from bl.string import String

class Text(File):

    def __init__(self, fn=None, text=None, encoding='UTF-8', **args):
        File.__init__(self, fn=fn, encoding=encoding, **args)
        if text is not None:
            self.text = text
        elif fn is not None and os.path.exists(fn):
            self.text = String(self.read().decode(encoding))
        else:
            self.text = String("")

    def write(self, fn=None, text=None, encoding='UTF-8', **args):
        try:
            data = (text or self.text or '').encode(encoding)
        except:
            data = (text or self.text or '').encode()
        File.write(self, fn=fn, data=data, **args)
        
