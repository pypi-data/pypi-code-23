"""
hudai.resources.company_industry
"""
from ..helpers.resource import Resource


class CompanyIndustryResource(Resource):
    def __init__(self, client):
        Resource.__init__(
            self, client, base_path='/companies/{company_id}/industries')
        self.resource_name = 'CompanyIndustry'

    def list(self, company_id, page=None):
        query_params = self._set_limit_offset({'page': page})

        return self.http_get('/', params={'company_id': company_id},
                             query_params=query_params)

    def create(self, company_id, industry_id):
        return self.http_post('/', params={'company_id': company_id},
                              data={'industry_id': industry_id})

    def fetch(self, company_id, industry_id):
        return self.http_get('/{industry_id}',
                             params={'company_id': company_id, 'industry_id': industry_id})

    def delete(self, company_id, industry_id):
        return self.http_delete('/{industry_id}',
                                params={'company_id': company_id, 'industry_id': industry_id})
