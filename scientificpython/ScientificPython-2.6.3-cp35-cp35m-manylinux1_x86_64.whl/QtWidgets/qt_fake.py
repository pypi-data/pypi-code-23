# Dummy module to make epydoc generate documentation even though
# Qt is not installed.

import sys
if 'epydoc' in sys.modules:

    class Qt:
        SolidLine=None
        SolidPattern=None

    class QWidget:
        pass

else:

    raise ImportError("Please install PyQt")

del sys
