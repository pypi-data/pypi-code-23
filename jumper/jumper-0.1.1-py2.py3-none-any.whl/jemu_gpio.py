"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from threading import Lock


class JemuGpio:
    _PIN_NUM = "pin_number"
    _TRANSITION_TYPE = "transition_type"

    def __init__(self):
        self._pin_level_callback = None
        self._jemu_socket_manager = None
        self._pin_level_statues = dict()
        self._lock = Lock()

    def on_pin_level_event(self, callback):
        with self._lock:
            self._pin_level_callback = callback

    def receive_packet(self, jemu_packet):
        if jemu_packet["type"] == "pin_level_event":
            with self._lock:
                self._pin_level_statues[jemu_packet[self._PIN_NUM]] = jemu_packet[self._TRANSITION_TYPE]
                if self._pin_level_callback:
                    self._pin_level_callback(jemu_packet[self._PIN_NUM], jemu_packet[self._TRANSITION_TYPE])

    def set_connection_manager(self, jemu_socket_manager):
        self._jemu_socket_manager = jemu_socket_manager
        self._jemu_socket_manager.register(self.receive_packet)

    def get_pin_level(self, pin_num):
        with self._lock:
            if pin_num in self._pin_level_statues:
                return self._pin_level_statues[pin_num] 
            else:
                return 1
