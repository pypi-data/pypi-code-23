from .module import Module

class ChatGlance(Module):
    type = 'chat:glance'

    def __init__(self, key, name, icon_1x, icon_2x, i18n=None, target=None, query_url=None, weight=None, conditions=None):
        super().__init__(key)
        name_dict = { 'value': name }
        if i18n is not None:
            name_dict['i18n'] = i18n
        self.add_property('name', name_dict)

        icon_dict = { 'url': icon_1x, 'url@2x': icon_2x }
        self.add_property('icon', icon_dict)

        if query_url is not None:
            self.add_property('queryUrl', query_url)
        
        if target is not None:
            self.add_property('target', target)
        
        if weight is not None:
            self.add_property('weight', weight)
        
        if conditions is not None:
            self.add_property('conditions', conditions)
