#!/bin/python
import roomai.common

class BridgePublicState(roomai.common.AbstractPublicState):
    '''
    The public state of Bridge.

    The attributes whose names start with "bidding" are used in the bidding stage \n
    The attributes whose names start with "playing" are used in the playing stage\n
    '''

    def __init__(self):
        super(BridgePublicState, self).__init__()
        self.__stage__ = "bidding"

        #self.__bidding_candidate_contract_point__ = None
        #self.__bidding_candidate_contract_suit__ = None
        self.__bidding_candidate_contract_card__ = None
        self.__bidding_magnification__ = 1
        self.__bidding_last_bidder__ = None

        self.__playing_is_vulnerable__ = [False for i in range(4)]
        self.__playing_contract_card__ = None
        self.__playing_magnification__ = 1
        self.__playing_dealerid__ = -1
        self.__playing_cards_on_table__ = []
        self.__playing_card_turn__ = -1
        self.__playing_win_tricks_sofar__ = [0 for i in range(4)]

    def __deepcopy__(self, memodict={}, newinstance = None):
        if newinstance is None:
            newinstance = BridgePublicState()
        newinstance = super(BridgePublicState, self).__deepcopy__(newinstance=newinstance)

        newinstance.__stage__ = self.__stage__

        if self.__bidding_candidate_contract_card__ is not None:
            newinstance.__bidding_candidate_contract_card__ = self.__bidding_candidate_contract_card__.__deepcopy__()
        newinstance.__bidding_magnification__ = self.__bidding_magnification__
        newinstance.__bidding_last_bidder__   = self.__bidding_last_bidder__

        newinstance.__playing_is_vulnerable__ = [f for f in self.__playing_is_vulnerable__]
        if self.__playing_contract_card__ is not None:
            newinstance.__playing_contract_card__ = self.__playing_contract_card__.__deepcopy__()
        newinstance.__playing_magnification__    = self.__playing_magnification__
        newinstance.__playing_dealerid__         = self.__playing_dealerid__
        newinstance.__playing_cards_on_table__   = [c.__deepcopy__() for c in self.__playing_cards_on_table__]
        newinstance.__playing_card_turn__        = self.__playing_card_turn__
        newinstance.__playing_win_tricks_sofar__ = [trick for trick in self.__playing_win_tricks_sofar__]

        return newinstance

    def __get_stage__(self):    return self.__stage__

    stage = property(__get_stage__, doc=" There are two stages: \"bidding\" and \"playing\"")

    ################## bidding stage #####################
    def __get_bidding_candidate_contract_card__(self): return self.__bidding_candidate_contract_card__

    bidding_candidate_contract_card = property(__get_bidding_candidate_contract_card__,
                                               doc="The candidate contract card at the bidding stage. The candidate contract card is None (at beginning) or one of BridgeBiddingPokerCard.\n")

    def __get_bidding_magnification__(self):    return self.__bidding_magnification__

    bidding_magnification = property(__get_bidding_magnification__,
                                     doc="In the bidding stage, normally, the magnification = 1. The \"double\" action makes magnification = 2, and the \"redouble\" makes magnification = 4")

    def __get_bidding_last_bidder__(self):   return self.__bidding_last_bidder__

    bidding_last_bidder = property(__get_bidding_last_bidder__,
                                   doc="In the bidding stage, the last playerid who lastly takes the \"bid\" action. The bidding_last_bidder is one of roomai.bridge.Direction.north, roomai.bridge.Direction.east, roomai.bridge.Direction.south and roomai.bridge.Direction.west. \n"
                                       "For example, the bidding_last_bidder = roomai.bridge.Direction.west")

    ########################## playing stage ####################

    def __get_playing_contract_card__(self):    return self.__playing_contract_card__

    playing_contract_card = property(__get_playing_contract_card__,
                                      doc="The contract point at the playing stage. The contract card is one of BridgeBiddingCard")

    def __get_playing_dealerid__(self): return self.__playing_dealerid__

    playing_dealerid = property(__get_playing_dealerid__, doc="The players[playing_dealerid] is the dealer")

    def __get_playing_cards_on_table__(self):   return tuple(self.__playing_cards_on_table__)

    playing_cards_on_table = property(__get_playing_cards_on_table__,
                                      doc="The playing_cards_on_table is the cards so far in this pier. For example, playing_cards_on_table = [roomai.bridge.BridgePokerCard.lookup(\"A_Spade\"),roomai.bridge.BridgePokerCard.lookup(\"2_Spade\")] when two players have taken actions in this pier.")

    def __get_playing_real_turn__(self):    return self.__playing_card_turn__

    playing_card_turn = property(__get_playing_real_turn__,
                                 doc="The players[turn] uses the players[playing_card_turn]'s cards to take an action. In general, turn == playing_card_turn. When playing_card_turn = dummy, turn = playing_dealerid")

    def __get_playing_win_tricks_sofar__(self):    return self.__playing_win_tricks_sofar__

    playing_win_tricks_sofar = property(__get_playing_win_tricks_sofar__,
                                        doc="playing_win_tricks_sofar is the number of the win tricks. For example, playing_win_tricks_sofar = [1,2,1,2] means 1) that players[0] and players[2] win 1 trick, and 2) that players[1] and players[3] win 2 tricks.")

    def __get_playing_magnification__(self):    return self.__playing_magnification__

    playing_magnification = property(__get_playing_magnification__,
                                     doc="The playing_magnification will affect the final scores. In general, playing_magnification = 1. The valid double in the bidding stage will make playing_magnification = 2 and the valid redouble will make playing_magnification = 4\n")

    def __get_playing_is_vulnerable__(self): return self.__playing_is_vulnerable__

    playing_is_vulnerable = property(__get_playing_is_vulnerable__,
                                     doc="The playing_is_vulnerable will affect the final scores. In general, playing_is_vulnerable = [False,False,False,False].")
