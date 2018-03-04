import json
import logging
from logging import Handler

import datetime
import requests


class ElsaHanlder(Handler):
    elsa_url: str = "http://elsa-col.ncloud.com/_store"

    def __init__(self, projectName: str, projectVersion: str = "1.0.0"):
        self.params: dict = {
            "projectName": projectName,
            "projectVersion": projectVersion,
            "body": None,
            "logLevel": None,
            "logType": None,
            "logSource": None,
        }
        Handler.__init__(self)
        self.projectName = projectName
        self.projectVersion = projectVersion

    def emit(self, record):
        try:
            self.acquire()
            msg = self.format(record)
            self.params["body"] = msg
            self.params["logLevel"] = self.level
            requests.post(ElsaHanlder.elsa_url, json=self.params)
        except Exception:
            self.handleError(record)
        finally:
            self.release()

    def __repr__(self):
        level = logging.getLevelName(self.level)
        name = __name__
        return '<%s %s(%s)>' % (self.__class__.__name__, name, level)


class ElsaJsonFormatter(logging.Formatter):
    def __init__(self, task_name=None):
        self.task_name = task_name
        logging.Formatter.__init__(self)

    def format(self, record):
        data = {
            "@message": record.msg,
            "@levelname": record.levelname,
            "@levelno": record.levelno,
            "@pathname": record.pathname,
            '@timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%fZ'),
            '@type': 'IronWorker'
        }

        if self.task_name:
            data['@task_name'] = self.task_name

        return json.dumps(data)