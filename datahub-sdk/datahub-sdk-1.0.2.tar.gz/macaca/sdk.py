import json
import urllib
import urllib2
import logging

LOGGER = logging.getLogger(__name__)

class DataHubSDK:
    def __init__(self, protocol = 'http', hostname = '127.0.0.1', port = '5678'):
        """Initialize the DataHubSDK."""
        self.rootUrl = '{0}://{1}:{2}'.format(protocol, hostname, port)

    def updateSceneByProjectIdAndDataId(self, projectId, dataId, data):
        LOGGER.debug(projectId, dataId, data)
        res = self.getDataByProjectIdAndDataId(projectId, dataId)
        if not res['success']:
            return 'error'

        url = '{0}/api/data/{1}/{2}'.format(self.rootUrl, projectId, dataId)
        LOGGER.debug(url, data)

        headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
        req = urllib2.Request(url, urllib.urlencode(data), headers)
        response = urllib2.urlopen(req)
        res = json.loads(response.read())
        response.close()
        return res

    def getDataListByProjectId(self, projectId, data):
        url = '{0}/api/data/{1}'.format(self.rootUrl, projectId)
        LOGGER.debug(url, data)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        res = json.loads(response.read())
        return res

    def getDataByProjectIdAndDataId(self, projectId, dataId):
        url = '{0}/api/data/{1}/{2}'.format(self.rootUrl, projectId, dataId)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        res = json.loads(response.read())
        response.close()
        return res


