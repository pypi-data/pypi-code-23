#!/usr/bin/env python3
import sys

from httpstatuspuppet.server import Server

server = Server()
print(f"Starting at {server.url}", file=sys.stderr)
server.run()
