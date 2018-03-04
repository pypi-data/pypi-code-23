import zmq
import threading
import uuid
from fysom import Fysom

import machinetalk.protobuf.types_pb2 as pb
from machinetalk.protobuf.message_pb2 import Container


class Publish(object):
    def __init__(self, debuglevel=0, debugname='Publish'):
        self.debuglevel = debuglevel
        self.debugname = debugname
        self._error_string = ''
        self.on_error_string_changed = []
        # ZeroMQ
        context = zmq.Context()
        context.linger = 0
        self._context = context
        # pipe to signalize a shutdown
        self._shutdown = context.socket(zmq.PUSH)
        self._shutdown_uri = b'inproc://shutdown-%s' % str(uuid.uuid4()).encode()
        self._shutdown.bind(self._shutdown_uri)
        # pipe for outgoing messages
        self._pipe = context.socket(zmq.PUSH)
        self._pipe_uri = b'inproc://pipe-%s' % str(uuid.uuid4()).encode()
        self._pipe.bind(self._pipe_uri)
        self._thread = None  # socket worker tread
        self._tx_lock = threading.Lock()  # lock for outgoing messages

        # Socket
        self.socket_uri = ''
        self._socket_port = 0
        self._socket_port_event = threading.Event()   # sync event for port
        self._socket_dsn = ''
        self._socket_dsn_event = threading.Event()   # sync event for dsn
        self._socket_topics = set()
        # more efficient to reuse protobuf messages
        self._socket_rx = Container()
        self._socket_tx = Container()

        # Heartbeat
        self._heartbeat_lock = threading.Lock()
        self._heartbeat_interval = 2500
        self._heartbeat_timer = None
        self._heartbeat_active = False

        # callbacks
        self.on_socket_message_received = []
        self.on_state_changed = []

        # fsm
        self._fsm = Fysom({'initial': 'down',
                          'events': [
                            {'name': 'start', 'src': 'down', 'dst': 'up'},
                            {'name': 'stop', 'src': 'up', 'dst': 'down'},
                            {'name': 'heartbeat_tick', 'src': 'up', 'dst': 'up'},
                          ]})

        self._fsm.ondown = self._on_fsm_down
        self._fsm.onafterstart = self._on_fsm_start
        self._fsm.onup = self._on_fsm_up
        self._fsm.onafterstop = self._on_fsm_stop
        self._fsm.onafterheartbeat_tick = self._on_fsm_heartbeat_tick

    def _on_fsm_down(self, _):
        if self.debuglevel > 0:
            print('[%s]: state DOWN' % self.debugname)
        for cb in self.on_state_changed:
            cb('down')
        return True

    def _on_fsm_start(self, _):
        if self.debuglevel > 0:
            print('[%s]: event START' % self.debugname)
        self.start_socket()
        self.start_heartbeat_timer()
        return True

    def _on_fsm_up(self, _):
        if self.debuglevel > 0:
            print('[%s]: state UP' % self.debugname)
        for cb in self.on_state_changed:
            cb('up')
        return True

    def _on_fsm_stop(self, _):
        if self.debuglevel > 0:
            print('[%s]: event STOP' % self.debugname)
        self.stop_heartbeat_timer()
        self.stop_socket()
        return True

    def _on_fsm_heartbeat_tick(self, _):
        if self.debuglevel > 0:
            print('[%s]: event HEARTBEAT TICK' % self.debugname)
        self.send_ping()
        self.reset_heartbeat_timer()
        return True

    @property
    def error_string(self):
        return self._error_string

    @error_string.setter
    def error_string(self, string):
        if self._error_string is string:
            return
        self._error_string = string
        for cb in self.on_error_string_changed:
            cb(string)

    @property
    def socket_port(self):
        self._socket_port_event.wait()
        return self._socket_port

    @property
    def socket_dsn(self):
        self._socket_dsn_event.wait()
        return self._socket_dsn

    def start(self):
        if self._fsm.isstate('down'):
            self._fsm.start()

    def stop(self):
        if self._fsm.isstate('up'):
            self._fsm.stop()

    def add_socket_topic(self, name):
        self._socket_topics.add(name)

    def remove_socket_topic(self, name):
        self._socket_topics.remove(name)

    def clear_socket_topics(self):
        self._socket_topics.clear()

    def _socket_worker(self, context, uri):
        poll = zmq.Poller()
        socket = context.socket(zmq.XPUB)
        socket.setsockopt(zmq.LINGER, 0)
        if (('ipc://' in uri) or ('inproc://' in uri)):
            socket.bind(uri)
        else:
            self._socket_port = socket.bind_to_random_port(uri)
            self._socket_port_event.set()   # set sync for port
        self._socket_dsn =socket.get_string(zmq.LAST_ENDPOINT, encoding='utf-8')
        self._socket_dsn_event.set()
        poll.register(socket, zmq.POLLIN)
        socket.setsockopt(zmq.XPUB_VERBOSE, 1)  # enable verbose subscription messages

        shutdown = context.socket(zmq.PULL)
        shutdown.connect(self._shutdown_uri)
        poll.register(shutdown, zmq.POLLIN)
        pipe = context.socket(zmq.PULL)
        pipe.connect(self._pipe_uri)
        poll.register(pipe, zmq.POLLIN)

        while True:
            s = dict(poll.poll())
            if shutdown in s:
                shutdown.recv()
                return  # shutdown signal
            if pipe in s:
                socket.send_multipart(pipe.recv_multipart(), zmq.NOBLOCK)
            if socket in s:
                self._socket_message_received(socket)

    def start_socket(self):
        self._thread = threading.Thread(target=self._socket_worker,
                                        args=(self._context, self.socket_uri,))
        self._thread.start()

    def stop_socket(self):
        self._shutdown.send(b' ')  # trigger socket thread shutdown
        self._thread = None
        self._socket_port_event.clear()   # clear sync for port

    def _heartbeat_timer_tick(self):
        with self._heartbeat_lock:
            self._heartbeat_timer = None  # timer is dead on tick

        if self.debuglevel > 0:
            print('[%s] heartbeat timer tick' % self.debugname)

        if self._fsm.isstate('up'):
            self._fsm.heartbeat_tick()


    def reset_heartbeat_timer(self):
        if not self._heartbeat_active:
            return

        self._heartbeat_lock.acquire()
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
            self._heartbeat_timer = None

        if self._heartbeat_interval > 0:
            self._heartbeat_timer = threading.Timer(self._heartbeat_interval / 1000.0,
                                                 self._heartbeat_timer_tick)
            self._heartbeat_timer.start()
        self._heartbeat_lock.release()
        if self.debuglevel > 0:
            print('[%s] heartbeat timer reset' % self.debugname)

    def start_heartbeat_timer(self):
        self._heartbeat_active = True
        self.reset_heartbeat_timer()

    def stop_heartbeat_timer(self):
        self._heartbeat_active = False
        self._heartbeat_lock.acquire()
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()
            self._heartbeat_timer = None
        self._heartbeat_lock.release()

    # process all messages received on socket
    def _socket_message_received(self, socket):
        msg = socket.recv()
        rx = msg

        for cb in self.on_socket_message_received:
            cb(rx)

    def send_socket_message(self, identity, msg_type, tx):
        with self._tx_lock:
            tx.type = msg_type
            if self.debuglevel > 0:
                print('[%s] sending message: %s' % (self.debugname, msg_type))
                if self.debuglevel > 1:
                    print(str(tx))

            self._pipe.send_multipart([identity, tx.SerializeToString()])
            tx.Clear()

    def send_ping(self):
        tx = self._socket_tx
        ids = self._socket_topics
        for receiver in ids:
            self.send_socket_message(receiver, pb.MT_PING, tx)

    def send_full_update(self, identity, tx):
        ids = [identity]
        pparams = tx.pparams
        pparams.keepalive_timer = self._heartbeat_interval
        for receiver in ids:
            self.send_socket_message(receiver, pb.MT_FULL_UPDATE, tx)

    def send_incremental_update(self, identity, tx):
        ids = [identity]
        for receiver in ids:
            self.send_socket_message(receiver, pb.MT_INCREMENTAL_UPDATE, tx)
