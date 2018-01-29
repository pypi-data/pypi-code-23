#!/usr/bin/env python

"""

Note: Natively, ``RooArgList`` has ``__getitem__`` defined, taking ``int`` key as input.

"""

def __iter__(self):
  """

  >>> list = getfixture('sample_RooArgList')
  >>> for x in list:
  ...   print x
  <ROOT.RooRealVar object ("x") at ...>
  <ROOT.RooRealVar object ("y") at ...>
  <ROOT.RooRealVar object ("z") at ...>

  """
  for i in range(len(self)):
    yield self.at(i)
