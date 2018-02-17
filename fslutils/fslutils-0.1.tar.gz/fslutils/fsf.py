""" Class and functions to encapsulate FSF information
"""

from os.path import isdir, join as pjoin
from collections import OrderedDict
import re

import numpy as np

from .supporting import read_file
from .featparser import fsf_to_dict


END_NO = re.compile(r'(\d+)$')

def _end_number(k):
    # Key sorter using number at end of string
    return int(END_NO.search(k).groups()[0])


class FSF(object):
    """ Encapsulate FSF contents
    """

    _known_keys = ['fmri', 'feat_files',
                   'initial_highres_files',
                   'highres_files']

    def __init__(self, contents):
        self.contents = contents
        for key, value in fsf_to_dict(contents).items():
            if key not in self._known_keys:
                raise ValueError('Unknown key {}'.format(key))
            self.__dict__[key] = value
        self.filename = None

    @classmethod
    def from_string(cls, in_str):
        """ Initialize from string `in_str`, return as FSF object
        """
        return cls(in_str)

    @classmethod
    def from_file(cls, file_ish):
        """ Initialize from contents of `file_ish`, return as FSF object

        Set filename if available.

        Parameters
        ----------
        file_ish : object
            Can be string, giving filename of design file, or of the containing
            FEAT directory, in which case we assume ``design.fsf`` as the
            design filename.  Can also be file-like object implementing
            ``read`` method.
        """
        if hasattr(file_ish, 'read'):
            filename = getattr(file_ish, 'name', None)
            contents = file_ish.read()
        else:
            if isdir(file_ish):  # Could be FEAT directory
                file_ish = pjoin(file_ish, 'design.fsf')
            filename = file_ish
            contents = read_file(file_ish)
        fsf = cls.from_string(contents)
        fsf.filename = filename
        return fsf

    def _numbered_vals(self, prefix):
        fsfd = self.fmri
        keys = [k for k in fsfd if k.startswith(prefix)]
        return [fsfd[k] for k in sorted(keys, key=_end_number)]

    def _get_contrasts(self, suffix='real'):
        contrasts = OrderedDict()
        fsfd = self.fmri
        # May be no contrasts of this type (given by suffix)
        names = self._numbered_vals('conname_{}.'.format(suffix))
        if not 'conname_{}.1'.format(suffix) in fsfd:
            return contrasts
        for i, name in enumerate(names):
            contrasts[name] = np.array(
                # 1-based indexing in FSF file
                self._numbered_vals('con_{}{}.'.format(suffix, i + 1)))
        return contrasts

    @property
    def contrasts_real(self):
        return self._get_contrasts('real')

    @property
    def contrasts_orig(self):
        return self._get_contrasts('orig')

    @property
    def evgs(self):
        evgs = []
        # 1-based indexing in FSF file
        evg_no = 1
        while True:
            evg_vals = self._numbered_vals('evg{}.'.format(evg_no))
            if len(evg_vals) == 0:
                break
            evgs.append(evg_vals)
            evg_no += 1
        return np.array(evgs)

    @property
    def n_events(self):
        return len(self._numbered_vals('conname_real.'))

    @property
    def events(self):
        events = OrderedDict()
        fsfd = self.fmri
        names = self._numbered_vals('evtitle')
        for i, name in enumerate(names):
            ev_no = str(i + 1)
            event = {}
            for key_root in ('shape',
                             'convolve',
                             'convolve_phase',
                             'tempfilt_yn',
                             'deriv_yn',
                             'custom'):
                event[key_root] = fsfd.get(key_root + ev_no)
            events[name] = event
        return events

    @property
    def groupmem(self):
        return np.array(self._numbered_vals('groupmem.'))


load = FSF.from_file

loads = FSF.from_string
