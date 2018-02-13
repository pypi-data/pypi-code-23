

from Queue import Empty
from duckietown_swarm.ipfs_utils import IPFSInterface
from duckietown_swarm.utils import DoAtInterval
import os
import pickle
import random
import time

from contracts import contract

from .dcache import DistributedRepoSwarm
from .dcache import ProcessFailure, CryptoKey
from .dcache_wire import create_propose_message
from .dcache_wire import put_in_queue
from .utils import get_at_least_one


def brain(cache_dir, incoming, name2queue, queue_publisher):
    ipfsi = IPFSInterface()

    dc = DistributedRepoSwarm()
    dc.use_cache_dir(cache_dir)

    fn = os.path.join(cache_dir, '.key.pickle')
    if not os.path.exists(fn):
        key0 = CryptoKey(str(random.randint(0, 10000)), str(random.randint(0, 10000)))
        with open(fn, 'wb') as f:
            pickle.dump(key0, f)
    with open(fn) as f: key = pickle.load(f)

    identity = key.hash
    identity = ipfsi.ipfs_id()
    print('Identity: %s' % identity)
    t = time.time()

    print('From cache: %s files' % len(dc.query('files')))
    print('From cache: %s verified' % len(dc.query('verified')))

#    ipfsi = IPFSInterface()
#    recursive, indirect = ipfsi.pin_ls()

#    pinned = recursive | indirect
#
#    pinned = set()
#    dc.send_all(pinned)

    def on_new_files(data):
        print('New member of files: %s' % data)
        pass

    def on_new_peer(data):
        print('New peer: %s' % data)
        pass

    dc.add_hook_proposed('peer', on_new_peer)
    dc.add_hook_proposed('files', on_new_files)

    interval_make_summary = DoAtInterval(10)
    DELTA_PEER = 10 * 60
    interval_advertise_peer = DoAtInterval(DELTA_PEER * 0.5)

    try:
        while True:
            if interval_make_summary.its_time():
                summary = dc.summary()
                Q = ipfsi.add_bytes(summary)
                print ('summary %s' % Q)
                queue_publisher.put(('summary2', Q))

            if interval_advertise_peer.its_time():
                msg = create_propose_message('peer', identity, validity=[t, t + DELTA_PEER])
                incoming.put(('self', msg))

            try:
                msgs = get_at_least_one(incoming, timeout=5.0)

                for from_channel, msg in msgs:
                    if not isinstance(msg, str):
                        msg = 'I expected the messages to be string, got %s' % msg
                        raise TypeError(msg)

                    try:
                        dc.process(msg, from_channel=from_channel)
                    except ProcessFailure as e:
                        print(str(e))

            except Empty:
                pass

            messages = []
            messages.extend(dc.rebroadcast('files', ['irc1', 'irc2', 'pubsub']))
            messages.extend(dc.rebroadcast('peer', ['irc1', 'irc2', 'pubsub']))
            messages.extend(dc.rebroadcast('trusted', ['irc1', 'irc2', 'pubsub']))
            messages.extend(dc.rebroadcast('admin', ['irc1', 'irc2', 'pubsub']))

            for channel_message in messages:
                put_in_queues(name2queue, channel_message)

            dc.cleanup()
            dc.sync()

    finally:
        print('Clean up cache')
        dc.close()


@contract(name2queue='dict(str:*)', channel_message='tuple')
def put_in_queues(name2queue, channel_message):
    to_channel, _ = channel_message
    for name, q in name2queue.items():
        if name in to_channel:
            put_in_queue(q, channel_message)

#class DistributedCache(object):
#
#    def __init__(self, cache_dir):
#        if not os.path.exists(cache_dir):
#            os.makedirs(cache_dir)
#
#        fname = os.path.join(cache_dir, '.cache.shelve')
#        print('cache: %s' % fname)
#        self.shelf = shelve.open(fname, writeback=True)
#
#        try:
#            self._init()
#        except:
#            print('Retting cache')
#            os.unlink(fname)
#            self.shelf = shelve.open(fname, writeback=True)
#            self._init()
#
#    def _init(self):
#        self.shelf['known_invalid'] = self.known_invalid = self.shelf.get('known_invalid', set())
#        self.shelf['known'] = self.known = self.shelf.get('known', set())
#        self.shelf['last_mentions'] = self.last_mentions = self.shelf.get('last_mentions', {})
#
#        self.last_broadcast = 0
#
#    def sync(self):
#        self.shelf['known_invalid'] = self.known
#        self.shelf['known'] = self.known
#        self.shelf['last_mentions'] = self.last_mentions
#        self.shelf.sync()
#
#    def close(self):
#        self.shelf.close()
#
#    def send_all(self, pinned=set([])):
#        self.pinned = pinned
#        from duckietown_swarm.irc2 import Queues
#        for ipfs in list(self.known):
#            if ipfs in self.known_invalid:
#                self.known.remove(ipfs)
#            else:
#                if not ipfs in self.pinned:
#                    Queues.pinner_queue.put(ipfs)
#                Queues.to_summary_publisher.put(('add', ipfs))
#
#    def interpret(self, msg):
#        from duckietown_swarm.irc2 import Queues
#
#        if msg['mtype'] == 'advertise-invalid':
#            ipfs = msg['details']['ipfs']
#            ipfs = str(ipfs)
#            if not ipfs in self.known_invalid:
#                print('brain: asking publisher to remove %s' % ipfs)
#                Queues.to_summary_publisher.put(('remove', ipfs))
#                self.known_invalid.add(ipfs)
#                if ipfs in self.known:
#                    self.known.remove(ipfs)
#                if ipfs in self.last_mentions:
#                    del self.last_mentions[ipfs]
#
#        if msg['mtype'] == 'advertise':
#            ipfs = msg['details']['ipfs']
#            ipfs = str(ipfs)
#
#            if ipfs in self.known_invalid:
#                # msg = 'brain: Ignoring known invalid %s' % ipfs
#                print(msg)
#                return
#
#            self.last_mentions[ipfs] = time.time()
#
#            if not ipfs in self.known:
#                self.known.add(ipfs)
#
#                if not ipfs in self.pinned:
#                    print('brain: asking pinner to add %s' % ipfs)
#                    Queues.pinner_queue.put(ipfs)
#
#                print('brain: asking publisher to add %s' % ipfs)
#                Queues.to_summary_publisher.put(('add', ipfs))
#
#    def rebroadcast(self):
#        """ Returns a list of messages """
#        h = list(self.known)
#
#        def key(x):
#            if x in self.last_mentions:
#                return self.last_mentions[x]
#            else:
#                return 0
#
#        sort = sorted(h, key=key)
#        messages = []
#        for hashed in sort:
#            messages.extend(self._consider_broadcasting(hashed))
#        return messages
#
#    def _consider_broadcasting(self, hashed):
#        # suppose we want to have a target rate of
#        target_rate = 0.33  # messages/s
#        # then if we know there are
#        # nusers = self.nusers
#        nusers = 3  # XXX
#        # on average each one should transmit
#        min_interval = target_rate / nusers
#
#        min_interval = max(min_interval, 10)
#
#        max_delta = 30
#        if not hashed in self.last_mentions:
#            do = True
#            delta = -1
#
##            print('%s rebroadcasting because never seen' % (hashed))
#        else:
#            delta = time.time() - self.last_mentions[hashed]
#            do = delta > max_delta
##            if do:
##                print('%s rebroadcasting because delta = %s' % (hashed, delta))
#        if do:
#            time_since = time.time() - self.last_broadcast
#            if time_since > min_interval:
#                msg = {'mtype': 'advertise',
#                       'details': {'bucket': 'files',
#                                      'ipfs': hashed,
#                                      'comment': "rebroadcast (after %.1f s)" % delta}}
#                self.last_mentions[hashed] = time.time()
#                self.last_broadcast = time.time()
#                return [msg]
#        return []
