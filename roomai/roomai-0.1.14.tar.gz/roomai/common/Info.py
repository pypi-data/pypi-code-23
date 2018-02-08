#!/bin/python
#coding=utf8

import roomai
from roomai.common import AbstractPublicState
from roomai.common import AbstractPersonState
logger = roomai.get_logger()


class Info(object):
    '''
    The class of information sent by env to a player. The Info class contains the public state and the corresponding person state w.r.t the target player
    '''
    def __init__(self):
        self.__public_state__       = AbstractPublicState()
        self.__person_state__       = AbstractPersonState()


    def __get_public_state__(self):
        return self.__public_state__
    public_state = property(__get_public_state__, doc="The public state in the information")

    def __get_person_state__(self):
        return self.__person_state__
    person_state = property(__get_person_state__, doc="The person state in the information")

    def __deepcopy__(self, memodict={}, newinstance = None):
        if newinstance is None:
            newinstance = Info()
        newinstance.__public_state__  = self.__public_state.__deepcopy__()
        newinstance.__personc_state__ = self.__person_state.__deepcopy__()
        return newinstance