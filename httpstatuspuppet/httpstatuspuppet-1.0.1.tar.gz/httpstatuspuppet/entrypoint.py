#!/usr/bin/env python3
import logging

from httpstatuspuppet.server import Server

logging.root.setLevel(logging.INFO)
server = Server()
logging.info(f"Starting at {server.url}")
server.run()
