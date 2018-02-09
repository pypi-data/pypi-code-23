#!/bin/python
#coding:utf-8
import roomai.common
import copy

class TexasHoldemPrivateState(roomai.common.AbstractPrivateState):

    '''
    The private state of TexasHoldem
    '''
    def __init__(self):
        super(TexasHoldemPrivateState, self).__init__()
        self.__keep_cards__ = []

    def __get_keep_cards__(self):   return tuple(self.__keep_cards__)
    keep_cards = property(__get_keep_cards__, doc="the keep cards.")


    def __deepcopy__(self, memodict={}, newinstance = None):
        if newinstance is None:
            newinstance = TexasHoldemPrivateState()
        if self.keep_cards is None:
            newinstance.__keep_cards__ = None
        else:
            newinstance.__keep_cards__ = [self.keep_cards[i].__deepcopy__() for i in range(len(self.keep_cards))]
        return newinstance