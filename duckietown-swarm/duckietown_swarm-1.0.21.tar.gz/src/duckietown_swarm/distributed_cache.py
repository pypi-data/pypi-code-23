from Queue import Empty
from duckietown_swarm.ipfs_utils import IPFSInterface
import os
import shelve
import time


def brain(cache_dir):

    from duckietown_swarm.irc2 import Queues
    dc = DistributedCache(cache_dir)

    print('From cache: %s files' % len(dc.known))

    ipfsi = IPFSInterface()
    recursive, indirect = ipfsi.pin_ls()

    pinned = recursive | indirect
#    print('pinned: %s' % pinned)
    # send all to pinner and summarizer
    dc.send_all(pinned)

    try:
        while True:
            try:
                msg = Queues.incoming.get(block=False, timeout=5.0)
                dc.interpret(msg)
            except Empty:
                pass
            # print('brain recv: %r' % msg)

            messages = dc.rebroadcast()
            for m in messages:
                # print('brain send: %r' % m)
                for q in Queues.outgoing:
                    q.put(m)

            dc.sync()

    finally:
        print('Clean up cache')
        dc.close()


class DistributedCache(object):

    def __init__(self, cache_dir):
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        fname = os.path.join(cache_dir, '.cache.shelve')
        print('cache: %s' % fname)
        self.shelf = shelve.open(fname, writeback=True)

        try:
            self._init()
        except:
            print('Retting cache')
            os.unlink(fname)
            self.shelf = shelve.open(fname, writeback=True)
            self._init()

    def _init(self):
        self.shelf['known'] = self.known = self.shelf.get('known', set())
        self.shelf['last_mentions'] = self.last_mentions = self.shelf.get('last_mentions', {})

        self.last_broadcast = 0

    def sync(self):
        self.shelf['known'] = self.known
        self.shelf['last_mentions'] = self.last_mentions
        self.shelf.sync()

    def close(self):
        self.shelf.close()

    def send_all(self, pinned=set([])):
        self.pinned = pinned
        from duckietown_swarm.irc2 import Queues
        for ipfs in self.known:
            if not ipfs in self.pinned:
                Queues.pinner_queue.put(ipfs)

            Queues.to_summary_publisher.put(ipfs)

    def interpret(self, msg):
        from duckietown_swarm.irc2 import Queues

        if msg['mtype'] == 'advertise':
            ipfs = msg['details']['ipfs']
            ipfs = str(ipfs)

            self.last_mentions[ipfs] = time.time()

            if not ipfs in self.known:
                self.known.add(ipfs)

                if not ipfs in self.pinned:
                    Queues.pinner_queue.put(ipfs)

                Queues.to_summary_publisher.put(ipfs)

    def rebroadcast(self):
        """ Returns a list of messages """
        h = list(self.known)

        def key(x):
            if x in self.last_mentions:
                return self.last_mentions[x]
            else:
                return 0

        sort = sorted(h, key=key)
        messages = []
        for hashed in sort:
            messages.extend(self._consider_broadcasting(hashed))
        return messages

    def _consider_broadcasting(self, hashed):
        # suppose we want to have a target rate of
        target_rate = 0.33  # messages/s
        # then if we know there are
        # nusers = self.nusers
        nusers = 3  # XXX
        # on average each one should transmit
        min_interval = target_rate / nusers

        min_interval = max(min_interval, 10)

        max_delta = 30
        if not hashed in self.last_mentions:
            do = True
            delta = -1

#            print('%s rebroadcasting because never seen' % (hashed))
        else:
            delta = time.time() - self.last_mentions[hashed]
            do = delta > max_delta
#            if do:
#                print('%s rebroadcasting because delta = %s' % (hashed, delta))
        if do:
            time_since = time.time() - self.last_broadcast
            if time_since > min_interval:
                msg = {'mtype': 'advertise',
                       'details': {'bucket': 'files',
                                      'ipfs': hashed,
                                      'comment': "rebroadcast (after %.1f s)" % delta}}
                self.last_mentions[hashed] = time.time()
                self.last_broadcast = time.time()
                return [msg]
        return []
