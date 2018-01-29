#!/usr/bin/env python
"""

Provide utils use for patcher.

"""
import functools
import logging
import ROOT
from array import array

#===============================================================================
# STRING
#===============================================================================

def capfirst(s):
  """
  >>> capfirst('aaa')
  'Aaa'
  >>> capfirst('aaaBbbCcc')
  'AaaBbbCcc'
  """
  return s[0].capitalize()+s[1:]

def pythoncase_to_camelcase(s):
  """
  >>> pythoncase_to_camelcase("line_color")
  'LineColor'
  >>> pythoncase_to_camelcase('AlreadyCamelCase')
  'AlreadyCamelCase'
  >>> pythoncase_to_camelcase('lowerCamelCase')
  'LowerCamelCase'
  """
  return ''.join(capfirst(s2) for s2 in s.split('_'))

#===============================================================================
# DECORATOR
#===============================================================================

def tuple_last_arg(func):
  """
  Make sure the last argument of the function is wrapped into tuple,
  useful when it's a setter-style class, ready to be unpacked.
  Only valid for non-kwargs function

  >>> @tuple_last_arg
  ... def foo(key, val):
  ...   print key, val
  >>> foo('key', 'val')
  key ('val',)
  """
  @functools.wraps(func)
  def wrap(*args):
    args = list(args)
    arg  = args[-1]
    args[-1] = arg if isinstance(arg, (list, tuple)) else (arg,)
    return func(*args)
  return wrap

#===============================================================================
# CASTER
#===============================================================================

def DoubleArray(arg):
  """
  Try to cast ``arg`` of correct type to ``array('d')``.
  If it's not the right type, return the original::

    >>> DoubleArray([2, 3, 4])
    array('d', [2.0, 3.0, 4.0])

    >>> DoubleArray('string')
    'string'

    >>> DoubleArray(42)
    42

  """
  if isinstance(arg, (list,tuple)) or hasattr(arg, '__iter__'):
    if all(isinstance(x,(int,float)) for x in arg):
      return array('d', arg)
  return arg

def RooArgList(arg):
  """
  Try to cast ``arg`` of correct type to ``RooArgList``.
  If it's not the right type, return the original::

    >>> RooArgList([1, 2, 3])  # need RooAbsArg, do nothing
    [1, 2, 3]

  """
  ## Expect it to be correct container
  if not isinstance(arg, (list,tuple)):
    return arg
  ## All members should be RooAbsArg
  if not all(isinstance(x, ROOT.RooAbsArg) for x in arg):
    return arg
  ## Finally
  return ROOT.RooArgList(*arg)

def RooArgSet(arg):
  """
  Try to cast ``arg`` of correct type to ``RooArgSet``.
  If it's not the right type, return the original::

    >>> RooArgSet({1, 2, 3})  # need RooAbsArg, do nothing
    set([1, 2, 3])

  """
  ## Expect it to be correct type
  if not isinstance(arg, set):
    return arg
  ## All members should be RooAbsArg
  if not all(isinstance(x, ROOT.RooAbsArg) for x in arg):
    return arg
  ## Finally
  return ROOT.RooArgSet(*arg)

def StdMap_string_RooDataSet(arg):
  """
  For ``RooFit.Import(std::map<string, RooDataSet*>)`` signature::

    >>> ds1 = ROOT.RooDataSet()
    >>> ds2 = ROOT.RooDataSet()
    >>> map = StdMap_string_RooDataSet({'signal': ds1, 'bkg': ds2})
    >>> map
    <ROOT.map<string,RooDataSet*> object at ...>
    >>> map.size()
    2L
    >>> len(map)
    2
    >>> map['signal']
    <ROOT.RooDataSet object at ...>

    ## For incorrect type
    >>> StdMap_string_RooDataSet('not_a_dict')
    'not_a_dict'

  """
  ## Require a dictionary as input
  if not isinstance(arg, dict):
    return arg
  ## Push to map
  cmap = ROOT.std.map('string,RooDataSet*')()
  for key, val in arg.iteritems():
    item = ROOT.std.pair("const string,RooDataSet*")(key, val)
    cmap.insert(cmap.cbegin(), item)
  return cmap

#-------------------------------------------------------------------------------

@tuple_last_arg
def RooCmdArg(key, val):
  """
  Caster for RooCmdArg from keyword-arguments::

    >>> RooCmdArg('Name', 'somename')
    <ROOT.RooCmdArg object ("Name") at ...>

  """
  return getattr(ROOT.RooFit, capfirst(key))(*val)

#===============================================================================
# PATCHERS
#===============================================================================

def new_signature_patcher(*args_casters, **kwargs_casters):
  """
  This function return the patcher (decotator), ready to be applied to the 
  target object, such that everytime the object makes a call::

    obj(*args, **kwargs)

  The args and kwargs will go through the given list of 
  args_casters, kwargs_casters respectively.

  Example::

    >> patcher = utils.new_signature_patcher(utils.RooArgSet, utils.RooArgList, kw=utils.RooCmdArg)
  
  """
  def patcher(func):
    @functools.wraps(func)
    def patched(*args, **kwargs):
      ## Apply patch to each list-arguments
      args = list(args)
      for i,arg in enumerate(args):
        for caster in args_casters:
          arg = caster(arg)
        args[i] = arg
      ## patch the keyword-arguments, then reduce them to list-arguments
      # as it's natively not supported by ROOT
      for key, val in kwargs.iteritems():
        for caster in kwargs_casters.values(): # keys dont matter
          val = caster(key, val)
        args.append(val) # append once it's patched by all casters
      ## Finally, run the true function
      return func(*args)
    return patched
  return patcher

#===============================================================================
