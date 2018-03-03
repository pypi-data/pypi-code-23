from .constants import DSwarmConstants
from .dcache_wire import create_dismiss_message, create_propose_message
from .ipfs_utils import CouldNotPin, IPFSInterface, InvalidHash
from .packaging import find_more_information, UnexpectedFormat
from .utils import as_seconds, now_until, now_until_forever


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
            validity = now_until(as_seconds('1h'))
            m = create_dismiss_message(DSwarmConstants.DLC_BUCKET_FILES, mh, validity)
            mi.send_to_brain('', m)
            continue
        except UnexpectedFormat as _e:
            print('Could not find more information for %s' % mh)
            validity = now_until(as_seconds('1h'))
            m = create_dismiss_message(DSwarmConstants.DLC_BUCKET_FILES, mh, validity)
            mi.send_to_brain('', m)
            continue

        validity = now_until_forever()
        m = create_propose_message(DSwarmConstants.DLC_BUCKET_VERIFIED, mh, validity)
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

            validity = now_until(as_seconds('7d'))
            m = create_propose_message(DSwarmConstants.DLC_BUCKET_SAFE, mh, validity)
            mi.send_to_brain('', m, sign=True)
