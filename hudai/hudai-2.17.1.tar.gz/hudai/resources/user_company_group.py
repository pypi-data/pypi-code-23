"""
hudai.resources.user_company_group
"""
from ..helpers.resource import Resource


class UserCompanyGroupResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/companies/groups')
        self.resource_name = 'UserCompanyGroup'

    def list(self, user_id=None, name=None, page=None):
        return self._list(user_id=user_id, name=name, page=page)

    def create(self, user_id=None, name=None):
        return self._create(user_id=user_id, name=name)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id, user_id=None, name=None):
        return self._update(entity_id, user_id=user_id, name=name)

    def delete(self, entity_id):
        return self._delete(entity_id)

    def add_company(self, group_id, company_id):
        return self.http_post('/{group_id}/companies',
                                params={'group_id': group_id},
                                data={'company_id': company_id})

    def remove_company(self, group_id, company_id):
        return self.http_delete('/{group_id}/companies',
                                params={'group_id': group_id},
                                data={'company_id': company_id})
