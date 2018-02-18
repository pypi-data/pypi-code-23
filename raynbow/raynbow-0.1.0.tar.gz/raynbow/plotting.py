"""Plotting functions."""
from functools import lru_cache

import numpy as np
from numpy import atan2, pi, cos, sin
from scipy.spatial import Delaunay

from matplotlib.collections import LineCollection

from raynbow.utilities import share_fig_ax, smooth
from raynbow.colorspaces import (
    XYZ_to_xy,
    wavelength_to_XYZ,
    xy_to_XYZ,
    XYZ_to_sRGB,
    XYZ_to_uvprime,
    uvprime_to_xy,
    multi_cct_duv_to_uvprime,
)
from raynbow.data import (
    prepare_robertson_interpfs
)


def __wavelength_to_rgb(wavelength, gamma=0.8):
    """Not intended for use by users, See noah.org: http://www.noah.org/wiki/Wavelength_to_RGB_in_Python .

    Parameters
    ----------
    wavelength : `float` or `int`
        wavelength of light
    gamma : `float`, optional
        output gamma

    Returns
    -------
    `tuple`
        R, G, B values

    """
    wavelength = float(wavelength)
    if wavelength >= 380 and wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif wavelength >= 440 and wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif wavelength >= 490 and wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif wavelength >= 510 and wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif wavelength >= 580 and wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif wavelength >= 645 and wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0

    return (R, G, B)


@lru_cache()
def render_plot_spectrum_background(xmin=380, xmax=730, numpts=100):
    """Render the background for a spectrum plot.

    Parameters
    ----------
    xmin : `int`, optional
        minimum wavelength to render
    xmax : `int`, optional
        maximum wavelength to render
    numpts : `int`, optional
        number of wavelengths to render

    Returns
    -------
    `numpy.ndarray`
        2 x numpts x 3 array of RGB values

    """
    wvl = np.linspace(xmin, xmax, numpts)
    out = [__wavelength_to_rgb(wavelength) for wavelength in wvl]
    return np.tile(np.asarray(out), (2, 1, 1))


def plot_spectrum(spectrum_dict, xrange=(380, 730), yrange=(0, 100), smoothing=None, fig=None, ax=None):
    """Plot a spectrum.

    Parameters
    ----------
    spectrum_dict : `dict`
        with keys wvl, values
    xrange : `iterable`
        pair of lower and upper x bounds
    yrange : `iterable`
        pair of lower and upper y bounds
    smoothing : `float`
        number of nanometers to smooth data by.  If None, do no smoothing
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    Returns
    -------
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    """
    wvl, values = spectrum_dict['wvl'], spectrum_dict['values']
    if smoothing is not None:
        dx = wvl[1] - wvl[0]
        window_width = int(smoothing / dx)
        values = smooth(values, window_width, window='flat')

    bg = render_plot_spectrum_background(xrange[0], xrange[1])
    fig, ax = share_fig_ax(fig, ax)
    ax.imshow(bg, extent=[*xrange, *yrange], interpolation='lanczos', aspect='auto')
    ax.plot(wvl, values, lw=3)
    ax.fill_between(wvl, values, yrange[1] * len(values), facecolor='w', alpha=0.5)
    ax.set(xlim=xrange, xlabel=r'Wavelength $\lambda$ [nm]',
           ylim=yrange, ylabel='Transmission [%]')

    return fig, ax


@lru_cache()
def render_cie_1931_background(xlow, xhigh, ylow, yhigh, samples):
    """Prepare the background for a CIE 1931 plot.

    Parameters
    ----------
    xlow : `int` or `float`
        left bound of the image
    xhigh : `int` or `float`
        right bound of the image
    ylow : `int` or `float`
        lower bound of the image
    yhigh : `int` or `float`
        upper bound of the image
    samples : `int`
        number of 1D samples within the region of interest, total pixels will be samples^2

    Returns
    -------
    `numpy.ndarray`
        3D array of sRGB values in the range [0,1] with shape [:,:,[R,G,B]]

    """
    wvl_mask = [400, 430, 460, 465, 470, 475, 480, 485, 490, 495,
                500, 505, 510, 515, 520, 525, 530, 540, 555, 570, 700]

    wvl_mask_xy = XYZ_to_xy(wavelength_to_XYZ(wvl_mask))

    # make equally spaced u,v coordinates on a grid
    x = np.linspace(xlow, xhigh, samples)
    y = np.linspace(ylow, yhigh, samples)
    xx, yy = np.meshgrid(x, y)

    # stack u and v for vectorized computations, also mask out negative values
    xxyy = np.stack((xx, yy), axis=2)

    # make a mask, of value 1 outside the horseshoe, 0 inside
    triangles = Delaunay(wvl_mask_xy, qhull_options='QJ Qf')
    wvl_mask = triangles.find_simplex(xxyy) < 0

    xyz = xy_to_XYZ(xxyy)
    data = XYZ_to_sRGB(xyz)

    # normalize and clip sRGB values.
    maximum = np.max(data, axis=-1)
    maximum[maximum == 0] = 1
    data = np.clip(data / maximum[:, :, np.newaxis], 0, 1)

    # now make an alpha/transparency mask to hide the background
    alpha = np.ones((samples, samples))
    alpha[wvl_mask] = 0
    data = np.dstack((data, alpha))
    return data


def cie_1931_plot(xlim=(0, 0.9), ylim=None, samples=300, fig=None, ax=None):
    """Create a CIE 1931 plot.

    Parameters
    ----------
    xlim : `iterable`
        left and right bounds of the plot
    ylim : `iterable`
        lower and upper bounds of the plot.  If `None`, the y bounds will be chosen to match the x bounds
    samples : `int`
        number of 1D samples within the region of interest, total pixels will be samples^2
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    Returns
    -------
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    """
    # duplicate xlim if ylim not set
    if ylim is None:
        ylim = xlim

    # don't compute over dead space
    xlim_bg = list(xlim)
    ylim_bg = list(ylim)
    if xlim[0] < 0:
        xlim_bg[0] = 0
    if xlim[1] > 0.75:
        xlim_bg[1] = 0.75
    if ylim[0] < 0:
        ylim_bg[0] = 0
    if ylim[1] > 0.85:
        ylim_bg[1] = 0.85

    # create lists of wavelengths and map them to uv,
    # a reduced set for a faster mask and
    # yet another set for annotation.
    wvl_line = np.arange(400, 700, 2.5)
    wvl_line_xy = XYZ_to_xy(wavelength_to_XYZ(wvl_line))

    wvl_annotate = [360, 400, 455, 470, 480, 490,
                    500, 510, 520, 540, 555, 570, 580, 590,
                    600, 615, 630, 700, 830]

    data = render_cie_1931_background(*xlim_bg, *ylim_bg, samples)

    # duplicate the lowest wavelength so that the boundary line is closed
    wvl_line_xy = np.vstack((wvl_line_xy, wvl_line_xy[0, :]))

    fig, ax = share_fig_ax(fig, ax)
    ax.imshow(data,
              extent=[*xlim_bg, *ylim_bg],
              interpolation='bilinear',
              origin='lower')
    ax.plot(wvl_line_xy[:, 0], wvl_line_xy[:, 1], ls='-', c='0.25', lw=2)
    fig, ax = cie_1931_wavelength_annotations(wvl_annotate, fig=fig, ax=ax)
    ax.set(xlim=xlim, xlabel='CIE x',
           ylim=ylim, ylabel='CIE y')

    return fig, ax


@lru_cache()
def render_cie_1976_background(xlow, xhigh, ylow, yhigh, samples):
    """Prepare the background for a CIE 1976 plot.

    Parameters
    ----------
    xlow : `int` or `float`
        left bound of the image
    xhigh : `int` or `float`
        right bound of the image
    ylow : `int` or `float`
        lower bound of the image
    yhigh : `int` or `float`
        upper bound of the image
    samples : `int`
        number of 1D samples within the region of interest, total pixels will be samples^2

    Returns
    -------
    `numpy.ndarray`
        3D array of sRGB values in the range [0,1] with shape [:,:,[R,G,B]]

    """
    wvl_mask = [400, 430, 460, 465, 470, 475, 480, 485, 490, 495,
                500, 505, 510, 515, 520, 525, 530, 535, 570, 700]

    wvl_mask_uv = XYZ_to_uvprime(wavelength_to_XYZ(wvl_mask))

    # make equally spaced u,v coordinates on a grid
    u = np.linspace(xlow, xhigh, samples)
    v = np.linspace(ylow, yhigh, samples)
    uu, vv = np.meshgrid(u, v)

    # stack u and v for vectorized computations, also mask out negative values
    uuvv = np.stack((uu, vv), axis=2)

    # make a mask, of value 1 outside the horseshoe, 0 inside
    triangles = Delaunay(wvl_mask_uv, qhull_options='QJ Qf')
    wvl_mask = triangles.find_simplex(uuvv) < 0

    xy = uvprime_to_xy(uuvv)
    xyz = xy_to_XYZ(xy)
    data = XYZ_to_sRGB(xyz)

    # normalize and clip sRGB values.
    maximum = np.max(data, axis=-1)
    maximum[maximum == 0] = 1
    data = np.clip(data / maximum[:, :, np.newaxis], 0, 1)

    # now make an alpha/transparency mask to hide the background
    alpha = np.ones((samples, samples))
    alpha[wvl_mask] = 0
    data = np.dstack((data, alpha))
    return data


def cie_1976_plot(xlim=(-0.09, 0.68), ylim=None, samples=400,
                  annotate_wvl=True, draw_plankian_locust=False,
                  fig=None, ax=None):
    """Create a CIE 1976 plot.

    Parameters
    ----------
    xlim : `iterable`
        left and right bounds of the plot
    ylim : `iterable`
        lower and upper bounds of the plot.  If `None`, the y bounds will be chosen to match the x bounds
    samples : `int`
        number of 1D samples within the region of interest, total pixels will be samples^2
    annotate_wvl : `bool`
        whether to plot wavelength annotations
    draw_plankian_locust : `bool`
        whether to draw the plankian locust
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    Returns
    -------
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    """
    # duplicate xlim if ylim not set
    if ylim is None:
        ylim = xlim

    # don't compute over dead space
    xlim_bg = list(xlim)
    ylim_bg = list(ylim)
    if xlim[0] < 0:
        xlim_bg[0] = 0
    if xlim[1] > 0.65:
        xlim_bg[1] = 0.65
    if ylim[0] < 0:
        ylim_bg[0] = 0
    if ylim[1] > 0.6:
        ylim_bg[1] = 0.6

    # create lists of wavelengths and map them to uv for the border line and annotation.
    wvl_line = np.arange(400, 700, 2)
    wvl_line_uv = XYZ_to_uvprime(wavelength_to_XYZ(wvl_line))
    # duplicate the lowest wavelength so that the boundary line is closed
    wvl_line_uv = np.vstack((wvl_line_uv, wvl_line_uv[0, :]))

    background = render_cie_1976_background(*xlim_bg, *ylim_bg, samples)

    fig, ax = share_fig_ax(fig, ax)
    ax.imshow(background,
              extent=[*xlim_bg, *ylim_bg],
              interpolation='bilinear',
              origin='lower')
    ax.plot(wvl_line_uv[:, 0], wvl_line_uv[:, 1], ls='-', c='0.25', lw=2.5)
    if annotate_wvl:
        wvl_annotate = [360, 400, 455, 470, 480, 490,
                        500, 510, 520, 540, 555, 570, 580, 590,
                        600, 610, 625, 700, 830]
        fig, ax = cie_1976_wavelength_annotations(wvl_annotate, fig=fig, ax=ax)
    if draw_plankian_locust:
        fig, ax = cie_1976_plankian_locust(fig=fig, ax=ax)
    ax.set(xlim=xlim, xlabel='CIE u\'',
           ylim=ylim, ylabel='CIE v\'')

    return fig, ax


def cie_1931_wavelength_annotations(wavelengths, fig=None, ax=None):
    """Draw lines normal to the spectral locust on a CIE 1931 diagram and writes the text for each wavelength.

    Parameters
    ----------
    wavelengths : `iterable`
        set of wavelengths to annotate
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    Returns
    -------
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    Notes
    -----
    see SE:
    https://stackoverflow.com/questions/26768934/annotation-along-a-curve-in-matplotlib

    """
    # some tick parameters
    tick_length = 0.025
    text_offset = 0.06

    # convert wavelength to u' v' coordinates
    wavelengths = np.asarray(wavelengths)
    idx = np.arange(1, len(wavelengths) - 1, dtype=int)
    wvl_lbl = wavelengths[idx]
    xy = XYZ_to_xy(wavelength_to_XYZ(wavelengths))
    x, y = xy[..., 0][idx], xy[..., 1][idx]
    x_last, y_last = xy[..., 0][idx - 1], xy[..., 1][idx - 1]
    x_next, y_next = xy[..., 0][idx + 1], xy[..., 1][idx + 1]

    angle = atan2(y_next - y_last, x_next - x_last) + pi / 2
    cos_ang, sin_ang = cos(angle), sin(angle)
    x1, y1 = x + tick_length * cos_ang, y + tick_length * sin_ang
    x2, y2 = x + text_offset * cos_ang, y + text_offset * sin_ang

    fig, ax = share_fig_ax(fig, ax)
    tick_lines = LineCollection(np.c_[x, y, x1, y1].reshape(-1, 2, 2), color='0.25', lw=1.25)
    ax.add_collection(tick_lines)
    for i in range(len(idx)):
        ax.text(x2[i], y2[i], str(wvl_lbl[i]), va="center", ha="center", clip_on=True)

    return fig, ax


def cie_1976_wavelength_annotations(wavelengths, fig=None, ax=None):
    """Draw lines normal to the spectral locust on a CIE 1976 diagram and writes the text for each wavelength.

    Parameters
    ----------
    wavelengths : `iterable`
        set of wavelengths to annotate
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    Returns
    -------
    fig : `matplotlib.figure.Figure`
    Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    Notes
    -----
    see SE:
    https://stackoverflow.com/questions/26768934/annotation-along-a-curve-in-matplotlib

    """
    # some tick parameters
    tick_length = 0.025
    text_offset = 0.06

    # convert wavelength to u' v' coordinates
    wavelengths = np.asarray(wavelengths)
    idx = np.arange(1, len(wavelengths) - 1, dtype=int)
    wvl_lbl = wavelengths[idx]
    uv = XYZ_to_uvprime(wavelength_to_XYZ(wavelengths))
    u, v = uv[..., 0][idx], uv[..., 1][idx]
    u_last, v_last = uv[..., 0][idx - 1], uv[..., 1][idx - 1]
    u_next, v_next = uv[..., 0][idx + 1], uv[..., 1][idx + 1]

    angle = atan2(v_next - v_last, u_next - u_last) + pi / 2
    cos_ang, sin_ang = cos(angle), sin(angle)
    u1, v1 = u + tick_length * cos_ang, v + tick_length * sin_ang
    u2, v2 = u + text_offset * cos_ang, v + text_offset * sin_ang

    fig, ax = share_fig_ax(fig, ax)
    tick_lines = LineCollection(np.c_[u, v, u1, v1].reshape(-1, 2, 2), color='0.25', lw=1.25)
    ax.add_collection(tick_lines)
    for i in range(len(idx)):
        ax.text(u2[i], v2[i], str(wvl_lbl[i]), va="center", ha="center", clip_on=True)

    return fig, ax


def cie_1976_plankian_locust(trange=(2000, 10000), num_points=100,
                             isotemperature_lines_at=None, isotemperature_du=0.025,
                             fig=None, ax=None):
    """Draw the plankian locust on the CIE 1976 color diagram.

    Parameters
    ----------
    trange : `iterable`
        (min,max) color temperatures
    num_points : `int`
        number of points to compute
    isotemperature_lines_at : `iterable`
        CCTs to plot isotemperature lines at, defaults to [2000, 3000, 4000, 5000, 6500, 10000] if None.
        set to False to not plot lines
    isotemperature_du : `float`
        delta-u, parameter, length in x of the isotemperature lines
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    Returns
    -------
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    """
    # compute the u', v' coordinates of the temperatures
    temps = np.linspace(trange[0], trange[1], num_points)
    interpf_u, interpf_v = prepare_robertson_interpfs(values=('u', 'v'), vs='K')
    u = interpf_u(temps)
    v = interpf_v(temps) * 1.5  # x1.5 converts 1960 uv to 1976 u' v'

    # if plotting isotemperature lines, compute the upper and lower points of
    # each line and connect them.
    plot_isotemp = True
    if isotemperature_lines_at is None:
        isotemperature_lines_at = np.asarray([2000, 3000, 4000, 5000, 6500, 10000])
        u_iso = interpf_u(isotemperature_lines_at)
        v_iso = interpf_v(isotemperature_lines_at)
        interpf_dvdu = prepare_robertson_interpfs(values='dvdu', vs='u')

        dvdu = interpf_dvdu(u_iso)
        du = isotemperature_du / dvdu

        u_high = u_iso + du / 2
        u_low = u_iso - du / 2
        v_high = (v_iso + du / 2 * dvdu) * 1.5  # factors of 1.5 convert from uv to u'v'
        v_low = (v_iso - du / 2 * dvdu) * 1.5
    elif isotemperature_lines_at is False:
        plot_isotemp = False

    fig, ax = share_fig_ax(fig, ax)
    ax.plot(u, v, c='0.15')
    if plot_isotemp is True:
        for ul, uh, vl, vh in zip(u_low, u_high, v_low, v_high):
            ax.plot([ul, uh], [vl, vh], c='0.15')

    return fig, ax


def cct_duv_diagram(samples=100, fig=None, ax=None):
    """Create a CCT-Duv diagram.

    For more information see Calculation of CCT and Duv and Practical Conversion Formulae, Yoshi Ohno, 2011.

    Parameters
    ----------
    samples : `int`
        number of samples on the background, total #pix will be samples^2
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    Returns
    -------
    fig : `matplotlib.figure.Figure`
        Figure to draw plot in
    ax : `matplotlib.axes.Axis`
        Axis to draw plot in

    """
    xlim = (2000, 10000)
    ylim = (-0.03, 0.03)

    cct = np.linspace(xlim[0], xlim[1], samples)  # todo: even sampling along log, not linear
    duv = np.linspace(ylim[0], ylim[1], samples)

    upvp = multi_cct_duv_to_uvprime(cct, duv)
    cct, duv = np.meshgrid(cct, duv)

    xy = uvprime_to_xy(upvp)
    xyz = xy_to_XYZ(xy)
    dat = XYZ_to_sRGB(xyz)

    maximum = np.max(dat, axis=-1)
    dat /= maximum[..., np.newaxis]
    dat = np.clip(dat, 0, 1)

    fig, ax = share_fig_ax(fig, ax)

    ax.imshow(dat,
              extent=[*xlim, *ylim],
              interpolation='bilinear',
              origin='lower',
              aspect='auto')

    ax.set(xlim=xlim, xlabel='CCT [K]',
           ylim=ylim, ylabel='Duv [a.u.]')

    return fig, ax
