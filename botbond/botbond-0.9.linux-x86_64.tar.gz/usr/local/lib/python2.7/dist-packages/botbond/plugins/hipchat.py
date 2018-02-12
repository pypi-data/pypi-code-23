# -*- coding: utf-8 -*-
"""hipchat plugin"""

__author__  = "Adrien DELLE CAVE"
__license__ = """
    Copyright (C) 2018  fjord-technologies

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
import emoji
import logging
import threading
import time

from datetime import datetime
from hypchat import HypChat

from botbond.classes.channels import BotbondChannel, BotbondChannelInBase, BotbondChannelOutBase, CHANNELS
from dwho.adapters.redis import DWhoAdapterRedis
from dwho.classes.plugins import DWhoPluginBase, PLUGINS


LOG     = logging.getLogger('botbond.plugins.hipchat')

logging.getLogger('requests').setLevel(logging.WARNING)

_DELAY  = 2


class BotbondHipchatChannelIn(BotbondChannelInBase):
    def run(self):
        while True:
            try:
                item     = CHANNELS[self.name].qget(True)
                ref_chan = CHANNELS[self.name].channel
                (ref_chan['conn'].get_room(ref_chan['room'])
                                 .message("%s on %s: %s" % (item['user'],
                                                            item['channel'],
                                                            emoji.emojize(item['message'], use_aliases=True))))
            except Exception, e:
                LOG.exception("%r", e)


class BotbondHipchatChannelOut(BotbondChannelOutBase):
    def run(self):
        while True:
            try:
                latest = self.channel['conn'].get_room(self.channel['room']).latest()
                for event in latest['items']:
                    if event['type'] not in ('message',):
                        continue

                    uid = "%s/%s" % (self.channel['name'], event['id'])

                    if self.channel['storage'].get_key(uid):
                        continue

                    self.channel['storage'].set_key(uid, time.mktime(time.gmtime()))

                    if isinstance(event['from'], dict):
                        if event['from']['mention_name'] == self.channel['me']['owner']['mention_name']:
                            continue
                        user_name = event['from']['name']
                    elif event['from'] == self.channel['me']['owner']['name']:
                        continue
                    else:
                        user_name = event['from']

                    for channel_out in self.channel['out']:
                        if channel_out not in CHANNELS:
                            LOG.error("invalid channel: %r", channel_out)
                            continue
                        CHANNELS[channel_out].qput({'message': event['message'],
                                                    'user':    user_name,
                                                    'channel': self.channel['name']})
                time.sleep(_DELAY)
            except Exception, e:
                LOG.exception("%r", e)


class BotbondHipchatPlugin(DWhoPluginBase):
    PLUGIN_NAME = 'hipchat'

    def safe_init(self):
        self.channels       = {}
        self.adapter_redis  = DWhoAdapterRedis(self.config, prefix = 'hipchat')

        if 'hipchat' not in self.config['plugins']:
            return

        for channel, params in self.config['plugins']['hipchat'].iteritems():
            self.channels[channel] = {'conn': HypChat(**params['options']),
                                      'id': None,
                                      'name': "%s://%s/%s" % (self.PLUGIN_NAME, channel, params['room']),
                                      'room': params['room'],
                                      'token': params['options']['token'],
                                      'out': params['out'],
                                      'me': None,
                                      'storage': self.adapter_redis}

            ref_chan = self.channels[channel]
            ref_chan['me'] = ref_chan['conn'].fromurl('{0}/v2/oauth/token/{1}'.format(
                                 ref_chan['conn'].endpoint,
                                 ref_chan['token']))
            CHANNELS.register(BotbondChannel(ref_chan))

    def at_start(self):
        for channel in self.channels.itervalues():
            BotbondHipchatChannelIn(channel['name'])()
            BotbondHipchatChannelOut(channel)()


if __name__ != "__main__":
    def _start():
        PLUGINS.register(BotbondHipchatPlugin())
    _start()
