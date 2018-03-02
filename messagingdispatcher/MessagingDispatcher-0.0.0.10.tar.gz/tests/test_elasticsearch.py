import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../')
from messagingdispatcher.search.esclient import ElasticSearchDocumentModel, ElasticSearch
from messagingdispatcher.config import CONFIG
import uuid

class TestElasticSearch(unittest.TestCase):
    def setUp(self):
        self._new_doc = ElasticSearchDocumentModel(index='order', 
                                                   doc_type='default', 
                                                   doc_id='1', 
                                                   body={
                                                        "id": 15,
                                                        "customer_id": 35,
                                                        "order_status_id": 1,
                                                        "order_status_name": "Pending",
                                                        "pickup_date_time": "2015-11-28 16:30",
                                                        "driver_id": 0,
                                                        "driver_name": "Nick Chen {}".format(uuid.uuid4())
                                                    })

    def test_document_model(self):
        self.assertEqual(self._new_doc.index, 'order')
        self.assertEqual(self._new_doc.doc_type, 'default')
        self.assertEqual(self._new_doc.doc_id, '1')

    def test_upsert_document(self):
        print(CONFIG.get('elasticsearch_endpoint'))
        es = ElasticSearch(host=CONFIG.get('elasticsearch_endpoint'))
        result = es.upsert_document(self._new_doc)
        self.assertEqual(result.get('_shards').get('successful'), 1)