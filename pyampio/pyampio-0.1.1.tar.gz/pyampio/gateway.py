"""This is a main AmpioGateway implementation module."""

import asyncio
import serial
import logging
from serial_asyncio import create_serial_connection
from enum import Enum, IntEnum
from pyampio.can import AmpioCanProtocol, Type
from pyampio.modules import AmpioModules


_LOG = logging.getLogger(__name__)


class GatewayState(Enum):
    """This is an enum class for Gateway State."""

    INIT = 0
    QUERY_MODULES = 4
    QUERY_MODULE_NAME = 5
    QUERY_MODULE_DETAILS = 6
    QUERY_MODULE_ITEM_NAMES = 7
    READY = 8


GATEWAY_CAN_ID = 0xdeadbeef

# Timeout for modules query after moving to next stage
QUERY_MODULES_TIMEOUT = 2


class ModuleFunction(IntEnum):
    """This is an enmu class for Module Functions."""

    Discovery = 0xff
    QueryNames = 0x01
    QueryDetails = 0x03
    QueryItemNames = 0x08


class AmpioGateway:
    """This is a AmpioGateway class handling the connection USB<->Ampio CAN bus."""

    def __init__(self, port=None, loop=None, no_query_module_details=False):
        """Initialize the :class: pyampio.AmpioGateway object.

        Args:
            port (str): The USB port path i.e. /dev/usb1
            loop: Asynction Event Loop

        """
        self._port = port
        self._loop = loop
        self._no_query_module_details = no_query_module_details

        self._modules = AmpioModules()
        self._on_discovered_callbacks = []

        self._is_relevant = lambda can_id: True
        self._reset_serial(port)
        self._protocol_coro = create_serial_connection(
            loop, lambda: AmpioCanProtocol(
                on_connected=self.on_connected,
                on_can_broadcast_received=self.on_can_broadcast_received,
                on_can_data_received=self.on_can_data_received,
                is_relevant=self._is_relevant
            ), port, baudrate=115200
        )
        self.protocol = None
        self._state = GatewayState.INIT
        loop.create_task(self._protocol_coro)

    def _reset_serial(self, port):
        ser = serial.Serial(port)
        ser.close()

    @property
    def state(self):
        """Return the current object state.

        Returns:
            GatewayState: The current gateway state.

        """
        return self._state

    @property
    def is_ready(self):
        """Return True if gateway is connected and Ready."""
        return self._state == GatewayState.READY

    @property
    def is_connected(self):
        """Return True if gateway is connected to serial port."""
        return self.protocol is not None

    @state.setter
    def state(self, value):
        """Set the object state."""
        _LOG.info("State change {}->{}".format(self._state.name, value.name))
        self._state = value

    def add_on_discovered_callback(self, callback):
        """Add the callback for On Discovered Event."""
        if callback not in self._on_discovered_callbacks:
            self._on_discovered_callbacks.append(callback)

    def remove_on_discovered_callback(self, callback):
        """Remove the callback for On Discovered Event."""
        try:
            self._on_discovered_callbacks.remove(callback)
        except ValueError:
            pass

    @asyncio.coroutine
    def on_discovered(self):
        """Fire the callback when all modules are fully discovered."""
        for callback in self._on_discovered_callbacks:
            yield from callback(modules=self._modules)

    @asyncio.coroutine
    def on_connected(self, protocol):
        """Call on gateway connected event."""
        _LOG.debug("Connected")
        self.protocol = protocol
        self.state = GatewayState.QUERY_MODULES
        # send the module discovery
        self.protocol.send_module_command(ModuleFunction.Discovery, GATEWAY_CAN_ID)
        self._loop.call_later(QUERY_MODULES_TIMEOUT, self.discovery_finished)

    def discovery_finished(self):
        """Schedule the Query Module Name phase when all module discovered."""
        module_quantity = len(self._modules)
        _LOG.info("Total number of modules discovered: {}".format(module_quantity))

        self.state = GatewayState.QUERY_MODULE_NAME
        self._loop.create_task(self.query_module_names())

    @asyncio.coroutine
    def query_module_names(self):
        """Run the Query Module Names phase."""
        for can_id, mod in self._modules:
            self.protocol.send_module_command(ModuleFunction.QueryNames, GATEWAY_CAN_ID, can_id)
            yield from self._modules.is_name_updated(can_id)

        _LOG.info("Module names discovered")
        if self._no_query_module_details:
            self.state = GatewayState.READY
            self._loop.create_task(self.on_discovered())
        else:
            self.state = GatewayState.QUERY_MODULE_DETAILS
            self._loop.create_task(self.query_module_details())

    @asyncio.coroutine
    def query_module_details(self):
        """Run the module details discovery phase."""
        for can_id, mod in self._modules:
            self.protocol.send_module_command(ModuleFunction.QueryDetails, GATEWAY_CAN_ID, can_id)
            yield from self._modules.is_details_updated(can_id)
        for can_id, mod in self._modules:
            _LOG.info(mod)
        _LOG.info("Module details discovered")
        self.state = GatewayState.READY
        self._loop.create_task(self.on_discovered())

        # TODO(klstanie): Add the attribute names discovery logic
        # Attribute names discovery not implemented yet
        # self.state = GatewayState.ATTRIBUTE_NAMES_DISCOVERY
        # self._loop.create_task(self.attribute_names_discovery())

    @asyncio.coroutine
    def query(self):
        """Run the attribute names discovery phase."""
        for can_id, mod in dict(self._modules.modules).items():
            self.protocol.send_module_command(ModuleFunction.QueryItemNames, GATEWAY_CAN_ID, can_id)
            yield from self._modules.is_attribute_names_updated(can_id)
        for can_id, mod in self._modules.modules.items():
            _LOG.info(mod)
        _LOG.info("Attribute names discovered")

    @asyncio.coroutine
    def close(self):
        """Close the Gateway Serial Connection."""
        self._loop.call_later(1, self.protocol.transport.close)

    @asyncio.coroutine
    def on_can_broadcast_received(self, can_id, can_data):
        """Handle the broadcast frame."""
        if self.state == GatewayState.READY:
            can_data_str = " ".join(["{:02x}".format(c) for c in can_data])
            _LOG.debug("CAN IN: id={:08x} data=[{}]".format(can_id, can_data_str))
            self._modules.broadcast_received(can_id, can_data)

    @asyncio.coroutine
    def on_can_data_received(self, can_id, can_data):
        """Handle the data frame."""
        if self.state == GatewayState.QUERY_MODULES:
            self._modules.add_module(can_id, can_data)
        elif self.state == GatewayState.QUERY_MODULE_NAME:
            self._modules.update_name(can_id, can_data)
        elif self.state == GatewayState.QUERY_MODULE_DETAILS:
            self._modules.update_details(can_id, can_data)

    def register_on_value_change_callback(self, can_id, attribute, index, callback):
        """Register the value changed callback."""
        self._modules.register_on_value_changed_callback(can_id, attribute, index, callback)

    def get_item_state(self, can_id, attribute, index):
        """Return the item state from ampio module."""
        return self._modules.get_state(can_id, attribute, index)

    def get_item_last_state(self, can_id, attribute, index):
        """Return the item last state from ampio module."""
        return self._modules.get_last_state(can_id, attribute, index)

    def get_item_measurement_unit(self, can_id, attribute, index):
        """Return the item measurement unit."""
        return self._modules.get_measurement_unit(can_id, attribute, index)

    def get_module_name(self, can_id):
        """Return Ampio module name."""
        return self._modules.get_module_name(can_id)

    def get_module_part_number(self, can_id):
        """Return Ampio module part number."""
        return self._modules.get_module_part_number(can_id)

    @asyncio.coroutine
    def send_value_with_mask(self, can_id, mask, value):
        """Send value to module using item mask.

        Params:
            can_id (int): Module CAN ID
            mask(int): 2 byte item mask
            value (int): Single byte value

        """
        if self.protocol:
            value = value.to_bytes(1, byteorder='big')
            mask &= 0xffff
            mask = mask.to_bytes(2, byteorder='big')
            self.protocol.send_frame(Type.SEND_VALUE_WITH_MASK, can_id, value + mask)
        pass

    @asyncio.coroutine
    def send_value_with_index(self, can_id, index, value):
        """Send value to module using item index.

        Params:
            can_id (int): Module CAN ID
            index (int): 1-based item index
            value (int): Single byte value

        """
        if self.protocol:
            value = value.to_bytes(1, byteorder='big')
            index -= 1
            index &= 0xff
            index = index.to_bytes(1, byteorder='big')
            self.protocol.send_frame(Type.SEND_VALUE_WITH_INDEX, can_id.to_bytes(4, byteorder='big'), value + index)

    @asyncio.coroutine
    def send_rgb_values(self, can_id, red, green, blue):
        """Send rgb color values to module."""
        if self.protocol:
            can_id_bytes = can_id.to_bytes(4, byteorder='big')
            values = red << 16 | green << 8 | blue
            values = values.to_bytes(3, byteorder='big')
            data = bytearray(can_id_bytes + b'\x14' + values)
            self.protocol.send_can_frame(GATEWAY_CAN_ID, data)

    @asyncio.coroutine
    def send_white_value(self, can_id, white):
        """Send white color value to module."""
        if self.protocol:
            can_id_bytes = can_id.to_bytes(4, byteorder='big')
            values = white.to_bytes(1, byteorder='big')
            data = bytearray(can_id_bytes + b'\x15' + values + b'\x03')
            self.protocol.send_can_frame(GATEWAY_CAN_ID, data)

    @asyncio.coroutine
    def send_red_value(self, can_id, white):
        """Send red color value to module."""
        if self.protocol:
            can_id_bytes = can_id.to_bytes(4, byteorder='big')
            values = white.to_bytes(1, byteorder='big')
            data = bytearray(can_id_bytes + b'\x15' + values + b'\x00')
            self.protocol.send_can_frame(GATEWAY_CAN_ID, data)

    @asyncio.coroutine
    def send_green_value(self, can_id, white):
        """Send green color value to module."""
        if self.protocol:
            can_id_bytes = can_id.to_bytes(4, byteorder='big')
            values = white.to_bytes(1, byteorder='big')
            data = bytearray(can_id_bytes + b'\x15' + values + b'\x01')
            self.protocol.send_can_frame(GATEWAY_CAN_ID, data)

    @asyncio.coroutine
    def send_blue_value(self, can_id, white):
        """Send blue color value to module."""
        if self.protocol:
            can_id_bytes = can_id.to_bytes(4, byteorder='big')
            values = white.to_bytes(1, byteorder='big')
            data = bytearray(can_id_bytes + b'\x15' + values + b'\x02')
            self.protocol.send_can_frame(GATEWAY_CAN_ID, data)

    @asyncio.coroutine
    def send_arm_in_mode_0(self, can_id, zone):
        """Send Arm in Mode 0 command to Satel Module."""
        cmd = b'\x1E\x00\x80'  # 0x1E - SATEL, 0x00 - API_SATEL_SUB_CMD (0x00 - CMD PIN from PAR), 0x80 - SATEL CMD

        zone_mask = (0x01 << (zone - 1)) & 0xffffffff

        zone_mask_bytes = zone_mask.to_bytes(4, byteorder='little')
        self.protocol.send_frame(
            Type.SEND_COMPLEX_FUNCTION,
            can_id.to_bytes(4, byteorder='big'), cmd + zone_mask_bytes)

    @asyncio.coroutine
    def send_disarm(self, can_id, zone, code=None):
        """Send Disarm command to Satel Module."""
        cmd = b'\x1E\x00\x84'  # 0x1E - SATEL, 0x00 - API_SATEL_SUB_CMD (0x00 - CMD PIN from PAR), 0x84 - SATEL CMD
        zone_mask = (0x01 << (zone - 1)) & 0xffffffff
        zone_mask_bytes = zone_mask.to_bytes(4, byteorder='little')
        self.protocol.send_frame(
            Type.SEND_COMPLEX_FUNCTION,
            can_id.to_bytes(4, byteorder='big'), cmd + zone_mask_bytes)

    @asyncio.coroutine
    def send_open_cover(self, can_id, index):
        """Send open cover command to module."""
        cmd = b'\x02'
        mask = (0x01 << (index - 1)) & 0xff
        mask_bytes = mask.to_bytes(1, byteorder='little')
        self.protocol.send_frame(
            Type.SEND_VALUE_WITH_MASK,
            can_id.to_bytes(4, byteorder='big'), cmd + mask_bytes)

    @asyncio.coroutine
    def send_close_cover(self, can_id, index):
        """Send close cover command to module."""
        cmd = b'\x01'
        mask = (0x01 << (index - 1)) & 0xff
        mask_bytes = mask.to_bytes(1, byteorder='little')
        self.protocol.send_frame(
            Type.SEND_VALUE_WITH_MASK,
            can_id.to_bytes(4, byteorder='big'), cmd + mask_bytes)

    @asyncio.coroutine
    def send_stop_cover(self, can_id, index):
        """Send stop cover command to module."""
        cmd = b'\x00'
        mask = (0x01 << (index - 1)) & 0xff
        mask_bytes = mask.to_bytes(1, byteorder='little')
        self.protocol.send_frame(
            Type.SEND_VALUE_WITH_MASK,
            can_id.to_bytes(4, byteorder='big'), cmd + mask_bytes)

    @asyncio.coroutine
    def send_set_cover_position(self, can_id, index, position):
        """Sent the command to set the cover position."""
        cmd = b'\x00\x01'
        mask = (0x01 << (index - 1)) & 0xff
        mask_bytes = mask.to_bytes(1, byteorder='little')
        position_bytes = position.to_bytes(1, byteorder='little')
        self.protocol.send_frame(
            Type.SEND_COMPLEX_FUNCTION,
            can_id.to_bytes(4, byteorder='big'), cmd + mask_bytes + position_bytes + b'\x66'  # tilt back prev pos
        )

    @asyncio.coroutine
    def send_set_cover_tilt_position(self, can_id, index, position):
        """Send the command to set the cover tilt position."""
        cmd = b'\x00\x02'
        mask = (0x01 << (index - 1)) & 0xff
        mask_bytes = mask.to_bytes(1, byteorder='little')
        position_bytes = position.to_bytes(1, byteorder='little')
        self.protocol.send_frame(
            Type.SEND_COMPLEX_FUNCTION,
            can_id.to_bytes(4, byteorder='big'), cmd + mask_bytes + position_bytes
        )
