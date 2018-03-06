"""Provides helper functions.
"""

import socket

def get_my_ip():
    """Returns the local IP address of this machine.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip
