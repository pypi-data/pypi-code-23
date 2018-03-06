import sys

PY2 = sys.version_info[0] == 2

if not PY2:
    from queue import Queue
else:
    from Queue import Queue
