"""Defines shared utility functions.
"""
import os
import binascii



def generate_random_digest(num_bytes=28, urandom=None, to_hex=None):
    """Generates a random hash and returns the hex digest.
    """
    if urandom is None:
        urandom = os.urandom
    if to_hex is None:
        to_hex = binascii.hexlify
    
    rvalues = urandom(num_bytes)
    return to_hex(rvalues)

