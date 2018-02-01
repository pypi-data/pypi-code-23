# coding: utf-8
import time
from threading import Thread, Event

# Queue
from ..event_queue import EventQueue

# Serial Objects
from serial import SerialException, serial_for_url
from ..transport import WatchedReader, ReaderMessage

# Extensions
from ..extensions import log

# Readers
from .reader_session import ReaderSession, ReaderRequestMessage, ResponseMessage, ControllerMessage

# Sensors
from .door_device import DoorDevice
from .reader_device import ReaderDevice

# Database
from ..database import Controller

# Tasks
from celery.exceptions import OperationalError
from ..tasks import update_door_status, update_reader_status, update_status_request, update_registration


class ControllerDevice(Thread):
    """ControllerDevice(Thread, BaseDevice)

    The controller uses UART communication from the incoming reader requests to determine validation and onboard relay
    settings. GPIO pins associated with each reader are pulled high when a slave ID of 1 to 4 are responding to the
    heartbeat request sent out periodically.

    The controller object acts as the central validation source worker for the Modis Lock. The object is responsible for
    communication with the controller on the lock that in turn communicates to the remote readers. Interface with the
    controller and controller is done through UART.

    GPIO pins are used for both status information as well as sensor readings. These GPIO states are tracked with the
    use of a database connection. Without this connection the controller will fail to initialize.

    Usually a controller object can be created with defaults with the .. file::`__init__.py` file of the package like this:

    """

    STATUS_INTERVAL = 45.0

    def __init__(self, controller):
        assert isinstance(controller, Controller)
        super(ControllerDevice, self).__init__(daemon=True, name='controller ' + controller.name)
        # Name of this controller
        self.__name = controller.name
        # Serial number
        self.__serial = controller.uuid
        # Software version
        self.__firmware_version = controller.software_version
        # Host ID that this controller is attached to
        self.__host_id = controller.host_idhost
        # ID of this controller
        self.__id = controller.idcontroller
        # Port assigned to this controller
        self.__port = controller.port
        self.__doors = list()
        self.__readers = dict()
        self.__sessions = dict()
        # Event on queue to signal events ready to execute
        self.__event = Event()
        self.__event_queue = EventQueue(self.__event)
        # Timer for checking status on readers and controller
        self.__status_timer = Thread(target=self._request_status, name='controller ' + controller.name + ' status')
        self.__transport = None
        self.__running = False

        try:
            serial_port = serial_for_url(self.port, baudrate=controller.baud_rate, timeout=1)
        except SerialException as e:
            log.error('Error initializing serial port: {}'.format(e))
            raise IOError
        else:
            # Serial port setup
            log.debug('Opened port on: {}'.format(controller.port))

        self.__transport = WatchedReader(serial_port, ReaderMessage)
        self.__transport.start()

        while not self.__transport.is_alive():
            time.sleep(0.5)

        self.__transport.set_handlers(self._handle_incoming, self._handle_noise)

        # Initialize the readers, doors
        for door in controller.door:
            self.__doors.append(DoorDevice(door, self._door_callback))

        for reader in controller.reader:
            nw = ReaderDevice(reader, self._reader_callback)
            self.__readers[nw.slave_address] = nw

    def _door_callback(self, door_id, value):
        """Door callback for handling events

        :param door_id:
        :param value:
        :return:
        """
        try:
            update_door_status.delay(door_id, value)
        except OperationalError:
            log.debug('Door status task not delivered:\nDoor id: {}\nValue: {}\n'.format(door_id, value))

    def _reader_callback(self, reader_id, value):
        """Reader callback for handling reader status events

        :param reader_id:
        :param value:
        :return:
        """
        try:
            update_reader_status.delay(reader_id, value)
        except OperationalError:
            log.debug('Reader status task not delivered:\nReader id: {}\nValue: {}\n'.format(reader_id, value))

    def _request_status(self):
        """Periodic task that requests active readers status

        :return:
        """
        time.sleep(10)

        while self.__running:
            log.debug('Requesting status')
            if self.__serial == '0':
                self.__event_queue.enqueue(self._handle_outgoing,
                                           ControllerMessage(ControllerMessage.CONTROLLER_REG_DATA),
                                           priority=200)
            else:
                # Send to host controller first
                self.__event_queue.enqueue(self._handle_outgoing, ControllerMessage(ControllerMessage.CONTROLLER_STATUS),
                                           priority=150)
            # Send to attached readers
            for reader in self.__readers.items():
                # Only active readers are requested
                if reader[1].current_state == reader[1].STATE_ACTIVE:
                    if reader[1].serial_number == '0':
                        self.__event_queue.enqueue(self._handle_outgoing,
                                                   ReaderRequestMessage(reader[0],
                                                                        ReaderRequestMessage.REQUEST_STATUS,
                                                                        ReaderRequestMessage.REQUEST_REG_DATA),
                                                   priority=200)
                    else:
                        self.__event_queue.enqueue(self._handle_outgoing,
                                                   ReaderRequestMessage(reader[0], ReaderRequestMessage.REQUEST_STATUS,
                                                                        ReaderRequestMessage.REQUEST_STATUS_COMMAND),
                                                   priority=150)
            time.sleep(self.STATUS_INTERVAL)

    def _handle_noise(self, packet):
        """Handle any characters that make it past the filters

        :param bytes packet:
        :return:
        """
        log.debug('Garbage received from uart outside of frame: {}'.format(packet))

    def _handle_incoming(self, packet):
        """Handles incoming packets from controller over UART

        :param bytes packet: Incoming packet request from transport
        :return:
        """
        log.debug('raw incoming message: {}'.format(packet))
        reader = ResponseMessage(packet)

        if reader.valid:
            if reader.address in self.__sessions:
                self.__sessions[reader.address].process_message(reader)
            elif reader.address == 0:
                if reader.frame_type == reader.RESPONSE_STATUS:
                    if reader.is_status:
                        try:
                            update_status_request.delay(self.id, 'CONTROLLER', reader.status)
                        except OperationalError:
                            log.debug('Controller response task not delivered:'
                                      '\nController id: {}\nValue: {}\n'.format(self.id, reader.status))
                    elif reader.is_registration:
                        self.__serial = reader.registration.get('uuid', '0')
                        self.__firmware_version = reader.registration.get('version', '0')
                        try:
                            update_registration.delay(self.id, 'CONTROLLER', reader.registration)
                        except OperationalError:
                            log.debug('Controller registration could not be updated')
            else:
                if reader.frame_type == reader.RESPONSE_STATUS:
                    if reader.is_status:
                        try:
                            update_status_request.delay(self.__readers[reader.address].device_id, 'READER', reader.status)
                        except OperationalError:
                            log.debug('Reader response task not delivered:'
                                      '\nReader id: {}\nValue: {}\n'.format(reader.address, reader.status))
                    elif reader.is_registration:
                        try:
                            self.__readers[reader.address].serial_number = reader.registration.get('uuid', '0')
                            self.__readers[reader.address].software_version = reader.registration.get('version', '0')

                            update_registration.delay(self.__readers[reader.address].device_id, 'READER', reader.registration)
                        except OperationalError:
                            log.debug('Reader registration could not be updated')
                        print('Registration data here')
                else:
                    self.__sessions[reader.address] = ReaderSession(reader,
                                                                    self.__readers[reader.address].device_id,
                                                                    request_cb=self._handle_outgoing)
        else:
            log.debug('** invalid packet received **')

    def _handle_outgoing(self, packet, **kwargs):
        """Handles all processed packages returning from the slave reader objects

        :param ReaderRequestMessage packet: Frame outgoing through controller to reader

        """
        if isinstance(packet, ReaderRequestMessage):
            if packet.frame_type == ReaderRequestMessage.REQUEST_DENIED or packet.frame_type == ReaderRequestMessage.REQUEST_APPROVED:
                try:
                    del self.__sessions[packet.address]
                except KeyError:
                    log.error('Key not found in sessions')
            self.__transport.send_packet(packet.message)
            log.debug('reader message sent: {}'.format(packet.message))
        elif isinstance(packet, ControllerMessage):
            self.__transport.send_packet(packet.message)
            log.debug('controller message sent: {}'.format(packet.message))

    @property
    def id(self):
        return self.__id

    @property
    def host_id(self):
        return self.__host_id

    @property
    def name(self):
        return self.__name

    @property
    def port(self):
        return self.__port

    def run(self):
        """Runs the controller thread

        Waits for interrupts and processes the event queue. During startup will send a command to the controller
        to restart.

        """
        # Reset on-board controller
        self.__event_queue.enqueue(self._handle_outgoing,
                                   ControllerMessage(ControllerMessage.CONTROLLER_REBOOT),
                                   priority=100)
        self.__running = True
        self.__status_timer.start()

        while self.__running:
            # Sleep until event happens
            self.__event.wait(timeout=100)
            # Process all the events
            while self.__event_queue.has_more():
                # Dequeue functions to run
                func, args, kwargs = self.__event_queue.dequeue()

                if func is not None:
                    func(*args, **kwargs)
            # All events processed go back to sleep
            self.__event.clear()

        for door in self.__doors:
            door.deinitialize()
        for reader in self.__readers:
            reader.deinitialize()
        self.__transport.stop()
        log.debug('readers/doors/ports de-initialized')

    def stop(self):
        """Stops the current running controller

        :return:
        """
        log.info('controller shutdown requested')
        self.__running = False


