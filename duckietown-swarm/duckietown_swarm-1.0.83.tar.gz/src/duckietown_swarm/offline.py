import sys

from contracts import contract
from system_cmd import CmdException

from .brain import DistributedRepoSwarm
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
#        n = len(envelopes)
#        if n > 1:
#            print('ignoring %s messages and process the last' % (n - 1))
#            envelopes = [envelopes[-1]]

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
                data = ipfsi.get(data_mh, timeout=timeout)
            except Timeout:
                print('timeout for %s' % data_mh)
                continue
            except CmdException as e:
                print(str(e))
                continue

            data = data.strip()

            lines = data.split('\n')

            i = 0
            for msg in lines:
                if msg in seen:
                    continue
                else:
#                    print('NEW: %s' % msg)
                    seen.add(msg)
                    i += 1
                    from_channel = '/ipfs/' + mh
                    mi.send_to_brain(from_channel, msg)

            new_ones = i
            print('read %s catchup messages: %s new ones' % (len(lines), new_ones))


def go_offline():
    s = sys.stdin.read()
    dc = read_lines(s)

    show = ['networks', 'peer', 'trusted', 'admin', 'files', 'verified', 'safe', 'summaries',
            'pri']
    for k in show:
        for x in dc.query(k):
            print('%s: %s' % (k, x))

#initialized bucket networks
#initialized bucket peer
#initialized bucket trusted
#initialized bucket admin
#initialized bucket files
#initialized bucket verified
#initialized bucket safe
#initialized bucket summaries
#initialized bucket pri


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


if __name__ == '__main__':
    go_offline()

