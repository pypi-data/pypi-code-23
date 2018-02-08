#!/bin/python
#coding:utf-8
import roomai.common
import copy


class TexasHoldemPersonState(roomai.common.AbstractPersonState):

    def __init__(self):
        super(TexasHoldemPersonState, self).__init__()
        self.__hand_cards__  =    []

    def __get_hand_cards__(self):   return tuple(self.__hand_cards__)
    hand_cards = property(__get_hand_cards__, doc="The hand cards of the corresponding player. It contains two poker cards. For example, hand_cards=[roomai.coomon.PokerCard.lookup(\"A_Spade\"),roomai.coomon.PokerCard.lookup(\"A_Heart\")]")

    def __deepcopy__(self, memodict={}, newinstance = None):
        if newinstance is None:
            newinstance    = TexasHoldemPersonState()
        newinstance = super(TexasHoldemPersonState, self).__deepcopy__(newinstance=newinstance)
        newinstance.__hand_cards__ = [c.__deepcopy__() for c in self.hand_cards]
        return  newinstance



