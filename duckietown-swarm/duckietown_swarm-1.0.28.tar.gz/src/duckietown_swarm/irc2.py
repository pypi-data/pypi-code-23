#! /usr/bin/env python

from duckietown_swarm.dcache import CryptoKey
from duckietown_swarm.ipfs_utils import IPFSInterface
from duckietown_swarm.udp_interface import UDP_PORT, get_suitable_udp_interfaces, \
    udp_broadcaster, udp_listener
from multiprocessing import Queue
import os
import pickle
import random
import sys

from contracts import contract

from .dcache import Envelope
from .directory_watcher_imp import directory_watcher
from .irc_talker import start_irc
from .pinner import pinner
from .pinner import verifier
from .process_manager import ProcessManager
from .pubsub_friends import pubsub_friendship
from .pubsub_processes import pubsub_reader_process, \
    pubsub_writer_process
from .summary import publish_ipns
from .utils import get_at_least_one

ipfsi = IPFSInterface()

APP = '/dswarm' + '/' + ipfsi.ipfs_id()

MADDR_BRAIN = APP + '/brain'
MADDR_PINNER = APP + '/pinner'
MADDR_VERIFIER = APP + '/verifier'
MADDR_IPNS = APP + '/ipns'
MADDR_DIRWATCHER = APP + '/dirwatcher'
MADDR_PUBSUBFRIENDS = APP + '/pubfriends'
MADDR_IRC = '/dns4/frankfurt.co-design.science/tcp/6667/irc'
IRC_CHANNEL = '#duckiebots'
MADDR_PUBSUBWRITER = APP + '/pubsubwriter'

pubsub_topic = 'duckiebots'

MADDR_PUBSUBWRITER = '/ipfs-pubsub/' + pubsub_topic


#from .summary import publisher_summary
class MessagingInterface():

    def __init__(self, key):
        self.key = key

        name2queue = {}
        name2queue[MADDR_PINNER] = Queue()
        name2queue[MADDR_BRAIN] = Queue()
        name2queue[MADDR_VERIFIER] = Queue()
        name2queue[MADDR_IPNS] = Queue()
        name2queue[MADDR_IRC] = Queue()
        name2queue[MADDR_PUBSUBWRITER] = Queue()

        self.udps = []

        for _name, x in get_suitable_udp_interfaces().items():
            _address = x['address']
            broadcast = x['broadcast']
            a = '/ip4/%s/udp/%s' % (broadcast, UDP_PORT)
            name2queue[a] = Queue()
            self.udps.append(a)

        self.name2queue = name2queue
        self.my_maddr = None

    def get_broadcasting_channels(self):
        return [
            MADDR_PUBSUBWRITER,
            MADDR_IRC + '/' + IRC_CHANNEL,
        ] + self.udps

    def copy_as(self, my_maddr):
        c = MessagingInterface(self.key)
        c.name2queue.update(self.name2queue)
        c.my_maddr = my_maddr
        return c

    @contract(from_channel=str, msg=str)
    def send_to_brain(self, from_channel, msg, sign=False):
        e = Envelope(from_channel, MADDR_BRAIN, msg)
        self.dispatch(e, sign=sign)

    @contract(mh=str)
    def send_to_pinner(self, mh):
        e = Envelope('', MADDR_PINNER, mh)
        self.dispatch(e)

    @contract(returns=Envelope)
    def get_next_for_me(self):
        q = self.name2queue[self.my_maddr]
        return q.get()

    @contract(returns='list($Envelope)')
    def get_many_for_me(self, timeout):
        q = self.name2queue[self.my_maddr]
        return get_at_least_one(q, timeout=timeout)

    @contract(mh=str)
    def send_to_verifier(self, mh):
        e = Envelope('', MADDR_VERIFIER, mh)
        self.dispatch(e)

    @contract(key=str, mh=str)
    def send_to_ipns_publisher(self, key, mh):
        assert mh.startswith('Qm'), (key, mh)
        e = Envelope('', MADDR_IPNS, (key, mh))
        self.dispatch(e)

    @contract(envelope=Envelope)
    def dispatch(self, envelope, sign=False):
        n = 0
        for name, q in self.name2queue.items():
            if envelope.maddr_to.startswith(name):
                maddr_to = envelope.maddr_to[len(name):]
                maddr_from = self.my_maddr + envelope.maddr_from
                e = Envelope(maddr_from, maddr_to, envelope.contents)
                if sign:
                    msg_sign = self.key.generate_sign_message(envelope.contents)
                    e_sign = Envelope(maddr_from, maddr_to, msg_sign)
                    q.put(e_sign)
                q.put(e)
                # print('orig: %s\nforw: %s' % (envelope, e))
                n += 1

        if n == 0:
            msg = 'Could not find channel for %s' % envelope.maddr_to
            raise Exception(msg)


def get_key(cache_dir):
    fn = os.path.join(cache_dir, '.key.pickle')
    if not os.path.exists(fn):
        key0 = CryptoKey(str(random.randint(0, 10000)), str(random.randint(0, 10000)))
        with open(fn, 'wb') as f:
            pickle.dump(key0, f)
    with open(fn) as f: key = pickle.load(f)

#    identity = key.hash
    key.hash = identity = ipfsi.ipfs_id()
    print('Identity: %s' % identity)
    return key


def duckietown_swarm_main():
    args = sys.argv[1:]
    if not args:
        watch_dir = os.path.expanduser('~/shared-logs')
    else:
        watch_dir = args[0]

    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)

    cache_dir = os.path.join(watch_dir, '.cache')
    key = get_key(cache_dir)
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

    use_irc = True
    use_pubsub = True
    use_udp = True

    mi = MessagingInterface(key)

    if use_udp:
        for x in mi.udps:
            pm = ProcessManager(udp_broadcaster,
                                (mi.copy_as(x),), x,
                                restart=True)
            pm.start()

            pm = ProcessManager(udp_listener,
                                (mi.copy_as(x),), x,
                                restart=True)
            pm.start()

    pm = ProcessManager(publish_ipns,
                        (mi.copy_as(MADDR_IPNS),), 'publish_ipns',
                        restart=True)
    pm.start()

    if use_pubsub:
        pm = ProcessManager(pubsub_reader_process,
                            (mi.copy_as(MADDR_PUBSUBWRITER), pubsub_topic), 'pubsub_reader',
                            restart=True)
        pm.start()

        pm = ProcessManager(pubsub_writer_process,
                            (mi.copy_as(MADDR_PUBSUBWRITER), pubsub_topic), 'pubsub_writer',
                            restart=True)
        pm.start()

    npinners = 10
    for i in range(npinners):

        pm = ProcessManager(pinner, (mi.copy_as(MADDR_PINNER),), 'pinner%d' % i, restart=True)
        pm.start()

    nverifiers = 5
    for i in range(nverifiers):
        pm = ProcessManager(verifier, (mi.copy_as(MADDR_VERIFIER),), 'verifier%d' % i, restart=True)
        pm.start()

    from duckietown_swarm.brain import brain

    server = ('frankfurt.co-design.science', 6667)
    channel = '#duckiebots'
    if use_irc:
        pm = ProcessManager(start_irc,
                            (mi.copy_as(MADDR_IRC), server, channel),
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
                        (mi.copy_as(MADDR_BRAIN), cache_dir), 'brain',
                        restart=True)
    brainp.start()

    pm = ProcessManager(directory_watcher,
                        (mi.copy_as(MADDR_DIRWATCHER), watch_dir), 'directory_watcher',
                        restart=True)
    pm.start()

    pm = ProcessManager(pubsub_friendship,
                        (mi.copy_as(MADDR_PUBSUBFRIENDS),), 'pubsub_friendship',
                        restart=True)
    pm.start()

#    pm = ProcessManager(publisher_summary,
#                        (mi, '/dswarm/summary'), 'publisher_summary',
#                        restart=True)
#    pm.start()

    brainp.p.join()


if __name__ == "__main__":
    duckietown_swarm_main()
