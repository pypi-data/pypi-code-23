# Python implementation of PasswordHash.* (v1.0) https://github.com/defuse/password-hashing
# Requires Python >= v2.7.9, due to https://www.python.org/dev/peps/pep-0466/#new-security-related-features-in-python-2-7-maintenance-releases
# Please note, this code has not been scrutinized or peer-reviewed at all.
# It is a naive attempt to re-implement PasswordHash.php.

import os
import base64
import hashlib
import six

import streql

# These constants may be changed without breaking existing hashes.
PBKDF2_ALGORITHM = u'sha256'
PBKDF2_ITERATIONS = 1000
PBKDF2_SALT_BYTE_SIZE = 24
PBKDF2_HASH_BYTE_SIZE = 24

# format: algorithm:iterations:salt:hash


def create_hash(
        password,
        algorithm=PBKDF2_ALGORITHM,
        iterations=PBKDF2_ITERATIONS,
        salt_byte_size=PBKDF2_SALT_BYTE_SIZE,
        hash_byte_size=PBKDF2_HASH_BYTE_SIZE):
    if isinstance(password, six.text_type):
        password = password.encode('utf-8')

    salt = base64.b64encode(os.urandom(salt_byte_size))
    hash = hashlib.pbkdf2_hmac(
        algorithm, password, salt, iterations)[
        0:hash_byte_size]
    return b'%s:%d:%s:%s' % (algorithm.encode(
        'utf-8'), iterations, salt, base64.b64encode(hash))


def validate_password(password, correct_hash):
    if isinstance(password, six.text_type):
        password = password.encode('utf-8')

    params = correct_hash.split(b':')
    if len(params) != 4:
        return False

    algorithm = params[0].decode('utf-8')
    iterations = int(params[1])
    salt = params[2]
    hash = base64.b64decode(params[3])

    computed_hash = hashlib.pbkdf2_hmac(
        algorithm, password, salt, iterations)[0:len(hash)]

    return streql.equals(hash, computed_hash)
