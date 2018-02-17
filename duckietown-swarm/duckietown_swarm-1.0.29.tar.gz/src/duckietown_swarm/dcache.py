'''

    Messages
    --------

    There are two primitives:


        propose(dcaddress, string, [t0, t1])
        dismiss(dcaddress, string, [t0, t1])


    where:

        dcaddress = [bucket1, bucket2, ...]
        validity = [from, to] or [null, to] or [from, null]

    The semantics of

        propose([bucket1, bucke2], string, [t0, t1])
        state['bucket1']['bucket2'].add(string)

        so that it is true that

            string in state['bucket1']['bucket2'] for t0 < t < t1

    This is true, unless a "dismiss" or "replace" command is given.

    Summaries
    ---------

    There is a message:

        ask-summary
        summary(ipfs)

    where ipfs is the multihash of a list of YAML messages to be interpreted.


    Signatures
    -------

        {mtype:'signed', what='QmContent', peerid='QmPublicKeyHash', signature='...'}

    Envelope
    -------

    There is some meta-information associated:

        signatures: a list of signatures



    Signature
    ---------

    A signature has:

        ID: (hash of public key)
        Signature: bytes
        Validity: [t0, t1]

    Routing
    -------

    channels: channels in which this was circulated, or None



    Python API querying
    ========

    In Python, a dcaddress is represented by a tuple of strings.

        dcaddress = ('my', 'prefix')

    A client is able to query as follows:

        h = storage.dca(dcaddress)

    List the contents

        ss = storage.list(dcprefix)

        for s in sl:
            s.data        # data
            s.validity    # t0, inf
            s.channels    # channels this was received from
            s.signatures  # collected signatures

    Distributed authenticated sets

        peer [PeerID]  The host HASH is a Duckiebot

            propose: peer
            dismiss: admin

        trusted [PeerID]

            propose: admin
            dismiss: admin

        admin [PeerID]

            propose: mama
            dismiss: mama

        summary [Hash]

            propose: anybody
            dismiss: trusted

        networks

            propose: admin
            dismiss: admin

            examples:

                /irc/address
                /udp/address

        files / HASH

            propose: anybody
            dismiss: trusted

        uploads / HASH

            propose: trusted
            dismiss: trusted

        propose('files', ipfs)
        dismiss('files', ipfs)

        propose('valid', ipfs)
        dismiss('valid', ipfs)
        replace('valid', ifps1, ipfs2)

        propose('summary', H('irc1'))

        propose('network', H('irc1'))
        propose('network', H('irc1'))

        propose(ipfs_host, 'role')



    Addresses

    /duckieswarm/<ID>/verifier
    /duckieswarm/<ID>/brain

    /dns4/frankfurt.co-design.science/tcp/6667/irc/#duckiebots
    /dns4/frankfurt.co-design.science/tcp/6667/irc/NickName
    /ip4/10.0.0.0/udp/6060/duckieswarmcall

'''
from collections import defaultdict, OrderedDict
import json
import os
import shelve
import time

import base58
from contracts import contract
from contracts.utils import raise_wrapped, indent

from .dcache_wire import CouldNotInterpret, interpret_message, MsgPropose
from .dcache_wire import MsgDismiss, MsgSignature, \
    create_propose_message
from .utils import pretty_print_dictionary, friendly_time_since, \
    duration_compact


class Envelope(object):

    def __init__(self, maddr_from, maddr_to, contents, comment=None):
        self.maddr_from = maddr_from
        self.maddr_to = maddr_to
        self.contents = contents
        self.comment = comment

    def __repr__(self):
        return 'Envelope(from: %s, to: %s, %s, %s)' % (self.maddr_from if self.maddr_from else '@',
                                                   self.maddr_to if self.maddr_to else '@',
                                                   self.comment if self.comment else '(nc)',
                                                   self.contents)

    def verbose(self):
        od = OrderedDict()
        od['from'] = self.maddr_from.__repr__()
        od['to'] = self.maddr_to.__repr__()
        od['payload'] = self.contents.__repr__()
        if self.comment:
            od['comment'] = self.comment.__repr__()
        return 'Envelope' + '\n' + indent(pretty_print_dictionary(od), '  ')

    def to_json(self):
        od = OrderedDict()
        od['from'] = self.maddr_from
        od['to'] = self.maddr_to
        od['payload'] = self.contents
        if self.comment:
            od['comment'] = self.comment
        s = json.dumps(od)
        return s

    @staticmethod
    def from_json(s):
        od = json.loads(s)
        payload = str(od['payload'])
        comment = od.get('comment', None)
        return Envelope(str(od['from']), str(od['to']), payload, comment=comment)


class NoSuchBucket(Exception):
    pass


def expired(validity):
    _, t1 = validity
    if t1 is None:
        return False
    return time.time() > t1


class BucketDataItem(object):

    def __init__(self):
        self.validity2signatures_propose = defaultdict(set)
        self.validity2signatures_dismiss = defaultdict(set)
        self.last_broadcast = {}

    def propose(self, validity, signatures, from_channel):
        self.validity2signatures_propose[validity].update(signatures)
        self.last_broadcast[from_channel] = time.time()

    def dismiss(self, validity, signatures, from_channel):
        self.validity2signatures_dismiss[validity].update(signatures)
        self.last_broadcast[from_channel] = time.time()

    def cleanup(self):
        for validity in list(self.validity2signatures_propose):
            if expired(validity):
                self.validity2signatures_propose.pop(validity)
        for validity in list(self.validity2signatures_dismiss):
            if expired(validity):
                self.validity2signatures_dismiss.pop(validity)

    def summary(self):
        res = []

        def time_friendly(delta):
            if delta > 0:
                return duration_compact(delta)
            else:
                return duration_compact(-delta) + ' ago'

        def interval_friendly(interval):
            t0, t1 = interval
            if t0:
                d0 = time_friendly(time.time() - t0)
            else:
                d0 = "forever"
            if t1:
                d1 = time_friendly(t1 - time.time())
            else:
                d1 = 'forever'
            return '[from %s ago to %s in the future]' % (d0, d1)

        for interval, signatures in self.validity2signatures_propose.items():
            msg = 'propose %s by %s' % (interval_friendly(interval), signatures)
            res.append(msg)
        for interval, signatures in self.validity2signatures_dismiss.items():
            msg = 'dismiss %s by %s' % (interval_friendly(interval), signatures)
            res.append(msg)

        for channel, last in self.last_broadcast.items():
            res.append('seen in %s: %s ago' % (channel, friendly_time_since(last)))

        return "\n".join(res)

    def valid(self, at):
        for validity, _signatures in self.validity2signatures_dismiss.items():
            if in_interval(validity, at):
                return False
        for validity, _signatures in self.validity2signatures_propose.items():
            if in_interval(validity, at):
                return True
        return False


def in_interval(interval, at):
    t0, t1 = interval
    ok1 = t0 is None or t0 <= at
    ok2 = t1 is None or at <= t1
    return ok1 and ok2


class Bucket(object):

    @contract(allowed='seq(str)')
    def __init__(self, allowed=[]):
        self.children = OrderedDict()
        self.allowed = list(allowed)
        self.data2dataitem = defaultdict(BucketDataItem)
        self.hook_proposed = []
        self.hook_dismissed = []

    def __getstate__(self):
        return {'children': self.children,
                'allowed': self.allowed,
                'data2dataitem': self.data2dataitem,
                'hook_proposed': [],
                'hook_dismissed': []}

    def cleanup(self):
        for data, dataitem in list(self.data2dataitem.items()):
            dataitem.cleanup()
            if (not dataitem.validity2signatures_propose and
                not dataitem.validity2signatures_dismiss):
                del self.data2dataitem[data]

    def summary(self):

        res = OrderedDict()

        if self.children:
            od = OrderedDict()
            for k, v in self.children.items():
                od[k] = v.summary()

            res['children:'] = pretty_print_dictionary(od)

        if self.data2dataitem:
            od = OrderedDict()
            for data, dataitem in self.data2dataitem.items():
                od[data.__repr__()] = dataitem.summary()
            res['data:'] = pretty_print_dictionary(od)

        return pretty_print_dictionary(res)

    def _is_allowed(self, roles):
        if not self.allowed:
            return True
        else:
            for a in self.allowed:
                if a in roles:
                    return True
            return False

    def propose(self, data, validity, roles, from_channel):
        if not self._is_allowed(roles):
            msg = 'Propose with invalid options: allowed = %s; roles = %s' % (self.allowed, roles)
            raise ProcessFailure(msg)
        found = data in self.data2dataitem
        ditem = self.data2dataitem[data]
        ditem.propose(validity, roles, from_channel)

        if not found:
            for hook in self.hook_proposed:
                hook(data)

    def dismiss(self, data, validity, roles, from_channel):
        if not self._is_allowed(roles):
            msg = 'Propose with invalid options: allowed = %s; roles = %s' % (self.allowed, roles)
            raise ProcessFailure(msg)
        ditem = self.data2dataitem[data]
        ditem.dismiss(validity, roles, from_channel)

        for hook in self.hook_dismissed:
            hook(data)

    def query(self, at):
        found = []
        for data, dataitem in self.data2dataitem.items():
            if dataitem.valid(at):
                found.append(data)
        return found

    def add_child_bucket(self, name, allowed):
        bucket = Bucket(allowed)
        self.children[name] = bucket

    def items(self):
        for k, child in self.children.items():
            yield (k,), child
            for n1, c1 in child.items():
                yield (k,) + n1, c1

    @contract(add='str|(tuple,seq(str))')
    def get_bucket(self, add, create_if_not_exists):
        if isinstance(add, str):
            add = (add,)
        try:
            return self._get_bucket(add, create_if_not_exists)
        except KeyError as e:
            msg = 'Could not resolve bucket "%s": invalid key %s.' % ("/".join(add), e)
            msg += '\n create_if_not_exists: %s' % create_if_not_exists
            raise_wrapped(NoSuchBucket, e, msg)

    def _get_bucket(self, add, create_if_not_exists):
        if not add:
            return self
        name = add[0]
        rest = add[1:]
        if create_if_not_exists and (not name in self.children):
            self.children[name] = Bucket(allowed=[])
        return self.children[name]._get_bucket(rest, create_if_not_exists)


class ProcessFailure(Exception):
    pass


def get_sha256_base58(contents):
    import hashlib
    m = hashlib.sha256()
    m.update(contents)
    s = m.digest()
    return base58.b58encode(s)


class Stats():

    def __init__(self):
        self.num_sent = 0
        self.num_received = 0
        self.last_sent = 0
        self.last_received = 0

    def get_last_activity(self):
        return max(self.last_sent, self.last_received)

    def just_received(self):
        self.num_received += 1
        self.last_received = time.time()

    def just_sent(self):
        self.num_sent += 1
        self.last_sent = time.time()

    def __repr__(self):
        s = []
        if self.num_sent == 0:
            s.append('(never)')
        else:
            s.append('recv %3d  %s' % (self.num_sent, friendly_time_since(self.last_sent)))

        if self.num_received == 0:
            s.append('(never)')
        else:
            s.append('sent %3d  %s' % (self.num_received, friendly_time_since(self.last_received)))

        s = [_.ljust(23) for _ in s]
        return " | ".join(s)


class DistributedRepo(object):

    def __init__(self):
        self.root = Bucket()
        self._set_time_function(time.time)

        self.signatures = defaultdict(dict)
        self.cache_dir = None
        self.all_channels = defaultdict(Stats)

    def use_cache_dir(self, cache_dir):
        fname = os.path.join(cache_dir, '.cache.shelve')
        print('using cache: %s' % fname)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        self.shelf = shelve.open(fname, writeback=True)

        try:
            self._init()
        except Exception as e:
            print(e)
            print('Resetting cache')
            os.unlink(fname)
            self.shelf = shelve.open(fname, writeback=True)
            self._init()

    def close(self):
        self.sync()
        self.shelf.close()

    def sync(self):
        self.shelf['root'] = self.root
        self.shelf.sync()

    def _init(self):
        self.shelf['root'] = self.root = self.shelf.get('root', self.root)
        self.shelf['signatures'] = self.signatures = self.shelf.get('signatures', self.signatures)
#        self.shelf['last_mentions'] = self.last_mentions = self.shelf.get('last_mentions', {})

    @staticmethod
    def get_data_hash(data):
        return get_sha256_base58(data)

    def _set_time_function(self, f):
        self._time_function = f

    def _get_roles_endorsing(self, wm, at):
        signatures = self._get_signatures(wm)
        roles = set()
        for s in signatures:
            roles.update(self._roles_from_signatures(s, at))
        if not roles:
            roles = set(['unknown'])
        return roles

    def _get_signatures(self, msg):
        hashed = get_sha256_base58(msg)
        if hashed in self.signatures:
            signatures = self.signatures[hashed]
            return list(signatures)
        else:
            return []

    def _roles_from_signatures(self, peerid, at=None):
        if at is None:
            at = time.time()
        roles = ['admin', 'trusted', 'peer']
        result = set()
        for role in roles:
            bucket = self.root.get_bucket(role, create_if_not_exists=False)
            contents = bucket.query(at)
            if peerid in contents:
                result.add(role)
        if not result:
            result = ['unknown']
        return set(result)

    def _add_signature(self, signer, data, signature):
        # todo: validate
#        expect = get_sha256_base58("")
#        if len(data) != len(expect):
#            msg = 'Invalid hash %s' % expect.__repr__()
#            raise ValueError(msg)
        self.signatures[data][signer] = signature

    def add_hook_proposed(self, buckets, f):
        if isinstance(buckets, str):
            buckets = (buckets,)
        bucket = self.root.get_bucket(buckets, create_if_not_exists=False)
        bucket.hook_proposed.append(f)

    def add_hook_dismissed(self, buckets, f):
        if isinstance(buckets, str):
            buckets = (buckets,)
        bucket = self.root.get_bucket(buckets, create_if_not_exists=False)
        bucket.hook_dismissed.append(f)

    def summary(self):
        od = OrderedDict()
        if False:
            if self.signatures:
                s = []
                for data_hash, signatures in self.signatures.items():
                    s.append('%s: %s' % (data_hash, signatures))
                od['signatures'] = "\n".join(s)
        od['buckets'] = self.root.summary()

        s = []
        ordered = sorted(self.all_channels, key=lambda k:-self.all_channels[k].last_received)
        for channel in ordered:
            stats = self.all_channels[channel]
            s.append('%10s: %s' % (stats, channel))
        od['activity'] = "\n".join(s)

        return pretty_print_dictionary(od)

    @contract(buckets='seq(str)', allowed='seq(str)')
    def init_bucket(self, buckets, allowed):
        if isinstance(buckets, str):
            buckets = (buckets,)
        buckets = tuple(buckets)
        prev = buckets[:-1]
        name = buckets[-1]
        parent = self.root.get_bucket(prev, create_if_not_exists=True)
        parent.add_child_bucket(name, allowed)
        print('initialized bucket %s' % "/".join(buckets))

    @contract(wm=str)
    def process(self, wm, from_channel, at=None):
        # print('process from %s: %s' % (from_channel, wm))
        if at is None:
            at = time.time()
        self.all_channels[from_channel].just_received()
        try:
            m = interpret_message(wm)
        except CouldNotInterpret as e:
            msg = 'Could not process message.'
            msg += '\n\n' + indent(wm, '  ') + '\n'
            raise_wrapped(ProcessFailure, e, msg, compact=True)

        try:
            if isinstance(m, MsgPropose):
                buckets = m.buckets
                data = m.data
                validity = m.validity
                bucket = self.root.get_bucket(buckets, create_if_not_exists=True)
#                roles = self._get_roles_endorsing(wm, at)
                signatures = self._get_signatures(wm)
                bucket.propose(data, validity, signatures, from_channel)
            elif isinstance(m, MsgDismiss):
                buckets = m.buckets
                data = m.data
                validity = m.validity
                bucket = self.root.get_bucket(buckets, create_if_not_exists=True)
                signatures = self._get_signatures(wm)
#                roles = self.signatures(wm, at)
                bucket.dismiss(data, validity, signatures, from_channel)
            elif isinstance(m, MsgSignature):
                self._add_signature(signer=m.signer, data=m.data, signature=m.signature)
            else:
                msg = 'Could not process class "%s".' % type(wm).__name__
                msg += '\n\n' + indent(wm, '  ') + '\n'
                raise ProcessFailure(msg)
        except NoSuchBucket as e:
            msg = 'Could not find bucket.'
            msg += '\n\n' + indent(wm, '  ') + '\n'
            raise_wrapped(ProcessFailure, e, msg, compact=True)

    def query(self, bucket, at=None):
        '''
            Iterates when
        '''
        if at is None:
            at = time.time()
        if isinstance(bucket, str):
            bucket = (bucket,)
        bucket = self.root.get_bucket(bucket, create_if_not_exists=False)
        return bucket.query(at)

    def cleanup(self):
        for _bucket_name, bucket in self.root.items():
            bucket.cleanup()

    @contract(returns='seq($Envelope)')
    def rebroadcast(self, bucket_name, channels, min_delta=30, min_silence=5, max_n=1):
        from duckietown_swarm.brain import ALL_BRAINS
        options = []

        bucket = self.root.get_bucket(bucket_name, create_if_not_exists=False)
        datas = bucket.query(at=time.time())
        for data in datas:
            dataitem = bucket.data2dataitem[data]
            for channel in channels:
                last_activity = self.all_channels[channel].get_last_activity()

                last = dataitem.last_broadcast.get(channel, 0)
                enough_silence = time.time() - last_activity > min_silence
                if not enough_silence:
                    continue
                need_update = time.time() - last > min_delta
                if need_update:
                    validity = list(dataitem.validity2signatures_propose)[0]
                    msg = create_propose_message(bucket_name, data, validity=validity)
                    options.append((last, Envelope('', channel + ALL_BRAINS, msg)))
                    dataitem.last_broadcast[channel] = time.time()
                    self.all_channels[channel].just_sent()

        s = [_[1] for _ in sorted(options, key=lambda _: _[0])]
        s = s[:max_n]
        return s


class ChannelStats(object):

    @contract(last_seen=float, signatures=set)
    def __init__(self, last_seen, signatures):
        self.last_seen = last_seen
        self.signatures = signatures


class CryptoKey(object):

    def __init__(self, private, public):
        self.private = private
        self.public = public
        self.hash = get_sha256_base58(public)

    def sign_hash(self, data):
        ''' Computes hash of data and then sign it '''
        return '%s signed by %s' % (data, self.hash)

    def generate_sign_message(self, data):
        from .dcache_wire import create_signature_message
        data_hash = get_sha256_base58(data)
        signer = self.hash
        signature = base58.b58encode(self.sign_hash(data_hash))
        msg = create_signature_message(data_hash, signer, signature)
        return msg

