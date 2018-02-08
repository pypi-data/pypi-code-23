#!/bin/python
import roomai.common
import roomai.sevenking
from roomai.sevenking import AllSevenKingPatterns

from functools import cmp_to_key

class SevenKingAction(roomai.common.AbstractAction):
    '''
    The SevenKing action. The SevenKing action contains some cards. Examples of usages:\n
    >> import roomai.sevenking\n
    >> action = roomai.sevenking.SevenKingAction.lookup("A_Spade,A_Heart") \n
    >> ## We strongly recommend you to get an action with the lookup function.\n
    >> action.key \n
    "A_Heart, A_Spade"\n
    >> action.cards[0].point\n
    "A"\n
    >> action.cards[0].suit\n
    "Heart"\n
    >> action.pattern\n
    p_2 # There are 2 cards in this action\n
    '''

    def __init__(self, key):
        if not isinstance(key,str):
            raise TypeError("The key for SevenKingAction is an str, not %s"%(type(str)))

        super(SevenKingAction,self).__init__(key)
        self.__cards__       = []
        if len(key) > 0:
            for c in self.key.split(","):
                self.__cards__.append(roomai.sevenking.SevenKingPokerCard.lookup(c))
            self.__cards__.sort(key = cmp_to_key(roomai.sevenking.SevenKingPokerCard.compare))
            self.__key__ = ",".join([c.key for c in self.__cards__])
        else:
            self.__key__ = ""

        self.__pattern__ = self.__action2pattern__(self)

    @classmethod
    def __action2pattern__(cls, action):
        num_cards  = len(action.cards)
        return AllSevenKingPatterns["p_%d"%(num_cards)]

    def __get_key__(self):
        return self.__key__
    key = property(__get_key__, doc="The key of this action. For example, key = \"3_Heart,3_Spade\". The check action's key = \"\"")


    def __get_cards__(self):
        return tuple(self.__cards__)
    cards = property(__get_cards__, doc="The cards in this action. For example, cards=[roomai.sevenking.SevenKingPokerCards.lookup(\"A_Spade\")]")

    def __get_pattern__(self):
        return self.__pattern__
    pattern = property(__get_pattern__, doc="The pattern of the action")

    @classmethod
    def lookup(cls, key):
        '''
        lookup a SevenKing action with the specified key
        
        :param key: The specified key
        :return: The action
        '''
        if key in AllSevenKingActions:
            return AllSevenKingActions[key]
        else:
            AllSevenKingActions[key] = SevenKingAction(key)
            return AllSevenKingActions[key]

    def __deepcopy__(self, memodict={}, newinstance = None):

        if self.__key__ in AllSevenKingActions:
            return AllSevenKingActions[self.__key__]

        if newinstance is None:
            newinstance = SevenKingAction(self.key)
        newinstance             = super(SevenKingAction,self).__deepcopy__(newinstance = newinstance)
        newinstance.__key__     = self.__key__
        newinstance.__cards__   = [card.__deepcopy__() for card in self.__cards__]
        newinstance.__pattern__ = self.__pattern
        AllSevenKingActions[self.__key__] = newinstance
        return newinstance

AllSevenKingActions = dict()

