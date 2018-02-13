import json
import logging
import time

# pylint: disable=wrong-import-position
import six

if six.PY2:
    # pylint: disable=import-error, no-name-in-module
    from urlparse import urlunparse
    from Queue import Queue, Full
else:
    from urllib.parse import urlunparse # pylint: disable=import-error, no-name-in-module
    from queue import Queue, Full # pylint: disable=import-error

import requests
from threading import Thread

from .base import BaseClient
from overlock.state import client_state
from overlock import __version__ as lib_version

logger = logging.getLogger(__name__)

# Info added to all requests
STD_INFO = {
    "library": "python",
    "version": lib_version,
}

class OverlockRequestsClient(BaseClient):
    """Connects to the agent over an http socket
    """

    def __init__(self, max_queue_size=500):
        self._session = requests.Session()
        self._msg_queue = Queue(maxsize=max_queue_size)
        self._worker = Thread(target=self._process_queue)
        self._worker.daemon = True
        self._worker.start()

    def _construct(self, vals):
        vals.update(STD_INFO)
        return json.dumps(vals, cls=client_state.serialiser)

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
                logger.warning("Error sending message to agent (%s)", repr(e))
                time.sleep(1)
                retry = (location, data)
            except Exception: # pylint: disable=broad-except
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
        netloc = "{}:{}".format(client_state.agent_host, client_state.agent_port)
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

    def update_metadata(self, new_metadata, node_id=None):
        self._send_message(
            "/metadata",
            {
                "metadata": new_metadata
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
