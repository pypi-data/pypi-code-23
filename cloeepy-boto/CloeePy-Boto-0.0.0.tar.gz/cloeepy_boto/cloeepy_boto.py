import sys
import boto3
from logging import Logger

class CloeePyBoto(object):
    def __init__(self, config:dict, log:Logger):
        # create copy of config
        params = config.copy()

        # create session
        log.info("Creating Boto Session")
        try:
            self.session = boto3.Session()
        except Exception as e:
            log.error(e.__str__())
            sys.exit(1)
        else:
            log.info("Successfully Created Boto Session")

        # set pluginNamespace
        self._namespace = "boto"
        if "pluginNamespace" in params:
            self._namespace = params["pluginNamespace"]
            del params["pluginNamespace"]

    def get_namespace(self):
        return self._namespace

    def get_value(self):
        return self.session
