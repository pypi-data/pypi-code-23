#! /usr/bin/env python

from multiprocessing import Queue
import os
import sys
import time

from contracts import contract
from contracts.utils import indent

from .crypto import get_key
from .dcache import Envelope
from .directory_watcher_imp import directory_watcher
from .ipfs_utils import IPFSInterface
from .irc_talker import start_irc
from .pinner import pinner
from .pinner import verifier
from .process_manager import ProcessManager
from .pubsub_friends import connecting_to_peer
from .pubsub_friends import pubsub_friendship
from .pubsub_processes import pubsub_reader_process, \
    pubsub_writer_process
from .spawn_ipfs import check_ipfs_executable
from .spawn_ipfs import run_ipfs, initialize_ipfs
from .summary import publish_ipns
from .tcpendpoint import tcplisten
from .udp_interface import UDP_PORT, get_suitable_udp_interfaces, \
    udp_broadcaster, udp_listener
from .utils import get_all_available
from .utils import get_at_least_one


class Dispatcher(object):

    def __init__(self, prefix):
        self.prefix = prefix
        self.name2queue = {}
        self.my_maddr = None

    @contract(envelope=Envelope)
    def dispatch(self, envelope, sign=False):
        n = 0
        if not envelope.maddr_to:
            em = 'The address is empty.'
            em += "\n" + envelope.verbose()
            raise Exception(em)
#        print('dispatch %s' % envelope.maddr_to)

        for name, q in self.name2queue.items():
            is_match, rest = prefix_match(address=envelope.maddr_to, x=name)
            if is_match:
#                print('Sending %r to pipe %r with rest %r' % (envelope.maddr_to, name, rest))
                maddr_to = rest
                maddr_from = self.my_maddr + envelope.maddr_from
                e = Envelope(maddr_from, maddr_to, envelope.contents)
                if sign:
#                    if 'signature' in envelope.contents:
#                        em = 'Will not sign a signature: %s' % envelope
#                        raise Exception(em)
                    msg_sign = self.key.generate_sign_message(envelope.contents)
                    e_sign = Envelope(maddr_from, maddr_to, msg_sign)
                    q.put(e_sign)
                q.put(e)
#                print('orig: %s\nforw: %s' % (envelope, e))
                n += 1

        if n == 0:
            msg = 'Could not find channel for %r' % envelope.maddr_to
            msg += '\n\n' + indent("\n".join(sorted(self.name2queue)), '  ')
            msg += '\n\nEnvelope:'
            msg += '\n\n' + indent(envelope.verbose(), '  ')
            raise CouldNotDispatch(msg)

    def get_ipfsi(self):
        return IPFSInterface(self.ipfs_path)

    @contract(returns=Envelope)
    def get_next_for_me(self):
        q = self.name2queue[self.my_maddr]
        return q.get()

    @contract(returns='list($Envelope)')
    def get_many_for_me(self, timeout):
        q = self.name2queue[self.my_maddr]
        return get_at_least_one(q, timeout=timeout)

    @contract(returns='list($Envelope)')
    def get_all_available_for_me(self):
        q = self.name2queue[self.my_maddr]
        return get_all_available(q)


class CouldNotDispatch(Exception):
    pass


def prefix_match(address, x):
    '''

    Examples:

        /irc/host/channel /irc/host/channel
        True, ''
        /irc/host/channel/b /irc/host/channel
        True, '/b'
        /irc/*/channel /irc/host/channel
        True, ''

        /irc/*/channel/b /irc/host/channel
        True, '/b'

    '''
    ta = address.split('/')
    tx = x.split('/')

#    print('ta: %s' % ta)
#    print('tx: %s' % tx)

    def match(A, B):
        assert not '*' in B, (A, B)
        return A == B or ('*' == A)

#    for lm in reversed(range(len(tx) + 1)):
    lm = len(tx)
    if len(ta) < len(tx):
        return False, None
    for i in range(lm):
        a = ta[i]
        x = tx[i]
        if not match(a, x):
#                print('not matched with %s because %s != %s' % (lm, a, x))
            return False, None
            break
    else:
#            print('matched up to %s: %r %r' % (lm, ta[:lm], tx[:lm]))
        remain = ta[lm:]
        if remain:
            rest = '/' + '/'.join(remain)
        else:
            rest = ''
        return True, rest


class MessagingInterface(Dispatcher):

    def __init__(self, key, ipfs_path):
        prefix = '/dswarm' + '/' + key.hash
        Dispatcher.__init__(self, prefix)

        self.key = key
        self.ipfs_path = ipfs_path

        APP = prefix
        self.MADDR_BRAIN = APP + '/brain'
        self.MADDR_PINNER = APP + '/pinner'
        self.MADDR_CONNECTOR = APP + '/connector'
        self.MADDR_VERIFIER = APP + '/verifier'
        self.MADDR_IPNS = APP + '/ipns'
        self.MADDR_DIRWATCHER = APP + '/dirwatcher'
        self.MADDR_PUBSUBFRIENDS = APP + '/pubfriends'
        self.MADDR_IRC = '/dns4/frankfurt.co-design.science/tcp/6667/irc'
        self.IRC_CHANNEL = '#duckiebots'
        self.MADDR_PUBSUBWRITER = APP + '/pubsubwriter'
        self.MADDR_READ_SUMMARIES = APP + '/read_summaries'
        self.MADDR_TCP_SERVER = APP + '/tcpserver'

        self.pubsub_topic = 'duckiebots'

        self.MADDR_PUBSUBWRITER = '/ipfs-pubsub/' + self.pubsub_topic

        self.name2queue = {}
        self.name2queue[self.MADDR_PINNER] = Queue()
        self.name2queue[self.MADDR_BRAIN] = Queue()
        self.name2queue[self.MADDR_VERIFIER] = Queue()
        self.name2queue[self.MADDR_IPNS] = Queue()
        self.name2queue[self.MADDR_IRC] = Queue()
        self.name2queue[self.MADDR_PUBSUBWRITER] = Queue()
        self.name2queue[self.MADDR_READ_SUMMARIES] = Queue()
        self.name2queue[self.MADDR_CONNECTOR] = Queue()
        self.name2queue[self.MADDR_TCP_SERVER] = Queue()

        self.udps = []

        for name, _ in get_suitable_udp_interfaces().items():
#            _address = x['address']
#            broadcast = x['broadcast']
#            a = '/ip4/%s/udp/%s' % (broadcast, UDP_PORT)
            a = '/udp/%s/%s' % (name, UDP_PORT)
            self.name2queue[a] = Queue()
            self.udps.append(a)

    def broadcast_to_all_brains(self, msg, sign):
        from .brain import ALL_BRAINS
        for c in self._get_broadcasting_channels():
            new_to = c + ALL_BRAINS
            envelope = Envelope(maddr_from='', maddr_to=new_to, contents=msg,
                                comment='process: ' + self.my_maddr)
            self.dispatch(envelope, sign=sign)

    def _get_broadcasting_channels(self):
        return [
            self.MADDR_PUBSUBWRITER,
            self.MADDR_IRC + '/' + self.IRC_CHANNEL,
        ] + self.udps

    def copy_as(self, my_maddr):
        c = MessagingInterface(self.key, self.ipfs_path)
        c.name2queue.update(self.name2queue)
        c.my_maddr = my_maddr
        return c

    @contract(from_channel=str, msg=str)
    def send_to_brain(self, from_channel, msg, sign=False):
        e = Envelope(from_channel, self.MADDR_BRAIN, msg)
        self.dispatch(e, sign=sign)

    @contract(mh='multihash')
    def send_to_pinner(self, mh):
        e = Envelope('', self.MADDR_PINNER, mh)
        self.dispatch(e)

#    @contract(mh='multihash')
    def send_to_connector(self, address):
        e = Envelope('', self.MADDR_CONNECTOR, address)
        self.dispatch(e)

    @contract(mh='multihash')
    def send_to_readsummaries(self, mh):
        e = Envelope('', self.MADDR_READ_SUMMARIES, mh)
        self.dispatch(e)

    @contract(mh=str)
    def send_to_verifier(self, mh):
        e = Envelope('', self.MADDR_VERIFIER, mh)
        self.dispatch(e)

    @contract(key=str, mh=str)
    def send_to_ipns_publisher(self, key, mh):
        assert mh.startswith('Qm'), (key, mh)
        e = Envelope('', self.MADDR_IPNS, (key, mh))
        self.dispatch(e)


def duckietown_swarm_main():
    args = sys.argv[1:]
    if not args:
        watch_dir = os.path.expanduser('~/shared-logs')
    else:
        watch_dir = args[0]

    use_irc = True
    use_pubsub = True
    use_udp = True

    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)

    cache_dir = os.path.join(watch_dir, '.cache')

    ipfs_path = os.path.join(cache_dir, '.ipfs')
    check_ipfs_executable(ipfs_path)
    initialize_ipfs(ipfs_path)
    ipfsi = IPFSInterface(ipfs_path)

    try:
        print ipfsi.stats_bw()
        print('OK - ipfs was running')
    except:
        print('Now starting ipfs')
        run_ipfs(ipfs_path, use_pubsub)
        while True:
            time.sleep(1)
            try:
                print ipfsi.stats_bw()
                break
            except:
                pass

    identity = ipfsi.ipfs_id()

    print('%s Identity: %s' % (ipfs_path, identity))

    ipfsi.p2p_listener_open('p2p-ssh', '/ip4/127.0.0.1/tcp/22')
    ipfsi.p2p_listener_open('p2p-dswarm', '/ip4/127.0.0.1/tcp/8000')

    key = get_key(cache_dir)
    key.hash = identity
    print('You can put any log file in the directory\n\n\t%s\n\n'
          'and it will be shared with the swarm.\n\n' % watch_dir)

    '''
        incoming -> [brain] -> outgoing
                               pinner_queue
                    publisher_queue


            pinner_queue -> [pinner] -> pinner

            publisher_queue -> [publisher] -> incoming



        outgoing[0] -> [irc server]
        outgoing[1]
    '''

    mi = MessagingInterface(key, ipfs_path)
    interfaces = get_suitable_udp_interfaces()
    if use_udp:
        for x in mi.udps:
            interface = x.split('/')[2]
            assert interface in interfaces, (interface, x.split('/'))
            pm = ProcessManager(udp_broadcaster,
                                (mi.copy_as(x), interface, UDP_PORT), x,
                                restart=True)
            pm.start()

            pm = ProcessManager(udp_listener,
                                (mi.copy_as(x), interface, UDP_PORT), x,
                                restart=True)
            pm.start()

    pm = ProcessManager(publish_ipns,
                        (mi.copy_as(mi.MADDR_IPNS),), 'publish_ipns',
                        restart=True)
    pm.start()

    if use_pubsub:
        pm = ProcessManager(pubsub_reader_process,
                            (mi.copy_as(mi.MADDR_PUBSUBWRITER), mi.pubsub_topic), 'pubsub_reader',
                            restart=True)
        pm.start()

        pm = ProcessManager(pubsub_writer_process,
                            (mi.copy_as(mi.MADDR_PUBSUBWRITER), mi.pubsub_topic), 'pubsub_writer',
                            restart=True)
        pm.start()

    npinners = 10
    for i in range(npinners):

        pm = ProcessManager(pinner, (mi.copy_as(mi.MADDR_PINNER),), 'pinner%d' % i, restart=True)
        pm.start()

    nconnectors = 10
    for i in range(nconnectors):

        pm = ProcessManager(connecting_to_peer, (mi.copy_as(mi.MADDR_CONNECTOR),), 'connector%d' % i, restart=True)
        pm.start()

    nverifiers = 5
    for i in range(nverifiers):
        pm = ProcessManager(verifier, (mi.copy_as(mi.MADDR_VERIFIER),), 'verifier%d' % i, restart=True)
        pm.start()

    from .brain import brain

    server = ('frankfurt.co-design.science', 6667)
    channel = '#duckiebots'
    if use_irc:
        pm = ProcessManager(start_irc,
                            (mi.copy_as(mi.MADDR_IRC), server, channel),
                            'irc1',
                            restart=True)
        pm.start()

#    if False:
#        servers = [('irc.freenode.net', 6667), ]
#        pm = ProcessManager(start_irc,
#                            ('to_irc2', servers, mi), 'irc2',
#                            restart=True)
#        pm.start()

    brainp = ProcessManager(brain,
                        (mi.copy_as(mi.MADDR_BRAIN), cache_dir), 'brain',
                        restart=True)
    brainp.start()

    pm = ProcessManager(directory_watcher,
                        (mi.copy_as(mi.MADDR_DIRWATCHER), watch_dir), 'directory_watcher',
                        restart=True)
    pm.start()

    from .offline import read_nodes_summaries

    for i in range(4):
        pm = ProcessManager(read_nodes_summaries,
                            (mi.copy_as(mi.MADDR_READ_SUMMARIES),), 'read_nodes_summaries%d' % i,
                            restart=True)
        pm.start()

    pm = ProcessManager(pubsub_friendship,
                        (mi.copy_as(mi.MADDR_PUBSUBFRIENDS),), 'pubsub_friendship',
                        restart=True)
    pm.start()

    port = 8000
    pm = ProcessManager(tcplisten,
                        (mi.copy_as(mi.MADDR_TCP_SERVER), port), 'tcplisten%s' % port,
                        restart=True)
    pm.start()

#    pm = ProcessManager(publisher_summary,
#                        (mi, '/dswarm/summary'), 'publisher_summary',
#                        restart=True)
#    pm.start()

    brainp.p.join()


if __name__ == "__main__":
    duckietown_swarm_main()
