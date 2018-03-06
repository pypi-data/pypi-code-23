import logging
from os import path
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import h5py
warnings.resetwarnings()

__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__version__ = "0.1.1"


class H5Array(object):
  """Wrap (d : h5py.Dataset, f : h5py.File) so that
  wrapped.x == numpy.array(f[d['x']])
  @return[out] wrapped  :
  """
  from numpy import array

  def __init__(self, data, meta=None):
    self.data = data
    self.meta = meta

  def __getattr__(self, item):
    return getattr(self.data, item)

  def __len__(self):
    return len(self.data)

  def __getitem__(self, item):
    res = self.data.__getitem__(item)
    return res if self.meta is None else self.array(self.meta[res])


class H5Reader(object):
  def __init__(self, fname, mode='r', prefix=None, **kwargs):
    self.f = h5py.File(fname, mode=mode, **kwargs)
    bname = path.splitext(path.split(fname)[-1])[0]
    self.prefix = prefix if prefix is not None \
        else bname + '/' if bname in self.f.keys() else ''

  def __getattr__(self, item):
    log = logging.getLogger(__name__)
    key = self.prefix + item
    log.debug(key)
    res = self.f[key]

    if res.dtype == 'O':
      return H5Array(res, self.f)
    return H5Array(res)

  def keys(self):
    return self.f[self.prefix].keys() if self.prefix else self.f.keys()
