import logging

from .sdk import DataHubSDK

LOGGER = logging.getLogger(__name__)

class DataHub:
    def __init__(self, hostname, port):
        """Initialize DataHub client."""
        self.sdk = DataHubSDK(hostname = hostname, port = port)

    def switchScene(self, hub, pathname, data):
        default = { 'currentScene': 'default', 'delay': '0', 'status': '200', 'responseHeaders': {} }
        data = dict(default, **data)
        self.sdk.updateSceneByProjectIdAndDataId(projectId = hub, dataId = pathname, data = data)

    def switchAllScenes(self, hub, data):
        LOGGER.debug(hub, data)
        res = self.sdk.getDataListByProjectId(projectId = hub, data = data)
        for item in res['data']:
            dataId = item['pathname']
            self.sdk.updateSceneByProjectIdAndDataId(projectId = hub, dataId = dataId, data = data)

