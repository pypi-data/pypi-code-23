#!/usr/bin/env python
"""

Apply hooks after the call from RooStats namespace. 
This has 2 forms:

1. ROOT.RooStats.ProfileLikelihoodCalculator

2. from ROOT.RooStats import ProfileLikelihoodCalculator

"""

import logging
import ROOT

## Collection of hooks 
hooks = []

def wrapper(old_getattribute):
  def getattribute(self, key):
    obj = old_getattribute(self, key)
    for hook in hooks:
      obj = hook(key, obj)
    return obj
  return getattribute

def inject(hook):
  """
  Hook signature:
      attr = hook(attribute_name, retrieved_attr)
  """
  hooks.append(hook)

def _init():
  ROOT.RooStats.__class__.__getattribute__ = wrapper(ROOT.RooStats.__class__.__getattribute__)  
  logging.debug('Binded to ROOT.RooStats')



  # def tracefunc(frame, event, arg, indent=[0]):
  #     print frame.f_code
  #     if event == "call":
  #         indent[0] += 2
  #         print "-" * indent[0] + "> call function", frame.f_code.co_name
  #     elif event == "return":
  #         print "<" + "-" * indent[0], "exit function", frame.f_code.co_name
  #         indent[0] -= 2
  #     return tracefunc
  # import sys
  # sys.settrace(tracefunc)
