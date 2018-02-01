from russell.exceptions import *
from russell.client.base import RussellHttpClient
from russell.log import logger as russell_logger


class EnvClient(RussellHttpClient):
    """
    Client to interact with Env api
    """
    def __init__(self):
        self.url = "/env"
        super(EnvClient, self).__init__()

    def get_all(self):
        try:
            response = self.request("GET",
                                    self.url)
            return response
        except Exception as e:
            russell_logger.info("Error while retrieving env: {}".format(e.message))
            return {}
