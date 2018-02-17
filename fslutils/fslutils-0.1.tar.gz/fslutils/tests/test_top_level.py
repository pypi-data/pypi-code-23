""" Test top-level namespace
"""

from os.path import join as pjoin, dirname

import fslutils
from fslutils.supporting import read_file

DATA_DIR = pjoin(dirname(__file__), 'data')


def test_fsf_one_sess_group(bart_pumps):
    fname = pjoin(DATA_DIR, 'one_sess_group.fsf')
    contents = read_file(fname)
    for fsf in (fslutils.FSF(contents),
                fslutils.fsf.load(fname),
                fslutils.fsf.loads(contents)):
        assert len(fsf.contrasts_real) == 1
