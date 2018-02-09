#!/bin/python
import roomai.common

class BridgePersonState(roomai.common.AbstractPersonState):
    '''
    The person state of Bridge
    '''
    def __init__(self):
        super(BridgePersonState, self).__init__()
        self.__hand_cards_dict__ = dict()

    def __get_hand_cards_dict__(self):   return roomai.common.FrozenDict(self.__hand_cards_dict__)
    hand_cards_dict = property(__get_hand_cards_dict__, doc = "The hand cards in the corresponding player. \n"
                                                              "For example, hand_cards_dict = {\"A_Heart\":roomai.bridge.BridgePokerCard.lookup(\"A_Heart\"), \"A_Spade\":roomai.bridge.BridgePokerCard.lookup(\"A_Spade\")}")

    def __deepcopy__(self, memodict={}, newinstance = None):
        if newinstance is None:
            newinstance = BridgePersonState()
        newinstance = super(BridgePersonState,self).__deepcopy__(newinstance=newinstance)
        newinstance.__hand_cards_dict__ = dict(self.__hand_cards_dict__)
        return newinstance
