""" Test FSF object
"""

from os.path import join as pjoin, dirname
from glob import glob
from collections import OrderedDict
from io import StringIO

import numpy as np
from numpy.testing import assert_array_equal

from fslutils.supporting import read_file
from fslutils.fsf import (FSF, load, loads)


DATA_DIR = pjoin(dirname(__file__), 'data')


def test_fsf_all():
    for design_fname in glob(pjoin(DATA_DIR, '*.fsf')):
        contents = read_file(design_fname)

        for fsf, exp_fname in ((FSF(contents), None),
                               (FSF.from_string(contents), None),
                               (loads(contents), None),
                               (FSF.from_file(design_fname), design_fname),
                               (load(design_fname), design_fname),
                               (FSF.from_file(StringIO(contents)), None),
                               (load(StringIO(contents)), None),
                   ):
            assert fsf.fmri['version'] == '6.00'
            assert isinstance(fsf.contrasts_real, OrderedDict)
            assert isinstance(fsf.contrasts_orig, OrderedDict)
            assert isinstance(fsf.groupmem, np.ndarray)
            assert isinstance(fsf.evgs, np.ndarray)
            assert fsf.filename == exp_fname

    # Loading via a file object
    fname = pjoin(DATA_DIR, 'one_sess_level1.fsf')
    with open(fname, 'rt') as fobj:
        fsf = load(fobj)
        assert fsf.fmri['version'] == '6.00'
        assert fsf.filename == fname

    # Check that we can load from FEAT directory
    fsf = load(pjoin(DATA_DIR, 'level1.feat'))
    assert fsf.fmri['version'] == '6.00'
    assert fsf.filename == pjoin(DATA_DIR, 'level1.feat', 'design.fsf')


def test_fsf_one_sess_group(bart_pumps):
    # Specific tests.
    fsf = load(pjoin(DATA_DIR, 'one_sess_group.fsf'))
    assert list(fsf.contrasts_orig) == []
    assert list(fsf.contrasts_real) == ['Group mean']
    assert_array_equal(fsf.contrasts_real['Group mean'], [1, 0])
    assert_array_equal(fsf.groupmem, [1] * 24)
    exp_evgs = np.ones((24, 2))
    exp_evgs[:, 1] = bart_pumps
    assert_array_equal(fsf.evgs, exp_evgs)
    assert len(fsf.feat_files) == 24


def test_fsf_level1():
    fsf = load(pjoin(DATA_DIR, 'one_sess_level1.fsf'))
    assert list(fsf.contrasts_real) == ['Cash-Inflate']
    assert_array_equal(fsf.contrasts_real['Cash-Inflate'],
                       [-1, 0, 0, 0, 1, 0, 0, 0])
    assert list(fsf.contrasts_orig) == ['Cash-Inflate']
    assert_array_equal(fsf.contrasts_orig['Cash-Inflate'],
                       [-1, 0, 1, 0])
    assert_array_equal(fsf.groupmem, [])
    assert_array_equal(fsf.evgs, [])
    assert fsf.fmri['tr'] == 2
    # Feat files are just the 4D functional
    assert len(fsf.feat_files) == 1
    # Events
    assert len(fsf.events) == 4
    assert list(fsf.events) == ['Inflate', 'Beforeexplode',
                                'Cashout', 'Explode']
    assert fsf.events['Inflate'] == dict(
        shape=3,
        convolve=3,
        convolve_phase=0,
        tempfilt_yn=True,
        deriv_yn=True,
        custom="/home/data/FBI/assessment/ds000009_R2.0.3/"
        "sub-25/func/sub-25_task-balloonanalogrisktask_label-inflate.txt")


def test_fsf_mid(sub_nos):
    fsf = load(pjoin(DATA_DIR, 'two_sess_mid.fsf'))
    assert len(fsf.contrasts_orig) == 0
    assert (list(fsf.contrasts_real) ==
            ['sub-{:02d}'.format(s) for s in sub_nos])
    for contrast, exp_contrast in zip(fsf.contrasts_real.values(), np.eye(24)):
        assert_array_equal(contrast, exp_contrast)
    assert_array_equal(fsf.groupmem, [1] * 48)
    assert_array_equal(fsf.evgs, np.kron(np.eye(24), np.ones((2, 1))))
    assert len(fsf.feat_files) == 48
