#! /usr/bin/env python

from multiprocessing import  Queue
import os
import sys

from .directory_watcher_imp import directory_watcher
from .irc_talker import start_irc
from .pinner import pinner
from .process_manager import ProcessManager
from .pubsub_friends import pubsub_friendship
from .pubsub_processes import pubsub_reader_process, \
    pubsub_writer_process
from .summary import publisher_summary


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

    incoming = Queue()
    pinner_queue = Queue()
    outgoing_irc1 = Queue()
    outgoing_irc2 = Queue()
    outgoing_pubsub = Queue()
    name2queue = {}
    name2queue['irc1'] = outgoing_irc1
    name2queue['irc2'] = outgoing_irc2
    name2queue['pubsub'] = outgoing_pubsub
    outgoing = [outgoing_irc1, outgoing_irc2, outgoing_pubsub]
    out_queues = outgoing + [incoming]
    to_summary_publisher = Queue()
    ipns_queue = Queue()

    pm = ProcessManager(publish_ipns,
                        (ipns_queue,), 'publish_ipns',
                        restart=True)
    pm.start()

    pm = ProcessManager(pubsub_reader_process,
                        ('pubsub', incoming,), 'pubsub_reader',
                        restart=True)
    pm.start()

    pm = ProcessManager(pubsub_writer_process,
                        ('pubsub_writer', outgoing_pubsub,), 'pubsub_writer',
                        restart=True)
    pm.start()

    npinners = 10
    for i in range(npinners):

        pm = ProcessManager(pinner,
                            (i, pinner_queue, out_queues), 'pinner%d' % i,
                            restart=True)
        pm.start()

    from duckietown_swarm.brain import brain

    cache_dir = os.path.join(watch_dir, '.cache')
    servers = [('frankfurt.co-design.science', 6667), ]
    pm = ProcessManager(start_irc,
                        ('irc1', servers, incoming, outgoing_irc1), 'irc1',
                        restart=True)
    pm.start()

    if False:
        servers = [('irc.freenode.net', 6667), ]
        pm = ProcessManager(start_irc,
                            ('irc2', servers, incoming, outgoing_irc2), 'irc2',
                            restart=True)
        pm.start()

    brainp = ProcessManager(brain,
                        (cache_dir, incoming, name2queue, ipns_queue), 'brain',
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
