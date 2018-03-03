from contracts import contract
from contracts.utils import indent
from system_cmd import CmdException

from .brain import DistributedRepoSwarm
from .dcache_wire import CouldNotInterpret, interpret_message
from .ipfs_utils import Timeout
from .irc2 import MessagingInterface

seen_mh = set()
seen = set()


@contract(mi=MessagingInterface)
def read_nodes_summaries(mi):
    timeout = '60s'
    ipfsi = mi.get_ipfsi()

    while True:
#        print('waiting for summary')
        envelopes = [mi.get_next_for_me()]
#
        n = len(envelopes)
        if n > 1:
            print('ignoring %s messages and process the last' % (n - 1))
            envelopes = [envelopes[-1]]

        for envelope in envelopes:
#
#            if envelope.maddr_from == mi.MADDR_BRAIN:
#                print('skipping this from ourselves: %s' % envelope)
#                continue

#            print envelope

            mh = envelope.contents
            if mh in seen_mh:
                continue

            seen_mh.add(mh)
            data_mh = mh + '/machines.txt'
            print('getting %s' % data_mh)

            try:
                data = ipfsi.cat(data_mh, timeout=timeout)
#                print('last chars of data: %r' % data[-300:])
            except Timeout:
                print('timeout for %s' % data_mh)
                continue
            except CmdException as e:
                print(str(e))
                continue

            data = data.strip()
            if not data:
                msg = 'Could not find any data in %s' % data_mh
                print(msg)
                continue

            lines = data.split('\n')

            i = 0
            for k, msg in enumerate(lines):
                if msg in seen:
                    continue

#                    print('NEW: %s' % msg)

                try:
                    interpret_message(msg)
                except CouldNotInterpret as e:
                    m = 'Could not interpret line %d of %d in %s' % (k, len(lines), data_mh)
                    m += '\n\n' + indent(msg.__repr__(), ' line > ')
                    m += '\n\n' + indent(str(e), '> ')
                    print(m)
                    continue

                seen.add(msg)
                i += 1
                from_channel = '/ipfs/' + mh
                mi.send_to_brain(from_channel, msg)

            new_ones = i
            print('read %s catchup messages: %s new ones' % (len(lines), new_ones))


def read_lines(s):
    lines = s.split('\n')
    dc = DistributedRepoSwarm()
    from_channel = 'stdin'
    i = 0
    for msg in lines:
        dc.process(msg, from_channel)
        i += 1
    print('processed: %s' % i)
    return dc

