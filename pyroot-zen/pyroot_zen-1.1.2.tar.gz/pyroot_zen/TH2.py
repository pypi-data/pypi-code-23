#!/usr/bin/env python

from collections import Iterable

#===============================================================================

def init(old_init):
  """
  Provide additional constructor signature::

    TH2( name, title, xarr, yarr )

  where ``xarr``, ``yarr`` are bins edges. The number of bins are ``nx-1, ny-1``::

    >>> ROOT.TH2F('H2', 'H2', range(8), range(10))
    <ROOT.TH2F object ("H2") at ...>

    >>> ROOT.TProfile2D('P2', 'P2', range(8), range(10))
    <ROOT.TProfile2D object ("P2") at ...>

    ## old signature still works
    >>> ROOT.TH2F('H3', 'H3', 8, range(8), 10, range(10))
    <ROOT.TH2F object ("H3") at ...>

  """
  def wrap(self, *args):
    ## Catch the right signature
    if len(args)==4:
      name, title, xarr, yarr = args
      if isinstance(xarr, Iterable) and isinstance(yarr, Iterable):
        new_args = name, title, len(xarr)-1, xarr, len(yarr)-1, yarr
        return old_init(self, *new_args)
    return old_init(self, *args)
  return wrap

#===============================================================================
