"""
hudai.resources.source
"""
from ..helpers.resource import Resource


class SourceResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/sources')
        self.resource_name = 'Source'

    def list(self, 
            domain=None,
            name=None, 
            min_reliability=None,
            max_reliability=None,
            article_id=None,
            page=None):
        return self._list(domain=domain, 
            name=name,
            min_reliability=min_reliability,
            max_reliability=max_reliability,
            article_id=article_id,
            page=page)

    def create(self,
            domain,  
            name, 
            reliability_score=None, 
            description=None, 
            language=None, 
            country=None):
        return self._create(domain=domain, 
            name=name, 
            reliability_score=reliability_score,
            description=description,
            language=language,
            country=country)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, 
            entity_id,
            domain=None,  
            name=None, 
            reliability_score=None, 
            description=None, 
            language=None, 
            country=None):
        return self._update(entity_id,
            domain=domain, 
            name=name,  
            reliability_score=reliability_score,
            description=description,
            language=language,
            country=country)

    def delete(self, entity_id):
        return self._delete(entity_id)
        