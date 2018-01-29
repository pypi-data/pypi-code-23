#!/usr/bin/env python

import logging
import ROOT

## Collection of hooks 
hooks = []

def hooked_TObject_callable(self, name):
  attr = object.__getattribute__(self, name)
  if hasattr(attr, '__call__'):
    if name not in ('__class__',) and not name.startswith('Get'): # usual skip
      clsname = self.__class__.__name__
      # If any hook gives an overriding result, use it
      for hook in hooks:
        res = hook(clsname, name, attr)
        if res is not None:
          return res
  return attr          

def _init():
  ROOT.TObject.__getattribute__ = hooked_TObject_callable
  logging.debug('Binded to TObject')

def inject(hook):
  """
  The signature shoud be:

    patched_caller = hook(class_name, attribute_name, original_caller)

  """
  hooks.append(hook)
