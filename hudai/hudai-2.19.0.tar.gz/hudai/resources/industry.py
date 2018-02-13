"""
hudai.resources.industry
"""
from ..helpers.resource import Resource


class IndustryResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/companies/industries')
        self.resource_name = 'Industry'

    def list(self, page=None):
        return self._list(page=page)

    def create(self,
               name=None,
               text_corpus=None):
        return self._create(name=name,
                            text_corpus=text_corpus)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id,
               name=None,
               text_corpus=None):
        return self._update(entity_id,
                            name=name,
                            text_corpus=text_corpus)

    def delete(self, entity_id):
        return self._delete(entity_id)
