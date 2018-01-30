from .server import *
from .handler import *
import sys
import logging
import select
from socket import socket, AF_INET, SOCK_STREAM
from my_own_jim.utils import send_message, get_message
from my_own_jim.config import *
from my_own_jim.core import Jim, JimMessage, JimResponse, JimContactList, JimAddContact, JimDelContact
from my_own_jim.exceptions import WrongInputError
from my_own_repo.server_models import session
from my_own_repo.server_repo import Repo
from my_own_repo.server_errors import ContactDoesNotExist

import my_own_logs.server_log_config
from my_own_logs.decorators import Log
# main
###############################################################################
def main():
    #loop
    try:
        addr = sys.argv[1]
    except IndexError:
        addr = ''
    try:
        port = int(sys.argv[2])
    except IndexError:
        port = 7777
    except ValueError:
        print('Порт должен быть целым числом')
        sys.exit(0)

    handler = Handler()
    server = Server(handler)
    server.bind(addr, port)
    server.listen_forever()



###############################################################################
#
###############################################################################
if __name__ == "__main__":
    main()



