#!/bin/python
import roomai.common

class KuhnPokerPublicState(roomai.common.AbstractPublicState):
    '''
    The public state class of the KuhnPoker game
    '''
    def __init__(self):
        super(KuhnPokerPublicState,self).__init__()
        self.__first__                      = 0
        self.__epoch__                      = 0
        self.__action_history__                = []

    def __get_first__(self):    return self.__first__
    first = property(__get_first__, doc="players[first] is expected to take an action")

    def __get_epoch(self):  return self.__epoch__
    epoch = property(__get_epoch)


    def __deepcopy__(self, memodict={}, newinstance = None):
        if newinstance is None:
            newinstance = KuhnPokerPublicState()
        newinstance = super(KuhnPokerPublicState, self).__deepcopy__(newinstance=newinstance)

        newinstance.__first__ = self.first
        newinstance.__epoch__ = self.epoch
        return newinstance

