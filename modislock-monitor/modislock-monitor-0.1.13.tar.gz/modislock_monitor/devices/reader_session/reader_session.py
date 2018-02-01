"""
.. uml::
@startuml

skinparam titleFontSize 20
skinparam titleFontColor blue
title State of Slave

skinparam state {
    StartColor MediumBlue
    EndColor Red

    BackgroundColor Peru
    BorderColor Gray
    ArrowColor red

    FontName Impact
    FontSize 16
    FontStyle plain
    FontColor black
    FontAlign center

    AttributeFontSize 12
    AttributeFontName sans
    AttributeFontStyle plain
    AttributeFontColor black
    AttributeFontAlign center

    ArrowFontSize 8
    ArrowFontName sans
    ArrowFontStyle italic
    ArrowFontColor black
    ArrowFontAlign left
}

[*] -down-> Idle : Newly\ncreated\nreader
Idle -left-> [*] : Timed out

state Idle {
    Idle : This state is renewed when a no event\nresponse is received from host.
    Idle -down-> Idle : No Event\nResponse
    Idle -down-> Processing : <-Event\nwith\nprotocol\nattached\nreceived\n
}

state Processing {
    Processing : Lookup protocol to determine how many keys and handler.
    Processing --> Waiting_For_Key : <-Waiting\nfor\nrequested\nkey
    Processing --> Idle : <-Approved/Denied

    state Validating {
        Validating : Validation will be handled by the validator which is a\ndynamic object, based on system options
    }
}

state Waiting_For_Key {
    Waiting_For_Key : Is a delay countdown state.\nIf the delay times out the\ntransaction is canceled.
    Waiting_For_Key --> Processing : <-Requested key\nsent for\nvalidation
}
@enduml

"""

from struct import pack
from transitions import Machine

# Database
from modislock_monitor.database import (Database, Relay, Reader, Door)
from .protocol import Validator
from .protocol.base import BaseValidator
from .reader_message import ResponseMessage, ReaderRequestMessage

# Timer
from threading import Timer


class ReaderSession:
    """SlaveReader represents a connected reader

    """
    states = ['idle', 'processing', 'waiting_for_key']

    def __init__(self, message, sensor_id, timeout=10, request_cb=None):
        """Main entry point for validation.

        Keeps track of address of origin of the frame.
        Has a state machine for the purpose of second validation cycle.

        :param ResponseMessage message: Address of Slave
        :param int timeout: Timeout for each request, after which time the session will end and return a denied
        :param func request_cb: Callback used when after validation/denied/request second key will send the message to

        """
        # Address of slave
        self.__address = message.address
        self.__sensor_id = sensor_id

        # State machine
        self.__machine = Machine(model=self, states=ReaderSession.states, initial='idle')

        # Transitions for the machine added
        self.__machine.add_transition(trigger='no_event',
                                      source='idle',
                                      dest='idle',
                                      after='_reset')
        self.__machine.add_transition(trigger='event_w_protocol',
                                      source='idle',
                                      dest='processing')
        self.__machine.add_transition(trigger='second_key_needed',
                                      source='processing',
                                      dest='waiting_for_key')
        self.__machine.add_transition(trigger='approved',
                                      source='waiting_for_key',
                                      dest='idle')
        self.__machine.add_transition(trigger='approved',
                                      source='processing',
                                      dest='idle')
        self.__machine.add_transition(trigger='denied',
                                      source='processing',
                                      dest='idle',
                                      after='_reset')
        self.__machine.add_transition(trigger='denied',
                                      source='waiting_for_key',
                                      dest='idle',
                                      after='_reset')

        # Callback for write requests
        self.__request = request_cb or self._default_request_cb

        # Validation Callable
        self.__validator = None

        # Timer object
        self._timer = Timer(timeout, self._session_timeout)
        self._timer.start()

        self.process_message(message)

    def _session_timeout(self):
        """Session Callback

        If the session times out, it will be reported back to the monitor for session destruction

        """
        self._reset()

    def _default_request_cb(self, write_message):
        """Default request call back.

        .. note:: Used if none is provided.

        :param str write_message: Message to be sent to callback

        """
        pass

    def _reset(self):
        """Reset the validator.

        This represents a resolved validation request and will send a denied response
        back through the request_cb.

        """
        # self.__validator = None
        self._timer.cancel()
        send_msg = ReaderRequestMessage(self.__address, ReaderRequestMessage.REQUEST_DENIED)
        self.__request(send_msg)

    def process_message(self, message):
        """Process incoming message

        Called during all stages of validation. Incoming packets are processed for
        validation or denied results. Results are passed to the request_cb.

        :param bytes message_str: Message to be processed originating from the reader

        """
        if self.__machine.is_state('idle', self):
            if message.frame_type == ResponseMessage.RESPONSE_NO_EVENT:
                self.no_event()
                return
            elif message.frame_type == ResponseMessage.RESPONSE_EVENT_W_PROTOCOL:
                # Transition state to -> State Processing
                self.event_w_protocol()
            else:
                self.no_event()

        if self.__machine.is_state('processing', self):
            """
            Process state is the main working area of the class. Validation and or request for second key here.
            """
            try:
                self.__validator = Validator(message.address, message.data)
            except (KeyError, TypeError):
                self.denied()
                return

            if self.__validator.valid:
                result = self.__validator.validate(message.data[3:])

                if result[0] == BaseValidator.VALIDATION_FIRST:
                    # Form message to reader, address, frame and challenge are on the argument
                    send_msg = ReaderRequestMessage(message.address, ReaderRequestMessage.REQUEST_SECOND_KEY, result[1])
                    # Change state machine to waiting_for_key
                    self.second_key_needed()
                    # Send the message
                    self.__request(send_msg)
                elif result[0] == BaseValidator.VALIDATION_OK:
                    self._timer.cancel()
                    self.approved()
                    send_msg = ReaderRequestMessage(message.address, ReaderRequestMessage.REQUEST_APPROVED, self.get_relay_settings())
                    self.__request(send_msg)

                elif (result[0] == BaseValidator.VALIDATION_DENIED) or \
                        (result[0] == BaseValidator.VALIDATION_NOT_FOUND) or \
                        (result[0] == BaseValidator.VALIDATION_ERROR):
                    self.denied()
            else:
                self.denied()
                return

        elif self.__machine.is_state('waiting_for_key', self):
            if message.frame_type == ResponseMessage.RESPONSE_SECOND_KEY:
                # State Waiting_For_Key - received second key on frame
                result = self.__validator.validate(message.data)

                if result[0] == BaseValidator.VALIDATION_OK:
                    self.approved()
                    self._timer.cancel()
                    send_msg = ReaderRequestMessage(message.address, ReaderRequestMessage.REQUEST_APPROVED, self.get_relay_settings())
                    self.__request(send_msg)

                elif (result[0] == BaseValidator.VALIDATION_DENIED) or \
                        (result[0] == BaseValidator.VALIDATION_NOT_FOUND) or \
                        (result[0] == BaseValidator.VALIDATION_ERROR):
                    self.denied()
            else:
                self.denied()

    @property
    def address(self):
        """Address of current session slave address

        :returns: address of slave

        """
        return self.__address

    def get_relay_settings(self):
        """Retrieves Reader Associated Relay Settings

        Requests the relay settings from the database. If the database fails, then relays fail to be triggered.

        .. note:: SELECT reader.name, door.name, relay.type, relay.enabled, relay. delay
        FROM relay JOIN door ON relay.door_iddoor = door.iddoor
        JOIN reader ON door.iddoor = reader.door_iddoor
        WHERE reader.idreader = 1;

        :returns bytes: encoded relay settings

        """
        with Database() as db:
            # Database connection
            relay = db.session.query(Relay)\
                .join(Door, Relay.door_iddoor == Door.iddoor)\
                .join(Reader, Door.iddoor == Reader.idreader)\
                .with_entities(Reader.name, Door.name, Relay.type, Relay.enabled, Relay.delay, Relay.position)\
                .filter(Reader.idreader == self.__sensor_id).all()

            relay_settings = {'r1': 0, 'r1d': 0, 'r2': 0, 'r2d': 0, 'o1': 0, 'o1d': 0, 'o2': 0, 'o2d': 0}

            if relay is not None:
                for settings in relay:
                    if 'MECHANICAL' in settings.type:
                        relay_settings['r1' if settings.position == 1 else 'r2'] = settings.enabled
                        relay_settings['r1d' if settings.position == 1 else 'r2d'] = settings.delay
                    elif 'SOLID_STATE' in settings.type:
                        relay_settings['o1' if settings.position == 3 else 'o2'] = settings.enabled
                        relay_settings['o1d' if settings.position == 3 else 'o2d'] = settings.delay

            """
            Formatting of the data is byte, int, byte, int , byte, byte
            """
            ret_relays = pack('>BIBIBIBI',
                              relay_settings['r1'],
                              relay_settings['r1d'],
                              relay_settings['r2'],
                              relay_settings['r2d'],
                              relay_settings['o1'],
                              relay_settings['o1d'],
                              relay_settings['o2'],
                              relay_settings['o2d'])

            return ret_relays
