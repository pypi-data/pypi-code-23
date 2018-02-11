"""Extract an image's dataset-level mask and write to a new file."""


__version__ = '1.2'
__author__ = 'Kevin Wurster'
__email__ = 'wursterk@gmail.com'
__source__ = 'https://github.com/geowurster/rio-ds-mask'
__license__ = '''
New BSD License

Copyright (c) 2017-2018, Kevin D. Wurster
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* The names of rio-ds-mask or its contributors may not be used to endorse or
  promote products derived from this software without specific prior written
  permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''


import itertools as it
import operator as op
import sys

import click
import cligj
import numpy as np
import rasterio as rio
from rasterio.rio import options


if sys.version_info[0] == 2:
    from itertools import imap as map


def _norm_gdal_mask(array, src_dtypes):

    """When writing masks GDAL uses 0's for opaque and 255's for transparent,
    but when reading masks the returned value differs based on the image's
    datatype.  8 bit images produce masks where 0's are opaque and 255's
    are transparent, however 16 bit images use 0's for opaque and 1's for
    transparent.  If the image's datatype is 'int16' or 'uint16' and the
    mask's maximum value is 1, then all 1's are translated to 255's.  The
    mask's datatype is preserved.  I have not fully investigated all of
    GDAL's masking options to determine if the behavior is consistent.  If
    it is found to be a deliberate choice then the normalization will be
    removed.

    Parameters
    ----------
    array : numpy.ndarray
        Array to normalize.
    src_dtypes : sequence
        Parent image's datatypes.

    Returns
    -------
    numpy.ndarray
    """

    cast = getattr(np, array.dtype.name)
    if set(src_dtypes) & {'uint16', 'int16'} and array.max() == 1:
        array = np.where(array > 0, cast(255), cast(0))
    return array


@click.command(name='ds-mask')
@options.file_in_arg
@options.file_out_arg
@cligj.format_opt
@options.dtype_opt
@options.creation_options
def rio_ds_mask(input, output, driver, dtype, creation_options):

    """Extract an image's dataset-level mask.

    Both output driver and datatype are derived from the input image if
    not given.

    In some cases this plugin alters GDAL's returned mask values.  When
    writing masks GDAL uses 0's for opaque and 255's for transparent, but
    when reading masks the returned value differs based on the image's
    datatype.  8 bit images produce 8 bit masks where 0's are opaque and
    255's are transparent, however 16 bit images use 0's for opaque and 1's
    for transparent, still stored as 8 bit.  If the image's datatype is
    'int16' or 'uint16' and the mask's maximum value is 1, then all 1's are
    translated to 255's.  The mask's datatype is preserved.  I have not fully
    investigated all of GDAL's masking options to determine if the behavior
    is consistent.  If it is found to be a deliberate choice then the
    normalization will be removed.
    """

    with rio.open(input) as src:

        all_windows = map(op.itemgetter(1), src.block_windows())
        window_data = ((w, src.dataset_mask(window=w)) for w in all_windows)

        first = next(window_data)
        window_data = it.chain([first], window_data)
        detected_dtype = first[1].dtype.name
        del first

        meta = src.meta.copy()
        meta.update(
            count=1,
            driver=driver or src.driver,
            dtype=dtype or detected_dtype)

        if creation_options:
            meta.update(**creation_options)

        with rio.open(output, 'w', **meta) as dst:
            for window, mask in window_data:
                dst.write(
                    _norm_gdal_mask(mask, src.dtypes), indexes=1, window=window)
