import time

from contracts import check_isinstance

from .dcache import DistributedRepo
from .dcache import ProcessFailure
from .dcache import get_sha256_base58
from .dcache_wire import create_dismiss_message
from .dcache_wire import create_propose_message
from .dcache_wire import create_signature_message
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

        self.init_bucket('summaries', allowed=[])  #

        self.init_bucket('pri', allowed=[])  #


ALL_BRAINS = '/dswarm/*/brain'


def brain(mi, cache_dir):
    from .irc2 import Envelope
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

    print('From cache: %s files' % len(dc.query('files')))
    print('From cache: %s verified' % len(dc.query('verified')))

#    ipfsi = IPFSInterface()
#    recursive, indirect = ipfsi.pin_ls()

#    pinned = recursive | indirect
#
#    pinned = set()
#    dc.send_all(pinned)

    def on_new_files(d):
        data = d['data']
        #print('New file: %s' % data)
        mi.send_to_verifier(data)

    def on_new_peer(d):
        data = d['data']
        print('New peer: %s' % data)

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
            #print('Ignoring new in bucket %s' % str(bucket))

    MINUTES = 60
    dc.add_hook_proposed('peer', on_new_peer)
    dc.add_hook_proposed('files', on_new_files)
    dc.add_hook_proposed('verified', on_new_verifed)
    dc.add_hook_proposed_all(on_new_summary)

    DELTA_MAKE_SUMMARY = 5 * MINUTES
    interval_make_summary = DoAtInterval(DELTA_MAKE_SUMMARY)
    DELTA_PEER = 10 * 60
    interval_advertise_peer = DoAtInterval(DELTA_PEER * 0.5)
    interval_addresses = DoAtInterval(10 * 60)
    interval_rebroadcast = DoAtInterval(10)

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
#                print msg

                # mi.send_to_ipns_publisher('summary2', Q)

            if interval_advertise_peer.its_time():
                t = time.time()
                msg = create_propose_message('peer', identity, validity=[t, t + DELTA_PEER])
                mi.send_to_brain('', msg, sign=True)

            msgs = mi.get_many_for_me(timeout=2)

            for envelope in msgs:
                msg = envelope.contents
                from_channel = envelope.maddr_from

                try:
                    dc.process(msg, from_channel=from_channel)
                except ProcessFailure as e:
                    em = 'Cannot interpret message from %r: ' % from_channel
                    em += '\n' + str(e)
                    print(em)

            if interval_rebroadcast.its_time():
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

            dc.cleanup()
            dc.sync()

    finally:
        print('Clean up cache')
        dc.close()

