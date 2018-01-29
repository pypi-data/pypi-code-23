#!/usr/bin/env python
import sys
import logging
import ROOT
from collections import OrderedDict

## Collection of hooks 
hooks_before = OrderedDict()
hooks_after  = OrderedDict()

def wrapper(func):
  def cppyy_import_hook(*args):
    logging.debug('importing: %s'%str(args))
    ## Hooks before import
    for hook in hooks_before.values():
      hook(args[0])
    ## Actual import
    module = func(*args)
    ## Hooks after import
    for hook in hooks_after.values():
      hook(args[0], module)
    return module
  return cppyy_import_hook

def inject_before(hook):
  """
  Signature: hook(name)

  >>> foo = lambda arg: None
  >>> inject_before(foo)
  >>> inject_before(foo)
  Traceback (most recent call last):
  ...
  ValueError: Hook name already used: <lambda>
  """
  logging.debug('Injecting: %r'%hook)
  name = hook.__name__
  if name in hooks_before:
    raise ValueError('Hook name already used: %s'%name)
  hooks_before[name] = hook

def inject_after(hook):
  """
  Signature: hook(name, module)

  >>> foo = lambda arg: None
  >>> inject_after(foo)
  >>> inject_after(foo)
  Traceback (most recent call last):
  ...
  ValueError: Hook name already used: <lambda>
  """
  logging.debug('Injecting: %r'%hook)
  name = hook.__name__
  if name in hooks_after:
    raise ValueError('Hook name already used: %s'%name)
  hooks_after[name] = hook

def remove(name):
  for d in hooks_before, hooks_after:
    if name in d:
      del d[name]

def _init():
  cppyy = sys.modules['cppyy']
  cppyy._backend.LookupCppEntity = wrapper(cppyy._backend.LookupCppEntity)
  logging.debug('Binded to LookupCppEntity')
