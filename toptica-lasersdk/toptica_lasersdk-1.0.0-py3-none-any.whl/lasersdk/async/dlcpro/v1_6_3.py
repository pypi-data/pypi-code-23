# Generated from 'v1_6_3.xml' on 2018-02-15 09:58:51.323204

from typing import Tuple

from toptica.lasersdk.async.client import AccessLevel
from toptica.lasersdk.async.client import Client

from toptica.lasersdk.async.client import DecofBoolean
from toptica.lasersdk.async.client import DecofInteger
from toptica.lasersdk.async.client import DecofReal
from toptica.lasersdk.async.client import DecofString
from toptica.lasersdk.async.client import DecofBinary

from toptica.lasersdk.async.client import MutableDecofBoolean
from toptica.lasersdk.async.client import MutableDecofInteger
from toptica.lasersdk.async.client import MutableDecofReal
from toptica.lasersdk.async.client import MutableDecofString
from toptica.lasersdk.async.client import MutableDecofBinary

from toptica.lasersdk.async.client import Connection
from toptica.lasersdk.async.client import NetworkConnection
from toptica.lasersdk.async.client import SerialConnection

from toptica.lasersdk.async.client import DecofError
from toptica.lasersdk.async.client import DeviceNotFoundError


class BuildInformation:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._build_node_name = DecofString(client, name + ':build-node-name')
        self._build_id = DecofString(client, name + ':build-id')
        self._build_number = DecofInteger(client, name + ':build-number')
        self._build_tag = DecofString(client, name + ':build-tag')
        self._c_compiler_id = DecofString(client, name + ':c-compiler-id')
        self._cxx_compiler_id = DecofString(client, name + ':cxx-compiler-id')
        self._job_name = DecofString(client, name + ':job-name')
        self._c_compiler_version = DecofString(client, name + ':c-compiler-version')
        self._build_url = DecofString(client, name + ':build-url')
        self._cxx_compiler_version = DecofString(client, name + ':cxx-compiler-version')

    @property
    def build_node_name(self) -> 'DecofString':
        return self._build_node_name

    @property
    def build_id(self) -> 'DecofString':
        return self._build_id

    @property
    def build_number(self) -> 'DecofInteger':
        return self._build_number

    @property
    def build_tag(self) -> 'DecofString':
        return self._build_tag

    @property
    def c_compiler_id(self) -> 'DecofString':
        return self._c_compiler_id

    @property
    def cxx_compiler_id(self) -> 'DecofString':
        return self._cxx_compiler_id

    @property
    def job_name(self) -> 'DecofString':
        return self._job_name

    @property
    def c_compiler_version(self) -> 'DecofString':
        return self._c_compiler_version

    @property
    def build_url(self) -> 'DecofString':
        return self._build_url

    @property
    def cxx_compiler_version(self) -> 'DecofString':
        return self._cxx_compiler_version


class Ipconfig:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cmd_port = DecofInteger(client, name + ':cmd-port')
        self._ip_addr = DecofString(client, name + ':ip-addr')
        self._mac_addr = DecofString(client, name + ':mac-addr')
        self._mon_port = DecofInteger(client, name + ':mon-port')
        self._net_mask = DecofString(client, name + ':net-mask')
        self._dhcp = DecofBoolean(client, name + ':dhcp')

    @property
    def cmd_port(self) -> 'DecofInteger':
        return self._cmd_port

    @property
    def ip_addr(self) -> 'DecofString':
        return self._ip_addr

    @property
    def mac_addr(self) -> 'DecofString':
        return self._mac_addr

    @property
    def mon_port(self) -> 'DecofInteger':
        return self._mon_port

    @property
    def net_mask(self) -> 'DecofString':
        return self._net_mask

    @property
    def dhcp(self) -> 'DecofBoolean':
        return self._dhcp

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)

    async def set_dhcp(self) -> None:
        await self.__client.exec(self.__name + ':set-dhcp', input_stream=None, output_type=None, return_type=None)

    async def set_ip(self, ip_addr: str, net_mask: str) -> None:
        assert isinstance(ip_addr, str), "expected type 'str' for parameter 'ip_addr', got '{}'".format(type(ip_addr))
        assert isinstance(net_mask, str), "expected type 'str' for parameter 'net_mask', got '{}'".format(type(net_mask))
        await self.__client.exec(self.__name + ':set-ip', ip_addr, net_mask, input_stream=None, output_type=None, return_type=None)


class FwUpdate:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name

    async def show_history(self) -> str:
        return await self.__client.exec(self.__name + ':show-history', input_stream=None, output_type=str, return_type=None)

    async def upload(self, stream_input: bytes, filename: str) -> None:
        assert isinstance(stream_input, bytes), "expected type 'bytes' for parameter 'stream_input', got '{}'".format(type(stream_input))
        assert isinstance(filename, str), "expected type 'str' for parameter 'filename', got '{}'".format(type(filename))
        await self.__client.exec(self.__name + ':upload', filename, input_stream=stream_input, output_type=None, return_type=None)

    async def show_log(self) -> str:
        return await self.__client.exec(self.__name + ':show-log', input_stream=None, output_type=str, return_type=None)


class ServiceReport:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._ready = DecofBoolean(client, name + ':ready')

    @property
    def ready(self) -> 'DecofBoolean':
        return self._ready

    async def print(self) -> bytes:
        return await self.__client.exec(self.__name + ':print', input_stream=None, output_type=bytes, return_type=None)

    async def service_report(self) -> bytes:
        return await self.__client.exec(self.__name + ':service-report', input_stream=None, output_type=bytes, return_type=None)

    async def request(self) -> None:
        await self.__client.exec(self.__name + ':request', input_stream=None, output_type=None, return_type=None)


class Licenses:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._installed_keys = DecofInteger(client, name + ':installed-keys')
        self._options = LicenseOptions(client, name + ':options')

    @property
    def installed_keys(self) -> 'DecofInteger':
        return self._installed_keys

    @property
    def options(self) -> 'LicenseOptions':
        return self._options

    async def get_key(self, key_number: int) -> str:
        assert isinstance(key_number, int), "expected type 'int' for parameter 'key_number', got '{}'".format(type(key_number))
        return await self.__client.exec(self.__name + ':get-key', key_number, input_stream=None, output_type=None, return_type=str)

    async def install(self, licensekey: str) -> bool:
        assert isinstance(licensekey, str), "expected type 'str' for parameter 'licensekey', got '{}'".format(type(licensekey))
        return await self.__client.exec(self.__name + ':install', licensekey, input_stream=None, output_type=None, return_type=bool)


class LicenseOptions:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._lock = LicenseOption(client, name + ':lock')

    @property
    def lock(self) -> 'LicenseOption':
        return self._lock


class LicenseOption:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._valid_until = DecofString(client, name + ':valid-until')
        self._licensee = DecofString(client, name + ':licensee')
        self._enabled = DecofBoolean(client, name + ':enabled')

    @property
    def valid_until(self) -> 'DecofString':
        return self._valid_until

    @property
    def licensee(self) -> 'DecofString':
        return self._licensee

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled


class SystemMessages:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._count = DecofInteger(client, name + ':count')
        self._latest_message = DecofString(client, name + ':latest-message')
        self._count_new = DecofInteger(client, name + ':count-new')

    @property
    def count(self) -> 'DecofInteger':
        return self._count

    @property
    def latest_message(self) -> 'DecofString':
        return self._latest_message

    @property
    def count_new(self) -> 'DecofInteger':
        return self._count_new

    async def show_persistent(self) -> str:
        return await self.__client.exec(self.__name + ':show-persistent', input_stream=None, output_type=str, return_type=None)

    async def show_new(self) -> str:
        return await self.__client.exec(self.__name + ':show-new', input_stream=None, output_type=str, return_type=None)

    async def show_log(self) -> str:
        return await self.__client.exec(self.__name + ':show-log', input_stream=None, output_type=str, return_type=None)

    async def show_all(self) -> str:
        return await self.__client.exec(self.__name + ':show-all', input_stream=None, output_type=str, return_type=None)

    async def mark_as_read(self, ID: int) -> None:
        assert isinstance(ID, int), "expected type 'int' for parameter 'ID', got '{}'".format(type(ID))
        await self.__client.exec(self.__name + ':mark-as-read', ID, input_stream=None, output_type=None, return_type=None)


class PowerSupply:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._type_ = DecofString(client, name + ':type')
        self._voltage_15Vn = DecofReal(client, name + ':voltage-15Vn')
        self._status = DecofInteger(client, name + ':status')
        self._voltage_5V = DecofReal(client, name + ':voltage-5V')
        self._current_5V = DecofReal(client, name + ':current-5V')
        self._voltage_15V = DecofReal(client, name + ':voltage-15V')
        self._load = DecofReal(client, name + ':load')
        self._revision = DecofString(client, name + ':revision')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._voltage_3V3 = DecofReal(client, name + ':voltage-3V3')
        self._current_15V = DecofReal(client, name + ':current-15V')
        self._current_15Vn = DecofReal(client, name + ':current-15Vn')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def voltage_15Vn(self) -> 'DecofReal':
        return self._voltage_15Vn

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def voltage_5V(self) -> 'DecofReal':
        return self._voltage_5V

    @property
    def current_5V(self) -> 'DecofReal':
        return self._current_5V

    @property
    def voltage_15V(self) -> 'DecofReal':
        return self._voltage_15V

    @property
    def load(self) -> 'DecofReal':
        return self._load

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def voltage_3V3(self) -> 'DecofReal':
        return self._voltage_3V3

    @property
    def current_15V(self) -> 'DecofReal':
        return self._current_15V

    @property
    def current_15Vn(self) -> 'DecofReal':
        return self._current_15Vn

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp


class PcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._channel_count = DecofInteger(client, name + ':channel-count')
        self._channel2 = PiezoDrv3(client, name + ':channel2')
        self._status = DecofInteger(client, name + ':status')
        self._revision = DecofString(client, name + ':revision')
        self._slot = DecofString(client, name + ':slot')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._variant = DecofString(client, name + ':variant')
        self._channel1 = PiezoDrv3(client, name + ':channel1')

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def channel_count(self) -> 'DecofInteger':
        return self._channel_count

    @property
    def channel2(self) -> 'PiezoDrv3':
        return self._channel2

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def channel1(self) -> 'PiezoDrv3':
        return self._channel1


class PiezoDrv3:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._voltage_set_dithering = MutableDecofBoolean(client, name + ':voltage-set-dithering')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._path = DecofString(client, name + ':path')
        self._status = DecofInteger(client, name + ':status')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._output_filter = OutputFilter3(client, name + ':output-filter')
        self._external_input = ExtInput3(client, name + ':external-input')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def voltage_set_dithering(self) -> 'MutableDecofBoolean':
        return self._voltage_set_dithering

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def output_filter(self) -> 'OutputFilter3':
        return self._output_filter

    @property
    def external_input(self) -> 'ExtInput3':
        return self._external_input

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set


class OutputFilter3:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._slew_rate = MutableDecofReal(client, name + ':slew-rate')
        self._slew_rate_limited = DecofBoolean(client, name + ':slew-rate-limited')
        self._slew_rate_enabled = MutableDecofBoolean(client, name + ':slew-rate-enabled')

    @property
    def slew_rate(self) -> 'MutableDecofReal':
        return self._slew_rate

    @property
    def slew_rate_limited(self) -> 'DecofBoolean':
        return self._slew_rate_limited

    @property
    def slew_rate_enabled(self) -> 'MutableDecofBoolean':
        return self._slew_rate_enabled


class ExtInput3:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._factor = MutableDecofReal(client, name + ':factor')
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class IoBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._digital_out2 = IoDigitalOutput(client, name + ':digital-out2')
        self._revision = DecofString(client, name + ':revision')
        self._digital_in3 = IoDigitalInput(client, name + ':digital-in3')
        self._out_a = IoOutputChannel(client, name + ':out-a')
        self._digital_out0 = IoDigitalOutput(client, name + ':digital-out0')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._out_b = IoOutputChannel(client, name + ':out-b')
        self._digital_out3 = IoDigitalOutput(client, name + ':digital-out3')
        self._digital_in1 = IoDigitalInput(client, name + ':digital-in1')
        self._digital_in0 = IoDigitalInput(client, name + ':digital-in0')
        self._digital_out1 = IoDigitalOutput(client, name + ':digital-out1')
        self._digital_in2 = IoDigitalInput(client, name + ':digital-in2')
        self._serial_number = DecofString(client, name + ':serial-number')

    @property
    def digital_out2(self) -> 'IoDigitalOutput':
        return self._digital_out2

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def digital_in3(self) -> 'IoDigitalInput':
        return self._digital_in3

    @property
    def out_a(self) -> 'IoOutputChannel':
        return self._out_a

    @property
    def digital_out0(self) -> 'IoDigitalOutput':
        return self._digital_out0

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def out_b(self) -> 'IoOutputChannel':
        return self._out_b

    @property
    def digital_out3(self) -> 'IoDigitalOutput':
        return self._digital_out3

    @property
    def digital_in1(self) -> 'IoDigitalInput':
        return self._digital_in1

    @property
    def digital_in0(self) -> 'IoDigitalInput':
        return self._digital_in0

    @property
    def digital_out1(self) -> 'IoDigitalOutput':
        return self._digital_out1

    @property
    def digital_in2(self) -> 'IoDigitalInput':
        return self._digital_in2

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number


class IoDigitalOutput:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._invert = MutableDecofBoolean(client, name + ':invert')
        self._mode = MutableDecofInteger(client, name + ':mode')
        self._value_set = MutableDecofBoolean(client, name + ':value-set')
        self._value_act = DecofBoolean(client, name + ':value-act')

    @property
    def invert(self) -> 'MutableDecofBoolean':
        return self._invert

    @property
    def mode(self) -> 'MutableDecofInteger':
        return self._mode

    @property
    def value_set(self) -> 'MutableDecofBoolean':
        return self._value_set

    @property
    def value_act(self) -> 'DecofBoolean':
        return self._value_act


class IoDigitalInput:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._value_act = DecofBoolean(client, name + ':value-act')

    @property
    def value_act(self) -> 'DecofBoolean':
        return self._value_act


class IoOutputChannel:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._linked_laser = MutableDecofInteger(client, name + ':linked-laser')
        self._voltage_offset = MutableDecofReal(client, name + ':voltage-offset')
        self._external_input = ExtInput2(client, name + ':external-input')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def linked_laser(self) -> 'MutableDecofInteger':
        return self._linked_laser

    @property
    def voltage_offset(self) -> 'MutableDecofReal':
        return self._voltage_offset

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set


class ExtInput2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._factor = MutableDecofReal(client, name + ':factor')
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class OutputFilter2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._slew_rate = MutableDecofReal(client, name + ':slew-rate')
        self._slew_rate_limited = DecofBoolean(client, name + ':slew-rate-limited')
        self._slew_rate_enabled = MutableDecofBoolean(client, name + ':slew-rate-enabled')

    @property
    def slew_rate(self) -> 'MutableDecofReal':
        return self._slew_rate

    @property
    def slew_rate_limited(self) -> 'DecofBoolean':
        return self._slew_rate_limited

    @property
    def slew_rate_enabled(self) -> 'MutableDecofBoolean':
        return self._slew_rate_enabled


class Buzzer:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._welcome = MutableDecofString(client, name + ':welcome')

    @property
    def welcome(self) -> 'MutableDecofString':
        return self._welcome

    async def play(self, melody: str) -> None:
        assert isinstance(melody, str), "expected type 'str' for parameter 'melody', got '{}'".format(type(melody))
        await self.__client.exec(self.__name + ':play', melody, input_stream=None, output_type=None, return_type=None)

    async def play_welcome(self) -> None:
        await self.__client.exec(self.__name + ':play-welcome', input_stream=None, output_type=None, return_type=None)


class TcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fpga_fw_ver = DecofString(client, name + ':fpga-fw-ver')
        self._channel1 = TcChannel2(client, name + ':channel1')
        self._revision = DecofString(client, name + ':revision')
        self._slot = DecofString(client, name + ':slot')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._channel2 = TcChannel2(client, name + ':channel2')
        self._serial_number = DecofString(client, name + ':serial-number')

    @property
    def fpga_fw_ver(self) -> 'DecofString':
        return self._fpga_fw_ver

    @property
    def channel1(self) -> 'TcChannel2':
        return self._channel1

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def channel2(self) -> 'TcChannel2':
        return self._channel2

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number


class TcChannel2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._temp_set_min = MutableDecofReal(client, name + ':temp-set-min')
        self._limits = TcChannelCheck2(client, name + ':limits')
        self._t_loop = TcChannelTLoop2(client, name + ':t-loop')
        self._current_set_max = MutableDecofReal(client, name + ':current-set-max')
        self._drv_voltage = DecofReal(client, name + ':drv-voltage')
        self._current_set_min = MutableDecofReal(client, name + ':current-set-min')
        self._power_source = DecofInteger(client, name + ':power-source')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._ntc_parallel_resistance = DecofReal(client, name + ':ntc-parallel-resistance')
        self._current_set = DecofReal(client, name + ':current-set')
        self._temp_act = DecofReal(client, name + ':temp-act')
        self._path = DecofString(client, name + ':path')
        self._ready = DecofBoolean(client, name + ':ready')
        self._status = DecofInteger(client, name + ':status')
        self._fault = DecofBoolean(client, name + ':fault')
        self._temp_set_max = MutableDecofReal(client, name + ':temp-set-max')
        self._resistance = DecofReal(client, name + ':resistance')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._c_loop = TcChannelCLoop2(client, name + ':c-loop')
        self._ntc_series_resistance = DecofReal(client, name + ':ntc-series-resistance')
        self._temp_reset = MutableDecofBoolean(client, name + ':temp-reset')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._current_act = DecofReal(client, name + ':current-act')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._external_input = ExtInput2(client, name + ':external-input')

    @property
    def temp_set_min(self) -> 'MutableDecofReal':
        return self._temp_set_min

    @property
    def limits(self) -> 'TcChannelCheck2':
        return self._limits

    @property
    def t_loop(self) -> 'TcChannelTLoop2':
        return self._t_loop

    @property
    def current_set_max(self) -> 'MutableDecofReal':
        return self._current_set_max

    @property
    def drv_voltage(self) -> 'DecofReal':
        return self._drv_voltage

    @property
    def current_set_min(self) -> 'MutableDecofReal':
        return self._current_set_min

    @property
    def power_source(self) -> 'DecofInteger':
        return self._power_source

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def ntc_parallel_resistance(self) -> 'DecofReal':
        return self._ntc_parallel_resistance

    @property
    def current_set(self) -> 'DecofReal':
        return self._current_set

    @property
    def temp_act(self) -> 'DecofReal':
        return self._temp_act

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def ready(self) -> 'DecofBoolean':
        return self._ready

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def fault(self) -> 'DecofBoolean':
        return self._fault

    @property
    def temp_set_max(self) -> 'MutableDecofReal':
        return self._temp_set_max

    @property
    def resistance(self) -> 'DecofReal':
        return self._resistance

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def c_loop(self) -> 'TcChannelCLoop2':
        return self._c_loop

    @property
    def ntc_series_resistance(self) -> 'DecofReal':
        return self._ntc_series_resistance

    @property
    def temp_reset(self) -> 'MutableDecofBoolean':
        return self._temp_reset

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    async def check_peltier(self) -> float:
        return await self.__client.exec(self.__name + ':check-peltier', input_stream=None, output_type=None, return_type=float)


class TcChannelCheck2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._timed_out = DecofBoolean(client, name + ':timed-out')
        self._out_of_range = DecofBoolean(client, name + ':out-of-range')
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')

    @property
    def timed_out(self) -> 'DecofBoolean':
        return self._timed_out

    @property
    def out_of_range(self) -> 'DecofBoolean':
        return self._out_of_range

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max


class TcChannelTLoop2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._on = MutableDecofBoolean(client, name + ':on')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')
        self._d_gain = MutableDecofReal(client, name + ':d-gain')

    @property
    def on(self) -> 'MutableDecofBoolean':
        return self._on

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain


class TcChannelCLoop2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._on = MutableDecofBoolean(client, name + ':on')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')

    @property
    def on(self) -> 'MutableDecofBoolean':
        return self._on

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain


class Standby:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._laser1 = StandbyLaser(client, name + ':laser1')
        self._state = DecofInteger(client, name + ':state')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def laser1(self) -> 'StandbyLaser':
        return self._laser1

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class StandbyLaser:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._nlo = StandbyShg(client, name + ':nlo')
        self._amp = StandbyAmp(client, name + ':amp')
        self._dl = StandbyDl(client, name + ':dl')

    @property
    def nlo(self) -> 'StandbyShg':
        return self._nlo

    @property
    def amp(self) -> 'StandbyAmp':
        return self._amp

    @property
    def dl(self) -> 'StandbyDl':
        return self._dl


class StandbyShg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_servo_subsystem = MutableDecofBoolean(client, name + ':disable-servo-subsystem')
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')
        self._disable_power_stabilization = MutableDecofBoolean(client, name + ':disable-power-stabilization')
        self._disable_cavity_lock = MutableDecofBoolean(client, name + ':disable-cavity-lock')
        self._disable_pc = MutableDecofBoolean(client, name + ':disable-pc')

    @property
    def disable_servo_subsystem(self) -> 'MutableDecofBoolean':
        return self._disable_servo_subsystem

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc

    @property
    def disable_power_stabilization(self) -> 'MutableDecofBoolean':
        return self._disable_power_stabilization

    @property
    def disable_cavity_lock(self) -> 'MutableDecofBoolean':
        return self._disable_cavity_lock

    @property
    def disable_pc(self) -> 'MutableDecofBoolean':
        return self._disable_pc


class StandbyAmp:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')
        self._disable_cc = MutableDecofBoolean(client, name + ':disable-cc')

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc

    @property
    def disable_cc(self) -> 'MutableDecofBoolean':
        return self._disable_cc


class StandbyDl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')
        self._disable_cc = MutableDecofBoolean(client, name + ':disable-cc')
        self._disable_pc = MutableDecofBoolean(client, name + ':disable-pc')

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc

    @property
    def disable_cc(self) -> 'MutableDecofBoolean':
        return self._disable_cc

    @property
    def disable_pc(self) -> 'MutableDecofBoolean':
        return self._disable_pc


class UvShgLaser:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pump_power_margin = DecofReal(client, name + ':pump-power-margin')
        self._operation_time_pump = DecofReal(client, name + ':operation-time-pump')
        self._power_act = DecofReal(client, name + ':power-act')
        self._error_txt = DecofString(client, name + ':error-txt')
        self._emission = DecofBoolean(client, name + ':emission')
        self._operation_time_uv = DecofReal(client, name + ':operation-time-uv')
        self._error = DecofInteger(client, name + ':error')
        self._baseplate_temperature = DecofReal(client, name + ':baseplate-temperature')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._remaining_optics_spots = DecofInteger(client, name + ':remaining-optics-spots')
        self._power_set = MutableDecofReal(client, name + ':power-set')
        self._status = DecofInteger(client, name + ':status')

    @property
    def pump_power_margin(self) -> 'DecofReal':
        return self._pump_power_margin

    @property
    def operation_time_pump(self) -> 'DecofReal':
        return self._operation_time_pump

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act

    @property
    def error_txt(self) -> 'DecofString':
        return self._error_txt

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def operation_time_uv(self) -> 'DecofReal':
        return self._operation_time_uv

    @property
    def error(self) -> 'DecofInteger':
        return self._error

    @property
    def baseplate_temperature(self) -> 'DecofReal':
        return self._baseplate_temperature

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def remaining_optics_spots(self) -> 'DecofInteger':
        return self._remaining_optics_spots

    @property
    def power_set(self) -> 'MutableDecofReal':
        return self._power_set

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    async def perform_optimization(self) -> None:
        await self.__client.exec(self.__name + ':perform-optimization', input_stream=None, output_type=None, return_type=None)

    async def clear_errors(self) -> None:
        await self.__client.exec(self.__name + ':clear-errors', input_stream=None, output_type=None, return_type=None)


class Laser:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._type_ = DecofString(client, name + ':type')
        self._scan = ScanGenerator(client, name + ':scan')
        self._wide_scan = WideScan(client, name + ':wide-scan')
        self._amp = LaserAmp(client, name + ':amp')
        self._health_txt = DecofString(client, name + ':health-txt')
        self._emission = DecofBoolean(client, name + ':emission')
        self._ctl = CtlT(client, name + ':ctl')
        self._pd_ext = PdExt(client, name + ':pd-ext')
        self._product_name = DecofString(client, name + ':product-name')
        self._power_stabilization = PwrStab(client, name + ':power-stabilization')
        self._nlo = Nlo(client, name + ':nlo')
        self._dpss = Dpss2(client, name + ':dpss')
        self._uv = UvShg(client, name + ':uv')
        self._recorder = Recorder(client, name + ':recorder')
        self._health = DecofInteger(client, name + ':health')
        self._dl = LaserHead(client, name + ':dl')
        self._scope = ScopeT(client, name + ':scope')

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def scan(self) -> 'ScanGenerator':
        return self._scan

    @property
    def wide_scan(self) -> 'WideScan':
        return self._wide_scan

    @property
    def amp(self) -> 'LaserAmp':
        return self._amp

    @property
    def health_txt(self) -> 'DecofString':
        return self._health_txt

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def ctl(self) -> 'CtlT':
        return self._ctl

    @property
    def pd_ext(self) -> 'PdExt':
        return self._pd_ext

    @property
    def product_name(self) -> 'DecofString':
        return self._product_name

    @property
    def power_stabilization(self) -> 'PwrStab':
        return self._power_stabilization

    @property
    def nlo(self) -> 'Nlo':
        return self._nlo

    @property
    def dpss(self) -> 'Dpss2':
        return self._dpss

    @property
    def uv(self) -> 'UvShg':
        return self._uv

    @property
    def recorder(self) -> 'Recorder':
        return self._recorder

    @property
    def health(self) -> 'DecofInteger':
        return self._health

    @property
    def dl(self) -> 'LaserHead':
        return self._dl

    @property
    def scope(self) -> 'ScopeT':
        return self._scope

    async def save(self) -> None:
        await self.__client.exec(self.__name + ':save', input_stream=None, output_type=None, return_type=None)

    async def load(self) -> None:
        await self.__client.exec(self.__name + ':load', input_stream=None, output_type=None, return_type=None)


class ScanGenerator:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._end = MutableDecofReal(client, name + ':end')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._unit = DecofString(client, name + ':unit')
        self._signal_type = MutableDecofInteger(client, name + ':signal-type')
        self._start = MutableDecofReal(client, name + ':start')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._offset = MutableDecofReal(client, name + ':offset')
        self._frequency = MutableDecofReal(client, name + ':frequency')

    @property
    def end(self) -> 'MutableDecofReal':
        return self._end

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def signal_type(self) -> 'MutableDecofInteger':
        return self._signal_type

    @property
    def start(self) -> 'MutableDecofReal':
        return self._start

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def offset(self) -> 'MutableDecofReal':
        return self._offset

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency


class WideScan:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan_begin = MutableDecofReal(client, name + ':scan-begin')
        self._remaining_time = DecofInteger(client, name + ':remaining-time')
        self._state = DecofInteger(client, name + ':state')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._speed = MutableDecofReal(client, name + ':speed')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._scan_end = MutableDecofReal(client, name + ':scan-end')
        self._progress = DecofInteger(client, name + ':progress')
        self._offset = MutableDecofReal(client, name + ':offset')
        self._duration = MutableDecofReal(client, name + ':duration')

    @property
    def scan_begin(self) -> 'MutableDecofReal':
        return self._scan_begin

    @property
    def remaining_time(self) -> 'DecofInteger':
        return self._remaining_time

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def speed(self) -> 'MutableDecofReal':
        return self._speed

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def scan_end(self) -> 'MutableDecofReal':
        return self._scan_end

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def offset(self) -> 'MutableDecofReal':
        return self._offset

    @property
    def duration(self) -> 'MutableDecofReal':
        return self._duration

    async def stop(self) -> None:
        await self.__client.exec(self.__name + ':stop', input_stream=None, output_type=None, return_type=None)

    async def start(self) -> None:
        await self.__client.exec(self.__name + ':start', input_stream=None, output_type=None, return_type=None)


class LaserAmp:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._type_ = DecofString(client, name + ':type')
        self._factory_settings = AmpFactory(client, name + ':factory-settings')
        self._seed_limits = AmpPower(client, name + ':seed-limits')
        self._cc = Cc5000Drv(client, name + ':cc')
        self._tc = TcChannel2(client, name + ':tc')
        self._ontime = DecofInteger(client, name + ':ontime')
        self._ontime_txt = DecofString(client, name + ':ontime-txt')
        self._output_limits = AmpPower(client, name + ':output-limits')
        self._legacy = DecofBoolean(client, name + ':legacy')
        self._version = DecofString(client, name + ':version')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._seedonly_check = AmpSeedonlyCheck(client, name + ':seedonly-check')

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def factory_settings(self) -> 'AmpFactory':
        return self._factory_settings

    @property
    def seed_limits(self) -> 'AmpPower':
        return self._seed_limits

    @property
    def cc(self) -> 'Cc5000Drv':
        return self._cc

    @property
    def tc(self) -> 'TcChannel2':
        return self._tc

    @property
    def ontime(self) -> 'DecofInteger':
        return self._ontime

    @property
    def ontime_txt(self) -> 'DecofString':
        return self._ontime_txt

    @property
    def output_limits(self) -> 'AmpPower':
        return self._output_limits

    @property
    def legacy(self) -> 'DecofBoolean':
        return self._legacy

    @property
    def version(self) -> 'DecofString':
        return self._version

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def seedonly_check(self) -> 'AmpSeedonlyCheck':
        return self._seedonly_check

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)


class AmpFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cc = AmpFactoryCc(client, name + ':cc')
        self._wavelength = MutableDecofReal(client, name + ':wavelength')
        self._power = MutableDecofReal(client, name + ':power')
        self._last_modified = DecofString(client, name + ':last-modified')
        self._modified = DecofBoolean(client, name + ':modified')
        self._seedonly_check = AmpFactorySeedonly(client, name + ':seedonly-check')
        self._output_limits = AmpFactoryPower(client, name + ':output-limits')
        self._seed_limits = AmpFactoryPower(client, name + ':seed-limits')
        self._tc = TcFactorySettings(client, name + ':tc')

    @property
    def cc(self) -> 'AmpFactoryCc':
        return self._cc

    @property
    def wavelength(self) -> 'MutableDecofReal':
        return self._wavelength

    @property
    def power(self) -> 'MutableDecofReal':
        return self._power

    @property
    def last_modified(self) -> 'DecofString':
        return self._last_modified

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def seedonly_check(self) -> 'AmpFactorySeedonly':
        return self._seedonly_check

    @property
    def output_limits(self) -> 'AmpFactoryPower':
        return self._output_limits

    @property
    def seed_limits(self) -> 'AmpFactoryPower':
        return self._seed_limits

    @property
    def tc(self) -> 'TcFactorySettings':
        return self._tc

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class AmpFactoryCc:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._current_clip_modified = DecofBoolean(client, name + ':current-clip-modified')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._current_clip_last_modified = DecofString(client, name + ':current-clip-last-modified')

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def current_clip_modified(self) -> 'DecofBoolean':
        return self._current_clip_modified

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def current_clip_last_modified(self) -> 'DecofString':
        return self._current_clip_last_modified


class AmpFactorySeedonly:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._warning_delay = MutableDecofReal(client, name + ':warning-delay')
        self._shutdown_delay = MutableDecofReal(client, name + ':shutdown-delay')

    @property
    def warning_delay(self) -> 'MutableDecofReal':
        return self._warning_delay

    @property
    def shutdown_delay(self) -> 'MutableDecofReal':
        return self._shutdown_delay


class AmpFactoryPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._power_max = MutableDecofReal(client, name + ':power-max')
        self._power_min_shutdown_delay = MutableDecofReal(client, name + ':power-min-shutdown-delay')
        self._power_min = MutableDecofReal(client, name + ':power-min')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._power_min_warning_delay = MutableDecofReal(client, name + ':power-min-warning-delay')
        self._power_max_shutdown_delay = MutableDecofReal(client, name + ':power-max-shutdown-delay')
        self._power_max_warning_delay = MutableDecofReal(client, name + ':power-max-warning-delay')

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def power_max(self) -> 'MutableDecofReal':
        return self._power_max

    @property
    def power_min_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_min_shutdown_delay

    @property
    def power_min(self) -> 'MutableDecofReal':
        return self._power_min

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def power_min_warning_delay(self) -> 'MutableDecofReal':
        return self._power_min_warning_delay

    @property
    def power_max_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_max_shutdown_delay

    @property
    def power_max_warning_delay(self) -> 'MutableDecofReal':
        return self._power_max_warning_delay


class TcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._ntc_parallel_resistance = MutableDecofReal(client, name + ':ntc-parallel-resistance')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._c_gain = MutableDecofReal(client, name + ':c-gain')
        self._power_source = MutableDecofInteger(client, name + ':power-source')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._current_max = MutableDecofReal(client, name + ':current-max')
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._ntc_series_resistance = MutableDecofReal(client, name + ':ntc-series-resistance')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._current_min = MutableDecofReal(client, name + ':current-min')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def ntc_parallel_resistance(self) -> 'MutableDecofReal':
        return self._ntc_parallel_resistance

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def c_gain(self) -> 'MutableDecofReal':
        return self._c_gain

    @property
    def power_source(self) -> 'MutableDecofInteger':
        return self._power_source

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def current_max(self) -> 'MutableDecofReal':
        return self._current_max

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def ntc_series_resistance(self) -> 'MutableDecofReal':
        return self._ntc_series_resistance

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def current_min(self) -> 'MutableDecofReal':
        return self._current_min

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max


class AmpPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._power = DecofReal(client, name + ':power')
        self._power_min_shutdown_delay = MutableDecofReal(client, name + ':power-min-shutdown-delay')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._power_min_warning_delay = MutableDecofReal(client, name + ':power-min-warning-delay')
        self._power_max_shutdown_delay = MutableDecofReal(client, name + ':power-max-shutdown-delay')
        self._power_max = MutableDecofReal(client, name + ':power-max')
        self._power_max_warning_delay = MutableDecofReal(client, name + ':power-max-warning-delay')
        self._power_min = MutableDecofReal(client, name + ':power-min')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._status = DecofInteger(client, name + ':status')

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def power_min_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_min_shutdown_delay

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def power_min_warning_delay(self) -> 'MutableDecofReal':
        return self._power_min_warning_delay

    @property
    def power_max_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_max_shutdown_delay

    @property
    def power_max(self) -> 'MutableDecofReal':
        return self._power_max

    @property
    def power_max_warning_delay(self) -> 'MutableDecofReal':
        return self._power_max_warning_delay

    @property
    def power_min(self) -> 'MutableDecofReal':
        return self._power_min

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def status(self) -> 'DecofInteger':
        return self._status


class Cc5000Drv:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._current_act = DecofReal(client, name + ':current-act')
        self._emission = DecofBoolean(client, name + ':emission')
        self._voltage_out = DecofReal(client, name + ':voltage-out')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._variant = DecofString(client, name + ':variant')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._path = DecofString(client, name + ':path')
        self._status = DecofInteger(client, name + ':status')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._aux = DecofReal(client, name + ':aux')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def voltage_out(self) -> 'DecofReal':
        return self._voltage_out

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit


class AmpSeedonlyCheck:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._warning_delay = MutableDecofReal(client, name + ':warning-delay')
        self._pump = DecofBoolean(client, name + ':pump')
        self._seed = DecofBoolean(client, name + ':seed')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._shutdown_delay = MutableDecofReal(client, name + ':shutdown-delay')
        self._status = DecofInteger(client, name + ':status')

    @property
    def warning_delay(self) -> 'MutableDecofReal':
        return self._warning_delay

    @property
    def pump(self) -> 'DecofBoolean':
        return self._pump

    @property
    def seed(self) -> 'DecofBoolean':
        return self._seed

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def shutdown_delay(self) -> 'MutableDecofReal':
        return self._shutdown_delay

    @property
    def status(self) -> 'DecofInteger':
        return self._status


class CtlT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._motor = CtlMotor(client, name + ':motor')
        self._mode_control = CtlModeControl(client, name + ':mode-control')
        self._scan = CtlScanT(client, name + ':scan')
        self._factory_settings = CtlFactory(client, name + ':factory-settings')
        self._wavelength_set = MutableDecofReal(client, name + ':wavelength-set')
        self._wavelength_act = DecofReal(client, name + ':wavelength-act')
        self._remote_control = CtlRemoteControl(client, name + ':remote-control')
        self._head_temperature = DecofReal(client, name + ':head-temperature')
        self._power = CtlPower(client, name + ':power')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._wavelength_min = DecofReal(client, name + ':wavelength-min')
        self._state = DecofInteger(client, name + ':state')
        self._tuning_current_min = DecofReal(client, name + ':tuning-current-min')
        self._tuning_power_min = DecofReal(client, name + ':tuning-power-min')
        self._wavelength_max = DecofReal(client, name + ':wavelength-max')
        self._optimization = CtlOptimizationT(client, name + ':optimization')
        self._state_txt = DecofString(client, name + ':state-txt')

    @property
    def motor(self) -> 'CtlMotor':
        return self._motor

    @property
    def mode_control(self) -> 'CtlModeControl':
        return self._mode_control

    @property
    def scan(self) -> 'CtlScanT':
        return self._scan

    @property
    def factory_settings(self) -> 'CtlFactory':
        return self._factory_settings

    @property
    def wavelength_set(self) -> 'MutableDecofReal':
        return self._wavelength_set

    @property
    def wavelength_act(self) -> 'DecofReal':
        return self._wavelength_act

    @property
    def remote_control(self) -> 'CtlRemoteControl':
        return self._remote_control

    @property
    def head_temperature(self) -> 'DecofReal':
        return self._head_temperature

    @property
    def power(self) -> 'CtlPower':
        return self._power

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def wavelength_min(self) -> 'DecofReal':
        return self._wavelength_min

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def tuning_current_min(self) -> 'DecofReal':
        return self._tuning_current_min

    @property
    def tuning_power_min(self) -> 'DecofReal':
        return self._tuning_power_min

    @property
    def wavelength_max(self) -> 'DecofReal':
        return self._wavelength_max

    @property
    def optimization(self) -> 'CtlOptimizationT':
        return self._optimization

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt


class CtlMotor:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_save_disabled = MutableDecofBoolean(client, name + ':power-save-disabled')
        self._position_hysteresis_microstep = MutableDecofInteger(client, name + ':position-hysteresis-microstep')
        self._position_hysteresis_fullstep = MutableDecofInteger(client, name + ':position-hysteresis-fullstep')
        self._position_accuracy_fullstep = MutableDecofInteger(client, name + ':position-accuracy-fullstep')
        self._position_accuracy_microstep = MutableDecofInteger(client, name + ':position-accuracy-microstep')

    @property
    def power_save_disabled(self) -> 'MutableDecofBoolean':
        return self._power_save_disabled

    @property
    def position_hysteresis_microstep(self) -> 'MutableDecofInteger':
        return self._position_hysteresis_microstep

    @property
    def position_hysteresis_fullstep(self) -> 'MutableDecofInteger':
        return self._position_hysteresis_fullstep

    @property
    def position_accuracy_fullstep(self) -> 'MutableDecofInteger':
        return self._position_accuracy_fullstep

    @property
    def position_accuracy_microstep(self) -> 'MutableDecofInteger':
        return self._position_accuracy_microstep


class CtlModeControl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._loop_enabled = MutableDecofBoolean(client, name + ':loop-enabled')

    @property
    def loop_enabled(self) -> 'MutableDecofBoolean':
        return self._loop_enabled


class CtlScanT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._wavelength_end = MutableDecofReal(client, name + ':wavelength-end')
        self._speed_min = DecofReal(client, name + ':speed-min')
        self._remaining_time = DecofInteger(client, name + ':remaining-time')
        self._speed = MutableDecofReal(client, name + ':speed')
        self._speed_max = DecofReal(client, name + ':speed-max')
        self._shape = MutableDecofInteger(client, name + ':shape')
        self._trigger = CtlTriggerT(client, name + ':trigger')
        self._microsteps = MutableDecofBoolean(client, name + ':microsteps')
        self._continuous_mode = MutableDecofBoolean(client, name + ':continuous-mode')
        self._progress = DecofInteger(client, name + ':progress')
        self._wavelength_begin = MutableDecofReal(client, name + ':wavelength-begin')

    @property
    def wavelength_end(self) -> 'MutableDecofReal':
        return self._wavelength_end

    @property
    def speed_min(self) -> 'DecofReal':
        return self._speed_min

    @property
    def remaining_time(self) -> 'DecofInteger':
        return self._remaining_time

    @property
    def speed(self) -> 'MutableDecofReal':
        return self._speed

    @property
    def speed_max(self) -> 'DecofReal':
        return self._speed_max

    @property
    def shape(self) -> 'MutableDecofInteger':
        return self._shape

    @property
    def trigger(self) -> 'CtlTriggerT':
        return self._trigger

    @property
    def microsteps(self) -> 'MutableDecofBoolean':
        return self._microsteps

    @property
    def continuous_mode(self) -> 'MutableDecofBoolean':
        return self._continuous_mode

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def wavelength_begin(self) -> 'MutableDecofReal':
        return self._wavelength_begin

    async def stop(self) -> None:
        await self.__client.exec(self.__name + ':stop', input_stream=None, output_type=None, return_type=None)

    async def pause(self) -> None:
        await self.__client.exec(self.__name + ':pause', input_stream=None, output_type=None, return_type=None)

    async def start(self) -> None:
        await self.__client.exec(self.__name + ':start', input_stream=None, output_type=None, return_type=None)

    async def continue_(self) -> None:
        await self.__client.exec(self.__name + ':continue', input_stream=None, output_type=None, return_type=None)


class CtlTriggerT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._output_enabled = MutableDecofBoolean(client, name + ':output-enabled')
        self._output_threshold = MutableDecofReal(client, name + ':output-threshold')
        self._input_enabled = MutableDecofBoolean(client, name + ':input-enabled')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')

    @property
    def output_enabled(self) -> 'MutableDecofBoolean':
        return self._output_enabled

    @property
    def output_threshold(self) -> 'MutableDecofReal':
        return self._output_threshold

    @property
    def input_enabled(self) -> 'MutableDecofBoolean':
        return self._input_enabled

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel


class CtlFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._tuning_current_min = DecofReal(client, name + ':tuning-current-min')
        self._tuning_power_min = DecofReal(client, name + ':tuning-power-min')
        self._wavelength_min = DecofReal(client, name + ':wavelength-min')
        self._wavelength_max = DecofReal(client, name + ':wavelength-max')

    @property
    def tuning_current_min(self) -> 'DecofReal':
        return self._tuning_current_min

    @property
    def tuning_power_min(self) -> 'DecofReal':
        return self._tuning_power_min

    @property
    def wavelength_min(self) -> 'DecofReal':
        return self._wavelength_min

    @property
    def wavelength_max(self) -> 'DecofReal':
        return self._wavelength_max

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class CtlRemoteControl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._factor = MutableDecofReal(client, name + ':factor')
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._speed = MutableDecofReal(client, name + ':speed')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def speed(self) -> 'MutableDecofReal':
        return self._speed

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class CtlPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_act = DecofReal(client, name + ':power-act')

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act


class CtlOptimizationT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._progress = DecofInteger(client, name + ':progress')

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    async def flow(self) -> None:
        await self.__client.exec(self.__name + ':flow', input_stream=None, output_type=None, return_type=None)

    async def smile(self) -> None:
        await self.__client.exec(self.__name + ':smile', input_stream=None, output_type=None, return_type=None)

    async def abort(self) -> None:
        await self.__client.exec(self.__name + ':abort', input_stream=None, output_type=None, return_type=None)


class PdExt:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._power = DecofReal(client, name + ':power')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._photodiode = DecofReal(client, name + ':photodiode')

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode


class PwrStab:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._gain = PwrStabGain2(client, name + ':gain')
        self._input_channel_value_act = DecofReal(client, name + ':input-channel-value-act')
        self._window = PwrStabWindow(client, name + ':window')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._output_channel = DecofInteger(client, name + ':output-channel')
        self._state = DecofInteger(client, name + ':state')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._sign = MutableDecofBoolean(client, name + ':sign')
        self._hold_output_on_unlock = MutableDecofBoolean(client, name + ':hold-output-on-unlock')

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def gain(self) -> 'PwrStabGain2':
        return self._gain

    @property
    def input_channel_value_act(self) -> 'DecofReal':
        return self._input_channel_value_act

    @property
    def window(self) -> 'PwrStabWindow':
        return self._window

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def output_channel(self) -> 'DecofInteger':
        return self._output_channel

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def sign(self) -> 'MutableDecofBoolean':
        return self._sign

    @property
    def hold_output_on_unlock(self) -> 'MutableDecofBoolean':
        return self._hold_output_on_unlock


class PwrStabGain2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._d = MutableDecofReal(client, name + ':d')
        self._i = MutableDecofReal(client, name + ':i')
        self._p = MutableDecofReal(client, name + ':p')
        self._all = MutableDecofReal(client, name + ':all')

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all


class PwrStabWindow:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._level_low = MutableDecofReal(client, name + ':level-low')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def level_low(self) -> 'MutableDecofReal':
        return self._level_low

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class Nlo:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shg = Shg(client, name + ':shg')
        self._power_optimization = NloLaserHeadPowerOptimization(client, name + ':power-optimization')
        self._pd = NloLaserHeadPhotoDiodes(client, name + ':pd')
        self._ssw_ver = DecofString(client, name + ':ssw-ver')
        self._fhg = Fhg(client, name + ':fhg')
        self._servo = NloLaserHeadServos(client, name + ':servo')

    @property
    def shg(self) -> 'Shg':
        return self._shg

    @property
    def power_optimization(self) -> 'NloLaserHeadPowerOptimization':
        return self._power_optimization

    @property
    def pd(self) -> 'NloLaserHeadPhotoDiodes':
        return self._pd

    @property
    def ssw_ver(self) -> 'DecofString':
        return self._ssw_ver

    @property
    def fhg(self) -> 'Fhg':
        return self._fhg

    @property
    def servo(self) -> 'NloLaserHeadServos':
        return self._servo


class Shg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pc = PiezoDrv2(client, name + ':pc')
        self._tc = TcChannel2(client, name + ':tc')
        self._factory_settings = ShgFactorySettings(client, name + ':factory-settings')
        self._scope = NloLaserHeadScopeT2(client, name + ':scope')
        self._scan = NloLaserHeadSiggen2(client, name + ':scan')
        self._lock = NloLaserHeadLockShg2(client, name + ':lock')

    @property
    def pc(self) -> 'PiezoDrv2':
        return self._pc

    @property
    def tc(self) -> 'TcChannel2':
        return self._tc

    @property
    def factory_settings(self) -> 'ShgFactorySettings':
        return self._factory_settings

    @property
    def scope(self) -> 'NloLaserHeadScopeT2':
        return self._scope

    @property
    def scan(self) -> 'NloLaserHeadSiggen2':
        return self._scan

    @property
    def lock(self) -> 'NloLaserHeadLockShg2':
        return self._lock

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)


class PiezoDrv2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._voltage_set_dithering = MutableDecofBoolean(client, name + ':voltage-set-dithering')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._path = DecofString(client, name + ':path')
        self._status = DecofInteger(client, name + ':status')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._external_input = ExtInput2(client, name + ':external-input')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def voltage_set_dithering(self) -> 'MutableDecofBoolean':
        return self._voltage_set_dithering

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set


class ShgFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._lock = NloLaserHeadLockFactorySettings(client, name + ':lock')
        self._pc = NloLaserHeadPcFactorySettings(client, name + ':pc')
        self._pd = NloLaserHeadShgPhotodiodesFactorySettings(client, name + ':pd')
        self._tc = NloLaserHeadTcFactorySettings(client, name + ':tc')
        self._modified = DecofBoolean(client, name + ':modified')

    @property
    def lock(self) -> 'NloLaserHeadLockFactorySettings':
        return self._lock

    @property
    def pc(self) -> 'NloLaserHeadPcFactorySettings':
        return self._pc

    @property
    def pd(self) -> 'NloLaserHeadShgPhotodiodesFactorySettings':
        return self._pd

    @property
    def tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._tc

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadLockFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._window = NloLaserHeadLockWindowFactorySettings(client, name + ':window')
        self._relock = NloLaserHeadRelockFactorySettings(client, name + ':relock')
        self._local_oscillator = NloLaserHeadLocalOscillatorFactorySettings(client, name + ':local-oscillator')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._analog_p_gain = MutableDecofReal(client, name + ':analog-p-gain')
        self._pid1_gain = NloLaserHeadPidGainFactorySettings(client, name + ':pid1-gain')
        self._pid2_gain = NloLaserHeadPidGainFactorySettings(client, name + ':pid2-gain')

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def window(self) -> 'NloLaserHeadLockWindowFactorySettings':
        return self._window

    @property
    def relock(self) -> 'NloLaserHeadRelockFactorySettings':
        return self._relock

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorFactorySettings':
        return self._local_oscillator

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def analog_p_gain(self) -> 'MutableDecofReal':
        return self._analog_p_gain

    @property
    def pid1_gain(self) -> 'NloLaserHeadPidGainFactorySettings':
        return self._pid1_gain

    @property
    def pid2_gain(self) -> 'NloLaserHeadPidGainFactorySettings':
        return self._pid2_gain


class NloLaserHeadLockWindowFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._threshold = MutableDecofReal(client, name + ':threshold')

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def threshold(self) -> 'MutableDecofReal':
        return self._threshold


class NloLaserHeadRelockFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._delay = MutableDecofReal(client, name + ':delay')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def delay(self) -> 'MutableDecofReal':
        return self._delay

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class NloLaserHeadLocalOscillatorFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._use_fast_oscillator = MutableDecofBoolean(client, name + ':use-fast-oscillator')
        self._phase_shift_shg = MutableDecofReal(client, name + ':phase-shift-shg')
        self._coupled_modulation = MutableDecofBoolean(client, name + ':coupled-modulation')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._attenuation_fhg_raw = MutableDecofInteger(client, name + ':attenuation-fhg-raw')
        self._attenuation_shg_raw = MutableDecofInteger(client, name + ':attenuation-shg-raw')
        self._phase_shift_fhg = MutableDecofReal(client, name + ':phase-shift-fhg')

    @property
    def use_fast_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_fast_oscillator

    @property
    def phase_shift_shg(self) -> 'MutableDecofReal':
        return self._phase_shift_shg

    @property
    def coupled_modulation(self) -> 'MutableDecofBoolean':
        return self._coupled_modulation

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def attenuation_fhg_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_fhg_raw

    @property
    def attenuation_shg_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_shg_raw

    @property
    def phase_shift_fhg(self) -> 'MutableDecofReal':
        return self._phase_shift_fhg


class NloLaserHeadPidGainFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')
        self._d = MutableDecofReal(client, name + ':d')
        self._p = MutableDecofReal(client, name + ':p')
        self._i = MutableDecofReal(client, name + ':i')
        self._all = MutableDecofReal(client, name + ':all')

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all


class NloLaserHeadPcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._scan_amplitude = MutableDecofReal(client, name + ':scan-amplitude')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._scan_offset = MutableDecofReal(client, name + ':scan-offset')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._capacitance = MutableDecofReal(client, name + ':capacitance')
        self._scan_frequency = MutableDecofReal(client, name + ':scan-frequency')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def scan_amplitude(self) -> 'MutableDecofReal':
        return self._scan_amplitude

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def scan_offset(self) -> 'MutableDecofReal':
        return self._scan_offset

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def capacitance(self) -> 'MutableDecofReal':
        return self._capacitance

    @property
    def scan_frequency(self) -> 'MutableDecofReal':
        return self._scan_frequency

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max


class NloLaserHeadShgPhotodiodesFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._int = NloLaserHeadPdDigilockFactorySettings(client, name + ':int')
        self._shg = NloLaserHeadPdFactorySettings(client, name + ':shg')
        self._fiber = NloLaserHeadPdFactorySettings(client, name + ':fiber')
        self._pdh_dc = NloLaserHeadPdDigilockFactorySettings(client, name + ':pdh-dc')
        self._pdh_rf = NloLaserHeadPdPdhFactorySettings(client, name + ':pdh-rf')

    @property
    def int(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._int

    @property
    def shg(self) -> 'NloLaserHeadPdFactorySettings':
        return self._shg

    @property
    def fiber(self) -> 'NloLaserHeadPdFactorySettings':
        return self._fiber

    @property
    def pdh_dc(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._pdh_dc

    @property
    def pdh_rf(self) -> 'NloLaserHeadPdPdhFactorySettings':
        return self._pdh_rf


class NloLaserHeadPdDigilockFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class NloLaserHeadPdFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class NloLaserHeadPdPdhFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = MutableDecofReal(client, name + ':gain')

    @property
    def gain(self) -> 'MutableDecofReal':
        return self._gain


class NloLaserHeadTcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._c_gain = MutableDecofReal(client, name + ':c-gain')
        self._power_source = MutableDecofInteger(client, name + ':power-source')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._ntc_series_resistance = MutableDecofReal(client, name + ':ntc-series-resistance')
        self._current_max = MutableDecofReal(client, name + ':current-max')
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._current_min = MutableDecofReal(client, name + ':current-min')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def c_gain(self) -> 'MutableDecofReal':
        return self._c_gain

    @property
    def power_source(self) -> 'MutableDecofInteger':
        return self._power_source

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def ntc_series_resistance(self) -> 'MutableDecofReal':
        return self._ntc_series_resistance

    @property
    def current_max(self) -> 'MutableDecofReal':
        return self._current_max

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def current_min(self) -> 'MutableDecofReal':
        return self._current_min

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max


class NloLaserHeadScopeT2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._timescale = MutableDecofReal(client, name + ':timescale')
        self._update_rate = MutableDecofInteger(client, name + ':update-rate')
        self._channel2 = NloLaserHeadScopeChannelT2(client, name + ':channel2')
        self._channelx = NloLaserHeadScopeXAxisT2(client, name + ':channelx')
        self._data = DecofBinary(client, name + ':data')
        self._channel1 = NloLaserHeadScopeChannelT2(client, name + ':channel1')
        self._variant = MutableDecofInteger(client, name + ':variant')

    @property
    def timescale(self) -> 'MutableDecofReal':
        return self._timescale

    @property
    def update_rate(self) -> 'MutableDecofInteger':
        return self._update_rate

    @property
    def channel2(self) -> 'NloLaserHeadScopeChannelT2':
        return self._channel2

    @property
    def channelx(self) -> 'NloLaserHeadScopeXAxisT2':
        return self._channelx

    @property
    def data(self) -> 'DecofBinary':
        return self._data

    @property
    def channel1(self) -> 'NloLaserHeadScopeChannelT2':
        return self._channel1

    @property
    def variant(self) -> 'MutableDecofInteger':
        return self._variant


class NloLaserHeadScopeChannelT2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._unit = DecofString(client, name + ':unit')
        self._name = DecofString(client, name + ':name')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class NloLaserHeadScopeXAxisT2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._spectrum_omit_dc = MutableDecofBoolean(client, name + ':spectrum-omit-dc')
        self._unit = DecofString(client, name + ':unit')
        self._scope_timescale = MutableDecofReal(client, name + ':scope-timescale')
        self._spectrum_range = MutableDecofReal(client, name + ':spectrum-range')
        self._xy_signal = MutableDecofInteger(client, name + ':xy-signal')
        self._name = DecofString(client, name + ':name')

    @property
    def spectrum_omit_dc(self) -> 'MutableDecofBoolean':
        return self._spectrum_omit_dc

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def scope_timescale(self) -> 'MutableDecofReal':
        return self._scope_timescale

    @property
    def spectrum_range(self) -> 'MutableDecofReal':
        return self._spectrum_range

    @property
    def xy_signal(self) -> 'MutableDecofInteger':
        return self._xy_signal

    @property
    def name(self) -> 'DecofString':
        return self._name


class NloLaserHeadSiggen2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._offset = MutableDecofReal(client, name + ':offset')
        self._frequency = MutableDecofReal(client, name + ':frequency')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def offset(self) -> 'MutableDecofReal':
        return self._offset

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency


class NloLaserHeadLockShg2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._pid2 = NloLaserHeadPid2(client, name + ':pid2')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._window = NloLaserHeadWindow2(client, name + ':window')
        self._cavity_slow_pzt_voltage = MutableDecofReal(client, name + ':cavity-slow-pzt-voltage')
        self._pid1 = NloLaserHeadPid2(client, name + ':pid1')
        self._state = DecofInteger(client, name + ':state')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._relock = NloLaserHeadRelock2(client, name + ':relock')
        self._local_oscillator = NloLaserHeadLocalOscillatorShg2(client, name + ':local-oscillator')
        self._analog_dl_gain = NloLaserHeadMinifalc2(client, name + ':analog-dl-gain')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._cavity_fast_pzt_voltage = MutableDecofReal(client, name + ':cavity-fast-pzt-voltage')

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def pid2(self) -> 'NloLaserHeadPid2':
        return self._pid2

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def window(self) -> 'NloLaserHeadWindow2':
        return self._window

    @property
    def cavity_slow_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_slow_pzt_voltage

    @property
    def pid1(self) -> 'NloLaserHeadPid2':
        return self._pid1

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def relock(self) -> 'NloLaserHeadRelock2':
        return self._relock

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorShg2':
        return self._local_oscillator

    @property
    def analog_dl_gain(self) -> 'NloLaserHeadMinifalc2':
        return self._analog_dl_gain

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def cavity_fast_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_fast_pzt_voltage


class NloLaserHeadPid2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = NloLaserHeadGain2(client, name + ':gain')

    @property
    def gain(self) -> 'NloLaserHeadGain2':
        return self._gain


class NloLaserHeadGain2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._i = MutableDecofReal(client, name + ':i')
        self._d = MutableDecofReal(client, name + ':d')
        self._p = MutableDecofReal(client, name + ':p')
        self._all = MutableDecofReal(client, name + ':all')

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all


class NloLaserHeadWindow2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._threshold = MutableDecofReal(client, name + ':threshold')
        self._calibration = NloLaserHeadWindowCalibration2(client, name + ':calibration')

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def threshold(self) -> 'MutableDecofReal':
        return self._threshold

    @property
    def calibration(self) -> 'NloLaserHeadWindowCalibration2':
        return self._calibration


class NloLaserHeadWindowCalibration2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name


class NloLaserHeadRelock2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._delay = MutableDecofReal(client, name + ':delay')
        self._frequency = MutableDecofReal(client, name + ':frequency')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def delay(self) -> 'MutableDecofReal':
        return self._delay

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency


class NloLaserHeadLocalOscillatorShg2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._use_fast_oscillator = MutableDecofBoolean(client, name + ':use-fast-oscillator')
        self._coupled_modulation = MutableDecofBoolean(client, name + ':coupled-modulation')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._use_external_oscillator = MutableDecofBoolean(client, name + ':use-external-oscillator')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._attenuation_raw = MutableDecofInteger(client, name + ':attenuation-raw')

    @property
    def use_fast_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_fast_oscillator

    @property
    def coupled_modulation(self) -> 'MutableDecofBoolean':
        return self._coupled_modulation

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def use_external_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_external_oscillator

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def attenuation_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_raw

    async def auto_pdh(self) -> None:
        await self.__client.exec(self.__name + ':auto-pdh', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadMinifalc2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._p_gain = MutableDecofReal(client, name + ':p-gain')

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain


class NloLaserHeadPowerOptimization:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._stage1 = NloLaserHeadStage2(client, name + ':stage1')
        self._abort = MutableDecofBoolean(client, name + ':abort')
        self._progress_data_shg = DecofBinary(client, name + ':progress-data-shg')
        self._status = DecofInteger(client, name + ':status')
        self._progress_data_fiber = DecofBinary(client, name + ':progress-data-fiber')
        self._stage4 = NloLaserHeadStage2(client, name + ':stage4')
        self._stage5 = NloLaserHeadStage2(client, name + ':stage5')
        self._progress = DecofInteger(client, name + ':progress')
        self._status_string = DecofString(client, name + ':status-string')
        self._progress_data_amp = DecofBinary(client, name + ':progress-data-amp')
        self._shg_advanced = MutableDecofBoolean(client, name + ':shg-advanced')
        self._ongoing = DecofBoolean(client, name + ':ongoing')
        self._stage2 = NloLaserHeadStage2(client, name + ':stage2')
        self._stage3 = NloLaserHeadStage2(client, name + ':stage3')
        self._progress_data_fhg = DecofBinary(client, name + ':progress-data-fhg')

    @property
    def stage1(self) -> 'NloLaserHeadStage2':
        return self._stage1

    @property
    def abort(self) -> 'MutableDecofBoolean':
        return self._abort

    @property
    def progress_data_shg(self) -> 'DecofBinary':
        return self._progress_data_shg

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def progress_data_fiber(self) -> 'DecofBinary':
        return self._progress_data_fiber

    @property
    def stage4(self) -> 'NloLaserHeadStage2':
        return self._stage4

    @property
    def stage5(self) -> 'NloLaserHeadStage2':
        return self._stage5

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def status_string(self) -> 'DecofString':
        return self._status_string

    @property
    def progress_data_amp(self) -> 'DecofBinary':
        return self._progress_data_amp

    @property
    def shg_advanced(self) -> 'MutableDecofBoolean':
        return self._shg_advanced

    @property
    def ongoing(self) -> 'DecofBoolean':
        return self._ongoing

    @property
    def stage2(self) -> 'NloLaserHeadStage2':
        return self._stage2

    @property
    def stage3(self) -> 'NloLaserHeadStage2':
        return self._stage3

    @property
    def progress_data_fhg(self) -> 'DecofBinary':
        return self._progress_data_fhg

    async def start_optimization_amp(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-amp', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_all(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-all', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_shg(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-shg', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_fiber(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-fiber', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_fhg(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-fhg', input_stream=None, output_type=None, return_type=int)


class NloLaserHeadStage2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._progress = DecofInteger(client, name + ':progress')
        self._restore_on_regress = MutableDecofBoolean(client, name + ':restore-on-regress')
        self._optimization_in_progress = DecofBoolean(client, name + ':optimization-in-progress')
        self._regress_tolerance = MutableDecofInteger(client, name + ':regress-tolerance')
        self._input = NloLaserHeadOptInput2(client, name + ':input')
        self._restore_on_abort = MutableDecofBoolean(client, name + ':restore-on-abort')

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def restore_on_regress(self) -> 'MutableDecofBoolean':
        return self._restore_on_regress

    @property
    def optimization_in_progress(self) -> 'DecofBoolean':
        return self._optimization_in_progress

    @property
    def regress_tolerance(self) -> 'MutableDecofInteger':
        return self._regress_tolerance

    @property
    def input(self) -> 'NloLaserHeadOptInput2':
        return self._input

    @property
    def restore_on_abort(self) -> 'MutableDecofBoolean':
        return self._restore_on_abort

    async def start_optimization(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization', input_stream=None, output_type=None, return_type=int)


class NloLaserHeadOptInput2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._value_calibrated = DecofReal(client, name + ':value-calibrated')

    @property
    def value_calibrated(self) -> 'DecofReal':
        return self._value_calibrated


class NloLaserHeadPhotoDiodes:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fhg_int = NloLaserHeadNloDigilockPhotodiode2(client, name + ':fhg-int')
        self._shg = NloLaserHeadNloPhotodiode2(client, name + ':shg')
        self._fhg = NloLaserHeadNloPhotodiode2(client, name + ':fhg')
        self._shg_pdh_rf = NloLaserHeadNloPdhPhotodiode2(client, name + ':shg-pdh-rf')
        self._amp = NloLaserHeadNloPhotodiode2(client, name + ':amp')
        self._shg_pdh_dc = NloLaserHeadNloDigilockPhotodiode2(client, name + ':shg-pdh-dc')
        self._fiber = NloLaserHeadNloPhotodiode2(client, name + ':fiber')
        self._shg_int = NloLaserHeadNloDigilockPhotodiode2(client, name + ':shg-int')
        self._fhg_pdh_dc = NloLaserHeadNloDigilockPhotodiode2(client, name + ':fhg-pdh-dc')
        self._dl = NloLaserHeadNloPhotodiode2(client, name + ':dl')
        self._fhg_pdh_rf = NloLaserHeadNloPdhPhotodiode2(client, name + ':fhg-pdh-rf')

    @property
    def fhg_int(self) -> 'NloLaserHeadNloDigilockPhotodiode2':
        return self._fhg_int

    @property
    def shg(self) -> 'NloLaserHeadNloPhotodiode2':
        return self._shg

    @property
    def fhg(self) -> 'NloLaserHeadNloPhotodiode2':
        return self._fhg

    @property
    def shg_pdh_rf(self) -> 'NloLaserHeadNloPdhPhotodiode2':
        return self._shg_pdh_rf

    @property
    def amp(self) -> 'NloLaserHeadNloPhotodiode2':
        return self._amp

    @property
    def shg_pdh_dc(self) -> 'NloLaserHeadNloDigilockPhotodiode2':
        return self._shg_pdh_dc

    @property
    def fiber(self) -> 'NloLaserHeadNloPhotodiode2':
        return self._fiber

    @property
    def shg_int(self) -> 'NloLaserHeadNloDigilockPhotodiode2':
        return self._shg_int

    @property
    def fhg_pdh_dc(self) -> 'NloLaserHeadNloDigilockPhotodiode2':
        return self._fhg_pdh_dc

    @property
    def dl(self) -> 'NloLaserHeadNloPhotodiode2':
        return self._dl

    @property
    def fhg_pdh_rf(self) -> 'NloLaserHeadNloPdhPhotodiode2':
        return self._fhg_pdh_rf


class NloLaserHeadNloDigilockPhotodiode2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._photodiode = DecofReal(client, name + ':photodiode')

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode


class NloLaserHeadNloPhotodiode2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._power = DecofReal(client, name + ':power')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class NloLaserHeadNloPdhPhotodiode2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = MutableDecofReal(client, name + ':gain')
        self._photodiode = DecofReal(client, name + ':photodiode')

    @property
    def gain(self) -> 'MutableDecofReal':
        return self._gain

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode


class Fhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pc = PiezoDrv2(client, name + ':pc')
        self._tc = TcChannel2(client, name + ':tc')
        self._factory_settings = FhgFactorySettings(client, name + ':factory-settings')
        self._scope = NloLaserHeadScopeT2(client, name + ':scope')
        self._scan = NloLaserHeadSiggen2(client, name + ':scan')
        self._lock = NloLaserHeadLockFhg(client, name + ':lock')

    @property
    def pc(self) -> 'PiezoDrv2':
        return self._pc

    @property
    def tc(self) -> 'TcChannel2':
        return self._tc

    @property
    def factory_settings(self) -> 'FhgFactorySettings':
        return self._factory_settings

    @property
    def scope(self) -> 'NloLaserHeadScopeT2':
        return self._scope

    @property
    def scan(self) -> 'NloLaserHeadSiggen2':
        return self._scan

    @property
    def lock(self) -> 'NloLaserHeadLockFhg':
        return self._lock

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)


class FhgFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._lock = NloLaserHeadLockFactorySettings(client, name + ':lock')
        self._pc = NloLaserHeadPcFactorySettings(client, name + ':pc')
        self._pd = NloLaserHeadFhgPhotodiodesFactorySettings(client, name + ':pd')
        self._tc = NloLaserHeadTcFactorySettings(client, name + ':tc')
        self._modified = DecofBoolean(client, name + ':modified')

    @property
    def lock(self) -> 'NloLaserHeadLockFactorySettings':
        return self._lock

    @property
    def pc(self) -> 'NloLaserHeadPcFactorySettings':
        return self._pc

    @property
    def pd(self) -> 'NloLaserHeadFhgPhotodiodesFactorySettings':
        return self._pd

    @property
    def tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._tc

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadFhgPhotodiodesFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._int = NloLaserHeadPdDigilockFactorySettings(client, name + ':int')
        self._fhg = NloLaserHeadPdFactorySettings(client, name + ':fhg')
        self._pdh_dc = NloLaserHeadPdDigilockFactorySettings(client, name + ':pdh-dc')
        self._pdh_rf = NloLaserHeadPdPdhFactorySettings(client, name + ':pdh-rf')

    @property
    def int(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._int

    @property
    def fhg(self) -> 'NloLaserHeadPdFactorySettings':
        return self._fhg

    @property
    def pdh_dc(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._pdh_dc

    @property
    def pdh_rf(self) -> 'NloLaserHeadPdPdhFactorySettings':
        return self._pdh_rf


class NloLaserHeadLockFhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._pid2 = NloLaserHeadPid2(client, name + ':pid2')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._cavity_slow_pzt_voltage = MutableDecofReal(client, name + ':cavity-slow-pzt-voltage')
        self._pid1 = NloLaserHeadPid2(client, name + ':pid1')
        self._state = DecofInteger(client, name + ':state')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._relock = NloLaserHeadRelock2(client, name + ':relock')
        self._local_oscillator = NloLaserHeadLocalOscillatorFhg(client, name + ':local-oscillator')
        self._window = NloLaserHeadWindow2(client, name + ':window')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._cavity_fast_pzt_voltage = MutableDecofReal(client, name + ':cavity-fast-pzt-voltage')

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def pid2(self) -> 'NloLaserHeadPid2':
        return self._pid2

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def cavity_slow_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_slow_pzt_voltage

    @property
    def pid1(self) -> 'NloLaserHeadPid2':
        return self._pid1

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def relock(self) -> 'NloLaserHeadRelock2':
        return self._relock

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorFhg':
        return self._local_oscillator

    @property
    def window(self) -> 'NloLaserHeadWindow2':
        return self._window

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def cavity_fast_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_fast_pzt_voltage


class NloLaserHeadLocalOscillatorFhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._use_fast_oscillator = MutableDecofBoolean(client, name + ':use-fast-oscillator')
        self._coupled_modulation = MutableDecofBoolean(client, name + ':coupled-modulation')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._attenuation_raw = MutableDecofInteger(client, name + ':attenuation-raw')

    @property
    def use_fast_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_fast_oscillator

    @property
    def coupled_modulation(self) -> 'MutableDecofBoolean':
        return self._coupled_modulation

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def attenuation_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_raw

    async def auto_pdh(self) -> None:
        await self.__client.exec(self.__name + ':auto-pdh', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadServos:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fiber2_vert = NloLaserHeadServoPwm2(client, name + ':fiber2-vert')
        self._ta1_vert = NloLaserHeadServoPwm2(client, name + ':ta1-vert')
        self._fhg2_hor = NloLaserHeadServoPwm2(client, name + ':fhg2-hor')
        self._ta1_hor = NloLaserHeadServoPwm2(client, name + ':ta1-hor')
        self._shg2_vert = NloLaserHeadServoPwm2(client, name + ':shg2-vert')
        self._shg1_vert = NloLaserHeadServoPwm2(client, name + ':shg1-vert')
        self._shg2_hor = NloLaserHeadServoPwm2(client, name + ':shg2-hor')
        self._ta2_hor = NloLaserHeadServoPwm2(client, name + ':ta2-hor')
        self._fiber1_vert = NloLaserHeadServoPwm2(client, name + ':fiber1-vert')
        self._fhg1_vert = NloLaserHeadServoPwm2(client, name + ':fhg1-vert')
        self._fiber1_hor = NloLaserHeadServoPwm2(client, name + ':fiber1-hor')
        self._uv_cryst = NloLaserHeadServoPwm2(client, name + ':uv-cryst')
        self._shg1_hor = NloLaserHeadServoPwm2(client, name + ':shg1-hor')
        self._fhg1_hor = NloLaserHeadServoPwm2(client, name + ':fhg1-hor')
        self._fhg2_vert = NloLaserHeadServoPwm2(client, name + ':fhg2-vert')
        self._fiber2_hor = NloLaserHeadServoPwm2(client, name + ':fiber2-hor')
        self._ta2_vert = NloLaserHeadServoPwm2(client, name + ':ta2-vert')
        self._uv_outcpl = NloLaserHeadServoPwm2(client, name + ':uv-outcpl')

    @property
    def fiber2_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._fiber2_vert

    @property
    def ta1_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._ta1_vert

    @property
    def fhg2_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._fhg2_hor

    @property
    def ta1_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._ta1_hor

    @property
    def shg2_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._shg2_vert

    @property
    def shg1_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._shg1_vert

    @property
    def shg2_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._shg2_hor

    @property
    def ta2_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._ta2_hor

    @property
    def fiber1_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._fiber1_vert

    @property
    def fhg1_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._fhg1_vert

    @property
    def fiber1_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._fiber1_hor

    @property
    def uv_cryst(self) -> 'NloLaserHeadServoPwm2':
        return self._uv_cryst

    @property
    def shg1_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._shg1_hor

    @property
    def fhg1_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._fhg1_hor

    @property
    def fhg2_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._fhg2_vert

    @property
    def fiber2_hor(self) -> 'NloLaserHeadServoPwm2':
        return self._fiber2_hor

    @property
    def ta2_vert(self) -> 'NloLaserHeadServoPwm2':
        return self._ta2_vert

    @property
    def uv_outcpl(self) -> 'NloLaserHeadServoPwm2':
        return self._uv_outcpl

    async def center_all_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-all-servos', input_stream=None, output_type=None, return_type=None)

    async def center_shg_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-shg-servos', input_stream=None, output_type=None, return_type=None)

    async def center_fiber_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-fiber-servos', input_stream=None, output_type=None, return_type=None)

    async def center_ta_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-ta-servos', input_stream=None, output_type=None, return_type=None)

    async def center_fhg_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-fhg-servos', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadServoPwm2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._display_name = DecofString(client, name + ':display-name')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._value = MutableDecofInteger(client, name + ':value')

    @property
    def display_name(self) -> 'DecofString':
        return self._display_name

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def value(self) -> 'MutableDecofInteger':
        return self._value

    async def center_servo(self) -> None:
        await self.__client.exec(self.__name + ':center-servo', input_stream=None, output_type=None, return_type=None)


class Dpss2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_act = DecofReal(client, name + ':power-act')
        self._error_code = DecofInteger(client, name + ':error-code')
        self._status = DecofInteger(client, name + ':status')
        self._current_max = DecofReal(client, name + ':current-max')
        self._operation_time = DecofReal(client, name + ':operation-time')
        self._power_max = DecofReal(client, name + ':power-max')
        self._current_act = DecofReal(client, name + ':current-act')
        self._tc_status_txt = DecofString(client, name + ':tc-status-txt')
        self._tc_status = DecofInteger(client, name + ':tc-status')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._power_margin = DecofReal(client, name + ':power-margin')
        self._power_set = MutableDecofReal(client, name + ':power-set')
        self._error_txt = DecofString(client, name + ':error-txt')

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act

    @property
    def error_code(self) -> 'DecofInteger':
        return self._error_code

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def current_max(self) -> 'DecofReal':
        return self._current_max

    @property
    def operation_time(self) -> 'DecofReal':
        return self._operation_time

    @property
    def power_max(self) -> 'DecofReal':
        return self._power_max

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def tc_status_txt(self) -> 'DecofString':
        return self._tc_status_txt

    @property
    def tc_status(self) -> 'DecofInteger':
        return self._tc_status

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def power_margin(self) -> 'DecofReal':
        return self._power_margin

    @property
    def power_set(self) -> 'MutableDecofReal':
        return self._power_set

    @property
    def error_txt(self) -> 'DecofString':
        return self._error_txt


class UvShg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan = NloLaserHeadSiggen1(client, name + ':scan')
        self._power_stabilization = UvShgPowerStabilization(client, name + ':power-stabilization')
        self._factory_settings = UvFactorySettings(client, name + ':factory-settings')
        self._eom = UvEom(client, name + ':eom')
        self._servo = NloLaserHeadUvServos(client, name + ':servo')
        self._cavity = UvCavity(client, name + ':cavity')
        self._operation_time = DecofReal(client, name + ':operation-time')
        self._pd = NloLaserHeadUvPhotoDiodes(client, name + ':pd')
        self._crystal = UvCrystal(client, name + ':crystal')
        self._status_parameters = UvStatusParameters(client, name + ':status-parameters')
        self._status = DecofInteger(client, name + ':status')
        self._error = DecofInteger(client, name + ':error')
        self._power_optimization = UvShgPowerOptimization(client, name + ':power-optimization')
        self._error_txt = DecofString(client, name + ':error-txt')
        self._lock = NloLaserHeadLockShg1(client, name + ':lock')
        self._power_margin = DecofReal(client, name + ':power-margin')
        self._pump = Dpss1(client, name + ':pump')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._ssw_ver = DecofString(client, name + ':ssw-ver')
        self._scope = NloLaserHeadScopeT1(client, name + ':scope')
        self._remaining_optics_spots = DecofInteger(client, name + ':remaining-optics-spots')
        self._baseplate_temperature = DecofReal(client, name + ':baseplate-temperature')

    @property
    def scan(self) -> 'NloLaserHeadSiggen1':
        return self._scan

    @property
    def power_stabilization(self) -> 'UvShgPowerStabilization':
        return self._power_stabilization

    @property
    def factory_settings(self) -> 'UvFactorySettings':
        return self._factory_settings

    @property
    def eom(self) -> 'UvEom':
        return self._eom

    @property
    def servo(self) -> 'NloLaserHeadUvServos':
        return self._servo

    @property
    def cavity(self) -> 'UvCavity':
        return self._cavity

    @property
    def operation_time(self) -> 'DecofReal':
        return self._operation_time

    @property
    def pd(self) -> 'NloLaserHeadUvPhotoDiodes':
        return self._pd

    @property
    def crystal(self) -> 'UvCrystal':
        return self._crystal

    @property
    def status_parameters(self) -> 'UvStatusParameters':
        return self._status_parameters

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def error(self) -> 'DecofInteger':
        return self._error

    @property
    def power_optimization(self) -> 'UvShgPowerOptimization':
        return self._power_optimization

    @property
    def error_txt(self) -> 'DecofString':
        return self._error_txt

    @property
    def lock(self) -> 'NloLaserHeadLockShg1':
        return self._lock

    @property
    def power_margin(self) -> 'DecofReal':
        return self._power_margin

    @property
    def pump(self) -> 'Dpss1':
        return self._pump

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def ssw_ver(self) -> 'DecofString':
        return self._ssw_ver

    @property
    def scope(self) -> 'NloLaserHeadScopeT1':
        return self._scope

    @property
    def remaining_optics_spots(self) -> 'DecofInteger':
        return self._remaining_optics_spots

    @property
    def baseplate_temperature(self) -> 'DecofReal':
        return self._baseplate_temperature

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)

    async def clear_errors(self) -> None:
        await self.__client.exec(self.__name + ':clear-errors', input_stream=None, output_type=None, return_type=None)

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)

    async def perform_optimization(self) -> None:
        await self.__client.exec(self.__name + ':perform-optimization', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadSiggen1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._amplitude = DecofReal(client, name + ':amplitude')
        self._offset = DecofReal(client, name + ':offset')
        self._frequency = DecofReal(client, name + ':frequency')

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def amplitude(self) -> 'DecofReal':
        return self._amplitude

    @property
    def offset(self) -> 'DecofReal':
        return self._offset

    @property
    def frequency(self) -> 'DecofReal':
        return self._frequency


class UvShgPowerStabilization:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = PwrStabGain1(client, name + ':gain')
        self._power_max = DecofReal(client, name + ':power-max')
        self._power_act = DecofReal(client, name + ':power-act')
        self._state = DecofInteger(client, name + ':state')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._power_min = DecofReal(client, name + ':power-min')
        self._power_set = DecofReal(client, name + ':power-set')

    @property
    def gain(self) -> 'PwrStabGain1':
        return self._gain

    @property
    def power_max(self) -> 'DecofReal':
        return self._power_max

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def power_min(self) -> 'DecofReal':
        return self._power_min

    @property
    def power_set(self) -> 'DecofReal':
        return self._power_set


class PwrStabGain1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._d = DecofReal(client, name + ':d')
        self._i = DecofReal(client, name + ':i')
        self._p = DecofReal(client, name + ':p')
        self._all = DecofReal(client, name + ':all')

    @property
    def d(self) -> 'DecofReal':
        return self._d

    @property
    def i(self) -> 'DecofReal':
        return self._i

    @property
    def p(self) -> 'DecofReal':
        return self._p

    @property
    def all(self) -> 'DecofReal':
        return self._all


class UvFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pc = NloLaserHeadPcFactorySettings(client, name + ':pc')
        self._pd = NloLaserHeadUvPhotodiodesFactorySettings(client, name + ':pd')
        self._crystal_tc = NloLaserHeadTcFactorySettings(client, name + ':crystal-tc')
        self._modified = DecofBoolean(client, name + ':modified')
        self._cavity_tc = NloLaserHeadTcFactorySettings(client, name + ':cavity-tc')
        self._eom_tc = NloLaserHeadTcFactorySettings(client, name + ':eom-tc')
        self._lock = NloLaserHeadLockFactorySettings(client, name + ':lock')

    @property
    def pc(self) -> 'NloLaserHeadPcFactorySettings':
        return self._pc

    @property
    def pd(self) -> 'NloLaserHeadUvPhotodiodesFactorySettings':
        return self._pd

    @property
    def crystal_tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._crystal_tc

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def cavity_tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._cavity_tc

    @property
    def eom_tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._eom_tc

    @property
    def lock(self) -> 'NloLaserHeadLockFactorySettings':
        return self._lock

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadUvPhotodiodesFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shg = NloLaserHeadPdFactorySettings(client, name + ':shg')
        self._pdh_dc = NloLaserHeadPdDigilockFactorySettings(client, name + ':pdh-dc')
        self._pdh_rf = NloLaserHeadPdPdhFactorySettings(client, name + ':pdh-rf')

    @property
    def shg(self) -> 'NloLaserHeadPdFactorySettings':
        return self._shg

    @property
    def pdh_dc(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._pdh_dc

    @property
    def pdh_rf(self) -> 'NloLaserHeadPdPdhFactorySettings':
        return self._pdh_rf


class UvEom:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._tc = TcChannel1(client, name + ':tc')

    @property
    def tc(self) -> 'TcChannel1':
        return self._tc


class TcChannel1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._temp_set_min = DecofReal(client, name + ':temp-set-min')
        self._limits = TcChannelCheck1(client, name + ':limits')
        self._t_loop = TcChannelTLoop1(client, name + ':t-loop')
        self._current_set_max = DecofReal(client, name + ':current-set-max')
        self._drv_voltage = DecofReal(client, name + ':drv-voltage')
        self._current_set_min = DecofReal(client, name + ':current-set-min')
        self._power_source = DecofInteger(client, name + ':power-source')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._ntc_parallel_resistance = DecofReal(client, name + ':ntc-parallel-resistance')
        self._current_set = DecofReal(client, name + ':current-set')
        self._temp_act = DecofReal(client, name + ':temp-act')
        self._path = DecofString(client, name + ':path')
        self._ready = DecofBoolean(client, name + ':ready')
        self._status = DecofInteger(client, name + ':status')
        self._fault = DecofBoolean(client, name + ':fault')
        self._temp_set_max = DecofReal(client, name + ':temp-set-max')
        self._resistance = DecofReal(client, name + ':resistance')
        self._temp_set = DecofReal(client, name + ':temp-set')
        self._temp_roc_limit = DecofReal(client, name + ':temp-roc-limit')
        self._c_loop = TcChannelCLoop1(client, name + ':c-loop')
        self._ntc_series_resistance = DecofReal(client, name + ':ntc-series-resistance')
        self._temp_reset = DecofBoolean(client, name + ':temp-reset')
        self._temp_roc_enabled = DecofBoolean(client, name + ':temp-roc-enabled')
        self._current_act = DecofReal(client, name + ':current-act')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._external_input = ExtInput1(client, name + ':external-input')

    @property
    def temp_set_min(self) -> 'DecofReal':
        return self._temp_set_min

    @property
    def limits(self) -> 'TcChannelCheck1':
        return self._limits

    @property
    def t_loop(self) -> 'TcChannelTLoop1':
        return self._t_loop

    @property
    def current_set_max(self) -> 'DecofReal':
        return self._current_set_max

    @property
    def drv_voltage(self) -> 'DecofReal':
        return self._drv_voltage

    @property
    def current_set_min(self) -> 'DecofReal':
        return self._current_set_min

    @property
    def power_source(self) -> 'DecofInteger':
        return self._power_source

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def ntc_parallel_resistance(self) -> 'DecofReal':
        return self._ntc_parallel_resistance

    @property
    def current_set(self) -> 'DecofReal':
        return self._current_set

    @property
    def temp_act(self) -> 'DecofReal':
        return self._temp_act

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def ready(self) -> 'DecofBoolean':
        return self._ready

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def fault(self) -> 'DecofBoolean':
        return self._fault

    @property
    def temp_set_max(self) -> 'DecofReal':
        return self._temp_set_max

    @property
    def resistance(self) -> 'DecofReal':
        return self._resistance

    @property
    def temp_set(self) -> 'DecofReal':
        return self._temp_set

    @property
    def temp_roc_limit(self) -> 'DecofReal':
        return self._temp_roc_limit

    @property
    def c_loop(self) -> 'TcChannelCLoop1':
        return self._c_loop

    @property
    def ntc_series_resistance(self) -> 'DecofReal':
        return self._ntc_series_resistance

    @property
    def temp_reset(self) -> 'DecofBoolean':
        return self._temp_reset

    @property
    def temp_roc_enabled(self) -> 'DecofBoolean':
        return self._temp_roc_enabled

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def external_input(self) -> 'ExtInput1':
        return self._external_input


class TcChannelCheck1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._timed_out = DecofBoolean(client, name + ':timed-out')
        self._out_of_range = DecofBoolean(client, name + ':out-of-range')
        self._temp_min = DecofReal(client, name + ':temp-min')
        self._timeout = DecofInteger(client, name + ':timeout')
        self._temp_max = DecofReal(client, name + ':temp-max')

    @property
    def timed_out(self) -> 'DecofBoolean':
        return self._timed_out

    @property
    def out_of_range(self) -> 'DecofBoolean':
        return self._out_of_range

    @property
    def temp_min(self) -> 'DecofReal':
        return self._temp_min

    @property
    def timeout(self) -> 'DecofInteger':
        return self._timeout

    @property
    def temp_max(self) -> 'DecofReal':
        return self._temp_max


class TcChannelTLoop1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._on = DecofBoolean(client, name + ':on')
        self._ok_tolerance = DecofReal(client, name + ':ok-tolerance')
        self._p_gain = DecofReal(client, name + ':p-gain')
        self._ok_time = DecofReal(client, name + ':ok-time')
        self._i_gain = DecofReal(client, name + ':i-gain')
        self._d_gain = DecofReal(client, name + ':d-gain')

    @property
    def on(self) -> 'DecofBoolean':
        return self._on

    @property
    def ok_tolerance(self) -> 'DecofReal':
        return self._ok_tolerance

    @property
    def p_gain(self) -> 'DecofReal':
        return self._p_gain

    @property
    def ok_time(self) -> 'DecofReal':
        return self._ok_time

    @property
    def i_gain(self) -> 'DecofReal':
        return self._i_gain

    @property
    def d_gain(self) -> 'DecofReal':
        return self._d_gain


class TcChannelCLoop1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._on = DecofBoolean(client, name + ':on')
        self._i_gain = DecofReal(client, name + ':i-gain')

    @property
    def on(self) -> 'DecofBoolean':
        return self._on

    @property
    def i_gain(self) -> 'DecofReal':
        return self._i_gain


class ExtInput1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._factor = DecofReal(client, name + ':factor')
        self._signal = DecofInteger(client, name + ':signal')
        self._enabled = DecofBoolean(client, name + ':enabled')

    @property
    def factor(self) -> 'DecofReal':
        return self._factor

    @property
    def signal(self) -> 'DecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled


class NloLaserHeadUvServos:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shg1_hor = NloLaserHeadServoPwm1(client, name + ':shg1-hor')
        self._shg2_vert = NloLaserHeadServoPwm1(client, name + ':shg2-vert')
        self._outcpl = NloLaserHeadServoPwm1(client, name + ':outcpl')
        self._comp_vert = NloLaserHeadServoPwm1(client, name + ':comp-vert')
        self._comp_hor = NloLaserHeadServoPwm1(client, name + ':comp-hor')
        self._hwp = NloLaserHeadServoPwm1(client, name + ':hwp')
        self._shg1_vert = NloLaserHeadServoPwm1(client, name + ':shg1-vert')
        self._shg2_hor = NloLaserHeadServoPwm1(client, name + ':shg2-hor')
        self._lens = NloLaserHeadServoPwm1(client, name + ':lens')
        self._cryst = NloLaserHeadServoPwm1(client, name + ':cryst')

    @property
    def shg1_hor(self) -> 'NloLaserHeadServoPwm1':
        return self._shg1_hor

    @property
    def shg2_vert(self) -> 'NloLaserHeadServoPwm1':
        return self._shg2_vert

    @property
    def outcpl(self) -> 'NloLaserHeadServoPwm1':
        return self._outcpl

    @property
    def comp_vert(self) -> 'NloLaserHeadServoPwm1':
        return self._comp_vert

    @property
    def comp_hor(self) -> 'NloLaserHeadServoPwm1':
        return self._comp_hor

    @property
    def hwp(self) -> 'NloLaserHeadServoPwm1':
        return self._hwp

    @property
    def shg1_vert(self) -> 'NloLaserHeadServoPwm1':
        return self._shg1_vert

    @property
    def shg2_hor(self) -> 'NloLaserHeadServoPwm1':
        return self._shg2_hor

    @property
    def lens(self) -> 'NloLaserHeadServoPwm1':
        return self._lens

    @property
    def cryst(self) -> 'NloLaserHeadServoPwm1':
        return self._cryst


class NloLaserHeadServoPwm1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._display_name = DecofString(client, name + ':display-name')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._value = DecofInteger(client, name + ':value')

    @property
    def display_name(self) -> 'DecofString':
        return self._display_name

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def value(self) -> 'DecofInteger':
        return self._value


class UvCavity:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pc = PiezoDrv1(client, name + ':pc')
        self._tc = TcChannel1(client, name + ':tc')

    @property
    def pc(self) -> 'PiezoDrv1':
        return self._pc

    @property
    def tc(self) -> 'TcChannel1':
        return self._tc


class PiezoDrv1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._feedforward_factor = DecofReal(client, name + ':feedforward-factor')
        self._voltage_set_dithering = DecofBoolean(client, name + ':voltage-set-dithering')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._feedforward_master = DecofInteger(client, name + ':feedforward-master')
        self._voltage_max = DecofReal(client, name + ':voltage-max')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._feedforward_enabled = DecofBoolean(client, name + ':feedforward-enabled')
        self._path = DecofString(client, name + ':path')
        self._status = DecofInteger(client, name + ':status')
        self._voltage_min = DecofReal(client, name + ':voltage-min')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._output_filter = OutputFilter1(client, name + ':output-filter')
        self._external_input = ExtInput1(client, name + ':external-input')
        self._voltage_set = DecofReal(client, name + ':voltage-set')

    @property
    def feedforward_factor(self) -> 'DecofReal':
        return self._feedforward_factor

    @property
    def voltage_set_dithering(self) -> 'DecofBoolean':
        return self._voltage_set_dithering

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def feedforward_master(self) -> 'DecofInteger':
        return self._feedforward_master

    @property
    def voltage_max(self) -> 'DecofReal':
        return self._voltage_max

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def feedforward_enabled(self) -> 'DecofBoolean':
        return self._feedforward_enabled

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def voltage_min(self) -> 'DecofReal':
        return self._voltage_min

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def output_filter(self) -> 'OutputFilter1':
        return self._output_filter

    @property
    def external_input(self) -> 'ExtInput1':
        return self._external_input

    @property
    def voltage_set(self) -> 'DecofReal':
        return self._voltage_set


class OutputFilter1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._slew_rate = DecofReal(client, name + ':slew-rate')
        self._slew_rate_limited = DecofBoolean(client, name + ':slew-rate-limited')
        self._slew_rate_enabled = DecofBoolean(client, name + ':slew-rate-enabled')

    @property
    def slew_rate(self) -> 'DecofReal':
        return self._slew_rate

    @property
    def slew_rate_limited(self) -> 'DecofBoolean':
        return self._slew_rate_limited

    @property
    def slew_rate_enabled(self) -> 'DecofBoolean':
        return self._slew_rate_enabled


class NloLaserHeadUvPhotoDiodes:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._shg = NloLaserHeadNloPhotodiode1(client, name + ':shg')
        self._pdh_dc = NloLaserHeadNloDigilockPhotodiode1(client, name + ':pdh-dc')
        self._pdh_rf = NloLaserHeadNloPdhPhotodiode1(client, name + ':pdh-rf')

    @property
    def shg(self) -> 'NloLaserHeadNloPhotodiode1':
        return self._shg

    @property
    def pdh_dc(self) -> 'NloLaserHeadNloDigilockPhotodiode1':
        return self._pdh_dc

    @property
    def pdh_rf(self) -> 'NloLaserHeadNloPdhPhotodiode1':
        return self._pdh_rf


class NloLaserHeadNloPhotodiode1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_factor = DecofReal(client, name + ':cal-factor')
        self._power = DecofReal(client, name + ':power')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_offset = DecofReal(client, name + ':cal-offset')

    @property
    def cal_factor(self) -> 'DecofReal':
        return self._cal_factor

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_offset(self) -> 'DecofReal':
        return self._cal_offset


class NloLaserHeadNloDigilockPhotodiode1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_offset = DecofReal(client, name + ':cal-offset')
        self._photodiode = DecofReal(client, name + ':photodiode')

    @property
    def cal_offset(self) -> 'DecofReal':
        return self._cal_offset

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode


class NloLaserHeadNloPdhPhotodiode1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = DecofReal(client, name + ':gain')
        self._photodiode = DecofReal(client, name + ':photodiode')

    @property
    def gain(self) -> 'DecofReal':
        return self._gain

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode


class UvCrystal:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._optics_shifters = NloLaserHeadUvCrystalSpots(client, name + ':optics-shifters')
        self._tc = TcChannel1(client, name + ':tc')

    @property
    def optics_shifters(self) -> 'NloLaserHeadUvCrystalSpots':
        return self._optics_shifters

    @property
    def tc(self) -> 'TcChannel1':
        return self._tc


class NloLaserHeadUvCrystalSpots:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_spot = DecofInteger(client, name + ':current-spot')
        self._remaining_spots = DecofInteger(client, name + ':remaining-spots')

    @property
    def current_spot(self) -> 'DecofInteger':
        return self._current_spot

    @property
    def remaining_spots(self) -> 'DecofInteger':
        return self._remaining_spots


class UvStatusParameters:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_stabilization_level_low_factor = DecofReal(client, name + ':power-stabilization-level-low-factor')
        self._power_stabilization_strategy = DecofInteger(client, name + ':power-stabilization-strategy')
        self._baseplate_temperature_limit = DecofReal(client, name + ':baseplate-temperature-limit')
        self._operational_pump_power = DecofReal(client, name + ':operational-pump-power')
        self._cavity_lock_settle_time = DecofInteger(client, name + ':cavity-lock-settle-time')
        self._power_margin_threshold = DecofReal(client, name + ':power-margin-threshold')
        self._power_lock_settle_time = DecofInteger(client, name + ':power-lock-settle-time')
        self._power_margin_tolerance_time = DecofInteger(client, name + ':power-margin-tolerance-time')
        self._power_output_relative_deviation_max = DecofReal(client, name + ':power-output-relative-deviation-max')
        self._temperature_settle_time = DecofInteger(client, name + ':temperature-settle-time')
        self._pump_lock_settle_time = DecofInteger(client, name + ':pump-lock-settle-time')
        self._settle_down_delay = DecofInteger(client, name + ':settle-down-delay')
        self._cavity_scan_duration = DecofInteger(client, name + ':cavity-scan-duration')
        self._cavity_lock_tolerance_factor = DecofInteger(client, name + ':cavity-lock-tolerance-factor')
        self._power_output_relative_error_max = DecofReal(client, name + ':power-output-relative-error-max')

    @property
    def power_stabilization_level_low_factor(self) -> 'DecofReal':
        return self._power_stabilization_level_low_factor

    @property
    def power_stabilization_strategy(self) -> 'DecofInteger':
        return self._power_stabilization_strategy

    @property
    def baseplate_temperature_limit(self) -> 'DecofReal':
        return self._baseplate_temperature_limit

    @property
    def operational_pump_power(self) -> 'DecofReal':
        return self._operational_pump_power

    @property
    def cavity_lock_settle_time(self) -> 'DecofInteger':
        return self._cavity_lock_settle_time

    @property
    def power_margin_threshold(self) -> 'DecofReal':
        return self._power_margin_threshold

    @property
    def power_lock_settle_time(self) -> 'DecofInteger':
        return self._power_lock_settle_time

    @property
    def power_margin_tolerance_time(self) -> 'DecofInteger':
        return self._power_margin_tolerance_time

    @property
    def power_output_relative_deviation_max(self) -> 'DecofReal':
        return self._power_output_relative_deviation_max

    @property
    def temperature_settle_time(self) -> 'DecofInteger':
        return self._temperature_settle_time

    @property
    def pump_lock_settle_time(self) -> 'DecofInteger':
        return self._pump_lock_settle_time

    @property
    def settle_down_delay(self) -> 'DecofInteger':
        return self._settle_down_delay

    @property
    def cavity_scan_duration(self) -> 'DecofInteger':
        return self._cavity_scan_duration

    @property
    def cavity_lock_tolerance_factor(self) -> 'DecofInteger':
        return self._cavity_lock_tolerance_factor

    @property
    def power_output_relative_error_max(self) -> 'DecofReal':
        return self._power_output_relative_error_max


class UvShgPowerOptimization:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._status_string = DecofString(client, name + ':status-string')
        self._status = DecofInteger(client, name + ':status')
        self._progress_data = DecofBinary(client, name + ':progress-data')
        self._abort = DecofBoolean(client, name + ':abort')
        self._ongoing = DecofBoolean(client, name + ':ongoing')
        self._cavity = NloLaserHeadStage1(client, name + ':cavity')

    @property
    def status_string(self) -> 'DecofString':
        return self._status_string

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def progress_data(self) -> 'DecofBinary':
        return self._progress_data

    @property
    def abort(self) -> 'DecofBoolean':
        return self._abort

    @property
    def ongoing(self) -> 'DecofBoolean':
        return self._ongoing

    @property
    def cavity(self) -> 'NloLaserHeadStage1':
        return self._cavity


class NloLaserHeadStage1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._progress = DecofInteger(client, name + ':progress')
        self._restore_on_regress = DecofBoolean(client, name + ':restore-on-regress')
        self._optimization_in_progress = DecofBoolean(client, name + ':optimization-in-progress')
        self._regress_tolerance = DecofInteger(client, name + ':regress-tolerance')
        self._input = NloLaserHeadOptInput1(client, name + ':input')
        self._restore_on_abort = DecofBoolean(client, name + ':restore-on-abort')

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def restore_on_regress(self) -> 'DecofBoolean':
        return self._restore_on_regress

    @property
    def optimization_in_progress(self) -> 'DecofBoolean':
        return self._optimization_in_progress

    @property
    def regress_tolerance(self) -> 'DecofInteger':
        return self._regress_tolerance

    @property
    def input(self) -> 'NloLaserHeadOptInput1':
        return self._input

    @property
    def restore_on_abort(self) -> 'DecofBoolean':
        return self._restore_on_abort


class NloLaserHeadOptInput1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._value_calibrated = DecofReal(client, name + ':value-calibrated')

    @property
    def value_calibrated(self) -> 'DecofReal':
        return self._value_calibrated


class NloLaserHeadLockShg1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._setpoint = DecofReal(client, name + ':setpoint')
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._pid2 = NloLaserHeadPid1(client, name + ':pid2')
        self._pid_selection = DecofInteger(client, name + ':pid-selection')
        self._window = NloLaserHeadWindow1(client, name + ':window')
        self._cavity_slow_pzt_voltage = DecofReal(client, name + ':cavity-slow-pzt-voltage')
        self._pid1 = NloLaserHeadPid1(client, name + ':pid1')
        self._state = DecofInteger(client, name + ':state')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._relock = NloLaserHeadRelock1(client, name + ':relock')
        self._local_oscillator = NloLaserHeadLocalOscillatorShg1(client, name + ':local-oscillator')
        self._analog_dl_gain = NloLaserHeadMinifalc1(client, name + ':analog-dl-gain')
        self._lock_enabled = DecofBoolean(client, name + ':lock-enabled')
        self._cavity_fast_pzt_voltage = DecofReal(client, name + ':cavity-fast-pzt-voltage')

    @property
    def setpoint(self) -> 'DecofReal':
        return self._setpoint

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def pid2(self) -> 'NloLaserHeadPid1':
        return self._pid2

    @property
    def pid_selection(self) -> 'DecofInteger':
        return self._pid_selection

    @property
    def window(self) -> 'NloLaserHeadWindow1':
        return self._window

    @property
    def cavity_slow_pzt_voltage(self) -> 'DecofReal':
        return self._cavity_slow_pzt_voltage

    @property
    def pid1(self) -> 'NloLaserHeadPid1':
        return self._pid1

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def relock(self) -> 'NloLaserHeadRelock1':
        return self._relock

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorShg1':
        return self._local_oscillator

    @property
    def analog_dl_gain(self) -> 'NloLaserHeadMinifalc1':
        return self._analog_dl_gain

    @property
    def lock_enabled(self) -> 'DecofBoolean':
        return self._lock_enabled

    @property
    def cavity_fast_pzt_voltage(self) -> 'DecofReal':
        return self._cavity_fast_pzt_voltage


class NloLaserHeadPid1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = NloLaserHeadGain1(client, name + ':gain')

    @property
    def gain(self) -> 'NloLaserHeadGain1':
        return self._gain


class NloLaserHeadGain1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_cutoff = DecofReal(client, name + ':i-cutoff')
        self._i_cutoff_enabled = DecofBoolean(client, name + ':i-cutoff-enabled')
        self._i = DecofReal(client, name + ':i')
        self._d = DecofReal(client, name + ':d')
        self._p = DecofReal(client, name + ':p')
        self._all = DecofReal(client, name + ':all')

    @property
    def i_cutoff(self) -> 'DecofReal':
        return self._i_cutoff

    @property
    def i_cutoff_enabled(self) -> 'DecofBoolean':
        return self._i_cutoff_enabled

    @property
    def i(self) -> 'DecofReal':
        return self._i

    @property
    def d(self) -> 'DecofReal':
        return self._d

    @property
    def p(self) -> 'DecofReal':
        return self._p

    @property
    def all(self) -> 'DecofReal':
        return self._all


class NloLaserHeadWindow1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_hysteresis = DecofReal(client, name + ':level-hysteresis')
        self._input_channel = DecofInteger(client, name + ':input-channel')
        self._threshold = DecofReal(client, name + ':threshold')
        self._calibration = NloLaserHeadWindowCalibration1(client, name + ':calibration')

    @property
    def level_hysteresis(self) -> 'DecofReal':
        return self._level_hysteresis

    @property
    def input_channel(self) -> 'DecofInteger':
        return self._input_channel

    @property
    def threshold(self) -> 'DecofReal':
        return self._threshold

    @property
    def calibration(self) -> 'NloLaserHeadWindowCalibration1':
        return self._calibration


class NloLaserHeadWindowCalibration1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name


class NloLaserHeadRelock1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._amplitude = DecofReal(client, name + ':amplitude')
        self._delay = DecofReal(client, name + ':delay')
        self._frequency = DecofReal(client, name + ':frequency')

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def amplitude(self) -> 'DecofReal':
        return self._amplitude

    @property
    def delay(self) -> 'DecofReal':
        return self._delay

    @property
    def frequency(self) -> 'DecofReal':
        return self._frequency


class NloLaserHeadLocalOscillatorShg1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._use_fast_oscillator = DecofBoolean(client, name + ':use-fast-oscillator')
        self._coupled_modulation = DecofBoolean(client, name + ':coupled-modulation')
        self._amplitude = DecofReal(client, name + ':amplitude')
        self._phase_shift = DecofReal(client, name + ':phase-shift')
        self._use_external_oscillator = DecofBoolean(client, name + ':use-external-oscillator')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._attenuation_raw = DecofInteger(client, name + ':attenuation-raw')

    @property
    def use_fast_oscillator(self) -> 'DecofBoolean':
        return self._use_fast_oscillator

    @property
    def coupled_modulation(self) -> 'DecofBoolean':
        return self._coupled_modulation

    @property
    def amplitude(self) -> 'DecofReal':
        return self._amplitude

    @property
    def phase_shift(self) -> 'DecofReal':
        return self._phase_shift

    @property
    def use_external_oscillator(self) -> 'DecofBoolean':
        return self._use_external_oscillator

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def attenuation_raw(self) -> 'DecofInteger':
        return self._attenuation_raw


class NloLaserHeadMinifalc1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._p_gain = DecofReal(client, name + ':p-gain')

    @property
    def p_gain(self) -> 'DecofReal':
        return self._p_gain


class Dpss1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_act = DecofReal(client, name + ':power-act')
        self._error_code = DecofInteger(client, name + ':error-code')
        self._status = DecofInteger(client, name + ':status')
        self._current_max = DecofReal(client, name + ':current-max')
        self._operation_time = DecofReal(client, name + ':operation-time')
        self._power_max = DecofReal(client, name + ':power-max')
        self._current_act = DecofReal(client, name + ':current-act')
        self._tc_status_txt = DecofString(client, name + ':tc-status-txt')
        self._tc_status = DecofInteger(client, name + ':tc-status')
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._power_margin = DecofReal(client, name + ':power-margin')
        self._power_set = DecofReal(client, name + ':power-set')
        self._error_txt = DecofString(client, name + ':error-txt')

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act

    @property
    def error_code(self) -> 'DecofInteger':
        return self._error_code

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def current_max(self) -> 'DecofReal':
        return self._current_max

    @property
    def operation_time(self) -> 'DecofReal':
        return self._operation_time

    @property
    def power_max(self) -> 'DecofReal':
        return self._power_max

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def tc_status_txt(self) -> 'DecofString':
        return self._tc_status_txt

    @property
    def tc_status(self) -> 'DecofInteger':
        return self._tc_status

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def power_margin(self) -> 'DecofReal':
        return self._power_margin

    @property
    def power_set(self) -> 'DecofReal':
        return self._power_set

    @property
    def error_txt(self) -> 'DecofString':
        return self._error_txt


class NloLaserHeadScopeT1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._timescale = DecofReal(client, name + ':timescale')
        self._update_rate = DecofInteger(client, name + ':update-rate')
        self._channel2 = NloLaserHeadScopeChannelT1(client, name + ':channel2')
        self._channelx = NloLaserHeadScopeXAxisT1(client, name + ':channelx')
        self._data = DecofBinary(client, name + ':data')
        self._channel1 = NloLaserHeadScopeChannelT1(client, name + ':channel1')
        self._variant = DecofInteger(client, name + ':variant')

    @property
    def timescale(self) -> 'DecofReal':
        return self._timescale

    @property
    def update_rate(self) -> 'DecofInteger':
        return self._update_rate

    @property
    def channel2(self) -> 'NloLaserHeadScopeChannelT1':
        return self._channel2

    @property
    def channelx(self) -> 'NloLaserHeadScopeXAxisT1':
        return self._channelx

    @property
    def data(self) -> 'DecofBinary':
        return self._data

    @property
    def channel1(self) -> 'NloLaserHeadScopeChannelT1':
        return self._channel1

    @property
    def variant(self) -> 'DecofInteger':
        return self._variant


class NloLaserHeadScopeChannelT1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = DecofInteger(client, name + ':signal')
        self._unit = DecofString(client, name + ':unit')
        self._name = DecofString(client, name + ':name')
        self._enabled = DecofBoolean(client, name + ':enabled')

    @property
    def signal(self) -> 'DecofInteger':
        return self._signal

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled


class NloLaserHeadScopeXAxisT1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._spectrum_omit_dc = DecofBoolean(client, name + ':spectrum-omit-dc')
        self._unit = DecofString(client, name + ':unit')
        self._scope_timescale = DecofReal(client, name + ':scope-timescale')
        self._spectrum_range = DecofReal(client, name + ':spectrum-range')
        self._xy_signal = DecofInteger(client, name + ':xy-signal')
        self._name = DecofString(client, name + ':name')

    @property
    def spectrum_omit_dc(self) -> 'DecofBoolean':
        return self._spectrum_omit_dc

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def scope_timescale(self) -> 'DecofReal':
        return self._scope_timescale

    @property
    def spectrum_range(self) -> 'DecofReal':
        return self._spectrum_range

    @property
    def xy_signal(self) -> 'DecofInteger':
        return self._xy_signal

    @property
    def name(self) -> 'DecofString':
        return self._name


class Recorder:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._sampling_interval = DecofReal(client, name + ':sampling-interval')
        self._state = DecofInteger(client, name + ':state')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._signals = RecorderInputs(client, name + ':signals')
        self._sample_count_set = MutableDecofInteger(client, name + ':sample-count-set')
        self._sample_count = DecofInteger(client, name + ':sample-count')
        self._data = RecorderData(client, name + ':data')
        self._recording_time = MutableDecofReal(client, name + ':recording-time')

    @property
    def sampling_interval(self) -> 'DecofReal':
        return self._sampling_interval

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def signals(self) -> 'RecorderInputs':
        return self._signals

    @property
    def sample_count_set(self) -> 'MutableDecofInteger':
        return self._sample_count_set

    @property
    def sample_count(self) -> 'DecofInteger':
        return self._sample_count

    @property
    def data(self) -> 'RecorderData':
        return self._data

    @property
    def recording_time(self) -> 'MutableDecofReal':
        return self._recording_time


class RecorderInputs:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channel1 = MutableDecofInteger(client, name + ':channel1')
        self._channelx = MutableDecofInteger(client, name + ':channelx')
        self._channel2 = MutableDecofInteger(client, name + ':channel2')

    @property
    def channel1(self) -> 'MutableDecofInteger':
        return self._channel1

    @property
    def channelx(self) -> 'MutableDecofInteger':
        return self._channelx

    @property
    def channel2(self) -> 'MutableDecofInteger':
        return self._channel2


class RecorderData:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._zoom_amplitude = MutableDecofReal(client, name + ':zoom-amplitude')
        self._channelx = RecorderChannel(client, name + ':channelx')
        self._zoom_data = DecofBinary(client, name + ':zoom-data')
        self._zoom_offset = MutableDecofReal(client, name + ':zoom-offset')
        self._recorded_sample_count = DecofInteger(client, name + ':recorded-sample-count')
        self._channel1 = RecorderChannel(client, name + ':channel1')
        self._channel2 = RecorderChannel(client, name + ':channel2')

    @property
    def zoom_amplitude(self) -> 'MutableDecofReal':
        return self._zoom_amplitude

    @property
    def channelx(self) -> 'RecorderChannel':
        return self._channelx

    @property
    def zoom_data(self) -> 'DecofBinary':
        return self._zoom_data

    @property
    def zoom_offset(self) -> 'MutableDecofReal':
        return self._zoom_offset

    @property
    def recorded_sample_count(self) -> 'DecofInteger':
        return self._recorded_sample_count

    @property
    def channel1(self) -> 'RecorderChannel':
        return self._channel1

    @property
    def channel2(self) -> 'RecorderChannel':
        return self._channel2

    async def get_data(self, start_index: int, count: int) -> bytes:
        assert isinstance(start_index, int), "expected type 'int' for parameter 'start_index', got '{}'".format(type(start_index))
        assert isinstance(count, int), "expected type 'int' for parameter 'count', got '{}'".format(type(count))
        return await self.__client.exec(self.__name + ':get-data', start_index, count, input_stream=None, output_type=None, return_type=bytes)

    async def zoom_out(self) -> None:
        await self.__client.exec(self.__name + ':zoom-out', input_stream=None, output_type=None, return_type=None)

    async def show_data(self, start_index: int, count: int) -> None:
        assert isinstance(start_index, int), "expected type 'int' for parameter 'start_index', got '{}'".format(type(start_index))
        assert isinstance(count, int), "expected type 'int' for parameter 'count', got '{}'".format(type(count))
        await self.__client.exec(self.__name + ':show-data', start_index, count, input_stream=None, output_type=None, return_type=None)


class RecorderChannel:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = DecofInteger(client, name + ':signal')
        self._unit = DecofString(client, name + ':unit')
        self._name = DecofString(client, name + ':name')

    @property
    def signal(self) -> 'DecofInteger':
        return self._signal

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def name(self) -> 'DecofString':
        return self._name


class LaserHead:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._type_ = DecofString(client, name + ':type')
        self._pc = PiezoDrv2(client, name + ':pc')
        self._version = DecofString(client, name + ':version')
        self._factory_settings = LhFactory(client, name + ':factory-settings')
        self._pressure_compensation = PressureCompensation(client, name + ':pressure-compensation')
        self._lock = Lock(client, name + ':lock')
        self._cc = CurrDrv1(client, name + ':cc')
        self._tc = TcChannel2(client, name + ':tc')
        self._ontime = DecofInteger(client, name + ':ontime')
        self._pd = PdCal(client, name + ':pd')
        self._ontime_txt = DecofString(client, name + ':ontime-txt')
        self._legacy = DecofBoolean(client, name + ':legacy')
        self._model = DecofString(client, name + ':model')
        self._serial_number = DecofString(client, name + ':serial-number')

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def pc(self) -> 'PiezoDrv2':
        return self._pc

    @property
    def version(self) -> 'DecofString':
        return self._version

    @property
    def factory_settings(self) -> 'LhFactory':
        return self._factory_settings

    @property
    def pressure_compensation(self) -> 'PressureCompensation':
        return self._pressure_compensation

    @property
    def lock(self) -> 'Lock':
        return self._lock

    @property
    def cc(self) -> 'CurrDrv1':
        return self._cc

    @property
    def tc(self) -> 'TcChannel2':
        return self._tc

    @property
    def ontime(self) -> 'DecofInteger':
        return self._ontime

    @property
    def pd(self) -> 'PdCal':
        return self._pd

    @property
    def ontime_txt(self) -> 'DecofString':
        return self._ontime_txt

    @property
    def legacy(self) -> 'DecofBoolean':
        return self._legacy

    @property
    def model(self) -> 'DecofString':
        return self._model

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)


class LhFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cc = LhFactoryCc(client, name + ':cc')
        self._wavelength = MutableDecofReal(client, name + ':wavelength')
        self._power = MutableDecofReal(client, name + ':power')
        self._last_modified = DecofString(client, name + ':last-modified')
        self._pd = LhFactoryPd(client, name + ':pd')
        self._modified = DecofBoolean(client, name + ':modified')
        self._threshold_current = MutableDecofReal(client, name + ':threshold-current')
        self._pc = PcFactorySettings(client, name + ':pc')
        self._tc = TcFactorySettings(client, name + ':tc')

    @property
    def cc(self) -> 'LhFactoryCc':
        return self._cc

    @property
    def wavelength(self) -> 'MutableDecofReal':
        return self._wavelength

    @property
    def power(self) -> 'MutableDecofReal':
        return self._power

    @property
    def last_modified(self) -> 'DecofString':
        return self._last_modified

    @property
    def pd(self) -> 'LhFactoryPd':
        return self._pd

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def threshold_current(self) -> 'MutableDecofReal':
        return self._threshold_current

    @property
    def pc(self) -> 'PcFactorySettings':
        return self._pc

    @property
    def tc(self) -> 'TcFactorySettings':
        return self._tc

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class LhFactoryCc:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._current_clip_modified = DecofBoolean(client, name + ':current-clip-modified')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._current_clip_last_modified = DecofString(client, name + ':current-clip-last-modified')

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def current_clip_modified(self) -> 'DecofBoolean':
        return self._current_clip_modified

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def current_clip_last_modified(self) -> 'DecofString':
        return self._current_clip_last_modified


class LhFactoryPd:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class PcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._scan_amplitude = MutableDecofReal(client, name + ':scan-amplitude')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._slew_rate = MutableDecofReal(client, name + ':slew-rate')
        self._scan_offset = MutableDecofReal(client, name + ':scan-offset')
        self._slew_rate_enabled = MutableDecofBoolean(client, name + ':slew-rate-enabled')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._capacitance = MutableDecofReal(client, name + ':capacitance')
        self._pressure_compensation_factor = MutableDecofReal(client, name + ':pressure-compensation-factor')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def scan_amplitude(self) -> 'MutableDecofReal':
        return self._scan_amplitude

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def slew_rate(self) -> 'MutableDecofReal':
        return self._slew_rate

    @property
    def scan_offset(self) -> 'MutableDecofReal':
        return self._scan_offset

    @property
    def slew_rate_enabled(self) -> 'MutableDecofBoolean':
        return self._slew_rate_enabled

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def capacitance(self) -> 'MutableDecofReal':
        return self._capacitance

    @property
    def pressure_compensation_factor(self) -> 'MutableDecofReal':
        return self._pressure_compensation_factor

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max


class PressureCompensation:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._factor = MutableDecofReal(client, name + ':factor')
        self._compensation_voltage = DecofReal(client, name + ':compensation-voltage')
        self._air_pressure = DecofReal(client, name + ':air-pressure')
        self._offset = DecofReal(client, name + ':offset')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor

    @property
    def compensation_voltage(self) -> 'DecofReal':
        return self._compensation_voltage

    @property
    def air_pressure(self) -> 'DecofReal':
        return self._air_pressure

    @property
    def offset(self) -> 'DecofReal':
        return self._offset

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class Lock:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._lock_tracking = Coordinate(client, name + ':lock-tracking')
        self._candidate_filter = AlCandidateFilter(client, name + ':candidate-filter')
        self._background_trace = DecofBinary(client, name + ':background-trace')
        self._type_ = MutableDecofInteger(client, name + ':type')
        self._pid2 = Pid(client, name + ':pid2')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._lockin = Lockin(client, name + ':lockin')
        self._candidates = DecofBinary(client, name + ':candidates')
        self._locking_delay = MutableDecofInteger(client, name + ':locking-delay')
        self._reset = AlReset(client, name + ':reset')
        self._pid1 = Pid(client, name + ':pid1')
        self._state = DecofInteger(client, name + ':state')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._relock = AlRelock(client, name + ':relock')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._lockpoint = AlLockpoint(client, name + ':lockpoint')
        self._window = AlWindow(client, name + ':window')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._lock_without_lockpoint = MutableDecofBoolean(client, name + ':lock-without-lockpoint')
        self._spectrum_input_channel = MutableDecofInteger(client, name + ':spectrum-input-channel')

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def lock_tracking(self) -> 'Coordinate':
        return self._lock_tracking

    @property
    def candidate_filter(self) -> 'AlCandidateFilter':
        return self._candidate_filter

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    @property
    def type_(self) -> 'MutableDecofInteger':
        return self._type_

    @property
    def pid2(self) -> 'Pid':
        return self._pid2

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def lockin(self) -> 'Lockin':
        return self._lockin

    @property
    def candidates(self) -> 'DecofBinary':
        return self._candidates

    @property
    def locking_delay(self) -> 'MutableDecofInteger':
        return self._locking_delay

    @property
    def reset(self) -> 'AlReset':
        return self._reset

    @property
    def pid1(self) -> 'Pid':
        return self._pid1

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def relock(self) -> 'AlRelock':
        return self._relock

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def lockpoint(self) -> 'AlLockpoint':
        return self._lockpoint

    @property
    def window(self) -> 'AlWindow':
        return self._window

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def lock_without_lockpoint(self) -> 'MutableDecofBoolean':
        return self._lock_without_lockpoint

    @property
    def spectrum_input_channel(self) -> 'MutableDecofInteger':
        return self._spectrum_input_channel

    async def show_candidates(self) -> Tuple[str, int]:
        return await self.__client.exec(self.__name + ':show-candidates', input_stream=None, output_type=str, return_type=int)

    async def select_lockpoint(self, x: float, y: float, type_: int) -> None:
        assert isinstance(x, float), "expected type 'float' for parameter 'x', got '{}'".format(type(x))
        assert isinstance(y, float), "expected type 'float' for parameter 'y', got '{}'".format(type(y))
        assert isinstance(type_, int), "expected type 'int' for parameter 'type_', got '{}'".format(type(type_))
        await self.__client.exec(self.__name + ':select-lockpoint', x, y, type_, input_stream=None, output_type=None, return_type=None)

    async def open(self) -> None:
        await self.__client.exec(self.__name + ':open', input_stream=None, output_type=None, return_type=None)

    async def find_candidates(self) -> None:
        await self.__client.exec(self.__name + ':find-candidates', input_stream=None, output_type=None, return_type=None)

    async def close(self) -> None:
        await self.__client.exec(self.__name + ':close', input_stream=None, output_type=None, return_type=None)


class Coordinate:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name

    async def get(self) -> Tuple[float, float]:
        return await self.__client.get(self.__name)

    async def set(self, x: float, y: float) -> None:
        assert isinstance(x, float), "expected type 'float' for 'x', got '{}'".format(type(x))
        assert isinstance(y, float), "expected type 'float' for 'y', got '{}'".format(type(y))
        await self.__client.set(self.__name, x, y)


class AlCandidateFilter:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._bottom = MutableDecofBoolean(client, name + ':bottom')
        self._edge_min_distance = MutableDecofInteger(client, name + ':edge-min-distance')
        self._top = MutableDecofBoolean(client, name + ':top')
        self._negative_edge = MutableDecofBoolean(client, name + ':negative-edge')
        self._edge_level = MutableDecofReal(client, name + ':edge-level')
        self._positive_edge = MutableDecofBoolean(client, name + ':positive-edge')
        self._peak_noise_tolerance = MutableDecofReal(client, name + ':peak-noise-tolerance')

    @property
    def bottom(self) -> 'MutableDecofBoolean':
        return self._bottom

    @property
    def edge_min_distance(self) -> 'MutableDecofInteger':
        return self._edge_min_distance

    @property
    def top(self) -> 'MutableDecofBoolean':
        return self._top

    @property
    def negative_edge(self) -> 'MutableDecofBoolean':
        return self._negative_edge

    @property
    def edge_level(self) -> 'MutableDecofReal':
        return self._edge_level

    @property
    def positive_edge(self) -> 'MutableDecofBoolean':
        return self._positive_edge

    @property
    def peak_noise_tolerance(self) -> 'MutableDecofReal':
        return self._peak_noise_tolerance


class Pid:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._lock_state = DecofBoolean(client, name + ':lock-state')
        self._gain = Gain(client, name + ':gain')
        self._regulating_state = DecofBoolean(client, name + ':regulating-state')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._hold_output_on_unlock = MutableDecofBoolean(client, name + ':hold-output-on-unlock')
        self._outputlimit = Outputlimit(client, name + ':outputlimit')
        self._slope = MutableDecofBoolean(client, name + ':slope')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._sign = MutableDecofBoolean(client, name + ':sign')
        self._hold_state = DecofBoolean(client, name + ':hold-state')

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def lock_state(self) -> 'DecofBoolean':
        return self._lock_state

    @property
    def gain(self) -> 'Gain':
        return self._gain

    @property
    def regulating_state(self) -> 'DecofBoolean':
        return self._regulating_state

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def hold_output_on_unlock(self) -> 'MutableDecofBoolean':
        return self._hold_output_on_unlock

    @property
    def outputlimit(self) -> 'Outputlimit':
        return self._outputlimit

    @property
    def slope(self) -> 'MutableDecofBoolean':
        return self._slope

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def sign(self) -> 'MutableDecofBoolean':
        return self._sign

    @property
    def hold_state(self) -> 'DecofBoolean':
        return self._hold_state


class Gain:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._fc_pd = DecofReal(client, name + ':fc-pd')
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')
        self._d = MutableDecofReal(client, name + ':d')
        self._p = MutableDecofReal(client, name + ':p')
        self._fc_ip = DecofReal(client, name + ':fc-ip')
        self._i = MutableDecofReal(client, name + ':i')
        self._all = MutableDecofReal(client, name + ':all')

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def fc_pd(self) -> 'DecofReal':
        return self._fc_pd

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def fc_ip(self) -> 'DecofReal':
        return self._fc_ip

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all


class Outputlimit:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._max = MutableDecofReal(client, name + ':max')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def max(self) -> 'MutableDecofReal':
        return self._max

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class Lockin:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._modulation_enabled = MutableDecofBoolean(client, name + ':modulation-enabled')
        self._lock_level = MutableDecofReal(client, name + ':lock-level')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._auto_lir = AutoLir(client, name + ':auto-lir')
        self._modulation_output_channel = MutableDecofInteger(client, name + ':modulation-output-channel')
        self._frequency = MutableDecofReal(client, name + ':frequency')

    @property
    def modulation_enabled(self) -> 'MutableDecofBoolean':
        return self._modulation_enabled

    @property
    def lock_level(self) -> 'MutableDecofReal':
        return self._lock_level

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def auto_lir(self) -> 'AutoLir':
        return self._auto_lir

    @property
    def modulation_output_channel(self) -> 'MutableDecofInteger':
        return self._modulation_output_channel

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency


class AutoLir:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._progress = DecofInteger(client, name + ':progress')

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    async def auto_lir(self) -> None:
        await self.__client.exec(self.__name + ':auto-lir', input_stream=None, output_type=None, return_type=None)


class AlReset:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class AlRelock:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._delay = MutableDecofReal(client, name + ':delay')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def delay(self) -> 'MutableDecofReal':
        return self._delay

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class AlLockpoint:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._type_ = DecofString(client, name + ':type')
        self._position = Coordinate(client, name + ':position')

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def position(self) -> 'Coordinate':
        return self._position


class AlWindow:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_high = MutableDecofReal(client, name + ':level-high')
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')
        self._level_low = MutableDecofReal(client, name + ':level-low')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def level_high(self) -> 'MutableDecofReal':
        return self._level_high

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis

    @property
    def level_low(self) -> 'MutableDecofReal':
        return self._level_low

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class CurrDrv1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._current_set_dithering = MutableDecofBoolean(client, name + ':current-set-dithering')
        self._emission = DecofBoolean(client, name + ':emission')
        self._pd = DecofReal(client, name + ':pd')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._variant = DecofString(client, name + ':variant')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._path = DecofString(client, name + ':path')
        self._status = DecofInteger(client, name + ':status')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._aux = DecofReal(client, name + ':aux')
        self._external_input = ExtInput2(client, name + ':external-input')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._current_act = DecofReal(client, name + ':current-act')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def current_set_dithering(self) -> 'MutableDecofBoolean':
        return self._current_set_dithering

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def pd(self) -> 'DecofReal':
        return self._pd

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit


class PdCal:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._power = DecofReal(client, name + ':power')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._photodiode = DecofReal(client, name + ':photodiode')

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode


class ScopeT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._timescale = MutableDecofReal(client, name + ':timescale')
        self._update_rate = MutableDecofInteger(client, name + ':update-rate')
        self._channel2 = ScopeChannelT(client, name + ':channel2')
        self._channelx = ScopeXAxisT(client, name + ':channelx')
        self._data = DecofBinary(client, name + ':data')
        self._channel1 = ScopeChannelT(client, name + ':channel1')
        self._variant = MutableDecofInteger(client, name + ':variant')

    @property
    def timescale(self) -> 'MutableDecofReal':
        return self._timescale

    @property
    def update_rate(self) -> 'MutableDecofInteger':
        return self._update_rate

    @property
    def channel2(self) -> 'ScopeChannelT':
        return self._channel2

    @property
    def channelx(self) -> 'ScopeXAxisT':
        return self._channelx

    @property
    def data(self) -> 'DecofBinary':
        return self._data

    @property
    def channel1(self) -> 'ScopeChannelT':
        return self._channel1

    @property
    def variant(self) -> 'MutableDecofInteger':
        return self._variant


class ScopeChannelT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._unit = DecofString(client, name + ':unit')
        self._name = DecofString(client, name + ':name')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def name(self) -> 'DecofString':
        return self._name

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class ScopeXAxisT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._spectrum_omit_dc = MutableDecofBoolean(client, name + ':spectrum-omit-dc')
        self._unit = DecofString(client, name + ':unit')
        self._scope_timescale = MutableDecofReal(client, name + ':scope-timescale')
        self._spectrum_range = MutableDecofReal(client, name + ':spectrum-range')
        self._xy_signal = MutableDecofInteger(client, name + ':xy-signal')
        self._name = DecofString(client, name + ':name')

    @property
    def spectrum_omit_dc(self) -> 'MutableDecofBoolean':
        return self._spectrum_omit_dc

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def scope_timescale(self) -> 'MutableDecofReal':
        return self._scope_timescale

    @property
    def spectrum_range(self) -> 'MutableDecofReal':
        return self._spectrum_range

    @property
    def xy_signal(self) -> 'MutableDecofInteger':
        return self._xy_signal

    @property
    def name(self) -> 'DecofString':
        return self._name


class Display:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._brightness = MutableDecofReal(client, name + ':brightness')
        self._auto_dark = MutableDecofBoolean(client, name + ':auto-dark')
        self._idle_timeout = MutableDecofInteger(client, name + ':idle-timeout')
        self._state = DecofInteger(client, name + ':state')

    @property
    def brightness(self) -> 'MutableDecofReal':
        return self._brightness

    @property
    def auto_dark(self) -> 'MutableDecofBoolean':
        return self._auto_dark

    @property
    def idle_timeout(self) -> 'MutableDecofInteger':
        return self._idle_timeout

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    async def update_state(self, active: bool) -> None:
        assert isinstance(active, bool), "expected type 'bool' for parameter 'active', got '{}'".format(type(active))
        await self.__client.exec(self.__name + ':update-state', active, input_stream=None, output_type=None, return_type=None)


class Cc5000Board:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._revision = DecofString(client, name + ':revision')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._inverter_temp_fuse = DecofReal(client, name + ':inverter-temp-fuse')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._inverter_temp = DecofReal(client, name + ':inverter-temp')
        self._power_15v = MutableDecofBoolean(client, name + ':power-15v')
        self._regulator_temp = DecofReal(client, name + ':regulator-temp')
        self._channel1 = Cc5000Drv(client, name + ':channel1')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._slot = DecofString(client, name + ':slot')
        self._parallel_mode = DecofBoolean(client, name + ':parallel-mode')
        self._regulator_temp_fuse = DecofReal(client, name + ':regulator-temp-fuse')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._variant = DecofString(client, name + ':variant')
        self._status = DecofInteger(client, name + ':status')

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def inverter_temp_fuse(self) -> 'DecofReal':
        return self._inverter_temp_fuse

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def inverter_temp(self) -> 'DecofReal':
        return self._inverter_temp

    @property
    def power_15v(self) -> 'MutableDecofBoolean':
        return self._power_15v

    @property
    def regulator_temp(self) -> 'DecofReal':
        return self._regulator_temp

    @property
    def channel1(self) -> 'Cc5000Drv':
        return self._channel1

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def parallel_mode(self) -> 'DecofBoolean':
        return self._parallel_mode

    @property
    def regulator_temp_fuse(self) -> 'DecofReal':
        return self._regulator_temp_fuse

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def status(self) -> 'DecofInteger':
        return self._status


class CcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._status = DecofInteger(client, name + ':status')
        self._revision = DecofString(client, name + ':revision')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._channel1 = CurrDrv2(client, name + ':channel1')
        self._channel2 = CurrDrv2(client, name + ':channel2')
        self._parallel_mode = DecofBoolean(client, name + ':parallel-mode')
        self._slot = DecofString(client, name + ':slot')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._variant = DecofString(client, name + ':variant')

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def channel1(self) -> 'CurrDrv2':
        return self._channel1

    @property
    def channel2(self) -> 'CurrDrv2':
        return self._channel2

    @property
    def parallel_mode(self) -> 'DecofBoolean':
        return self._parallel_mode

    @property
    def slot(self) -> 'DecofString':
        return self._slot

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def variant(self) -> 'DecofString':
        return self._variant


class CurrDrv2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._current_set_dithering = MutableDecofBoolean(client, name + ':current-set-dithering')
        self._emission = DecofBoolean(client, name + ':emission')
        self._pd = DecofReal(client, name + ':pd')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._variant = DecofString(client, name + ':variant')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._path = DecofString(client, name + ':path')
        self._status = DecofInteger(client, name + ':status')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._aux = DecofReal(client, name + ':aux')
        self._external_input = ExtInput3(client, name + ':external-input')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._current_act = DecofReal(client, name + ':current-act')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._output_filter = OutputFilter3(client, name + ':output-filter')
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def current_set_dithering(self) -> 'MutableDecofBoolean':
        return self._current_set_dithering

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def pd(self) -> 'DecofReal':
        return self._pd

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def external_input(self) -> 'ExtInput3':
        return self._external_input

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def output_filter(self) -> 'OutputFilter3':
        return self._output_filter

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit


class McBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fpga_fw_ver = DecofString(client, name + ':fpga-fw-ver')
        self._revision = DecofString(client, name + ':revision')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._relative_humidity = DecofReal(client, name + ':relative-humidity')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._air_pressure = DecofReal(client, name + ':air-pressure')

    @property
    def fpga_fw_ver(self) -> 'DecofString':
        return self._fpga_fw_ver

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def relative_humidity(self) -> 'DecofReal':
        return self._relative_humidity

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def air_pressure(self) -> 'DecofReal':
        return self._air_pressure


class DLCpro:
    def __init__(self, connection: Connection) -> None:
        self.__client = Client(connection)
        self._fw_ver = DecofString(self.__client, 'fw-ver')
        self._ssw_svn_revision = DecofString(self.__client, 'ssw-svn-revision')
        self._uptime = DecofInteger(self.__client, 'uptime')
        self._ssw_ver = DecofString(self.__client, 'ssw-ver')
        self._system_type = DecofString(self.__client, 'system-type')
        self._system_model = DecofString(self.__client, 'system-model')
        self._svn_revision = DecofString(self.__client, 'svn-revision')
        self._system_label = MutableDecofString(self.__client, 'system-label')
        self._decof_ver = DecofString(self.__client, 'decof-ver')
        self._build_information = BuildInformation(self.__client, 'build-information')
        self._decof_svn_revision = DecofString(self.__client, 'decof-svn-revision')
        self._uptime_txt = DecofString(self.__client, 'uptime-txt')
        self._echo = MutableDecofBoolean(self.__client, 'echo')
        self._serial_number = DecofString(self.__client, 'serial-number')
        self._net_conf = Ipconfig(self.__client, 'net-conf')
        self._fw_update = FwUpdate(self.__client, 'fw-update')
        self._system_service_report = ServiceReport(self.__client, 'system-service-report')
        self._time = MutableDecofString(self.__client, 'time')
        self._licenses = Licenses(self.__client, 'licenses')
        self._tan = DecofInteger(self.__client, 'tan')
        self._system_messages = SystemMessages(self.__client, 'system-messages')
        self._power_supply = PowerSupply(self.__client, 'power-supply')
        self._emission = DecofBoolean(self.__client, 'emission')
        self._pc1 = PcBoard(self.__client, 'pc1')
        self._io = IoBoard(self.__client, 'io')
        self._buzzer = Buzzer(self.__client, 'buzzer')
        self._tc1 = TcBoard(self.__client, 'tc1')
        self._system_health = DecofInteger(self.__client, 'system-health')
        self._standby = Standby(self.__client, 'standby')
        self._uv = UvShgLaser(self.__client, 'uv')
        self._laser1 = Laser(self.__client, 'laser1')
        self._display = Display(self.__client, 'display')
        self._ampcc2 = Cc5000Board(self.__client, 'ampcc2')
        self._ampcc1 = Cc5000Board(self.__client, 'ampcc1')
        self._system_health_txt = DecofString(self.__client, 'system-health-txt')
        self._tc2 = TcBoard(self.__client, 'tc2')
        self._pc3 = PcBoard(self.__client, 'pc3')
        self._frontkey_locked = DecofBoolean(self.__client, 'frontkey-locked')
        self._pc2 = PcBoard(self.__client, 'pc2')
        self._cc2 = CcBoard(self.__client, 'cc2')
        self._interlock_open = DecofBoolean(self.__client, 'interlock-open')
        self._mc = McBoard(self.__client, 'mc')
        self._cc1 = CcBoard(self.__client, 'cc1')
        self._ul = MutableDecofInteger(self.__client, 'ul')

    def __enter__(self):
        return self

    def __exit__(self):
        raise RuntimeError()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, *args):
        await self.close()

    def __await__(self):
        return self.__aenter__().__await__()

    async def open(self) -> None:
        await self.__client.open()

    async def close(self) -> None:
        await self.__client.close()

    @property
    def fw_ver(self) -> 'DecofString':
        return self._fw_ver

    @property
    def ssw_svn_revision(self) -> 'DecofString':
        return self._ssw_svn_revision

    @property
    def uptime(self) -> 'DecofInteger':
        return self._uptime

    @property
    def ssw_ver(self) -> 'DecofString':
        return self._ssw_ver

    @property
    def system_type(self) -> 'DecofString':
        return self._system_type

    @property
    def system_model(self) -> 'DecofString':
        return self._system_model

    @property
    def svn_revision(self) -> 'DecofString':
        return self._svn_revision

    @property
    def system_label(self) -> 'MutableDecofString':
        return self._system_label

    @property
    def decof_ver(self) -> 'DecofString':
        return self._decof_ver

    @property
    def build_information(self) -> 'BuildInformation':
        return self._build_information

    @property
    def decof_svn_revision(self) -> 'DecofString':
        return self._decof_svn_revision

    @property
    def uptime_txt(self) -> 'DecofString':
        return self._uptime_txt

    @property
    def echo(self) -> 'MutableDecofBoolean':
        return self._echo

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def net_conf(self) -> 'Ipconfig':
        return self._net_conf

    @property
    def fw_update(self) -> 'FwUpdate':
        return self._fw_update

    @property
    def system_service_report(self) -> 'ServiceReport':
        return self._system_service_report

    @property
    def time(self) -> 'MutableDecofString':
        return self._time

    @property
    def licenses(self) -> 'Licenses':
        return self._licenses

    @property
    def tan(self) -> 'DecofInteger':
        return self._tan

    @property
    def system_messages(self) -> 'SystemMessages':
        return self._system_messages

    @property
    def power_supply(self) -> 'PowerSupply':
        return self._power_supply

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def pc1(self) -> 'PcBoard':
        return self._pc1

    @property
    def io(self) -> 'IoBoard':
        return self._io

    @property
    def buzzer(self) -> 'Buzzer':
        return self._buzzer

    @property
    def tc1(self) -> 'TcBoard':
        return self._tc1

    @property
    def system_health(self) -> 'DecofInteger':
        return self._system_health

    @property
    def standby(self) -> 'Standby':
        return self._standby

    @property
    def uv(self) -> 'UvShgLaser':
        return self._uv

    @property
    def laser1(self) -> 'Laser':
        return self._laser1

    @property
    def display(self) -> 'Display':
        return self._display

    @property
    def ampcc2(self) -> 'Cc5000Board':
        return self._ampcc2

    @property
    def ampcc1(self) -> 'Cc5000Board':
        return self._ampcc1

    @property
    def system_health_txt(self) -> 'DecofString':
        return self._system_health_txt

    @property
    def tc2(self) -> 'TcBoard':
        return self._tc2

    @property
    def pc3(self) -> 'PcBoard':
        return self._pc3

    @property
    def frontkey_locked(self) -> 'DecofBoolean':
        return self._frontkey_locked

    @property
    def pc2(self) -> 'PcBoard':
        return self._pc2

    @property
    def cc2(self) -> 'CcBoard':
        return self._cc2

    @property
    def interlock_open(self) -> 'DecofBoolean':
        return self._interlock_open

    @property
    def mc(self) -> 'McBoard':
        return self._mc

    @property
    def cc1(self) -> 'CcBoard':
        return self._cc1

    @property
    def ul(self) -> 'MutableDecofInteger':
        return self._ul

    async def system_summary(self) -> str:
        return await self.__client.exec('system-summary', input_stream=None, output_type=str, return_type=None)

    async def system_connections(self) -> Tuple[str, int]:
        return await self.__client.exec('system-connections', input_stream=None, output_type=str, return_type=int)

    async def error_log(self) -> str:
        return await self.__client.exec('error-log', input_stream=None, output_type=str, return_type=None)

    async def debug_log(self) -> str:
        return await self.__client.exec('debug-log', input_stream=None, output_type=str, return_type=None)

    async def service_log(self) -> str:
        return await self.__client.exec('service-log', input_stream=None, output_type=str, return_type=None)

    async def service_report(self) -> bytes:
        return await self.__client.exec('service-report', input_stream=None, output_type=bytes, return_type=None)

    async def service_script(self, stream_input: bytes) -> None:
        assert isinstance(stream_input, bytes), "expected type 'bytes' for parameter 'stream_input', got '{}'".format(type(stream_input))
        await self.__client.exec('service-script', input_stream=stream_input, output_type=None, return_type=None)

    async def change_password(self, password: str) -> None:
        assert isinstance(password, str), "expected type 'str' for parameter 'password', got '{}'".format(type(password))
        await self.__client.exec('change-password', password, input_stream=None, output_type=None, return_type=None)

    async def change_ul(self, ul: AccessLevel, passwd: str) -> int:
        assert isinstance(ul, AccessLevel), "expected type 'AccessLevel' for parameter 'ul', got '{}'".format(type(ul))
        assert isinstance(passwd, str), "expected type 'str' for parameter 'passwd', got '{}'".format(type(passwd))
        return await self.__client.change_ul(ul, passwd)

