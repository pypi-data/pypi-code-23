from .module import Module

class ChatSidebar(Module):
    type = 'chat:sidebar'

    def __init__(self, key, name, url, icon_1x=None, icon_2x=None, i18n=None, weight=None, conditions=None):
        super().__init__(key)
        name_dict = { 'value': name }
        if i18n is not None:
            name_dict['i18n'] = i18n
        self.add_property('name', name_dict)

        self.add_property('url', url)

        if icon_1x is not None:
            icon_dict = { 'url': icon_1x, 'url@2x': icon_2x }
            self.add_property('icon', icon_dict)
        
        if weight is not None:
            self.add_property('weight', weight)
        
        if conditions is not None:
            self.add_property('conditions', conditions)
