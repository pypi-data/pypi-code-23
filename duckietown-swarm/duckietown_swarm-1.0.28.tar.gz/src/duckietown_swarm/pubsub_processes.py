from duckietown_swarm.dcache import create_propose_message
import subprocess
import time

from system_cmd import system_cmd_result


def pubsub_reader_process(mi, topic):
    cmd = ['ipfs', 'pubsub', 'sub', '--discover', topic]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    maddr = '/ipfs-pubsub/' + topic
    t = time.time()
    msg = create_propose_message(('pri', mi.key.hash, 'addresses'),
                                 maddr, validity=[t, t + 300])

    for line in iter(proc.stdout.readline, ''):
        line = line.strip()
        try:
            line = line.encode()
            mi.send_to_brain('', line)
        except ValueError as e:
            msg = 'Could not decode JSON: %s\n%r' % (e, line)
            print(msg)


def pubsub_writer_process(mi, topic):
    while True:
        msg = mi.get_next_for_me().contents
        cmd = ['ipfs', 'pubsub', 'pub', topic, msg]
        system_cmd_result('.', cmd, raise_on_error=False)
