"""
hudai.resources.user_source
"""
from ..helpers.resource import Resource


class UserSourceResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/sources/users')
        self.resource_name = 'UserSource'

    def list(self, user_id=None, source_id=None, page=None):
        return self._list(user_id=user_id, source_id=name, page=page)

    def create(self, user_id, source_id, reliability_score):
        return self._create(user_id=user_id, source_id=source_id, reliability_score=reliability_score)

    def update(self, user_id, source_id, reliability_score=None):
        return self.http_put('/', 
            data={
                'user_id': user_id,
                'source_id': source_id,
                'reliability_score': reliability_score
            })

    def delete(self, user_id, source_id):
        return self.http_delete('/', query_params={'user_id': user_id, 'source_id': source_id})