# -*- coding: utf-8 -*-

from __future__ import print_function

import socket
import time
import logging

from .disassembler import PacketDisassembler, GreetingDisassembler
from .assembler import SimpleAssembler
from .event import AmiPublisherSubscriber

logger = logging.getLogger(__name__)


SERVE_SLEEP = 1
BUFFER_SIZE = 1024 * 1024


class Manager(object):
    _socket = None
    _host = None
    _port = None
    _secret = None
    _reconnect = None

    _assembler = None
    _disassembler = None
    _state_holder = None
    _serve_sleep = 1

    _event = None

    def __init__(self, host, port, user, secret, reconnect=False):
        self._host = host
        self._port = port
        self._user = user
        self._secret = secret
        self._reconnect = reconnect
        self._state_holder = self.StateHolder()
        self._event = AmiPublisherSubscriber()
        
        self._state_holder.play()
        self._switch_to_start_state()

    def serve_forever(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect()
        self._do_serve()

    def _switch_to_start_state(self):
        self._assembler = SimpleAssembler()
        self._disassembler = GreetingDisassembler(
            ongreeting=self._on_greeting
        )

    def _switch_to_full_state(self):
        self._disassembler = PacketDisassembler(
            onpacket=self._on_packet,
            onresponse=self._on_response,
            onevent=self._on_event,
            onunkown=self._onunkown
        )
    
    def _on_greeting(self, packet):
        self._switch_to_full_state()
        self._login()

    def _on_packet(self, packet):
        self._event.fire(packet)
        
    def _on_response(self, packet):
        pass

    def _on_event(self, packet):
        pass

    def _onunkown(self, packet):
        pass

    def _onlogin(self):
        pass

    def _do_serve(self):
        while True:
            
            try:
                self._state_holder.check()
            except self.StateHolder.StateHolderPause:
                self._sleep()
                continue
            except self.StateHolder.StateHolderStop:
                self._close()
                return
            
            try:
                received = self._socket.recv(BUFFER_SIZE)
            except Exception as exception:
                print(exception)
                self._close()
                return

            if received:
                self._disassembler(received)
            else:
                print('get empty received [%s]' % received)
            
            self._sleep()
    
    def _sleep(self):
        time.sleep(SERVE_SLEEP)
    
    def _close(self):
        try:
            self._socket.shutdown()
            self._socket.close()
        except Exception:
            pass
    
    def _pause_listen(self):
        self._state_holder.pause()

    def _connect(self):
        if self._socket is None:
            raise ValueError

        self._socket.connect((self._host, self._port))

    def _login(self):
        return self.send({
            'Action': 'Login',
            'ActionID': 1,
            'Username': self._user,
            'Secret': self._secret
        })

    def send(self, data):
        return self._socket.send(self._assembler(data))

    @property
    def event(self):
        return self._event

    class StateHolder(object):
        _state = None

        def stop(self):
            self._state = self.StateHolderStop()

        def pause(self):
            self._state = self.StateHolderPause()
        
        def play(self):
            self._state = self.StateHolderPlay()

        def check(self):
            if not isinstance(self._state, self.StateHolderPlay):
                raise self._state or self.StateHolderNone()

        class StateHolderStop(Exception): pass
        class StateHolderPause(Exception): pass
        class StateHolderPlay(Exception): pass
        class StateHolderNone(Exception): pass
