from activecampaign3.resource import Resource

class EcommerceConnection(Resource):
    _resource_path = 'connections'
    _valid_search_params = ['service', 'externalid']
    _valid_save_params = "service externalid name logoUrl linkUrl".split()
