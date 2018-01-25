"""
hudai.resources.article_key_term
"""
from ..helpers.resource import Resource


class ArticleCompanyResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/articles/companies')
        self.resource_name = 'ArticleCompany'

    def list(self, article_id=None, company_id=None, page=None):
        return self._list(
            article_id=article_id,
            company_id=company_id,
            page=page
        )

    def create(self, article_id, company_id):
        return self._create(
            article_id=article_id,
            company_id=company_id
        )

    def delete(self, article_id, company_id):
        return self.http_delete('/',
                                query_params={
                                    'article_id': article_id,
                                    'company_id': company_id
                                })
