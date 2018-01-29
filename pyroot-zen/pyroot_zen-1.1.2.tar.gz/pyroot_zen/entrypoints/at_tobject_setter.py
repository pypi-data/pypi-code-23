#!/usr/bin/env python

import logging
import ROOT
from .. import utils

## Collection of hooks 
hooks = []

@utils.tuple_last_arg
def hooked_TObject_setter(self, key, val):
  """
  Shorten the setter to pythonic-descriptor

  ## Simple class
  >>> obj = ROOT.TH1F()
  >>> obj.name = 'foo'
  >>> obj.GetName()
  'foo'
  >>> obj.nameTitle = 'bar', 'baz'  # Setting by tuples
  >>> obj.non_existent_attribute = 'foo'
  Traceback (most recent call last):
    ...
  AttributeError: 'TH1F' object has no attribute 'non_existent_attribute'

  Note: In this construction, duck-typing of the new attribute is forbidden, 
        for ease-of-mind!
  Note: For special pointer-object like gPad, the hack is in _ExpandMacroFunction

  ## SetOwnership
  Usage:
  >> c = ROOT.TCanvas()
  >> c.ownership = False
  
  Note: apply on top of above __setattr__
  Note: Prefer not-auto so that user is in control.

  """

  ## Patch for SetOwnership (adding new attribute).
  if key == 'ownership':
    ROOT.SetOwnership(self, val[0])
    return

  ## Use native setter, prohibit attribute-duck-type
  ## Search also smaller 'setXXX' as in RooFit.
  clsname = self.__class__.__name__
  for prefix in ['Set', 'set']:
    name = prefix+utils.pythoncase_to_camelcase(key)
    try:
      func = super(ROOT.TObject, self).__getattribute__(name)
      ## Apply hooks before final eval
      for hook in hooks:
        func = hook(clsname, name, func)
      ## Execute evaluation
      return func(*val)

    ## If the search fails, silently retry next one.
    except AttributeError:
      pass

  ## None of the search keywords found
  raise AttributeError("%r object has no attribute %r"%(clsname,key))

def _init():
  ROOT.TObject.__setattr__ = hooked_TObject_setter
  logging.debug('Binded to TObject')

def inject(hook):
  """
  Inject the hook to apply to arguments before the actual setter call:

  The signature shoud be:

      new_setter = hook(class_name, attribute_name, original_setter)

  Primary used to apply RooFit arglist/set patcher into setters,
  e.g., ModelConfig.SetSnapshot(RooArgSet)
  
  """
  hooks.append(hook)
