import roomai.common
from roomai.sevenking import SevenKingPokerCard


class SevenKingPrivateState(roomai.common.AbstractPrivateState):
    '''
    The private state of SevenKing
    '''
    def __init__(self):
        super(SevenKingPrivateState,self).__init__()
        self.__keep_cards__   = []

    def __get_keep_cards__(self):
        return tuple(self.__keep_cards__)
    keep_cards = property(__get_keep_cards__, doc="The keep cards")

    def __deepcopy__(self, newinstance = None, memodict={}):
        if newinstance is None:
            newinstance = SevenKingPrivateState()
        newinstance                = super(SevenKingPrivateState,self).__deepcopy__(newinstance = newinstance)
        newinstance.__keep_cards__ =  [card.__deepcopy__() for card in self.keep_cards   ]
        return newinstance