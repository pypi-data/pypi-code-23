from system_cmd import system_cmd_result

from .dcache_wire import put_in_queue
from .ipfs_utils import IPFSInterface, InvalidHash
from .packaging import find_more_information, UnexpectedFormat
from .utils import get_at_least_one


def pinner(i, read_from, out_queues):
    ## Read from the queue
    ipfsi = IPFSInterface()
    done = set()
    while True:
        msgs = get_at_least_one(read_from, 10)
        for msg in msgs:
            if msg in done:
                print('Pinner received %s twice' % msg)
                continue
            done.add(msg)

            try:
                _more_info = find_more_information(ipfsi, msg, find_provs=True)
                # print more_info
            except InvalidHash as _e:
                advertise_invalid(out_queues, msg, "Hash not found")
                continue
            except UnexpectedFormat as _e:
                print('Could not find more information for %s' % msg)
                advertise_invalid(out_queues, msg, "Format not respected")
                continue

            print('Pinner %d %s: pinning' % (i, msg))

            cmd = ['ipfs', 'pin', 'add', '-r', '--timeout', '30s', msg]
            res = system_cmd_result(cwd='.', cmd=cmd, raise_on_error=False)
            if res.ret != 0:
                print('Pinner %d %s: could not pin file' % (i, msg))
            else:
                print('Pinner %d %s: OK' % (i, msg))


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

