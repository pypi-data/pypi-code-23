from duckietown_swarm.brain import DistributedRepoSwarm
from duckietown_swarm.crypto import CryptoKey
from duckietown_swarm.dcache_wire import create_propose_message, create_dismiss_message
import time

from comptests.registrar import comptest, run_module_tests


@comptest
def init1():

    ds = DistributedRepoSwarm()
    key_admin = CryptoKey(None, 'mypublickey')
    key_trusted = CryptoKey('mysecretkeytrusted', 'mypublickey2')
    key_mine = CryptoKey('mykey', 'mykey11')

    ds.root.get_bucket('admin').propose(key_admin.hash, (time.time(), None), roles=['admin'])
    ds.root.get_bucket('trusted').propose(key_trusted.hash, (time.time(), None), roles=['admin'])
    msgs = []

    wm = create_propose_message('networks', '/pubsub/duckiebots')
    msgs.append(key_admin.generate_sign_message(wm))
    msgs.append(wm)

    wm = create_propose_message('networks', 'irc:frankfurt.co-design.science/#duckiebots',
                                validity=(0, time.time()))
    msgs.append(wm)

    wm = create_dismiss_message('networks', 'irc:frankfurt.co-design.science/#duckiebots',
                                validity=(time.time(), time.time() + 10))
    msgs.append(wm)

    for msg in msgs:
        ds.process(msg)

    print ds.summary()

    assert ds.query('networks') == ['/pubsub/duckiebots']

    # try to add an admin without a signature
    wm = create_propose_message('admin', key_mine.hash)
    try:
        ds.process(wm)
    except:
        pass
    else:
        msg = 'Invalid operation was accepted'
        raise Exception(msg)

#
#    ds.propose('networks',)
#    ds.propose('networks',)
#
#    ds.propose('files', 'QmPointerA')
#
#    entries = ds.bucket('networks')
#    assert entries[0].data == '/pubsub/duckiebots'
#    assert entries[0].validity.end == float('inf')
#    assert set(entries[0].channels) == set(['direct'])
#    c = entries[0].channels['direct']
#    assert isinstance(c, ChannelStats)

#    assert ChannelStats.counter == 1
#    ChannelStats.last
#    s.data  # data
#    s.validity  # t0, inf
#    s.channels  # channels this was received from
#    s.signatures  # collected signatures


if __name__ == '__main__':
    run_module_tests()
