#!/bin/python
import roomai.common
import roomai.bridge

class BridgeAction(roomai.common.AbstractAction):
    '''
    The action of Bridge. There are two stages: bidding and playing. The actions are different in the different stages.\n
    \n\n
    ################ In the bidding stage  ################ \n
    The action key looks like "bidding_(option)_(point)_(suit)".\n
    The option is one of "bid","double","redouble" and "pass".\n
    When the option is "bid", the point and suit are the candidate point (one of "A","2","3","4","5","6" and "7")and suit (one of "NotTrump","Spade","Heart","Diamond" and "Club").\n
    When the option is "double" or "redouble" or "pass". No point and suit. The action key looks like bidding_option\n  
    The example of the Bridge action's usage in the bidding stage:\n
    >>action = roomai.bridge.BridgeAction.lookup("bidding_bid_A_Heart") \n
    ## We strongly recommend you to use the lookup fuction to get an action.\n
    >>action.key \n
    "bidding_bid_A_Heart"\n
    >>action.stage \n
    "bidding"\n
    >>action.bidding_option\n
    "bid"\n
    >>action.bidding_contract_point \n
    "A"\n
    >>action.bidding_contract_suit\n
    "Heart"\n
    \n
    >>action = roomai.bridge.BridgeAction.lookup("bidding_pass")\n
    >>action.bidding_option\n
    "pass"\n
    \n\n
    ################ In the playing stage  ################\n
    The action key looks like playing_(point)_(suit). The example of the Bridge action's usage in the playing stage:\n
    >> action = roomai.bridge.BridgeAction.lookup("playing_A_heart") \n
    >> action.key \n
    "playing_A_heart"\n
    >>action.stage \n
    "playing"\n
    >>action.playing_card.point\n
    "A"\n
    >>action.playing_card.point_rank\n
    12\n
    >>action.playing_card.suit\n
    "Heart"\n
    >>action.playing_card.suit_rank\n
    2\n
    '''

    def __init__(self, stage, bidding_option, bidding_pokercard, playing_pokercard):
        self.__stage__  = stage
        self.__bidding_option__               = bidding_option
        self.__bidding_pokercard__            = bidding_pokercard
        self.__playing_pokercard__            = playing_pokercard

        key = None
        if self.__stage__ == "bidding":
            if self.__bidding_option__ == "bid":
                key= "bidding_" + self.__bidding_option__+"_" + self.__bidding_pokercard__.key
            else:
                key = "bidding_" + self.__bidding_option__
        elif self.__stage__ == "playing":
            key = "playing_" + self.__playing_pokercard__.key
        else:
            raise ValueError("The stage param must be \"bidding\" or \"playing\"")

        super(BridgeAction, self).__init__(key=key)


    def __get_key__(self): return self.__key__
    key = property(__get_key__)
    '''
    The key of the Bridge action. For example, \n
    >>action = roomai.bridge.BridgeAction.lookup(\"bidding_bid_1_Heart\")\n
    >>action.key\n 
    \"bidding_bid_1_heart\"\n
    '''

    def __get_stage__(self): return self.__stage__
    stage = property(__get_stage__)
    '''
    The stage of Bridge. For example, \n
    >>action = room.bridge_BridgeAction.lookup(\"playing_A_Heart\")\n
    >>action.stage \n
    \"playing\"\n
    '''


    def __get_bidding_option__(self):   return self.__bidding_option__
    bidding_option = property(__get_bidding_option__)
    '''
    When stage = \"bidding\", the bidding_option is one of \"bid\",\"double\",\"redouble\" and \"pass\".\n
    When stage = \"playing\", the bidding_option is always None.
   '''

    def __get_bidding_card__(self): return self.__bidding_pokercard__
    bidding_card = property(__get_bidding_card__)
    '''
    The bidding_card is the card used for bidding in the bidding stage of Bridge.\n
    Valid points of bidding_card are \"A\",\"2\",\"3\",\"4\",\"5\",\"6\" and \"7\"). \n
    Valid suits of bidding_card are \"NotTrump\",\"Spade\",\"Heart\",\"Diamond\" and \"Club\".
    When stage = \"playing\", the bidding_card always be None.\n
    When stage = \"bidding\", and the bidding_option != \"bid\", the bidding_card always be None.\n
    When stage = \"bidding\", and the bidding_option = \"bid\", the bidding_card is the card used for bidding.\n
    Example of usage:\n
    >>action = roomai.bridge.BridgeAction.lookup(\"bidding_bid_A_NotTrump\")\n
    >>action.bidding_card.key\n
    \"A_NotTrump\"\n
    >>action.bidding_card.suit  \n
    \"NotTrump\"\n
    >>action.bidding_card.point_rank \n
    1\n
    >>action.playing_card.suit_rank \n
    4'''

    def __get_playing_card__(self): return self.__playing_pokercard__
    playing_card = property(__get_playing_card__)
    '''
    When stage = \"bidding\", the playing_card always be None\n
    When stage = \"playing\", the playing_card is the card in this Bridge action. For example, \n
    >>action = roomai.bridge.BridgeAction.lookup(\"playing_A_Heart\")\n
    >>action.playing_card.key \n
    \"A_Heart\"\n
    >>action.playing_card.point \n
    \"A\"\n
    >>action.playing_card.suit  \n
    \"Heart\"\n
    >>action.playing_card.point_rank \n
    12\n
    >>action.playing_card.suit_rank \n
    1
    '''


    def __deepcopy__(self, memodict={}, newinstance = None):
        return AllBridgeActions[self.key]

    @classmethod
    def lookup(self, key):
        '''
        lookup an action with the key
        
        :param key: the key of the targeted action
        :return: the action with this key
        '''
        if key not in AllBridgeActions:
            stage = "bidding"
            bidding_option =  None
            bidding_card   =  None
            playing_card   =  None

            if "bidding" in key:
                stage  = "bidding"
                lines  = key.split("_")
                bidding_option = lines[1]
                if bidding_option == "bid":
                    bidding_card   = roomai.bridge.AllBridgeBiddingPokerCards[lines[2]+"_" + lines[3]]
            elif "playing" in key:
                stage          = "playing"
                playing_card   = roomai.bridge.BridgeBiddingPokerCard.lookup(key.replace("playing_", ""))
            else:
                raise ValueError("%s is an invalid key"%(key))

            AllBridgeActions[key] = BridgeAction(stage, bidding_option, bidding_card, playing_card)
        return AllBridgeActions[key]


AllBridgeActions = dict()