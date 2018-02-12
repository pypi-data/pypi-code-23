# -*- coding: utf-8 -*-
"""slack plugin"""

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
import re
import threading
import time

from slackclient import SlackClient

from botbond.classes.channels import BotbondChannel, BotbondChannelInBase, BotbondChannelOutBase, CHANNELS
from dwho.adapters.redis import DWhoAdapterRedis
from dwho.classes.plugins import DWhoPluginBase, PLUGINS
from websocket import WebSocketConnectionClosedException


LOG         = logging.getLogger('botbond.plugins.slack')

logging.getLogger('requests').setLevel(logging.WARNING)

_CHANS_INFO = {}
_USERS_INFO = {}
_RE_MENTION = re.compile(r'<@([WU][^>]+)>').finditer
_DELAY      = 2


class BotbondSlackChannelIn(BotbondChannelInBase):
    def run(self):
        while True:
            try:
                item     = CHANNELS[self.name].qget(True)
                ref_chan = CHANNELS[self.name].channel
                ref_chan['conn'].api_call(
                    'chat.postMessage',
                    channel = ref_chan['room'],
                    text    = emoji.emojize(item['message'], use_aliases=True),
                    username = "%s on %s" % (item['user'], item['channel']))
            except Exception, e:
                LOG.exception("%r", e)


class BotbondSlackChannelOut(BotbondChannelOutBase):
    def _get_channel_info(self, conn, channel_id):
        if _CHANS_INFO.get(channel_id):
            return _CHANS_INFO[channel_id]

        res = conn.api_call('channels.info',
                            channel = channel_id)

        if res and res['ok']:
            _CHANS_INFO[channel_id] = res['channel']

        return _CHANS_INFO.get(channel_id)

    def _get_user_info(self, conn, user_id):
        if _USERS_INFO.get(user_id):
            return _USERS_INFO[user_id]

        res = conn.api_call('users.info',
                            user = user_id)

        if res and res['ok']:
            _USERS_INFO[user_id] = res['user']

        return _USERS_INFO.get(user_id)

    def replace_mention(self, conn, msg):
        for user_id in _RE_MENTION(msg):
            user = self._get_user_info(conn, user_id.group(1))
            if user:
                if 'profile' in user:
                    real_name = user['profile']['display_name_normalized'] or user['profile']['real_name_normalized']
                else:
                    real_name = user['real_name']

                msg = msg.replace(user_id.group(0), "@%s" % real_name)

        return msg

    def run(self):
        while True:
            try:
                for event in self.channel['conn'].rtm_read():
                    if event['type'] not in ('message', 'file_shared') \
                       or 'subtype' in event \
                       or 'channel' not in event \
                       or 'user' not in event:
                        continue

                    chan_info = self._get_channel_info(self.channel['conn'], event['channel'])
                    if not chan_info:
                        continue

                    if self.channel['room'] not in (chan_info['name'], chan_info['name_normalized']):
                        continue

                    user_info = self._get_user_info(self.channel['conn'], event['user'])
                    if not user_info:
                        continue

                    for channel_out in self.channel['out']:
                        if channel_out not in CHANNELS:
                            LOG.error("invalid channel: %r", channel_out)
                            continue
                        CHANNELS[channel_out].qput({'message': self.replace_mention(self.channel['conn'], event['text']),
                                                    'user': user_info['real_name'],
                                                    'channel': self.channel['name']})

                time.sleep(_DELAY)
            except WebSocketConnectionClosedException:
                LOG.info("reconnecting to: %r", self.channel['name'])
                time.sleep(_DELAY)
                self.channel['conn'] = SlackClient(self.channel['options']['token'])
            except Exception, e:
                LOG.exception("%r", e)


class BotbondSlackPlugin(DWhoPluginBase):
    PLUGIN_NAME = 'slack'

    def safe_init(self):
        self.channels       = {}
        self.adapter_redis  = DWhoAdapterRedis(self.config, prefix = 'slack')

        if 'slack' not in self.config['plugins']:
            return

        for channel, params in self.config['plugins']['slack'].iteritems():
            self.channels[channel] = {'conn': SlackClient(params['options']['token']),
                                      'id': None,
                                      'name': "%s://%s/%s" % (self.PLUGIN_NAME, channel, params['room']),
                                      'room': params['room'],
                                      'options': params['options'],
                                      'out': params['out'],
                                      'storage': self.adapter_redis}
            ref_chan = self.channels[channel]

            if not ref_chan['conn'].rtm_connect(with_team_state=False):
                LOG.error("unable to connect to %r", channel)
                continue

            ref_chan['id'] = ref_chan['conn'].api_call('auth.test')['user_id']
            CHANNELS.register(BotbondChannel(ref_chan))

    def at_start(self):
        for channel in self.channels.itervalues():
            BotbondSlackChannelIn(channel['name'])()
            BotbondSlackChannelOut(channel)()


if __name__ != "__main__":
    def _start():
        PLUGINS.register(BotbondSlackPlugin())
    _start()
