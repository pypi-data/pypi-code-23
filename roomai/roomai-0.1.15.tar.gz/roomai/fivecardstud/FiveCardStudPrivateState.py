#!/bin/python
import roomai
import roomai.common

class FiveCardStudPrivateState(roomai.common.AbstractPrivateState):
    """
    """
    all_hand_cards    = None

    def __deepcopy__(self, memodict={}, newinstance = None):
        '''
        
        :param memodict: 
        :return: 
        '''

        if newinstance is None:
            newinstance = FiveCardStudPrivateState()
        copyinstance = super(FiveCardStudPrivateState, self).__deepcopy__(newinstance = newinstance)

        if self.all_hand_cards is None:
            copyinstance.all_hand_cards = None
        else:
            copyinstance.all_hand_cards = [self.all_hand_cards[i].__deepcopy__() for i in range(len(self.all_hand_cards))]
        return copyinstance