from random_executor import RandomExecutor
from pddlsim.simulator import Simulator
import random
import copy

class AvoidReturn(RandomExecutor):
    def __init__(self,use_lapkt_successor=True):
        super(AvoidReturn, self).__init__(True,use_lapkt_successor)

    def initilize(self,services): 
        super(AvoidReturn, self).initilize(services)
        self.previous_state = None

    def next_action(self):
        '''
        save previous state after choosing next action
        '''
        next_action = super(AvoidReturn, self).next_action()
        self.previous_state = self.services.perception.get_state() 
        return next_action

    def remove_return_actions(self,options):
        if self.previous_state:            
            return filter(lambda option: self.services.action_simulator.next_state(option) != self.previous_state, options)
        return options

    def pick_from_many(self, options):
        options = self.remove_return_actions(options)
        return random.choice(options)
