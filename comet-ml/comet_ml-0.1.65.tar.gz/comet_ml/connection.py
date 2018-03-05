from __future__ import print_function

import json
import os
import sys
import threading
import time

import requests

import comet_ml
import websocket
from comet_ml import config
from comet_ml.json_encoder import NestedEncoder

server_address = os.environ.get('COMET_URL_OVERRIDE',
                                'https://www.comet.ml/clientlib/')
TIMEOUT = 10


class RestServerConnection(object):
    """
    A static class that handles the connection with the server.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_run_id(api_key, project_name):
        """
        Gets a new run id from the server.
        :param api_key: user's API key
        :return: run_id - String
        """
        endpoint_url = server_address + "logger/add/run"
        headers = {'Content-Type': 'application/json;charset=utf-8'}

        try:
            version_num = comet_ml.__version__
        except NameError:
            version_num = None

        payload = {
            "apiKey": api_key,
            "local_timestamp": int(time.time() * 1000),
            "projectName": project_name,
            "libVersion": version_num
        }
        r = requests.post(
            url=endpoint_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=TIMEOUT)

        if r.status_code != 200:
            raise ValueError(r.content)

        res_body = json.loads(r.content.decode('utf-8'))

        return RestServerConnection._parse_run_id_res_body(res_body)

    @staticmethod
    def _parse_run_id_res_body(res_body):
        run_id_server = res_body["runId"]
        ws_full_url = res_body["ws_full_url"]

        project_id = res_body.get("project_id", None)

        is_github = bool(res_body.get("githubEnabled", False))

        focus_link = res_body.get("focusUrl", None)

        if "msg" in res_body:
            print("\n" + res_body["msg"])

        return run_id_server, ws_full_url, project_id, is_github, focus_link


class Reporting(object):
    def __init__(self):
        pass

    @staticmethod
    def report(event_name=None,
               api_key=None,
               run_id=None,
               experiment_key=None,
               project_id=None,
               err_msg=None,
               is_alive=None):

        try:
            if event_name is not None:
                endpoint_url = server_address + "notify"
                headers = {'Content-Type': 'application/json;charset=utf-8'}

                payload = {
                    "event_name": event_name,
                    "api_key": api_key,
                    "run_id": run_id,
                    "experiment_key": experiment_key,
                    "project_id": project_id,
                    "err_msg": err_msg,
                    "timestamp": int(time.time() * 1000)
                }

                r = requests.post(
                    url=endpoint_url,
                    data=json.dumps(payload),
                    headers=headers,
                    timeout=TIMEOUT / 2)

        except Exception as e:
            pass


class WebSocketConnection(threading.Thread):
    """
    Handles the ongoing connection to the server via Web Sockets.
    """

    def __init__(self, ws_server_address):
        threading.Thread.__init__(self)
        self.priority = 0.2
        self.daemon = True

        if config.DEBUG:
            websocket.enableTrace(True)

        self.address = ws_server_address
        self.ws = self.connect_ws(self.address)

    def is_connected(self):
        if self.ws.sock is not None:
            return self.ws.sock.connected

        return False

    def connect_ws(self, ws_server_address):
        ws = websocket.WebSocketApp(
            ws_server_address,
            on_message=WebSocketConnection.on_message,
            on_error=WebSocketConnection.on_error,
            on_close=WebSocketConnection.on_close)
        ws.on_open = WebSocketConnection.on_open
        return ws

    def run(self):
        while True:
            try:
                self.ws.run_forever()
            except Exception as e:
                if sys is not None and config.DEBUG:
                    print(e, file=sys.stderr)

    def send(self, messages):
        """ Encode the messages into JSON and send them on the websocket
        connection
        """
        data = self._encode(messages)
        self._send(data)

    def _encode(self, messages):
        """ Encode a list of messages into JSON
        """
        messages_arr = []
        for message in messages:
            payload = {}
            # make sure connection is actually alive
            if message.stdout is not None:
                payload["stdout"] = message
            else:
                payload["log_data"] = message

            messages_arr.append(payload)

        data = json.dumps(messages_arr, cls=NestedEncoder, allow_nan=False)
        return data

    def _send(self, data):
        if self.ws.sock:
            self.ws.send(data)
            return
        else:
            self.wait_for_connection()

    def wait_for_connection(self, num_of_tries=5):
        """
        waits for the server connection
        Args:
            num_of_tries: number of times to try connecting before giving up

        Returns: True if succeeded to connect.

        """
        if not self.is_connected():
            counter = 0

            while not self.is_connected() and counter < num_of_tries:
                time.sleep(2)
                counter += 1

            if not self.is_connected():
                raise ValueError(
                    "Could not connect to server after multiple tries. ")

        return True

    @staticmethod
    def on_open(ws):
        if config.DEBUG:
            print("Socket connection open")

    @staticmethod
    def on_message(ws, message):
        if config.DEBUG:
            print(message)

    @staticmethod
    def on_error(ws, error):
        error_type_str = type(error).__name__
        ignores = [
            'WebSocketBadStatusException', 'error',
            'WebSocketConnectionClosedException', 'ConnectionRefusedError',
            'BrokenPipeError'
        ]

        if not config.DEBUG and error_type_str in ignores:
            return

        print(error)

    @staticmethod
    def on_close(ws):
        if config.DEBUG:
            print("### closed ###")
