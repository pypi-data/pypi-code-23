# -*- coding: utf-8 -*-

from bruker_opus_filereader import OpusReader

import logging
import unittest

###############################################################################
class OpusTest(unittest.TestCase):

    logger = logging.getLogger('bruker_opus')

    dataBlocks = [
            'Sample', 'IgSm', 'Optik', 'Acquisition', 'Instrument',
            'Fourier Transformation', 'IgSm Data Parameter']


    def setUp(self):
        pass

    
    def test_00_readFile(self):
        OpusTest.sample = OpusReader('..\\data\\a6040_MIR_alignment.0')
        OpusTest.sample.readDataBlocks()
        
        for dataBlock in OpusTest.dataBlocks:
            self.assertTrue(dataBlock in OpusTest.sample.keys())

    def test_01_readStringParameter(self):
        OpusTest.


    def tearDown(self):
        pass
    
###############################################################################
if __name__ == '__main__':
    ### configuration
    # loggingLevel = logging.DEBUG
    loggingLevel = logging.INFO

    ### set logging
    logging.basicConfig(level = loggingLevel)
    logger = logging.getLogger('bruker_opus')
    logger.setLevel(loggingLevel)

    ### run unit test
    unittest.main()