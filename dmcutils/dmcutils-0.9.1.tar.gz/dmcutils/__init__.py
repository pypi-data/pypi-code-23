from pathlib import Path
import h5py
import numpy as np
from scipy.misc import bytescale
#
from histutils.timedmc import frame2ut1


def h5toh5(fn,kineticsec,startutc):
    """
    determine UTC time of each frame and index of each frame
    """
    fn = Path(fn).expanduser()

    with h5py.File(fn, 'r', libver='latest') as f:
        data = f['/rawimg']

        rawind = np.arange(data.shape[0])+1

    ut1 = frame2ut1(startutc,kineticsec,rawind)

    return rawind, ut1


def mean16to8(I):
    """
    input:
    I: uint16 ndarray image

    output:
    uint8 ndarray

    1. take mean of uint16 image stack
    2. clip off extrema (very dim or bright)
    3. return uint8 image
    """
    fmean = I.mean(axis=0)
    l,h = np.percentile(fmean, (0.5,99.5))
# %% 16 bit to 8 bit using scikit-image
    return bytescale(fmean, cmin=l, cmax=h)
