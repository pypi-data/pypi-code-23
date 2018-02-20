import sys

__version__ = '0.1.1'


# python version
_p3 = False
if sys.version_info > (3, 0):
    _p3 = True
del(sys)

# old hyperspy wants API 'QDate' set to version 2
if not _p3:
    try:
        import sip
        sip.setapi('QDate', 2)
        sip.setapi('QDateTime', 2)
        sip.setapi('QString', 2)
        sip.setapi('QTextStream', 2)
        sip.setapi('QTime', 2)
        sip.setapi('QUrl', 2)
        sip.setapi('QVariant', 2)
        del(sip)
    except:
        pass


__all__ = [
    'fft_tools',
    'fpd_file',
    'fpd_processing',
    'gwy',
    'ransac_tools',
    'synthetic_data',
    'tem_helper']

# To get sub-modules
for x in __all__:
    exec('from . import %s' %(x))
del(x)

# Import classes
from .dpc_explorer_class import DPC_Explorer
del(dpc_explorer_class)

from .segmented_dpc_class import SegmentedDPC
del(segmented_dpc_class)
