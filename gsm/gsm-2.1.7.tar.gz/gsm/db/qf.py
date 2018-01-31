import os.path
import gsm

def queryfile(rel_qfile):
    p = os.path.abspath(os.path.dirname(gsm.__file__))
    return os.path.join(p, rel_qfile)
