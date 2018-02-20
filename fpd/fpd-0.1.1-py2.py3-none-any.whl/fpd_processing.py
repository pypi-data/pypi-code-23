from __future__ import print_function

import numpy as np
import scipy as sp
from scipy.ndimage.filters import gaussian_filter, gaussian_filter1d
#from scipy.ndimage.measurements import center_of_mass
from scipy.signal import fftconvolve

import matplotlib as mpl
import matplotlib.pyplot as plt

from skimage.feature import canny, peak_local_max
from skimage.transform import hough_circle
from skimage import color
from skimage.draw import circle_perimeter
from skimage.feature import register_translation
#from skimage.transform import pyramid_expand
from skimage.filters import threshold_otsu
from skimage.morphology import disk, binary_closing, binary_opening

import h5py
import datetime
import os
import multiprocessing as mp
from functools import partial
import sys
import itertools
import collections
import time
import warnings
from numbers import Number
from tqdm import tqdm

from itertools import combinations
from collections import namedtuple

from . import _p3



def _check_libs():
    try:
        import numpy as np
        import ctypes
        from ctypes.util import find_library
        
        # https://stackoverflow.com/questions/29559338/set-max-number-of-threads-at-runtime-on-numpy-openblas

        #np.show_config()
        # this is hard coded so may not be always reliable
        blas_libs = np.__config__.openblas_info['libraries']
        openblas_lib = None
        if any([x.lower()=='openblas' for x in blas_libs]):
            libpath = find_library('openblas')
            openblas_lib = ctypes.cdll.LoadLibrary(libpath)
        if openblas_lib:
            ob_threads = openblas_lib.openblas_get_num_threads()
            if ob_threads !=1:
                # doesn't seem to work:
                openblas_lib.openblas_set_num_threads(1)
                print('-------------------------------------------------------------------')
                print('FPD: It looks like numpy is using OpenBLAS with %d threads.' %(ob_threads))
                print('FPD: Performance might be improved by running with 1 thread.')
                print("FPD: Try setting env variable 'OMP_NUM_THREADS=1' before importing.")
                print('-------------------------------------------------------------------\n')
    except:
        pass
_check_libs()



def _int_factors(n):
    '''
    Return 1D array of factors of integer, n, in ascending order.
    
    '''
    
    nat_nums = np.arange(1, n+1)
    rems = np.remainder(n, nat_nums)
    inds = np.where(rems == 0)
    factors = nat_nums[inds]
    return factors


def _find_nearest_int_factor(n, f):
    '''
    Returns tuple of:
        nearest integer factor of n to f
        factors
    
    '''
    
    factors = _int_factors(n)
    i = np.abs(factors - f).argmin()
    factor = factors[i]
    return factor, factors



#--------------------------------------------------
def rebinA(a, *args):
    '''
    Return array 'a' rebinned to shape provided in args.
    
    Parameters
    ----------
    a : array-like
        Array to be rebinned.
    args : tuple
        New shape.
    
    Returns
    -------
    Rebinned array.
    
    Notes
    -----
    Based on http://scipy-cookbook.readthedocs.io/items/Rebinning.html

    Examples
    --------
    >>> import fpd.fpd_processing as fpdp
    >>> import numpy as np
    
    >>> a = np.random.rand(6, 4, 2)
    >>> print(a.shape)
    (6, 4, 2)
    
    >>> b = fpdp.rebinA(a, *[i//2 for i in a.shape])
    >>> print(b.shape)
    (3, 2, 1)
    
    '''

    shape = a.shape
    lenShape = len(shape)
    factor = (np.asarray(shape)/np.asarray(args)).astype(int)
    evList = ['a.reshape('] + \
             ['args[%d],factor[%d],'%(i, i) for i in range(lenShape)] + \
             [')'] + ['.sum(%d)'%(i+1) for i in range(lenShape)]
    #print(''.join(evList))
    return eval(''.join(evList))


#--------------------------------------------------
def _block_indices(dshape, ncr):  
    '''
    Generate list of indices of blocks of data of shape dshape of size ncr.
    
    Parameters
    ----------
    dshape : tuple
        Shape of data array.
    ncr : tuple, None
        Chunk length in each axis.
        If any entry is None, indices will be for all data.
        
    Returns
    -------
    List of lists by which chunks of array may be indixed.
    
    Examples
    --------
    >>> import fpd.fpd_processing as fpdp
    >>> fpdp._block_indices(dshape=(5,8), ncr=(None,)*2)
    [[(0, 5)], [(0, 8)]]

    >>> r_if, c_if = fpdp._block_indices(dshape=(5,8), ncr=(3,)*2)
    >>> print(r_if, c_if)
    [(0, 3), (3, 5)] [(0, 3), (3, 6), (6, 8)]
    
    >>> for i,(ri, rf) in enumerate(r_if):
    ...     for j,(ci, cf) in enumerate(c_if):
    ...         print('\tScan [row,col] chunk [%d, %d] of [%d, %d] - %05.1f%%' %(i+1, j+1, len(r_if), len(c_if), (j+1+i*len(c_if))*100.0/(len(c_if)*len(r_if))), end='\r')
    >>>
    >>>     # data_out[ri:rf,ci:cf] = f(data[ri:rf,ci:cf])

    '''
    
    assert len(dshape) >= len(ncr)
    
    inds = [list(range(x)) for x in dshape[:len(ncr)]]
    ns = [n if n is not None else dshape[i] for (i, n) in enumerate(ncr)]
    rc_ifs = [list(zip([0]+inds[i][n::n],
                  inds[i][n::n]+[inds[i][-1]+1])) for i, n in enumerate(ns)]
    return rc_ifs


#--------------------------------------------------
def sum_im(data, nr, nc, mask=None):
    '''
    Return a real-space sum image from data. 
    
    Parameters
    ----------
    data : array_like
        Mutidimensional fpd data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    mask : 2-D array or None
        Mask is applied to data before taking sum.
        Shape should be that of the detector.
        
    Returns
    -------
    Array of shape (scanY, scanX, ...).
    
    Notes
    -----
    If nr or nc are None, the entire dimension is processed at once. 
    
    '''
    
    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    if mask is not None:
        for i in range(len(nondet)): 
            mask = np.expand_dims(mask, 0)
            # == mask = mask[None,None,None,...]
       
    sum_im = np.empty(nondet)
    print('Calculating real-space sum images.')
    total_ims = np.prod(nondet)
    with tqdm(total=total_ims, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):                
                if mask is None:
                    d = data[ri:rf, ci:cf, ...]
                else:
                    d = (data[ri:rf, ci:cf, ...]*mask)
                sum_im[ri:rf, ci:cf, ...] = d.sum((-2, -1))
                pbar.update(np.prod(d.shape[:-2]))
    print('\n')
    return sum_im


#--------------------------------------------------
def sum_dif(data, nr, nc, mask=None):
    '''
    Return a summed diffraction image from data. 
    
    Parameters
    ----------
    data : array_like
        Mutidimensional fpd data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    mask : array-like or None
        Mask applied to data before taking sum.
        Shape should be that of the scan.
        
    Returns
    -------
    Array of shape (..., detY, detX).
    
    Notes
    -----
    If nr or nc are None, the entire dimension is processed at once. 
    
    '''
    
    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    if mask is not None:
        for i in range(len(nonscan)): 
            mask = np.expand_dims(mask, -1)
            # == mask = mask[..., None,None,None]
            
    sum_dif = np.zeros(nonscan)
    print('Calculating diffraction sum images.')
    total_ims = np.prod(nondet)
    with tqdm(total=total_ims, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):           
                if mask is None:
                    d = data[ri:rf, ci:cf, ...]
                else:
                    d = (data[ri:rf, ci:cf, ...]*mask)
                sum_dif += d.sum((0, 1))
                pbar.update(np.prod(d.shape[:-2]))
    print('\n')
    return sum_dif


#--------------------------------------------------
def synthetic_aperture(shape, cyx, rio, sigma=1, dt=np.float, aaf=3, norm=True):
    '''
    Create circular synthetic apertures. Sub-pixel accurate with aaf>1.
    
    Parameters
    ----------
    shape : length 2 iterable
        Image data shape (y,x).
    cyx : length 2 iterable
        Centre y, x pixel cooridinates
    rio : 2d array or length n itterable
        Inner and outer radii [ri,ro) in a number of forms.
        If a length n itterable and not 2d array, n-1 apertures are returned.
        If a 2d array of shape nx2, rio are taken from rows.
    sigma : scalar
        Stdev of Gaussian filter applied to aperture.
    dt : datatype
        Numpy datatype of returned array. If integer type, data is scaled.
    aaf : integer
        Anti-aliasing factor. Use 1 for none.
    norm : bool
        Controls normalisation of actual to ideal area. 
        For apertures extending beyond the image border, the value is 
        increase to give the same 'volume'.
    
    Returns
    -------
    Array of shape (n_ap, y, x).
    
    Notes
    -----
    Some operations may be more efficient if dt is of the same type as 
    the data to which it will be applied.
    
    Examples
    --------
    >>> import fpd.fpd_processing as fpdp
    >>> import matplotlib.pyplot as plt
    >>> plt.ion()
    
    >>> aps = fpdp.synthetic_aperture((256,)*2, (128,)*2, np.linspace(32, 192, 10))
    >>> _ = plt.matshow(aps[0])
    
    '''
    
    assert type(aaf) == int
    
    if type(rio) == np.ndarray and rio.ndim == 2:
        n = rio.shape[0]
    else:
        n = len(rio)-1
        rio = list(zip(rio[:-1], rio[1:]))
    
    m = np.ones((n,)+shape, dtype=dt)
    
    # prepare boolean edge selection
    yi, xi = np.indices(shape)
    ri = ((xi-cyx[1])**2 + (yi-cyx[0])**2)**0.5
    yb = np.logical_or(yi == 0, yi == shape[0]-1)
    xb = np.logical_or(xi == 0, xi == shape[1]-1)
    bm = np.logical_or(xb, yb)    
    ri_edge = ri[bm]
    ri_min = ri_edge.min()
    
    cy, cx = [t*aaf for t in cyx]
    shape = tuple([t*aaf for t in shape])
    y, x = np.indices(shape)
    sigma *= aaf
    
    for i, rio in enumerate(rio):
        ri, ro = [t*aaf for t in rio]
        r = np.sqrt((x - cx)**2 + (y - cy)**2)
        mi = np.logical_and(r >= ri, r < ro)
        mi = gaussian_filter(mi.astype(np.float),
                             sigma, 
                             order=0,
                             mode='reflect')
        
        if np.issubdtype(dt, float):
            mi = mi.astype(dt)
        elif np.issubdtype(dt, 'uint'):
            mi = (mi/mi.max()*np.iinfo(dt).max).astype(dt)
        else:
            print("WARNING: dtype '%s' not supported!" %(dt))
            mi = np.ones(shape)*np.nan
        if aaf != 1:
            mi = sp.ndimage.interpolation.zoom(mi, 
                                               1.0/aaf, 
                                               output=None,
                                               order=1,
                                               mode='constant',
                                               cval=0.0,
                                               prefilter=True)
        # clip any values outside range coming from interpolation
        mi = mi.clip(0, 1)
        if norm:
            mi *= (np.pi*(ro**2-ri**2)/aaf**2)/mi.sum()     # normalisation
        elif rio[1] > ri_min:
            #warnings.simplefilter('always', UserWarning)
            #warnings.warn(('Apperture may extend beyond image.'
            #               +' Consider setting norm to False.')
            #               , UserWarning) 
            #warnings.filters.pop(0)
            print("WARNING: Aperture extends beyond image (max r = %0.1f). Consider setting norm to True. 'rio':" %(ri_min), rio)
        m[i, :, :] = mi
    return m


#--------------------------------------------------
def synthetic_images(data, nr, nc, apertures):
    '''
    Make synthetic images from data and aperture.
    
    Parameters
    ----------
    data : array_like
        Mutidimensional fpd data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    apertures : array-like
        Mask applied to data before taking sum.
        Shape should 3-D (apN, detY, detX).
        
    Returns
    -------
    Array of shape (apN, scanY, scanX, ...).
    
    Notes
    -----
    If nr or nc are None, the entire dimension is processed at once. 
    
    '''
    
    apertures = np.rollaxis(apertures, 0, 3)
    apN = apertures.shape[-1] 

    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    for i in range(len(nondet)): 
        apertures = np.expand_dims(apertures, 0)
        # == apertures = apertures[None,None,None,...]
    
    sim = np.empty(nondet + (apN,))
    print('Calculating synthetic aperture images.')
    total_ims = np.prod(nondet)
    with tqdm(total=total_ims, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):
                d = data[ri:rf, ci:cf, ...][..., None]
                # extra -1 for extra last axis
                sim[ri:rf, ci:cf, ...] = (d*apertures).sum((-3, -2))
                pbar.update(np.prod(d.shape[:-3]))
    print('\n')
    return np.rollaxis(sim, -1, 0)


#--------------------------------------------------
def find_circ_centre(im, sigma, rmms, mask=None, plot=True, spf=1, low_threshold=0.1,
                     high_threshold=0.2):
    '''
    Find centre and radius of circle in image. Sub-pixel accurate with spf>1.
    
    Parameters
    ----------
    im : 2-D array
        Image data.
    sigma : scalar
        Smoothing width for canny edge detection .
    rmms : length 3 iterable
        Radius (min, max, step) in pixels.
    mask : array-like or None
        Mask for canny edge detection.
        If None, no mask is applied.
    plot : bool
        Determines if best matching circle is plotted in matplotlib.
    spf : integer
        Sub-pixel factor. 1 for none. 
        If not None, step is forced to 1 and corresponds to 1/spf pixels.
    low_threshold : float
        Lower bound for hysteresis thresholding (linking edges) in [0, 1].
    high_threshold : float
        Upper bound for hysteresis thresholding (linking edges) in [0, 1].
    
    Returns
    -------
    Tuple of (center_y, center_x), radius.
    
    Notes
    -----
    Image is first scaled to full range of dtype, then upscaled if chosen.
    Canny edge detection is performed, followed by a Hough transform.
    Linking of edges is set by thresholds. See skimage.feature.canny for
    details. The single best matching circle is returned.
    
    Examples
    --------
    Two calls can be made to make subpixel calculations efficient by 
    reducing the range over which the Hough transform takes place.
    
    >>> import fpd.fpd_processing as fpdp
    >>> from fpd.synthetic_data import disk_image
    
    >>> im = disk_image(intensity=64, radius=32)
    >>> rmms = (10, 100, 2)
    >>> spf = 1
    >>> sigma = 2
    >>> cyx, r = fpdp.find_circ_centre(im, sigma, rmms, mask=None, plot=True, spf=spf)
    
    >>> rmms = (r-4, r+4, 1)
    >>> spf = 4
    >>> cyx, r = fpdp.find_circ_centre(im, sigma, rmms, mask=None, plot=True, spf=spf)
    
    '''
    
    #TODO
    #decision on best centre, improved?
    #subpixel by 2-d gaussian fitting to hough space?
    
    ## scale im so default thresholding works appropriately (% of range)
    #im = (im.astype(np.float)/im.max()*np.iinfo(im.dtype).max)
    #im = im.astype(im.dtype)
    im = im.astype(float)
    
    if spf > 1:
        spf = float(spf)
        im = sp.ndimage.interpolation.zoom(im,
                                           spf,
                                           output=None,
                                           order=1,
                                           mode='reflect',
                                           prefilter=True)
        rmms = [x*spf for x in rmms[:2]] + [1]
    
    if plot: 
        kwd = dict(adjustable='box-forced', aspect='equal')
        f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharex=True, sharey=True,
                                          subplot_kw=kwd, figsize=(8,3))
        # plot image
        ax1.imshow(im, interpolation='nearest', cmap='gray')#,
                    #norm=mpl.colors.LogNorm())
        ax1.set_title('Image')

    edges = canny(im, sigma, mask=mask, use_quantiles=True,
                  low_threshold=low_threshold,
                  high_threshold=high_threshold)
    if plot:
        ax2.imshow(edges, interpolation='nearest', cmap='gray')
        ax2.set_title('Edges')


    # hough transform
    hough_radii = np.arange(rmms[0], rmms[1], rmms[2])
    hough_res = hough_circle(edges, hough_radii)

    centers = []
    accums = []
    radii = []

    for radius, h in zip(hough_radii, hough_res):
        num_peaks = 1
        peaks = peak_local_max(h, num_peaks=num_peaks)
        centers.extend(peaks)
        accums.extend(h[peaks[:, 0], peaks[:, 1]])
        radii.extend([radius] * num_peaks)
        
    accum_order = np.argsort(accums)[::-1]
    
    
    # Draw the most prominent 1 circles
    if plot: imc = color.gray2rgb(im/im.max())

    for idx in accum_order[:1]:
        center_y, center_x = centers[idx]
        radius = int(radii[idx])
        cy, cx = circle_perimeter(center_y, center_x, radius)
        if plot: imc[cy, cx] = (1, 0, 0)

        if plot:
            imc[center_y, center_x] = (0, 1, 0)
            ax3.imshow(imc, interpolation='nearest')
            ax3.set_title('Detected Circle')
            plt.draw()
    
    if spf > 1:
        center_y, center_x, radius = center_y/spf, center_x/spf, radius/spf
    print('Centre:\t(%0.3f,%0.3f)\nRadius:\t%0.3f' %(center_y, center_x, radius))

    return (center_y, center_x), radius


#--------------------------------------------------
def radial_average(data, cyx, mask=None, r_nm_pp=None, plot=False, spf=1.0):
    '''
    Returns the radial average of one image or multiple images.
    Sub-pixel accurate with spf>1.
    
    Parameters
    ----------
    data : ndarray
        Image data of shape (...,y,x).
    cyx : length 2 tuple
        Centre y, x pixel cooridinates.
    r_nm_pp : scalar or None
        Value for reciprocal nm per pixel.
        If None, values are in pixels.
    spf : scalar
        Sub-pixel factor for upscaling to give sub-pixel calculations. 
        If 1, pixel level calculations.
        
    Returns
    -------
    r_pix, rms : tuple of ndarrays
        radii, mean intensity
    
    Notes
    -----
    If r_nm_pp is not None, radii is in 1/nm, otherwise in pixels.
    This is convenient when analysing diffraction data. 
    
    Examples
    --------
    >>> import numpy as np
    >>> import fpd.fpd_processing as fpdp
    
    >>> cyx = (128,)*2
    >>> im_shape = (256,)*2
    >>> y, x = np.indices(im_shape)
    >>> r = np.sqrt((y - cyx[0])**2 + (x - cyx[1])**2)
    >>> data = np.dstack((r**0.5, r, r**2))
    >>> data = np.rollaxis(data, 2, 0)

    >>> r_pix, radial_mean = fpdp.radial_average(data, cyx, plot=True, spf=2)
    
    '''
    
    if r_nm_pp is None:
        r_nm_pp = 1.0
        xlab = 'Pixel'
    else:
        xlab = '1/nm'
        
    if len(data.shape) == 2:
        # single image, reshaped to 1 x Y x X
        data = data[None, ...]
        nr = 1
        nc = 1
        nonim_shape = (1,)
    else:
        # fpd data with images in last 2 dims
        nonim_shape = data.shape[:-2]
    
    if spf>1:
        spf = float(spf)
        r_nm_pp /= spf
        cyx = [x*spf for x in cyx]
        data = sp.ndimage.interpolation.zoom(data, 
                                             (1,)*len(nonim_shape)+(spf,)*2, 
                                             output=None, 
                                             order=3, 
                                             mode='reflect', 
                                             prefilter=True)
    im_shape = data.shape[-2:]
    y, x = np.indices(im_shape)
    r = np.sqrt((y - cyx[0])**2 + (x - cyx[1])**2)
    r = r.astype(np.int)     # need int for bincounting

    if mask is not None:
        if spf > 1:
            mask = sp.ndimage.interpolation.zoom(mask, 
                                                 spf, 
                                                 output=None,
                                                 order=0,
                                                 mode='reflect',
                                                 prefilter=True)
        r = r[mask]

    for i in range(np.prod(nonim_shape)):
        nd_indx = np.unravel_index(i, nonim_shape)
        
        di = data[nd_indx]
        if mask is not None:
            di = di[mask]

        with np.errstate(invalid='ignore', divide='ignore'):
            tbin = np.bincount(r.ravel(), di.ravel())
            nr = np.bincount(r.ravel())
            radial_mean = tbin / nr
        if i == 0:
            rms = np.empty(nonim_shape + radial_mean.shape)
        rms[nd_indx] = radial_mean[:]
    r_pix = np.arange(radial_mean.shape[0])*r_nm_pp
    
    if plot:
        f, ax = plt.subplots()
        ax.plot(r_pix, rms.T)
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel(xlab)
        plt.ylabel('Mean Intensity')
        plt.tight_layout()
        plt.draw()
    
    return (r_pix, rms)


#--------------------------------------------------
def _comf(d, use_ap, aperture, yixi, thr):
    '''
    CoM process data function that operates on single image at a time.
    
    See 'center_of_mass' for 'thr' and 'aperture' documentation.
    
    d is 2-D image.
    use_ap is boolean determining is aperture is used.
    yixi is index array, as defined in calling function.
    
    '''
    
    if _p3:
        s_obj = str
    else:
        s_obj = basestring    

    
    if thr is None:
        pass
    elif isinstance(thr, Number):
        d = (d >= thr)
    elif isinstance(thr, s_obj):
        if thr.lower() == 'otsu':
            thr_val = threshold_otsu(d)
            d = (d >= thr_val)
        else:
            # string not understood
            pass
    elif callable(thr):
        # function
        d = thr(d)
        
    if use_ap:
        d = d*aperture
    ds = d.sum((0, 1))                     # sum_im
    comi = (d[..., None]*yixi).sum((0, 1))/ds[..., None]
    return comi


class DummyFile(object):
    def flush(self): pass
    def write(self, x): pass


#--------------------------------------------------
def center_of_mass(data, nr, nc, aperture=None, pre_func=None, thr=None,
                   rebin=None, parallel=True, ncores=None, print_stats=True,
                   origin='top'):
    '''
    Calculate a centre of mass image from fpd data. The results are
    naturally sub-pixel resolution.
    
    Parameters
    ----------
    data : array_like
        Mutidimensional data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    aperture : array_like
        Mask of shape (detY, detX), applied to diffraction data after
        `pre_func` processing. Note, the data is automatically cropped
        according to the mask for efficiency.
    pre_func : callable
        Function that operates (out-of-place) on data before processing.
        out = pre_func(in), where in is nd_array of shape (n, detY, detX).
    thr : object
        Control thresholding of difraction image.
        If None, no thresholding.
        If scalar, threshold value.
        If string, 'otsu' for otsu thresholding.
        If callable, function(2-D array) returns thresholded image.
    rebin : integer or None
        Rebinning factor for detector dimensions. None or 1 for none. 
        If the value is incompatible with the cropped array shape, the
        nearest compatible value will be used instead. 
    parallel : bool
        If True, calculations are multiprocessed.
    ncores : None or int
        Number of cores to use for mutliprocessing. If None, all cores
        are used.
    print_stats : bool
        If True, statistics on the analysis are printed.
    origin : str
        Controls y-origin of returned data. If origin='top', pythonic indexing 
        is used. If origin='bottom', increasing y is up.
    
    Returns
    -------
    Array of shape (yx, scanY, scanX, ...).
    Increasing Y, X CoM is disc shift up, right in image.
    
    Notes
    -----
    The order of operations is rebinning, pre_func, threshold, aperture,
    and CoM.
    
    If nr or nc are None, the entire dimension is processed at once. 
    
    The execution of pre_func is not multiprocessed, so it could employ 
    multiprocessing for cpu intensive calculations.
    
    Multiple processing runs at a similar speed as non parallel code
    in simplest case.
    
    Possible alternative was not as fast in tests:
    from scipy.ndimage.measurements import center_of_mass
    
    Examples
    --------
    Using an aperture and rebinning:
    
    >>> import numpy as np
    >>> import fpd.fpd_processing as fpdp
    >>> from fpd.synthetic_data import disk_image, fpd_data_view
    
    >>> radius = 32
    >>> im = disk_image(intensity=1e3, radius=radius, size=256, upscale=8, dtype='u4')
    >>> data = fpd_data_view(im, (32,)*2, colours=0)
    >>> ap = fpdp.synthetic_aperture(data.shape[-2:], cyx=(128,)*2, rio=(0, 48), sigma=0, aaf=1)[0]
    >>> com_y, com_x = fpdp.center_of_mass(data, nc=9, nr=9, rebin=3, aperture=ap)
    
    
    '''
    
    if ncores is None:
        ncores = mp.cpu_count()
    
    # rebinning
    rebinf = 1
    rebinning = rebin is not None and rebin != 1
    if rebinning:
        rebinf = rebin
    
    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    use_ap = False
    if isinstance(aperture, np.ndarray):
        # determine limits to index array for efficiency
        rii, rif = np.where(aperture.sum(axis=1) > 0)[0][[0, -1]]
        cii, cif = np.where(aperture.sum(axis=0) > 0)[0][[0, -1]]
        use_ap = True
        aperture = aperture[rii:rif+1, cii:cif+1].astype(np.float)
    else:
        rii, rif = 0, detY-1
        cii, cif = 0, detX-1
    data_square_len = rif-rii+1
    
    if rebinning:
        f, fs = _find_nearest_int_factor(data_square_len, rebin)
        if rebin != f:
            print('(Cropped) image data shape:', (data_square_len,)*2)
            print('Requested rebin (%d) changed to nearest value (%d). Possible values are:' %(rebin, f), fs)
            rebin = f
        if use_ap:
            ns = tuple([int(x/rebin) for x in aperture.shape])
            aperture = rebinA(aperture, *ns)
    
    
    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    com_im = np.zeros(nondet + (2,), dtype=np.float)
    yi, xi = np.indices((detY, detX))
    yi = yi[::-1, ...]   # reverse order so increasing Y is up.
    
    yixi = np.concatenate((yi[..., None], xi[..., None]), 2)
    yixi = yixi[rii:rif+1, cii:cif+1, :].astype(np.float)
    if rebinning:
        ns = tuple([int(x/rebin) for x in yixi.shape[:2]]) + yixi.shape[2:]
        yixi = rebinA(yixi, *ns)
    
    if print_stats:
        print('Calculating centre-of-mass images.')
        tqdm_file = sys.stderr
    else:
        tqdm_file = DummyFile()
    total_nims = np.prod(nondet)
    with tqdm(total=total_nims, file=tqdm_file, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):               
                d = data[ri:rf, ci:cf, ..., rii:rif+1, cii:cif+1].astype(np.float)
                d = np.ascontiguousarray(d)
                if rebinning:
                    ns = d.shape[:-2] + tuple([int(x/rebin) for x in d.shape[-2:]])
                    d = rebinA(d, *ns)
                
                # modify with function
                if pre_func is not None:
                    d = pre_func(d)
                
                partial_comf = partial(_comf, 
                                       use_ap=use_ap, 
                                       aperture=aperture, 
                                       yixi=yixi, 
                                       thr=thr)
                
                d_shape = d.shape   # scanY, scanX, ..., detY, detX
                d.shape = (np.prod(d_shape[:-2]),) + d_shape[-2:]   
                # (scanY, scanX, ...), detY, detX
                
                if parallel:
                    pool = mp.Pool(processes=ncores)
                    rslt = pool.map(partial_comf, d)
                    pool.close()
                else:
                    rslt = list(map(partial_comf, d))
                rslt = np.asarray(rslt)
                
                #print(d_shape, com_im[ri:rf,ci:cf,...].shape, rslt.shape)
                rslt.shape = d_shape[:-2]+(2,)
                com_im[ri:rf, ci:cf, ...] = rslt
                pbar.update(np.prod(d.shape[:-2]))
    if print_stats:
        print('\n')
    com_im = (com_im)/rebinf**2 
    
    # roll: (scanY, scanX, ..., yx) to (yx, scanY, scanX, ...) 
    com_im = np.rollaxis(com_im, -1, 0)
    
    # default origin implementation is bottom
    if origin.lower() == 'top':
        com_im[0] = nonscan[0]-1 - com_im[0]
    
    # print some stats
    if print_stats:
        _print_shift_stats(com_im)
    
    return com_im


#--------------------------------------------------
def _g2d_der(sigma, truncate=4.0):
    '''
    Returns tuple (gy, gy) of first partial derivitives of Gaussian.
    Y increasing is up.
    
    '''
    
    d = int(np.ceil(sigma*truncate))
    dtot = 2*d+1
    y, x = np.indices((dtot,)*2)-d
    
    gx = -x/(2*np.pi*sigma**4)*np.exp(-(x**2+y**2)/(2*sigma**2))
    gy = -np.rollaxis(gx, 1, 0) # -ve to have y increasin upward
    #plt.matshow(gx)
    #plt.matshow(gy)
    
    return (gy, gx)


#--------------------------------------------------
def _grad(im, gxy, mode):
    '''
    Calculate gradient by colvolving 'im' with 'gxy'.
    'mode' is passed to fftconvolve.
    
    '''
    img = np.abs(fftconvolve(im, gxy, mode))
    return img



def _process_grad(d, pre_func, mode, sigma, truncate, gxy, 
                  parallel, ncores, post_func):
    ''' Calculate gradients. '''
    
    if pre_func is not None:
        d = pre_func(d)
    
    if mode == '1d':
        # ok for small sigma, poor at diagonals at high sigma 
        df = d.astype(float)
        gy = gaussian_filter1d(df, sigma=sigma, axis=-2, order=1,
                            mode='reflect', truncate=truncate)
        gx = gaussian_filter1d(df, sigma=sigma, axis=-1, order=1, 
                            mode='reflect', truncate=truncate)
        gm = (gy**2+gx**2)**0.5
    elif mode == '2d':        
        partial_grad = partial(_grad, gxy=gxy, mode='same')
        d_shape = d.shape
        d.shape = (np.prod(d_shape[:-2]),)+d_shape[-2:]
        
        if parallel:
            pool = mp.Pool(processes=ncores)
            rslt = pool.map(partial_grad, d)
            pool.close()
        else:
            rslt = list(map(partial_grad, d))
        gm = np.asarray(rslt)
    else:
        raise ValueError('Mode value unknown.')
    
    if post_func is not None:
        gm = post_func(gm)
    
    gm = gm.reshape((-1,) + gm.shape[-2:])
    return gm



#--------------------------------------------------
def phase_correlation(data, nr, nc, cyx=None, crop_r=None, sigma=2.0,
                      spf=100, pre_func=None, post_func=None, mode='2d',
                      ref_im=None, rebin=None, truncate=4.0, parallel=True,
                      ncores=None, print_stats=True, origin='top'):
    '''
    Perform phase correlation on fpd data using efficient upscaling to
    achieve sub-pixel resolution.
    
    Parameters
    ----------
    data : array_like
        Mutidimensional data of shape (scanY, scanX, ..., detY, detX).
    nr : integer or None
        Number of rows to process at once (see Notes).
    nc : integer or None
        Number of columns to process at once (see Notes).
    cyx : length 2 iterable or None
        Centre of disk in pixels (cy, cx).
        If None, centre is used.
    crop_r : scalar or None
        Radius of circle about cyx defining square crop limits used for
        cross-corrolation, in pixels.
        If None, the maximum square array about cyx is used.
    sigma : scalar
        Smoothing of Gaussian derivitive.
    spf : integer
        Sub-pixel factor i.e. 1/spf is resolution.
    pre_func : callable
        Function that operates (out-of-place) on data before processing.
        out = pre_func(in), where in is nd_array of shape (n, detY, detX).
    post_func : callable
        Function that operates (out-of-place) on data after derivitive.
        out = post_func(in), where in is nd_array of shape (n, detY, detX).
    mode : string
        Derivative type. 
        If '1d', 1d convolution; faster but not so good for high sigma.
        If '2d', 2d convolution; more accurate but slower.
    ref_im : None or ndarray
        2-D image used as reference. 
        If None, the first probe position is used.
    rebin : integer or None
        Rebinning factor for detector dimensions. None or 1 for none. 
        If the value is incompatible with the cropped array shape, the
        nearest compatible value will be used instead. 
        'cyx' and 'crop_r' are for the original image and need not be modified.
        'sigma' and 'spf' are scaled with rebinning factor, as are output shifts.
    truncate : scalar
        Number of sigma to which Gaussians are calculated.
    parallel : bool
        If True, derivative and correlation calculations are multiprocessed.
        Note, if `mode=1d`, the derivative calculations are not multiprocessed,
        but may be multithreaded if enabled in the numpy linked BLAS lib.
    ncores : None or int
        Number of cores to use for mutliprocessing. If None, all cores
        are used.
    print_stats : bool
        If True, statistics on the analysis are printed.
    origin : str
        Controls y-origin of returned data. If origin='top', pythonic indexing 
        is used. If origin='bottom', increasing y is up.
        
    Returns
    -------
    Tuple of (shift_yx, shift_err, shift_difp, ref), where:
    shift_yx : array_like
        Shift array in pixels, of shape ((y,x), scanY, scanX, ...).
        Increasing Y, X is disc shift up, right in image.
    shift_err : 2-D array
        Translation invariant normalized RMS error in correlations.
        See skimage.feature.register_translation for details.
    shift_difp : 2-D array
        Global phase difference between the two images.
        (should be zero if images are non-negative).
        See skimage.feature.register_translation for details.
    ref : 2-D array
        Reference image.
    
    Notes
    -----
    The order of operations is rebinning, pre_func, derivative, 
    post_func, and correlation.
    
    If nr or nc are None, the entire dimension is processed at once. 
    
    Specifying 'crop_r' (and appropriate cyx) can speed up calculation significantly.
    
    The execution of 'pre_func' and 'post_func' are not multiprocessed, so 
    they could employ multiprocessing for cpu intensive calculations.
    
    Efficient upscaling is based on:
    http://scikit-image.org/docs/stable/auto_examples/transform/plot_register_translation.html
    http://scikit-image.org/docs/stable/api/skimage.feature.html#skimage.feature.register_translation
    
    '''
    
    if ncores is None:
        ncores = mp.cpu_count()
    
    nondet = data.shape[:-2]
    nonscan = data.shape[2:]
    scanY, scanX = data.shape[:2]
    detY, detX = data.shape[-2:]
    
    r_if, c_if = _block_indices((scanY, scanX), (nr, nc))
    
    if crop_r is None:
        # all indices
        rii, rif = 0, detY-1
        cii, cif = 0, detX-1
    else:
        crop_r = np.round([crop_r]).astype(int)[0]
        if cyx is None:
            cyx = [(detY-1)/2.0, (detX-1)/2.0]
        cy, cx = np.round(cyx).astype(int)
    
        crop_r_max = int(min(cx, detX-1-cx, cy, detY-1-cy))  # L R T B
        if crop_r > crop_r_max:
            print("WARNING: 'crop_r' (%d) is being set to max. value (%d)." %(crop_r, crop_r_max))
            crop_r = crop_r_max
        # indices
        rii, rif = (cy-crop_r, cy+crop_r-1)
        cii, cif = (cx-crop_r, cx+crop_r-1)
    cropped_im_shape = (rif+1-rii, cif+1-cii)
       
    
    # rebinning
    rebinf = 1
    rebinning = rebin is not None and rebin != 1
    if rebinning:
        f, fs = _find_nearest_int_factor(cropped_im_shape[0], rebin)
        if rebin != f:
            print('Image data cropped to:', cropped_im_shape)
            print('Requested rebin (%d) changed to nearest value: %d. Possible values are:' %(rebin, f), fs)
            rebin = f
        rebinf = rebin
        sigma = float(sigma)/rebinf
        spf = int(float(spf)*rebinf)
    rebinned_im_shape = tuple([x//rebinf for x in cropped_im_shape])
    #print('Cropped shape: ', cropped_im_shape)
    #if rebinning:
        #print('Rebinned cropped shape: ', rebinned_im_shape)
    
    
    # gradient of gaussian
    gy, gx = _g2d_der(sigma, truncate=truncate)
    gxy = gx + 1j*gy
    #gxy = (gx**2 + gy**2)**0.5
    
    
    ### ref im
    if ref_im is None:
        # use first point
        ref_im = data[0, 0, ...]
        for i in range(len(nondet)-2):
            ref_im = ref_im[0]
    else:
        # provided option
        ref_im = ref_im
    
    ref = ref_im[rii:rif+1, cii:cif+1]
    for t in range(len(nondet)): 
        ref = np.expand_dims(ref, 0)    # ref[None, None, None, ...]
    if rebinning:
        ns = ref.shape[:-2] + tuple([int(x/rebin) for x in ref.shape[-2:]])
        ref = rebinA(ref, *ns)
    ref = _process_grad(ref, pre_func, mode, sigma, truncate, gxy,
                        parallel, ncores, post_func)[0]
    
    
    shift_yx = np.empty(nondet + (2,))
    shift_err = np.empty(nondet)
    shift_difp = np.empty_like(shift_err)
    
    if print_stats:
        print('\nCalculating phase correlation shift.')
        tqdm_file = sys.stderr
    else:
        tqdm_file = DummyFile()
    total_nims = np.prod(nondet)
    with tqdm(total=total_nims, file=tqdm_file, mininterval=0, leave=True, unit='images') as pbar:
        for i, (ri, rf) in enumerate(r_if):
            for j, (ci, cf) in enumerate(c_if):               
                # read selected data (into memory if hdf5)  
                d = data[ri:rf, ci:cf, ..., rii:rif+1, cii:cif+1]
                d = np.ascontiguousarray(d)
                if rebinning:
                    ns = d.shape[:-2] + tuple([int(x/rebinf) for x in d.shape[-2:]])
                    d = rebinA(d, *ns)
                
                # calc grad
                gm = _process_grad(d, pre_func, mode, sigma, truncate, gxy,
                                   parallel, ncores, post_func)
                
                # Could combine grad and reg to skip ifft/fft,
                # and calc ref grad fft only once
                # For 1d mode, could try similar combinations, but using 
                # functions across ndarray axes with multithreaded blas.
                
                ## do correlation
                # gm is (n, detY, detX), with last 2 rebinned
                partial_reg = partial(register_translation, ref, upsample_factor=spf)
                
                if parallel:
                    pool = mp.Pool(processes=ncores)
                    rslt = pool.map(partial_reg, gm)
                    pool.close()
                else:
                    rslt = list(map(partial_reg, gm))
                shift, error, phasediff = np.asarray(rslt).T
                shift = np.array(shift.tolist())
                # -ve shift to swap source/ref coords to be consistent with 
                # other phase analyses
                shift *= -1.0
                
                shift_yx[ri:rf, ci:cf].flat = shift
                shift_err[ri:rf, ci:cf].flat = error
                shift_difp[ri:rf, ci:cf].flat = phasediff
                
                pbar.update(np.prod(d.shape[:-2]))
    if print_stats:
        print('')
        sys.stdout.flush()    
    shift_yx = np.rollaxis(shift_yx, -1, 0)
       
    # reverse y for shift up being positive
    flp = np.array([-1, 1])
    for i in range(len(nonscan)):
        flp = np.expand_dims(flp, -1)
    shift_yx = shift_yx*flp
    
    # default origin implementation is bottom
    if origin.lower() == 'top':
        shift_yx[0] = -shift_yx[0]
        
    # scale shifts for rebinning
    if rebinning:
        shift_yx *= rebinf
    
    # print stats
    if print_stats:
        _print_shift_stats(shift_yx)

    return shift_yx, shift_err, shift_difp, ref


def _print_shift_stats(shift_yx):
    ''' Prints statistics of 'shift_yx' array'''
    shift_yx_mag = (shift_yx**2).sum(0)**0.5
    shift_yxm = np.concatenate((shift_yx, shift_yx_mag[None, ...]), axis=0)
    
    non_yx_axes = tuple(range(1, len(shift_yxm.shape)))
    yxm_mn, yxm_std = shift_yxm.mean(non_yx_axes), shift_yxm.std(non_yx_axes)
    yxm_min, yxm_max = shift_yxm.min(non_yx_axes), shift_yxm.max(non_yx_axes)
    yxm_ptp = yxm_max - yxm_min
    
    print('{:10s}{:>8s}{:>11s}{:>11s}'.format('Statistics', 'y', 'x', 'm'))
    print('{:s}'.format('-'*40))
    print('{:6s}: {:10.3f} {:10.3f} {:10.3f}'.format(*(('Mean',)+tuple(yxm_mn))))
    print('{:6s}: {:10.3f} {:10.3f} {:10.3f}'.format(*(('Min',)+tuple(yxm_min))))
    print('{:6s}: {:10.3f} {:10.3f} {:10.3f}'.format(*(('Max',)+tuple(yxm_max))))
    print('{:6s}: {:10.3f} {:10.3f} {:10.3f}'.format(*(('Std',)+tuple(yxm_std))))
    print('{:6s}: {:10.3f} {:10.3f} {:10.3f}'.format(*(('Range',)+tuple(yxm_ptp))))
    print()
    


def disc_edge_sigma(im, sigma=2, cyx=None, r=None, plot=True):
    '''
    Calculates disc edge width by averaging sigmas from fitting Erfs to unwrapped disc.
    
    Parameters
    ----------
    im : 2-D array
        Image of disc.
    sigma : scalar
        Estimate of edge stdev.
    cyx : length 2 iterable or None
        Centre coordinates of disc. If None, these are calculated.
    r : scalar or None
        Disc radius in pixels. If None, the value is calculated.
    plot : bool
        Determines if images are plotted.
    
    Returns
    -------
    sigma_wt_avg : scalar
        Average sigma value, weighted if possible by fit error.
    sigma_wt_std : scalar
        Average sigma standard deviation, weighted if possible by fit error.
        Nan if no weighting is posible.
    sigma_std : scalar
        Standard deviation of all sigma values.
    (sigma_vals, sigma_stds) : tuple of 1-D arrays
        Sigma values and standard deviations from fit.
    
    Notes
    -----
    `sigma` is used for initial value and for setting range of fit.
    Increasing value widens region fitted to.
    
    Examples
    --------
    >>> import fpd
    >>> import matplotlib.pylab as plt
    >>>
    >>> plt.ion()
    >>>
    >>> im = fpd.synthetic_data.disk_image(intensity=16, radius=32, sigma=5.0, size=256, noise=True)
    >>> cyx, r = fpd.fpd_processing.find_circ_centre(im, 2, (22, int(256/2.0), 1), spf=1, plot=False)
    >>>
    >>> returns = fpd.fpd_processing.disc_edge_sigma(im, sigma=6, cyx=cyx, r=r, plot=True)
    >>> sigma_wt_avg, sigma_wt_std, sigma_std, (sigma_vals, sigma_stds) = returns

    '''
     
    from hyperspy.signals import EELSSpectrum
    from hyperspy.component import Component

    detY, detX = im.shape
    
    if cyx is None or r is None:
        cyx_, r_ = find_circ_centre(im, 2, (3, int(detY/2.0), 1), spf=1, plot=plot)
    if cyx is None:
        cyx = cyx_
    if r is None:
        r = r_
    cy, cx = cyx
    
    # set up coordinated
    yi, xi = np.indices((detY, detX), dtype=float)
    yi-=cy
    xi-=cx
    ri2d = (yi**2+xi**2)**0.5
    ti2d = np.arctan2(yi, xi)

    interp_pix = 0.25   # interpolation resolution
    rr, tt = np.meshgrid(np.arange(0, 2.5*r, interp_pix), 
                         np.arange(-180,180,1*4)/180.0*np.pi, 
                         indexing='ij')
    xx = rr*np.sin(tt)+cx
    yy = rr*np.cos(tt)+cy

    # MAP TO RT  
    rt_val = sp.ndimage.interpolation.map_coordinates(im.astype(float), 
                                                      np.vstack([yy.flatten(), xx.flatten()]) )
    rt_val = rt_val.reshape(rr.shape)

    if plot:
        plt.matshow(rt_val)
        plt.figure()
        plt.plot(rt_val[:,::18])
        plt.xlabel('Interp pixels')
        plt.ylabel('Intensity')
    
    
    # Fit edge
    der = -np.diff(rt_val, axis=0)
    s = EELSSpectrum(rt_val.T)
    #s.align1D()
    #s.plot()

    s_av = s#.sum(0)
    #s_av.plot()
    
    s_av.metadata.set_item("Acquisition_instrument.TEM.Detector.EELS.collection_angle", 1)
    s_av.metadata.set_item("Acquisition_instrument.TEM.beam_energy ", 1)
    s_av.metadata.set_item("Acquisition_instrument.TEM.convergence_angle", 1)
    
    m = s_av.create_model(auto_background=False)
    
    # http://hyperspy.org/hyperspy-doc/v0.8/user_guide/model.html   
    class My_Component(Component):
        """
        """
        def __init__(self, origin=0, A=1, sigma=1):
            # Define the parameters
            Component.__init__(self, ('origin', 'A', 'sigma'))
            #self.name = 'Erf'

            # Optionally we can set the initial values
            self.origin.value = origin
            self.A.value = A
            self.sigma.value = sigma

        # Define the function as a function of the already defined parameters, x
        # being the independent variable value
        def function(self, x):
            p1 = self.origin.value
            p2 = self.A.value
            p3 = self.sigma.value
            #return p1 + x * p2 + p3
            return p2*( sp.special.erf( (x-p1)/(np.sqrt(2)*p3) )+1.0 ) /2.0

    g = My_Component()
    m.append(g)
    
    # set defaults
    sigma = sigma
    m.set_parameters_value('sigma',  sigma/interp_pix, component_list=[g])
    m.set_parameters_value('A', -np.percentile(rt_val, 90), component_list=[g])
    m.set_parameters_value('origin', r/interp_pix, component_list=[g])
    
    # set fit range
    ri2d_edge_min = np.concatenate((ri2d[[0, -1], :], ri2d[:, [0, -1]].T), axis=1).min()
    rmin = max( (r-3*sigma), 0 )
    rmax = min( (r+3*sigma), ri2d_edge_min )
    m.set_signal_range(rmin/interp_pix, rmax/interp_pix)
    
    m.multifit()
    if plot:
        m.plot()

    sigma_vals = np.abs(g.sigma.map['values'])*interp_pix
    sigma_stds = np.abs(g.sigma.map['std'])*interp_pix
    
    # calculate averages
    sigma_std = sigma_vals.std()
    
    err_is = np.where(np.isfinite(sigma_stds))[0]
    if err_is.size > 1:
        print('Calculating weighted average...')
        vs = sigma_vals[err_is]
        ws = 1.0/sigma_stds[err_is]**2
        sigma_wt_avg = (vs*ws).sum()/ws.sum()
        sigma_wt_std = (1.0/ws.sum())**0.5
    else:
        print('Calculating unweighted average...')
        sigma_wt_avg = sigma_vals.mean()
        sigma_wt_std = np.nan
    print('Avg: %0.3f +/- %0.3f' %(sigma_wt_avg, sigma_wt_std))
    print('Std: %0.3f' %(sigma_std))
    
    
    sigma_pcts = np.percentile(sigma_vals, [10, 50, 90])
    print('Percentiles (10, 50, 90): %0.3f, %0.3f, %0.3f' %tuple(sigma_pcts))
    
    return(sigma_wt_avg, sigma_wt_std, sigma_std, (sigma_vals, sigma_stds))


def nrmse(ref_im, test_ims):
    '''
    Euclidean normalised mean square error.
    
    Parameters
    ----------
    ref_im : 2-D array
        Reference image.
    test_ims : ndarray
        Images to compare.
    
    '''
    
    im1 = ref_im.astype(float)
    im2 = test_ims.astype(float)
    n = (((im1-im2)**2).mean((-2, -1)) / ((im1**2+im2**2).mean((-2, -1))/2))**0.5
    return n


def find_matching_images(images, aperture=None, avg_nims=3, cut_len=20, plot=True):
    '''
    Finds matching images using euclidean normalised mean square error through
    all combinations of a given number of images.
    
    Parameters
    ----------
    images : ndarray
        Array of images with image axes in last 2 dimensions.
    aperture : 2D array
        An aperture to apply to the images.
    avg_nims : int
        The number of images in a combination.
    cut_len : int
        The number of combinations in which to look for common images.
    
    Returns
    -------
    named tuple 'matching' containing:
    
    yxi_combos : tuple of two 2-D arrays
        y- and x-indices of combinations, sorted by match quality.
    yxi_common :
        y- and x-indices of most common image in ``cut_len`` combinations.
    ims_common : 3-D array
        All images in in ``cut_len`` combinations matched with most common image.
    ims_best : 3-D array
        Best matching ``avg_nims`` images.
    
    Notes
    -----
    The number of combinations increases very rapidly with ``avg_nims`` and
    the number of images. Using around 100 or so images runs relatively quickly.
    
    Examples
    --------
    >>> from fpd.synthetic_data import disk_image, shift_array, shift_images
    >>> import fpd.fpd_processing as fpdp

    Generate synthetic data.
    >>> disc = disk_image(radius=32, intensity=64)
    >>> shift_array = shift_array(6, shift_min=-1, shift_max=1)

    Set shifts on diagonal to zero.
    >>> diag_inds = [np.diag(x) for x in np.indices(shift_array[0].shape)]
    >>> shift_array[0][diag_inds] = 0
    >>> shift_array[1][diag_inds] = 0
    
    Generate shifted images.
    >>> images = shift_images(shift_array, disc, noise=False)
    >>> aperture = fpdp.synthetic_aperture(images.shape[-2:], cyx=(128,)*2, rio=(0, 48), sigma=0, aaf=1)[0]
    
    Find matching images.
    >>> matching = fpdp.find_matching_images(images, aperture, plot=True)
    >>> ims_best = matching.ims_best.mean(0)
    
    '''
    
    ims_orig = images

    # flattten original images
    ims_orig_shape = ims_orig.shape
    ims_orig.shape = (-1,) + ims_orig.shape[-2:]
    n_ims = ims_orig.shape[0]

    # apply aperture and crop
    if aperture is not None:
        ri, rf = np.where(aperture.sum(0))[0][[0, -1]]
        ci, cf = np.where(aperture.sum(1))[0][[0, -1]]
        sr = slice(ri, rf+1)
        sc = slice(ci, cf+1)
        aperture = aperture[sr, sc]
        ims = ims_orig[:, sr, sc]*(aperture[None, ...].astype(int))
    else:
        ims = ims_orig

    # calculate nrsme for all combinations in one half diagonal
    err = np.ones((n_ims, n_ims), dtype=float)
    err[:] = np.nan
    print('Calculating NRSME for all image combinations')
    for ri, ref_im in enumerate(tqdm(ims)):
        test_ims = ims[:ri]
        err_col = nrmse(ref_im, test_ims)
        err[:ri, ri] = err_col
    if plot:
        f, (ax1, ax2) = plt.subplots(1, 2, sharex=False, sharey=False, figsize=(8,4))
        ax1.imshow(err, interpolation="nearest")
        ax1.set_xlabel('Flattened image index')
        ax1.set_ylabel('Flattened image index')
        ax1.set_title('NRSME')

        '''
        import hyperspy.api as hs
        err_ims = np.reshape(err, (-1,) + ims_orig_shape[:2])
        hs.signals.Signal2D(err_ims).plot()
        '''
    # loop over all combinations
    print('Calculating combined NRSME for all combinations of %d images' %(avg_nims))
    combs_tot = int(np.math.factorial(n_ims)/(np.math.factorial(avg_nims)*np.math.factorial(n_ims-avg_nims)))
    comb_vals = np.empty(combs_tot, dtype=float)
    comb_inds = np.empty((combs_tot, avg_nims), dtype=int)
    for i, inds in enumerate(tqdm(combinations(range(n_ims), avg_nims), total=combs_tot)):
        # calculate rmse from values at intercepts of row and column slices
        ind_perms = np.array(list(combinations(inds, 2))).T
        intercept_vals = err[ind_perms[0], ind_perms[1]]
        comb_vals[i] = np.nansum(intercept_vals**2).sum()**0.5
        comb_inds[i] = inds

    # sort perms by rmse
    si = np.argsort(comb_vals)
    comb_vals = comb_vals[si]
    comb_inds = comb_inds[si]

    if plot:
        # Combined NRSME
        ax2.semilogx(comb_vals)
        ax2.set_xlabel('Combination index')
        ax2.set_ylabel('Combined NRSME')
        ax2.set_title('%d combinations of %d images' %(combs_tot, avg_nims))
        plt.tight_layout()

        # map of scan locations
        gri, gci = np.unravel_index(comb_inds, ims_orig_shape[:2])
        map_im = np.zeros(ims_orig_shape[:2])
        for i in range(cut_len):
            map_im[gri[i], gci[i]] += 1
        f, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(8,4))
        ax1.imshow(map_im)
        ax1.set_xlabel('Scan X index')
        ax1.set_ylabel('Scan Y index')
        ax1.set_title('First %d combinations of %d images' %(cut_len, avg_nims))

    # find most common scan index within cut
    common_im_ind = np.bincount(comb_inds[:cut_len].flat).argmax()
    print('Most common scan index in 1st %d combinations of %d images:' %(cut_len, avg_nims), np.unravel_index(common_im_ind, ims_orig_shape[:2]))
    contains_common_im = (comb_inds[:cut_len] == common_im_ind).sum(1) > 0

    # unique image indices within cut with most popular image in common
    common_im_inds = np.unique(comb_inds[:cut_len][contains_common_im].flatten())
    print('Number of unique images in these combinations sharing this index: %d' %(len(common_im_inds)))
    if plot:
        # plot unique points
        sel_im = np.zeros(ims_orig_shape[:2])
        sel_im.flat[common_im_inds] = 1
        ax2.imshow(sel_im)
        ax2.set_xlabel('Scan X index')
        #plt.ylabel('Scan Y index')
        plt.title('Unique images in 1st %d combinations of %d images\nsharing most common image' %(cut_len, avg_nims))

    # calculate means and stds
    if plot:
        f, axs = plt.subplots(3, 2, sharex=True, sharey=True, figsize=(5,8))
        ax1, ax2, ax3, ax4, ax5, ax6 = axs.flatten()
        
        im_common = ims[common_im_inds]
        im_common_mean = im_common.mean(0)
        im_common_std = im_common.std(0)
        ax1.imshow(im_common_mean)
        ax2.imshow(im_common_std)
        ax1.set_title('Most common %d best' %(len(common_im_inds)))
        
        im_best = ims[comb_inds[0]]
        im_best_mean = im_best.mean(0)
        im_best_std = im_best.std(0)
        ax3.imshow(im_best_mean)
        ax4.imshow(im_best_std)
        ax3.set_title('Best combination of %d' %(avg_nims))

        im_worst = ims[comb_inds[-1]]
        im_worst_mean = im_worst.mean(0)
        im_worst_std = im_worst.std(0)
        ax5.imshow(im_worst_mean)
        ax6.imshow(im_worst_std)
        ax5.set_title('Worst combination of %d' %(avg_nims))
    print('')

    # return data
    yxi_combos = np.unravel_index(comb_inds, ims_orig_shape[:2])
    yxi_common = np.unravel_index(common_im_inds, ims_orig_shape[:2])

    ims_common = ims_orig[common_im_inds]
    ims_common_mean = im_common.mean(0)
    ims_common_std = im_common.std(0)
    
    ims_best = ims_orig[comb_inds[0]]
    ims_best_mean = im_best.mean(0)
    ims_best_std = im_best.std(0)
    
    images.shape = ims_orig_shape
    
    rtn = namedtuple('matching', ['yxi_combos', 'yxi_common', 'ims_common', 'ims_best'])
    return rtn(yxi_combos, yxi_common, ims_common, ims_best)


def make_ref_im(image, edge_sigma, aperture=None, upscale=4, bin_opening=None, bin_closing=None, crop_pad=False, plot=True):
    '''
    Generate a cleaned version of the image supplied for use as a reference.
    
    Parameters
    ----------
    image : 2-D array
        Image to process.
    edge_sigma : float
        Edge width in pixels.
    aperture : None or 2-D array
        If not None, the data will be multiplied by the aperture mask.
    upscale : int
        Upscaling factor.
    bin_opening : None or int
        Circular element radius used for binary opening.
    bin_closing : None or int
        Circular element radius used for binary closing.
    crop_pad : bool
        If True and ``aperture`` is not None, the image is cropped before
        upscaling and padded in returned image for efficiency.
    plot : bool
        If True, the images are plotted.
    
    Notes
    -----
    The sequence of operation is:
        apply aperture
        upscale
        bin_opening
        bin_closing
        edge_sigma
        downscale
        scale magnitude
    
    Examples
    --------
    >>> from fpd.synthetic_data import disk_image
    >>> import fpd.fpd_processing as fpdp

    Generate synthetic image
    >>> image = disk_image(radius=32, intensity=64)
    
    Get centre and edge, and make aperture
    >>> cyx, cr = fpdp.find_circ_centre(image, sigma=6, rmms=(2, int(image.shape[0]/2.0), 1), plot=False)
    >>> edge_sigma = fpdp.disc_edge_sigma(image, sigma=2, cyx=cyx, r=cr, plot=False)[0]
    >>> aperture = fpdp.synthetic_aperture(image.shape[-2:], cyx=cyx, rio=(0, cr+16), sigma=0, aaf=1)[0]
    
    Make reference image
    >>> ref_im = fpdp.make_ref_im(image, edge_sigma, aperture)
    
    '''
    
    # float
    im = image.astype(float)
    im_shape = image.shape
    
    # mask
    if aperture is not None:
        im = im*aperture
        if crop_pad:
            #crop and pad for efficiency
            ci, cf = np.where((aperture>0.5).sum(0)>0)[0][[0, -1]]
            ri, rf = np.where((aperture>0.5).sum(0)>0)[0][[0, -1]]
            im = im[ri:rf+1, ci:cf+1]
        
    
    # upscale and threshold
    ref_imu = sp.ndimage.interpolation.zoom(im, zoom=4, output=None,
                                            order=3, mode='constant',
                                            cval=0.0, prefilter=True)
    thresh = threshold_otsu(ref_imu)
    processed = ref_imu >= thresh
    
    # binary opening / closing
    if bin_opening is not None:
        el = disk(bin_opening*upscale)
        processed = binary_opening(processed, el)
    if bin_closing is not None:
        el = disk(bin_closing*upscale)
        processed = binary_closing(processed, el)

    # smooth and downscale
    processed = sp.ndimage.filters.gaussian_filter(processed*1.0, edge_sigma*upscale)
    processed = sp.ndimage.interpolation.zoom(processed, zoom=1.0/upscale,
                                              output=None, order=3,
                                              mode='constant', cval=0.0,
                                              prefilter=True)

    # scale mag
    mag_scale = np.percentile(im[processed>0.5], 50)
    processed = processed*mag_scale
    
    if aperture is not None and crop_pad:
        im_pad = np.zeros_like(image, dtype=float)
        im_pad[ri:rf+1, ci:cf+1] = im
        im = im_pad
        
        im_pad = np.zeros_like(image, dtype=float)
        im_pad[ri:rf+1, ci:cf+1] = processed
        processed = im_pad

    # plot
    if plot:
        err = processed-im
        pct = 0.1
        vmin_max = np.percentile(err, [pct, 100-pct])
        vmin, vmax = np.abs(vmin_max).max() * np.array([-1, 1])
        
        f, (ax1, ax2, ax3) = plt.subplots(1, 3, sharex=True, sharey=True, figsize=(9,3))
        ax1.imshow(im)
        ax2.imshow(processed)
        ax3.imshow(err, vmin=vmin, vmax=vmax, cmap='bwr')
        ax1.set_title('Original')
        ax2.set_title('Processed')
        ax3.set_title('Processed : Original\n%0.3f - %0.3f' %(vmin_max[0], vmin_max[1]))
    
    return processed


