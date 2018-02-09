#!/bin/python
import roomai.common

class KuhnPokerPrivateState(roomai.common.AbstractPrivateState):
    '''
    The private state class of KuhnPoker
    '''

    def __deepcopy__(self, memodict={}, newinstance = None):
        return AKuhnPokerPrivateState
AKuhnPokerPrivateState = KuhnPokerPrivateState()