#!/bin/python
import roomai.common
import copy


class KuhnPokerChanceAction(roomai.common.AbstractAction):
    '''
    The KuhnPoker action used by the chance player. Example of usages:\n
    >> import roomai.kuhn\n
    >> action = roomai.kuhn.KuhnPokerChanceAction("0,1")\n
    >> action.key \n
    "0,1"\n
    >> action.number_for_player0\n
    0\n
    >> action.number_for_player1\n
    1\n
    '''

    def __init__(self, key):
        super(KuhnPokerChanceAction, self).__init__(key)
        self.__key__ = key
        n1_n2        = key.split(",")
        self.__number_for_player0 = int(n1_n2[0])
        self.__number_for_player1 = int(n1_n2[1])

    def __get_key__(self):
        return self.__key__
    key = property(__get_key__, doc="The key of the KuhnPokerChance action, for example, \"0,1\"")

    def __get_number_for_player0__(self):
        return self.__number_for_player0
    number_for_player0 = property(__get_number_for_player0__, doc = "The number of the players[0]")

    def __get_number_for_player1__(self):
        return self.__number_for_player1
    number_for_player1 = property(__get_number_for_player1__, doc = "The number of the players[1]")

    @classmethod
    def lookup(cls, key):
        return AllKuhnChanceActions[key]

    def __deepcopy__(self, memodict={}, newinstance=None):
        return KuhnPokerChanceAction.lookup(self.key)

AllKuhnChanceActions = {"0,1": KuhnPokerChanceAction("0,1"), \
                        "1,0": KuhnPokerChanceAction("1,0"),\
                        "0,2": KuhnPokerChanceAction("0,2"), \
                        "2,0": KuhnPokerChanceAction("2,0"), \
                        "1,2": KuhnPokerChanceAction("1,2"), \
                        "2,1": KuhnPokerChanceAction("2,1"),}


