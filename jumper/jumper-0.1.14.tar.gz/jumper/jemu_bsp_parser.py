"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
import os
import json
from .jemu_button import JemuButton
from .jemu_mem_peripheral import JemuMemPeripheral
from .jemu_bma280 import JemuBMA280
from .jemu_sudo import JemuSudo
from .jemu_bq24160 import JemuBQ24160
from .jemu_bq27421 import JemuBQ27421


class JemuBspParser:
    _EXTERNAL_PERIPHERAL = "External"
    _NRF52_PERIPHERAL = "nrf52832"

    _bsp_json_path = None

    def __init__(self, bsp_json_path):
        self._bsp_json_path = bsp_json_path

    def get_components(self, jemu_connection):
        components_list = []
        mcu_list = []

        if not os.path.isfile(self._bsp_json_path):
            raise Exception(self._bsp_json_path + ' is not found')
        elif not os.access(self._bsp_json_path, os.R_OK):
            raise Exception(self._bsp_json_path + ' is not readable')
        else:
            with open(self._bsp_json_path) as bsp_json_file:
                bsp_json = json.load(bsp_json_file)

                for component in bsp_json["components"]:
                    component_id = component["id"]
                    component_obj = None

                    if ("config" in component) and ("generators" in component["config"]):
                        generators = component["config"]["generators"]
                    else:
                        generators = None

                    if 'class' in component:
                        if component["class"] == "Button":
                            component_obj = JemuButton(jemu_connection, component_id)

                        if component["class"] == "BME280":
                            component_obj = JemuMemPeripheral(jemu_connection, component_id, self._EXTERNAL_PERIPHERAL, generators)

                        if component["class"] == "BQ24160":
                            component_obj = JemuBQ24160(jemu_connection, component_id, self._EXTERNAL_PERIPHERAL, generators)

                        if component["class"] == "BQ27421":
                            component_obj = JemuBQ27421(jemu_connection, component_id, self._EXTERNAL_PERIPHERAL, generators)

                        if component["class"] == "BMA280":
                            component_obj = JemuBMA280(jemu_connection, component_id, self._EXTERNAL_PERIPHERAL, generators)
                            components_list.append({"obj": component_obj, "name": component["name"]})

                        if component_obj is not None:
                            components_list.append({"obj": component_obj, "name": component["name"]})

                        if component["class"] == "MCU":
                            mcu_list.append(component["name"])
                            peripheral_obj = JemuSudo(jemu_connection, 39, "nrf52832")
                            components_list.append({"obj": peripheral_obj, "name": "SUDO"})
                    
            return components_list
