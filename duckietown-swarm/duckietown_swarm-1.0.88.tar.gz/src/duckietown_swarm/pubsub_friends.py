from duckietown_swarm.constants import DSwarmConstants
import time

from system_cmd import system_cmd_result

from .dcache import create_propose_message

DSC = DSwarmConstants


def pubsub_friendship(mi):
    ipfsi = mi.get_ipfsi()

    ## Read from the queue
    ID = ipfsi.ipfs_id()

    # signal that we are here
    token = ipfsi.block_put(DSC.PUBSUB_FRIENDS_GREETING)

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
            t = time.time()
            interval = (t, t + 9 * 60)
            mi.send_to_brain('', create_propose_message('peer', h, interval))

            found.add(h)

        time.sleep(30)


def connecting_to_peer(mi):
    ipfsi = mi.get_ipfsi()
    ID = ipfsi.ipfs_id()

    while True:
        envelope = mi.get_next_for_me()
        h = envelope.contents
        ipfs = ipfsi.get_executable()
        cmd = [ipfs, 'swarm', 'connect', '--timeout', '30s', h]
        res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False,
                              display_stdout=False, display_stderr=False,
                              env=ipfsi._get_env())
        ok = res.ret == 0
#        from_where = envelope.maddr_from
        # print('Connecting to new friend %s (%s): ' % (h, from_where) + ("OK" if ok else "(not possible) "))
        if ok:
            interval = (time.time(), time.time() + 9 * 60)
            connection = '%s:%s' % (ID, h)
            msg = create_propose_message('connections', connection, interval)
            mi.send_to_brain('', msg)

