

instance = None

from django_framework.django_helpers.register_helpers import Registry

class UrlRegistry(Registry):
    REGISTRY_TYPE = 'URL'
    REGISTER = {}
    
    SHOULD_CHECK_TYPE = True
    
    @classmethod
    def set_instance(cls):
        if instance == None:
            global instance
            instance = UrlRegistry()


def register_url(cls, version = None):
    UrlRegistry.set_instance()
    instance.register(cls = cls)

def get_url(url_name): # converts string to cls
    
    return instance.get(name = url_name)
    
def get_url_name(url): # converts cls to a string
    return instance.get_name(cls = url)

def get_url_name_list(): # converts cls to a string
    return instance.get_name_list()

