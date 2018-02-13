#! /usr/bin/env python

import random
from tempfile import mkdtemp
import time

from contracts import contract
import irc.bot  #@UnresolvedImport
from irc.client import ServerNotConnectedError

from . import __version__
from .dcache_wire import put_in_queue
from .utils import get_at_least_one


class SwarmBot(irc.bot.SingleServerIRCBot):

    def __init__(self, servers, stream_name, queue_to_brain, channel, nickname):

        irc.bot.SingleServerIRCBot.__init__(self, servers, nickname, nickname)
        self.target = channel
        self.queue_to_brain = queue_to_brain
        self.stream_name = stream_name
        self.seen = {}
        self.tmpdir = mkdtemp(prefix='swarm')

        self.admitted = False
        self.disconnected = False
        self.last_broadcast = 0

        self.lateness = random.uniform(0, 10)
        self.nusers = 10

    def on_pubmsg(self, c, e):
        self._handle(c, e)

    def _handle(self, _c, e):
        s = str(e.arguments[0])
        put_in_queue(self.queue_to_brain, (self.stream_name, s))

    def on_privmsg(self, c, e):
        self._handle(c, e)

    def on_welcome(self, connection, _event):
#        print('welcome message from %s: \n%s' % (connection.server, " ".join(event.arguments)))
        connection.join(self.target)
        print('Connected to %s on IRC server %s.' % (self.target, connection.server))
        self.admitted = True

    def on_join(self, _c, _e):
        users = self.channels[self.target].users()
        self.nusers = len(users)
#        print('current users: %s' % users)

    def on_disconnect(self, _c, event):
        print('Disconnected', event.__dict__)
        self.disconnected = True

    @contract(d=str)
    def send_message(self, d):
        self.connection.privmsg(self.target, d)
        print('to %s: %s' % (self.target, d))
        self.last_broadcast = time.time()


def start_irc(stream_name, servers, queue_to_brain, outgoing_irc):
    random.seed()
    channel = '#duckiebots'

    nickname = 'D_%s_' % (__version__) + str(random.randint(0, 100000))
    nickname = nickname.replace('.', '_')
    print('Using nickname %s' % nickname)

    delta_wait_for_welcome = 60
    c = SwarmBot(servers, stream_name, queue_to_brain, channel, nickname)
    while True:

        while True:
            attempt_start = time.time()
            c.admitted = False
            print('server list: %s' % [_.host for _ in c.server_list])
            c._connect()
            while not c.admitted:
                # print('Waiting for welcome')
                time.sleep(1)
                c.reactor.process_once()

                delta = time.time() - attempt_start
                give_up = delta > delta_wait_for_welcome
                if give_up:
                    print('Could not receive welcome. giving up after %d s' % delta_wait_for_welcome)
                    break
            if c.admitted:
                break
            print('Changing server')
            c.jump_server()

        c.disconnected = False

        while True:
            time.sleep(1.0)
            c.reactor.process_once(1.0)
            if c.disconnected:
                break

            xs = get_at_least_one(outgoing_irc, timeout=1.0)
            for to_channel, x in xs:
                if to_channel == stream_name:
                    try:
                        c.send_message(x)
                    except ServerNotConnectedError:
                        break

