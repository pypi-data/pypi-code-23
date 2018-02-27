from duckietown_swarm.dcache import create_propose_message, Envelope, \
    BOOTSTRAP_PATTERNS
from duckietown_swarm.dcache_wire import create_request_message
from duckietown_swarm.ipfs_utils import IPFSInterface
from duckietown_swarm.utils import now_until
import subprocess
import time

from system_cmd import system_cmd_result


def pubsub_reader_process(mi, topic):
    ipfsi = IPFSInterface(mi.ipfs_path)
    from .irc2 import CouldNotDispatch

    ipfs = ipfsi.get_executable()
    cmd = [ipfs, 'pubsub', 'sub', '--discover', topic]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            env=ipfsi._get_env())

    # add my address
    maddr = '/ipfs-pubsub/' + topic
    t = time.time()
    msg = create_propose_message(('pri', mi.key.hash, 'addresses'),
                                 maddr, validity=[t, t + 300])
    mi.send_to_brain('', msg, sign=True)

    for line in iter(proc.stdout.readline, ''):
        line = line.strip()
        try:
            line = line.encode()
            env = Envelope.from_json(line)
#            e.maddr_from = '/ip4/%s/udp/%s' % (who_host, who_port) + e.maddr_from
#            mi.send_to_brain('', line)
        except ValueError as e:
            msg = 'Could not decode JSON: %s\n%r' % (e, line)
            print(msg)

        try:
            mi.dispatch(env)
        except CouldNotDispatch as e:
            pass  # print(e)


def pubsub_writer_process(mi, topic):
    ipfsi = IPFSInterface(mi.ipfs_path)

    msg = create_request_message(BOOTSTRAP_PATTERNS, validity=now_until(105))
    maddr_from = '/dswarm/%s/brain' % ipfsi.ipfs_id()
    # otherwise I will answer to myself
#    maddr_from = '/dswarm/*/brain'  #% ipfsi.ipfs_id()
    envelope = Envelope(maddr_from=maddr_from,
                 maddr_to='/dswarm/*/brain',
                 contents=msg)
    q = mi.name2queue[mi.my_maddr]
    q.put(envelope)

#    # sen
#    patterns = ['/peers', '*/summaries', '*/ipfs_addresses']
#    msg = create_request_message(patterns, validity=now_until(105))
#    maddr_from = '/dswarm/%s/brain' % ipfsi.ipfs_id()
#    envelope = Envelope(maddr_from=maddr_from,
#                 maddr_to='/dswarm/*/brain',
#                 contents=msg)
#    q.put(envelope)

    ipfs = ipfsi.get_executable()
    while True:
        envelope = mi.get_next_for_me()
        envelope_json = envelope.to_json()
        if envelope.maddr_to == "":
            em = 'Will not write empty to: \n%s' % envelope.verbose()
            raise Exception(em)
#        print('writing: %s' % envelope)
        cmd = [ipfs, 'pubsub', 'pub', topic, envelope_json + '\n']
        system_cmd_result('.', cmd, raise_on_error=False,
                          env=ipfsi._get_env())
