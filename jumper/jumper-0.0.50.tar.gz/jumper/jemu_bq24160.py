"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from jemu_mem_peripheral import JemuMemPeripheral


class JemuBQ24160(JemuMemPeripheral):
    _COMMAND = "command"
    _TYPE_STRING = "type"
    _PERIPHERAL_ID = "peripheral_id"
    _INTERRUPT_TYPE = "interrupt_type"
    _PERIPHERAL_TYPE = "peripheral_type"
    _COMMAND_BATTERY_USB_CHARGE = "battery_charge_usb_event"
    _COMMAND_BATTERY_IN_CHARGE = "battery_charge_in_event"
    _COMMAND_BATTERY_DISCHARGE = "battery_discharge_event"
    _COMMAND_SET_INTERRUPT = "set_interrupt"

    # interrupt types
    TIMER_FAULT_INTERRUPT = "timer_fault_interrupt"
    WATCHDOG_EXPIRATION_INTERRUPT = "watchdog_expiration_interrupt"
    SLEEP_MODE_INTERRUPT = "sleep_mode_interrupt"
    TEMPERATURE_FAULT_INTERRUPT_ = "temperature_fault_interrupt"
    BATTERY_FAULT_INTERRUPT = "battery_fault_interrupt"
    THERMAL_SHUTDOWN_INTERRUPT = "thermal_shutdown_interrupt"
    IN_SUPPLY_INTERRUPT = "in_supply_interrupt"
    USB_SUPPLY_INTERRUPT = "usb_supply_interrupt"

    def __init__(self, jemu_connection, id, peripheral_type, generators):
        JemuMemPeripheral.__init__(self, jemu_connection, id, peripheral_type, generators)
        
    def _charge_json(self, charge_type):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: charge_type,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def _no_charge_json(self):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_BATTERY_DISCHARGE,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def _battery_interrupt_json(self, interrupt):
        return {
            self._TYPE_STRING: self._COMMAND,
            self._PERIPHERAL_ID: self._id,
            self._COMMAND: self._COMMAND_SET_INTERRUPT,
            self._INTERRUPT_TYPE: interrupt,
            self._PERIPHERAL_TYPE: self._peripheral_type
        }

    def charge(self, charge_type):
        """
          :param charge_type: usb ot in
        This function informs the peripheral to start charging.
        During charging, stat and int pins sets to low.
        """
        if charge_type == "usb":
            self._jemu_connection.send_json(self._charge_json(self._COMMAND_BATTERY_USB_CHARGE))
        elif charge_type == "in":
            self._jemu_connection.send_json(self._charge_json(self._COMMAND_BATTERY_IN_CHARGE))
        else:
            raise Exception("BQ24160: charge expect to get 'usb' or 'in' value")

    def charge_completed(self):
        """
        This function informs the peripheral when charging is complete.
        On charging complete, stat and int pins sets to high impedance.
        """
        self._jemu_connection.send_json(self._no_charge_json())

    def discharge(self):
        """
        This function disables charging operation.
        On charging disable, stat and int pins sets to high impedance.
        """
        self._jemu_connection.send_json(self._no_charge_json())

    def interrupt(self, interrupt):
        """
        This function activates an interrupt in the bq24160 peripheral.
        On interrupt a 128 microsecond pulse is sent out over stat and int pins.
        :param interrupt: Interrupt type
        """
        self._jemu_connection.send_json(self._battery_interrupt_json(interrupt))