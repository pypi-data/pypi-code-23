# -*- coding: utf-8 -*-
"""This is a module implementing the Ampio Module class."""

import io
import yaml
import re
from functools import partial
from collections import defaultdict
from inspect import getmembers, isfunction
import datetime as dt
from pyampio.broadcast import BroadcastCache
from pyampio.broadcast import BroadcastTypes  # noqa
from pyampio import converters
import logging
from voluptuous import Schema, Required, All, Lower, Any, Optional, Coerce, Invalid
from voluptuous.humanize import validate_with_humanized_errors


_LOG = logging.getLogger(__name__)

QUERY_MODULE_DETAILS_TIMEOUT_SECONDS = 2


def conv():
    """Build map of converter names and code functions."""
    conv_map = {}
    for name, code in getmembers(converters):
        if isfunction(code):
            conv_map[name] = code
    return conv_map


converters_map = conv()

converter_list = [o for o in getmembers(converters) if isfunction(o[1])]


class AmpioModule:
    """This is AmpioModule class representing the Ampio Module."""

    def __init__(self, can_id, code, protocol, software_version, part_number, description, attributes):
        """Initialize the :class: pyampio.modules.AmpioModule object.

        Args:
            can_id (int): CAN_ID
            code (int): The module code numer
            protocol (int): Protocol version
            software_version (int): Software version
            part_number (str): Ampio Module P/N
            description (str): Module description
            attributes (dict): Module attributed

        """
        self.can_id = can_id
        self.physical_can_id = can_id
        self.pcb = 0
        self.code = code
        self.protocol = protocol
        self.software_version = software_version
        self.part_number = part_number
        self.description = description
        self.attributes = attributes
        # (attribute, index) -> (broadcast, index, unit) map
        self.map = {}
        self._broadcasts = {}
        self._broadcast_cache = BroadcastCache(self.on_change)
        # TODO: Remove
        self._callbacks = defaultdict(list)
        self._state_update_callbacks = defaultdict(list)
        self._name_parts = [""] * 6
        self._details_flag = 0x00

        self._make_attribute_map()

    def __str__(self):
        """Return the string representation of the module details."""
        can_id = "         {:08X}".format(self.can_id) if self.physical_can_id == self.can_id \
            else "{:08X}/{:08X}".format(self.physical_can_id, self.can_id)
        return "{} {:2}-{:16} {:02} {:45} {:5d} {:2d} {}".format(
            can_id, self.code, self.part_number, self.protocol, self.description,
            self.software_version, self.pcb, self.name)
    __repr__ = __str__

    @property
    def name(self):
        """Return the discovered module name."""
        return ("".join(self._name_parts)).strip()

    @property
    def is_name_complete(self):
        """Return true if module name discovery is completed."""
        return "" not in self._name_parts

    @property
    def is_details_complete(self):
        """Return true if module details discovery is completed."""
        return self._details_flag == 0xff

    def update_pcb_version(self, pcb):
        """Update the pcb version."""
        self.pcb = pcb

    def broadcast_received(self, can_data):
        """Handle the received broadcast frame."""
        self._broadcast_cache.update(can_data[1:])

    def update_name(self, index, data):
        """Handle the frame from the block with module name."""
        self._name_parts[index] = data.decode('cp1250')

    def update_details(self, can_data, update_can_id_callback):
        """Handle the frame with module details."""
        data_id = can_data[1]
        if data_id == 0x00:
            data_h = can_data[2]
            data_l = can_data[3]
            uptime = (can_data[4] << 16) | (can_data[5] << 8) | can_data[6]
            packet_size = can_data[7]
            _LOG.debug("UPDATE DETAILS 0x00: {:08x} data_h={:02x} data_l={:02x} uptime={} packet_size={}".format(
                self.can_id, data_h, data_l, uptime, packet_size))
            self._details_flag |= 0x01

        elif data_id == 0x01:
            zd_counter = (can_data[2] << 16) | (can_data[3] << 8) | can_data[4]
            reset_counter = (can_data[5] << 8) | can_data[6]
            can_errors = can_data[7]
            _LOG.debug("UPDATE DETAILS 0x01: {:08x} zd_counter={:06x} reset_counter={:04x} can_errors={}".format(
                self.can_id, zd_counter, reset_counter, can_errors))
            self._details_flag |= 0x02

        elif data_id == 0x02:
            com_stat = can_data[2]
            rx_errcnt = can_data[3]
            tx_errcnt = can_data[4]
            vdc = can_data[5] / 10
            l_zas = can_data[6]
            temperature = can_data[7]
            _LOG.debug("UPDATE DETAILS 0x02: {:08x} com_stat={} rx_errcnt={} tx_errcnt={} vdc={} l_zas={} temperature={}".format(
                self.can_id, com_stat, rx_errcnt, tx_errcnt, vdc, l_zas, temperature))
            self._details_flag |= 0x04

        elif data_id == 0x03:
            ecan_status = can_data[2]
            conditions_status = can_data[3]
            cpu_load = can_data[4]
            conditions = can_data[5] << 8
            _LOG.debug("UPDATE DETAILS 0x03: {:08x} ecan_status={} conditions_status={} cpu_load={} conditions={}".format(
                self.can_id, ecan_status, conditions_status, cpu_load, conditions))
            self._details_flag |= 0x08

        elif data_id == 0x04:
            time_quartz_errors = (can_data[2] << 16) | (can_data[3] << 8) | can_data[4]
            quarc_counter = (can_data[5] << 8) | can_data[6]
            _LOG.debug("UPDATE DETAILS 0x04: {:08x} time_quartz_errors={:06x} quarc_counter={:04x}".format(
                self.can_id, time_quartz_errors, quarc_counter))
            self._details_flag |= 0x10

        elif data_id == 0x05:
            new_can_id = int.from_bytes(can_data[2:], byteorder='little', signed=False)
            self.physical_can_id = self.can_id
            self.can_id = new_can_id
            update_can_id_callback(self, self.physical_can_id, new_can_id)
            self._details_flag |= 0x20

        elif data_id == 0x06:
            bin_inputs = can_data[2]
            bin_outputs = can_data[3]
            inputs = can_data[4]
            outputs = can_data[5]
            flags = can_data[6]
            line_flags = can_data[7]
            _LOG.debug(
                "UPDATE DETAILS 0x06: {:08x} bin_inputs={} bin_outputs={} inputs={} outputs={} flags={} line_flags={}".format(
                    self.can_id, bin_inputs, bin_outputs, inputs, outputs, flags, line_flags))
            self._details_flag |= 0x40
        elif data_id == 0x07:
            onewires = can_data[2]
            sub_procs = can_data[3]
            sub_type = can_data[4]
            mask = can_data[5]
            _LOG.debug("UPDATE DETAILS 0x07: {:08x} onewires={} sub_cpus={} sub_type={} mask={}".format(
                self.can_id, onewires, sub_procs, sub_type, mask))
            self._details_flag |= 0x80

    def state_changed(self, attribute, index):
        """Fire the state changed callback."""
        callbacks = self._state_update_callbacks.get((attribute, index))
        if callbacks:
            for callback in callbacks:
                callback()

    def register_state_changed_callback(self, attribute, index, callback):
        """Register calback for attribute state change."""
        self._state_update_callbacks[(attribute, index)].append(callback)
        return

    # TODO: Remove
    def update_listeners(self, attribute, index, old_value, new_value, unit=""):
        """Fire the callback for attribute change listeners."""
        callbacks = self._callbacks.get((attribute, index))
        if callbacks:
            for callback in callbacks:
                callback(self.can_id, attribute, index, old_value, new_value, unit)

    def add_listener(self, attribute, index, callback):
        """Add the callback for attribute value change event."""
        _LOG.debug("MAC: {} {} {} callback added".format(self.can_id, attribute, index))
        self._callbacks[(attribute, index)].append(callback)
        return
        # TODO: check if callback is callable
        # if attribute is None:
        #     attributes = self.attributes
        # else:
        #     attributes = {attribute: self.attributes.get(attribute, 0)}
        # for attribute, idx in attributes.items():
        #     if index is None:
        #         indices = range(1, idx + 1)
        #     else:
        #         indices = [index]
        #     for idx in indices:
        #         _LOG.debug("MAC: {} {} {} callback added".format(self.can_id, attribute, idx))
        #         self._callbacks[(attribute, idx)].append(callback)

    def remove_listener(self, attribute, index, callback):
        """Remove the callback."""
        callbacks = self._callbacks.get((attribute, index))
        if callbacks:
            try:
                callbacks.remove(callback)
            except ValueError:
                pass

    def on_change(self, broadcast_type, data):
        """Handle the on change event when attribute has changed."""
        # TODO: use map
        _LOG.debug("ON CHANGE: {:08x} {}: {}".format(self.can_id, broadcast_type, data))
        details = self.attributes.get(broadcast_type.value)
        if details:
            # [{'base': 1, 'name': 'temperature', 'max': 1, 'unit': 'C', 'converter': convert_temperature, 'min': 1}]
            for properties in details:
                name = properties['name']
                base = properties['base']
                max_index = properties['max']
                min_index = properties['min']
                unit = properties['unit']
                converter = properties['converter']
                index, old_value, new_value = data
                converted_index = index - min_index + base
                if min_index <= index <= max_index:
                    if converter is not None:
                        old_value = converter(old_value)
                        new_value = converter(new_value)
                    _LOG.debug("Changed {}({}) {}{}->{}{}".format(name, converted_index, old_value, unit, new_value, unit))
                    # remove
                    self.update_listeners(name, converted_index, old_value=old_value, new_value=new_value, unit=unit)
                    self.state_changed(attribute=name, index=converted_index)

    def get_attributes(self):
        """Generate the attribute names for module."""
        for _, attributes in self.attributes.items():
            for attribute_detail in attributes:
                name = attribute_detail['name']
                base = attribute_detail['base']
                min_broadcast_index = attribute_detail['min']
                max_broadcast_index = attribute_detail['max']
                unit = attribute_detail['unit']
                # TODO: simplify
                for index in range(min_broadcast_index, max_broadcast_index + 1):
                    conv_index = index - min_broadcast_index + base
                    yield name, conv_index, unit

    def _make_attribute_map(self):
        for broadcast_type, broadcast_details in self.attributes.items():
            for broadcast_detail in broadcast_details:
                attribute = broadcast_detail['name']
                base = broadcast_detail['base']
                min_broadcast_index = broadcast_detail['min']
                max_broadcast_index = broadcast_detail['max']
                unit = broadcast_detail['unit']
                converter = broadcast_detail['converter']
                for index in range(min_broadcast_index, max_broadcast_index + 1):
                    absolute_index = index - min_broadcast_index + base
                    self.map[(attribute, absolute_index)] = (BroadcastTypes(broadcast_type), index, unit, converter)

    def get_state(self, attribute, index):
        """Return the item state."""
        broadcast_type, index, unit, converter = self.map.get((attribute, index), (None, None, None, None))
        if broadcast_type is not None:
            value = self._broadcast_cache.get_value(broadcast_type, index)
            if value is not None:
                value = converter(value)
            return value
        else:
            return None

    def get_last_state(self, attribute, index):
        """Return the item last state."""
        broadcast_type, index, unit, converter = self.map.get((attribute, index), (None, None, None, None))
        if broadcast_type is not None:
            value = self._broadcast_cache.get_last_value(broadcast_type, index)
            if value is not None:
                value = converter(value)
            return value
        else:
            return None

    def get_measurement_unit(self, attribute, index):
        """Return measurement unit."""
        _, _, unit, _ = self.map.get((attribute, index), (None, None, None, None))
        return unit


def load_yaml(file_path):
    """Load YAML file from full file path and return dict."""
    dictionary = {}
    with io.open(file_path, 'r', encoding="utf-8") as yamlfile:
        try:
            dictionary = yaml.load(yamlfile)
        except yaml.YAMLError:
            raise
    return dictionary


module_data = load_yaml(__file__[:-2] + "yaml")


def validate_converter(value):
    """Validate the converter function name."""
    if value in converters_map or value is None:
        return value
    else:
        raise Invalid("Unknown converter function: '{}' type: '{}'".format(value, type(value)))


def update_converter_if_none(value):
    """Make a default converter to transparently pass the value without conversion."""
    conv_func_name = value.get('converter')
    if conv_func_name:
        value['converter'] = converters_map[conv_func_name]
    else:
        value['converter'] = converters_map['convert_unchanged']

    return value


def validate_broadcast(value):
    """Validate if broadcast name is known in module.yaml file."""
    new_value = {}
    for broadcast_name, details in value.items():
        try:
            broadcast_value = eval("BroadcastTypes." + broadcast_name).value
        except AttributeError:
            raise Invalid("Unknown Broadcast Name: {}".format(broadcast_name))
        new_value[broadcast_value] = details
    return new_value


BROADCAST_SCHEMA = All(Schema({
    Required('name'): Coerce(str),
    Required('base'): Coerce(int),
    Required('min'): Coerce(int),
    Required('max'): Coerce(int),
    Optional('unit', default=""): Coerce(str),
    Required('converter', default=None): validate_converter,
}), update_converter_if_none)

ATTRIBUTE_SCHEMA = All(Schema({
    str: [BROADCAST_SCHEMA]
}), validate_broadcast)

MODULE_INFO_SCHEMA = All(Schema({
    Required('code'): Coerce(int),
    Required('protocol'): All(Lower, Any('any', Coerce(int))),
    Required('software_versions'): All([Coerce(int)]),
    Required('description'): Coerce(str),
    Required('attributes'): ATTRIBUTE_SCHEMA,
}))


SCHEMA = All(Schema({
    str: MODULE_INFO_SCHEMA,
}))

validate_with_humanized_errors(data=module_data, schema=SCHEMA)
module_info = SCHEMA(module_data)


class ModuleFactory:
    """This is a ModuleFactory class to create specific module class based on discovered data."""

    factories = {}

    @staticmethod
    def create_module(can_id, code, protocol, software_version):
        """Create module object based on proivded data.

        Args:
            can_id (int): CAN ID
            code (int): Module Code Number
            protocol (int): Module CAN protocol version
            software_version (int): Module software version

        """
        max_match = 0
        matched_pn = None
        for part_number, details in module_info.items():
            match = 0
            if details['code'] == code:
                match += 1
            if (details['protocol'] in [protocol, "any"]) and match == 1:
                match += 1
            if software_version in details['software_versions'] and match == 2:
                match += 1
            if match > max_match:
                max_match = match
                matched_pn = part_number
            if max_match == 3:
                break

        if matched_pn is None:
            return None
        info = module_info.get(matched_pn)
        attributes = info.get('attributes')
        description = info.get("description")

        return AmpioModule(can_id=can_id, code=code, protocol=protocol, software_version=software_version,
                           part_number=matched_pn, description=description, attributes=attributes)


class AmpioModules:
    """This is a ModuleManager class implementation."""

    def __init__(self):
        """Initialize the :class: pyampio.modules.ModuleManager object."""
        self._modules = {}
        self._can_id_map_to_module = {}

    def __len__(self):
        """Return the number of modules."""
        return len(self._modules)

    def __iter__(self):
        """Iterate over module dictionary."""
        return iter(dict(self._modules).items())

    def add_module(self, can_id, can_data):
        """Add new module.

        Args:
            can_id (int): CAN ID
            can_data (bytearray): CAN frame data

        """
        sw_version = int((can_data[2] << 8) | can_data[3])
        pcb = int(can_data[4])
        code = int(can_data[1])
        protocol_version = int(can_data[5])
        mod = ModuleFactory.create_module(can_id=can_id, code=code, protocol=protocol_version, software_version=sw_version)
        try:
            mod.update_pcb_version(pcb)
        except AttributeError:
            _LOG.error("MODULE NOT IMPLEMENTED: {:08x} code={} {}".format(can_id, code, can_data))
            return

        self._modules[can_id] = mod
        self._can_id_map_to_module[can_id] = mod

    def update_name(self, can_id, can_data):
        """Update the module name.

        Args:
            can_id (int): CAN ID
            can_data (bytearray): CAN frame data

        """
        if can_data[0] == 0x0f and len(can_data) == 8:
            index = int(can_data[1])
            mod = self._modules.get(can_id)
            if mod is not None:
                mod.update_name(index, can_data[2:])
            else:
                _LOG.warning("Update name to unknown module: {:08x}".format(can_id))

    def update_details(self, can_id, can_data):
        """Update the module details.

        Args:
            can_id (int): CAN ID
            can_data (bytearray): CAN frame data

        """
        mod = self._modules.get(can_id)
        if mod is not None:
            mod.update_details(can_data, self.on_can_id_update)
        else:
            _LOG.warning("Update details to unknown module: {:08x}".format(can_id))

    def is_name_updated(self, can_id):
        """Return true if module name is updated else yield."""
        mod = self._modules.get(can_id)
        if mod:
            while not mod.is_name_complete:
                yield
            return True
        else:
            _LOG.warning("No module id {}".format(can_id))

    def is_details_updated(self, can_id):
        """Return true if module details are updated else yield."""
        start_time = dt.datetime.now()
        mod = self._modules.get(can_id)
        if mod:
            while not mod.is_details_complete and \
                    (dt.datetime.now() - start_time).seconds < QUERY_MODULE_DETAILS_TIMEOUT_SECONDS:
                yield
        if (dt.datetime.now() - start_time).seconds >= QUERY_MODULE_DETAILS_TIMEOUT_SECONDS:
            _LOG.warning("Query took more than {} seconds: {}".format(
                QUERY_MODULE_DETAILS_TIMEOUT_SECONDS, mod))
        return True

    def is_attribute_names_updated(self, can_id):
        """Return true if attribute name are updated else yield."""
        # TODO: Implementation needed
        while True:
            yield

    def on_can_id_update(self, mod, can_id, new_can_id):
        """Handle the CAN_ID update (i.e. physical -> logical)."""
        if can_id != new_can_id:
            self._can_id_map_to_module[new_can_id] = mod

    def broadcast_received(self, can_id, can_data):
        """Handle the received broadcast."""
        mod = self.get_module(can_id)
        if mod is None:
            _LOG.debug("Update for unknown module can_id={:08x}".format(can_id))
            return
        mod.broadcast_received(can_data)

    def add_on_value_changed_callback(self, can_id, attribute, index, callback):
        # TODO: Remove
        """Add the on value changed callback."""
        mod = self.get_module(can_id)
        if mod:
            for (attrib, idx, unit) in mod.get_attributes():
                if attribute is not None:
                    if attribute != attrib:
                        continue
                if index is not None:
                    if index != idx:
                        continue
                mod.add_listener(attrib, idx, partial(callback, self))
                _LOG.debug("On value changed callback added {} {} {}".format(can_id, attrib, idx))
        else:
            _LOG.warning("Module not known: {:08x}".format(can_id))

    def register_on_value_changed_callback(self, can_id, attribute, index, callback):
        """Register on value change_callback."""
        mod = self.get_module(can_id)
        attribute_re = re.compile(attribute)
        if mod:
            for (attrib, idx, unit) in mod.get_attributes():
                if attribute is not None:
                    if attribute_re.match(attrib) is None:
                        continue
                if index is not None:
                    if index != idx:
                        continue
                mod.register_state_changed_callback(attrib, idx, callback)
                _LOG.debug("On value changed callback added {} {} {}".format(can_id, attrib, idx))
        else:
            _LOG.warning("Module not known: {:08x}".format(can_id))

    @property
    def modules(self):
        """Return the module dictionary."""
        return self._modules

    def get_module(self, can_id):
        """Get the module from CAN ID."""
        return self._can_id_map_to_module.get(can_id)

    def get_attributes(self, can_id, attribute):
        """Generate the module attributes."""
        mod = self.get_module(can_id)
        if mod:
            for (attr, index, _) in mod.get_attributes():
                if attr == attribute:
                    yield attribute, index

    def get_state(self, can_id, attribute, index):
        """Return item state."""
        mod = self.get_module(can_id)
        if mod:
            return mod.get_state(attribute, index)
        else:
            return None

    def get_last_state(self, can_id, attribute, index):
        """Return item last state."""
        mod = self.get_module(can_id)
        if mod:
            return mod.get_last_state(attribute, index)
        else:
            return None

    def get_measurement_unit(self, can_id, attribute, index):
        """Return measurement unit."""
        mod = self.get_module(can_id)
        if mod:
            return mod.get_measurement_unit(attribute, index)
        else:
            return None

    def get_module_name(self, can_id):
        """Return module name."""
        mod = self.get_module(can_id)
        if mod:
            return mod.name
        else:
            return None

    def get_module_part_number(self, can_id):
        """Return module name."""
        mod = self.get_module(can_id)
        if mod:
            return mod.part_number
        else:
            return None
