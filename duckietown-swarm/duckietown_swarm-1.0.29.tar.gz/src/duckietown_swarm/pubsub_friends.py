from duckietown_swarm.dcache import create_propose_message
from duckietown_swarm.ipfs_utils import IPFSInterface
import time

from system_cmd import system_cmd_result


def pubsub_friendship(mi):

    ipfsi = IPFSInterface()

    ## Read from the queue
    ID = ipfsi.ipfs_id()

    # signal that we are here
#    cmd = ['ipfs', 'block', 'put']
#    res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=True, display_stdout=False, display_stderr=False,
#                      write_stdin='duckiebots\n')
#    token = res.stdout.strip()
    token = ipfsi.block_put('duckiebots\n')
    found = set()
    while True:
        # find other duckiebots
        hosts = ipfsi.dht_findprovs(token, timeout='30s')

        # print('Found %s Duckiebots in the hidden botnet.' % len(hosts))
        for h in hosts:
            # do not connect to self
            if h == ID: continue
            if h in found:
                continue

            # publicize peer
            interval = (time.time(), time.time() + 9 * 60)
            mi.send_to_brain('', create_propose_message('peer', h, interval))

            found.add(h)
            cmd = ['ipfs', 'swarm', 'connect', '--timeout', '30s', '/p2p-circuit/ipfs/' + h]
            _ = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False,
                                  display_stdout=False, display_stderr=False)
            ok = _.ret == 0
            print('Connecting to new friend %s: ' % h + ("OK" if ok else "(not possible)"))
            if ok:
                interval = (time.time(), time.time() + 9 * 60)
                connection = '%s:%s' % (ID, h)
                msg = create_propose_message('connections', connection, interval)
                mi.send_to_brain('', msg)

        time.sleep(30)
