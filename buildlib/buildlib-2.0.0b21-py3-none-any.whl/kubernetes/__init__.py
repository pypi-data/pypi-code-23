from buildlib.kubernetes import cmd
from base64 import b64encode
import string
import random


def generate_password(length: int = 32):
    """
    Generate a base64 encoded string consisting of numbers and upper/lower case
    ascii letters.
    Kubernetes requires base64 encoding.
    """
    rand_items = (
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _
        in range(length)
    )
    s = ''.join(rand_items)
    s = b64encode(s.encode()).decode('utf8')

    return s
