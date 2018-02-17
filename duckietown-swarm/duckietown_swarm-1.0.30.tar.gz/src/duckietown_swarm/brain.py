from Queue import Empty
from duckietown_swarm.dcache import get_sha256_base58
from duckietown_swarm.dcache_wire import create_signature_message
import time

from contracts import check_isinstance

from .dcache import DistributedRepo
from .dcache import ProcessFailure
from .dcache_wire import create_dismiss_message
from .dcache_wire import create_propose_message
from .ipfs_utils import IPFSInterface
from .irc2 import MessagingInterface
from .utils import DoAtInterval


class DistributedRepoSwarm(DistributedRepo):

    def __init__(self):
        DistributedRepo.__init__(self)
        self.init_bucket('networks', allowed=[])
        self.init_bucket('peer', allowed=[])
        self.init_bucket('trusted', allowed=['trusted', 'admin'])
        self.init_bucket('admin', allowed=['admin'])

        self.init_bucket('files', allowed=[])
        self.init_bucket('verified', allowed=[])  #
        self.init_bucket('safe', allowed=[])  #

#        self.init_bucket('summaries', allowed=[])  #

        self.init_bucket('pri', allowed=[])  #


ALL_BRAINS = '/dswarm/*/brain'


def brain(mi, cache_dir):
    from duckietown_swarm.irc2 import Envelope
    check_isinstance(mi, MessagingInterface)

    ipfsi = IPFSInterface()

    dc = DistributedRepoSwarm()
    dc.use_cache_dir(cache_dir)

    t = time.time()

    proposed = set(dc.query('files'))
    verified = set(dc.query('verified'))
    for p in proposed:
        if not p in verified:
            mi.send_to_verifier(p)

    print('From cache: %s files' % len(dc.query('files')))
    print('From cache: %s verified' % len(dc.query('verified')))

#    ipfsi = IPFSInterface()
#    recursive, indirect = ipfsi.pin_ls()

#    pinned = recursive | indirect
#
#    pinned = set()
#    dc.send_all(pinned)

    def on_new_files(data):
        print('New file: %s' % data)
        mi.send_to_verifier(data)

    def on_new_peer(data):
        print('New peer: %s' % data)
#        mi.send_to_connector(data)

    def on_new_verifed(data):
        print('New verified: %s' % data)
        mi.send_to_pinner(data)

    dc.add_hook_proposed('peer', on_new_peer)
    dc.add_hook_proposed('files', on_new_files)
    dc.add_hook_proposed('verified', on_new_verifed)

    interval_make_summary = DoAtInterval(6 * 3)
    DELTA_PEER = 10 * 60
    interval_advertise_peer = DoAtInterval(DELTA_PEER * 0.5)
    interval_addresses = DoAtInterval(10 * 60)

    key = mi.key
    identity = key.hash
    last_summary = None
    try:
        while True:
            if interval_addresses.its_time():
                addresses = ipfsi.get_addresses()
                for address in addresses:
                    if (address.startswith('/ip4/127.0.0.1/') or
                        address.startswith('/ip6/')):
                        continue
                    t = time.time()
                    msg = create_propose_message(('pri', identity, 'addresses'),
                                                 address, validity=[t, t + 300])
                    mi.send_to_brain('', msg, sign=True)

            if interval_make_summary.its_time():
                summary = dc.summary()
                summary = summary.replace(identity, 'QmSELF')
                Q = ipfsi.add_bytes(summary)
                print('summary %s' % Q)

                bucket = ('pri', identity, 'summaries')
                t = time.time()
                if last_summary is not None:
                    msg = create_dismiss_message(bucket, last_summary, validity=[t, None])

                    mi.broadcast_to_all_brains(msg, sign=True)

                msg = create_propose_message(bucket, Q, validity=[t, t + 300])
                mi.broadcast_to_all_brains(msg, sign=True)

                last_summary = Q
                mi.send_to_ipns_publisher('summary2', Q)

            if interval_advertise_peer.its_time():
                t = time.time()
                msg = create_propose_message('peer', identity, validity=[t, t + DELTA_PEER])
                mi.send_to_brain('', msg, sign=True)

            try:
                msgs = mi.get_many_for_me(timeout=0.5)

                for envelope in msgs:
                    msg = envelope.contents
                    from_channel = envelope.maddr_from

                    if not isinstance(msg, str):
                        x = 'I expected the messages to be string, got %s' % msg
                        raise TypeError(x)

                    try:
                        dc.process(msg, from_channel=from_channel)
                    except ProcessFailure as e:
                        em = 'Cannot interpret message from %r: ' % from_channel
                        em += '\n' + str(e)
                        print(em)

            except Empty:
                pass

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
#                        print('Created signature: %s' % e_sign)
                        mi.dispatch(e_sign)
                mi.dispatch(envelope)

            dc.cleanup()
            dc.sync()

    finally:
        print('Clean up cache')
        dc.close()

