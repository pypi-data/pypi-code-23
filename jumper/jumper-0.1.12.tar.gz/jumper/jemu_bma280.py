from jemu_mem_peripheral import JemuMemPeripheral


class JemuBMA280(JemuMemPeripheral):
    _LEVEL_HIGH = 1
    _LEVEL_LOW = 0
    _RESPONSE_TIMEOUT = 10

    _TYPE_STRING = "type"
    _VALUE = "value"
    _PERIPHERAL_ID = "peripheral_id"
    _PERIPHERAL_TYPE = "peripheral_type"
    _INTERRUPT = "interrupts"
    _COMMAND = "command"
    _COMMAND_SET_INTERRUPT = "set_interrupt"
    _COMMAND_UNSET_INTERRUPT = "unset_interrupt"
    _COMMAND_RESET_INTERRUPT = "reset_interrupts"

    class Interrupts(object):
        SLOPE_X = "slope_x"
        SLOPE_Y = "slope_y"
        SLOPE_Z = "slope_z"
        LOW_G = "low_g"
        HIGH_G_X = "high_g_x"
        HIGH_G_Y = "high_g_y"
        HIGH_G_Z = "high_g_z"
        DOUBLE_TAP_X = "double_tap_x"
        DOUBLE_TAP_Y = "double_tap_y"
        DOUBLE_TAP_Z = "double_tap_z"
        SINGLE_TAP_X = "single_tap_x"
        SINGLE_TAP_Y = "single_tap_y"
        SINGLE_TAP_Z = "single_tap_z"
        ORIENT_XY = "orient_xy"
        ORIENT_Z = "orient_z"
        FLAT = "flat"
        FIFO_FULL = "fifo_full"
        FIFO_WATERMARK = "fifo_watermark"
        NEW_DATA = "new_data"

    def __init__(self, jemu_connection, id, peripheral_type, generators):
        JemuMemPeripheral.__init__(self, jemu_connection, id, peripheral_type, generators)

    def _set_interrupt_json(self, interrupt):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._INTERRUPT: interrupt,
            self._COMMAND: self._COMMAND_SET_INTERRUPT,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def _unset_interrupt_json(self, interrupt):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_UNSET_INTERRUPT,
            self._INTERRUPT: interrupt,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def _reset_interrupt_json(self, interrupt):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_RESET_INTERRUPT,
            self._INTERRUPT: interrupt,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def set_interrupt(self, interrupt):
        self._jemu_connection.send_json(self._set_interrupt_json(interrupt))

    def unset_interrupt(self, interrupt):
        self._jemu_connection.send_json(self._unset_interrupt_json(interrupt))

    def reset_interrupts(self):
        self._jemu_connection.send_json(self._reset_interrupt_json('reset_interrupt'))
