

import time

from .dcache_wire import create_dismiss_message, create_propose_message
from .ipfs_utils import CouldNotPin, IPFSInterface, InvalidHash
from .packaging import find_more_information, UnexpectedFormat


def verifier(mi):

    ipfsi = IPFSInterface(mi.ipfs_path)
    done = set()

    while True:
        mh = mi.get_next_for_me().contents
#        print('considering %s' % mh)
        if mh in done:
#            print('verifier received %s twice' % mh)
            continue

        done.add(mh)

        try:
            more_info = find_more_information(ipfsi, mh, find_provs=False)
            print('%s verified %s' % (mh, more_info.filename))
        except InvalidHash as _e:
            t = time.time()
            m = create_dismiss_message('files', mh, [t, t + 60 * 60])
            mi.send_to_brain('', m)
            continue
        except UnexpectedFormat as _e:
            print('Could not find more information for %s' % mh)
            t = time.time()
            m = create_dismiss_message('files', mh, [t, t + 60 * 60])
            mi.send_to_brain('', m)
            continue

        t = time.time()
        m = create_propose_message('verified', mh, [t, None])
        mi.send_to_brain('', m, sign=True)


def pinner(mi):
    timeout = '15m'
    ## Read from the queue
    ipfsi = IPFSInterface(mi.ipfs_path)
    done = set()
    while True:
        mh = mi.get_next_for_me().contents

        if mh in done:
            print('Pinner received %s twice' % mh)
            continue

        done.add(mh)

        try:
            ipfsi.pin_add(mh, recursive=True, timeout=timeout)
        except CouldNotPin as e:
            print('Pinner %s: could not pin file: %s' % (mh, e))
        else:
            print('Pinner %s: OK' % (mh))

            t = time.time()
            m = create_propose_message('safe', mh, [t, t + 60 * 60 * 24 * 7])
            mi.send_to_brain('', m, sign=True)
