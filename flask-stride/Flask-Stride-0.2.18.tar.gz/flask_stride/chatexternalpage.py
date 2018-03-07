from .module import Module

class ChatExternalPage(Module):
    type = 'chat:externalPage'

    def __init__(self, key, name, url, i18n=None):
        super().__init__(key)
        name_dict = {'value': name}
        if i18n is not None:
            name_dict['i18n'] = i18n
        self.add_property('name', name_dict)
        self.add_property('url', url)
