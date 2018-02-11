"""
Collection of functions to perform spectral analysis on 1-D signals
Copyright (C) 2017 - Pietro Mascolo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Pietro Mascolo
Email: iz4vve@gmail.com
"""
import numpy as np
from scipy.fftpack import fft, ifft
from statsmodels.tsa.stattools import acf


def band_pass(signal, low, high):
    """
    Band pass filter working in the frequency domain

    :param signal: timeseries
    :param low: lower bound of the frequency band to keep
    :param high: higher bound of the frequency band to keep
    :return: filtered signal
    :rtype: numpy.array
    """
    return np.array(
        i.real for i in ifft([i for i in fft(signal) if low < i < high])
    )


def remove_band(signal, low, high):
    """
    Band filter working in the frequency domain. The frequency band specified
    is removed from the signal's spectrum

    :param signal: timeseries
    :param low: lower bound of the frequency band to eliminate
    :param high: higher bound of the frequency band to eliminate
    :return: filtered signal
    :rtype: numpy.array
    """
    return np.array(
        i.real for i in ifft([i for i in fft(signal) if not low < i < high])
    )


def cut_frequencies(signal, threshold, keep_high=False):
    """
    Cuts frequencies of the spectrum of a signal at a threshold

    :param signal: timeseries
    :param threshold: threshold to cut signal's spectrum
    :param keep_high: if true only frequencies > threshold will be kept,
                      otherwise low frequencies will be kept
    :return: filtered signal
    :rtype: numpy.array
    """
    if keep_high:
        return np.array(
            i.real for i in ifft([i for i in fft(signal) if i < threshold])
        )
    return np.array(
        i.real for i in ifft([i for i in fft(signal) if i > threshold])
    )


def autocorr(signal, **kwargs):
    """
    Calculates autocorrelation coefficients for a signal

    :param signal: timeseries
    :param kwargs: keyword arguments of statsmodels.tsa.statstool.acf
    :return: autocorrelation coefficients
    :rtype: numpy.array
    """
    return acf(signal, **kwargs)
