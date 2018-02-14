import os
import sys
sys.path.insert(0, os.curdir)

if not os.path.exists("/tmp/pyspooler"):
    os.makedirs("/tmp/pyspooler")
