#!/bin/python
import roomai.common
import copy

class FiveCardStudPersonState(roomai.common.AbstractPersonState):
    """
    """
    id                = None
    available_actions = None

    first_hand_card   = None
    second_hand_card  = None
    third_hand_card   = None
    fourth_hand_card  = None
    fifth_hand_card   = None


    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        copyinstance    = FiveCardStudPersonState()
        copyinstance.id = self.id

        if self.available_actions is not None:
            copyinstance.available_actions = dict()
            for key in self.available_actions:
                copyinstance.available_actions[key] = self.available_actions[key].__deepcopy__()
        else:
            copyinstance.available_actions = None

        if self.first_hand_card is not None:
            copyinstance.first_hand_card = self.first_hand_card.__deepcopy__()
        else:
            copyinstance.first_hand_card = None

        if self.second_hand_card is not None:
            copyinstance.second_hand_card = self.second_hand_card.__deepcopy__()
        else:
            copyinstance.second_hand_card = None

        if self.third_hand_card is not None:
            copyinstance.third_hand_card = self.third_hand_card.__deepcopy__()
        else:
            copyinstance.third_hand_card = None

        if self.fourth_hand_card is not None:
            copyinstance.fourth_hand_card = self.fourth_hand_card.__deepcopy__()
        else:
            copyinstance.fourth_hand_card = None

        if self.fifth_hand_card is not None:
            copyinstance.fifth_hand_card = self.fifth_hand_card.__deepcopy__()
        else:
            copyinstance.fifth_hand_card = None


        return copyinstance
