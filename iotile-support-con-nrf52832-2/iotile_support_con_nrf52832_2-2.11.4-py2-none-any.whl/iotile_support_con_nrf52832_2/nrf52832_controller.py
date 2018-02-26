#nrf52832_controller.py
#Proxy object for controller module based on 

from iotile.core.hw.proxy.proxy import TileBusProxyObject
from iotile.core.hw.proxy.external_proxy import find_proxy_plugin
from typedargs.annotate import param, annotated, return_type, context, docannotate
from typedargs import iprint
from iotile.core.hw.exceptions import *
from iotile.core.exceptions import *
from iotile.core.utilities import typedargs


@context("NRF52832Controller")
class NRF52832Controller (TileBusProxyObject):
    def __init__(self, stream, addr):
        super(NRF52832Controller, self).__init__(stream, addr)
        self.name = 'NRF52832Controller'
        self._sensorgraph = find_proxy_plugin('iotile_standard_library/lib_controller', 'SensorGraphPlugin')(self)
        self._testinterface = find_proxy_plugin('iotile_standard_library/lib_controller', 'ControllerTestPlugin')(self)
        self._tileinterface = find_proxy_plugin('iotile_standard_library/lib_controller', 'TileManagerPlugin')(self)
        self._trub = find_proxy_plugin('iotile_standard_library/lib_controller', 'RemoteBridgePlugin')(self)
        self._configstore = find_proxy_plugin('iotile_standard_library/lib_controller', 'ConfigDatabasePlugin')(self)

    @classmethod
    def ModuleName(cls):
        return 'NRF52 '

    @annotated
    def test_interface(self):
        """Create a context for basic tile functionality and throughput testing."""

        return self._testinterface

    @return_type("integer")
    def inc_atecc(self):
        """Test incrementing a counter inside the ATECC508A chip."""

        err, value = self.rpc(0xAB, 0x01, result_format="LL")
        if err:
            raise HardwareError("Error talking to ATECC508A chip", code=err)

        return value

    @return_type("basic_dict")
    def query_streaming(self):
        """Query the current parameters used for streaming data over bluetooth.

        This function returns information like:
        - The maximum size of a report that the device will emit
        - The supported and selected compression types to be used when transmitting
          data.
        """

        max_packet, supported_comp, chosen_comp = self.rpc(0x0A, 0x06, result_format="LBB")

        return {
            'max_report_size': max_packet,
            'supported_compression': supported_comp,
            'selected_compression': chosen_comp
        }

    @param("max_packet", "integer", "positive", desc="The maximum report size that the device should send")
    def config_streaming(self, max_packet):
        """Configure the curent parameters to use for streaming until we disconnect."""

        # Currently hardcode a lack of support for compression

        err, = self.rpc(0x0A, 0x05, max_packet, 0, arg_format="LB", result_format="L")
        if err:
            raise HardwareError("Error configuring streaming", code=err)

    @docannotate
    def query_bleparams(self):
        """Query the current BLE connection parameters.

        The connection interval and timeout information is returned
        as well as the device's preferred information as a dictionary.

        This function can be used to determine whether you should
        request the device change its connection parameters.

        Returns:
            basic_dict: A dictionary of connection information.
        """

        err, interval, timeout, pref_min, pref_max, pref_timeout = self.rpc(0x80, 0x00, result_format="LHHHHH2x")
        if err != 0:
            raise HardwareError("Could not query ble parameters", error_code=err)

        return {
            'conn_interval_ms': interval * 1.25,
            'preferred_min_ms': pref_min * 1.25,
            'preferred_max_ms': pref_max * 1.25,
            'timeout_ms': timeout * 10,
            'pref_timeout_ms': pref_timeout * 10
        }

    @docannotate
    def update_bleparams(self, min_conn, max_conn, timeout):
        """Update the current BLE connection parameters.

        These parameters determine the maximum throughput of the BLE connection
        by setting the interval with which the two parties communicate.  With
        most devices either 4 or 6 packets may be sent in each direction during
        each connection interval. With standard 20-byte packets this means that
        the maximum throughput is:
              4*20*1000
            -------------
            conn_interval

        with conn_interval in units of milliseconds, this will result in a
        throughput in bytes per second.  Note that this throughput will only
        be reached if you are able to queue at least 4 packets in advance of
        each connection interval, which will only be possible if you don't need
        an explicit acknowledgement from the other side for each packet before
        generating the next packet.

        This function will trigger the device to request a connection parameter
        update with its central and then return.  You can check if the parameters
        changed by calling query_bleparams afterward.

        There are certain requirements that must be followed for the parameters
        or if will be rejected by the partner device.  It may always be rejected
        if the partner feels like it.

        In particular:
        - min_conn in [7.5 ms, 4 s]
        - max_conn >= min_conn and giving a range is better than forcing a single
          value although you can set min_conn to max_conn to force a single value.
        - timeout in [100 ms, 32 s]

        Args:
            min_conn (float): The minimum connection interval in ms.  The minimum
                acceptable value is 7.5 ms.
            max_conn (float): The maximum connection interval in ms.  The minimum
                acceptable value is 7.5 ms.
            timeout (float): The supervisory timeout in seconds.  If
                no successful communication happens in this timeout, the
                connection is terminated.  This minimum acceptable value is 100 ms.
        """

        min_conn = int(min_conn / 1.25)
        max_conn = int(max_conn / 1.25)
        timeout = int(timeout / 0.01)

        err, = self.rpc(0x80, 0x01, min_conn, max_conn, timeout, 0, arg_format="HHHH", result_format="L")
        if err:
            raise HardwareError("Could not trigger update to ble connection parameters", error_code=err)

    @annotated
    def config_database(self):
        return self._configstore

    @annotated
    def remote_bridge(self):
        return self._trub
        
    @annotated
    def sensor_graph(self):
        return self._sensorgraph

    @annotated
    def tile_manager(self):
        return self._tileinterface

    @annotated
    def reset(self):
        """Reset this controller tile."""

        #NB, the wait time here must be longer than the supervisory timeout on the BLE
        #connection, otherwise the ble connection will not be seen to be disconnected
        #on the client side.
        iprint("Resetting, takes at least 2 seconds")
        TileBusProxyObject.reset(self, wait=2.0)

    @return_type("string")
    def hardware_version(self):
        """Return the embedded hardware version string for this tile
        """
        res = self.rpc(0x00, 0x02, result_type=(0, True))

        #Result is a string but with zero appended to the end to make it a fixed 10 byte
        #size
        binary_version = res['buffer']

        ver = ""

        for x in binary_version:
            if x != 0:
                ver += chr(x)

        return ver

    @param("expected", "string", desc="The hardware string we expect to find")
    @return_type("bool")
    def check_hardware(self, expected):
        """Make sure the hardware version is what we expect

        Returns true if the hardware is the expected version, false otherwise
        """

        if len(expected) < 10:
            expected += '\0'*(10 - len(expected))
        err, = self.rpc(0x00, 0x03, expected, result_format="L")
        if err == 0:
            return True

        return False
