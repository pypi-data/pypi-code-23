"""Color and spectral data."""
import csv
from functools import lru_cache
from pathlib import Path

import numpy as np
from numpy import exp

from scipy.interpolate import interp1d
from scipy.constants import c, h, k
# c - speed of light
# h - planck constant
# k - boltzman constant

# standard illuminant information
CIE_ILLUMINANT_METADATA = {
    'files': {
        'A': 'cie_A_300_830_1nm.csv',
        'B': 'cie_B_380_770_5nm.csv',
        'C': 'cie_C_380_780_5nm.csv',
        'D': 'cie_Dseries_380_780_5nm.csv',
        'E': 'cie_E_380_780_5nm.csv',
        'F': 'cie_Fseries_380_730_5nm.csv',
        'HP': 'cie_HPseries_380_780_5nm.csv',
    },
    'columns': {
        'A': 1,
        'B': 1,
        'C': 1,
        'D50': 1, 'D55': 2, 'D65': 3, 'D75': 4,
        'E': 1,
        'F1': 1, 'F2': 2, 'F3': 3, 'F4': 4, 'F5': 5, 'F6': 6,
        'F7': 7, 'F8': 8, 'F9': 9, 'F10': 10, 'F11': 11, 'F12': 12,
        'HP1': 1, 'HP2': 2, 'HP3': 3, 'HP4': 4, 'HP5': 5,
    }
}


@lru_cache()
def prepare_robertson_cct_data():
    """Prepare Robertson's correlated color temperature data.

    Returns
    -------
    `dict` containing: urd, K, u, v, dvdu.

    Notes
    -----
    CCT values in L*u*v* coordinates, i.e. uv, not u'v'.
    see the following for the source of these values:
    https://www.osapublishing.org/josa/abstract.cfm?uri=josa-58-11-1528

    """
    tmp_list = []
    p = Path(__file__).parent / 'datasets' / 'robertson_cct.csv'
    with open(p, 'r') as fid:
        reader = csv.reader(fid)
        for row in reader:
            tmp_list.append(row)

    values = np.asarray(tmp_list[1:])
    urd, k, u, v, dvdu = values[:, 0], values[:, 1], values[:, 2], values[:, 3], values[:, 4]
    return {
        'urd': urd,
        'K': k,
        'u': u,
        'v': v,
        'dvdu': dvdu
    }


@lru_cache()
def prepare_robertson_interpfs(values=('u', 'v'), vs='K'):
    """Prepare interpolation functions for robertson CCT data.

    Parameters
    ----------
    values : `tuple` of `strs`, {'u', 'v', 'K', 'urd', 'dvdu'}
        which values to interpolate; defaults to u and v

    vs : `str`, {'u', 'v', 'K', 'urd', 'dvdu'}
        what to interpolate against; defaults to CCT

    Returns
    -------
    `list`
        each element is a scipy.interpolate.interp1d callable in the same order as the values arg

    """
    data = prepare_robertson_cct_data()
    if type(values) in (list, tuple):
        interpfs = []
        for value in values:
            x, y = data[vs], data[value]
            interpfs.append(interp1d(x, y))
        return interpfs
    else:
        return interp1d(data[vs], data[values])


def prepare_illuminant_spectrum(illuminant='D65', bb_wvl=None, bb_norm=True):
    """Prepare the SPD for a given illuminant.

    Parameters
    ----------
    illuminant : `str`, {'A', 'B', 'C', 'D50', 'D55', 'D65', 'E', 'F1'..'F12', 'HP1'..'HP5', 'bb_xxxx'}
        CIE illuminant (A, B, C, etc) or blackbody (bb_xxxx); for blackbody xxxx is the temperature

    bb_wvl : `numpy.ndarray`
        array of wavelengths to compute a requested black body SPD at

    bb_norm : `bool`
        whether to normalize a computed blackbody spectrum

    Returns
    -------
    `dict`
        with keys: `wvl`, `values`

    """
    if illuminant[0:2].lower() == 'bb':
        _, temp = illuminant.split('_')
        if bb_wvl is None:
            bb_wvl = np.arange(380, 780, 5)
        spd = blackbody_spectrum(float(temp), bb_wvl)
        spec = {
            'wvl': bb_wvl,
            'values': spd
        }
        if bb_norm is True:
            spec = normalize_spectrum(spec, to='peak 560')
            spec['values'] *= 100
            return spec
        else:
            return spec
    else:
        return _prepare_ciesource_spectrum(illuminant)


@lru_cache()
def _prepare_ciesource_spectrum(illuminant):
    """Retrive a CIE standard source from its csv file.

    Parameters
    ----------
    illuminant : `str`, {'A', 'B', 'C', 'D50', 'D55', 'D65', 'E', 'F1'..'F12', 'HP1'..'HP5'}
        CIE illuminant

    Returns
    -------
    `dict`
        with keys: `wvl`, `values`

    """
    if illuminant[0:2].upper() == 'HP':
        file = CIE_ILLUMINANT_METADATA['files']['HP']
    else:
        file = CIE_ILLUMINANT_METADATA['files'][illuminant[0].upper()]
    column = CIE_ILLUMINANT_METADATA['columns'][illuminant.upper()]

    tmp_list = []
    p = Path(__file__).parent / 'datasets' / file
    with open(p, 'r') as fid:
        reader = csv.reader(fid)
        for row in reader:
            tmp_list.append(row)

    values = np.asarray(tmp_list[1:])
    return {
        'wvl': values[:, 0],
        'values': values[:, column],
    }


def value_array_to_tristimulus(values):
    """Pull tristimulus data as numpy arrays from a list of CSV rows.

    Parameters
    ----------
    values : `list`
        list with each element being a row of a CSV, headers omitted

    Returns
    -------
    `dict`
        with keys: wvl, X, Y, Z

    """
    values = np.asarray(values)
    wvl, X, Y, Z = values[:, 0], values[:, 1], values[:, 2], values[:, 3]
    return {
        'wvl': wvl,
        'X': X,
        'Y': Y,
        'Z': Z
    }


# these two functions could be better refactored, but meh.
@lru_cache()
def prepare_cie_1931_2deg_observer():
    """Prepare the CIE 1931 standard 2 degree observer.

    Returns
    -------
    `dict`
        with keys: wvl, X, Y, Z

    """
    tmp_list = []
    p = Path(__file__).parent / 'datasets' / 'cie_xyz_1931_2deg_tristimulus_5nm.csv'
    with open(p, 'r') as fid:
        reader = csv.reader(fid)
        for row in reader:
            tmp_list.append(row)

    return value_array_to_tristimulus(tmp_list[1:])


@lru_cache()
def prepare_cie_1964_10deg_observer():
    """Prepare the CIE 1964 standard 10 degree observer.

    Returns
    -------
    `dict`
        with keys: wvl, X, Y, Z

    """
    tmp_list = []
    p = Path(__file__).parent / 'datasets' / 'cie_xyz_1964_10deg_tristimulus_5nm.csv'
    with open(p, 'r') as fid:
        reader = csv.reader(fid)
        for row in reader:
            tmp_list.append(row)

    return value_array_to_tristimulus(tmp_list[1:])


def prepare_cmf(observer='1931_2deg'):
    """Safely returns the color matching function dictionary for the specified observer.

    Parameters
    ----------
    observer : `str`, {'1931_2deg', '1964_10deg'}
        the observer to return

    Returns
    -------
    `dict`
        cmf dict

    Raises
    ------
    ValueError
        observer not 1931 2 degree or 1964 10 degree

    """
    if observer.lower() == '1931_2deg':
        return prepare_cie_1931_2deg_observer()
    elif observer.lower() == '1964_10deg':
        return prepare_cie_1964_10deg_observer()
    else:
        raise ValueError('observer must be 1931_2deg or 1964_10deg')


def blackbody_spectrum(temperature, wavelengths):
    """Compute the spectral power distribution of a black body at a given temperature.

    Parameters
    ----------
    temperature : `float`
        body temp, in Kelvin
    wavelengths : `numpy.ndarray`
        array of wavelengths, in nanometers

    Returns
    -------
    `numpy.ndarray`
        spectral power distribution in units of W/m^2/nm

    """
    wavelengths = wavelengths / 1e9
    return (2 * h * c ** 2) / (wavelengths ** 5) * \
        1 / (exp((h * c) / (wavelengths * k * temperature) - 1))


def normalize_spectrum(spectrum, to='peak vis'):
    """Normalize a spectrum to have unit peak within the visible band.

    Parameters
    ----------
    spectrum : `dict`
        with keys wvl, value
    to : `str`, {'peak vis', 'peak'}
        what to normalize the spectrum to; maximum will be 1.0

    Returns
    -------
    `dict`
        with keys wvl, values

    """
    wvl, vals = spectrum['wvl'], spectrum['values']
    if to.lower() == 'peak vis':
        low, high = np.searchsorted(wvl, 400), np.searchsorted(wvl, 700)
        vals2 = vals / vals[low:high].max()
    elif to.lower() in ('peak 560', '560', '560nm'):
        idx = np.searchsorted(wvl, 560)
        vals2 = vals / vals[idx]
    return {
        'wvl': wvl,
        'values': vals2,
    }
