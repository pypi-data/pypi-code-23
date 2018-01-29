from collections import Iterable

#===============================================================================

def init(old_init):
  """
  Provide additional constructor signature::

    TH1( name, title, arr )

  i.e., skip the argument for array's length,
  where arr are bins edges. The number of bins is narr-1

  >>> ROOT.TH1F('name', 'title', range(10))
  <ROOT.TH1F object ("name") at ...>
  """
  def wrap(self, *args):
    ## Catch the right signature
    if len(args)==3:
      name, title, arr = args
      if isinstance(arr, Iterable):
        new_args = name, title, len(arr)-1, arr
        return old_init(self, *new_args)
    return old_init(self, *args)
  return wrap
