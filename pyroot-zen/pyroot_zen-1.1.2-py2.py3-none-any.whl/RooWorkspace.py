import ROOT

def Import(self, *args, **kwargs):
  """
  Workaround "import" keyword (which is a reserved keyword in python)::

    ## Prepare
    >>> w = ROOT.RooWorkspace()
    >>> h = ROOT.TH1F('name', 'title', 100, 0, 100)

    ## Returns kTRUE if an error has occurred.
    >>> w.Import(h)
    False
    
    ## Support import arguments
    >>> w.Import(h, "newname", True)
    False
  
  """
  return getattr(self,'import')(*args, **kwargs)
