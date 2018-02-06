# -*- coding: utf-8 -*-

###############################################################################
import numpy as np 
import os
import unittest

from ono.bruker_opus_filereader import OpusReader

### local imports from ########################################################
from semi.carbon_concentration.carbon_fit import CarbonFit

###############################################################################
class TestCarbonFit(unittest.TestCase):

    data = {}

    @classmethod
    def setUpClass(cls):
        testdir = os.path.abspath(os.path.dirname(__file__))
        basedir = os.path.abspath(os.path.join(testdir, '..'))
        datadir = os.path.join(basedir, 'data')

        ### reference data
        filename = 'Abs_119_624_2015_12_07.1'
        cls.ref_file = os.path.join(datadir, filename)
        
        opus = OpusReader(cls.ref_file)
        opus.readDataBlocks()

        fxv = opus['AB Data Parameter']['FXV']
        lxv = opus['AB Data Parameter']['LXV']
        npt = opus['AB Data Parameter']['NPT']
        cls.wn = np.linspace(fxv, lxv, npt)
        cls.ref = opus['AB']

        ### low carbon sample
        filename = 'Abs_119_625_2015_12_07.1'
        cls.sample_file = os.path.join(datadir, filename)
        
        opus = OpusReader(cls.sample_file)
        opus.readDataBlocks()

        fxv = opus['AB Data Parameter']['FXV']
        lxv = opus['AB Data Parameter']['LXV']
        npt = opus['AB Data Parameter']['NPT']
        cls.wn_low_carbon = np.linspace(fxv, lxv, npt)
        cls.sample_low_carbon = opus['AB']

        ### high carbon sample
        filename = 'Abs_119_626_2015_12_07.1'
        cls.sample_file = os.path.join(datadir, filename)
        
        opus = OpusReader(cls.sample_file)
        opus.readDataBlocks()

        fxv = opus['AB Data Parameter']['FXV']
        lxv = opus['AB Data Parameter']['LXV']
        npt = opus['AB Data Parameter']['NPT']
        cls.wn_high_carbon = np.linspace(fxv, lxv, npt)
        cls.sample_high_carbon = opus['AB']


    def test_00_fit_high_carbon(self):
        carbon = CarbonFit(
            TestCarbonFit.wn,
            TestCarbonFit.ref,
            TestCarbonFit.sample_high_carbon)
        
        carbon.fit()
        
        self.assertAlmostEqual(carbon.absMax, 0.4008, places=4)
        self.assertLess(carbon.wFWHM, 2)
        self.assertAlmostEqual(carbon.cCarbon, 9.1296E+15, delta=1E+13)

        
    def test_01_fit_low_carbon(self):
        carbon = CarbonFit(
            TestCarbonFit.wn,
            TestCarbonFit.ref,
            TestCarbonFit.sample_low_carbon)
        
        carbon.fit()
        
        self.assertAlmostEqual(carbon.absMax, 0.05776, places=4)
        self.assertLess(carbon.wFWHM, 2)
        self.assertAlmostEqual(carbon.cCarbon, 1.3798E+15, delta=1E+13)
