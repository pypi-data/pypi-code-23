
# Serial Objects
import serial
from serial.threaded import Protocol
from watchedserial import WatchedReaderThread
from threading import Timer


class PacketHandler(Protocol):
    """Packet Handler for communications between host and readers.

    The handler is quite simplified from the previous version and simply enqueues a task onto the event queue.

    """
    START = b'('
    STOP = b')'

    def __init__(self):
        self.packet = bytearray()
        self.in_packet = False
        self.terminate = False
        self.current_count = 0
        self.remaining_count = 0
        self.transport = None
        self._timer = None

    def _reset_buffer(self):
        del self.packet[:]
        self.in_packet = False
        self.terminate = False
        self.current_count = 0
        self.remaining_count = 0

    def connection_made(self, transport):
        """Store transport"""
        self.transport = transport

    def connection_lost(self, exc):
        """Forget transport"""
        self.transport = None
        self.in_packet = False
        del self.packet[:]
        super(PacketHandler, self).connection_lost(exc)

    def data_received(self, data):
        """Find data enclosed in START/STOP, call handle_packet"""
        for byte in serial.iterbytes(data):
            if byte == self.START and self.in_packet is False:
                self.in_packet = True
                self._timer = Timer(0.200, self._reset_buffer)
                self._timer.start()
            elif self.in_packet is True:
                self.current_count += 1

                if self.current_count == 3:
                    self.remaining_count = int.from_bytes(byte, byteorder='big')
                    self.packet.extend(byte)
                elif self.current_count == (3 + self.remaining_count):
                    self.terminate = True
                    self.packet.extend(byte)
                elif self.terminate and byte == self.STOP:
                    self._timer.cancel()
                    self.handle_packet(bytes(self.packet))  # Make read-only copy
                    self._reset_buffer()
                else:
                    self.packet.extend(byte)
            else:
                self.handle_out_of_packet_data(byte)

    def handle_packet(self, packet):
        """Places the packet with the handler function onto the event queue

        :param bytes packet:

        """
        raise NotImplementedError('please implement functionality in handle_packet')
        # Monitor.monitor.events.enqueue(Monitor.handle_incoming, args=[packet], priority=10)

    def handle_out_of_packet_data(self, data):
        """Handles any bytes received from outside a frame

        :param bytes data:
        """
        raise NotImplementedError('please implement functionality in handle_out_of_packet_data')
        # log.debug('Garbage received from uart outside of frame: {}'.format(data))


class WatchedReader(WatchedReaderThread):
    """Used for robust connectivity to the controller.

    Will reconnect to the controller in event that communication
    is terminated. The following functions are overridden from the base class for events of reconnection and
    disconnection.

    """
    name = 'WatchedReader'

    def __init__(self, serial_instance, protocol_factory):
        super(WatchedReader, self).__init__(serial_instance, protocol_factory)

    def set_handlers(self, handle_frame, handle_noframe):
        if self.protocol:
            self.protocol.handle_frame = handle_frame
            self.protocol.handle_outof_frame = handle_noframe

    def handle_reconnect(self):
        # TODO Handle reconnect
        pass

    def handle_disconnect(self, error):
        # TODO Handle disconnect
        pass

    def send_packet(self, packet):
        """Sends properly terminated frame

        :param bytes packet:
        """
        assert type(packet) is bytearray, 'Type must be byte array'
        message = bytearray(self.protocol.START)
        message.extend(packet)
        message.extend(self.protocol.STOP)
        self.write(message)


# Transportation mechanism
class ReaderMessage(PacketHandler):
    """Packet Handler for communications between host and readers.

    The handler is quite simplified from the previous version and simply enqueues a task onto the event queue.

    """

    def __init__(self):
        super(ReaderMessage, self).__init__()
        self.__handle_frame = None
        self.__handle_outof_frame = None

    def handle_packet(self, packet):
        """Places the packet with the handler function onto the event queue

        :param bytes packet:

        """
        if self.handle_frame is not None:
            self.handle_frame(packet)

    def handle_out_of_packet_data(self, data):
        """Handles any bytes received from outside a frame

        :param bytes data:
        """
        if self.handle_outof_frame is not None:
            self.handle_outof_frame(data)

    @property
    def handle_frame(self):
        return self.__handle_frame

    @handle_frame.setter
    def handle_frame(self, callback):
        self.__handle_frame = callback

    @property
    def handle_outof_frame(self):
        return self.__handle_outof_frame

    @handle_outof_frame.setter
    def handle_outof_frame(self, callback):
        self.__handle_outof_frame = callback
