import duckietown_swarm
import fnmatch
import socket
import time

from contracts import check_isinstance

from .dcache import DistributedRepo, ProcessFailure, interpret_message, Envelope
from .dcache_wire import MsgPing, create_pong_message, \
    MsgRequest, create_dismiss_message, create_propose_message, create_signature_message
from .ipfs_utils import IPFSInterface
from .irc2 import MessagingInterface
from .utils import DoAtInterval, get_sha256_base58


class DistributedRepoSwarm(DistributedRepo):

    def __init__(self):
        DistributedRepo.__init__(self)
        self.init_bucket('networks')
        self.init_bucket('peer')
#        self.init_bucket('trusted')
#        self.init_bucket('admin')

        self.init_bucket('files')
        self.init_bucket('verified')  #
        self.init_bucket('safe')  #

#        self.init_bucket('summaries', allowed=[])  #

        self.init_bucket('pri')  #


MINUTES = 60
ALL_BRAINS = '/dswarm/*/brain'
DELTA_MAKE_SUMMARY = 5 * MINUTES
DAYS = 60 * 60 * 24


def brain(mi, cache_dir):
    check_isinstance(mi, MessagingInterface)

    ipfsi = IPFSInterface(mi.ipfs_path)

    dc = DistributedRepoSwarm()
    dc.use_cache_dir(cache_dir)

    t = time.time()

    proposed = set(dc.query('files'))
    verified = set(dc.query('verified'))
    for p in proposed:
        if not p in verified:
            mi.send_to_verifier(p)

    already_verified = set(dc.query('verified'))
    already_files = set(dc.query('files'))
    print('From cache: %s files' % len(already_files))
    print('From cache: %s verified' % len(already_verified))

    def on_new_files(d):
        data = d['data']
        if not data in already_verified:
            print('New file: %s' % d)
            mi.send_to_verifier(data)
            already_verified.add(data)

    def on_new_peer(d):
        data = d['data']
        print('New peer: %s' % data)
        if data != identity:
            address = '/p2p-circuit/ipfs/' + data
            mi.send_to_connector(address)

    def on_new_verifed(d):
        data = d['data']
        #print('New verified: %s' % data)
        mi.send_to_pinner(data)

    def on_new_summary(d):
        bucket = d['bucket_name']
        data = d['data']
        if bucket[-1] == 'summaries':
            #print('New summary: %s' % d)
            which = bucket[1]
            if which != identity:
                print('Look up from %s %s' % (which, data))
                mi.send_to_readsummaries(data)
        else:
            pass

    IPFS_ADDRESSES = 'ipfs_addresses'

    def on_new_peer_address(d):
        bucket = d['bucket_name']
        data = d['data']
#        print('on_new_peer_address: %s ' % d)
        if bucket[-1] == IPFS_ADDRESSES:
            which = bucket[-2]
            print('on_new_peer_address: %s %s' % (which, data))
            if which != identity:
                mi.send_to_connector(data)
        else:
            pass

#            print('Ignoring new in bucket %s = %s' % (str(bucket), data))

    dc.add_hook_proposed('peer', on_new_peer)
    dc.add_hook_proposed('files', on_new_files)
    dc.add_hook_proposed('verified', on_new_verifed)
    dc.add_hook_proposed_all(on_new_summary)
    dc.add_hook_proposed_all(on_new_peer_address)

    interval_make_summary = DoAtInterval(DELTA_MAKE_SUMMARY)
    DELTA_PEER = 10 * 60
    interval_advertise_peer = DoAtInterval(DELTA_PEER * 0.5)
    interval_addresses = DoAtInterval(10 * 60)
    interval_rebroadcast = DoAtInterval(3 * 60)
    interval_connect = DoAtInterval(5 * 60)

    key = mi.key
    identity = key.hash

    for peer in dc.query('peer'):
        if peer != identity:
            print('trying to connect %s' % peer)
            address = '/p2p-circuit/ipfs/' + peer
            mi.send_to_connector(address)

    try:
        while True:
            if interval_addresses.its_time():
                addresses = ipfsi.get_addresses()
                print('addresses: %s' % addresses)
                for address in addresses:
                    if (address.startswith('/ip4/127.0.0.1/') or
                        address.startswith('/ip6/')):
                        continue
                    t = time.time()
                    msg = create_propose_message(('pri', identity, IPFS_ADDRESSES),
                                                 address, validity=[t, t + 60 * 60])
                    mi.send_to_brain('', msg, sign=True)

            if interval_connect.its_time():
                for t, bucket in dc.root.items():
                    if t[-1] == IPFS_ADDRESSES:
                        if t[-2] == identity: continue
                        for address in bucket.query(time.time()):
                            print('connecting %s' % address)
                            mi.send_to_connector(address)

            if interval_make_summary.its_time():
                periodic_make_summary(dc, mi, identity, ipfsi)

            if interval_advertise_peer.its_time():
                t = time.time()
                msg = create_propose_message('peer', identity, validity=[t, t + DELTA_PEER])
                mi.send_to_brain('', msg, sign=True)

                import platform
                DELTA_INFO = 5 * DAYS
                properties = {}
                properties['hostname'] = socket.gethostname()
                properties['processor'] = platform.processor()
                properties['machine'] = platform.machine()
                properties['node'] = platform.node()
                properties['version/dswarm'] = duckietown_swarm.__version__
                properties['version/python'] = platform.python_version()
                properties['version/ipfs'] = ipfsi.version()

                properties['system'] = platform.system()

                for k, v in properties.items():
                    bucket = ('pri', identity, 'info') + tuple(k.split('/'))
                    msg = create_propose_message(bucket, v, validity=[t, t + DELTA_INFO])
                    mi.send_to_brain('', msg, sign=True)

            envelopes = mi.get_many_for_me(timeout=2)

            for envelope in envelopes:

                try:
                    m = interpret_message(envelope.contents)
                except:
                    pass
                else:
                    if isinstance(m, MsgPing):
                        reply_ping(mi, dc, envelope)

                    elif isinstance(m, MsgRequest):
                        reply_msg_request(mi, dc, envelope, m)

                    else:
                        try:
                            dc.process(envelope.contents, envelope.maddr_from)
                        except ProcessFailure as e:
                            em = 'Cannot interpret message: '
                            em += '\n' + str(e)
                            print(em)

            if interval_rebroadcast.its_time():
                periodic_rebroadcast(mi, dc)

            dc.cleanup()
            dc.sync()

    finally:
        print('Clean up cache')
        dc.close()


last_summary = None


def periodic_make_summary(dc, mi, identity, ipfsi):
    global last_summary
    summary_humans = dc.summary()
    summary_humans = summary_humans.replace(identity, 'QmSELF')
    summary_messages = dc.summary_messages()

    summary = ipfsi.get_tree_builder()
    summary.add_file_content('humans.txt', summary_humans)
    summary.add_file_content('machines.txt', '\n'.join(summary_messages))
    Q = summary.get_hash()

    bucket = ('pri', identity, 'summaries')
    t = time.time()
    if last_summary is not None:
        msg = create_dismiss_message(bucket, last_summary, validity=[t, None])
        mi.broadcast_to_all_brains(msg, sign=True)

    validity = [t, t + DELTA_MAKE_SUMMARY * 2]
    msg = create_propose_message(bucket, Q, validity)
    mi.broadcast_to_all_brains(msg, sign=True)

    last_summary = Q
    print('summary: %s' % last_summary)


def periodic_rebroadcast(mi, dc):
    messages = []

    for t, _ in dc.root.items():
        out_channels = mi._get_broadcasting_channels()
        these = dc.rebroadcast(t, out_channels)

        messages.extend(these)

    for envelope in messages:
        # find signatures
        hashed = get_sha256_base58(envelope.contents)
        if hashed in dc.signatures:
            for signer, signature in dc.signatures[hashed].items():
                msg = create_signature_message(hashed, signer, signature)
                e_sign = Envelope(envelope.maddr_from, envelope.maddr_to, msg)
                mi.dispatch(e_sign)
        mi.dispatch(envelope)


def reply_msg_request(mi, dc, envelope, m):
    messages = []
    patterns = m.patterns

    if mi.my_maddr in envelope.maddr_from:
        msg = 'Ignoring request from ourselves.'
        print(msg)
        return
    print('received request: %s' % envelope)
    print('patterns: %s' % str(patterns))

    def matches(x):
        for pattern in patterns:
            if fnmatch.fnmatch(x, pattern):
                return True
        return False

    for bucket_name, _bucket in dc.root.items():
        c = "/" + "/".join(bucket_name)
#        print('looking for %s' % str(bucket_name))
        if not matches(c):
#            print('%s does not match %s' % (c, patterns))
            continue
        out = dc._summary_message_for_bucket(bucket_name, only_positive=True)
#        print(bucket.summary())

        messages.extend(out)

#    messages = sorted(messages, key=lambda _: _[0])
#    for m in messages:
#        print m
#    messages = [_[1] for _ in messages]
#    messages = list(set(messages))

    print('Sending %d messages in response to query %s' % (len(messages), patterns))
    for msg in messages:
        e = Envelope('', envelope.maddr_from, msg)
        mi.dispatch(e)

    pong = create_pong_message()
    e = Envelope('', envelope.maddr_from, pong)
    mi.dispatch(e)


def reply_ping(mi, _, envelope):
    pong = create_pong_message()
    e = Envelope('', envelope.maddr_from, pong)
    mi.dispatch(e)
