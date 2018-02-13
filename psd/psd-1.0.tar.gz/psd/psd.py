#!/usr/bin/env python3
"""
Import, compute and plot Power Spectral Densities

Use this tool to quickly compute, or plot PSDs from data contained
in one or multiple files, using parametrized Welch method.

Jean-Baptiste Bayle, APC/CNRS/CNES, 20/03/2017.
"""

import argparse
import numpy as np
import scipy.signal as sg
import matplotlib.pyplot as plt


def parse_arguments():
    """Create parser and return parsed arguments."""
    parser = argparse.ArgumentParser(
        description='Plot Power Spectral Densities from data files.',
        epilog='Jean-Baptiste Bayle, 20/03/2017.')
    parser.add_argument(
        'filenames',
        type=str, nargs='+',
        help='text or Nympy files containing data')
    parser.add_argument(
        '-c', '--columns',
        type=int, nargs='*',
        help='indices of columns to be computed (default all)')
    parser.add_argument(
        '-s', '--skiprows',
        type=int, default=0,
        help='skip the first rows (default to 0)')
    parser.add_argument(
        '-n', '--nperseg',
        type=int, default=None,
        help='number of points per segment (default length of data)')
    parser.add_argument(
        '--overlap',
        type=float, default=0.5,
        help='overlap ratio between segments (default 0.5)')
    parser.add_argument(
        '--window',
        type=str, default='nuttall4',
        help='windowing function (default to Nuttall4 window)')
    parser.add_argument(
        '--no-legend',
        dest='legend', action='store_false',
        help='hide legend (default show)')
    parser.add_argument(
        '--time-series',
        action='store_true',
        help='plot time series instead of psd')
    parser.add_argument(
        '--title',
        type=str,
        help='plot title'
    )
    parser.add_argument(
        '-o', '--output',
        type=str, default=None,
        help='output file for PSD data or image file (default show)')
    return parser.parse_args()


class Series(object):
    """Define a series of data and computed PSD."""

    def __init__(self, times, data, title):
        super().__init__()
        self.times = times
        self.data = data
        self.title = title
        self.frequencies = None
        self.psd = None

    @property
    def sampling_freq(self):
        """Return sampling frequency from first points."""
        return 1.0 / (self.times[1] - self.times[0])

    @staticmethod
    def from_file(filename, columns=None, skiprows=0):
        """Load series from a file."""
        print('Loading data from ' + filename + '...')
        if skiprows > 0:
            print('Skipping', skiprows, 'rows of data...')
        if filename.endswith('.npy'):
            file_data = np.load(filename)
            file_data = file_data[skiprows:]
        else:
            file_data = np.loadtxt(filename, skiprows=skiprows)
        column_count = file_data.shape[1]
        titles = Series.extract_titles(filename, column_count)
        columns = columns if columns is not None else range(1, column_count)
        return [Series(file_data[:, 0], file_data[:, col], titles[col]) for col in columns]

    @staticmethod
    def from_files(filenames, columns=None, skiprows=0):
        """Load series from multiple files."""
        series = []
        for filename in filenames:
            series += Series.from_file(filename, columns, skiprows)
        return series

    @staticmethod
    def extract_titles(filename, column_count, commentchar='#'):
        """Extract column titles from file."""
        titles = None
        if not filename.endswith('.npy'):
            with open(filename) as data_file:
                first = data_file.readline().strip()
                if first.startswith(commentchar):
                    titles = first.replace(commentchar, '').split()
        if titles is None:
            titles = [filename + '-' + str(col) for col in range(column_count)]
        return titles

    def compute(self, nperseg=None, overlap=0.5, window='nuttall4'):
        """Compute series PSD and return a PSD series."""
        if nperseg is None:
            nperseg = len(self.data)
        freq = self.sampling_freq
        print('Computing PSD for', self.title,
              '(using', nperseg, 'points at', "%.1f" % freq, 'Hz)...')
        estimator = SpectralEstimator(freq, window, nperseg, overlap)
        self.frequencies, self.psd = estimator.compute(self.data)
        return self

    def filter_nan(self):
        """Filter out NaN values from series."""
        nans = np.isnan(self.data)
        self.times = self.times[~nans]
        self.data = self.data[~nans]
        self.frequencies = None
        self.psd = None
        return self

    def skiprows(self, rowcount):
        """Remove first rows of data."""
        self.times = self.times[rowcount:]
        self.data = self.data[rowcount:]
        self.frequencies = None
        self.psd = None
        return self

    def time_series(self, legend=True, title=None):
        """Plot series data vs. time in linear scale."""
        plt.plot(self.times, self.data, 'o-', label=self.title)
        plt.xlabel('Time [s]')
        plt.grid('on')
        plt.ylabel('Signals')
        if legend:
            plt.legend()
        if title is not None:
            plt.title(title)
        return self

    def plot(self, legend=True, title=None):
        """Plot PSD vs. frequencies in a log-log scale."""
        plt.loglog(self.frequencies, self.psd, label=self.title)
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('PSD [/Hz]')
        plt.grid('on')
        if legend:
            plt.legend()
        if title is not None:
            plt.title(title)
        return self

    def save(self, filename):
        """Save PSD to Numpy binary file."""
        np.save(filename, [self.frequencies, self.psd])
        return self

    @staticmethod
    def save_many(series, filename):
        """Save multiple series to Numpy binary file."""
        data = [(serie.frequencies, serie.psd) for serie in series]
        np.save(filename, data)

    @staticmethod
    def savetxt_many(series, filename):
        """Save multiple series to text file."""
        psds = []
        header = []
        for serie in series:
            psds.append(serie.frequencies)
            header.append(serie.title + '-freq')
            psds.append(serie.psd)
            header.append(serie.title)
        psds = np.stack(psds, axis=1)
        np.savetxt(filename, psds, header=' '.join(header))


class SpectralEstimator(object):
    """Helper methods for spectral estimation."""
    def __init__(self, fsampling, window, nperseg, overlap):
        self.fsampling = fsampling
        self.window = SpectralEstimator.get_window(window, nperseg)
        self.nperseg = nperseg
        self.noverlap = int(nperseg * overlap)

    @staticmethod
    def get_window(window, nperseg):
        """Return window of type `window` for a length of `nperseg`."""
        func = None
        if window == 'nuttall3':
            coeffs = [0.375, -0.5, 0.125]
            func = lambda x: SpectralEstimator.nuttall(x, coeffs)
        elif window == 'nuttal3a':
            coeffs = [0.40897, -0.5, 0.09103]
            func = lambda x: SpectralEstimator.nuttall(x, coeffs)
        elif window == 'nuttall3b':
            coeffs = [0.4243801, -0.4973406, 0.0782793]
            func = lambda x: SpectralEstimator.nuttall(x, coeffs)
        elif window == 'nuttall4':
            coeffs = [0.3125, -0.46875, 0.1875, -0.03125]
            func = lambda x: SpectralEstimator.nuttall(x, coeffs)
        elif window == 'nuttall4a':
            coeffs = [0.338946, -0.481973, 0.161054, -0.018027]
            func = lambda x: SpectralEstimator.nuttall(x, coeffs)
        elif window == 'nuttall4b':
            coeffs = [0.355768, -0.487396, 0.144232, -0.012604]
            func = lambda x: SpectralEstimator.nuttall(x, coeffs)
        elif window == 'nuttall4c':
            coeffs = [0.3635819, -0.4891775, 0.1365995, -0.0106411]
            func = lambda x: SpectralEstimator.nuttall(x, coeffs)
        if func is not None:
            bins = np.arange(0.0, 1.0, 1.0 / nperseg)
            return [func(i) for i in bins]
        return sg.get_window(window, nperseg)

    @staticmethod
    def nuttall(point, coeffs):
        """Apply nuttall window at `point` for given coefficients."""
        coeffs = np.array(coeffs)
        args = 2 * np.pi * point * np.arange(0, len(coeffs))
        terms = coeffs * np.cos(args)
        return np.sum(terms)

    def compute(self, data):
        """Return frequencies and psd estimation for data."""
        return sg.welch(data, self.fsampling, self.window, self.nperseg, self.noverlap)


def main():
    """Load data file and parse arguments before computing and plotting PSD."""
    # Load all data series from files
    args = parse_arguments()
    series = Series.from_files(args.filenames, args.columns, args.skiprows)
    for serie in series:
        serie.filter_nan()

    # Compute psd if needed
    show = args.output is None
    savetxt = not show and args.output.endswith('.txt')
    savefig = not show and args.output.endswith(('.png', '.pdf', '.ps', '.eps', '.svg'))
    savenpy = not show and not savefig and not savetxt
    if not args.time_series or savetxt:
        for serie in series:
            serie.compute(args.nperseg, args.overlap, args.window)

    # Save to file if needed
    if savetxt or savenpy:
        print('Saving results to ' + args.output + '...')
        if savetxt:
            Series.savetxt_many(series, args.output)
        else:
            Series.save_many(series, args.output)
        return

    # Plot time series or psd
    print("Plotting results...")
    if args.time_series:
        for serie in series:
            serie.time_series(legend=args.legend, title=args.title)
    else:
        for serie in series:
            serie.plot(legend=args.legend, title=args.title)

    # Save figure if needed
    if savefig:
        print('Saving figure to ' + args.output + '...')
        plt.savefig(args.output)
        return

    # Else, show it
    plt.show()


if __name__ == '__main__':
    main()
