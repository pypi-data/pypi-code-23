import scipy.signal as signal
import numpy as np


class Filter:
    TYPE_SGOLAY = "sgolay"
    TYPE_MEDIAN = "median"
    PARAM_WINDOW_LENGTH = "window_length"
    PARAM_POLY_ORDER = "polynomial_order"

    # MOVING_AVERAGE = "MovingAverage"
    # LMS = "LMS"
    # LOW_PASS = "LowPass"

    def __init__(self):
        self.type = self.TYPE_SGOLAY
        self.data = []
        self._diff = None
        self.PARAMETERS = {
            self.TYPE_SGOLAY: {
                self.PARAM_WINDOW_LENGTH: 31,
                self.PARAM_POLY_ORDER: 5
            },
            self.TYPE_MEDIAN: {
                self.PARAM_WINDOW_LENGTH: 31
            }
        }

    def set_data(self, data):
        self.data = data
        self._diff = None
        return self

    def set_type(self, flt_type):
        if self._type_exist(flt_type):
            self.type = flt_type
        else:
            raise ValueError("Unrecognised filter of type: " + flt_type)

    def set_param(self, param, value):
        self.PARAMETERS[self.type][param] = value

    def get(self):
        return getattr(self, 'get_' + self.type)()

    def get_sgolay(self):
        params = self._get_params(self.TYPE_SGOLAY)
        return signal.savgol_filter(self.data, params[self.PARAM_WINDOW_LENGTH], params[self.PARAM_POLY_ORDER])

    def get_median(self):
        params = self._get_params(self.TYPE_MEDIAN)
        return signal.medfilt(self.data, [params[self.PARAM_WINDOW_LENGTH]])

    def remove_outliers(self, threshold=5, interpolation_window=10):
        """
        :param threshold: Absolute minimum difference between two samples to be considered an outlier
        :param interpolation_window: Maximum consecutive samples to be considered as outliers
        :return: numpy.array of set data without outliers
        """
        filled = np.array(self.data)
        for i, val in enumerate(filled[0:-interpolation_window]):
            for n in range(i + 1, i + 1 + interpolation_window):
                if abs(val - filled[n]) < threshold:
                    if n - i > 1:  # If index n pointing after outlier, do interpolation
                        filled[i:(n + 1)] = np.linspace(val, filled[n], (n + 1) - i)
                    break
        return filled

    def detect_stuck(self, threshold=10):
        """
        :param threshold: Number of samples needed for stuck marking
        :return:
        """
        d_data = self.get_derivative()
        d_data[np.abs(d_data) > 0] = 1
        return signal.medfilt(d_data, [threshold * 2 - 1])

    def get_line_interpolation(self):
        d_data = self.get_derivative()
        d_mean = np.mean(d_data[0:90000])
        mean = np.mean(self.data)
        half_s_len = len(self.data) / 2
        return [(index - half_s_len) * d_mean + mean for index, val in enumerate(self.data)]

    def get_derivative(self):
        if self._diff is None:
            self._diff = np.diff(self.data)
            self._diff = np.append(self._diff[0], self._diff)
        return self._diff

    def in_range(self, lower_bound, upper_bound):
        return (lower_bound < self.data) & (self.data < upper_bound)

    def _get_params(self, flt_type):
        return self.PARAMETERS[flt_type]

    def _type_exist(self, flt_type):
        if flt_type in self.PARAMETERS:
            return True
        else:
            return False
