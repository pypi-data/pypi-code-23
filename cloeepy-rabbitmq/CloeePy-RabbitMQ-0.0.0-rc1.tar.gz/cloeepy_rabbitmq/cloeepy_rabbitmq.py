import os
import sys
import pika
from logging import Logger

class CloeePyRabbitMQ(object):
    def __init__(self, config:dict, log:Logger):
        params = config.copy()

        # set pluginNamespace
        self._namespace = "rabbitmq"
        if "pluginNamespace" in params:
            self._namespace = params["pluginNamespace"]
            del params["pluginNamespace"]

        # use environment variables for username and password if they exist
        if 'CLOEEPY_RABBITMQ_USERNAME' in os.environ and 'CLOEEPY_RABBITMQ_PASSWORD' in os.environ:
            log.info("RabbitMQ: Using credentials defined in environment")
            params["credentials"]["username"] = os.environ["CLOEEPY_RABBITMQ_USERNAME"]
            params["credentials"]["password"] = os.environ["CLOEEPY_RABBITMQ_PASSWORD"]

        # instantiate ConnectionParameters
        conn_params = pika.ConnectionParameters(
            **params["connection"],
            credentials= pika.credentials.PlainCredentials(**params["credentials"]),
        )

        # dial RabbitMQ
        log.info("Dialing RabbitMQ")
        connection_class = getattr(pika, params["connectionClass"])
        self.conn = connection_class(conn_params)
        if self.conn.is_open:
            log.info("Successfully connected to RabbitMQ")
        else:
            log.error("An error occurred when attempting to connect to RabbitMQ")
            sys.exit(1)

    def get_namespace(self):
        return self._namespace

    def get_value(self):
        return self.conn
