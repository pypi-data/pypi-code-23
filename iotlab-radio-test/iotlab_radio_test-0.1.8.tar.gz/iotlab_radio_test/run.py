#!/usr/bin/env python
import Queue
import logging
import os
import socket
import sys
import threading

from iotlab_radio_test.constants import PREFIX_RAW, FORMAT_STRING_CH_TX, FORMAT_STRING_CH_TXNONE, SOCKET_TIMEOUT

class ExperimentLogger(object):
    """ Log output to file
    """

    def __init__(self, raw_dir):
        self.raw_dir = raw_dir

    def append(self, msg, channel, txpower):
        if txpower is None:
            filename = FORMAT_STRING_CH_TXNONE.format(PREFIX_RAW, channel, 'log')
        else:
            filename = FORMAT_STRING_CH_TX.format(PREFIX_RAW, channel, float(txpower), 'log')
        full_path = os.path.join(self.raw_dir, filename)
        logging.debug("writing file to %s ", filename)
        with open(full_path, "a") as output_file:
            output_file.write(msg)

        merge_full_path = os.path.join(self.raw_dir, 'radio-raw.log')
        with open(merge_full_path, "a") as output_file:
            output_file.write(msg)

    def close(self):
        pass


class ClientCommand(object):
    """ A command to the client thread.
        Each command type has its associated data:

        CONNECT:    (host, port) tuple
        SEND:       Data string
        RECEIVE:    None
        CLOSE:      None
    """
    CONNECT, SEND, RECEIVE, CLOSE = range(4)

    def __init__(self, command_type, data=None):
        self.type = command_type
        self.data = data


class ClientReply(object):
    """ A reply from the client thread.
        Each reply type has its associated data:

        ERROR:      The error string
        SUCCESS:    Depends on the command - for RECEIVE it's the received
                    data string, for others None.
    """
    ERROR, SUCCESS = range(2)

    def __init__(self, reply_type, data=None):
        self.type = reply_type
        self.data = data


class SocketClientThread(threading.Thread):
    """ Implements the threading.Thread interface (start, join, etc.) and
        can be controlled via the cmd_q Queue attribute. Replies are
        placed in the reply_q Queue attribute.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, raw_dir, cmd_q=None, reply_q=None):
        super(SocketClientThread, self).__init__()
        self.cmd_q = cmd_q or Queue.Queue()
        self.cmd_q_total_size = 0
        self.reply_q = reply_q or Queue.Queue()
        self.alive = threading.Event()
        self.alive.set()
        self.socket = None
        self.my_logger = ExperimentLogger(raw_dir)
        self.logger = logging.getLogger('iotlab-radiotest')
        self.fed = False

        self.handlers = {
            ClientCommand.CONNECT: self._handle_connect,
            ClientCommand.CLOSE: self._handle_close,
            ClientCommand.SEND: self._handle_send,
            ClientCommand.RECEIVE: self._handle_receive,
        }

    def run(self):
        # while self.alive.isSet():
        while True:
            try:
                # Queue.get with timeout to allow checking self.alive
                cmd = self.cmd_q.get(True, 0.1)
                # reply = self.reply_q.get(True, 0.1)
                self.handlers[cmd.type](cmd)
            except Queue.Empty:
                if self.fed:
                    self.logger.info("Queue is empty, exiting")
                    sys.exit(0)
                continue

    def join(self, timeout=None):
        self.alive.clear()
        threading.Thread.join(self, timeout)

    def _handle_connect(self, cmd):
        try:
            self.socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((cmd.data[0], cmd.data[1]))
            self.reply_q.put(self._success_reply())
        except IOError as error:
            self.reply_q.put(self._error_reply(str(error)))

    def _handle_close(self, cmd):
        self.socket.close()
        reply = ClientReply(ClientReply.SUCCESS)
        self.reply_q.put(reply)

    def _handle_send(self, cmd):
        my_cmd = cmd.data[0].replace("\n", "")
        self.logger.info("(%s/%s) SEND %s", self.cmd_q.qsize(), self.cmd_q_total_size, my_cmd)
        try:
            self.socket.send(cmd.data[0])
            self.reply_q.put(self._success_reply())
        except IOError as error:
            self.reply_q.put(self._error_reply(str(error)))

    def _handle_receive(self, cmd):
        my_cmd = cmd.data[0].replace("\n", "")
        self.logger.info("(%s/%s) RECV %s", self.cmd_q.qsize(), self.cmd_q_total_size, my_cmd)
        # We assume after X second timeout, all data are received
        # Assume we can get all data in X seconds
        self.socket.settimeout(SOCKET_TIMEOUT)
        data = ""
        while True:
            try:
                packet = (self.socket.recv(4096))
                data += packet
                if not packet:
                    break
            except socket.timeout:
                break
        self.reply_q.put(self._success_reply(data, cmd.data[1], cmd.data[2], cmd.data[3]))
        return

    @staticmethod
    def _error_reply(errstr):
        return ClientReply(ClientReply.ERROR, errstr)

    def _success_reply(self, data=None, node_id=None, channel=None, txpower=None):
        if data is not None:
            self.logger.debug(data)
            self.my_logger.append(data, channel, txpower)
        return ClientReply(ClientReply.SUCCESS, data)

    def send_iotlab_cmd(self, cmd):
        # Copy list argument in a new array
        my_cmd = list(cmd)
        # Put command to the cmd_q queue
        # NOTE: do not forget CR and LR in order to execute command by serial_aggregator
        my_cmd[0] += "\r\n"
        cl_cmd_send = ClientCommand(ClientCommand.SEND, my_cmd)
        self.cmd_q.put(cl_cmd_send)

        # Wait for reply in the same queue in order to preserver order !!!
        # Mandatory in order to write results in good directory hierarchy
        # my_cmd[1] => node_id
        # my_cmd[2] => channel
        # my_cmd[3] => txpower
        cl_cmd_recv = ClientCommand(ClientCommand.RECEIVE, my_cmd)
        self.cmd_q.put(cl_cmd_recv)


def run_main(config, exp_dir, raw_dir, port):
    log_filename = os.path.join(exp_dir, "raw.log")
    setup_logger(log_filename)

    logger = logging.getLogger('iotlab-radiotest')

    logger.info("Starting IoT-LAB Experiment batch in experiment dir %s", exp_dir)
    my_t = SocketClientThread(raw_dir)
    my_t.start()

    logger.info("Connect to serial_aggregator")
    cmd_connect = ClientCommand(ClientCommand.CONNECT, ["localhost", port])
    my_t.cmd_q.put(cmd_connect)

    reply = my_t.reply_q.get()

    if reply.type == ClientReply.ERROR:
        logger.error('Couldnt connect to serial_aggregator on the site SSH, '
                      'you might need to do an auth-cli on the frontend')
        exit(-1)

    cmd = ["", "", "", ""]

    # Question : should we modify first node_id or channel first during time ?
    for node_id in config.node_list:
        for channel in config.radio.channel_list:
            cmd[0] = "channel %s" % channel
            cmd[1] = node_id
            cmd[2] = channel
            cmd[3] = None
            my_t.send_iotlab_cmd(cmd)
            for txpower in config.radio.txpower_list:
                cmd_tuple = (node_id,
                             node_id,
                             txpower,
                             config.radio.packet_size,
                             config.radio.packet_numbers,
                             config.radio.packet_interval)
                # send
                cmd[0] = "m3-%s;send %s %g %u %u %u" % cmd_tuple
                cmd[1] = node_id
                cmd[2] = channel
                cmd[3] = txpower
                my_t.send_iotlab_cmd(cmd)
                # show
                cmd[0] = "show"
                my_t.send_iotlab_cmd(cmd)
                # clear node receive table
                cmd[0] = "clear"
                my_t.send_iotlab_cmd(cmd)
    # Notify thread stop condition
    my_t.fed = True
    my_t.cmd_q_total_size = my_t.cmd_q.qsize()
    logger.info("Total items in command queue %s", my_t.cmd_q_total_size)
    my_t.join()
    logger.info("End")


def setup_logger(log_filename):
    logger = logging.getLogger('iotlab-radiotest')

    formatter = logging.Formatter('%(asctime)s %(message)s')

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)

    log_file = logging.FileHandler(log_filename)
    log_file.setLevel(logging.DEBUG)
    log_file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(log_file)