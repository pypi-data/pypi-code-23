"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from jemu_mem_peripheral import JemuMemPeripheral


class JemuBQ27421(JemuMemPeripheral):
    _COMMAND = "command"
    _TYPE_STRING = "type"
    _PERIPHERAL_ID = "peripheral_id"
    _INTERRUPT = "interrupts"
    _PERIPHERAL_TYPE = "peripheral_type"
    _COMMAND_SET_INTERRUPT = "set_interrupt"

    def __init__(self, jemu_connection, id, peripheral_type, generators):
        JemuMemPeripheral.__init__(self, jemu_connection, id, peripheral_type, generators)

    def _battery_interrupt_json(self):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_SET_INTERRUPT,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def interrupt(self):
        """
        This function activates an interrupt in the bq27421 peripheral.
        On interrupt a 1 ms pulse is sent out over gpout pin.
        """
        self._jemu_connection.send_json(self._battery_interrupt_json())
