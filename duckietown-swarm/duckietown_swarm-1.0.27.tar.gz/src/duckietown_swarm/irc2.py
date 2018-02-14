#! /usr/bin/env python

from duckietown_swarm.dcache_wire import put_in_queue
from duckietown_swarm.pinner import verifier
from duckietown_swarm.utils import get_at_least_one
from multiprocessing import  Queue
import os
import sys

from contracts import contract

from .directory_watcher_imp import directory_watcher
from .irc_talker import start_irc
from .pinner import pinner
from .process_manager import ProcessManager
from .pubsub_friends import pubsub_friendship
from .pubsub_processes import pubsub_reader_process, \
    pubsub_writer_process
from .summary import publisher_summary


class MessagingInterface():

    def __init__(self, name2queue):
        self.name2queue = name2queue

    @contract(from_channel=str, msg=str)
    def send_to_brain(self, from_channel, msg):
        self.send_to_channel('to_brain', (from_channel, msg))

    @contract(returns='list')
    def get_for_brain(self):
        q = self.name2queue['to_brain']
        return get_at_least_one(q, timeout=5.0)

    @contract(mh=str)
    def send_to_pinner(self, mh):
        self.send_to_channel('to_pinner', mh)

    def get_for_pinner(self):
        q = self.name2queue['to_pinner']
        return q.get()

    @contract(mh=str)
    def send_to_verifier(self, mh):
        self.send_to_channel('to_verifier', mh)

    def get_for_verifier(self):
        q = self.name2queue['to_verifier']
        return q.get()

    @contract(returns='str')
    def get_for_pubsub_writer(self):
        q = self.name2queue['to_pubsub']
        _, m = q.get()
        return m

    @contract(key=str, mh=str)
    def send_to_ipns_publisher(self, key, mh):
        assert mh.startswith('Qm'), (key, mh)
        self.send_to_channel('to_ipns', (key, mh))

    def send_to_channel(self, channel_name, msg):
        q = self.name2queue[channel_name]
        print('->%s: %s' % (channel_name, msg))
        q.put(msg, block=False)

    @contract(channel_message='tuple')
    def send_to_matching_channels(self, channel_message):
        to_channel, _ = channel_message
        n = 0
        for name, q in self.name2queue.items():
            if name in to_channel:
                put_in_queue(q, channel_message)
                n += 1
        if n == 0:
            msg = 'Could not find channel %r' % to_channel
            raise Exception(msg)


def duckietown_swarm_main():
    from duckietown_swarm.summary import publish_ipns
    args = sys.argv[1:]
    if not args:
        watch_dir = os.path.expanduser('~/shared-logs')
    else:
        watch_dir = args[0]

    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)
    print('You can put any log file in the directory\n\n\t%s\n\nand it will be shared with the swarm.\n\n' % watch_dir)

    '''

        incoming -> [brain] -> outgoing
                               pinner_queue
                    publisher_queue


            pinner_queue -> [pinner] -> pinner

            publisher_queue -> [publisher] -> incoming



        outgoing[0] -> [irc server]
        outgoing[1]
    '''

    name2queue = {}
    pinner_queue = name2queue['to_pinner'] = Queue()
    incoming = name2queue['to_brain'] = Queue()
    outgoing_irc2 = name2queue['to_irc1'] = Queue()
    outgoing_irc1 = name2queue['to_irc2'] = Queue()
    name2queue['to_pubsub'] = Queue()
    outgoing = [name2queue['to_irc1'], name2queue['to_irc2'], name2queue['to_pubsub']]
    to_summary_publisher = name2queue['to_summary_publisher'] = Queue()
    ipns_queue = name2queue['to_ipns'] = Queue()
    name2queue['to_verifier'] = Queue()

    mi = MessagingInterface(name2queue)
    out_queues = outgoing + [incoming]

    pm = ProcessManager(publish_ipns,
                        (name2queue['to_ipns'],), 'publish_ipns',
                        restart=True)
    pm.start()

    pm = ProcessManager(pubsub_reader_process,
                        ('pubsub', mi,), 'pubsub_reader',
                        restart=True)
    pm.start()

    pm = ProcessManager(pubsub_writer_process,
                        (mi,), 'pubsub_writer',
                        restart=True)
    pm.start()

    npinners = 10
    for i in range(npinners):

        pm = ProcessManager(pinner, (mi,), 'pinner%d' % i, restart=True)
        pm.start()

    nverifiers = 5
    for i in range(nverifiers):
        pm = ProcessManager(verifier, (mi,), 'verifier%d' % i, restart=True)
        pm.start()

    from duckietown_swarm.brain import brain

    cache_dir = os.path.join(watch_dir, '.cache')
    servers = [('frankfurt.co-design.science', 6667), ]
    pm = ProcessManager(start_irc,
                        ('to_irc1', servers, mi), 'irc1',
                        restart=True)
    pm.start()

    if False:
        servers = [('irc.freenode.net', 6667), ]
        pm = ProcessManager(start_irc,
                            ('to_irc2', servers, mi), 'irc2',
                            restart=True)
        pm.start()

    brainp = ProcessManager(brain,
                        (cache_dir, mi), 'brain',
                        restart=True)
    brainp.start()

    pm = ProcessManager(directory_watcher,
                        (watch_dir, 'directory_watcher', incoming), 'directory_watcher',
                        restart=True)
    pm.start()

    pm = ProcessManager(pubsub_friendship,
                        ('pubsub_friendship', incoming), 'pubsub_friendship',
                        restart=True)
    pm.start()

    pm = ProcessManager(publisher_summary,
                        (to_summary_publisher, ipns_queue, out_queues), 'publisher_summary',
                        restart=True)
    pm.start()

    brainp.p.join()


if __name__ == "__main__":
    duckietown_swarm_main()
