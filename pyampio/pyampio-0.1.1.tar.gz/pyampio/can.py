"""Ampio CAN protocol implementation."""

import asyncio
import logging
import struct
from enum import Enum, unique


_LOG = logging.getLogger(__name__)


@unique
class Type(Enum):
    """This is a frame type enum for USB CAN module frames."""

    # send raw can frame
    CAN = 0x00
    SEND_VALUE_WITH_MASK = 0x10
    SEND_VALUE_WITH_INDEX = 0x11
    SEND_COMPLEX_FUNCTION = 0x12


class CanType(Enum):
    """CAN frame types."""

    BROADCAST = 0xfe
    DATA_REPLY = 0x0f


class AmpioCanProtocol(asyncio.Protocol):
    """This is an Ampio CAN protocol implementation for serial USB module."""

    def __init__(self,
                 on_connected=None,
                 on_can_broadcast_received=None,
                 on_can_data_received=None,
                 is_relevant=None):
        """Initialize the :class: pyampio.can.AmpioCanProtocol object.

        Args:
            on_connected (callable): The callback function for on_connected event
            on_can_broadcast_received (callable): The callback function for on_broadcast_received event
            on_can_data_received (callable): The callback function for on can_data_received event
            is_relevant (callable): Filter function to filter relevant frames. i.e. can_id based.

        """
        if is_relevant:
            self._is_relevant = is_relevant
        else:
            self._is_relevant = lambda can_id: True

        self._assembly_buffer = b''
        self.transport = None
        # on connected coroutine
        self._on_connected = on_connected
        # 0xfe
        self._on_can_broadcast_received = on_can_broadcast_received
        # 0x0f
        self._on_can_data_received = on_can_data_received

        self.frame_type_map = {
            CanType.BROADCAST: self._on_can_broadcast_received,
            CanType.DATA_REPLY: self._on_can_data_received,
        }

    def connection_made(self, transport):
        """Protocol connection made."""
        self.transport = transport
        _LOG.debug('port opened')
        self.transport.serial.rts = False
        self.transport.serial.dtr = False
        self.transport.serial.write_timeout = 10
        self.transport.serial.reset_input_buffer()
        self.transport.serial.reset_output_buffer()
        if self._on_connected:
            self.transport._loop.create_task(self._on_connected(self))

    @asyncio.coroutine
    def open_connection(self):
        """Protocol connection open."""
        _LOG.debug("Opening connection")

    def send_api_function(self, api_func, can_id, data):
        """Send API function to module.

        Args:
            api_func (int): API function
            can_id (int): CAN ID
            data (bytearray): Data

        """
        self.send_frame(api_func, can_id, bytearray(data))

    def send_module_command(self, func, gateway_can_id, can_id=None):
        """Send module command.

        Args:
            own_can_id (int): own can Id
            can_id (int): destination module can id
            func (int): module function number

        """
        data = can_id.to_bytes(4, byteorder='big') + func.to_bytes(1, byteorder='big') if can_id else \
            func.to_bytes(1, byteorder='big')
        self.send_can_frame(gateway_can_id, data)

    def send_can_frame(self, can_id, data):
        """Send the CAN frame.

        Args:
            can_id (int): CAN ID
            data (bytearray): Array of CAN data bytes

        """
        self.send_frame(Type.CAN, can_id.to_bytes(4, byteorder='big'), data)

    def send_frame(self, frame_type, can_id_bytes, data):
        """Send the RAW frame to serial interface.

        Args:
            frame_type (Type): Frame type enum
            can_id_bytes (bytearray): CAN ID
            data (bytearray): Array of CAN data bytes

        """
        # encode can_id to bytes
        # can_id_bytes = can_id.to_bytes(4, byteorder='big')
        # build the frame
        frame = bytearray(b'\x2d\xd4\x00\x00' + can_id_bytes + data + b'\x00')
        # calculate and update length
        frame[2] = len(frame) - 3
        # update frame type
        frame[3] = frame_type.value
        # calculate CRC
        frame[-1] = sum(frame[:-1]) & 0xff
        self.transport.write(frame)
        can_data_str = " ".join(["{:02x}".format(c) for c in frame])
        _LOG.info("CAN SERIAL OUT: frame=[{}]".format(can_data_str))

    @asyncio.coroutine
    def _process_frame(self, frame):
        frame_len = frame[0]
        if frame_len == 0:
            _LOG.warning("Frame length is zero")
            return
        try:
            frame_type = Type(frame[1])
        except ValueError:
            _LOG.warning("Unknown frame type {}".format(frame[1]))
            return

        if frame_type == Type.CAN:
            can_len = frame[0] - 6
            if not (0 < can_len < 9):
                _LOG.error("Invalid CAN frame length: {}".format(can_len))
                return

            try:
                device_id = struct.unpack(">L", frame[2:6])[0]
            except struct.error:
                _LOG.error("Unable to decode CAN ID: {}".format(frame))

            can_data = frame[6:]
            yield from self._process_can_frame(device_id, can_len, can_data)

    @asyncio.coroutine
    def _process_can_frame(self, can_id, can_len, can_data):
        if self._is_relevant(can_id):
            can_data_str = " ".join(["{:02x}".format(c) for c in can_data])
            _LOG.debug("CAN IN: id={:08x} len={:02x} data=[{}]".format(can_id, can_len, can_data_str))

        try:
            coro = self.frame_type_map[CanType(can_data[0])]
            if coro:
                yield from coro(can_id, can_data)
        except ValueError:
            can_data_str = " ".join(["{:02x}".format(c) for c in can_data])
            _LOG.warning("Frame type not implemented: id={:08x} len={:02x} data=[{}]".format(
                can_id, can_len, can_data_str))

    def data_received(self, data):
        """Process received raw data from the wire."""
        # _LOG.debug("-" * 20)
        # _LOG.debug('Data received: {!r}'.format(data.hex()))
        # _LOG.debug('Assembly buffer: {!r}'.format(self._assembly_buffer.hex()))
        # _LOG.debug("-" * 20)
        data = self._assembly_buffer + data
        data_length = len(data)
        while data_length > 3:
            if data[0:2] == b'\x2d\xd4':
                frame_length = data[2] + 3
                if frame_length > data_length:
                    # frame fragment
                    break
                frame = data[:frame_length]
                crc = sum(frame[:-1]) & 0xff
                if crc == frame[-1]:
                    # _LOG.debug("Data: {!r}".format(frame.hex()))
                    frame = frame[2:-1]
                    self.transport._loop.create_task(self._process_frame(frame))
                else:
                    _LOG.error("CRC error: {!r} calc crc={:02x} frame crc={:02x}".format(frame.hex(), crc, frame[-1]))

                data = data[frame_length:]
                data_length -= frame_length
            else:
                # walk through the buffer trying to find preamble 0x2dd4
                _LOG.warning("Synchronization error. Trying to find a frame preamble")
                _LOG.warning(data)
                data = data[1:]
                data_length -= 1
                # anyway can't assemble frame - resetting the assembly buffer
                self._assembly_buffer = b''

        self._assembly_buffer = data

    def connection_lost(self, exc):
        """Handle the connection lost event."""
        _LOG.error("Port closed")
        self.transport._loop.stop()

    def pause_writing(self):
        """Handle pause writing event."""
        _LOG.warning('pause writing')
        _LOG.warning(self.transport.get_write_buffer_size())

    def pause_reading(self):
        """Handle pause reading event."""
        _LOG.warning(self.transport.get_write_buffer_size())
        _LOG.warning('resume writing')
