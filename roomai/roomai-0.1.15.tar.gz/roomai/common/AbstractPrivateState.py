#!/bin/python
#coding=utf8

import roomai
import roomai.common
logger = roomai.get_logger()



class AbstractPrivateState(object):
    '''
    The Abstract class of the private state. The information in the private state is hidden from every player
    '''
    def __deepcopy__(self, memodict={}, newinstance = None):
        if newinstance is None:
            return AbstractPrivateState()
        else:
            return newinstance