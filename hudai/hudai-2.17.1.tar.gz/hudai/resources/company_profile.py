"""
hudai.resources.company_profile
"""
from ..helpers.resource import Resource


class CompanyProfileResource(Resource):
    def __init__(self, client):
        Resource.__init__(
            self, client, base_path='/companies/{company_id}/profiles')
        self.resource_name = 'CompanyProfile'

    def fetch(self, company_id):
        return self.http_get(
            '/',
            params={
                'company_id': company_id
            }
        )
