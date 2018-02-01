"""
.. uml::
    @startuml
    skinparam backgroundColor #EEEBDC

    title Status Slave Heartbeat

    participant HOST
    participant SLAVE

    autonumber 1
    note over HOST, SLAVE: runs every second
    note over HOST #FFAAAA: ""<size:10>0x01,0x01,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_EVENT <size:14>0x01</size>
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x01,0x00,x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_NO_EVENT 0x10
    ... 50ms ...

    newpage Communication Single Key Approved
    skinparam backgroundColor #EEEBDC
    autonumber 1
    note over HOST #FFAAAA: ""<size:10>0x01,0x01,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_EVENT 0x01
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x20,0x08,<PIN:8831>,x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_EVENT_W_PROTOCOL 0x20
    ... 50ms ...

    note over HOST #FFAAAA: ""<size:10>0x01,0x05,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_APPROVED 0x05
    ... 50ms ...

    newpage Communication Single Key Denied
    skinparam backgroundColor #EEEBDC
    autonumber 1
    note over HOST #FFAAAA: ""<size:10>0x01,0x01,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_EVENT 0x01
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x20,0x08,<PIN:8831>,x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_EVENT_W_PROTOCOL 0x20
    ... 50ms ...

    note over HOST #FFAAAA: ""<size:10>0x01,0x05,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_DENIED 0x04
    ... 50ms ...

    newpage Communication Multiple Key Approved
    skinparam backgroundColor #EEEBDC
    autonumber 1
    note over HOST #FFAAAA: ""<size:10>0x01,0x01,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_EVENT 0x01
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x20,0x09,<U2F:23432>x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_EVENT_W_PROTOCOL 0x20
    ... 50ms ...

    note over HOST #FFAAAA: ""<size:10>0x01,0x02,0x16,<1ST CHALLENGE>,0x21</size>""
    HOST -> SLAVE : REQUEST_SECOND_KEY 0x04
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x30,0x40,<2ND KEY>,x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_SECOND_KEY 0x30
    ... 50ms ...

    note over HOST #FFAAAA: ""<size:10>0x01,0x05,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_APPROVED 0x05
    ... 50ms ...

    newpage Slave Status
    skinparam backgroundColor #EEEBDC
    autonumber 1
    note over HOST #FFAAAA: ""<size:10>0x01,0x04,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_STATUS 0x03
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x40,0x10,<STATUS CODES>,x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_STATUS 0x40
    ... 50ms ...
    @enduml
"""
from ...extensions import log

class ResponseMessage:
    """Slave response from reader

    Communication coming from the reader in single byte array and parses into respective fields.

    """
    RESPONSE_NO_EVENT = 0x10
    RESPONSE_EVENT_W_PROTOCOL = 0x20
    RESPONSE_SECOND_KEY = 0x30
    RESPONSE_STATUS = 0x40
    TERMINATOR = b'\n'

    def __init__(self, raw_msg):
        """Message comming from reader

        :param bytes raw_msg:

        """
        assert isinstance(raw_msg, (bytes, bytearray)), 'Message is in {} but bytes are required'.format(type(raw_msg))
        self.__status = {'temp': 0, 'validations': 0, 'denials': 0}
        self.__registration = {'uuid': '0', 'version': '0.0.0'}
        self.__address = 0
        self.__frame_type = 0
        self.__data_size = 0
        self.__data = None
        self.__valid = True
        self.__is_status = False
        self.__is_registration = False

        try:
            self.__address = int.from_bytes(raw_msg[:1], byteorder='big')
            self.__frame_type = int.from_bytes(raw_msg[1:2], byteorder='big')
            self.__data_size = int.from_bytes(raw_msg[2:3], byteorder='big')
        except (TypeError, KeyError):
            self.__valid = False
        else:
            if self.RESPONSE_NO_EVENT <= self.frame_type <= self.RESPONSE_STATUS:
                if self.frame_type == self.RESPONSE_STATUS and self.data_size is not 0:
                    self._parse_status(raw_msg[3:])

                if self.data_size is not 0:
                    self.__data = raw_msg[3:]
                else:
                    self.__data = None
            else:
                self.__valid = False

    def _parse_status(self, data):
        try:
            status = data.decode('utf-8').split(':')
        except UnicodeDecodeError:
            pass
        else:
            try:
                for param in status:
                    if param[0] == 'T':
                        self.status['temp'] = int(param[1:])
                        self.__is_status = True
                    elif param[0] == 'V':
                        self.status['validations'] = int(param[1:])
                        self.__is_status = True
                    elif param[0] == 'D':
                        self.status['denials'] = int(param[1:])
                        self.__is_status = True
                    elif param[0] == 'U':
                        num = int.from_bytes(param[1:].encode(), byteorder='little')
                        self.__registration['uuid'] = str(num)
                        self.__is_registration = True
                    elif param[0] == 'S':
                        self.__registration['version'] = param[1:]
                        self.__is_registration = True
            except (ValueError, TypeError, AttributeError) as e:
                log.debug('Error parsing status data: {}'.format(e))

    @property
    def is_registration(self):
        return self.__is_registration

    @property
    def registration(self):
        return self.__registration

    @property
    def is_status(self):
        return self.__is_status

    @property
    def status(self):
        return self.__status

    @property
    def address(self):
        return self.__address

    @property
    def frame_type(self):
        return self.__frame_type

    @property
    def data_size(self):
        return self.__data_size

    @property
    def data(self):
        return self.__data

    @property
    def valid(self):
        return self.__valid

    @property
    def message(self):
        """Message of response

        :returns: bytearray representing the message

        """
        msg = bytearray()
        msg.append(self.address)
        msg.append(self.frame_type)
        msg.append(self.data_size)

        if self.data_size != 0:
            data = self.data.to_bytes(self.data_size, byteorder='big')
            msg.extend(data)

        return msg


class ReaderRequestMessage:
    """Slave request

    Represents the communication sent to the slave reader.

    Arguments passed to the class are encoded into a byte array
    suitable for transmission to the reader.

    >>> msg = ReaderRequestMessage(0x01, 0x01, None)

    """
    REQUEST_EVENT = 0x01
    REQUEST_SECOND_KEY = 0x02
    REQUEST_STATUS = 0x03
    REQUEST_DENIED = 0x04
    REQUEST_APPROVED = 0x05
    REQUEST_STATUS_COMMAND = b'S'
    REQUEST_REG_DATA = b'A'
    MAX_DATA = 255

    def __init__(self, address, request_type, data=None):
        assert isinstance(address, int), 'address needs to be of type int'
        assert isinstance(request_type, int), 'request_type needs to be of type int'
        # Hold the empty message to be returned
        self.__message = bytearray()
        self.__message.append(address)
        self.__message.append(request_type)
        self.__data_size = 0
        self.__data = None

        if data is not None:
            """
            If data is greater than 255 bytes, then drop the data.
            """
            if len(data) < self.MAX_DATA:
                self.__data_size = len(data)
                self.__message.append(self.__data_size)
                self.__data = data
                self.__message.extend(self.__data)
            else:
                self.__message.append(0)
        else:
            self.__message.append(0)

        # self._message.extend(self.TERMINATOR)

    @property
    def message(self):
        """Message of request

        :returns: bytearray representing the message

        """
        return self.__message

    @property
    def address(self):
        """Address of request

        :returns: Address encoded on message

        """
        return int.from_bytes(self.__message[:1], byteorder='big')

    @property
    def frame_type(self):
        """Frame type of request

        :returns: int - Type of communication of message

        """
        return int.from_bytes(self.__message[1:2], byteorder='big')

    @property
    def data_size(self):
        """Data Size

        Number of bytes attached to message data section

        :returns: int - data size
        """
        return self.__data_size

    @property
    def data(self):
        """Data on request

        :returns: bytearray - Returns the data encoded onto the message
        """
        return self.__data


class ControllerMessage:
    """Message intended for communication with the host controller

    :param bytes command:
    """

    CONTROLLER_REBOOT = b'R'
    CONTROLLER_TEMP = b'T'
    CONTROLLER_FLASH = b'F'
    CONTROLLER_LONG_FLASH = b'L'
    CONTROLLER_STATUS = b'S'
    CONTROLLER_REG_DATA = b'A'

    def __init__(self, command):
        assert isinstance(command, bytes), 'command needs to be of type bytes'
        self.__message = bytearray()
        self.__message.append(0x00)
        self.__message.append(0x03)
        self.__message.append(0x01)
        self.__message.extend(command)

    @property
    def message(self):
        """Message of request

        :returns: bytearray representing the message

        """
        return self.__message
