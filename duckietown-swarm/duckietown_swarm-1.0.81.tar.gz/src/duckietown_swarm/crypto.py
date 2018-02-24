import random

import base58

from .dcache import create_signature_message
from .utils import get_sha256_base58


class CryptoKey(object):

    def __init__(self, private, public):
        self.private = private
        self.public = public
        self.hash = get_sha256_base58(public)

    def sign_hash(self, data_hash):
        ''' Computes hash of data and then sign it '''
        #return '%s signed by %s' % (data, self.hash)
        return get_sha256_base58(data_hash + 'signature')

    def generate_sign_message(self, data):
        data_hash = get_sha256_base58(data)
        signer = self.hash
        signature = base58.b58encode(self.sign_hash(data_hash))
#        signature = self.sign_hash(data)
        msg = create_signature_message(data_hash, signer, signature)
        return msg


def get_key(cache_dir):
#    if not os.path.exists(cache_dir):
#        os.makedirs(cache_dir)
#    fn = os.path.join(cache_dir, '.key.pickle')
#    if not os.path.exists(fn):
    key = CryptoKey(str(random.randint(0, 10000)), str(random.randint(0, 10000)))
#        with open(fn, 'wb') as f:
#            pickle.dump(key0, f)
#    with open(fn) as f: key = pickle.load(f)

#    identity = key.hash
    return key
