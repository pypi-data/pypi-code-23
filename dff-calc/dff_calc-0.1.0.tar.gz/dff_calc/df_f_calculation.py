"""
__author__ = Hagai Hargil
"""
import numpy as np
import attr
from attr.validators import instance_of
import pandas as pd


@attr.s(slots=True)
class DffCalculator:
    """
    Takes a matrix with rows as independent fluorescent traces,
    and returns a similar-sized matrix with the corresponding dF/F values
    calculated based on https://www.nature.com/articles/nprot.2010.169
    """
    data = attr.ib(validator=instance_of(np.ndarray))
    fps = attr.ib(default=30., validator=instance_of(float))  # Hz
    tau_0 = attr.ib(default=0.1, validator=instance_of(float))  # seconds, EWMA parameter
    tau_1 = attr.ib(default=0.35, validator=instance_of(float))  # seconds, smoothed F0 parameter
    tau_2 = attr.ib(default=2., validator=instance_of(float))  # seconds, time window before t to minimize
    invert = attr.ib(default=False, validator=instance_of(bool))
    f0 = attr.ib(init=False)
    unfiltered_dff = attr.ib(init=False)
    dff = attr.ib(init=False)
    trace_num = attr.ib(init=False)  # number of traces
    sample_num = attr.ib(init=False)  # number of samples per trace
    min_per = attr.ib(init=False)

    def calc(self) -> np.ndarray:
        """ Main function to run the calculation
        :returns: Filtered dF/F matri
        """
        self.__calc_f0()
        self.__calc_dff_unfiltered()
        self.__filter_dff()
        if self.data.ndim == 1:
            return self.dff.values.ravel()
        else:
            return self.dff.values

    def __attrs_post_init__(self):
        """ Change params to have fitting units """
        self.tau_0 = self.fps * self.tau_0
        self.tau_1 = int(self.fps * self.tau_1)
        self.tau_2 = int(self.fps * self.tau_2)
        self.trace_num = self.data.shape[0]
        self.min_per = max(1, int(self.fps / 10))
        if self.invert:
            self.data = -self.data

    def __calc_f0(self):
        """
        Return the F_0(t) baseline for the dF/F calculation using a boxcar window
        :return:
        """
        data = pd.DataFrame(self.data.T)
        self.f0 = data.rolling(window=self.tau_1, win_type='boxcar').mean()\
                      .rolling(window=self.tau_2, min_periods=self.min_per).min() + np.finfo(float).eps

    def __calc_dff_unfiltered(self):
        """ Subtract baseline from current fluorescence """
        raw_calc = (self.data - self.f0.values.ravel()) / self.f0.values.ravel()
        self.unfiltered_dff = pd.DataFrame(raw_calc)
        self.unfiltered_dff.fillna(0)

    def __filter_dff(self):
        """ Apply an exponentially weighted moving average to the dF/F data """
        alpha = 1 - np.exp(-1/self.tau_0)
        self.dff = self.unfiltered_dff.ewm(alpha=alpha, min_periods=self.min_per).mean()
