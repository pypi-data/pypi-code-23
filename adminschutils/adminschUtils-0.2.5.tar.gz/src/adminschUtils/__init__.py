"""
Admin.sch utils package. It's a collections of useful helper functions.
"""
import asyncio
import uvloop

from .config import Config
from .webserver import Webserver

asyncio.set_event_loop(uvloop.new_event_loop())
LOOP = asyncio.get_event_loop()

