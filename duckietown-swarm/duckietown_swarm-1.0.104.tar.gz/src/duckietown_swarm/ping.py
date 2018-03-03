
from .dcache import Envelope, interpret_message
from .dcache_wire import create_ping_message
from .socket_utils import AsyncLineBasedConnection


def duckietown_swarm_ping_main():
    import argparse

    parser = argparse.ArgumentParser(description='Ping the swarm')
    parser.add_argument('host', type=str, default='localhost')
    parser.add_argument('who', default='/dswarm/*/brain', help='who to ping')

    args = parser.parse_args()

    host = args.host
    port = 8000
    maddr_to = args.who
    albc = AsyncLineBasedConnection(host, port)
    maddr_from = '/cli'

    inbound = albc.get_q_inbound()
    outbound = albc.get_q_outbound()

    def ping():
        e = Envelope(maddr_from=maddr_from,
                     maddr_to=maddr_to,
                     contents=create_ping_message())
        outbound.put(e)

    ping()

    while True:
        env = inbound.get()
        msg = interpret_message(env.contents)
        print('obtained from %s: %s' % (env.maddr_from, msg.__repr__()))
        ping()


if __name__ == '__main__':
    duckietown_swarm_ping_main()
