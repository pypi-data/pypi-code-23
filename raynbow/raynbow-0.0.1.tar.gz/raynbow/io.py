"""File readers for commercial instrumentation."""
import numpy as np


def read_oceanoptics(file_path):
    """Read spectral transmission data from an ocean optics spectrometer.

    Parameters
    ----------
    file_path : `str` or path_like
        path to a file

    Returns
    -------
    `dict`
        a dictionary with keys of wvl and values

    Raises
    ------
    `IOError`
        if the file is malformed.

    """
    with open(file_path, 'r') as fid:
        txtlines = fid.readlines()

        idx, ready_length, ready_spectral = None, False, False
        for i, line in enumerate(txtlines):
            if 'Number of Pixels in Spectrum' in line:
                length, ready_length = int(line.split()[-1]), True
            elif '>>>>>Begin Spectral Data<<<<<' in line:
                idx, ready_spectral = i, True

        if not ready_length or not ready_spectral:
            raise IOError('''File lacks line stating "Number of Pixels in Spectrum" or
                             ">>>>>Begin Spectral Data<<<<<" and appears to be corrupt.''')
        data_lines = txtlines[idx + 1:]
        wavelengths = np.empty(length)
        values = np.empty(length)
        for idx, line in enumerate(data_lines):
            wvl, val = line.split()
            wavelengths[idx] = wvl
            values[idx] = val

        return {
            'wvl': wavelengths,
            'values': values,
        }
