from .module import Module

class ChatActionTarget(Module):
    type = 'chat:actionTarget'

    # Target types allowed for "static" actions
    valid_targets = [ 'callService', 'openConfiguration', 'openDialog', 'openExternalPage', 'openSidebar' ]

    def __init__(self, key, target, parameters={}):
        if target not in self.valid_targets:
            raise ValueError('Invalid Action Target: '+target)

        super().__init__(key)

        target_parameters = []
        if target == 'callService':
            target_parameters = ["url"]
        elif target == 'openConfiguration':
            target_parameters = ["key"]
        elif target == 'openDialog':
            target_parameters = ["key"]
        elif target == 'openExternalPage':
            target_parameters = ["key"]
        elif target == 'openSidebar':
            target_parameters = ["key"]

        params = {}

        for tp in target_parameters:
            params[tp] = parameters[tp]

        self.add_property(target, params)