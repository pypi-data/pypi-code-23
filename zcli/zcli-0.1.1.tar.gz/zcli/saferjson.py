import json
from decimal import Decimal
from zcli.acctab import AccumulatorTable


def encode_param(arg, pretty=False):
    t = type(arg)
    if t is str:
        return arg
    elif t in [int, Decimal]:
        return str(arg)
    elif t in [bool, unicode, list, dict, AccumulatorTable]:
        dumpf = dumps_pretty if pretty else dumps_compact
        return dumpf(arg)
    else:
        assert False, 'Invalid ZcashCLI argument: {!r}'.format(arg)


def dump_pretty(obj, f):
    return json.dump(
        obj,
        f,
        indent=2,
        separators=(',', ': '),
        sort_keys=True,
        default=_transcode_to_jsonobj,
    )


def dump_compact(obj, f):
    return json.dump(
        obj,
        f,
        indent=None,
        separators=(',', ':'),
        sort_keys=True,
        default=_transcode_to_jsonobj,
    )


def dumps_pretty(obj):
    return json.dumps(
        obj,
        indent=2,
        separators=(',', ': '),
        sort_keys=True,
        default=_transcode_to_jsonobj,
    )


def dumps_compact(obj):
    return json.dumps(
        obj,
        indent=None,
        separators=(',', ':'),
        sort_keys=True,
        default=_transcode_to_jsonobj,
    )


def load(f):
    return json.load(
        f,
        parse_float=Decimal,
        parse_int=Decimal,
        object_pairs_hook=_decode_obj_pairs,
    )


def loads(s):
    return json.loads(
        s,
        parse_float=Decimal,
        parse_int=Decimal,
        object_pairs_hook=_decode_obj_pairs,
    )


# Private dump helpers:
def _transcode_to_jsonobj(obj):
    assert isinstance(obj, Decimal), 'Cannot encode to JSON: {!r}'.format(obj)
    f = float(obj)
    roundtrip = Decimal(f)
    error = abs(obj - roundtrip)
    # Fail if error > 9 decimal places (1 more than Zatoshi precision):
    errorapprox = error.quantize(Decimal('0.000000001'))
    if errorapprox == Decimal(0):
        return f
    else:
        raise ValueError(
            'Encoding decimal {} (via float {}) introduces error: {}'
            .format(obj, f, error))


# Private load helpers:
def _decode_obj_pairs(items):
    d = {}
    for (k, value) in items:
        if k in d:
            raise ValueError('Duplicate key "{}".'.format(k))
        else:
            d[k] = value
    return d
