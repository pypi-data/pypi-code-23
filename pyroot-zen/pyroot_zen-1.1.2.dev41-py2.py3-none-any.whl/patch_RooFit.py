#!/usr/bin/env python
"""

Provide patching for RooFit classes & functions.

TODO: ROOT.RooFit.Conditional
"""

import logging
import ROOT   # vanilla handle
import utils  # local
logging.debug('Patching RooFit starts.')

## Trigger import of RooFit library, one more time.
ROOT.RooFit
import entrypoints
entrypoints.at_roostats_lookup._init()

#===============================================================================
# INNER PATCH: GETTER + SETTER
#===============================================================================

def hook_NonTObject_getter_setter(name, obj):
  """
  Prepare the new getter/setter which perform search from ``xxx.foo --> xxx.SetFoo()``.
  This is needed for the remaining classes that are not derived from TObject::

    ## test 1st-way of import
    >>> calc = ROOT.RooStats.ProfileLikelihoodCalculator()
    >>> calc.confidenceLevel = 0.95
    >>> calc.hypoTest
    <ROOT.RooStats::HypoTestResult object at ...>

    ## test 2nd-way of import
    >>> from ROOT.RooStats import SPlot
    >>> sp = SPlot()
    >>> sp.numSWeightVars
    0

  """

  @utils.tuple_last_arg
  def new_setter(self, key, val):
    ## let AttributeError be raised
    fname = 'Set'+utils.capfirst(key)
    func = super(self.__class__, self).__getattribute__(fname)
    return func(*val)
  def new_getter(self, key):
    fname = 'Get'+utils.capfirst(key)
    func = super(self.__class__, self).__getattribute__(fname)
    return func()

  ## The hook will apply patch only for ordinary classes
  # try to skip patched object (even though it should be idempotent).
  if not name.startswith('__') and not name in ('ModelConfig',):
    logging.debug('Patching: %s'%name)
    obj.__getattr__ = new_getter # override any existing __getter__, if any.
    obj.__setattr__ = new_setter # override any existing __setter__, if any.
  return obj

entrypoints.at_roostats_lookup.inject(hook_NonTObject_getter_setter)

#===============================================================================
# INNER PATCH: ARGUMENTS CONVERTER
#===============================================================================

## Patch to wrap pythonic-list,set to RooArgList/Set
patcher = utils.new_signature_patcher(utils.RooArgSet, utils.RooArgList, kw=utils.RooCmdArg)

def hook_roofit_constructors(name, obj):
  """
  Hook to apply above patcher to constructor of classes in RooFit.

  >>> x = ROOT.RooRealVar('x', 'x', 0)
  >>> ROOT.RooDataSet('ds', 'ds', {x})
  <ROOT.RooDataSet object ("ds") at ...>
  """
  if name.startswith('Roo') and name not in ('RooFit', 'RooStats'):
    obj.__init__ = patcher(obj.__init__)

entrypoints.at_cpp_lookup.inject_after(hook_roofit_constructors)

def hook_roofit_setter(clsname, attrname, setter):
  """
  Hook to apply above patcher to setter of classes in RooFit.

  >>> mc = ROOT.RooStats.ModelConfig()
  >>> mc.pdf = 'model'
  """
  valid = False
  if clsname.startswith('Roo') and clsname not in ('RooFit', 'RooStats'):
    valid = True
  elif clsname in ('ModelConfig',):
    valid = True  
  return patcher(setter) if valid else setter

entrypoints.at_tobject_setter.inject(hook_roofit_setter)

def hook_roofit_callable(clsname, attrname, attr):
  """
  Hook to apply above patcher to callable of classes in RooFit

  >>> x = ROOT.RooRealVar('x', 'x', 0)
  >>> ds = ROOT.RooDataSet('ds', 'ds', {x})
  >>> ds.add({x})

  >>> x.frame(name='somename', title='sometitle')
  <ROOT.RooPlot object ("somename") at ...>

  """
  ## Activate only for RooFit classes
  if not clsname.startswith('Roo'):
    return
  logging.debug('probing: %s %s %s'%(clsname, attrname, attr))
  return patcher(attr)

entrypoints.at_tobject_callable.inject(hook_roofit_callable)

#-------------------------------------------------------------------------------

## stdmap
patcher_map_str_ds = utils.new_signature_patcher(utils.StdMap_string_RooDataSet)
ROOT.RooFit.Import = staticmethod(patcher_map_str_ds(ROOT.RooFit.Import))

#===============================================================================
# OUTER PATCH
#===============================================================================

from . import RooArgSet
ROOT.RooArgSet.__iter__  = RooArgSet.__iter__
ROOT.RooArgSet.keys      = RooArgSet.keys
ROOT.RooArgSet.iteritems = RooArgSet.iteritems
del RooArgSet

from . import RooArgList
ROOT.RooArgList.__iter__  = RooArgList.__iter__
del RooArgList

from . import RooWorkspace
ROOT.RooWorkspace.Import = RooWorkspace.Import
del RooWorkspace

from . import RooCategory
ROOT.RooCategory.__len__  = RooCategory.__len__
ROOT.RooCategory.__iter__ = RooCategory.__iter__
del RooCategory

#===============================================================================

logging.info('Patching RooFit completed.')
