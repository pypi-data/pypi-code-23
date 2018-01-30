import logging
from .exceptions import NotNumber, BadPortNumber
__author__ = 'Benjamin P. Trachtenberg'
__copyright__ = "Copyright (c) 2018, Benjamin P. Trachtenberg"
__credits__ = 'Benjamin P. Trachtenberg'
__license__ = 'MIT'
__status__ = 'prod'
__version_info__ = (1, 0, 0, __status__)
__version__ = '.'.join(map(str, __version_info__))
__maintainer__ = 'Benjamin P. Trachtenberg'
__email__ = 'e_ben_75-python@yahoo.com'
LOGGER = logging.getLogger(__name__)


def check_number(number):
    """
    Function to verify item entered is a number
    :param
        number: Thing to check for a number
    :return
        Exception if it is not good

    """
    try:
        int(number)

    except Exception:
        LOGGER.critical('Function check_number bad number {number}'.format(number=number))
        raise NotNumber('A number is required you entered {number}!!'.format(number=number))


def check_tcp_udp_port_number(port_number):
    """
    Function to verify a  tcp or udp port number 0 to 65535
    :param
        port_number: The VLAN number
    :return
        Exception if it is not good

    """
    check_number(port_number)

    if int(port_number) not in range(1, 65536):
        LOGGER.critical('Function check_tcp_udp_port_number bad tcp/udp port# '
                        '{port_number}'.format(port_number=port_number))
        raise BadPortNumber('TCP/UDP port numbers should be between 1 and 65535, you entered '
                            '{port_number}'.format(port_number=port_number))