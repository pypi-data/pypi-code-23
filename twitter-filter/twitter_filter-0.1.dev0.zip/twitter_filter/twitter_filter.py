# -*- coding: utf-8 -*-
"""

Main Code

"""

from datetime import datetime

from twitter_filter.batcher import Batcher
from twitter_filter.twitter_listener import Listener

from twitter_filter.twitter_api import TwitterApiWrapper

batcher_instance = Batcher(datetime.now(), "new data", 3, "config.txt")
listener_instance = Listener(batcher_instance)
api_instance = TwitterApiWrapper("config.txt", listener_instance)


stream = api_instance.get_stream_api_instance()
api_instance.filter(["Apple"], stream, ["en"])
