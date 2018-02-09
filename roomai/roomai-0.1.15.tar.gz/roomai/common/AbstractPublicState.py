#!/bin/python
#coding=utf8

import roomai
import roomai.common
logger = roomai.get_logger()



######################################################################### Basic Concepts #####################################################
class AbstractPublicState(object):
    '''
    The abstract class of the public state. The information in the public state is public to every player
    '''
    def __init__(self):
        self.__turn__            = None
        self.__action_history__  = []

        self.__is_terminal__     = False
        self.__scores__          = None

    def __get_turn__(self): return self.__turn__
    turn = property(__get_turn__, doc = "The players[turn] is expected to take an action.")

    def __get_action_history__(self):   return tuple(self.__action_history__)
    action_history = property(__get_action_history__, doc = "The action_history so far. For example, action_history = [(0, roomai.kuhn.KuhnAction.lookup(\"check\"),(1,roomai.kuhn.KuhnAction.lookup(\"bet\")].\n"
                                                            "The format of the item in action_history is (person_id, action)")

    def __get_is_terminal__(self):   return  self.__is_terminal__
    is_terminal = property(__get_is_terminal__,doc = "is_terminal = True means the game is over. At this time, scores is not None, scores = [float0,float1,...] for player0, player1,... For example, scores = [-1,2,-1].\n"
                                                     "is_terminal = False, the scores is None.")

    def __get_scores__(self):   return self.__scores__
    scores = property(__get_scores__, doc = "is_terminal = True means the game is over. At this time, scores is not None, scores = [float0,float1,...] for player0, player1,... For example, scores = [-1,3,-2].\n"
                                            "is_terminal = False, the scores is None.")

    def __deepcopy__(self, memodict={}, newinstance = None):
        if newinstance is None:
            newinstance = AbstractPublicState()

        newinstance.__turn__           = self.__turn__
        newinstance.__action_history__ = list(self.__action_history__)
        newinstance.__is_terminal__ = self.is_terminal
        if self.scores is None:
            newinstance.__scores__ = None
        else:
            newinstance.__scores__ = [score for score in self.scores]
        return newinstance