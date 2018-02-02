import json
import logging
import time

import six

if six.PY2:
    from urlparse import urlunparse
    from Queue import Queue, Full
else:
    from urllib.parse import urlunparse
    from queue import Queue, Full

import requests
from threading import Thread

from .base import BaseClient
from overlock.state import client_state


logger = logging.getLogger(__name__)


class OverlockRequestsClient(BaseClient):
    """Connects to the agent over an http socket
    """

    def __init__(self, max_queue_size=500):
        self._port = client_state.agent_port
        self._host = client_state.agent_host
        self._session = requests.Session()
        self._msg_queue = Queue(maxsize=max_queue_size)
        self._worker = Thread(target=self._process_queue)
        self._worker.daemon = True
        self._worker.start()

    def _construct(self, vals):
        r = { "version": client_state.version, }
        r.update(vals)

        return json.dumps(r, cls=client_state.serialiser)

    def _process_queue(self):

        retry = None
        while True:
            location, data = retry or self._msg_queue.get(True)
            try:
                self._session.post(
                    location,
                    data=data,
                    headers={"content-type": "application/json"},
                )
            except (requests.Timeout, requests.ConnectionError) as e:
                time.sleep(1)
                retry = (location, data)
            except Exception as e:
                logger.exception("Unexpected error message to agent")
            else:
                retry = None

    def _queue_message(self, location, data):
        try:
            self._msg_queue.put_nowait((location, data))
        except Full:
            self._msg_queue.get()
            self._queue_message(location, data)

    def _send_message(self, path, vals, node_id):
        location = self._loc(path, node_id)
        data = self._construct(vals)
        self._queue_message(location, data)

    def _loc(self, path, node_id):
        netloc = "{}:{}".format(self._host, self._port)
        path = "/api/v1/{}/{}".format(path.lstrip("/"), client_state.process_name)
        query = "node_id={:s}".format(node_id) if node_id else None

        return urlunparse(("http", netloc, path, None, query, None))
    
    def update_state(self, new_state, node_id=None):
        self._send_message(
            "/state",
            {
                "state": new_state
            },
            node_id,
        )

    def update_metadata(self, new_state, node_id=None):
        self._send_message(
            "/metadata",
            {
                "metadata": new_state
            },
            node_id,
        )

    def lifecycle_event(self, key_type, comment, node_id=None):
        self._send_message(
            "/lifecycle",
            {
                "type": key_type,
                "comment": comment,
            },
            node_id,
        )

    def post_log(self, log_data, node_id=None):
        self._send_message(
            "/log",
            {
                "logs": [
                    log_data,
                ]
            },
            node_id,
        )
