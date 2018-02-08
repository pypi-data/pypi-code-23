#!/bin/python
import roomai
import roomai.common

class FiveCardStudPrivateState(roomai.common.AbstractPrivateState):
    """
    """
    all_hand_cards    = None

    def __deepcopy__(self, memodict={}):
        """

        Args:
            memodict:

        Returns:

        """
        copyinstance = FiveCardStudPrivateState()
        if self.all_hand_cards is None:
            copyinstance.all_hand_cards = None
        else:
            copyinstance.all_hand_cards = [self.all_hand_cards[i].__deepcopy__() for i in range(len(self.all_hand_cards))]
        return copyinstance