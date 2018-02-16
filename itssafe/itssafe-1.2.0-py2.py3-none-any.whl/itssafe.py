import six
import pytz
import base64
import datetime

ARBITRARY_EPOCH = 1293840000   # number of seconds of 1/1/2011 after 1/1/1970


class BadSignature(Exception):
    pass


class SignatureExpired(Exception):
    pass


class Unsignable(Exception):
    pass


# def make_hmac_signature_old(string, key):
#     import hmac
#     import hashlib
#     mac = hmac.new(key.encode('ascii'), string, hashlib.sha1)
#     return base64.b64encode(mac.digest())


def make_hmac_signature(string, key):
    import hmac
    import hashlib
    mac = hmac.new(key.encode('utf-8'), string.encode('utf-8'), hashlib.sha1)
    return base64.b64encode(mac.digest()).decode('utf-8')


def get_secs_since_epoch():
    unix_epoch = pytz.utc.localize(datetime.datetime(1970, 1, 1))
    now = pytz.utc.localize(datetime.datetime.utcnow())
    now_in_secs = (now - unix_epoch).total_seconds()
    return now_in_secs - ARBITRARY_EPOCH


# def sign_old(bytes_string, key, secs_since_epoch=None):
#     if secs_since_epoch is None:
#         secs_since_epoch = get_secs_since_epoch()
#     sse_as_bytes = six.text_type(secs_since_epoch).encode('ascii')
#     encoded_secs_since_epoch = base64.b64encode(sse_as_bytes)
#     timestamped_data = bytes_string + b'.' + encoded_secs_since_epoch
#     signature = make_hmac_signature_old(timestamped_data, key)
#     signed_string = timestamped_data + b'.' + signature
#     return signed_string


def sign(text, key, secs_since_epoch=None):
    if not isinstance(text, six.text_type) or not isinstance(key, six.text_type):
        raise Unsignable("input string and key should be a text type (py2 - unicode; py3 - str)")
    if secs_since_epoch is None:
        secs_since_epoch = get_secs_since_epoch()
    sse_as_bytes = six.text_type(secs_since_epoch).encode('utf-8')
    encoded_secs_since_epoch = base64.b64encode(sse_as_bytes).decode('utf-8')
    timestamped_data = text + '.' + encoded_secs_since_epoch
    signature = make_hmac_signature(timestamped_data, key)
    signed_text = timestamped_data + '.' + signature
    return signed_text


# def sign_compare():
#     sse = get_secs_since_epoch()
#     # print("sign old = %s" % sign(six.text_type('what'), six.text_type('why'), secs_since_epoch=sse))
#     # print("sign new = %s" % sign_new(six.text_type('what'), six.text_type('why'), secs_since_epoch=sse))
#     # print("sign old = %s" % sign('what', 'why', secs_since_epoch=sse))
#     print("sign new = %s" % sign_new('what', 'why', secs_since_epoch=sse))


# def unsign_old(bytes_string, key, max_age=10 * 60):
#     timestamped_string, signature_in = bytes_string.rsplit(b'.', 1)
#     signature_calced = make_hmac_signature_old(timestamped_string, key)
#     if signature_calced != signature_in:
#         raise BadSignature("signature '%s' does not match" % signature_in)
#     string_res, timestamp = timestamped_string.rsplit(b'.', 1)
#     decoded_timestamp_str = base64.b64decode(timestamp)
#     try:
#         decoded_timestamp = float(decoded_timestamp_str)
#     except ValueError:
#         raise BadSignature("timestamp does not decode to a float. timestamp = '%s'" % timestamp)
#     secs_since_epoch = get_secs_since_epoch()
#     time_diff = secs_since_epoch - decoded_timestamp
#     if abs(time_diff) > max_age:
#         raise SignatureExpired("decoded timestamp = '%s'; current seconds since epoch = '%s'; current - decoded = '%s'" % (decoded_timestamp, secs_since_epoch, time_diff))
#     return string_res


def unsign(signed_text, key, max_age=10 * 60):
    if not isinstance(signed_text, six.text_type) or not isinstance(key, six.text_type):
        raise BadSignature("input string should be a text type (py2 - unicode; py3 - str)")
    timestamped_string, signature_in = signed_text.rsplit('.', 1)
    signature_calced = make_hmac_signature(timestamped_string, key)
    if signature_calced != signature_in:
        raise BadSignature("signature '%s' does not match" % signature_in)
    unsigned_result, timestamp = timestamped_string.rsplit('.', 1)
    decoded_timestamp_str = base64.b64decode(timestamp)
    try:
        decoded_timestamp = float(decoded_timestamp_str)
    except ValueError:
        raise BadSignature("timestamp does not decode to a float. timestamp = '%s'" % timestamp)
    secs_since_epoch = get_secs_since_epoch()
    time_diff = secs_since_epoch - decoded_timestamp
    if abs(time_diff) > max_age:
        raise SignatureExpired("decoded timestamp = '%s'; current seconds since epoch = '%s'; current - decoded = '%s'" % (decoded_timestamp, secs_since_epoch, time_diff))
    return unsigned_result


# def unsign_compare():
#     sse = get_secs_since_epoch()
#     # signed = sign_new(six.text_type('what'), six.text_type('why'), secs_since_epoch=sse)
#     # print("unsigned old = %s" % unsign(signed, six.text_type('why')))
#     # print("unsigned new = %s" % unsign_new(signed, six.text_type('why')))
#     signed = sign_new('what', 'why', secs_since_epoch=sse)
#     # print("unsigned old = %s" % unsign(signed, 'why'))
#     print("unsigned new = %s" % unsign_new(signed, 'why'))


# below functions are helpers for testing and debugging

def datetime_from_secs(secs):
    timestamp = secs + ARBITRARY_EPOCH
    return pytz.utc.localize(datetime.datetime.utcfromtimestamp(timestamp))


def to_chicago_time(a_time):
    chicago = pytz.timezone('America/Chicago')
    return a_time.astimezone(chicago)
