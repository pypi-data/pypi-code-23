import roomai.common
from roomai.sevenking import SevenKingPokerCard

class SevenKingPublicState(roomai.common.AbstractPublicState):
    def __init__(self):
        super(SevenKingPublicState,self).__init__()
        self.__stage__            = None
        self.__num_normal_players__      = None
        self.__showed_cards__     = None
        self.__num_showed_cards__ = None
        self.__num_keep_cards__   = None
        self.__num_hand_cards__   = None
        self.__is_fold__          = None
        self.__num_fold__         = None
        self.__license_action__   = None

    def __get_stage__(self):    return self.__stage__
    stage = property(__get_stage__, doc="There are two stages in SevenKing. In the first stage(stage = 0), the player gets the same number of the poker cards after he takes an action (throws some cards)."+
                                        "In the second stage (stage=1), the player doesn't get the supplement. The player who firstly throws all his hand cards is the winner. ")


    def __get_num_normal_players__(self): return self.__num_normal_players__
    num_normal_players = property(__get_num_normal_players__, doc="The number of players in this game")


    def __get_showed_cards__(self):
        if self.__showed_cards__ is None:
            return None
        return tuple(self.__showed_cards__)
    showed_cards = property(__get_showed_cards__, doc="The poker cards have been thrown by the players and are public to all now."
                                                      "For example, showed_cards = [roomai.sevenking.SevenKingPokerCards.lookup(\"A_Spade\"),roomai.sevenking.SevenKingPokerCards.lookup(\"3_Heart\")]")


    def __get_num_showed_cards__(self):
        return self.__num_showed_cards__
    num_showed_cards = property(__get_num_showed_cards__, doc="The number of showed poker cards")

    def __get_num_hand_cards__(self):
        if self.__num_hand_cards__ is None:
            return None
        return tuple(self.__num_hand_cards__)
    num_hand_cards = property(__get_num_hand_cards__, doc="The number of cards in different players. For example, num_hand_cards = [3,5,2] denotes the player0 has 3 poker cards, the player1 has 5 poker cards and the player2 has 2 poker cards")

    def __get_is_fold__(self):
        if self.__is_fold__ is None:
            return None
        return tuple(self.__is_fold__)
    is_fold = property(__get_is_fold__, doc="is_fold is an array of which player has take the fold action. For example, is_fold = [true,true,false] denotes the player0 and player1 have taken the fold action")


    def __get_num_fold__(self):
        return self.__num_fold__
    num_fold = property(__get_num_fold__, doc="The number of players who has taken the fold action")


    def __get_license_action__(self):
        return self.__license_action__
    license_action = property(__get_license_action__, doc="Generally, the player need takes an action with the same pattern as the license action. Unless the player takes an action at the beginning of a round")

    def __deepcopy__(self, newinstance = None, memodict={}):
        if  newinstance is None:
            newinstance = SevenKingPublicState()
        newinstance   = super(SevenKingPublicState,self).__deepcopy__(newinstance = newinstance)

        newinstance.__stage__ = self.stage
        newinstance.__num_normal_players__ = self.num_normal_players

        if self.showed_cards is None:
            newinstance.__showed_cards = None
        else:
            newinstance.__showed_cards = [card.__deepcopy__() for card in self.showed_cards]

        newinstance.__num_showd_cards__ = self.num_showed_cards
        newinstance.__num_keep_cards__  = self.num_keep_cards
        newinstance.__num_hand_cards__  = self.num_hand_cards
        if self.is_fold is None:
            newinstance.__is_fold__ = None
        else:
            newinstance.__is_fold__         = list(self.__is_fold__)
        newinstance.__num_fold__  = self.num_fold
        if self.license_action is None:
            newinstance.__license_action = None
        else:
            newinstance.self.__license_action__  = self.license_action

        return newinstance