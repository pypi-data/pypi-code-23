#!/usr/bin/env python

def __len__(self):
  """

  >>> cat = getfixture('sample_RooCategory')
  >>> len(cat)
  3
  """
  return self.numTypes()

def __iter__(self):
  """
  Loop over ordered labels.

  >>> cat = getfixture('sample_RooCategory')
  >>> for x in cat: print(x)
  alpha
  beta
  gamma

  """
  i0 = self.index # initial state
  for i in xrange(len(self)):
    self.index = i
    yield self.label
  self.index = i0 # restore
