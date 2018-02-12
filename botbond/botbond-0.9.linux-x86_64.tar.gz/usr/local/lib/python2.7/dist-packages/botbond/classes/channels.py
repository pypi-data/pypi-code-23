# -*- coding: utf-8 -*-
"""botbond channels"""

__author__  = "Adrien DELLE CAVE <adc@doowan.net>"
__license__ = """
    Copyright (C) 2016  doowan

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""

import abc
import logging
import Queue
import threading

LOG     = logging.getLogger('botbond.channels')


class BotbondChannels(dict):
    def register(self, channel):
        if not isinstance(channel, BotbondChannel):
            raise TypeError("Invalid Channel class. (class: %r)" % channel)
        return dict.__setitem__(self, channel.name, channel)

CHANNELS = BotbondChannels()


class BotbondChannel(object):
    def __init__(self, channel):
        self.channel = channel
        self.name    = channel['name']
        self.queue   = Queue.Queue()

    def qput(self, item):
        return self.queue.put(item)

    def qget(self, block = True, timeout = None):
        return self.queue.get(block, timeout)


class BotbondChannelInBase(threading.Thread):
    __metaclass__ = abc.ABCMeta

    def __init__(self, channel_name):
        threading.Thread.__init__(self)
        self.daemon  = True
        self.name    = channel_name

    def __call__(self):
        self.start()
        return self


class BotbondChannelOutBase(threading.Thread):
    __metaclass__ = abc.ABCMeta

    def __init__(self, channel):
        threading.Thread.__init__(self)
        self.channel = channel
        self.daemon  = True
        self.name    = channel['name']

    def __call__(self):
        self.start()
        return self
