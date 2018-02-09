'''
Utilities for signal processing 
'''

'''
Author: Thomas Haslwanter
Version: 1.2
Date: Nov-2013
'''

import numpy as np
import matplotlib.pyplot as plt

import math 
from numpy import dot

def pSpect(data, rate):
    '''
    Power spectrum and frequency

    Parameters
    ----------
    data : array, shape (N,)
        measurement data
    rate : float
        sampling rate [Hz]

    Returns
    -------
    powerspectrum : array, shape (N,)
    frequency : array, shape (N,)

    Example
    -------
    >>> pxx, freq = pSpect(data, 1000)

    '''

    from scipy.fftpack import fft
    nData = len(data)
    window = np.hamming(nData)
    fftData = fft(data*window)
    PowerSpect = fftData * fftData.conj() / nData
    freq = np.arange(nData) * float(rate) / nData
    return (PowerSpect, freq)

def show_se(raw):
    '''Show mean and standard error, of a dataset in column form.

    Parameters
    ----------
    raw : array (N,M)
        input data, M sets of N data points

    Returns
    -------
    avg : array (N,)
        average value
    se : array (N,)
        standard error

    Examples
    --------
    >>> t = np.arange(0,20,0.1)
    >>> x = np.sin(t)
    >>> data = []
    >>> for ii in range(10):
    >>>     data.append(x + np.random.randn(len(t)))
    >>> show_se(np.array(data).T)

    Notes
    -----
    .. image:: _static/show_se.png
        :scale: 50%

    '''

    N = len(raw)

    # Calculate mean and standard error
    avg = np.mean(raw, axis=1)
    std = np.std(raw, axis=1, ddof=1)
    se = std/np.sqrt(N)

    # Calculate upper and lower limit, for showing the standard error
    upper = avg + se
    lower = avg - se

    # Plot the data
    plt.fill_between(t, lower, upper, color='gray', alpha=0.5)
    plt.hold(True)
    plt.plot(t,avg)
    plt.show()

    return (avg, se)


def corrvis(x,y):
    '''
    Visualize correlation, by calculating the cross-correlation of two signals.
    The aligned signals and the resulting cross correlation value are shown,
    and advanced when the user hits a key or clicks with the mouse.

    Parameters
    ----------
    X : array (N,)
        Comparison signal

    Y : array (M,)
        Reference signal

    Examples
    --------
    >>> x = np.r_[0:2*pi:10j]
    >>> y = np.sin(x)
    >>> corrvis(y,y)

    Notes
    -----
    Based on an idea from dpwe@ee.columbia.edu

    '''

    Nx = x.size
    Ny = y.size
    Nr = Nx + Ny -1
    
    xmin = -(Nx - 1)
    xmax = Ny + Nx -1
    
    # First plot: Signal 1
    ax1 = plt.subplot(311)
    ax1.plot(range(Ny), y)
    ax = ax1.axis()
    ax1.axis([xmin, xmax, ax[2], ax[3]])
    ax1.grid(True)
    ax1.set_xticklabels(())
    ax1.set_ylabel('Y[n]')
    
    # Precalculate limits of correlation output
    axr = [xmin, xmax, np.correlate(x,y,'full').min(), np.correlate(x,y,'full').max()]
    
    # Make a version of y padded to the full extent of X's we'll shift
    padY = np.r_[np.zeros(Nx-1), y, np.zeros(Nx-1)]
    Npad = padY.size
    R = []

    # Generate the cross-correlation, step-by-step
    for p in range(Nr):
        
        # Figure aligned X
        ax2 = plt.subplot(312)
        ax2.hold(False)
        ax2.plot(np.arange(Nx)-Nx+p+1, x)
        ax = ax2.axis()
        ax2.axis([xmin, xmax, ax[2], ax[3]])
        ax2.grid(True)
        ax2.set_ylabel('X[n-l]')
        ax2.set_xticklabels(())
        
        # Calculate correlation
        # Pad an X to the appropriate place
        padX = np.r_[np.zeros(p), x, np.zeros(Npad-Nx-p)]
        R = np.r_[R, np.sum(padX * padY)]
        
        # Third plot: cross-correlation values
        ax3 = plt.subplot(313)
        ax3.hold(False)
        ax3.plot(np.arange(len(R))-(Nx-1), R, linewidth=2)
        ax3.axis(axr)
        ax3.grid(True)
        ax3.set_ylabel('Rxy[l]')
        
        # Update the plot
        plt.draw()
        plt.waitforbuttonpress()
        
    plt.show()

if __name__ == '__main__':
    t = np.arange(0,10,0.1)
    x = np.sin(t) + 0.2*np.random.randn(len(t))
    smoothed = savgol(x, 11)
    plt.plot(t, smoothed)
    plt.show()
    print('Done')
