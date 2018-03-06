"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""

from time import sleep
from jemu_mem_peripheral import JemuMemPeripheral
import threading

class JemuConnectionException(Exception):
    pass

class JemuSudo(JemuMemPeripheral):
    _id = None
    _jemu_connection = None
    _peripheral_type = None
    _state = None

    _STOP_AFTER_COMMAND = "stop_after"
    _START_COMMAND = "resume_running"
    _COMMAND = "command"
    _NANO_SECONDS = "nanoseconds"
    _TYPE_STRING = "type"
    _PERIPHERAL_ID = "peripheral_id"
    _PERIPHERAL_TYPE = "peripheral_type"
    _STOPPED = "stopped"
    _RESUMED = "resumed"
    _COMMAND_SET_TIMER = "set_timer"
    _MESSAGE_ID = "message_id"
    _GET_STATE_COMMAND = "get_state"
    _CANCEL_STOP_ON_TICK = "cancel_stop"
    _GET_DEVICE_TIME = "get_device_time"

    def __init__(self, jemu_connection, id, peripheral_type):
        JemuMemPeripheral.__init__(self, jemu_connection, id, peripheral_type, None)
        self._id = id
        self._timer_id_counter = 0
        self._peripheral_type = peripheral_type
        self._jemu_connection = jemu_connection
        self._jemu_connection.register(self.receive_packet)
        self._timer_id_callback_dict = {}
        self._state_lock = threading.RLock()
        self._state = None
        self._device_time_lock = threading.RLock()
        self._device_time = None
        self._resumed_packet_received = threading.Event()
        self._stopped_packet_received = threading.Event()

    def _generate_json_command(self, command):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: command,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def stop_after_ns(self, nanoseconds):
        json_command = self._generate_json_command(self._STOP_AFTER_COMMAND)
        json_command[self._NANO_SECONDS] = nanoseconds
        self._jemu_connection.send_json(json_command)

    def run_for_ns(self, nanoseconds):
        if self.get_state() == 'running':
            self._stopped_packet_received.clear()
            self.stop_after_ns(0)
            self._wait_for_event_from_connection(self._stopped_packet_received)

        if nanoseconds > 0:
            self._stopped_packet_received.clear()
            self.stop_after_ns(nanoseconds)
            self.resume()
            self._wait_for_event_from_connection(self._stopped_packet_received)

    def resume(self):
        if self.get_state() == 'paused':
            self._resumed_packet_received.clear()
            self._jemu_connection.send_json(self._generate_json_command(self._START_COMMAND))
            self._wait_for_event_from_connection(self._resumed_packet_received)

    def wait_until_stopped(self):
        self._stopped_packet_received.clear()
        self._wait_for_event_from_connection(self._stopped_packet_received)

    def _wait_for_event_from_connection(self, event):
        while not event.is_set():
            if not self._jemu_connection.is_connected():
                raise JemuConnectionException("Error: The Emulator was closed unexpectedly.")
            event.wait(0.2)

    def cancel_stop(self):
        self._jemu_connection.send_json(self._generate_json_command(self._CANCEL_STOP_ON_TICK))

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._TYPE_STRING] == self._STOPPED:
            self._stopped_packet_received.set()

        elif jemu_packet[self._TYPE_STRING] == self._RESUMED:
            self._resumed_packet_received.set()

        elif 'type' in jemu_packet and jemu_packet["type"] == "timer_id":
            cur_id = jemu_packet["value"]
            for id_from_dict in self._timer_id_callback_dict:
                if id_from_dict == int(cur_id):
                    self._timer_id_callback_dict[int(cur_id)]()

        elif 'type' in jemu_packet and jemu_packet["type"] == "emulator_state":
            with self._state_lock:
                self._state = jemu_packet["value"]

        elif 'type' in jemu_packet and jemu_packet["type"] == "device_time":
            with self._device_time_lock:
                self._device_time = jemu_packet["value"]

    def set_timer(self, ticks, callback):
        self._timer_id_callback_dict.update({self._timer_id_counter: callback})
        json_command = self._generate_json_command(self._COMMAND_SET_TIMER)
        json_command[self._NANO_SECONDS] = ticks
        json_command[self._MESSAGE_ID] = self._timer_id_counter
        self._timer_id_counter += 1
        self._jemu_connection.send_json(json_command)

    def get_state(self):
        self._state = None
        json_command = self._generate_json_command(self._GET_STATE_COMMAND)
        self._jemu_connection.send_json(json_command)
        state = self._state
        while state is None:
            sleep(0.01)
            with self._state_lock:
                state = self._state
        return self._state

    def _get_device_time(self):
        stop = False
        while not stop:
            sleep(0.01)
            with self._device_time_lock:
                if self._device_time is not None:
                    stop = True
        return self._device_time

    def get_device_time_ns(self):
        self._device_time = None
        json_command = self._generate_json_command(self._GET_DEVICE_TIME)
        self._jemu_connection.send_json(json_command)
        return self._get_device_time()
