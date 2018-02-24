import time
import struct
import binascii
from iotile.core.hw.proxy.plugin import TileBusProxyPlugin
from typedargs.annotate import param, return_type, context
from iotile.core.exceptions import HardwareError, ArgumentError


@context("ControllerTest")
class ControllerTestPlugin(TileBusProxyPlugin):
    """
    ControllerTest - a context to test basic tile functionality and performance

    Methods in this context can be used to assess tile health as well as the throughput
    available through the tilebus transport protocol that is being used to inject RPCs 
    into the iotile.  
    """

    def __init__(self, parent):
        super(ControllerTestPlugin, self).__init__(parent)

    @return_type("string")
    @param("input", "string")
    def echo(self, input):
        """
        Echo the input string back as a basic test of functionality
        """

        res = self.rpc(0x10, 0x00, input, result_type=(0, True))
        return str(res['buffer'])

    @return_type("integer")
    def current_time(self):
        """Return the current time on the device."""

        res = self.rpc(0x10, 0x01, result_type=(0, True))
        uptime, = struct.unpack("<L", res['buffer'])

        return uptime

    @return_type("float")
    def current_temp(self):
        """Return the current temperature in celsius as float."""

        err, val = self.rpc(0x10, 0x09, result_format="LL")
        if err:
            raise HardwareError("Error getting current temperature", error_code=err)

        #Result is an unsigned 16.16 int
        shifted_val = val << 16
        shifted_val -= (512 << 32)

        return float(shifted_val) / (1 << 32)

    @param("data", "string", desc="Trace data to send to the controller")
    def trace(self, data):
        """Send trace data to the controller to trace.

        This function takes the data parameter and sends it to the controller
        in 20 byte chunks to the trace_data RPC so that it gets traced out
        of the controller's configured trace endpoint (potentially over BLE).

        Args:
            data (string): The data to send to the controller.
        """
        for i in xrange(0, len(data), 20):
            chunk = data[i:i+20]
            err, = self.rpc(0x10, 0x0c, chunk, result_format="L")
            if err != 0:
                raise HardwareError("Error tracing data", error_code=err)

    @return_type("map(string, float)")
    def temp_range(self):
        """Return the min and max temperature seen by the device in the last configurable recording interval

        Calls to this function made within 10 seconds of a recording interval change will raise an error
        since there will not have been an updated temperature reading to start the interval.

        Raises:
            HardwareError: If there is no data available since we just started the temperature measurement interval
        """

        minval, maxval = self.rpc(0x10, 0x0a, result_format="LL")

        shifted_val = minval << 16
        shifted_val -= (512 << 32)

        if minval > maxval:
            raise HardwareError("No data available yet for this measurement interval, try again in 10 seconds")

        minval = float(shifted_val) / (1 << 32)

        shifted_val = maxval << 16
        shifted_val -= (512 << 32)

        maxval = float(shifted_val) / (1 << 32)

        return {'min': minval, 'max': maxval}


    @param("iterations", "integer", desc="Number of calls to make in order to do the test")
    @return_type("map(string, float)")
    def throughput(self, iterations):
        """
        Test the throughput with which RPCs can be sent to this device

        Test both RPCs that contain full payloads and RPCs that do not 
        contain payloads incase the underlying transport layer optimizes
        in the no payload case. 

        The return type is expressed in calls per second
        """

        #Test full payloads
        start = time.clock()

        for i in xrange(0, iterations):
            self.echo(" "*20)

        end = time.clock()

        bw_full = iterations / (end-start)

        #Test empty payloads
        start = time.clock()

        for i in xrange(0, iterations):
            self.echo("")

        end = time.clock()

        bw_empty = iterations / (end-start)

        return {'full_payload': bw_full, 'empty_payload': bw_empty}

    @return_type("float")
    def battery_voltage(self):
        """
        Measure the controller's battery voltage and report it in volts
        """

        error, value = self.rpc(0x10, 0x02, result_format="LL")
        if error != 0:
            raise HardwareError("Battery voltage sampling is not supported", error_code=error)

        return float(value)/(1<<16)

    def grouper(self, iterable, n, fillvalue=None):
        from itertools import izip_longest

        args = [iter(iterable)] * n
        return izip_longest(*args, fillvalue=fillvalue)

    @param("address", "integer", "nonnegative", desc="Address to start reading")
    @param("length", "integer", "positive", desc="Length to read")
    @return_type("string")
    def read_flash(self, address, length):
        import binascii
        data = bytearray()

        while length > 0:
            chunk = length
            if length > 20:
                chunk = 20

            arg = struct.pack("<L", address)
            res = self.rpc(0x10, 0x03, arg, result_type=(0, True))

            data += res['buffer'][:chunk]

            length -= chunk
            address += chunk

        words = [x for x in self.grouper(data, 4, 0x00)]
        hexwords = [str(bytearray(x)).encode('hex') for x in words]
        
        return " ".join(hexwords)

    @param("address", "integer", "nonnegative", desc="Address to start reading")
    def erase_sector(self, address):
        arg = struct.pack("<L", address)
        self.rpc(0x10, 0x04, arg)

    @param("enabled", "bool", desc="Enable debug mode?")
    def set_debug_mode(self, enabled):
        """Enable or disable debug mode where tiles do not sleep
        """

        self.rpc(0x10, 0x05, int(enabled))

    @param("enabled", "bool", desc="Enable debug mode?")
    def set_safe_mode(self, enabled):
        """Enable or disable safe mode where tiles are not allows to run usercode
        """

        self.rpc(0x10, 0x06, int(enabled))

    @return_type("basic_dict")
    def get_info(self):
        """Get parameters about controller status like debug mode, safe mode, uuid, etc

        Returns:
            dict: A dictionary with the following keys set: device_id, stateman_flags,
                safe_mode, debug_mode
        """

        device_id, flags, specific_flags, os_version, app_version = self.rpc(0x10, 0x08, result_format="LLB3xLL")

        result = {}
        result['device_id'] = device_id
        result['stateman_flags'] = flags
        result['safe_mode'] = bool(specific_flags & (1<<1))
        result['debug_mode'] = bool(specific_flags & (1<<0))

        #packed_version = tag | (major << 26) | (minor << 20)
        #The controller stores a 20 bit tag value that should uniquely identify
        #the kind of OS or APP that it is running.  Each of those are asociated
        #with a 6.6 bit X.Y major and minor version number.
        result['os_tag'] = os_version  & ((1 << 20) - 1)
        result['app_tag'] = app_version & ((1 << 20) - 1)
        result['os_version'] = '%d.%d'  % ((os_version >> 26) &  ((1 << 6) - 1),  (os_version>>20) & ((1 << 6) - 1))
        result['app_version'] = '%d.%d'  % ((app_version >> 26) &  ((1 << 6) - 1), (app_version>>20) & ((1 << 6) - 1))
        result['os_info_raw'] = os_version
        result['app_info_raw'] = app_version

        return result

    @param("name", "string", desc="app or os")
    @param("tag", "integer", "nonnegative", desc="OS or app tag to program")
    @param("version", "string", desc="The major.minor version to program")
    def set_version(self, name, tag, version="0.0"):
        """Update the controller's internal app or os info to the given tag/version.

        The tag is a 20-bit number that should uniquely identify the type of hardware/firmware
        combination on the device and the version is a 6.6 bit fixed point number that follows
        major.minor semantic version with 0.0 indicating an unknown version.
        """

        if name not in ['app', 'os']:
            raise ArgumentError("You must specify either app or os to set_version", name=name)

        update_app = int(name == 'app')
        update_os = int(name == 'os')

        if tag >= (1 << 20):
            raise ArgumentError("The tag number is too high.  It must fit in 20-bits", max_tag=1 << 20, tag=tag)

        if "." not in version:
            raise ArgumentError("You must pass a version number in X.Y format", version=version)

        major, _, minor = version.partition('.')
        try:
            major = int(major)
            minor = int(minor)
        except ValueError:
            raise ArgumentError("Unable to convert version string into major and minor version numbers", version=version)

        if major < 0 or minor < 0 or major >= (1 << 6) or minor >= (1 << 6):
            raise ArgumentError("Invalid version numbers that must be in the range [0, 63]", major=major, minor=minor, version_string=version)

        version_number = (major << 6) | minor
        combined_tag = (version_number << 20) | tag

        args = struct.pack("<LLBB", combined_tag, combined_tag, update_os, update_app)

        err, = self.rpc(0x10, 0x0B, args, result_format="L")
        if err:
            raise HardwareError("Error setting version", error_code=err, tag=tag, version=version)

    @param("key", "string", desc="The key to set in hex, should be 64 hex characters")
    def set_userkey(self, key):
        """Set the user key for the device

        Raises:
            HardwareError: if the key could not be set
        """

        binkey = bytearray(binascii.unhexlify(key))
        assert len(binkey) == 32

        #Send with cmd 0: set low part
        err, = self.rpc(0x10, 0x07, 0, 0, binkey[:16], result_format="L")
        if err:
            raise HardwareError("Error setting the lowest 16 bytes of key", error_code=err)

        #Send with cmd 1: set high part and save
        err, = self.rpc(0x10, 0x07, 1, 0, binkey[16:], result_format="L")
        if err:
            raise HardwareError("Error setting the highest 16 bytes of key", error_code=err)
