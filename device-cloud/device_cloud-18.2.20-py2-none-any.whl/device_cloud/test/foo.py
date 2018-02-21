#!/usr/bin/env python
import json
import os
import unittest
from binascii import crc32
import mock
import platform
import re
import socket
import ssl
import sys

# yocto supports websockets, not websocket, so check for that
try:
    import websocket
except ImportError:
    import websockets as websocket

from time import sleep

import device_cloud
import device_cloud.test.test_helpers as helpers

if sys.version_info.major == 2:
    builtin = "__builtin__"
else:
    builtin = "builtins"


class ClientConnectSuccess(unittest.TestCase):
    @mock.patch("ssl.SSLContext")
    @mock.patch(builtin + ".open")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    @mock.patch("time.sleep")
    @mock.patch("paho.mqtt.client.Client")
    @mock.patch("socket.gethostbyname")
    def runTest(self, mock_mqtt, mock_sleep, mock_exists, mock_isfile,
                mock_open, mock_context, mock_gethostbyname):
        # Set up mocks
        mock_exists.side_effect = [True, True, True]
        mock_isfile.side_effect = [True]
        mock_gethostbyname.side_effect = [ "1.1.1.1" ]
        read_strings = [json.dumps(self.config_args), helpers.uuid]
        mock_read = mock_open.return_value.__enter__.return_value.read
        mock_read.side_effect = read_strings
        mock_mqtt.return_value = helpers.init_mock_mqtt()

        # Initialize client
        kwargs = {"loop_time":1, "thread_count":0}
        self.client = device_cloud.Client("testing-client", kwargs)
        self.client.initialize()

        # Connect successfully
        mqtt = self.client.handler.mqtt
        assert self.client.connect(timeout=5) == device_cloud.STATUS_SUCCESS
        mqtt.connect.assert_called_once_with("api.notarealcloudhost.com",
                                             8883, 60)
        assert self.client.is_connected() is True
        assert self.client.disconnect() == device_cloud.STATUS_SUCCESS
        mqtt.disconnect.assert_called_once()
        assert self.client.is_connected() is False

    def setUp(self):
        # Configuration to be 'read' from config file
        self.config_args = helpers.config_file_default()

