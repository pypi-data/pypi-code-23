from duckietown_swarm.dcache_wire import create_dismiss_message, \
    create_propose_message
import time

from system_cmd import system_cmd_result

from .dcache_wire import put_in_queue
from .ipfs_utils import IPFSInterface, InvalidHash
from .packaging import find_more_information, UnexpectedFormat
from .utils import get_at_least_one


def verifier(mi):

    ipfsi = IPFSInterface()
    done = set()
    print('starting')
    while True:
        mh = mi.get_for_verifier()
        print('got %s' % mh)
        if mh in done:
            print('verifier received %s twice' % mh)
            continue

        done.add(mh)

        try:
            _more_info = find_more_information(ipfsi, mh, find_provs=False)
            # print more_info
        except InvalidHash as _e:
            t = time.time()
            m = create_dismiss_message('files', mh, [t, t + 60 * 60])
            mi.send_to_brain('verifier', m)
            continue
        except UnexpectedFormat as _e:
            print('Could not find more information for %s' % mh)
            t = time.time()
            m = create_dismiss_message('files', mh, [t, t + 60 * 60])
            mi.send_to_brain('verifier', m)
            continue

        t = time.time()
        m = create_propose_message('verified', mh, [t, t + 60 * 60])
        mi.send_to_brain('verifier', m)


def pinner(mi):
    ## Read from the queue
#    ipfsi = IPFSInterface()
    done = set()
    while True:
        mh = mi.get_for_pinner()

        if mh in done:
            print('Pinner received %s twice' % mh)
            continue
        done.add(mh)

        print('%s: pinning' % (mh))

        cmd = ['ipfs', 'pin', 'add', '-r', '--timeout', '30s', mh]
        res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False)
        if res.ret != 0:
            print('Pinner %s: could not pin file' % (mh))
        else:
            print('Pinner %s: OK' % (mh))


adversised_invalid = set()


def advertise_invalid(out_queues, ipfs_hash, comment=""):
    if ipfs_hash in adversised_invalid:
        return
    adversised_invalid.add(ipfs_hash)
    msg = {'mtype': 'advertise-invalid',
           'details': {'bucket': 'files', 'ipfs': ipfs_hash},
           'comment': comment}

    for q in out_queues:
        put_in_queue(q, msg)

