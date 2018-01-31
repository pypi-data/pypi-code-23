import elasticsearch

INDEX = "slackr"
DOC_TYPE = "json"


class Connection():

    def __init__(self):
        self.index = None
        self.es = elasticsearch.Elasticsearch()
        self.checkConnection()
        self.deleteIndex()
        self.createIndex()

    def checkConnection(self):
        try:
            self.es.info()
        except elasticsearch.ConnectionError:
            raise elasticsearch.ConnectionError("Cannot find Elastic Search process")
        except Exception, e:
            raise EnvironmentError("Unknown Exception: %s" % e)

    def createIndex(self):
        '''
        The first event
        :param event: 
        :return: 
        '''
        print("Creating Elastic Search Index --> %s" % INDEX)
        try:
            self.es.indices.create(INDEX, ignore=[400, 404], timeout=30)
        except elasticsearch.ElasticsearchException, e:
            raise e

    def deleteIndex(self):
        try:
            self.es.indices.delete(INDEX, ignore=[400, 404])
        except Exception, e:
            raise e

    def sendEventToElastic(self, event):
        # Send events to Elastic
        try:
            self.es.index(index=INDEX, doc_type=DOC_TYPE, body=event)
        except elasticsearch.TransportError, e:
            if e.status_code == 409:
                self.createIndex()
        except elasticsearch.ElasticsearchException, e:
            print(e)
            raise elasticsearch.ElasticsearchException()
        except Exception:
            raise Exception


