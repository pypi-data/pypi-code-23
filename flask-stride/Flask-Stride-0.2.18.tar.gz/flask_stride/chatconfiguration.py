from .module import Module

class ChatConfiguration(Module):
    type = 'chat:configuration'

    def __init__(self, key, page_url=None, page_target=None, externalpage_url=None, state_url=None):
        super().__init__(key)

        targets = [ page_url, page_target, externalpage_url ]

        non_null_targets = [ t for t in targets if t is not None ]

        num_targets = len(non_null_targets)
        if num_targets != 1:
            raise ValueError('Must have exactly 1 target. Received {}'.format(num_targets))

        if page_url is not None:
            self.add_property('page', {'url': page_url})

        if page_target is not None:
            self.add_property('page', {'url': page_target})

        if externalpage_url is not None:
            self.add_property('page', {'url': externalpage_url})

        if state_url is not None:
            self.add_property('state', {'url': state_url})
