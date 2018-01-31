"""
hudai.resources.person
"""
from ..helpers.resource import Resource


class PersonResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/people')
        self.resource_name = 'Person'

    def list(self, name=None, title=None, term=None, twitter_handle=None, company_id=None, page=None):
        return self._list(name=name,
                          title=title,
                          term=term,
                          twitter_handle=twitter_handle,
                          company_id=company_id,
                          page=page)

    def create(self, name=None, title=None, twitter_handle=None, linked_in_url=None, image_url=None, source=None, company_id=None):
        return self._create(name=name,
                            title=title,
                            twitter_handle=twitter_handle,
                            linked_in_url=linked_in_url,
                            image_url=image_url,
                            source=source,
                            company_id=company_id)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id, name=None, title=None, twitter_handle=None, linked_in_url=None, image_url=None, source=None, company_id=None):
        return self._update(entity_id,
                            name=name,
                            title=title,
                            twitter_handle=twitter_handle,
                            linked_in_url=linked_in_url,
                            image_url=image_url,
                            source=source,
                            company_id=company_id)

    def delete(self, entity_id):
        return self._delete(entity_id)

    def quotes(self, entity_id, page=None):
        return self.http_get('/{id}/quotes',
                             params={'id': entity_id, 'page': page})
