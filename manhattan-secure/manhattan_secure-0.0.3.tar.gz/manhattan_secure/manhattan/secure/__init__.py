"""
Utils for securing processes and data.
"""

import binascii
import hashlib
import random
import time
import urllib.parse
import uuid

__all__ = [
    'encrypt_password',
    'random_code',
    'random_token',
    'safe_redirect_url'
    ]


def encrypt_password(password, salt, hash_name='sha256', iterations=100000):
    """
    Given a password and salt[1] return a hash string that cannot be reversed
    but which can be regenerated given the same password and salt.

    The name of the hash used and the number of iterations performed can be
    specified, by default the hash used is 'sha256' and the number of itertaions
    is 100,000.

    NOTE: When running tests it can be a good idea to specify a lower number of
    iterations (e.g 1) as the default 100,000 takes a while and can dramatically
    increase the amount of time it takes for tests to complete.

    NOTE: Remember the salt needs to be stored along with the password hash,
    without the salt it's not possible to test if a password from a user is
    correct.

    [1] (https://en.wikipedia.org/wiki/Salt_%28cryptography%29)
    """
    dk = hashlib.pbkdf2_hmac(
        hash_name,
        str(password).encode('utf8'),
        str(salt).encode('utf8'),
        iterations
        )
    return str(binascii.hexlify(dk))

def random_code(length=8, charset='abcdefghkmnopqrstuvw23456789'):
    """
    Generate a random code. Optionally the length of the code and the charset
    used to generate it can be specified.

    NOTE: Random codes are suitable for short term one time use, for example a
    asking a user to confirm an action by entering a code we sent them. They are
    not suitable as passwords, even if the charset is made more complex there's
    no guarantee the output code will be good/safe password choice.
    """
    rnd = random.SystemRandom()
    return ''.join([rnd.choice(charset) for i in range(0, length)])

def random_token():
    """Generate a random hexadecimal token 32 characters in length"""
    m = hashlib.md5()
    m.update(str(time.time()).encode('utf8'))
    m.update(str(uuid.uuid4()).encode('utf8'))
    return m.hexdigest()

def safe_redirect_url(url, ignore_paths=None):
    """
    Return a local path that can be safely redirected to, e.g after successfully
    signing in. If a safe redirect path cannot be generated then `None` is
    returned.

    URLs are converted to a local path (e.g `'http://www.example.com/foo'`
    becomes `'/foo'`).

    Optionally a list of paths that should be ignored can be specified. It's
    common practise to specify the '/sign-out' path (or equivalent) as this can
    put the user in a never ending loop.

    NOTE: There is not check performed to see if the URL exists (e.g if it
    returns a 404.
    """

    # Parse the URL
    url_parts = urllib.parse.urlparse(url)

    # Convert the URL to a local path
    path = url_parts.path

    # Ensure the URL starts with a '/'
    if not path.startswith('/'):
        return None

    # Ensure the path starts with a single '/'
    path = '/' + path.lstrip('/')

    # Check if we should ignore this path
    ignore_paths = ignore_paths or []
    if path in ignore_paths:
        return None

    # URL is safe return it along with any query and/or fragment
    if url_parts.query:
        path += '?' + url_parts.query

    if url_parts.fragment:
        path += '#' + url_parts.fragment

    return path
