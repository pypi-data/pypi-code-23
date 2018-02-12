# coding=utf-8

"""
Tests for the common lib.
"""
import logging
import os
import unittest

from tmlab_common.common import (read_csv_header,
                                 create_out_fname)

__author__ = 'cmayes'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Constants #
DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
SUB_DATA_DIR = os.path.join(DATA_DIR, 'small_tests')
LAMMPS_PROC_DIR = os.path.join(DATA_DIR, 'lammps_proc')
FES_DIR = os.path.join(DATA_DIR, 'fes_out')
CALC_PKA_DIR = 'calc_pka'

CSV_FILE = os.path.join(DATA_DIR, CALC_PKA_DIR, 'rad_PMF_last2ns3_1.txt')
FRENG_TYPES = [float, str]

ORIG_WHAM_ROOT = "PMF_last2ns3_1"
ORIG_WHAM_FNAME = ORIG_WHAM_ROOT + ".txt"
ORIG_WHAM_PATH = os.path.join(DATA_DIR, ORIG_WHAM_FNAME)
SHORT_WHAM_PATH = os.path.join(DATA_DIR, ORIG_WHAM_FNAME)
EMPTY_CSV = os.path.join(DATA_DIR, 'empty.csv')

OUT_PFX = 'rad_'

# Data #
CSV_HEADER = ['coord', 'free_energy', 'corr']

# Tests #

class TestReadFirstRow(unittest.TestCase):

    def testFirstRow(self):
        self.assertListEqual(CSV_HEADER, read_csv_header(CSV_FILE))

    def testEmptyFile(self):
        self.assertIsNone(read_csv_header(EMPTY_CSV))


class TestFnameManipulation(unittest.TestCase):
    def testOutFname(self):
        """
        Check for prefix addition.
        """
        self.assertTrue(create_out_fname(ORIG_WHAM_PATH, prefix=OUT_PFX).endswith(
            os.sep + OUT_PFX + ORIG_WHAM_FNAME))



