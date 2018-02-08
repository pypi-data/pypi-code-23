#!/bin/python
#coding:utf-8

import roomai.common
import copy

class StageSpace:
    firstStage  = 1
    secondStage = 2
    thirdStage  = 3
    fourthStage = 4


AllCardsPattern = dict()
#0     1           2       3           4                                    5     6
#name, isStraight, isPair, isSameSuit, [SizeOfPair1, SizeOfPair2,..](desc), rank, cards
AllCardsPattern["Straight_SameSuit"] = \
["Straight_SameSuit",   True,  False, True,  [],         100]
AllCardsPattern["4_1"] = \
["4_1",                 False, True,  False, [4,1],      98]
AllCardsPattern["3_2"] = \
["3_2",                 False, True,  False, [3,2],      97]
AllCardsPattern["SameSuit"] = \
["SameSuit",            False, False, True,  [],         96]
AllCardsPattern["Straight_DiffSuit"] = \
["Straight_DiffSuit",   True,  False, False, [],         95]
AllCardsPattern["3_1_1"] = \
["3_1_1",               False, True,  False, [3,1,1],    94]
AllCardsPattern["2_2_1"] = \
["2_2_1",               False, True,  False, [2,2,1],    93]
AllCardsPattern["2_1_1_1"] = \
["2_1_1_1",             False, True,  False, [2,1,1,1],  92]
AllCardsPattern["1_1_1_1_1"] = \
["1_1_1_1_1",           False, True,  False, [1,1,1,1,1],91]






