#!/bin/python
# coding=utf8

import roomai
import roomai.common
from roomai.common import AbstractPersonState
from roomai.common import AbstractPublicState
from roomai.common import AbstractPrivateState
from roomai.common import Info

logger = roomai.get_logger()


class AbstractEnv(object):
    '''
    The abstract class of game environment
    '''

    def __init__(self, params=dict()):
        self.__params__ = dict(params)
        self.__public_state_history__ = []
        self.__person_states_history__ = []
        self.__private_state_history__ = []

        self.public_state = AbstractPublicState()
        self.person_states = [AbstractPersonState()]
        self.private_state = AbstractPrivateState()

    def __gen_infos__(self):

        num_players = len(self.person_states)
        __infos__ = [Info() for i in range(num_players)]

        for i in range(num_players):
            __infos__[i].__person_state__ = self.person_states[i]  # .__deepcopy__()
            __infos__[i].__public_state__ = self.public_state  # .__deepcopy__()

        return tuple(__infos__)

    def __gen_history__(self):

        if "backward_enable" not in self.__params__ or self.__params__["backward_enable"] == False:
            return

        self.__public_state_history__.append(self.public_state.__deepcopy__())
        self.__private_state_history__.append(self.private_state.__deepcopy__())
        self.__person_states_history__.append([person_state.__deepcopy__() for person_state in self.person_states])

    def init(self, params=dict()):
        '''
        Initialize the game environment 

        :param params:  
        :return:  infos, public_state, person_states, private_state
        '''

        raise ("The init function hasn't been implemented")

    def forward(self, action):
        """
        The game environment steps with the action taken by the current player

        :param action, chance_action
        :returns:infos, public_state, person_states, private_state
        """
        raise NotImplementedError("The forward hasn't been implemented")

    def backward(self):
        '''
        The game goes back to the previous states

        :returns:infos, public_state, person_states, private_state
        :raise:Env has reached the initialization state and can't go back further.
        '''

        if "backward_enable" not in self.__params__ or self.__params__["backward_enable"] == False:
            raise ValueError(
                "Env can't backward when params[\"backward_enable\"] = False. If you want to use this backward function, please env.init({\"backward_enable\":true,...})")

        if len(self.__public_state_history__) == 1:
            raise ValueError("Env has reached the initialization state and can't go back further. ")
        self.__public_state_history__.pop()
        self.__private_state_history__.pop()
        self.__person_states_history__.pop()

        p = len(self.__public_state_history__) - 1
        self.public_state = self.__public_state_history__[p].__deepcopy__()
        self.private_state = self.__private_state_history__[p].__deepcopy__()
        self.person_states = [person_state.__deepcopy__() for person_state in self.__person_states_history__[p]]

        infos = self.__gen_infos__()
        return infos, self.public_state, self.person_states, self.private_state

    def __deepcopy__(self, memodict={}, newinstance=None):
        if newinstance is None:
            newinstance = AbstractEnv()
        newinstance.__params__ = dict(self.__params__)
        newinstance.private_state = self.private_state.__deepcopy__()
        newinstance.public_state = self.public_state.__deepcopy__()
        newinstance.person_states = [pe.__deepcopy__() for pe in self.person_states]

        newinstance.__private_state_history__ = [pr.__deepcopy__() for pr in self.__private_state_history__]
        newinstance.__public_state_history__ = [pu.__deepcopy__() for pu in self.__public_state_history__]
        newinstance.__person_states_history__ = []
        if len(self.person_states) > 0:
            for i in range(len(self.person_states)):
                newinstance.__person_states_history__.append(
                    [pe.__deepcopy__() for pe in self.__person_states_history__[i]])

        return newinstance

    ### provide some util functions
    @classmethod
    def compete(cls, env, players):
        '''
        Use the game environment to hold a compete for the players

        :param env: The game environment
        :param players: The players
        :return: scores for the players
        '''
        raise NotImplementedError("The round function hasn't been implemented")

    @classmethod
    def is_action_valid(cls, action, public_state, person_state):
        '''
        Is the action valid given the public state and the person state

        :param action: 
        :param public_state: 
        :param person_state: 
        :return: A boolean variable indicating whether is the action valid 
        '''
        raise NotImplementedError("The is_action_valid function hasn't been implemented")

    @classmethod
    def available_actions(self, public_state, person_state):
        '''
        Generate all valid actions given the public state and the person state

        :param public_state: 
        :param person_state: 
        :return: A dict(action_key, action) contains all valid actions
        '''
        raise NotImplementedError("The available_actions function hasn't been implemented")