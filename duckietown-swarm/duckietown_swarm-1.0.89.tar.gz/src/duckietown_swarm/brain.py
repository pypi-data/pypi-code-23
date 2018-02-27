import duckietown_swarm
import fnmatch
import socket
import sys
import time

from contracts import check_isinstance
from contracts.utils import indent

from .constants import DSwarmConstants
from .dcache import DistributedRepo, ProcessFailure, interpret_message, Envelope
from .dcache_wire import MsgCommand
from .dcache_wire import MsgPing, create_pong_message, \
    MsgRequest, create_dismiss_message, create_propose_message, create_signature_message
from .ipfs_utils import IPFSInterface
from .irc2 import MessagingInterface
from .udp_interface import get_mac_addresses
from .utils import DoAtInterval, get_sha256_base58
from .utils import as_seconds

DSC = DSwarmConstants


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

        self.init_bucket(DSC.PRI)  #


def brain(mi, cache_dir):
    check_isinstance(mi, MessagingInterface)

    ipfsi = IPFSInterface(mi.ipfs_path)

    dc = DistributedRepoSwarm()
    dc.use_cache_dir(cache_dir)

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

    def on_new_peer_address(d):
        bucket = d['bucket_name']
        data = d['data']
#        print('on_new_peer_address: %s ' % d)
        if bucket[-1] == DSC.IPFS_ADDRESSES:
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

    interval_make_summary = DoAtInterval(as_seconds(DSwarmConstants.SDELTA_MAKE_SUMMARY))
    interval_advertise_peer = DoAtInterval(DSwarmConstants.DELTA_PEER * 0.5)
    interval_addresses = DoAtInterval('10m')
    interval_rebroadcast = DoAtInterval('3m')
    interval_connect = DoAtInterval('5m')
    interval_advertises_ipfs_peers = DoAtInterval('1m')
    interval_cleanup_sync = DoAtInterval('5m', '5m')
    interval_queue_stats = DoAtInterval('10s')

    key = mi.key
    identity = key.hash

    for peer in dc.query('peer'):
        if peer != identity:
            print('trying to connect %s' % peer)
            address = '/p2p-circuit/ipfs/' + peer
            mi.send_to_connector(address)

    try:
        should_quit = False
        while not should_quit:
            if interval_advertises_ipfs_peers.its_time():
                periodic_advertise_ipfs_peers(dc, mi, identity, ipfsi)

            if interval_addresses.its_time():
                periodic_advertise_ipfs_addresses(dc, mi, identity, ipfsi)

            if interval_connect.its_time():
                periodic_try_connect(dc, mi, identity, ipfsi)

            if interval_make_summary.its_time():
                print('making summary...')
                periodic_make_summary(dc, mi, identity, ipfsi)

            if interval_advertise_peer.its_time():
                periodic_advertise_self(dc, mi, identity, ipfsi)

            envelopes = mi.get_many_for_me(timeout=2)

            if interval_queue_stats.its_time():
                msg = 'Processing %d envelopes' % len(envelopes)
                print(msg)

            sys.stderr.write('-')
            for envelope in envelopes:
                sys.stderr.write('e')

                try:
                    m = interpret_message(envelope.contents)
                except Exception as e:
                    msg = 'Could not interpret message from %s' % envelope.maddr_from
                    msg += '\n\n' + indent(str(e), '> ')
                    print(msg)
                else:
                    if isinstance(m, MsgPing):
                        reply_ping(mi, dc, envelope)

                    elif isinstance(m, MsgRequest):
                        reply_msg_request(mi, dc, envelope, m)

                    elif isinstance(m, MsgCommand):
                        if m.command == 'quit':
                            should_quit = True
                            pong = create_pong_message()
                            e = Envelope('', envelope.maddr_from, pong)
                            mi.dispatch(e)
                            time.sleep(5)
                        else:
                            print('cannot interpret %r' % m.command)
                            pong = create_pong_message()
                            e = Envelope('', envelope.maddr_from, pong)
                            mi.dispatch(e)
                    else:
                        try:
                            dc.process(envelope.contents, envelope.maddr_from)
                        except ProcessFailure as e:
                            em = 'Cannot interpret message: '
                            em += '\n' + str(e)
                            print(em)

            if interval_rebroadcast.its_time():
                periodic_rebroadcast(mi, dc)

            if interval_cleanup_sync.its_time():
                dc.cleanup()
                dc.sync()

        print('Graceful exit.')
    finally:

        print('Clean up cache')
        dc.close()


last_summary = None


def periodic_advertise_ipfs_addresses(dc, mi, identity, ipfsi):  #@UnusedVariable
    addresses = ipfsi.get_addresses()
    print('addresses: %s' % addresses)
    for address in addresses:
        if (address.startswith('/ip4/127.0.0.1/') or
            address.startswith('/ip6/')):
            continue
        t = time.time()
        msg = create_propose_message((DSC.PRI, identity, DSC.IPFS_ADDRESSES),
                                     address, validity=[t, t + as_seconds('1h')])
        mi.send_to_brain('', msg, sign=True)


def periodic_advertise_ipfs_peers(dc, mi, identity, ipfsi):  #@UnusedVariable
    peers = ipfsi.swarm_peers()
    for peer in peers:
        t = time.time()
        msg = create_propose_message((DSC.PRI, identity, DSC.IPFS_PEERS),
                                     peer, validity=[t, t + as_seconds('1h')])
        mi.send_to_brain('', msg, sign=True)


def periodic_try_connect(dc, mi, identity, ipfsi):  #@UnusedVariable
    for t, bucket in dc.root.items():
        if t[-1] == DSC.IPFS_ADDRESSES:
            if t[-2] == identity: continue
            for address in bucket.query(time.time()):
                print('connecting %s' % address)
                mi.send_to_connector(address)


def periodic_advertise_self(dc, mi, identity, ipfsi):  #@UnusedVariable
    t = time.time()
    msg = create_propose_message('peer', identity, validity=[t, t + DSwarmConstants.DELTA_PEER])
    mi.send_to_brain('', msg, sign=True)

    import platform

    properties = {}
    properties['hostname'] = socket.gethostname()
    properties['processor'] = platform.processor()
    properties['machine'] = platform.machine()
    properties['node'] = platform.node()
    properties['version/dswarm'] = duckietown_swarm.__version__
    properties['version/python'] = platform.python_version()
    properties['version/ipfs'] = ipfsi.version()

    interfaces = []
    for iname, mac in get_mac_addresses().items():
        i = '%s;%s' % (iname, mac)
        interfaces.append(i)
    properties['interfaces'] = interfaces
    properties['system'] = platform.system()

    for k, v in properties.items():
        if not isinstance(v, list):
            v = [v]
        for x in v:
            bucket = (DSC.PRI, identity, 'info') + tuple(k.split('/'))
            msg = create_propose_message(bucket, x, validity=[t, t + as_seconds(DSC.SDELTA_INFO)])
            mi.send_to_brain('', msg, sign=True)


def periodic_make_summary(dc, mi, identity, ipfsi):
    global last_summary
    summary_humans = dc.summary()
    summary_humans = summary_humans.replace(identity, 'QmSELF')
    summary_messages = dc.summary_messages()

    summary = ipfsi.get_tree_builder()
    summary.add_file_content('humans.txt', summary_humans)
    summary.add_file_content('machines.txt', '\n'.join(summary_messages))
    Q = summary.get_hash()

    bucket = (DSC.PRI, identity, 'summaries')
    t = time.time()
    if last_summary is not None:
        msg = create_dismiss_message(bucket, last_summary, validity=[t, None])
        mi.broadcast_to_all_brains(msg, sign=True)

    validity = [t, t + as_seconds(DSwarmConstants.SDELTA_MAKE_SUMMARY) * 2]
    msg = create_propose_message(bucket, Q, validity)
    mi.broadcast_to_all_brains(msg, sign=True)

    last_summary = Q
    print('summary: %s' % last_summary)


def periodic_rebroadcast(mi, dc):
    messages = []

    for t, _ in dc.root.items():
        out_channels = mi._get_broadcasting_channels()
        these = dc.rebroadcast(t, out_channels)
        # TODO: make sure that there is a signature
        if t[0] == DSC.PRI:
            for m in these:
                hashed = get_sha256_base58(m.contents)
                if not hashed in dc.signatures:
                    print('No signature available for %s' % "/".join(t))
                else:
                    messages.append(m)

        else:
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
        # print(msg)
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
        if not matches(c):
            continue
        out = dc._summary_message_for_bucket(bucket_name, only_positive=True)

        messages.extend(out)

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
