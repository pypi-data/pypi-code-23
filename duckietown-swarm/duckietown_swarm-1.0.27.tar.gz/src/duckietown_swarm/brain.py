from Queue import Empty
import os
import pickle
import random
import time

from contracts import check_isinstance

from .dcache import DistributedRepoSwarm
from .dcache import ProcessFailure, CryptoKey
from .dcache_wire import create_propose_message
from .ipfs_utils import IPFSInterface
from .irc2 import MessagingInterface
from .utils import DoAtInterval


def brain(cache_dir, mi):
    check_isinstance(mi, MessagingInterface)

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
        print('New member of files: %s' % data)
        mi.send_to_verifier(data)

    def on_new_peer(data):
        print('New peer: %s' % data)
#        mi.send_to_connector(data)

    def on_new_verifed(data):
#        print('New peer: %s' % data)
        mi.send_to_pinner(data)

    dc.add_hook_proposed('peer', on_new_peer)
    dc.add_hook_proposed('files', on_new_files)

    interval_make_summary = DoAtInterval(10)
    DELTA_PEER = 10 * 60
    interval_advertise_peer = DoAtInterval(DELTA_PEER * 0.5)

    out_channels = ['to_irc1', 'to_irc2', 'to_pubsub']

    try:
        while True:
            if interval_make_summary.its_time():
                summary = dc.summary()
                Q = ipfsi.add_bytes(summary)
                print ('summary %s' % Q)
                for channel in out_channels:
                    t = time.time()
                    msg = create_propose_message('summaries', Q, validity=[t, t + 300])
                    mi.send_to_matching_channels((channel, msg))
                mi.send_to_ipns_publisher('summary2', Q)

            if interval_advertise_peer.its_time():
                t = time.time()
                msg = create_propose_message('peer', identity, validity=[t, t + DELTA_PEER])
                mi.send_to_brain('self', msg)

            try:
                msgs = mi.get_for_brain()

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

            topics = ['peer', 'trusted', 'admin', 'files', 'verified', 'summaries']

            for t in topics:
                messages.extend(dc.rebroadcast(t, out_channels))

            for channel_message in messages:
                mi.send_to_matching_channels(channel_message)

            dc.cleanup()
            dc.sync()

    finally:
        print('Clean up cache')
        dc.close()

