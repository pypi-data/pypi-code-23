"""Color space transforms."""

import numpy as np
from numpy import sqrt
from scipy.interpolate import interp1d

from raynbow.data import (
    prepare_cmf,
    prepare_illuminant_spectrum,
    prepare_robertson_interpfs,
    blackbody_spectrum,
)

# some CIE constants
CIE_K = 24389 / 27
CIE_E = 216 / 24389

# from Ohno PDF, see D_uv function.
NIST_DUV_k0 = -0.471106
NIST_DUV_k1 = +1.925865
NIST_DUV_k2 = -2.4243787
NIST_DUV_k3 = +1.5317403
NIST_DUV_k4 = -0.5179722
NIST_DUV_k5 = +0.0893944
NIST_DUV_k6 = -0.00616793

# sRGB conversion matrix
XYZ_to_sRGB_mat_D65 = np.asarray([
    [3.2404542, -1.5371385, -0.4985314],
    [-0.9692660, 1.8760108, 0.0415560],
    [0.0556434, -0.2040259, 1.0572252]
])
XYZ_to_sRGB_mat_D50 = np.asarray([
    [3.1338561, -1.6168667, -0.4906146],
    [-0.9787684, 1.9161415, 0.0334540],
    [0.0719453, -0.2289914, 1.4052427],
])

# Adobe RGB 1998 matricies
XYZ_to_AdobeRGB_mat_D65 = np.asarray([
    [2.0413690, -0.5649464, -0.3446944],
    [-0.9692660, 1.8760108, 0.0415560],
    [0.0134474, -0.1183897, 1.0154096],
])
XYZ_to_AdobeRGB_mat_D50 = np.asarray([
    [1.9624274, -0.6105343, -0.3413404],
    [-0.9787684, 1.9161415, 0.0334540],
    [0.0286869, -0.1406752, 1.3487655],
])

COLOR_MATRICIES = {
    'sRGB': {
        'D65': XYZ_to_sRGB_mat_D65,
        'D50': XYZ_to_sRGB_mat_D50,
    },
    'AdobeRGB': {
        'D65': XYZ_to_AdobeRGB_mat_D65,
        'D50': XYZ_to_AdobeRGB_mat_D50,
    },
}


def multi_cct_duv_to_uvprime(cct, duv):
    """Convert multi CCT, Duv value pairs to u'v' coordinates.

    Parameters
    ----------
    cct : `iterable`
        CCT values
    duv : `iterable`
        Duv values

    Returns
    -------
    `numpy.ndarray`
        2D array of u'v' values

    """
    upvp = np.empty((len(cct), len(duv), 2))
    for i, cct_v in enumerate(cct):
        for j, duv_v in enumerate(duv):
            values = CCT_Duv_to_uvprime(cct_v, duv_v)
            upvp[j, i, 0] = values[0]
            upvp[j, i, 1] = values[1]
    return upvp


def spectrum_to_XYZ_emissive(spectrum_dict, cmf='1931_2deg'):
    """Convert an emissive spectrum to XYZ coordinates.

    Parameters
    ----------
    spectrum_dict : `dict`
        dictionary with wvl, values keys
    cmf : `str`
        which color matching function to use, defaults to CIE 1931 2 degree observer

    Returns
    -------
    X : `float`
        X tristimulus value
    Y : `float`
        Y tristimulus value
    Z : `float`
        Z tristimulus value

    """
    wvl, values = spectrum_dict['wvl'], spectrum_dict['values']

    cmf = prepare_cmf(cmf)
    wvl_cmf = cmf['wvl']
    try:
        can_be_direct = np.allclose(wvl_cmf, wvl)
    except ValueError as e:
        can_be_direct = False
    if not can_be_direct:
        dat_interpf = interp1d(wvl, values, kind='linear', bounds_error=False, fill_value=0, assume_sorted=True)
        values = dat_interpf(wvl_cmf)

    dw = wvl_cmf[1] - wvl_cmf[0]
    k = 100 / (values * cmf['Y']).sum() / dw
    X = k * (values * cmf['X']).sum()
    Y = k * (values * cmf['Y']).sum()
    Z = k * (values * cmf['Z']).sum()
    return X, Y, Z


def spectrum_to_XYZ_nonemissive(spectrum_dict, illuminant='D65', cmf='1931_2deg'):
    """Convert an emissive spectrum to XYZ coordinates.

    Parameters
    ----------
    spectrum_dict : `dict`
        dictionary with wvl, values keys
    illuminant : `str`, {'A', 'B', 'C', 'D50', 'D55', 'D65', 'E', 'F1'..'F12', 'HP1'..'HP5', 'bb_xxxx'}
        CIE illuminant (A, B, C, etc) or blackbody (bb_xxxx); for blackbody xxxx is the temperature
    cmf : `str`
        which color matching function to use, defaults to CIE 1931 2 degree observer

    Returns
    -------
    X : `float`
        X tristimulus value
    Y : `float`
        Y tristimulus value
    Z : `float`
        Z tristimulus value

    """
    wvl, values = spectrum_dict['wvl'], spectrum_dict['values']

    cmf = prepare_cmf(cmf)
    wvl_cmf = cmf['wvl']
    try:
        can_be_direct = np.allclose(wvl_cmf, wvl)
    except ValueError as e:
        can_be_direct = False

    if not can_be_direct:
        dat_interpf = interp1d(wvl, values, kind='linear', bounds_error=False, fill_value=0, assume_sorted=True)
        values = dat_interpf(wvl_cmf)

    ill_spectrum = prepare_illuminant_spectrum(illuminant)

    try:
        can_be_direct_illuminant = np.allclose(wvl_cmf, ill_spectrum['wvl'])
    except ValueError as e:
        can_be_direct_illuminant = False
    if can_be_direct_illuminant:
        ill_spectrum = ill_spectrum['values']
    else:
        ill_wvl, ill_vals = ill_spectrum['wvl'], ill_spectrum['values']
        ill_interpf = interp1d(ill_wvl, ill_vals, kind='linear', bounds_error=False, fill_value=0, assume_sorted=True)
        ill_spectrum = ill_interpf(wvl_cmf)

    dw = wvl_cmf[1] - wvl_cmf[0]
    k = 100 / (values * ill_spectrum * cmf['Y']).sum() / dw
    X = k * (values * ill_spectrum * cmf['X']).sum()
    Y = k * (values * ill_spectrum * cmf['Y']).sum()
    Z = k * (values * ill_spectrum * cmf['Z']).sum()
    return X, Y, Z


def _spectrum_to_coordinates(spectrum_dict, out_function, emissive=False, nonemissive_illuminant='D65'):
    """Compute the coordinates defined by out_function from a given spectrum dictionary.

    Parameters
    ----------
    spectrum_dict : `dict`
        dictionary with keys wvl, values
    out_function : `function`
        an XYZ_to_something function.  More generally, a function which takes XYZ tristimulus values
        and returns color coordinates
    emissive : `boolean`
        whether the spectrum is an emissive or nonemissive one
    nonemissive_illuminant : `str`, {'A', 'B', 'C', 'D50', 'D55', 'D65', 'E', 'F1'..'F12', 'HP1'..'HP5', 'bb_xxxx'}
        reference illuminant for non-emissive spectra

    Returns
    -------
    `object`
        return defined by out_function

    """
    if not emissive:
        XYZ = spectrum_to_XYZ_nonemissive(spectrum_dict, illuminant=nonemissive_illuminant)
    else:
        XYZ = spectrum_to_XYZ_emissive(spectrum_dict)

    return out_function(XYZ)


def spectrum_to_xyY(spectrum_dict, emissive=False, nonemissive_illuminant='D65'):
    """Compute the xyY chromaticity values of a spectrum object.

    Parameters
    ----------
    spectrum_dict : `dict`
        dictionary with keys wvl, values
    emissive : `boolean`
        whether the spectrum is an emissive or nonemissive one
    nonemissive_illuminant : `str`, {'A', 'B', 'C', 'D50', 'D55', 'D65', 'E', 'F1'..'F12', 'HP1'..'HP5', 'bb_xxxx'}
        reference illuminant for non-emissive spectra

    Returns
    -------
    `numpy.ndarray`
        array with last dimension x, y, Y

    """
    return _spectrum_to_coordinates(spectrum_dict, XYZ_to_xyY, emissive, nonemissive_illuminant)


def spectrum_to_xy(spectrum_dict, emissive=False, nonemissive_illuminant='D65'):
    """Compute the xy chromaticity values of a spectrum object.

    Parameters
    ----------
    spectrum_dict : `dict`
        dictionary with keys wvl, values
    emissive : `boolean`
        whether the spectrum is an emissive or nonemissive one
    nonemissive_illuminant : `str`, {'A', 'B', 'C', 'D50', 'D55', 'D65', 'E', 'F1'..'F12', 'HP1'..'HP5', 'bb_xxxx'}
        reference illuminant for non-emissive spectra

    Returns
    -------
    `numpy.ndarray`
        array with last dimension x, y

    """
    return _spectrum_to_coordinates(spectrum_dict, XYZ_to_xy, emissive, nonemissive_illuminant)


def spectrum_to_uvprime(spectrum_dict, emissive=False, nonemissive_illuminant='D65'):
    """Compute the xy chromaticity values of a spectrum object.

    Parameters
    ----------
    spectrum_dict : `dict`
        dictionary with keys wvl, values
    emissive : `boolean`
        whether the spectrum is an emissive or nonemissive one
    nonemissive_illuminant : `str`, {'A', 'B', 'C', 'D50', 'D55', 'D65', 'E', 'F1'..'F12', 'HP1'..'HP5', 'bb_xxxx'}
        reference illuminant for non-emissive spectra

    Returns
    -------
    `numpy.ndarray`
        array with last dimension u', v'

    """
    return _spectrum_to_coordinates(spectrum_dict, XYZ_to_uvprime, emissive, nonemissive_illuminant)


def spectrum_to_CCT_Duv(spectrum_dict, emissive=False, nonemissive_illuminant='D65'):
    """Compute the CCT and Duv values of a spectrum object.

    Parameters
    ----------
    spectrum_dict : `dict`
        dictionary with keys wvl, values
    emissive : `boolean`
        whether the spectrum is an emissive or nonemissive one
    nonemissive_illuminant : `str`, {'A', 'B', 'C', 'D50', 'D55', 'D65', 'E', 'F1'..'F12', 'HP1'..'HP5', 'bb_xxxx'}
        reference illuminant for non-emissive spectra

    Returns
    -------
    `numpy.ndarray`
        array with last dimension CCT, Duv

    """
    if not emissive:
        XYZ = spectrum_to_XYZ_nonemissive(spectrum_dict, illuminant=nonemissive_illuminant)
    else:
        XYZ = spectrum_to_XYZ_emissive(spectrum_dict)

    upvp = XYZ_to_uvprime(XYZ)
    cctduv = uvprime_to_CCT_Duv(upvp)
    return cctduv


def wavelength_to_XYZ(wavelength, observer='1931_2deg'):
    """Use tristimulus color matching functions to map a awvelength to XYZ coordinates.

    Parameters
    ----------
    wavelength : `float`
        wavelength in nm
    observer : `str`, {'1931_2deg', '1964_2deg'}
        CIE observer name, must be 1931_2deg or 1964_10deg

    Returns
    -------
    `numpy.ndarray`
        array with last dimension X, Y, Z

    """
    wavelength = np.asarray(wavelength)

    cmf = prepare_cmf(observer)
    wvl, X, Y, Z = cmf['wvl'], cmf['X'], cmf['Y'], cmf['Z']

    ia = {'bounds_error': False, 'fill_value': 0, 'assume_sorted': True}
    f_X, f_Y, f_Z = interp1d(wvl, X, **ia), interp1d(wvl, Y, **ia), interp1d(wvl, Z, **ia)
    x, y, z = f_X(wavelength), f_Y(wavelength), f_Z(wavelength)

    shape = wavelength.shape
    return np.stack((x, y, z), axis=len(shape))


def XYZ_to_xyY(XYZ, assume_nozeros=True, ref_white='D65'):
    """Convert XYZ points to xyY points.

    Parameters
    ----------
    XYZ : `numpy.ndarray`
        array with last dimension corresponding to X, Y, Z.

    assume_nozeros : `bool`
        assume there are no zeros present, computation will run faster as `True`, if `False` will
        correct for all zero values
    ref_white : `str`, {'A', 'B', 'C', 'D50', 'D55', 'D65', 'E', 'F1'..'F12', 'HP1'..'HP5', 'bb_xxxx'}
        string for reference illuminant used in the case
        where X==Y==Z==0.

    Returns
    -------
    `numpy.ndarray`
        aray with last dimension x, y, Y

    Notes
    -----
    If X==Y==Z==0 and assume_nozeros is False, will return the chromaticity coordinates
    of the reference white.

    """
    XYZ = np.asarray(XYZ)
    X, Y, Z = XYZ[..., 0], XYZ[..., 1], XYZ[..., 2]

    if not assume_nozeros:
        zero_X = X == 0
        zero_Y = Y == 0
        zero_Z = Z == 0
        allzeros = np.all(np.dstack((zero_X, zero_Y, zero_Z)))
        X[allzeros] = 0.3
        Y[allzeros] = 0.3
        Z[allzeros] = 0.3

    x = X / (X + Y + Z)
    y = Y / (X + Y + Z)
    Y = Y
    shape = x.shape

    if not assume_nozeros:
        spectrum = prepare_illuminant_spectrum(ref_white)
        xyz = spectrum_to_XYZ_emissive(spectrum)
        xr, yr = XYZ_to_xy(xyz)
        x[allzeros] = xr
        y[allzeros] = yr
        Y[:] = xyz[1]

    return np.stack((x, y, Y), axis=len(shape))


def XYZ_to_xy(XYZ):
    """Convert XYZ points to xy points.

    Parameters
    ----------
    XYZ : `numpy.ndarray`
        ndarray with last dimension corresponding to X, Y, Z

    Returns
    -------
    `numpy.ndarray`
        array with last dimension x, y

    """
    xyY = XYZ_to_xyY(XYZ)
    return xyY_to_xy(xyY)


def XYZ_to_uvprime(XYZ):
    """Convert XYZ points to u'v' points.

    Parameters
    ----------
    XYZ : `numpy.ndarray`
        ndarray with last dimension corresponding to X, Y, Z

    Returns
    -------
    `numpy.ndarray`
        array with last dimension u' v'

    """
    XYZ = np.asarray(XYZ)
    X, Y, Z = XYZ[..., 0], XYZ[..., 1], XYZ[..., 2]
    u = (4 * X) / (X + 15 * Y + 3 * Z)
    v = (9 * Y) / (X + 15 * Y + 3 * Z)

    shape = u.shape
    return np.stack((u, v), axis=len(shape))


def xyY_to_xy(xyY):
    """Convert xyY points to xy points.

    Parameters
    ----------
    xyY : `numpy.ndarray`
        ndarray with last dimension corresponding to x, y, Y

    Returns
    -------
    `numpy.ndarray`
        array with last dimension x, y

    """
    xyY = np.asarray(xyY)
    x, y = xyY[..., 0], xyY[..., 1]

    shape = x.shape
    return np.stack((x, y), axis=len(shape))


def xyY_to_XYZ(xyY):
    """Convert xyY points to XYZ points.

    Parameters
    ----------
    xyY : `numpy.ndarray`
        ndarray with last dimension corresponding to x, y, Y

    Returns
    -------
    `numpy.ndarray`
        array with last dimension X, Y, Z

    """
    xyY = np.asarray(xyY)
    x, y, Y = xyY[..., 0], xyY[..., 1], xyY[..., 2]
    y_l = y.copy()
    idxs = y_l == 0
    y_l[idxs] = 0.3
    X = np.asarray((x * Y) / y_l)
    Y = np.asarray(Y)
    Z = np.asarray(((1 - x - y_l) * Y) / y_l)
    X[idxs] = 0
    Y[idxs] = 0
    Z[idxs] = 0

    shape = X.shape
    return np.stack((X, Y, Z), axis=len(shape))


def xy_to_xyY(xy, Y=1):
    """Convert xy points to xyY points.

    Parameters
    ----------
    xy : `numpy.ndarray`
        ndarray with last dimension corresponding to x, y

    Y : `numpy.ndarray`
        Y value to fill with

    Returns
    -------
    `numpy.ndarray`
        array with last dimension x, y, Y

    """
    xy = np.asarray(xy)
    shape = xy.shape

    x, y = xy[..., 0], xy[..., 1]
    Y = np.ones(x.shape) * Y

    return np.stack((x, y, Y), axis=len(shape) - 1)


def xy_to_XYZ(xy):
    """Convert xy points to xyY points.

    Parameters
    ----------
    xy : `numpy.ndarray`
        ndarray with last dimension corresponding to x, y

    Returns
    -------
    `numpy.ndarray`
        array with last dimension X, Y, Z

    """
    xy = np.asarray(xy)
    xyY = xy_to_xyY(xy)
    return xyY_to_XYZ(xyY)


def xy_to_uvprime(xy):
    """Compute u'v' chromaticity coordinates from xy chromaticity coordinates.

    Parameters
    ----------
    xy : `iterable`
        x, y chromaticity coordinates

    Returns
    -------
    `numpy.ndarray`
        array with last dimension u', v'.

    """
    xy = np.asarray(xy)
    x, y = xy[..., 0], xy[..., 1]
    u = 4 * x / (-2 * x + 12 * y + 3)
    v = 6 * y / (-2 * x + 12 * y + 3) * 1.5  # inline conversion from v -> v'
    shape = xy.shape
    return np.stack((u, v), axis=len(shape) - 1)


def xy_to_CCT_Duv(xy):
    """Compute the correlated color temperature and Delta uv given x,y chromaticity coordinates.

    Parameters
    ----------
    xy : `iterable`
        x, y chromaticity coordinates

    Returns
    -------
    `tuple`
        CCT, Duv values

    """
    upvp = xy_to_uvprime(xy)
    return uvprime_to_CCT_Duv(upvp)


def uvprime_to_xy(uvprime):
    """Convert u' v' points to xyY x,y points.

    Parameters
    ----------
    uvprime : `numpy.ndarray`
        array with last dimension u' v'

    Returns
    -------
    `numpy.ndarray`
        array with last dimension x, y

    """
    uv = np.asarray(uvprime)
    u, v = uv[..., 0], uv[..., 1]
    x = (9 * u) / (6 * u - 16 * v + 12)
    y = (4 * v) / (6 * u - 16 * v + 12)

    shape = x.shape
    return np.stack((x, y), axis=len(shape))


def _uvprime_to_CCT_Duv_triangulation(u, v, dmm1, dmp1, umm1, ump1, vmm1, vm, vmp1, tmm1, tmp1, sign):
    """Ohno 2011 triangulation technique to compute Duv from a CIE 1960 u, v coordinate.

    Parameters
    ----------
    u : `numpy.ndarray`
        array of u values
    v : `numpy.ndarray`
        array of v values
    dmm1 : `numpy.ndarray`
        "d sub m minus one" - distance for the m-1th CCT
    dmp1 : `numpy.ndarray`
        "d sub m plus one" - distance for the m+1th CCT
    umm1 : `numpy.ndarray`
        "u sub m minus one" - u coordinate for the m-1th CCT
    ump1 : `numpy.ndarray`
        "u sub m plus one" - u coordinate for the m+1th CCT
    vmm1 : `numpy.ndarray`
        "v sub m minus one" - v coordinate for the m-1th CCT
    vm : `numpy.ndarray`
        array of v values for the closest match in the interpolated robertson 1961 data
    vmp1 : `numpy.ndarray`
        "v sub m plus one" - v coordinate for the m+1th CCT
    tmm1 : `numpy.ndarray`
        "t sub m minus one" - the m-1th CCT
    tmp1 : `numpy.ndarray`
        "t sub m plus one" - the m-1th CCT
    sign : `int`
        either -1 or 1, indicates the sign of the Duv value

    Returns
    -------
    `numpy.ndarray`
        Duv values

    """
    ell = np.hypot(umm1 - ump1, vmm1 - vmp1)
    x = (dmm1 ** 2 - dmp1 ** 2 + ell ** 2) / (2 * ell)
    CCT = tmp1 + (tmp1 - tmp1) * (x / ell)
    Duv = sign * sqrt(dmm1 ** 2 - x ** 2)
    return CCT, Duv


def _uvprime_to_CCT_Duv_parabolic(tmm1, tm, tmp1, dmm1, dm, dmp1, sign):
    """Ohno 2011 parabolic technique for computing CCT.

    Parameters
    ----------
    tmm1 : `numpy.ndarray`
        "T sub m minus 1", the m+1th CCT value
    tm : `numpy.ndarray`
        "T sub m", the mth CCT value
    tmp1 : `numpy.ndarray`
        "T sub m plus 1", the m+1th CCT value
    dmm1 : `numpy.ndarray`
        "d sub m minus 1", the m-1th distance value
    dm : `numpy.ndarray`
        "d sub m", the mth distance value
    dmp1 : `numpy.ndarray`
        "d sub m plus 1", m+1th distance value
    sign : `int`
        either -1 or 1, indicating the sign of the solution

    Returns
    -------
    `tuple`
        CCT, Duv values

    """
    x = (tmm1 - tm) * (tmp1 - tmm1) * (tm - tmp1)
    a = (tmp1 * (dmm1 - dm) + tm * (dmp1 - dmm1) + tmm1 * (dm - dmp1)) * x ** -1
    b = (-(tmp1 ** 2 * (dmm1 - dm) + tm ** 2 * (dmp1 - dmm1) + tmm1 ** 2 *
           (dm - dmp1)) * x ** -1)
    c = (-(dmp1 * (tmm1 - tm) * tm * tmm1 + dm *
           (tmp1 - tmm1) * tmp1 * tmm1 + dmm1 *
           (tm - tmp1) * tmp1 * tm) * x ** -1)

    CCT = -b / (2 * a)
    Duv = sign * (a * CCT ** 2 + b * CCT + c)
    return CCT, Duv


def uvprime_to_CCT_Duv(uvprime, interp_samples=10000):
    """Compute Duv from u'v' coordinates.

    Parameters
    ----------
    uvprime : `numpy.ndarray`
        array with last dimension u' v'
    interp_samples : `int`
        number of samples to use in interpolation

    Returns
    -------
    `float`
        CCT

    Notes
    -----
    see "Calculation of CCT and Duv and Practical Conversion Formulae", Yoshi Ohno
    http://www.cormusa.org/uploads/CORM_2011_Calculation_of_CCT_and_Duv_and_Practical_Conversion_Formulae.PDF

    """
    uvp = np.asarray(uvprime)
    u, v = uvp[..., 0], uvp[..., 1] / 1.5  # inline conversion from v' -> v

    # get interpolators for robertson's CCT data
    interp_u, interp_v = prepare_robertson_interpfs(values=('u', 'v'), vs='K')

    # now produce arrays of u, v coordinates with fine sampling on a log scale
    sample_K = np.logspace(3.225, 4.25, num=interp_samples, base=10)
    u_i, v_i = interp_u(sample_K), interp_v(sample_K)
    distance = sqrt((u_i - u) ** 2 + (v_i - v) ** 2)
    closest = np.argmin(distance)

    tmm1 = sample_K[closest - 1]
    tmp1 = sample_K[closest + 1]

    dmm1 = distance[closest - 1]
    dmp1 = distance[closest + 1]
    dm = distance[closest]

    umm1 = u_i[closest - 1]
    ump1 = u_i[closest + 1]
    vmm1 = v_i[closest - 1]
    vmp1 = v_i[closest + 1]
    vm = v_i[closest]
    if vm <= v:
        sign = 1
    else:
        sign = -1

    CCT, Duv = _uvprime_to_CCT_Duv_triangulation(u, v, dmm1, dmp1, umm1, ump1, vmm1, vm, vmp1, tmm1, tmp1, sign)

    if abs(Duv) > 0.002:
        CCT, Duv = _uvprime_to_CCT_Duv_parabolic(tmm1, CCT, tmp1, dmm1, dm, dmp1, sign)
    return CCT, Duv


def CCT_Duv_to_uvprime(CCT, Duv, delta_t=0.01):
    """Convert (CCT,Duv) coordinates to upvp coordinates.

    Parameters
    ----------
    CCT : `float` or `iterable`
        CCT coordinate
    Duv : `float` or `iterable`
        Duv coordinate
    delta_t : `float`
        temperature differential used to compute the tangent line to the plankian locust.
        Default to 0.01, Ohno suggested (2011).

    Returns
    -------
    u' : `float`
        u' coordinate
    v' : `float`
        v' coordinate

    """
    CCT, Duv = np.asarray(CCT), np.asarray(Duv)

    wvl = np.arange(360, 835, 5)
    bb_spec_0 = blackbody_spectrum(CCT, wvl)
    bb_spec_1 = blackbody_spectrum(CCT + delta_t, wvl)
    bb_spec_0 = {
        'wvl': wvl,
        'values': bb_spec_0,
    }
    bb_spec_1 = {
        'wvl': wvl,
        'values': bb_spec_1,
    }

    xyz_0 = spectrum_to_XYZ_emissive(bb_spec_0)
    xyz_1 = spectrum_to_XYZ_emissive(bb_spec_1)
    upvp_0 = XYZ_to_uvprime(xyz_0)
    upvp_1 = XYZ_to_uvprime(xyz_1)

    u0, v0 = upvp_0[..., 0], upvp_0[..., 1]
    u1, v1 = upvp_1[..., 0], upvp_1[..., 1]
    du, dv = u1 - u0, v1 - v0
    u = u0 + Duv * dv / sqrt(du**2 + dv**2)
    v = u0 + Duv * du / sqrt(du**2 + dv**2)
    return u, v * 1.5**2  # factor of 1.5 converts v -> v'


def XYZ_to_AdobeRGB(XYZ, illuminant='D65'):
    """Convert XYZ points to AdobeRGB values.

    Parameters
    ----------
    XYZ : `numpy.ndarray`
        array with last dimension corresponding to X, Y, Z
    illuminant : `str`, {'D50', 'D65'}
        which white point illuminant to use

    Returns
    -------
    `numpy.ndarray`
        array with last dimension R, G, B

    Raises
    ------
    ValueError
        invalid illuminant

    """
    if illuminant.upper() == 'D65':
        invmat = COLOR_MATRICIES['AdobeRGB']['D65']
    elif illuminant.upper() == 'D50':
        invmat = COLOR_MATRICIES['AdobeRGB']['D50']
    else:
        raise ValueError('Must use D65 or D50 illuminant.')

    return XYZ_to_RGB(XYZ, invmat)


def XYZ_to_sRGB(XYZ, illuminant='D65', gamma_encode=True):
    """Convert XYZ points to sRGB values.

    Parameters
    ----------
    XYZ : `numpy.ndarray` ndarray with last dimension X, Y, Z
    illuminant : `str`, {'D50', 'D65'}
        which white point illuminant to use

    gamma_encode : `bool`
        if True, apply sRGB_oetf to the data for display,
        if false, leave values in linear regime.

    Returns
    -------
    `numpy.ndarray`
        array with last dimension R, G, B

    Raises
    ------
    ValueError
        invalid illuminant

    """
    if illuminant.upper() == 'D65':
        invmat = COLOR_MATRICIES['sRGB']['D65']
    elif illuminant.upper() == 'D50':
        invmat = COLOR_MATRICIES['sRGB']['D50']
    else:
        raise ValueError('Must use D65 or D50 illuminant.')

    if gamma_encode is True:
        rgb = XYZ_to_RGB(XYZ, invmat)
        return sRGB_oetf(rgb)
    else:
        return XYZ_to_RGB(XYZ, invmat)


def XYZ_to_RGB(XYZ, conversion_matrix, XYZ_scale=20):
    """Convert XYZ points to RGB points.

    Parameters
    ----------
    XYZ : `numpy.ndarray`
        array with last dimension X, Y, Z
    conversion_matrix : `str`
        conversion matrix to use to convert XYZ to RGB values
    XYZ_scale : `float`
        maximum value of XYZ values; XYZ will be normalized by this prior to conversion

    Returns
    -------
    `numpy.ndarray`
        array with last dimension R, G, B

    """
    XYZ = np.asarray(XYZ) / XYZ_scale
    if len(XYZ.shape) == 1:
        return np.matmul(conversion_matrix, XYZ)
    else:
        return np.tensordot(XYZ, conversion_matrix, axes=((2), (1)))


def sRGB_oetf(L):
    """Opto-electrical transfer function for the sRGB colorspace.  Similar to gamma.

    Parameters
    ----------
    L : `numpy.ndarray`
        sRGB values

    Returns
    -------
    `numpy.ndarray`
        L', L modulated by the oetf

    Notes
    -----
    input must be an array, cannot be a scalar

    """
    L = np.asarray(L)
    negative = L < 0
    L_l = L.copy()
    L_l[negative] = 0.0
    return np.where(L_l <= 0.0031308, L_l * 12.92, 1.055 * (L_l ** (1 / 2.4)) - 0.055)


def sRGB_reverse_oetf(V):
    """Reverse Opto-electrical transfer function for the sRGB colorspace.  Similar to gamma.

    Parameters
    ----------
    V : `numpy.ndarray`
        sRGB values

    Returns
    -------
    `numpy.ndarray`
        V', V modulated by the oetf

    """
    V = np.asarray(V)
    return np.where(V <= sRGB_oetf(0.0031308), V / 12.92, ((V + 0.055) / 1.055) ** 2.4)
