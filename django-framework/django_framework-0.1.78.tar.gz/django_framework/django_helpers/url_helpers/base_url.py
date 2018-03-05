

class BaseURL(object):

    URL_PATTERNS = []
    
    @classmethod
    def get_urlpatterns(cls):
        '''Method called by load_urlpatterns, makes it more simpel to get model urlpatterns'''
        return cls.URL_PATTERNS
    