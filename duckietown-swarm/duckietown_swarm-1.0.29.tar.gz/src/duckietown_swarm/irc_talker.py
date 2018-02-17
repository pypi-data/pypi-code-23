#! /usr/bin/env python

from duckietown_swarm.dcache import Envelope
import random
from tempfile import mkdtemp
import time

from contracts import contract
from irc.bot import SingleServerIRCBot
from irc.client import ServerNotConnectedError

from . import __version__
from .dcache import CryptoKey, create_propose_message
from .ipfs_utils import IPFSInterface


class SwarmBot(SingleServerIRCBot):

    def __init__(self, servers, stream_name, mi, channel, nickname):
        SingleServerIRCBot.__init__(self, servers, nickname, nickname)
        self.mi = mi
        self.target = channel

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

    def on_privmsg(self, c, e):
        self._handle(c, e)

    def _handle(self, _c, e):
        s = str(e.arguments[0])
        # {'source': u'andrea!~andrea@nutonomy02.n.subnet.rcn.com', 'tags': [], 'type': 'pubmsg', 'target': u'#duckiebots', 'arguments': [u'deplep']}
        source = e.source
        if '!' in source:
            source = source[:source.index('!')]

        sn = '/' + str(source)

        envelope = Envelope.from_json(s)
        envelope.maddr_from = sn + envelope.maddr_from
#        c.send_message(dest, envelope_json)
        self.mi.dispatch(envelope)

#        self.mi.send_to_brain(sn, s)

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
    def send_message(self, target, d):
        self.connection.privmsg(target, d)
#        print('to %s: %s' % (target, d))
        self.last_broadcast = time.time()


def start_irc(mi, server, channel):
    random.seed()

    ipfsi = IPFSInterface()
    identity = ipfsi.ipfs_id()

    nickname = 'D_%s_' % (__version__.replace('.', '_')) + identity[-6:]
    print('Using nickname %s' % nickname)

    delta_wait_for_welcome = 60
    stream_name = '/dns4/' + server[0] + '/tcp/' + str(server[1]) + '/irc'
    assert stream_name in mi.name2queue
    assert stream_name == mi.my_maddr

    key0 = CryptoKey(str(random.randint(0, 10000)), str(random.randint(0, 10000)))
    key0.hash = ipfsi.ipfs_id()

    t = time.time()
    irc_names = [
        stream_name + '/' + nickname,
        stream_name + '/' + channel,
    ]
    for irc_name in irc_names:
        msg = create_propose_message(('pri', identity, 'addresses'), irc_name, validity=[t, t + 300])
        mi.send_to_brain('', msg, sign=True)

    c = SwarmBot([server], stream_name, mi, channel, nickname)
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
                    print('Could not receive welcome. giving up after %d s'
                          % delta_wait_for_welcome)
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

            xs = mi.get_many_for_me(timeout=1.0)

            for envelope in xs:
                try:
                    if not envelope.maddr_to or envelope.maddr_to[0] != '/':
                        msg = 'Invalid addr_to: %r' % envelope.maddr_to
                        print(msg)
                        continue

#                    print('irc: maddr_to = %r' % envelope.maddr_to)
                    # '/#duckiebots/dswarm/*/brain'
                    tokens = envelope.maddr_to.split('/')
                    assert tokens[0] == ''  # starts with '/'
                    dest = tokens[1]  # = '#duckiebots'
                    rest = '/' + "/".join(tokens[2:])
#                    print('dest: %r rest: %r' % (dest, rest))
                    envelope.maddr_to = rest
                    envelope_json = envelope.to_json()
                    c.send_message(dest, envelope_json)
#                    mi.send_to_brain(envelope.maddr_to, envelope.contents)
                except ServerNotConnectedError:
                    break

