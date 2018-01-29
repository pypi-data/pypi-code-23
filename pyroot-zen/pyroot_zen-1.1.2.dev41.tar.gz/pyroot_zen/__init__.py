"""

`pyroot_zen` package.

"""

__author__  = 'Chitsanu Khurewathanakul'
__email__   = 'chitsanu.khurewathanakul@gmail.com'
__license__ = 'GNU GPLv3'

## Import ROOT, if not already, then patch it
import ROOT
import patch_ROOT
del patch_ROOT
