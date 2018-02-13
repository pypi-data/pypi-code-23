"""
hudai.resources.stock_alert
"""
from ..helpers.resource import Resource


class StockAlertResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/companies/stock-alerts')
        self.resource_name = 'StockAlert'

    def list(self,
             company_id=None,
             occurring_before=None,
             occurring_after=None,
             page=None):
        query_params = self._set_limit_offset({
            'company_id': company_id,
            'occurring_before': occurring_before,
            'occurring_after': occurring_after,
            'page': page
        })

        return self.http_get('/', query_params=query_params)

    def create(self,
               company_id=None,
               first_value=None,
               first_value_occurred_at=None,
               second_value=None,
               second_value_occurred_at=None):
        return self.http_post('/',
                              data={'company_id': company_id,
                                    'first_value': first_value,
                                    'first_value_occurred_at': first_value_occurred_at,
                                    'second_value': second_value,
                                    'second_value_occurred_at': second_value_occurred_at})

    def fetch(self, entity_id):
        return self.http_get('/{id}', params={'id': entity_id})

    def delete(self, entity_id):
        return self.http_delete('/{id}', params={'id': entity_id})
