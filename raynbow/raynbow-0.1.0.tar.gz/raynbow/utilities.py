"""Utility functions."""
from matplotlib import pyplot as plt
import numpy as np


def share_fig_ax(fig=None, ax=None, numax=1, sharex=False, sharey=False):
    """Reurns the given figure and/or axis if given one.  If they are None, creates a new fig/ax.

    Parameters
    ----------
    fig : `matplotlib.figure.Figure`
        figure
    ax : `matplotlib.axes.Axis`
        axis or array of axes
    numax : `int`
        number of axes in the desired figure, 1 for most plots, 3 for plot_fourier_chain
    sharex : `bool`, optional
        whether to share the x axis
    sharey : `bool`, optional
        whether to share the y axis

    Returns
    -------
    `matplotlib.figure.Figure`
        A figure object
    `matplotlib.axes.Axis`
        An axis object

    """
    if fig is None and ax is None:
        fig, ax = plt.subplots(nrows=1, ncols=numax, sharex=sharex, sharey=sharey)
    elif ax is None:
        ax = fig.gca()

    return fig, ax


def smooth(x, window_len=3, window='flat'):
    """Smooth data.

    Parameters
    ----------
    x : `iterable`
        the input signal
    window_len
        the dimension of the smoothing window; should be an odd integer
    window : {'flat', 'hanning', 'hamming', 'bartlett', 'blackman'}
        the type of window to use

    Returns
    -------
    `numpy.ndarray`
        smoothed data

    Notes
    -----
    length(output) != length(input), to correct this: return
    y[(window_len/2-1):-(window_len/2)] instead of just y.

    adapted from scipy signal smoothing cookbook,
    http://scipy-cookbook.readthedocs.io/items/SignalSmooth.html

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    Raises
    ------
    ValueError
        invalid window provided

    """
    x = np.asarray(x)
    if window_len == 1:  # short circuit and return original array if window length is unity
        return x

    if x.ndim != 1:
        raise ValueError('Data must be 1D.')

    if x.size < window_len:
        raise ValueError('Data must be larger than window.')

    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError('Window must be one of flat, hanning, hamming, bartlett, blackman')

    s = np.r_[x[window_len - 1:0: - 1], x, x[-2:-window_len - 1:-1]]
    if window.lower() == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')
    return y[(int(np.floor(window_len / 2)) - 1):-(int(np.ceil(window_len / 2)))]
