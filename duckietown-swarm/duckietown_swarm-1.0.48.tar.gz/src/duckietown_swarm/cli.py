
from Queue import Empty
from duckietown_swarm.brain import DistributedRepoSwarm
from duckietown_swarm.dcache_wire import create_request_message, MsgPong
import sys
import time

import yaml

from .dcache import Envelope, interpret_message
from .socket_utils import AsyncLineBasedConnection


def now_until(delta):
    t = time.time()
    return [t, t + delta]


def duckietown_swarm_cli_main():
    import argparse

    parser = argparse.ArgumentParser(description='Ping the swarm')
    parser.add_argument('host', type=str, default='localhost')
    parser.add_argument('what', default='*', help='what to request')

    args = parser.parse_args()

    host = args.host
    port = 8000

    albc = AsyncLineBasedConnection(host, port)
    maddr_from = '/cli'

    inbound = albc.get_q_inbound()
    outbound = albc.get_q_outbound()

    what = args.what
    msg = create_request_message(what, validity=now_until(5))

    e = Envelope(maddr_from=maddr_from,
                 maddr_to='/dswarm/*/brain',
                 contents=msg)

    outbound.put(e)

    dc = DistributedRepoSwarm()
    from_channel = 'stdin'
    i = 0

    wait_since_last = 15.0
    t_last = time.time()
    while True:
        try:
            env = inbound.get(block=True, timeout=1.0)
            t_last = time.time()
            sys.stderr.write('.')
        except Empty:
            if i > 0:
                if time.time() - t_last > wait_since_last:
                    break
        else:
            msg = interpret_message(env.contents)
            if isinstance(msg, MsgPong):
                break
            dc.process(env.contents, from_channel)
        i += 1
    print('processed %s messages' % i)

    data = dc.summary_dict()
    print(yaml.dump(data))


if __name__ == '__main__':
    duckietown_swarm_cli_main()
