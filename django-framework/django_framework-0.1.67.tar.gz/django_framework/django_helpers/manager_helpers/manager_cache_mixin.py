from django_framework.django_helpers.cache_helpers import ManagerCache, APICache
from django_framework.django_helpers.model_helpers.model_registry import get_model_name


class ManagerCacheMixin(object):
    '''Note that in this version of base_manager, it must also use this Mixin'''
    
    @classmethod
    def _clear_cache(cls, models):
        '''We are in the process of updating this such that the profile_models will be returning profile_uuids instead
        this is a work in progress and will not be full implemented till a later date.  TODO!  Jan 05 2018
        Jan 05 2018 it currently will accept either as profiles: model, or profile_uuid, see try catch below
        '''
        profile_models = cls.get_related_model(models = models, relationship_name = 'profile')

        full_name, model_name = get_model_name(cls.Model)
        if len(profile_models) > 10:
            api_cache = APICache(model_name = model_name, token = None, url = '')
            api_cache.clear_level(level = 2, token = None)
        else:
            
            for profile in profile_models:
                try:
                    profile_uuid = profile.uuid

                except: # we are trying to swap to a profile_uuid version...
                    profile_uuid = profile
                
                api_cache = APICache(model_name = model_name, token = profile_uuid, url = '')
                response = api_cache.clear_level(level = 1, token = profile_uuid)
                
                
    @classmethod
    def get_cache(cls, key):
        return ManagerCache(model_name = cls.Model.__name__, key = key)
