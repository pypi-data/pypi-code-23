#!/usr/bin/env python
"""

Test each example that it runs succesfully.

"""

import os
import pytest
from subprocess import check_output, STDOUT
from pyroot_zen import ROOT

def test_lhcb_z_csc(tmpdir):
  stdout = check_output('examples/lhcb_z_csc.py', stderr=STDOUT)
  assert 'Info in <TCanvas::Print>: pdf file lhcb_z_csc.pdf has been created' in stdout

def test_poisson_likelihood(tmpdir):
  stdout = check_output('examples/poisson_likelihood.py', stderr=STDOUT)
  assert '68% interval on s is : [0.57, 4.09]' in stdout
  assert 'Best fitted POI value = 2.00027 +/- 1.70987' in stdout
  assert 'The computed upper limit is: 6.22525348101 +/- 0.0' in stdout
