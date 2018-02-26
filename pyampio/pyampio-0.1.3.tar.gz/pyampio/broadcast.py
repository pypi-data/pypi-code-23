"""This is a broadcast type definition module."""

from enum import Enum
import logging

_LOG = logging.getLogger(__name__)


def bits_to_indices(mask):
    """Generate list of indices of bits set to one in the value."""
    i = 1
    while mask > 0:
        if bool(mask & 0x1):
            yield i
        mask >>= 1
        i += 1
    return


class BroadcastTypes(Enum):
    """The BroadcastTypes enum with known broadcast frame types."""

    TemperatureInt = 0x05
    Temperature1T3 = 0x06
    Temperature4T6 = 0x07
    Analog1T6 = 0x0c
    Analog7T12 = 0x0d
    Analog13T18 = 0x0e
    BinInOut = 0x0f
    DateTime = 0x10
    Value32b = 0x18
    SatelArmed = 0x19
    SatelAlarm = 0x1a
    SatelInput1T48 = 0x1b
    SatelInput49T96 = 0x1c
    SatelInput97T128 = 0x1d
    SatelOutput1T48 = 0x1e
    SatelOutput49T96 = 0x1f
    SatelOutput97T128 = 0x20
    Value16b1T3 = 0x21
    Value16b4T6 = 0x22
    Value16b7T9 = 0x23
    Value16b10T12 = 0x24
    Value16b13T15 = 0x25
    Value8b1T6 = 0x26
    Value8b7T12 = 0x27
    Value8b13T18 = 0x28
    Event = 0x2b
    SatelInput129T176 = 0x31
    SatelInput177T224 = 0x32
    SatelInput225T256 = 0x33
    SatelOutput129T176 = 0x34
    SatelOutput177T224 = 0x35
    SatelOutput225T256 = 0x36
    SatelBreached = 0x38
    SatelArming = 0x39
    SatelArming10s = 0x3a
    HeatingZoneSummary = 0xc8
    HeatingZone1 = 0xc9
    HeatingZone2 = 0xca
    HeatingZone3 = 0xcb
    HeatingZone4 = 0xcc
    HeatingZone5 = 0xcd
    HeatingZone6 = 0xce
    HeatingZone7 = 0xcf
    HeatingZone8 = 0xd0
    HeatingZone9 = 0xd1
    HeatingZone10 = 0xd2
    HeatingZone11 = 0xd3
    HeatingZone12 = 0xd4
    HeatingZone13 = 0xd5
    HeatingZone14 = 0xd6
    HeatingZone15 = 0xd7
    HeatingZone16 = 0xd8
    Flag = 0x80


broadcasts = {}


def register_broadcast(broadcast_types, target_class):
    """Register broadcast class.."""
    for broadcast_type in broadcast_types:
        broadcasts[broadcast_type] = target_class


class BroadcastMeta(type):
    """This is BroadcastMeta class for Broadcast class self registration."""

    def __new__(cls, clsname, bases, attrs):
        """Register the broadcast class."""
        newclass = super(cls, BroadcastMeta).__new__(cls, clsname, bases, attrs)
        register_broadcast(newclass.broadcast_types, newclass)
        return newclass


class BroadcastFactory:
    """This is a BroadcastFactory class for Broadcast object creation."""

    @staticmethod
    def create_broadcast(data):
        """Create the Broadcast object based on the frame date."""
        try:
            broadcast_type = BroadcastTypes(data[0])
        except ValueError:
            _LOG.debug("Unknown broadcast type: {:02x}".format(data[0]))
            return None

        return broadcasts.get(broadcast_type)(data[1:])


class BroadcastCache:
    """The BroadcastCache object is a cache for received broadcast for module."""

    def __init__(self, on_changed=None):
        """Initialize the BroadcastCache object."""
        self._cache = {}
        self._on_changed_callback = on_changed

    def update(self, data):
        """Update the cache with broadcast data."""
        try:
            broadcast_type = BroadcastTypes(data[0])
        except ValueError:
            _LOG.debug("Update for unknown broadcast type: {:02x}".format(data[0]))
            return

        if broadcast_type in self._cache:
            self._cache[broadcast_type].update(data[1:])
        else:
            broadcast = BroadcastFactory.create_broadcast(data)
            if broadcast is not None:
                self._cache[broadcast_type] = broadcast
            else:
                _LOG.warning("Unknown broadcast: {}:{}".format(broadcast, broadcast_type))
                return
        try:
            for change in self._cache[broadcast_type].changes():
                _LOG.debug("Type: {} Change: {}".format(type(self._cache[broadcast_type]), change))
                if self._on_changed_callback is not None:
                    self._on_changed_callback(broadcast_type, change)
        except TypeError:
            _LOG.critical("Data: {}".format(data))
            _LOG.critical("Broadcast type: {}".format(broadcast_type))
            _LOG.critical("Cache: {}".format(self._cache))
            raise

    def get_value(self, broadcast_type, index):
        """Get the value state from broadcast.

        Returns: value state or None if not received yet

        """
        broadcast_object = self._cache.get(broadcast_type, None)
        if broadcast_object:
            return broadcast_object.state(index)
        else:
            return None

    def get_last_value(self, broadcast_type, index):
        """Get the value state from broadcast.

        Returns: value state or None if not received yet

        """
        broadcast_object = self._cache.get(broadcast_type, None)
        if broadcast_object:
            return broadcast_object.last_state(index)
        else:
            return None


class BroadcastBinary(metaclass=BroadcastMeta):
    """This is a BroadcastBinary class representing binary data frames."""

    broadcast_types = [
        BroadcastTypes.Flag,
        BroadcastTypes.BinInOut,
        BroadcastTypes.HeatingZoneSummary,
        BroadcastTypes.SatelInput1T48,
        BroadcastTypes.SatelInput49T96,
        BroadcastTypes.SatelInput97T128,
        BroadcastTypes.SatelInput129T176,
        BroadcastTypes.SatelInput177T224,
        BroadcastTypes.SatelInput225T256,
        BroadcastTypes.SatelOutput1T48,
        BroadcastTypes.SatelOutput49T96,
        BroadcastTypes.SatelOutput97T128,
        BroadcastTypes.SatelOutput129T176,
        BroadcastTypes.SatelOutput177T224,
        BroadcastTypes.SatelOutput225T256,
        BroadcastTypes.SatelArmed,
        BroadcastTypes.SatelAlarm,
        BroadcastTypes.SatelBreached,
        BroadcastTypes.SatelArming,
        BroadcastTypes.SatelArming10s,
    ]

    def __init__(self, data=None):
        """Initialize BroadcastBinary class from frame data."""
        self._value = int.from_bytes(data[2:], byteorder='little', signed=False) if data else 0
        self._previous_value = 0

    def update(self, data):
        """Update BroadcastBinary class from frame data."""
        value = int.from_bytes(data, byteorder='little', signed=False)
        self._previous_value = self._value
        self._value = value

    def changes(self):
        """Yield the value changes in broadcast data."""
        mask = self._previous_value ^ self._value
        for index in bits_to_indices(mask):
            previous_value = bool(self._previous_value & (0x1 << (index - 1)))
            new_value = bool(self._value & (0x1 << (index - 1)))
            yield index, previous_value, new_value

    def state(self, index):
        """Return the current value state from broadcast."""
        return bool(self._value & (0x1 << (index - 1)))

    def last_state(self, index):
        """Return the last value state from broadcast."""
        return bool(self._previous_value & (0x1 << (index - 1)))


class BroadcastValue8b(metaclass=BroadcastMeta):
    """This is a BroadcastValue8b class representing 8-bit data frames."""

    broadcast_types = [
        BroadcastTypes.Analog1T6,
        BroadcastTypes.Analog7T12,
        BroadcastTypes.Analog13T18,
        BroadcastTypes.TemperatureInt,
        BroadcastTypes.Value8b1T6,
        BroadcastTypes.Value8b7T12,
        BroadcastTypes.Value8b13T18,
    ]

    def __init__(self, data=None):
        """Initialize BroadcastValue8b class from frame data."""
        self._values = [None] * 6
        self._previous_values = [None] * 6
        if data:
            self.update(data)

    def update(self, data):
        """Update BroadcastValue8b class from frame data."""
        values = [int(temp) for temp in data] if data else [None] * 6
        for index, value in enumerate(values):
            if value != self._values[index]:
                self._previous_values[index] = self._values[index]
                self._values[index] = value

        _LOG.debug("Value 8b: Value {}".format(self._values))

    def changes(self):
        """Yield the value changes in broadcast data."""
        for index, (current, previous) in enumerate(zip(self._values, self._previous_values), start=1):
            if current != previous:
                yield index, previous, current

    def state(self, index):
        """Return the current value state from broadcast."""
        try:
            return self._values[index - 1]
        except IndexError:
            return None
        return None

    def last_state(self, index):
        """Return the last value state from broadcast."""
        try:
            return self._previous_values[index - 1]
        except IndexError:
            return None
        return None


class BroadcastValue16b(metaclass=BroadcastMeta):
    """This is a BroadcastValue16b class representing 16-bit data frames."""

    broadcast_types = [
        BroadcastTypes.Value16b1T3,
        BroadcastTypes.Value16b4T6,
        BroadcastTypes.Value16b7T9,
        BroadcastTypes.Value16b10T12,
        BroadcastTypes.Value16b13T15,
        BroadcastTypes.Temperature1T3,
        BroadcastTypes.Temperature4T6,
    ]

    def __init__(self, data=None):
        """Initialize BroadcastValue16b class from frame data."""
        self._values = [0] * 3
        self._previous_values = [0] * 3
        if data:
            self.update(data)

    def update(self, data):
        """Update BroadcastValue16b class from frame data."""
        self._previous_values = list(self._values)
        self._values = [int.from_bytes(temp, byteorder='little', signed=False)
                        for temp in zip(*[iter(data)] * 2)] if data else [0] * 3
        _LOG.debug("Value 16b: Value {}".format(self._values))

    def state(self, index):
        """Return the current value state from broadcast."""
        try:
            return self._values[index - 1]
        except IndexError:
            return None
        return None

    def last_state(self, index):
        """Return the last value state from broadcast."""
        try:
            return self._previous_values[index - 1]
        except IndexError:
            return None
        return None

    def changes(self):
        """Yield the value changes in broadcast data."""
        for index, (current, previous) in enumerate(zip(self._values, self._previous_values), start=1):
            if current != previous:
                yield index, previous, current


class BroadcastValue32b(metaclass=BroadcastMeta):
    """This is a BroadcastValue32b class representing 32-bit data frames."""

    broadcast_types = [
        BroadcastTypes.Value32b
    ]

    def __init__(self, data=None):
        """Initialize BroadcastValue32b class from frame data."""
        self._values = {}
        self._previous_values = {}
        if data:
            self.update(data)

    def update(self, data):
        """Update BroadcastValue32b class from frame data."""
        index = int.from_bytes(data[0:2], byteorder="big", signed=False)
        value = int.from_bytes(data[2:], byteorder="little", signed=False)
        self._previous_values[index] = self._values.get(index, 0)
        self._values[index] = value
        _LOG.debug("Value 32b: Index {} Value {}".format(index + 1, value))

    def state(self, index):
        """Return the current value state from broadcast."""
        try:
            return self._values[index - 1]
        except KeyError:
            _LOG.warning("Value 32b: No value for index: {}".format(index))
            return None
        return None

    def last_state(self, index):
        """Return the last value state from broadcast."""
        try:
            return self._previous_values[index - 1]
        except KeyError:
            _LOG.warning("Value 32b: No value for index: {}".format(index))
            return None
        return None

    def changes(self):
        """Yield the value changes in broadcast data."""
        for index in self._values.keys():
            if self._previous_values[index] != self._values[index]:
                yield index + 1, self._previous_values[index], self._values[index]


class BroadcastHeatingZone(metaclass=BroadcastMeta):
    """This is a BroadcastHeatingZone class representing heating zone information."""

    broadcast_types = [
        BroadcastTypes.HeatingZone1,
        BroadcastTypes.HeatingZone2,
        BroadcastTypes.HeatingZone3,
        BroadcastTypes.HeatingZone4,
        BroadcastTypes.HeatingZone5,
        BroadcastTypes.HeatingZone6,
        BroadcastTypes.HeatingZone7,
        BroadcastTypes.HeatingZone8,
        BroadcastTypes.HeatingZone9,
        BroadcastTypes.HeatingZone10,
        BroadcastTypes.HeatingZone11,
        BroadcastTypes.HeatingZone12,
        BroadcastTypes.HeatingZone13,
        BroadcastTypes.HeatingZone14,
        BroadcastTypes.HeatingZone15,
        BroadcastTypes.HeatingZone16,

    ]

    def __init__(self, data=None):
        """Initialize BroadcastHeatingZone class from frame data."""
        self._values = [0] * 7
        self._previous_values = [0] * 7
        if data:
            self.update(data)

    def update(self, data):
        """Update BroadcastHeatingZone class from frame data."""
        self._previous_values = list(self._values)
        # temp measured
        self._values[0] = int.from_bytes(data[:2], byteorder='little', signed=False)
        # temp setpoint
        self._values[1] = int.from_bytes(data[2:4], byteorder='little', signed=False)
        # control mode
        self._values[2] = int(data[4])

        zone_params = int(data[5])
        # active
        self._values[3] = bool(zone_params & 0x01)
        # heating
        self._values[4] = bool(zone_params & 0x02)
        # day_mode
        self._values[5] = bool(zone_params & 0x04)
        # mode
        self._values[6] = int(zone_params & 0x70)
        _LOG.debug("Heating Zone Update: {}".format(self._values))

    def state(self, index):
        """Return the current value state from broadcast."""
        try:
            return self._values[index - 1]
        except IndexError:
            return None
        return None

    def last_state(self, index):
        """Return the last value state from broadcast."""
        try:
            return self._previous_values[index - 1]
        except IndexError:
            return None
        return None

    def changes(self):
        """Yield the value changes in broadcast data."""
        for index, (current, previous) in enumerate(zip(self._values, self._previous_values), start=1):
            if current != previous:
                yield index, previous, current


class BroadcastDateTime(metaclass=BroadcastMeta):
    """This is BroadcastDateTime representing date/time information."""

    broadcast_types = [
        BroadcastTypes.DateTime
    ]

    def __init__(self, data=None):
        """Initialize BroadcastDateTime class from frame data."""
        self._values = [None] * 7
        self._previous_values = [None] * 7

        if data is not None:
            self.update(data)

    def update(self, data):
        """Update BroadcastDateTime class from frame data."""
        self._previous_values = list(self._values)
        # year
        self._values[0] = int(data[0])
        # months
        self._values[1] = int(data[1] & 0x0f)
        # day
        self._values[2] = int(data[2] & 0x1f)
        # weekday
        self._values[3] = int(data[3] & 0x07)
        # daytime
        self._values[4] = bool(data[4] & 0x80)
        # hour
        self._values[5] = int(data[4] & 0x1f)
        # minute
        self._values[6] = int(data[5] & 0x7f)
        _LOG.debug("20{}-{}-{} {}:{} Weekday={} Day={}".format(
            self._values[0], self._values[1], self._values[2],
            self._values[5], self._values[6], self._values[3], self._values[4]))

    def state(self, index):
        """Return the current value state from broadcast."""
        try:
            return self._values[index - 1]
        except IndexError:
            return None
        return None

    def last_state(self, index):
        """Return the last value state from broadcast."""
        try:
            return self._previous_values[index - 1]
        except IndexError:
            return None
        return None

    def changes(self):
        """Yield the value changes in broadcast data."""
        for index, (current, previous) in enumerate(zip(self._values, self._previous_values), start=1):
            if current != previous:
                yield index, previous, current


class BroadcastEvent(metaclass=BroadcastMeta):
    """This is a BroadcastEvent frame representing the Ampio Event frame."""

    broadcast_types = [
        BroadcastTypes.Event
    ]

    def __init__(self, data=None):
        """Initialize BroadcastEvent class from frame data."""
        self._previous_values = [False] * 256
        self._values = [False] * 256
        if data is not None:
            self.update(data)
        pass

    def update(self, data):
        """Update BroadcastEvent class from frame data."""
        index = int(data[0])
        self._values[index] = True
        self._previous_values[index] = False

    def state(self, index):
        """Return the current value state from broadcast."""
        try:
            return self._values[index]
        except IndexError:
            return None
        return None

    def last_state(self, index):
        """Return the last value state from broadcast."""
        try:
            return self._previous_values[index - 1]
        except IndexError:
            return None
        return None

    def changes(self):
        """Yield the value changes in broadcast data."""
        for index, (current, previous) in enumerate(zip(self._values, self._previous_values), start=1):
            if current != previous:
                yield index, previous, current
                self._values[index] = self._previous_values[index] = False
