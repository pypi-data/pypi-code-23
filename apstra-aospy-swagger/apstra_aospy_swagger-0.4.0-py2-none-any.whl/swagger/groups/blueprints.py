from aospy.swagger.indexer import Indexer, IndexItem

class BlueprintItem(IndexItem):

    def query_qe(self, queryexpr):
        got = self.api.post(self.url + "/qe", json={'query': queryexpr.strip()})
        if not got.ok:
            raise RuntimeError(
                'unable to execute query: %s' % got.reason,
                self, got)

        return got.json()['items']

    def query_ql(self, queryexpr, **queryvars):
        query = dict(query=queryexpr.strip())
        if queryvars:
            query['variables'] = queryvars

        got = self.api.post(self.url + "/ql", json=query)
        if not got.ok:
            raise RuntimeError(
                'unable to execute query: %s' % got.reason,
                self, got)

        return got.json()['data']


class Blueprints(Indexer):
    def __init__(self, aos):
        rqst = aos.request.blueprints.get_api_blueprints
        super(Blueprints, self).__init__(rqst, index_item_type=BlueprintItem)
        self.run()
