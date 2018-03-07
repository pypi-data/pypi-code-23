import os
import sys
import logging
import logging.handlers
import multiprocessing
import multiprocessing.queues
import threading
import traceback
import time
try:
    import SocketServer as socketserver
except ImportError:
    import socketserver
import struct
import pickle
import select


# logging via sockethandler
__socket_logging_inited = False


def init_socket_logging(level=logging.INFO, host='localhost', port=logging.handlers.DEFAULT_TCP_LOGGING_PORT):
    global __socket_logging_inited
    logger = logging.getLogger()
    if not __socket_logging_inited:
        logger.setLevel(level)
        __socket_logging_inited = True
        logger.addHandler(logging.handlers.SocketHandler(host, port))
    else:
        logger.warning('multiple calls to init_socket_logging.')


class _LogSocketHandler(socketserver.StreamRequestHandler):
    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        logger = logging.getLogger()
        while True:
            chunk = self.rfile.read(4)
            if len(chunk) < 4:
                logger.warning('len(chunk)<4 in LogSocketHandler. Socket log may lost.')
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.rfile.read(slen)
            while len(chunk) < slen:
                chunk = chunk + self.rfile.read(slen - len(chunk))
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            logger.handle(record)


def _init_logging():
    log_dir = './log/'
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    log_file = time.strftime('%Y_%m_%d_%H_%M_%S') + '.log'
    log_path = os.path.join(log_dir, log_file)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter('%(asctime)s_%(levelname)s_%(processName)s_%(process)d_%(module)s:  %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(log_path, mode='w', maxBytes=100000000)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(fmt)
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


class _LogSocketServer(socketserver.ThreadingTCPServer):

    def __init__(self, host='localhost', port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=_LogSocketHandler):
        super().__init__((host, port), handler)
        _init_logging()
        logging.getLogger().info('socket logging server inited!')

    def start_server(self):
        logging.getLogger().info('start logging server forever!')
        while True:
            rd, wd, xd = select.select([self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()


__server_process = None


def _start_socket_logging_server():
    server = _LogSocketServer()
    server.start_server()


def start_socket_logging_server():
    global __server_process
    __server_process = multiprocessing.Process(target=_start_socket_logging_server)
    __server_process.daemon = True
    __server_process.start()
    return __server_process


def get_socket_server_process():
    global __server_process
    return __server_process


def get_logger(name=''):
    return logging.getLogger(name)
