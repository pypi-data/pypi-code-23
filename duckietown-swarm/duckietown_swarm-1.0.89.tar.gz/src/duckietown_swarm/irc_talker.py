
#! /usr/bin/env python

from collections import defaultdict
from duckietown_swarm.dcache import BOOTSTRAP_PATTERNS
from duckietown_swarm.dcache_wire import create_ping_message
import random
import socket
from tempfile import mkdtemp
import time

from contracts import contract
from contracts.utils import indent
from irc.bot import SingleServerIRCBot
from irc.client import ServerNotConnectedError, MessageTooLong

from . import __version__
from .dcache import  create_propose_message
from .dcache import Envelope, CouldNotReadEnvelope
from .dcache_wire import create_request_message
from .fragments import fragmentize, Assembler
from .ipfs_utils import IPFSInterface
from .utils import now_until


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

        self.nreceived = 0
        self.assemblers = defaultdict(Assembler)

        ipfsi = mi.get_ipfsi()
        self.identity = ipfsi.ipfs_id()

    def on_pubmsg(self, c, e):
        self._handle(c, e)

    def on_privmsg(self, c, e):
        self._handle(c, e)

    def on_namreply(self, _c, e):
        names = map(str, e.arguments[2].split())
        print('list of handles: %s' % names)
        for name in names:
            e = Envelope(
                    maddr_from='/dswarm/%s/brain' % self.identity,
                    maddr_to='/dswarm/*/brain',
                    contents=create_ping_message())
            send(self, e, name)

    def _handle(self, _c, e):
        self.nreceived += 1
        s = str(e.arguments[0])
        # {'source': u'andrea!~andrea@nutonomy02.n.subnet.rcn.com',
        # 'tags': [], 'type': 'pubmsg', 'target': u'#duckiebots', 'arguments': [u'deplep']}
        source = e.source
        if '!' in source:
            source = source[:source.index('!')]

        sn = '/' + str(source)

        self.assemblers[sn].push(s)
        msgs = self.assemblers[sn].pop()
        for msg in msgs:
            try:
                envelope = Envelope.from_json(msg)
            except CouldNotReadEnvelope as e:
                em = 'Could not read envelope from %s: %s' % (sn, e)
                print(em)
            else:
                envelope.maddr_from = sn + envelope.maddr_from
                from duckietown_swarm.irc2 import CouldNotDispatch

                try:
                    self.mi.dispatch(envelope)
                except CouldNotDispatch as e:
                    print(s)

    def on_welcome(self, connection, _event):
#        print('welcome message from %s: \n%s' % (connection.server, " ".join(event.arguments)))
        connection.join(self.target)
        connection.set_keepalive(30)
        print('Connected to %s on IRC server %s.' % (self.target, connection.server))
        self.admitted = True

    def on_join(self, c, e):
        nick = e.source.nick
#        print('on_join %s' % nick)
        if nick != c.get_nickname():
            e = Envelope(
                    maddr_from='/dswarm/%s/brain' % self.identity,
                    maddr_to='/dswarm/*/brain',
                    contents=create_ping_message())
            send(self, e, nick)
#            self.channels[ch] = Channel()
#
#        users = self.channels[self.target].users()
#        self.nusers = len(users)
#
#        if False:
#            msg = create_request_message(BOOTSTRAP_PATTERNS, validity=now_until(105))
#            maddr_from = '/dswarm/%s/brain' % self.identity
#            envelope = Envelope(maddr_from=maddr_from,
#                         maddr_to='/dswarm/*/brain',
#                         contents=msg)
#            send(self, envelope, self.target)
##        print('current users: %s' % users)

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

    ipfsi = IPFSInterface(mi.ipfs_path)
    identity = ipfsi.ipfs_id()
    hostname = socket.gethostname()
    printable = ''.join(ch for ch in hostname if ch.isalnum())
    printable = printable[:8]
    nickname = '%s_' % (__version__[-3:].replace('.', '')) + printable + '_' + identity[-4:]
    print('Using nickname %s' % nickname)

    delta_wait_for_welcome = 60
    stream_name = '/dns4/' + server[0] + '/tcp/' + str(server[1]) + '/irc'
    assert stream_name in mi.name2queue
    assert stream_name == mi.my_maddr

#    key0 = CryptoKey(str(random.randint(0, 10000)), str(random.randint(0, 10000)))
#    key0.hash = ipfsi.ipfs_id()

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
                c.reactor.process_once(1.0)

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
#            print('processing once')
            c.reactor.process_once()
            if c.disconnected:
                break

            xs = mi.get_many_for_me(timeout=1.0)
#            print('get_many_for_me %s' % len(xs))
            for envelope in xs:
                try:
                    if not envelope.maddr_to or envelope.maddr_to[0] != '/':
                        msg = 'Invalid addr_to: %r' % envelope.maddr_to
                        msg += '\n\n' + indent(envelope, '  ')
                        print(msg)
                        continue

                    # orig = envelope.maddr_to
                    tokens = envelope.maddr_to.split('/')
                    assert tokens[0] == ''  # starts with '/'
                    dest = tokens[1]  # = '#duckiebots'
                    rest = '/' + "/".join(tokens[2:])
                    envelope.maddr_to = rest

#                    print('orig: %s  new: %s' % (orig, envelope.maddr_to))
                    if False:
                        print('not sending: %s' % envelope.contents)
                    else:
                        send(c, envelope, dest)

#                    mi.send_to_brain(envelope.maddr_to, envelope.contents)
                except ServerNotConnectedError as e:
                    print e
                    break


@contract(envelope=Envelope)
def send(c, envelope, dest):
    envelope_json = envelope.to_json()
#    print('send: %s' % envelope_json)
    limit, chunk_size = 300, 150
    try:
        if len(envelope_json) < limit:
            raw = [envelope_json]
        else:
            raw = fragmentize(envelope_json, max_chunk_length=chunk_size)

        for r in raw:
            if len(r) > 415:
                print('Do not expect a string of len %s to be ok.' % len(r))
            c.send_message(dest, r)
    except MessageTooLong as e:
        print(e)
        msg = 'Envelope size is %s' % len(envelope_json)
        print(msg)
