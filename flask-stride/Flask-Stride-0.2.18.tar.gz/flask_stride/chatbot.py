from .module import Module

class ChatBot(Module):
    type = 'chat:bot'

    def __init__(self, key, mention_path=None, direct_message_path=None):
        super().__init__(key)
        if mention_path is not None:
            self.add_property('mention', {'url': mention_path})
        if direct_message_path is not None:
            self.add_property('directMessage', {'url': direct_message_path})
