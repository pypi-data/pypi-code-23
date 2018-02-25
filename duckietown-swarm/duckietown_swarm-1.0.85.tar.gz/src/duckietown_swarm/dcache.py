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
from duckietown_swarm.intervals_utils import interval_friendly, in_interval
from duckietown_swarm.proposals import Proposal, strictly_dominated_by_set, \
    ANONYMOUS
from duckietown_swarm.utils import get_sha256_base58
import itertools
import json
import os
import shelve
import time

from base58 import b58encode, b58decode
from contracts import contract
from contracts.utils import raise_wrapped, indent, raise_desc

from .dcache_wire import CouldNotInterpret, interpret_message, MsgPropose
from .dcache_wire import MsgDismiss, MsgSignature, create_propose_message
from .dcache_wire import MsgPing, MsgPong
from .dcache_wire import create_dismiss_message
from .dcache_wire import create_signature_message
from .utils import pretty_print_dictionary, friendly_time_since

BOOTSTRAP_PATTERNS = ['/peers', '*/summaries', '*/ipfs_addresses', '*/info/*', '*/versions/*']


class Envelope(object):

    @staticmethod
    def encode(s):
#        return base92.b92encode(s)
#        return base85.b85encode(s)
        return s
        return b58encode(s)

    @staticmethod
    def decode(s):
        return s
        return b58decode(s)
#        return base85.b85decode(s)
#        return base92.b92decode(s)

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
        od['payload'] = Envelope.encode(self.contents)
        if self.comment:
            od['comment'] = self.comment
        s = json.dumps(od)
        if len(s) > 512:
            print('warning: size of message is %s' % len(s))
        return s

    @staticmethod
    def from_json(s):
        if not s.startswith('{') or not s.endswith('}'):
            msg = 'The message of length %s appears truncated.' % len(s)
            raise_desc(CouldNotReadEnvelope, msg, s=s.__repr__())
        try:
            od = json.loads(s)
            payload = Envelope.decode(str(od['payload']))
            comment = od.get('comment', None)
            return Envelope(str(od['from']), str(od['to']), payload, comment=comment)
        except Exception as e:
            msg = 'Could not read envelope of length %s.' % len(s)
            raise_wrapped(CouldNotReadEnvelope, e, msg, s=s)


class CouldNotReadEnvelope(Exception):
    pass


class NoSuchBucket(Exception):
    pass


def expired(validity, t=None):
    if t is None:
        t = time.time()
    _, t1 = validity
    if t1 is None:
        return False
    return t > t1


class BucketDataItem(object):

    def __init__(self):
#        self.validity2signatures_propose = defaultdict(set)
        self.validity2signatures_dismiss = defaultdict(set)

        self.proposals_propose = set()

        self.last_broadcast_propose = {}
        self.last_broadcast_dismiss = {}

    @contract(validity='seq[2]')
    def propose(self, validity, signatures, from_channel):
#        print('BucketDataItem %s %s %s' % (validity, signatures, from_channel))
        if not signatures:
            signatures = [ANONYMOUS]
        for s in signatures:
            p = Proposal(validity, s)
            self.propose_(p, from_channel)

    @contract(proposal=Proposal)
    def propose_(self, proposal, from_channel):
        if proposal in self.proposals_propose:
            return
#        else:
#            print('%s is not in %s ' % (proposal, self.proposals_propose))
        dominated_by = strictly_dominated_by_set(proposal, self.proposals_propose)
        if dominated_by:
            return
#            msg = 'Ignoring proposed:'
#            msg += '\n\n' + indent(proposal, '  ')
#            msg += '\n\nBecause dominated by'
#            for d in dominated_by:
#                msg += '\n\n' + indent(d, '  ')
#            print msg
#            return dominated_by

        self.proposals_propose.add(proposal)

#        self.validity2signatures_propose[proposal.validity].update(proposal.signatures)

        if not from_channel in self.last_broadcast_propose:
            self.last_broadcast_propose[from_channel] = Stats()

        self.last_broadcast_propose[from_channel].just_received()

        _cleaned = self.cleanup()

#        if cleaned:
#            msg = 'Cleaning results:\n\n' + indent("\n".join(cleaned), '  ')
#            print msg

#        return cleaned

    def dismiss(self, validity, signatures, from_channel):
        self.validity2signatures_dismiss[validity].update(signatures)
        if not from_channel in self.last_broadcast_dismiss:
            self.last_broadcast_dismiss[from_channel] = Stats()
        self.last_broadcast_dismiss[from_channel].just_received()

#    def is_strictly_dominated(self, proposal):
#        available = set(self.iterate_existing_proposals())
#        return strictly_dominated_by_set(proposal, available)

#    def iterate_existing_proposals(self):
#        for v0, signers in self.validity2signatures_propose.items():
#            yield Proposal(v0, signers)
##            if signers:
#                for s in signers:
#                    yield Proposal(v0, [s])
#            else:
#                yield Proposal(v0, [])

    def cleanup_expired(self, t=None):
        for proposal in list(self.proposals_propose):
            if expired(proposal.validity, t):
                self.proposals_propose.remove(proposal)

        for validity in list(self.validity2signatures_dismiss):
            if expired(validity, t):
                self.validity2signatures_dismiss.pop(validity)

    def cleanup(self):
        cleaned_up = []
        # find all proposals
        dominated = defaultdict(set)
        current = list(self.proposals_propose)
        for c1, c2 in itertools.product(current, current):
            if Proposal.strictly_dominates(c1, c2):
                dominated[c2] = c1

        for proposal, by_what in dominated.items():
            cleaned_up.append('found redundant %s dominated by %s' % (proposal, by_what))
            self.proposals_propose.remove(proposal)
        return cleaned_up

    def is_tombstoned(self):
#        if len(self.validity2signatures_propose) == 0:
        for validity, _dataitem in self.validity2signatures_dismiss.items():
            if in_interval(validity, time.time()) and validity[1] == None:
                return True
        return False

    def summary(self):
        res = []

        if self.is_tombstoned():
            res.append('TOMBSTONED')
#        else:
#            res.append('ACTIVE')

        for proposal in self.proposals_propose:
            msg = 'propose %s by %s' % (interval_friendly(proposal.validity), proposal.who)
            res.append(msg)
        for interval, signatures in self.validity2signatures_dismiss.items():
            msg = 'dismiss %s by %s' % (interval_friendly(interval), signatures)
            res.append(msg)

        for channel, last in self.last_broadcast_propose.items():
            res.append(' %s: %s' % (last, channel))
        for channel, last in self.last_broadcast_dismiss.items():
            res.append('%s: %s' % (last, channel))

        return "\n".join(res)

    def valid(self, at):
        for validity, _signatures in self.validity2signatures_dismiss.items():
            if in_interval(validity, at):
                return False
        for proposal in self.proposals_propose:
            if in_interval(proposal.validity, at):
                return True
        return False


class Bucket(object):

    def __init__(self):
        self.children = OrderedDict()
        self.data2dataitem = defaultdict(BucketDataItem)
        self.hook_proposed = []
        self.hook_dismissed = []

    def __getstate__(self):
        return {'children': self.children,
                'data2dataitem': self.data2dataitem,
                'hook_proposed': [],
                'hook_dismissed': []}

    def cleanup(self):
        cleaned_up = []
        for data, dataitem in list(self.data2dataitem.items()):
            for _ in dataitem.cleanup():
                cleaned_up.append('%s | %s' % (data, _))

            if (not dataitem.proposals_propose and
                not dataitem.validity2signatures_dismiss):
                del self.data2dataitem[data]

        return cleaned_up

    def summary(self):

        res = OrderedDict()

        if self.children:
            od = OrderedDict()
            for k, v in self.children.items():
                od[k] = v.summary()

            res['children:'] = pretty_print_dictionary(od)

        if self.data2dataitem:
            od = OrderedDict()
            ntomb = 0

            for data, dataitem in self.data2dataitem.items():
                if dataitem.is_tombstoned():
                    ntomb += 1
                else:
                    od[data.__repr__()] = dataitem.summary()

            res['data:'] = pretty_print_dictionary(od)
            res['num tombstoned:'] = str(ntomb)

        return pretty_print_dictionary(res)

    @contract(validity='seq[2]')
    def propose(self, data, validity, roles, from_channel):
        found = data in self.data2dataitem
        ditem = self.data2dataitem[data]
        ditem.propose(validity, roles, from_channel)

        if not found:
            for hook in self.hook_proposed:
                hook(dict(data=data, validity=validity, roles=roles, from_channel=from_channel))

    def dismiss(self, data, validity, roles, from_channel):
        ditem = self.data2dataitem[data]
        ditem.dismiss(validity, roles, from_channel)

        for hook in self.hook_dismissed:
            hook(dict(data=data, validity=validity, roles=roles, from_channel=from_channel))

    def query(self, at):
        found = []
        for data, dataitem in self.data2dataitem.items():
            if dataitem.valid(at):
                found.append(data)
        return found

    def add_child_bucket(self, name):
        self.children[name] = Bucket()

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
            self.children[name] = Bucket()
        return self.children[name]._get_bucket(rest, create_if_not_exists)


class ProcessFailure(Exception):
    pass


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
            s.append('')
        else:
            s.append('sent %3d  %s' % (self.num_sent, friendly_time_since(self.last_sent)))

        if self.num_received == 0:
            s.append('')
        else:
            s.append('recv %3d  %s' % (self.num_received, friendly_time_since(self.last_received)))

        s = [_.ljust(23) for _ in s]
        return " | ".join(s)


storage_version = 9


class DistributedRepo(object):

    get_data_hash = get_sha256_base58

    def __init__(self):
        self.root = Bucket()

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
        self.shelf['signatures'] = self.signatures
        self.shelf.sync()

    def _init(self):
        if not 'version' in self.shelf or self.shelf['version'] != storage_version:
            print('Resetting cache because of version')
            for f in ['root', 'signatures']:
                if f in self.shelf:
                    self.shelf.pop(f)

        self.shelf['version'] = storage_version

        self.shelf['root'] = self.root = self.shelf.get('root', self.root)
        self.shelf['signatures'] = self.signatures = self.shelf.get('signatures', self.signatures)

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

    def add_hook_proposed_all(self, f):

        class Wrapper():

            def __init__(self, name, f0):
                self.name = name
                self.f0 = f0

            def __call__(self, d):
                d['bucket_name'] = self.name
                self.f0(d)

        for bucket_name, bucket in self.root.items():
            bucket.hook_proposed.append(Wrapper(bucket_name, f))

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
#        if False:
#            if self.signatures:
#                s = []
#                for data_hash, signatures in self.signatures.items():
#                    s.append('%s: %s' % (data_hash, signatures))
#                od['signatures'] = "\n".join(s)
        od['buckets'] = self.root.summary()

        s = []
        ordered = sorted(self.all_channels, key=lambda k:-self.all_channels[k].last_received)
        for channel in ordered:
            stats = self.all_channels[channel]
            s.append('%10s: %s' % (stats, channel))
        od['activity'] = "\n".join(s)

        return pretty_print_dictionary(od)

    def summary_messages(self):
        ''' Returns a list of strings that represent
            the data so far.
        '''

        out = []

        for bucket_name, _bucket in self.root.items():
            out.extend(self._summary_message_for_bucket(bucket_name))
        return out

    def summary_dict(self):
        ''' Returns a view of the data using simple structures '''

        @contract(D=dict)
        def setit(D, name, what):
            one, rest = name[0], name[1:]
            if not one in D: D[one] = {}
            if not rest:
                D[one] = what
            else:
                a = D[one]
                if not isinstance(a, dict):
                    raise ValueError('a = %s' % str(a))
                setit(a, rest, what)

        d = {}
        for bucket_name, bucket in self.root.items():
            datas = bucket.query(at=time.time())
            what = []
            for data in datas:
                dataitem = bucket.data2dataitem[data]
                if dataitem.is_tombstoned():
                    continue
                what.append(data)

            if what:
                try:
                    setit(d, bucket_name, what)
                except ValueError as e:
                    msg = 'Cannot set value for %s = %s: %s' % (bucket_name, what, e)
                    print(msg)
#                    raise_wrapped(ValueError, e, msg)

        return d

    def _summary_message_for_bucket(self, bucket_name, only_positive=False):
        out = []

        def add(msg):
            data_hash = get_sha256_base58(msg)
            available = self.signatures.get(data_hash, {})
#            if not available:
#                print('no signatures found for %s' % msg)
            for signer, signature in available.items():
                smsg = create_signature_message(data_hash, signer, signature)
                out.append(smsg)

            if not available and bucket_name[0] == 'pri':
                print('Not broadcasting %s because no signature available.' % "/".join(bucket_name))
            else:
#                print('Found signature by %s ' % (signer))
                out.append(msg)

        bucket = self.root.get_bucket(bucket_name, create_if_not_exists=False)
        datas = bucket.query(at=time.time())
        for data in datas:
            dataitem = bucket.data2dataitem[data]
            if dataitem.is_tombstoned():
                continue
            t = time.time()
            if not only_positive:
                for validity, _ in dataitem.validity2signatures_dismiss.items():
                    if validity[1] is None or t <= validity[1]:
                        msg = create_dismiss_message(bucket_name, data, validity)
                        add(msg)

            for proposal in dataitem.proposals_propose:
                if not expired(proposal.validity):
                    msg = create_propose_message(bucket_name, data, proposal.validity)
                    add(msg)
        return out

    @contract(buckets='seq(str)')
    def init_bucket(self, buckets):
        if isinstance(buckets, str):
            buckets = (buckets,)
        buckets = tuple(buckets)
        prev = buckets[:-1]
        name = buckets[-1]
        parent = self.root.get_bucket(prev, create_if_not_exists=True)
        parent.add_child_bucket(name)
#        print('initialized bucket %s' % "/".join(buckets))

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

                if buckets[0] == 'pri' and not (buckets[1] in signatures):
                    msg = 'Not setting %s because signatures=%s (from: %s)' % (buckets, signatures, from_channel)
                    print(msg)
                else:
                    bucket.propose(data, validity, signatures, from_channel)
            elif isinstance(m, MsgDismiss):
                buckets = m.buckets
                data = m.data
                validity = m.validity
                bucket = self.root.get_bucket(buckets, create_if_not_exists=True)
                signatures = self._get_signatures(wm)

                if buckets[0] == 'pri' and not buckets[1] in signatures:
                    msg = 'Not dismissing %s because signatures=%s (from: %s)' % (buckets, signatures, from_channel)
                    print(msg)
                else:
                    bucket.dismiss(data, validity, signatures, from_channel)
            elif isinstance(m, MsgSignature):
                self._add_signature(signer=m.signer, data=m.data, signature=m.signature)
            elif isinstance(m, MsgPing):
                print('ping %s' % from_channel)
            elif isinstance(m, MsgPong):
                print('pong %s' % from_channel)
            else:
                msg = 'Could not process class "%s".' % type(m).__name__
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
            removed = bucket.cleanup()
            if removed:
                print('For %s, removed\n%s' % (_bucket_name, removed))

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

                last = dataitem.last_broadcast_propose.get(channel, Stats()).get_last_activity()
                enough_silence = time.time() - last_activity > min_silence
                if not enough_silence:
                    continue
                need_update = time.time() - last > min_delta
                if need_update:
                    for proposal in dataitem.proposals_propose:
                        validity = proposal.validity
#                        validity = list(dataitem.validity2signatures_propose)[0]
                        # XXX: too many?
                        msg = create_propose_message(bucket_name, data, validity=validity)
                        options.append((last, Envelope('', channel + ALL_BRAINS, msg), data, channel))

        s = [_[1:] for _ in sorted(options, key=lambda _: _[0])]
        s = s[:max_n]

        for _envelope, data, channel in s:
            dataitem = bucket.data2dataitem[data]
            if not channel in dataitem.last_broadcast_propose:
                dataitem.last_broadcast_propose[channel] = Stats()
            dataitem.last_broadcast_propose[channel].just_sent()
            self.all_channels[channel].just_sent()

        return [_[0] for _ in s]


class ChannelStats(object):

    @contract(last_seen=float, signatures=set)
    def __init__(self, last_seen, signatures):
        self.last_seen = last_seen
        self.signatures = signatures

