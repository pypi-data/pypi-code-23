import time


def brain():
    from duckietown_swarm.irc2 import Queues
    dc = DistributedCache()
    while True:
        msg = Queues.incoming.get()
        # print('brain recv: %r' % msg)
        dc.interpret(msg)
        messages = dc.rebroadcast()
        for m in messages:
            # print('brain send: %r' % m)
            for q in Queues.outgoing:
                q.put(m)


class DistributedCache():

    def __init__(self):
        self.known = set()
        # last mentions
        self.last_mentions = {}
        self.last_broadcast = 0

    def interpret(self, msg):
        from duckietown_swarm.irc2 import Queues

        if msg['mtype'] == 'advertise':
            ipfs = msg['details']['ipfs']
            ipfs = str(ipfs)

            self.last_mentions[ipfs] = time.time()

#            if not ipfs in list(self.seen.values()):
            if not ipfs in self.known:
                self.known.add(ipfs)
                Queues.pinner_queue.put(ipfs)

#                self._update_summary()

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

#        max_delta = 30 + self.lateness

        max_delta = 0  # always
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
