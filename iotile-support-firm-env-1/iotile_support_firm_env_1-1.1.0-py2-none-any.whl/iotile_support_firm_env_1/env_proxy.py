from iotile.core.hw.proxy.proxy import TileBusProxyObject
from iotile.core.hw.exceptions import *
from iotile.core.utilities.console import ProgressBar
import struct
from iotile.core.utilities.intelhex import IntelHex
from time import sleep
import uuid
import datetime
from typedargs.annotate import annotated, param, return_type, context, docannotate
from iotile.core.utilities.typedargs import iprint
from iotile.core.utilities import typedargs
from itertools import product
from iotile.core.exceptions import *
import math
import binascii

@context("ENVProxy")
class ENVProxy (TileBusProxyObject):
    """
    Provide access to ENV tile functionality


    :param stream: CMDStream instance that can communicate with this tile
    :param addr: Local tilebus address of this tile
    """

    @classmethod
    def ModuleName(cls):
        return 'envbsl'

    def __init__(self, stream, addr):
        super(ENVProxy, self).__init__(stream, addr)

    @annotated
    def poll_data(self):
        """Tell the BME280 to poll data.

        """
        error, = self.rpc(0x80, 0x00, result_format="L")
        if error != 0:
            raise HardwareError("Error polling", code=error)

    @return_type("float")
    def get_temperature(self):
        """Acquire temperature without polling. Returns in C

        :rtype: float
        """
        reading, = self.rpc(0x80, 0x01, result_format="l")
        return float(reading)/100.

    @return_type("float")
    def get_pressure(self):
        """Acquire pressure without polling. Return in hPa

        :param: channel: The channel that should be fetched
        :rtype: float
        """
        reading, = self.rpc(0x80, 0x02, result_format="L")
        return float(reading)/100.

    @return_type("float")
    def get_humidity(self):
        """Acquire humidity without polling. Return in RH%

        :rtype: float
        """
        reading, = self.rpc(0x80, 0x03, result_format="L")
        return float(reading)/1024.

    @return_type("string")
    def sample_temperature(self):
        """Poll BME and then acquire temperature. String formatted result.

        :rtype: string
        """
        self.poll_data()
        reading, = self.rpc(0x80, 0x01, result_format="l")
        return "%0.2f C" % (float(reading)/100.)

    @return_type("string")
    def sample_pressure(self):
        """Poll BME and then acquire pressure. String formatted result.

        :rtype: string
        """
        self.poll_data()
        reading, = self.rpc(0x80, 0x02, result_format="L")
        return "%0.4f hPa" % (float(reading)/100.)

    @return_type("string")
    def sample_humidity(self):
        """Poll BME and then acquire humidity. String formatted result.

        :rtype: string
        """
        self.poll_data()
        reading, = self.rpc(0x80, 0x03, result_format="L")
        return "%0.4f RH" % (reading/1024.)

    @return_type("integer", formatter="hex")
    @param("register", "integer", desc="register to read")
    def get_reg(self, register):
        """Get a register byte value in the BME280 chip. 

        :param: register: The register.
        :rtype: string
        """
        reading, = self.rpc(0x80, 0x04, register, arg_format="i",result_format="B")
        return reading

    @docannotate
    def get_calibration(self):
        """Get the current calibration information saved in the tile.

        Returns:
            basic_dict: The calibration information
        """

        temp_off, hum_off, press_off = self.rpc(0x80, 0x42, result_format="LLL")

        return {
            "temp_offset": temp_off,
            "humidity_offset": hum_off,
            "pressure_offset": press_off
        }

    @docannotate
    def set_calibration(self, temp_off, hum_off, pressure_off):
        """Set the tile calibration information.

        Args:
            temp_off (int): The temperature offset.
            hum_off (int): The humidity offset.
            pressure_off (int): The pressure offset.
            
        """


        err, = self.rpc(0x80, 0x40, temp_off, hum_off, pressure_off, arg_format="lll", result_format="L")
        if err:
            raise HardwareError("Error setting calibration", error_code=err)

    @docannotate
    def persist_calibration(self):
        """Save the current calibration persistently.

        This function also stores a unique guid and the current timestamp
        with the data so that we always know when the calibration was performed.

        Returns:
            str: The guid that was saved with the calibration data.
        """

        guid = uuid.uuid4()
        now = datetime.datetime.utcnow()
        ref = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)

        secs = (now - ref).total_seconds()

        err, = self.rpc(0x80, 0x41, secs, guid.bytes_le, arg_format="L16s", result_format="L")
        if err:
            raise HardwareError("Error persisting calibration", error_code=err)

        return str(guid)

    @docannotate
    def calibration_info(self):
        """Get the calibration date and serial number of the last calibration.

        Returns:
            basic_dict: a dictionary with calibration_time, serial_number 
                members.
        """

        timestamp, guid_bytes = self.rpc(0x80, 0x43, result_format="L16s")

        guid = uuid.UUID(bytes_le=guid_bytes)
        ref = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)
        delta = datetime.timedelta(seconds=timestamp)

        calib_date = ref + delta

        if delta == 0:
            return None

        return {
            'calibration_time': calib_date,
            'serial_number': guid
        }