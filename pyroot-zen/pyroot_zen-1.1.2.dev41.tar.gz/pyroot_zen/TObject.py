#!/usr/bin/env python

import functools
import ROOT
import utils # local

#===============================================================================

def getattr(cls, func_default=None):
  """
  Shorten the getter to pythonic-descriptor, 
  valid only for getter with no arguments::
  
    ## Simple class
    >>> obj = ROOT.TH1F('htemp1', 'htemp1', 100, 0, 100)
    >>> obj.name            # Instead of obj.GetName()
    'htemp1'
    >>> ROOT.gROOT.files    # Instead of gROOT.GetListOfFiles()
    <ROOT.TList object ("Files") at ...>

    ## Some class has innate getattr, so it'll be decorated
    >>> ROOT.TTree.__getattr__
    <unbound method TTree.__getattr__>
    >>> obj = ROOT.TTree('some_name', 'some_title')
    >>> obj.title           # Instead of obj.GetTitle()
    'some_title'

    ## If missing, raise exception
    >>> obj.unknown_attr
    Traceback (most recent call last):
      ...
    AttributeError: 'TTree' object has no attribute 'unknown_attr'

  """
  PREFIXES = 'Get', 'GetListOf', 'get'

  def TObject_getattr(self, key):
    ## Try func_default, property style first (e.g., new-style tree branch)
    # some of these or hidden var, so it's not exposed by hasattr.
    if func_default:
      try:
        return func_default(self, key)
      except AttributeError:
        pass
      try:
        return super(cls, self).__getattribute__(key)
      except AttributeError:
        pass

    ## By python design, the key (unmodified) should already be search on
    #  local instance already. Only once the search fails, getattr is a fallback.
    ## Check over these fallbacks
    for prefix in PREFIXES:
      name = prefix+utils.pythoncase_to_camelcase(key)
      # attempt with given getattr first, if any.
      try:
        if func_default:
          return func_default(self,name)()
      except AttributeError:
        pass
      # then, attempt with super.
      try:
        return super(cls,self).__getattribute__(name)()
      except AttributeError:
        pass
    raise AttributeError("%r object has no attribute %r"%(self.__class__.__name__,key))

  if func_default:
    return functools.wraps(func_default)(TObject_getattr)
  return TObject_getattr

#===============================================================================

def getitem(self, key):
  """
  Shorten ``obj.FindObject('name')`` to ``obj['name']``::

    >>> h = ROOT.TH1F('htemp2', 'htemp2', 100, 0, 100)

    >>> ROOT.gROOT['htemp2']
    <ROOT.TH1F object ("htemp2") at ...>

    >>> ROOT.gROOT['bad_item']
    Traceback (most recent call last):
      ...
    KeyError: 'bad_item'

  """
  if hasattr(self, 'FindObject'):
    res = self.FindObject(key)
    if res: # guard missing
      return res
  ## not so useful yet...
  # if hasattr(self, 'Get'):
  #   res = self.Get(key)
  #   if res:
  #     return res
  raise KeyError(key)

#===============================================================================
