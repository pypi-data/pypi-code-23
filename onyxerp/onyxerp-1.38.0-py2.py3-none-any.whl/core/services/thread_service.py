import threading
from concurrent.futures import ThreadPoolExecutor

from django.db import connection


class ThreadService(threading.Thread):
    """
    ThreadService
    """
    __target = None
    __kwargs = dict()
    __app = object

    def __init__(self, callback, app: object, **keywargs):
        super(ThreadService, self).__init__()
        self.__target = callback
        self.__kwargs = keywargs
        self.__app = app
        self.__kwargs['thread_pooler'] = ThreadPoolExecutor(max_workers=10)

    def run(self):
        """

        :return:
        """
        self.__target(**self.__kwargs)
        connection.close()
        self.__app['log'].info("Background thread finished!")
        return None

    def start(self):
        """

        :return:
        """
        self.__app['log'].info("Background thread started!")
        return super(ThreadService, self).start()
