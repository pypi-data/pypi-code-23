# __init__.py

import os, sys
paths_to_append = []
paths_to_append.append( os.path.join(os.path.dirname(__file__), "modules","_plot_seq") )
paths_to_append.append( os.path.join(os.path.dirname(__file__), "modules","_plot_prf") )
paths_to_append.append( os.path.join(os.path.dirname(__file__), "modules") )
paths_to_append.append( os.path.dirname(__file__) )
for p in paths_to_append:
  if p not in sys.path:
    """ if we do not check, we end up with copies of same paths in sys.path """
    sys.path.append( p )


from plot_prf import plot_prf
from plot_seq import plot_seq
