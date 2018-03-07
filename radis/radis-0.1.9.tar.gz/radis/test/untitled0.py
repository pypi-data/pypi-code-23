# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 09:32:32 2018

@author: erwan
"""

from __future__ import absolute_import
def _test_band(name):
    
    ''' run pyspecair, do all the tests, blabla
    '''
    
    return True  #/False

def test_N2_CB():
    band = 'N2_CB'
    
    return _test_band(band)

def test_N2_BA():
    band = 'N2_BA'
    
    return _test_band(band)


# Here we just make sure there is a test routine associated to each molecular
# system. We dont run the tests

from pyspecair.core import MOLECULAR_BAND_LIST

dict_test_functions = {
        'N2_CB':test_N2_CB,
        'N2_BA':test_N2_BA}

# Make sure there is a test routine associated to each function 
for band in MOLECULAR_BAND_LIST:
    assert band in dict_test_functions











