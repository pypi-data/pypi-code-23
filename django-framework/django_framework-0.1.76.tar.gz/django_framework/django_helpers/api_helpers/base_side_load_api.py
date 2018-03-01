

from base_api import BaseAPI

# the following function will account for local overrides if they exist!!
from django_framework.base_framework.model_api.api import _models_with_cache


class BaseSideLoadApi(BaseAPI):
    '''THe goal of this API class is to make it to make multiple "fetches" in one go! ideally in heirachal information format
    or flat your choice
    '''
    
    MODEL_NAMES = [] # should be a list! ['gateway', 'datastream']
    RESPONSE_TYPE = 'conglomerate'
    
    def __init__(self, request, admin = False):
        self.request = request
        self.admin = admin # this may not work as well with admin = True but your choice!!

        super(BaseSideLoadApi, self).__init__(request= self.request, admin = admin)
        

    def get_data_from_many_models(self):
        '''Grab the proper ModelApi.  The reason we use _models_with_cache is
        so we can get from cache if needed and also if there are any local model api overrides
        '''
        responses = []
        for model_name in self.MODEL_NAMES:
            response = _models_with_cache(request = self.request, model_name_slug = model_name, admin = self.admin)
            responses.append(response)
        self.set_response(response = responses, response_type = self.RESPONSE_TYPE)

##### SAMPLE CORRESPONDING URL for easy peasyiness
# # # 
# # # from api import SideLoadApi
# # #  
# # # @api_view(["GET"])
# # # @try_except_response
# # # def gateway_server_models(request):
# # #     api = SideLoadApi(request = request, admin = False)
# # #     api.get_data_from_many_models()
# # #     response = api.get_response()
# # #     return Response(response, status = 200)
# # # 
# # # class SideLoadURL(BaseURL):
# # #     
# # #     URL_PATTERNS = [
# # #         regex_url.url('gateway_server/special/$', gateway_server_models, name = 'gateway_server')
# # #     
# # #     ]
# # #     
# # # register_url(SideLoadURL)