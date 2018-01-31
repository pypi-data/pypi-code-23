# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd

from bruker_opus_filereader import OpusReader
from ifg_spectrum_data import Interferogram

###############################################################################

# read data
sample = OpusReader('..\\data\\b476_MIR_single_sided.0')
# sample = OpusReader('..\\data\\a6040_MIR_alignment.0')
sample.readDataBlocks()

lwn = sample['Instrument']['LWN']
lambda_laser = 1 / lwn / 100 * 1E+9

dx = 1 / 2 / lwn
y = sample['IgSm']

ifg = Interferogram(y, dx)
ifg.roll()

spectrum = ifg.spectrum()

df = pd.read_csv('..\\data\\b476_MIR_single_sided.csv', header=None)
wn = df[0]
spectrum_opus = df[1]


# plots
plt.close('all')
plt.subplot(2,1,1)
ifg.plot()
plt.subplot(2,1,2)
spectrum.plot('complex')
plt.xlim((6000, 0))
plt.ylim((-2.5, 5))
plt.xlabel('wavenumber [cm$^{-1}$]')

# plt.figure()
plt.plot(wn, 8 * spectrum_opus)

# black body radiation
'''
import numpy as np
import scipy.constants as constants

h = constants.Planck
c = constants.speed_of_light
k = constants.Boltzmann

T = 3000

wn = np.linspace(1, 20000)
wn_per_meter = wn * 100
rho = 1E-15 * wn_per_meter**3 / (np.exp(h * c * wn_per_meter / k / T) - 1)
plt.plot(wn, rho)
plt.xlim((20000, 0))
'''