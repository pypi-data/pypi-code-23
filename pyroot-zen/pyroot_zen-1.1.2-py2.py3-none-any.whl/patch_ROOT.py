"""

Perform all patching to ROOT handle here.

"""

import sys
import logging
import ROOT  # reimport it directly outside lazy call.
logging.info('Patching ROOT starts.')
from . import utils
from . import entrypoints

#===============================================================================
# TObject GETTER & SETTER
#===============================================================================

from . import TObject

"""
Case: Innate extra getattr

Some subclass DOES have its own getattr. Need to add them manually.
Note: I don't yet explore what those innate getattr do anything in extra.

In the future version, it'll be nice to be able to detect this automatically

  >>> ROOT.TTree.__getattr__
  <unbound method TTree.__getattr__>

  >> ROOT.TTree.__setattr__
  <slot wrapper '__setattr__' of 'object' objects>

"""
for clsname in 'TTree', 'TFile':
  cls = getattr(ROOT, clsname)
  cls.__getattr__ = TObject.getattr(ROOT.TObject, cls.__getattr__)
del cls, clsname

"""
Case: No extra getattr

  >>> ROOT.TPaveText.__getattr__
  AttributeError: type object 'TPaveText' has no attribute '__getattr__'

  >>> ROOT.TPaveText.__setattr__
  <slot wrapper '__setattr__' of 'object' objects>

"""
ROOT.TObject.__getattr__ = TObject.getattr(ROOT.TObject)

## Getitem
ROOT.TObject.__getitem__ = TObject.getitem

del TObject

#===============================================================================
# ROOT._ExpandMacroFunction
#===============================================================================

@utils.tuple_last_arg
def EMF_setattr(self, key, val):
  """
  Allow setter on ``ROOT._ExpandMacroFunction``.
  """
  key = utils.capfirst(key)
  if key == 'Ownership':
    assert len(val)==1 and isinstance(val[0], bool), 'Wrong arg for SetOwnership.'
    ROOT.SetOwnership(self, val[0])
  else:
    return getattr(self, 'Set'+key)(*val)  

## Access the private _ExpandMacroFunction via __class__
ROOT.gPad.__class__.__setattr__ = EMF_setattr

#===============================================================================
# INNER PATCHING: CONSTRUCTORS, SIGNATURE
#===============================================================================

def hook_constructors_double(name, obj):
  """
  Patch: wrap list of float into float array.
  Hook : Apply to the constructors of the classes.

  >>> ROOT.TH1F('htemp', 'htemp', 3, [1, 2, 3, 4])
  <ROOT.TH1F object ("htemp") at ...>

  >>> ROOT.TGraph(3, [1,2,3], [2,3,4])
  <ROOT.TGraph object ("Graph") at ...>
  """
  ## Patch
  patcher = utils.new_signature_patcher(utils.DoubleArray)
  
  ## Apply on subset of class heuristically...
  valid = False
  if name.startswith('TH'):
    valid = True
  if name.startswith('TProfile'):
    valid = True
  if name.startswith('TGraph'):
    valid = True
  if name in ('TPolyLine',):
    valid = True
  if valid:
    logging.debug('Patching init: '+name)
    obj.__init__ = patcher(obj.__init__)

entrypoints.at_cpp_lookup.inject_after(hook_constructors_double)
del hook_constructors_double

#===============================================================================
# OUTER PATCH: EXTRA FUNCTIONALITY
#===============================================================================

## new signature: (name, title, xarray)
from . import TH1
ROOT.TH1F.__init__ = TH1.init(ROOT.TH1F.__init__) 
del TH1

## new signature: (name, title, xarray, yarray)
from . import TH2
ROOT.TH2F.__init__       = TH2.init(ROOT.TH2F.__init__)
ROOT.TProfile2D.__init__ = TH2.init(ROOT.TProfile2D.__init__)
del TH2

## Delegation
from . import TMultiGraph
ROOT.TMultiGraph.__len__     = TMultiGraph.__len__
ROOT.TMultiGraph.__getitem__ = TMultiGraph.__getitem__
del TMultiGraph

#===============================================================================
# ROOFIT HOOK
#===============================================================================

## Inject an import hook, which will trigger the RooFit patch only when
# there's an actual import.
def hook_await_roofit0(name):
  if name.startswith('Roo'):
    import patch_RooFit # Trigger patch (to inject hooks) before the true import
    entrypoints.at_cpp_lookup.remove('hook_await_roofit0') # expired

entrypoints.at_cpp_lookup.inject_before(hook_await_roofit0)
del hook_await_roofit0

#===============================================================================

## Finally
logging.info('Patching ROOT completed.')
