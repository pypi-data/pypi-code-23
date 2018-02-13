from collections import OrderedDict, namedtuple
import copy
import json

from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped

MSG_PROPOSE = 'propose'
MSG_DISMISS = 'dismiss'
MSG_SIGNATURE = 'signature'

FIELD_BUCKET = 'bucket'
FIELD_MTYPE = 'mtype'
FIELD_VALIDITY = 'validity'
FIELD_PROPOSE_DATA = 'data'
FIELD_SIGN_DATA = 'data'
FIELD_SIGNER = 'signer'
FIELD_SIGNATURE = 'signature'


@contract(buckets='str|seq(str)', data=str, validity='None|seq[2]', returns=str)
def create_propose_message(buckets, data, validity=None):
    '''
        Done:

            {'mtype': 'propose', 'data': data, 'validity': [0, null]}
    '''
    if isinstance(buckets, str):
        buckets = (buckets,)

    if validity is None:
        validity = None, None

    res = OrderedDict()
    res[FIELD_MTYPE] = MSG_PROPOSE
    res[FIELD_BUCKET] = list(buckets)
    res[FIELD_PROPOSE_DATA] = data
    res[FIELD_VALIDITY] = _format_validity(validity)
    s = json.dumps(res).encode()
    return s


@contract(buckets='str|seq(str)', data=str, validity='seq[2]', returns=str)
def create_dismiss_message(buckets, data, validity):
    '''
        Done:

            {'mtype': 'dismiss', 'data': data, 'validity': [0, null]}
    '''
    if isinstance(buckets, str):
        buckets = (buckets,)

    res = OrderedDict()
    res[FIELD_MTYPE] = MSG_DISMISS
    res[FIELD_BUCKET] = list(buckets)
    res[FIELD_PROPOSE_DATA] = data
    res[FIELD_VALIDITY] = _format_validity(validity)
    s = json.dumps(res).encode()
    return s


def _format_validity(validity):

    def intornone(x):
        return None if x is None else int(x)

    return [intornone(validity[0]), intornone(validity[1])]


MsgPropose = namedtuple('MsgPropose', 'buckets data validity')
MsgDismiss = namedtuple('MsgDismiss', 'buckets data validity')
MsgSignature = namedtuple('MsgSignature', 'signer data signature')


@contract(d='dict')
def interpret_propose_message(d):
    d2 = copy.deepcopy(d)
    assert d2.pop(FIELD_MTYPE) == MSG_PROPOSE

    buckets = tuple(map(str, d2.pop(FIELD_BUCKET)))
    data = str(d2.pop(FIELD_PROPOSE_DATA))
    validity = tuple(d2.pop(FIELD_VALIDITY))
    if d2:
        msg = 'Additional fields %s in %s' % (list(d2), d)
        raise CouldNotInterpret(msg)
    return MsgPropose(buckets=buckets, data=data, validity=validity)


@contract(d='dict')
def interpret_dismiss_message(d):
    d2 = copy.deepcopy(d)
    assert d2.pop(FIELD_MTYPE) == MSG_DISMISS

    buckets = tuple(map(str, d2.pop(FIELD_BUCKET)))
    data = str(d2.pop(FIELD_PROPOSE_DATA))
    validity = tuple(d2.pop(FIELD_VALIDITY))
    if d2:
        msg = 'Additional fields %s in %s' % (list(d2), d)
        raise CouldNotInterpret(msg)
    return MsgDismiss(buckets=buckets, data=data, validity=validity)


class CouldNotInterpret(Exception):
    pass


@contract(s=str)
def interpret_message(s):
    cases = {
        MSG_PROPOSE: interpret_propose_message,
        MSG_DISMISS: interpret_dismiss_message,
        MSG_SIGNATURE: interpret_signature_message,
    }
    try:
        d = json.loads(s)
    except ValueError as e:
        msg = 'Could not read JSON:\n\n   %s' % s
        raise_wrapped(CouldNotInterpret, e, msg)
    check_isinstance(d, dict)
    mtype = d['mtype']
    if mtype in cases:
        return cases[mtype](d)
    else:
        msg = 'Invalid type %r' % mtype
        raise CouldNotInterpret(msg)


@contract(data_hash='str', signer='str', signature=str, returns=str)
def create_signature_message(data_hash, signer, signature):
    '''
        data_mhash

        Result:

            {'mtype': 'sign', 'hash': data, 'signer': hash, 'signature': signature}

    '''
    res = OrderedDict()
    res[FIELD_MTYPE] = MSG_SIGNATURE
    res[FIELD_SIGN_DATA] = data_hash
    res[FIELD_SIGNER] = signer
    res[FIELD_SIGNATURE] = signature
    s = json.dumps(res).encode()
    return s


@contract(d='dict')
def interpret_signature_message(d):
    d2 = copy.deepcopy(d)
    assert d2.pop(FIELD_MTYPE) == MSG_SIGNATURE

    signature = str(d2.pop(FIELD_SIGNATURE))
    data = str(d2.pop(FIELD_SIGN_DATA))
    signer = str(d2.pop(FIELD_SIGNER))
    if d2:
        msg = 'Additional fields %s in %s' % (list(d2), d)
        raise CouldNotInterpret(msg)
    return MsgSignature(signature=signature, data=data, signer=signer)


@contract(message='tuple(str, str)')
def put_in_queue(queue, message):
    check_isinstance(message, tuple)
    print('put_in_queue %s %s' % message)
    queue.put(message)
