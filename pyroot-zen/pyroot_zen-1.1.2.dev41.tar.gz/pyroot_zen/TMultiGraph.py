from . import *

def __len__(self):
  """
  Return the number of graphs in this ``TMultiGraph``.

  >>> gr = ROOT.TMultiGraph()
  >>> gr.Add(ROOT.TGraph())
  >>> gr.Add(ROOT.TGraph())
  >>> len(gr)
  2

  """
  return len(self.graphs)

def __getitem__(self, index):
  """
  Delegate the ``GetListOfGraphs`` to ``__getitem__`` protocol.

  >>> g1 = ROOT.TGraph()
  >>> g1.name = 'g1'
  >>> gr = ROOT.TMultiGraph()
  >>> gr.Add(g1)
  >>> gr[0]
  <ROOT.TGraph object ("g1") at ...>

  """
  return self.graphs[index]
