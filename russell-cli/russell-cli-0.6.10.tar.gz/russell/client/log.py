# coding=utf-8
from enum import Enum

try:
    import _thread
except ImportError:
    import thread as _thread
import websocket
from russell.client.base import RussellHttpClient
from russell.manager.auth_config import AuthConfigManager
from russell.cli.utils import *
from russell.exceptions import *

SOCKET_STATE = Enum('State', 'INIT UPLOADING FINISH FAILED')


class LogClient(RussellHttpClient):

    def __init__(self):
        self.ws_url = "ws://{host}:{port}".format(host=russell.russell_fs_host,
                                                  port=russell.russell_fs_port)
        super(LogClient, self).__init__()

    def on_message(self, ws, message):
        if self.access_token.token != ws.header.get('access_token'):
            russell_logger.warning('token invalid')
        print(json.loads(message).get('data'))

    def on_error(self, ws, error):
        self.STATE = SOCKET_STATE.FAILED
        russell_logger.debug(str(error))
        raise Exception(str(error))

    def on_close(self, ws):
        russell_logger.debug('close connection to server')

    def on_open(self, ws):
        russell_logger.debug('setup connection to server')

    def get_logs(self, task_id, tail, follow):
        # websocket.enableTrace(True)
        web_socket = websocket.WebSocketApp(
            url=self.ws_url + "/log/{}/".format(task_id),
            # url=self.ws_url + "/log/{}/?access_token={}".format(task_id, self.access_token.token),
            header={
                'access_token': self.access_token.token,
                'tail': str(tail),
                'follow': str(follow)
            },
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        web_socket.on_open = self.on_open
        web_socket.run_forever()

    def get_state(self):
        return self.STATE
