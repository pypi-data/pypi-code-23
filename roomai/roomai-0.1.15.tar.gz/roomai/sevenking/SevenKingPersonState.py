#!/bin/python
import roomai.common
from roomai.sevenking import SevenKingPokerCard

AllPointRank2Cards = dict()
class SevenKingPersonState(roomai.common.AbstractPersonState):
    '''
    The person state of SevenKing 
    '''
    def __init__(self):
        super(SevenKingPersonState,self).__init__()
        self.__hand_cards__         = []
        self.__hand_cards_keyset__  = set()
        self.__hand_cards_key__     = ""

    def __get_hand_cards__(self):
        return tuple(self.__hand_cards__)
    hand_cards = property(__get_hand_cards__, doc="The hand cards of the person state. For example, hand_cards = [roomai.sevenking.SevenKingPokerCard.lookup(\"A_Spade\")] ")

    def __get_hand_cards_key__(self):
        return self.__hand_cards_key__
    hand_cards_key = property(__get_hand_cards_key__, doc="The hand cards key of the person state. For example, hand_cards_key  = \"3_Spade,A_Spade\"")

    def __get_hand_cards_keyset__(self):
        return frozenset(self.__hand_cards_keyset__)
    hand_cards_keyset = property(__get_hand_cards_keyset__, doc = "The set of the poker cards' key in the hand cards. For example, hand_cards_keyset={\"A_Spade\"}")


    def __add_card__(self, c):
        self.__hand_cards__.append(c)
        self.__hand_cards_keyset__.add(c.key)

        for j in range(len(self.__hand_cards)-1,0,-1):
            if SevenKingPokerCard.compare(self.__hand_cards__[j - 1], self.__hand_cards__[j]) > 0:
                tmp = self.__hand_cards__[j]
                self.__hand_cards__[j] = self.__hand_cards__[j-1]
                self.__hand_cards__[j-1] = tmp
            else:
                break

        self.__hand_cards_key = ",".join([c.key for c in self.__hand_cards__])

    def __add_cards__(self, cards):
        len1 = len(self.__hand_cards__)
        for c in cards:
            self.__hand_cards__.append(c)
            self.__hand_cards_keyset__.add(c.key)
        len2 = len(self.__hand_cards__)


        for i in range(len1,len2-1):
            for j in range(i,0,-1):
                if SevenKingPokerCard.compare(self.__hand_cards__[j-1], self.__hand_cards__[j]) > 0:
                    tmp      = self.__hand_cards__[j]
                    self.__hand_cards__[j] = self.__hand_cards__[j-1]
                    self.__hand_cards__[j-1] = tmp
                else:
                    break


        #self.__hand_cards.sort(cmp=SevenKingPokerCard.compare)
        self.__hand_cards_key__ = ",".join([c.key for c in self.__hand_cards__])



    def __del_card__(self, c):
        self.__hand_cards_keyset__.remove(c.key)

        tmp = self.__hand_cards__
        self.__hand_cards__ = []
        for i in range(len(tmp)):
            if c.key == tmp[i].key:
                continue
            self.__hand_cards__.append(tmp[i])
        self.__hand_cards_key__ = ",".join([c.key for c in self.__hand_cards__])


    def __del_cards__(self, cards):
        for c in cards:
            self.__hand_cards_keyset__.remove(c.key)

        tmp = self.__hand_cards__
        self.__hand_cards__ = []
        for i in range(len(tmp)):
            if tmp[i].key not in self.__hand_cards_keyset__:
                continue
            self.__hand_cards__.append(tmp[i])
        self.__hand_cards_key__ = ",".join([c.key for c in self.__hand_cards__])

    def __gen_pointrank2cards__(self):
        if self.__hand_cards_key__ in AllPointRank2Cards:
            return AllPointRank2Cards[self.__hand_cards_key__]
        else:
            point2cards = dict()
            for c in self.hand_cards:
                pointrank = c.point_rank
                if pointrank not in point2cards:
                    point2cards[pointrank] = []
                point2cards[pointrank].append(c)
            for p in point2cards:
                for i in range(len(point2cards[p])-1):
                    for j in range(i+1,len(point2cards[p])):
                        if SevenKingPokerCard.compare(point2cards[p][i],point2cards[p][j]) > 0:
                            tmp = point2cards[p][i]
                            point2cards[p][i] = point2cards[p][j]
                            point2cards[p][j] = tmp
                #point2cards[p].sort(cmp=SevenKingPokerCard.compare)

            AllPointRank2Cards[self.__hand_cards_key__] = point2cards
            return point2cards

    def __deepcopy__(self, memodict={}, newinstance = None):
        if newinstance is None:
            newinstance          = SevenKingPersonState()
        newinstance      = super(SevenKingPersonState, self).__deepcopy__(newinstance= newinstance)
        newinstance.__hand_cards__           = list(tuple(self.__hand_cards__))
        newinstance.__hand_cards_set__       = set(self.__hand_cards_keyset__)
        newinstance.__hand_cards_key__       = self.__hand_cards_key__
        return newinstance



