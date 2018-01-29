"""

Make ``RooArgSet`` obeys the pythonic-set protocol,
with additional non-ambigious dictionary protocol.

Note: Natively, ``RooArgSet`` has ``__getitem__`` defined, taking string key as input.

"""

def __iter__(self):
  """
  Iterate over set objects, additionally ordered by their names.

  >>> set = getfixture('sample_RooArgSet')
  >>> for x in set:
  ...   print x
  <ROOT.RooRealVar object ("x") at ...>
  <ROOT.RooRealVar object ("y") at ...>
  <ROOT.RooRealVar object ("z") at ...>

  """
  for key in self.keys():
    yield self.find(key)

def keys(self):
  """
  Like ``dict.keys``.

  >>> set = getfixture('sample_RooArgSet')
  >>> set.keys()
  ['x', 'y', 'z']
  """
  return self.contentsString().split(',')

def iteritems(self):
  """
  Provide the dict-iterable protocol, yield (key, obj) in this RooArgSet.

  >>> set = getfixture('sample_RooArgSet')
  >>> for key, val in set.iteritems():
  ...   print key, val
  x <ROOT.RooRealVar object ("x") at ...>
  y <ROOT.RooRealVar object ("y") at ...>
  z <ROOT.RooRealVar object ("z") at ...>

  """
  for key in self.keys():
    yield key, self.find(key)
