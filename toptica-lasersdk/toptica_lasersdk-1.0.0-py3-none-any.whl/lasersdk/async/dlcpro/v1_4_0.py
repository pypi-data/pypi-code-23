# Generated from 'v1_4_0.xml' on 2018-02-15 09:58:50.622040

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

    async def show_new(self) -> str:
        return await self.__client.exec(self.__name + ':show-new', input_stream=None, output_type=str, return_type=None)

    async def mark_as_read(self, ID: int) -> None:
        assert isinstance(ID, int), "expected type 'int' for parameter 'ID', got '{}'".format(type(ID))
        await self.__client.exec(self.__name + ':mark-as-read', ID, input_stream=None, output_type=None, return_type=None)

    async def show_all(self) -> str:
        return await self.__client.exec(self.__name + ':show-all', input_stream=None, output_type=str, return_type=None)

    async def show_persistent(self) -> str:
        return await self.__client.exec(self.__name + ':show-persistent', input_stream=None, output_type=str, return_type=None)

    async def show_log(self) -> str:
        return await self.__client.exec(self.__name + ':show-log', input_stream=None, output_type=str, return_type=None)


class Licenses:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._options = LicenseOptions(client, name + ':options')
        self._installed_keys = DecofInteger(client, name + ':installed-keys')

    @property
    def options(self) -> 'LicenseOptions':
        return self._options

    @property
    def installed_keys(self) -> 'DecofInteger':
        return self._installed_keys

    async def install(self, licensekey: str) -> bool:
        assert isinstance(licensekey, str), "expected type 'str' for parameter 'licensekey', got '{}'".format(type(licensekey))
        return await self.__client.exec(self.__name + ':install', licensekey, input_stream=None, output_type=None, return_type=bool)

    async def get_key(self, key_number: int) -> str:
        assert isinstance(key_number, int), "expected type 'int' for parameter 'key_number', got '{}'".format(type(key_number))
        return await self.__client.exec(self.__name + ':get-key', key_number, input_stream=None, output_type=None, return_type=str)


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
        self._enabled = DecofBoolean(client, name + ':enabled')
        self._licensee = DecofString(client, name + ':licensee')

    @property
    def valid_until(self) -> 'DecofString':
        return self._valid_until

    @property
    def enabled(self) -> 'DecofBoolean':
        return self._enabled

    @property
    def licensee(self) -> 'DecofString':
        return self._licensee


class FwUpdate:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name

    async def upload(self, stream_input: bytes, filename: str) -> None:
        assert isinstance(stream_input, bytes), "expected type 'bytes' for parameter 'stream_input', got '{}'".format(type(stream_input))
        assert isinstance(filename, str), "expected type 'str' for parameter 'filename', got '{}'".format(type(filename))
        await self.__client.exec(self.__name + ':upload', filename, input_stream=stream_input, output_type=None, return_type=None)

    async def show_log(self) -> str:
        return await self.__client.exec(self.__name + ':show-log', input_stream=None, output_type=str, return_type=None)

    async def show_history(self) -> str:
        return await self.__client.exec(self.__name + ':show-history', input_stream=None, output_type=str, return_type=None)


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


class Cc5000Board:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._status = DecofInteger(client, name + ':status')
        self._regulator_temp_fuse = DecofReal(client, name + ':regulator-temp-fuse')
        self._inverter_temp_fuse = DecofReal(client, name + ':inverter-temp-fuse')
        self._channel1 = Cc5000Drv(client, name + ':channel1')
        self._power_15v = MutableDecofBoolean(client, name + ':power-15v')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._regulator_temp = DecofReal(client, name + ':regulator-temp')
        self._parallel_mode = DecofBoolean(client, name + ':parallel-mode')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._variant = DecofString(client, name + ':variant')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._inverter_temp = DecofReal(client, name + ':inverter-temp')
        self._revision = DecofString(client, name + ':revision')
        self._slot = DecofString(client, name + ':slot')

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def regulator_temp_fuse(self) -> 'DecofReal':
        return self._regulator_temp_fuse

    @property
    def inverter_temp_fuse(self) -> 'DecofReal':
        return self._inverter_temp_fuse

    @property
    def channel1(self) -> 'Cc5000Drv':
        return self._channel1

    @property
    def power_15v(self) -> 'MutableDecofBoolean':
        return self._power_15v

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def regulator_temp(self) -> 'DecofReal':
        return self._regulator_temp

    @property
    def parallel_mode(self) -> 'DecofBoolean':
        return self._parallel_mode

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def inverter_temp(self) -> 'DecofReal':
        return self._inverter_temp

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def slot(self) -> 'DecofString':
        return self._slot


class Cc5000Drv:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._emission = DecofBoolean(client, name + ':emission')
        self._path = DecofString(client, name + ':path')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._current_act = DecofReal(client, name + ':current-act')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._status = DecofInteger(client, name + ':status')
        self._voltage_out = DecofReal(client, name + ':voltage-out')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._output_filter = OutputFilter1(client, name + ':output-filter')
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._aux = DecofReal(client, name + ':aux')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._variant = DecofString(client, name + ':variant')

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def voltage_out(self) -> 'DecofReal':
        return self._voltage_out

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def output_filter(self) -> 'OutputFilter1':
        return self._output_filter

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def variant(self) -> 'DecofString':
        return self._variant


class OutputFilter1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._slew_rate_enabled = MutableDecofBoolean(client, name + ':slew-rate-enabled')
        self._slew_rate = MutableDecofReal(client, name + ':slew-rate')
        self._slew_rate_limited = DecofBoolean(client, name + ':slew-rate-limited')

    @property
    def slew_rate_enabled(self) -> 'MutableDecofBoolean':
        return self._slew_rate_enabled

    @property
    def slew_rate(self) -> 'MutableDecofReal':
        return self._slew_rate

    @property
    def slew_rate_limited(self) -> 'DecofBoolean':
        return self._slew_rate_limited


class CcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._status = DecofInteger(client, name + ':status')
        self._channel1 = CurrDrv2(client, name + ':channel1')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._parallel_mode = DecofBoolean(client, name + ':parallel-mode')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._variant = DecofString(client, name + ':variant')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._revision = DecofString(client, name + ':revision')
        self._channel2 = CurrDrv2(client, name + ':channel2')
        self._slot = DecofString(client, name + ':slot')

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def channel1(self) -> 'CurrDrv2':
        return self._channel1

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def parallel_mode(self) -> 'DecofBoolean':
        return self._parallel_mode

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def channel2(self) -> 'CurrDrv2':
        return self._channel2

    @property
    def slot(self) -> 'DecofString':
        return self._slot


class CurrDrv2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._emission = DecofBoolean(client, name + ':emission')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._variant = DecofString(client, name + ':variant')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._path = DecofString(client, name + ':path')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')
        self._current_act = DecofReal(client, name + ':current-act')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._status = DecofInteger(client, name + ':status')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._aux = DecofReal(client, name + ':aux')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._pd = DecofReal(client, name + ':pd')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._external_input = ExtInput2(client, name + ':external-input')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._current_set_dithering = MutableDecofBoolean(client, name + ':current-set-dithering')

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def pd(self) -> 'DecofReal':
        return self._pd

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def current_set_dithering(self) -> 'MutableDecofBoolean':
        return self._current_set_dithering


class OutputFilter2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._slew_rate_enabled = MutableDecofBoolean(client, name + ':slew-rate-enabled')
        self._slew_rate = MutableDecofReal(client, name + ':slew-rate')
        self._slew_rate_limited = DecofBoolean(client, name + ':slew-rate-limited')

    @property
    def slew_rate_enabled(self) -> 'MutableDecofBoolean':
        return self._slew_rate_enabled

    @property
    def slew_rate(self) -> 'MutableDecofReal':
        return self._slew_rate

    @property
    def slew_rate_limited(self) -> 'DecofBoolean':
        return self._slew_rate_limited


class ExtInput2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._factor = MutableDecofReal(client, name + ':factor')

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor


class Standby:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._state = DecofInteger(client, name + ':state')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._laser1 = StandbyLaser(client, name + ':laser1')

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def laser1(self) -> 'StandbyLaser':
        return self._laser1


class StandbyLaser:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amp = StandbyAmp(client, name + ':amp')
        self._nlo = StandbyShg(client, name + ':nlo')
        self._dl = StandbyDl(client, name + ':dl')

    @property
    def amp(self) -> 'StandbyAmp':
        return self._amp

    @property
    def nlo(self) -> 'StandbyShg':
        return self._nlo

    @property
    def dl(self) -> 'StandbyDl':
        return self._dl


class StandbyAmp:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_cc = MutableDecofBoolean(client, name + ':disable-cc')
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')

    @property
    def disable_cc(self) -> 'MutableDecofBoolean':
        return self._disable_cc

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc


class StandbyShg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_power_stabilization = MutableDecofBoolean(client, name + ':disable-power-stabilization')
        self._disable_cavity_lock = MutableDecofBoolean(client, name + ':disable-cavity-lock')
        self._disable_servo_subsystem = MutableDecofBoolean(client, name + ':disable-servo-subsystem')
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')
        self._disable_pc = MutableDecofBoolean(client, name + ':disable-pc')

    @property
    def disable_power_stabilization(self) -> 'MutableDecofBoolean':
        return self._disable_power_stabilization

    @property
    def disable_cavity_lock(self) -> 'MutableDecofBoolean':
        return self._disable_cavity_lock

    @property
    def disable_servo_subsystem(self) -> 'MutableDecofBoolean':
        return self._disable_servo_subsystem

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc

    @property
    def disable_pc(self) -> 'MutableDecofBoolean':
        return self._disable_pc


class StandbyDl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._disable_cc = MutableDecofBoolean(client, name + ':disable-cc')
        self._disable_tc = MutableDecofBoolean(client, name + ':disable-tc')
        self._disable_pc = MutableDecofBoolean(client, name + ':disable-pc')

    @property
    def disable_cc(self) -> 'MutableDecofBoolean':
        return self._disable_cc

    @property
    def disable_tc(self) -> 'MutableDecofBoolean':
        return self._disable_tc

    @property
    def disable_pc(self) -> 'MutableDecofBoolean':
        return self._disable_pc


class Laser:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan = Siggen(client, name + ':scan')
        self._nlo = Nlo(client, name + ':nlo')
        self._amp = LaserAmp(client, name + ':amp')
        self._scope = ScopeT(client, name + ':scope')
        self._ctl = CtlT(client, name + ':ctl')
        self._emission = DecofBoolean(client, name + ':emission')
        self._type_ = DecofString(client, name + ':type')
        self._dl = LaserHead(client, name + ':dl')
        self._health = DecofInteger(client, name + ':health')
        self._pd_ext = PdExt(client, name + ':pd-ext')
        self._power_stabilization = PwrStab(client, name + ':power-stabilization')
        self._product_name = DecofString(client, name + ':product-name')
        self._health_txt = DecofString(client, name + ':health-txt')

    @property
    def scan(self) -> 'Siggen':
        return self._scan

    @property
    def nlo(self) -> 'Nlo':
        return self._nlo

    @property
    def amp(self) -> 'LaserAmp':
        return self._amp

    @property
    def scope(self) -> 'ScopeT':
        return self._scope

    @property
    def ctl(self) -> 'CtlT':
        return self._ctl

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def dl(self) -> 'LaserHead':
        return self._dl

    @property
    def health(self) -> 'DecofInteger':
        return self._health

    @property
    def pd_ext(self) -> 'PdExt':
        return self._pd_ext

    @property
    def power_stabilization(self) -> 'PwrStab':
        return self._power_stabilization

    @property
    def product_name(self) -> 'DecofString':
        return self._product_name

    @property
    def health_txt(self) -> 'DecofString':
        return self._health_txt

    async def load(self) -> None:
        await self.__client.exec(self.__name + ':load', input_stream=None, output_type=None, return_type=None)

    async def detect(self) -> None:
        await self.__client.exec(self.__name + ':detect', input_stream=None, output_type=None, return_type=None)

    async def save(self) -> None:
        await self.__client.exec(self.__name + ':save', input_stream=None, output_type=None, return_type=None)


class Siggen:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._unit = DecofString(client, name + ':unit')
        self._signal_type = MutableDecofInteger(client, name + ':signal-type')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._offset = MutableDecofReal(client, name + ':offset')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._end = MutableDecofReal(client, name + ':end')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._start = MutableDecofReal(client, name + ':start')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def signal_type(self) -> 'MutableDecofInteger':
        return self._signal_type

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def offset(self) -> 'MutableDecofReal':
        return self._offset

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def end(self) -> 'MutableDecofReal':
        return self._end

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def start(self) -> 'MutableDecofReal':
        return self._start

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude


class Nlo:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._ssw_ver = DecofString(client, name + ':ssw-ver')
        self._fhg = Fhg(client, name + ':fhg')
        self._shg = Shg(client, name + ':shg')
        self._power_optimization = NloLaserHeadPowerOptimization(client, name + ':power-optimization')
        self._pd = NloLaserHeadPhotoDiodes(client, name + ':pd')
        self._servo = NloLaserHeadServos(client, name + ':servo')

    @property
    def ssw_ver(self) -> 'DecofString':
        return self._ssw_ver

    @property
    def fhg(self) -> 'Fhg':
        return self._fhg

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
    def servo(self) -> 'NloLaserHeadServos':
        return self._servo


class Fhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan = NloLaserHeadSiggen(client, name + ':scan')
        self._factory_settings = FhgFactorySettings(client, name + ':factory-settings')
        self._lock = NloLaserHeadLockFhg(client, name + ':lock')
        self._scope = NloLaserHeadScopeT(client, name + ':scope')
        self._pc = PiezoDrv1(client, name + ':pc')
        self._tc = TcChannel(client, name + ':tc')

    @property
    def scan(self) -> 'NloLaserHeadSiggen':
        return self._scan

    @property
    def factory_settings(self) -> 'FhgFactorySettings':
        return self._factory_settings

    @property
    def lock(self) -> 'NloLaserHeadLockFhg':
        return self._lock

    @property
    def scope(self) -> 'NloLaserHeadScopeT':
        return self._scope

    @property
    def pc(self) -> 'PiezoDrv1':
        return self._pc

    @property
    def tc(self) -> 'TcChannel':
        return self._tc

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadSiggen:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._offset = MutableDecofReal(client, name + ':offset')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def offset(self) -> 'MutableDecofReal':
        return self._offset

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class FhgFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._modified = DecofBoolean(client, name + ':modified')
        self._pd = NloLaserHeadFhgPhotodiodesFactorySettings(client, name + ':pd')
        self._pc = NloLaserHeadPcFactorySettings(client, name + ':pc')
        self._tc = NloLaserHeadTcFactorySettings(client, name + ':tc')
        self._lock = NloLaserHeadLockFactorySettings(client, name + ':lock')

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def pd(self) -> 'NloLaserHeadFhgPhotodiodesFactorySettings':
        return self._pd

    @property
    def pc(self) -> 'NloLaserHeadPcFactorySettings':
        return self._pc

    @property
    def tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._tc

    @property
    def lock(self) -> 'NloLaserHeadLockFactorySettings':
        return self._lock

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadFhgPhotodiodesFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pdh_dc = NloLaserHeadPdDigilockFactorySettings(client, name + ':pdh-dc')
        self._pdh_rf = NloLaserHeadPdPdhFactorySettings(client, name + ':pdh-rf')
        self._fhg = NloLaserHeadPdFactorySettings(client, name + ':fhg')
        self._int = NloLaserHeadPdDigilockFactorySettings(client, name + ':int')

    @property
    def pdh_dc(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._pdh_dc

    @property
    def pdh_rf(self) -> 'NloLaserHeadPdPdhFactorySettings':
        return self._pdh_rf

    @property
    def fhg(self) -> 'NloLaserHeadPdFactorySettings':
        return self._fhg

    @property
    def int(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._int


class NloLaserHeadPdDigilockFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

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


class NloLaserHeadPcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan_offset = MutableDecofReal(client, name + ':scan-offset')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._scan_frequency = MutableDecofReal(client, name + ':scan-frequency')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._scan_amplitude = MutableDecofReal(client, name + ':scan-amplitude')
        self._capacitance = MutableDecofReal(client, name + ':capacitance')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')

    @property
    def scan_offset(self) -> 'MutableDecofReal':
        return self._scan_offset

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def scan_frequency(self) -> 'MutableDecofReal':
        return self._scan_frequency

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def scan_amplitude(self) -> 'MutableDecofReal':
        return self._scan_amplitude

    @property
    def capacitance(self) -> 'MutableDecofReal':
        return self._capacitance

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor


class NloLaserHeadTcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._c_gain = MutableDecofReal(client, name + ':c-gain')
        self._current_max = MutableDecofReal(client, name + ':current-max')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._ntc_series_resistance = MutableDecofReal(client, name + ':ntc-series-resistance')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._power_source = MutableDecofInteger(client, name + ':power-source')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._current_min = MutableDecofReal(client, name + ':current-min')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def c_gain(self) -> 'MutableDecofReal':
        return self._c_gain

    @property
    def current_max(self) -> 'MutableDecofReal':
        return self._current_max

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def ntc_series_resistance(self) -> 'MutableDecofReal':
        return self._ntc_series_resistance

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def power_source(self) -> 'MutableDecofInteger':
        return self._power_source

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def current_min(self) -> 'MutableDecofReal':
        return self._current_min

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain


class NloLaserHeadLockFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._relock = NloLaserHeadRelockFactorySettings(client, name + ':relock')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._window = NloLaserHeadLockWindowFactorySettings(client, name + ':window')
        self._analog_p_gain = MutableDecofReal(client, name + ':analog-p-gain')
        self._local_oscillator = NloLaserHeadLocalOscillatorFactorySettings(client, name + ':local-oscillator')
        self._pid2_gain = NloLaserHeadPidGainFactorySettings(client, name + ':pid2-gain')
        self._pid1_gain = NloLaserHeadPidGainFactorySettings(client, name + ':pid1-gain')

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def relock(self) -> 'NloLaserHeadRelockFactorySettings':
        return self._relock

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def window(self) -> 'NloLaserHeadLockWindowFactorySettings':
        return self._window

    @property
    def analog_p_gain(self) -> 'MutableDecofReal':
        return self._analog_p_gain

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorFactorySettings':
        return self._local_oscillator

    @property
    def pid2_gain(self) -> 'NloLaserHeadPidGainFactorySettings':
        return self._pid2_gain

    @property
    def pid1_gain(self) -> 'NloLaserHeadPidGainFactorySettings':
        return self._pid1_gain


class NloLaserHeadRelockFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._delay = MutableDecofReal(client, name + ':delay')

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def delay(self) -> 'MutableDecofReal':
        return self._delay


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


class NloLaserHeadLocalOscillatorFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._phase_shift_shg = MutableDecofReal(client, name + ':phase-shift-shg')
        self._attenuation_shg_raw = MutableDecofInteger(client, name + ':attenuation-shg-raw')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._attenuation_fhg_raw = MutableDecofInteger(client, name + ':attenuation-fhg-raw')
        self._phase_shift_fhg = MutableDecofReal(client, name + ':phase-shift-fhg')

    @property
    def phase_shift_shg(self) -> 'MutableDecofReal':
        return self._phase_shift_shg

    @property
    def attenuation_shg_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_shg_raw

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def attenuation_fhg_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_fhg_raw

    @property
    def phase_shift_fhg(self) -> 'MutableDecofReal':
        return self._phase_shift_fhg


class NloLaserHeadPidGainFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')
        self._p = MutableDecofReal(client, name + ':p')
        self._i = MutableDecofReal(client, name + ':i')
        self._all = MutableDecofReal(client, name + ':all')
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._d = MutableDecofReal(client, name + ':d')

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d


class NloLaserHeadLockFhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._relock = NloLaserHeadRelock(client, name + ':relock')
        self._pid1 = NloLaserHeadPid(client, name + ':pid1')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._window = NloLaserHeadWindow(client, name + ':window')
        self._cavity_fast_pzt_voltage = MutableDecofReal(client, name + ':cavity-fast-pzt-voltage')
        self._pid2 = NloLaserHeadPid(client, name + ':pid2')
        self._cavity_slow_pzt_voltage = MutableDecofReal(client, name + ':cavity-slow-pzt-voltage')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._state = MutableDecofInteger(client, name + ':state')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._local_oscillator = NloLaserHeadLocalOscillatorFhg(client, name + ':local-oscillator')
        self._background_trace = DecofBinary(client, name + ':background-trace')

    @property
    def relock(self) -> 'NloLaserHeadRelock':
        return self._relock

    @property
    def pid1(self) -> 'NloLaserHeadPid':
        return self._pid1

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def window(self) -> 'NloLaserHeadWindow':
        return self._window

    @property
    def cavity_fast_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_fast_pzt_voltage

    @property
    def pid2(self) -> 'NloLaserHeadPid':
        return self._pid2

    @property
    def cavity_slow_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_slow_pzt_voltage

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def state(self) -> 'MutableDecofInteger':
        return self._state

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorFhg':
        return self._local_oscillator

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace


class NloLaserHeadRelock:
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


class NloLaserHeadPid:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._gain = NloLaserHeadGain(client, name + ':gain')

    @property
    def gain(self) -> 'NloLaserHeadGain':
        return self._gain


class NloLaserHeadGain:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._p = MutableDecofReal(client, name + ':p')
        self._i = MutableDecofReal(client, name + ':i')
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')
        self._all = MutableDecofReal(client, name + ':all')
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._d = MutableDecofReal(client, name + ':d')

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d


class NloLaserHeadWindow:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._threshold = MutableDecofReal(client, name + ':threshold')
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def threshold(self) -> 'MutableDecofReal':
        return self._threshold

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis


class NloLaserHeadLocalOscillatorFhg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._use_external_oscillator = MutableDecofBoolean(client, name + ':use-external-oscillator')
        self._use_fast_oscillator = MutableDecofBoolean(client, name + ':use-fast-oscillator')
        self._coupled_modulation = MutableDecofBoolean(client, name + ':coupled-modulation')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._attenuation_raw = MutableDecofInteger(client, name + ':attenuation-raw')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')

    @property
    def use_external_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_external_oscillator

    @property
    def use_fast_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_fast_oscillator

    @property
    def coupled_modulation(self) -> 'MutableDecofBoolean':
        return self._coupled_modulation

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def attenuation_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_raw

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    async def auto_pdh(self) -> None:
        await self.__client.exec(self.__name + ':auto-pdh', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadScopeT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channel1 = NloLaserHeadScopeChannelT(client, name + ':channel1')
        self._data = DecofBinary(client, name + ':data')
        self._variant = MutableDecofInteger(client, name + ':variant')
        self._channelx = NloLaserHeadScopeXAxisT(client, name + ':channelx')
        self._timescale = MutableDecofReal(client, name + ':timescale')
        self._channel2 = NloLaserHeadScopeChannelT(client, name + ':channel2')
        self._update_rate = MutableDecofInteger(client, name + ':update-rate')

    @property
    def channel1(self) -> 'NloLaserHeadScopeChannelT':
        return self._channel1

    @property
    def data(self) -> 'DecofBinary':
        return self._data

    @property
    def variant(self) -> 'MutableDecofInteger':
        return self._variant

    @property
    def channelx(self) -> 'NloLaserHeadScopeXAxisT':
        return self._channelx

    @property
    def timescale(self) -> 'MutableDecofReal':
        return self._timescale

    @property
    def channel2(self) -> 'NloLaserHeadScopeChannelT':
        return self._channel2

    @property
    def update_rate(self) -> 'MutableDecofInteger':
        return self._update_rate


class NloLaserHeadScopeChannelT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._unit = DecofString(client, name + ':unit')
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._name = DecofString(client, name + ':name')

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def name(self) -> 'DecofString':
        return self._name


class NloLaserHeadScopeXAxisT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._xy_signal = MutableDecofInteger(client, name + ':xy-signal')
        self._spectrum_omit_dc = MutableDecofBoolean(client, name + ':spectrum-omit-dc')
        self._scope_timescale = MutableDecofReal(client, name + ':scope-timescale')
        self._spectrum_range = MutableDecofReal(client, name + ':spectrum-range')
        self._unit = DecofString(client, name + ':unit')
        self._name = DecofString(client, name + ':name')

    @property
    def xy_signal(self) -> 'MutableDecofInteger':
        return self._xy_signal

    @property
    def spectrum_omit_dc(self) -> 'MutableDecofBoolean':
        return self._spectrum_omit_dc

    @property
    def scope_timescale(self) -> 'MutableDecofReal':
        return self._scope_timescale

    @property
    def spectrum_range(self) -> 'MutableDecofReal':
        return self._spectrum_range

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def name(self) -> 'DecofString':
        return self._name


class PiezoDrv1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._path = DecofString(client, name + ':path')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._status = DecofInteger(client, name + ':status')
        self._output_filter = OutputFilter1(client, name + ':output-filter')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._external_input = ExtInput1(client, name + ':external-input')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._voltage_set_dithering = MutableDecofBoolean(client, name + ':voltage-set-dithering')
        self._voltage_act = DecofReal(client, name + ':voltage-act')

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def output_filter(self) -> 'OutputFilter1':
        return self._output_filter

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def external_input(self) -> 'ExtInput1':
        return self._external_input

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def voltage_set_dithering(self) -> 'MutableDecofBoolean':
        return self._voltage_set_dithering

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act


class ExtInput1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._factor = MutableDecofReal(client, name + ':factor')

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor


class TcChannel:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._t_loop = TcChannelTLoop(client, name + ':t-loop')
        self._current_set_min = MutableDecofReal(client, name + ':current-set-min')
        self._path = DecofString(client, name + ':path')
        self._ready = DecofBoolean(client, name + ':ready')
        self._ntc_series_resistance = DecofReal(client, name + ':ntc-series-resistance')
        self._current_set = DecofReal(client, name + ':current-set')
        self._current_act = DecofReal(client, name + ':current-act')
        self._c_loop = TcChannelCLoop(client, name + ':c-loop')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._temp_set_min = MutableDecofReal(client, name + ':temp-set-min')
        self._temp_reset = MutableDecofBoolean(client, name + ':temp-reset')
        self._limits = TcChannelCheck(client, name + ':limits')
        self._status = DecofInteger(client, name + ':status')
        self._disabled_preset = TcDisabledPreset(client, name + ':disabled-preset')
        self._current_set_max = MutableDecofReal(client, name + ':current-set-max')
        self._fault = DecofBoolean(client, name + ':fault')
        self._resistance = DecofReal(client, name + ':resistance')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._power_source = DecofInteger(client, name + ':power-source')
        self._temp_act = DecofReal(client, name + ':temp-act')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._temp_set_max = MutableDecofReal(client, name + ':temp-set-max')
        self._drv_voltage = DecofReal(client, name + ':drv-voltage')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def t_loop(self) -> 'TcChannelTLoop':
        return self._t_loop

    @property
    def current_set_min(self) -> 'MutableDecofReal':
        return self._current_set_min

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def ready(self) -> 'DecofBoolean':
        return self._ready

    @property
    def ntc_series_resistance(self) -> 'DecofReal':
        return self._ntc_series_resistance

    @property
    def current_set(self) -> 'DecofReal':
        return self._current_set

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def c_loop(self) -> 'TcChannelCLoop':
        return self._c_loop

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def temp_set_min(self) -> 'MutableDecofReal':
        return self._temp_set_min

    @property
    def temp_reset(self) -> 'MutableDecofBoolean':
        return self._temp_reset

    @property
    def limits(self) -> 'TcChannelCheck':
        return self._limits

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def disabled_preset(self) -> 'TcDisabledPreset':
        return self._disabled_preset

    @property
    def current_set_max(self) -> 'MutableDecofReal':
        return self._current_set_max

    @property
    def fault(self) -> 'DecofBoolean':
        return self._fault

    @property
    def resistance(self) -> 'DecofReal':
        return self._resistance

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def power_source(self) -> 'DecofInteger':
        return self._power_source

    @property
    def temp_act(self) -> 'DecofReal':
        return self._temp_act

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def temp_set_max(self) -> 'MutableDecofReal':
        return self._temp_set_max

    @property
    def drv_voltage(self) -> 'DecofReal':
        return self._drv_voltage

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    async def check_peltier(self) -> float:
        return await self.__client.exec(self.__name + ':check-peltier', input_stream=None, output_type=None, return_type=float)


class TcChannelTLoop:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')
        self._on = MutableDecofBoolean(client, name + ':on')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

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
    def on(self) -> 'MutableDecofBoolean':
        return self._on

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance


class TcChannelCLoop:
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


class TcChannelCheck:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._out_of_range = DecofBoolean(client, name + ':out-of-range')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._timed_out = DecofBoolean(client, name + ':timed-out')

    @property
    def out_of_range(self) -> 'DecofBoolean':
        return self._out_of_range

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def timed_out(self) -> 'DecofBoolean':
        return self._timed_out


class TcDisabledPreset:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name


class Shg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan = NloLaserHeadSiggen(client, name + ':scan')
        self._factory_settings = ShgFactorySettings(client, name + ':factory-settings')
        self._lock = NloLaserHeadLockShg(client, name + ':lock')
        self._scope = NloLaserHeadScopeT(client, name + ':scope')
        self._pc = PiezoDrv1(client, name + ':pc')
        self._tc = TcChannel(client, name + ':tc')

    @property
    def scan(self) -> 'NloLaserHeadSiggen':
        return self._scan

    @property
    def factory_settings(self) -> 'ShgFactorySettings':
        return self._factory_settings

    @property
    def lock(self) -> 'NloLaserHeadLockShg':
        return self._lock

    @property
    def scope(self) -> 'NloLaserHeadScopeT':
        return self._scope

    @property
    def pc(self) -> 'PiezoDrv1':
        return self._pc

    @property
    def tc(self) -> 'TcChannel':
        return self._tc

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)


class ShgFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._modified = DecofBoolean(client, name + ':modified')
        self._pd = NloLaserHeadShgPhotodiodesFactorySettings(client, name + ':pd')
        self._pc = NloLaserHeadPcFactorySettings(client, name + ':pc')
        self._tc = NloLaserHeadTcFactorySettings(client, name + ':tc')
        self._lock = NloLaserHeadLockFactorySettings(client, name + ':lock')

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def pd(self) -> 'NloLaserHeadShgPhotodiodesFactorySettings':
        return self._pd

    @property
    def pc(self) -> 'NloLaserHeadPcFactorySettings':
        return self._pc

    @property
    def tc(self) -> 'NloLaserHeadTcFactorySettings':
        return self._tc

    @property
    def lock(self) -> 'NloLaserHeadLockFactorySettings':
        return self._lock

    async def retrieve_now(self) -> None:
        await self.__client.exec(self.__name + ':retrieve-now', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadShgPhotodiodesFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pdh_dc = NloLaserHeadPdDigilockFactorySettings(client, name + ':pdh-dc')
        self._amp = NloLaserHeadPdFactorySettings(client, name + ':amp')
        self._int = NloLaserHeadPdDigilockFactorySettings(client, name + ':int')
        self._fiber = NloLaserHeadPdFactorySettings(client, name + ':fiber')
        self._dl = NloLaserHeadPdFactorySettings(client, name + ':dl')
        self._shg = NloLaserHeadPdFactorySettings(client, name + ':shg')
        self._pdh_rf = NloLaserHeadPdPdhFactorySettings(client, name + ':pdh-rf')

    @property
    def pdh_dc(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._pdh_dc

    @property
    def amp(self) -> 'NloLaserHeadPdFactorySettings':
        return self._amp

    @property
    def int(self) -> 'NloLaserHeadPdDigilockFactorySettings':
        return self._int

    @property
    def fiber(self) -> 'NloLaserHeadPdFactorySettings':
        return self._fiber

    @property
    def dl(self) -> 'NloLaserHeadPdFactorySettings':
        return self._dl

    @property
    def shg(self) -> 'NloLaserHeadPdFactorySettings':
        return self._shg

    @property
    def pdh_rf(self) -> 'NloLaserHeadPdPdhFactorySettings':
        return self._pdh_rf


class NloLaserHeadLockShg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._relock = NloLaserHeadRelock(client, name + ':relock')
        self._pid1 = NloLaserHeadPid(client, name + ':pid1')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._window = NloLaserHeadWindow(client, name + ':window')
        self._cavity_fast_pzt_voltage = MutableDecofReal(client, name + ':cavity-fast-pzt-voltage')
        self._pid2 = NloLaserHeadPid(client, name + ':pid2')
        self._cavity_slow_pzt_voltage = MutableDecofReal(client, name + ':cavity-slow-pzt-voltage')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._state = MutableDecofInteger(client, name + ':state')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._analog_dl_gain = NloLaserHeadMinifalc(client, name + ':analog-dl-gain')
        self._local_oscillator = NloLaserHeadLocalOscillatorShg(client, name + ':local-oscillator')
        self._background_trace = DecofBinary(client, name + ':background-trace')

    @property
    def relock(self) -> 'NloLaserHeadRelock':
        return self._relock

    @property
    def pid1(self) -> 'NloLaserHeadPid':
        return self._pid1

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def window(self) -> 'NloLaserHeadWindow':
        return self._window

    @property
    def cavity_fast_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_fast_pzt_voltage

    @property
    def pid2(self) -> 'NloLaserHeadPid':
        return self._pid2

    @property
    def cavity_slow_pzt_voltage(self) -> 'MutableDecofReal':
        return self._cavity_slow_pzt_voltage

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def state(self) -> 'MutableDecofInteger':
        return self._state

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def analog_dl_gain(self) -> 'NloLaserHeadMinifalc':
        return self._analog_dl_gain

    @property
    def local_oscillator(self) -> 'NloLaserHeadLocalOscillatorShg':
        return self._local_oscillator

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace


class NloLaserHeadMinifalc:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._p_gain = MutableDecofReal(client, name + ':p-gain')

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain


class NloLaserHeadLocalOscillatorShg:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._use_external_oscillator = MutableDecofBoolean(client, name + ':use-external-oscillator')
        self._use_fast_oscillator = MutableDecofBoolean(client, name + ':use-fast-oscillator')
        self._coupled_modulation = MutableDecofBoolean(client, name + ':coupled-modulation')
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._attenuation_raw = MutableDecofInteger(client, name + ':attenuation-raw')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')

    @property
    def use_external_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_external_oscillator

    @property
    def use_fast_oscillator(self) -> 'MutableDecofBoolean':
        return self._use_fast_oscillator

    @property
    def coupled_modulation(self) -> 'MutableDecofBoolean':
        return self._coupled_modulation

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def attenuation_raw(self) -> 'MutableDecofInteger':
        return self._attenuation_raw

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    async def auto_pdh(self) -> None:
        await self.__client.exec(self.__name + ':auto-pdh', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadPowerOptimization:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._status = DecofInteger(client, name + ':status')
        self._stage2 = NloLaserHeadStage(client, name + ':stage2')
        self._ongoing = DecofBoolean(client, name + ':ongoing')
        self._shg_advanced = MutableDecofBoolean(client, name + ':shg-advanced')
        self._progress_data_fhg = DecofBinary(client, name + ':progress-data-fhg')
        self._progress_data_shg = DecofBinary(client, name + ':progress-data-shg')
        self._stage1 = NloLaserHeadStage(client, name + ':stage1')
        self._progress = DecofInteger(client, name + ':progress')
        self._abort = MutableDecofBoolean(client, name + ':abort')
        self._stage3 = NloLaserHeadStage(client, name + ':stage3')
        self._progress_data_amp = DecofBinary(client, name + ':progress-data-amp')
        self._status_string = DecofString(client, name + ':status-string')
        self._progress_data_fiber = DecofBinary(client, name + ':progress-data-fiber')
        self._stage5 = NloLaserHeadStage(client, name + ':stage5')
        self._stage4 = NloLaserHeadStage(client, name + ':stage4')

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def stage2(self) -> 'NloLaserHeadStage':
        return self._stage2

    @property
    def ongoing(self) -> 'DecofBoolean':
        return self._ongoing

    @property
    def shg_advanced(self) -> 'MutableDecofBoolean':
        return self._shg_advanced

    @property
    def progress_data_fhg(self) -> 'DecofBinary':
        return self._progress_data_fhg

    @property
    def progress_data_shg(self) -> 'DecofBinary':
        return self._progress_data_shg

    @property
    def stage1(self) -> 'NloLaserHeadStage':
        return self._stage1

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def abort(self) -> 'MutableDecofBoolean':
        return self._abort

    @property
    def stage3(self) -> 'NloLaserHeadStage':
        return self._stage3

    @property
    def progress_data_amp(self) -> 'DecofBinary':
        return self._progress_data_amp

    @property
    def status_string(self) -> 'DecofString':
        return self._status_string

    @property
    def progress_data_fiber(self) -> 'DecofBinary':
        return self._progress_data_fiber

    @property
    def stage5(self) -> 'NloLaserHeadStage':
        return self._stage5

    @property
    def stage4(self) -> 'NloLaserHeadStage':
        return self._stage4

    async def start_optimization_shg(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-shg', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_all(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-all', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_fhg(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-fhg', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_fiber(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-fiber', input_stream=None, output_type=None, return_type=int)

    async def start_optimization_amp(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization-amp', input_stream=None, output_type=None, return_type=int)


class NloLaserHeadStage:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._input = NloLaserHeadOptInput(client, name + ':input')
        self._restore_on_abort = MutableDecofBoolean(client, name + ':restore-on-abort')
        self._regress_tolerance = MutableDecofInteger(client, name + ':regress-tolerance')
        self._restore_on_regress = MutableDecofBoolean(client, name + ':restore-on-regress')
        self._optimization_in_progress = DecofBoolean(client, name + ':optimization-in-progress')
        self._progress = DecofInteger(client, name + ':progress')

    @property
    def input(self) -> 'NloLaserHeadOptInput':
        return self._input

    @property
    def restore_on_abort(self) -> 'MutableDecofBoolean':
        return self._restore_on_abort

    @property
    def regress_tolerance(self) -> 'MutableDecofInteger':
        return self._regress_tolerance

    @property
    def restore_on_regress(self) -> 'MutableDecofBoolean':
        return self._restore_on_regress

    @property
    def optimization_in_progress(self) -> 'DecofBoolean':
        return self._optimization_in_progress

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    async def start_optimization(self) -> int:
        return await self.__client.exec(self.__name + ':start-optimization', input_stream=None, output_type=None, return_type=int)


class NloLaserHeadOptInput:
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
        self._fhg_pdh_dc = NloLaserHeadNloDigilockPhotodiode(client, name + ':fhg-pdh-dc')
        self._amp = NloLaserHeadNloPhotodiode(client, name + ':amp')
        self._shg_int = NloLaserHeadNloDigilockPhotodiode(client, name + ':shg-int')
        self._fhg = NloLaserHeadNloPhotodiode(client, name + ':fhg')
        self._shg = NloLaserHeadNloPhotodiode(client, name + ':shg')
        self._fiber = NloLaserHeadNloPhotodiode(client, name + ':fiber')
        self._dl = NloLaserHeadNloPhotodiode(client, name + ':dl')
        self._fhg_int = NloLaserHeadNloDigilockPhotodiode(client, name + ':fhg-int')
        self._shg_pdh_rf = NloLaserHeadNloPdhPhotodiode(client, name + ':shg-pdh-rf')
        self._fhg_pdh_rf = NloLaserHeadNloPdhPhotodiode(client, name + ':fhg-pdh-rf')
        self._shg_pdh_dc = NloLaserHeadNloDigilockPhotodiode(client, name + ':shg-pdh-dc')

    @property
    def fhg_pdh_dc(self) -> 'NloLaserHeadNloDigilockPhotodiode':
        return self._fhg_pdh_dc

    @property
    def amp(self) -> 'NloLaserHeadNloPhotodiode':
        return self._amp

    @property
    def shg_int(self) -> 'NloLaserHeadNloDigilockPhotodiode':
        return self._shg_int

    @property
    def fhg(self) -> 'NloLaserHeadNloPhotodiode':
        return self._fhg

    @property
    def shg(self) -> 'NloLaserHeadNloPhotodiode':
        return self._shg

    @property
    def fiber(self) -> 'NloLaserHeadNloPhotodiode':
        return self._fiber

    @property
    def dl(self) -> 'NloLaserHeadNloPhotodiode':
        return self._dl

    @property
    def fhg_int(self) -> 'NloLaserHeadNloDigilockPhotodiode':
        return self._fhg_int

    @property
    def shg_pdh_rf(self) -> 'NloLaserHeadNloPdhPhotodiode':
        return self._shg_pdh_rf

    @property
    def fhg_pdh_rf(self) -> 'NloLaserHeadNloPdhPhotodiode':
        return self._fhg_pdh_rf

    @property
    def shg_pdh_dc(self) -> 'NloLaserHeadNloDigilockPhotodiode':
        return self._shg_pdh_dc


class NloLaserHeadNloDigilockPhotodiode:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class NloLaserHeadNloPhotodiode:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power = DecofReal(client, name + ':power')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class NloLaserHeadNloPdhPhotodiode:
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


class NloLaserHeadServos:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._fiber1_vert = NloLaserHeadServoPwm(client, name + ':fiber1-vert')
        self._fiber1_hor = NloLaserHeadServoPwm(client, name + ':fiber1-hor')
        self._fhg1_vert = NloLaserHeadServoPwm(client, name + ':fhg1-vert')
        self._fhg2_vert = NloLaserHeadServoPwm(client, name + ':fhg2-vert')
        self._shg1_vert = NloLaserHeadServoPwm(client, name + ':shg1-vert')
        self._fhg2_hor = NloLaserHeadServoPwm(client, name + ':fhg2-hor')
        self._ta1_vert = NloLaserHeadServoPwm(client, name + ':ta1-vert')
        self._fiber2_vert = NloLaserHeadServoPwm(client, name + ':fiber2-vert')
        self._shg1_hor = NloLaserHeadServoPwm(client, name + ':shg1-hor')
        self._ta1_hor = NloLaserHeadServoPwm(client, name + ':ta1-hor')
        self._fiber2_hor = NloLaserHeadServoPwm(client, name + ':fiber2-hor')
        self._uv_cryst = NloLaserHeadServoPwm(client, name + ':uv-cryst')
        self._shg2_vert = NloLaserHeadServoPwm(client, name + ':shg2-vert')
        self._ta2_vert = NloLaserHeadServoPwm(client, name + ':ta2-vert')
        self._uv_outcpl = NloLaserHeadServoPwm(client, name + ':uv-outcpl')
        self._shg2_hor = NloLaserHeadServoPwm(client, name + ':shg2-hor')
        self._ta2_hor = NloLaserHeadServoPwm(client, name + ':ta2-hor')
        self._fhg1_hor = NloLaserHeadServoPwm(client, name + ':fhg1-hor')

    @property
    def fiber1_vert(self) -> 'NloLaserHeadServoPwm':
        return self._fiber1_vert

    @property
    def fiber1_hor(self) -> 'NloLaserHeadServoPwm':
        return self._fiber1_hor

    @property
    def fhg1_vert(self) -> 'NloLaserHeadServoPwm':
        return self._fhg1_vert

    @property
    def fhg2_vert(self) -> 'NloLaserHeadServoPwm':
        return self._fhg2_vert

    @property
    def shg1_vert(self) -> 'NloLaserHeadServoPwm':
        return self._shg1_vert

    @property
    def fhg2_hor(self) -> 'NloLaserHeadServoPwm':
        return self._fhg2_hor

    @property
    def ta1_vert(self) -> 'NloLaserHeadServoPwm':
        return self._ta1_vert

    @property
    def fiber2_vert(self) -> 'NloLaserHeadServoPwm':
        return self._fiber2_vert

    @property
    def shg1_hor(self) -> 'NloLaserHeadServoPwm':
        return self._shg1_hor

    @property
    def ta1_hor(self) -> 'NloLaserHeadServoPwm':
        return self._ta1_hor

    @property
    def fiber2_hor(self) -> 'NloLaserHeadServoPwm':
        return self._fiber2_hor

    @property
    def uv_cryst(self) -> 'NloLaserHeadServoPwm':
        return self._uv_cryst

    @property
    def shg2_vert(self) -> 'NloLaserHeadServoPwm':
        return self._shg2_vert

    @property
    def ta2_vert(self) -> 'NloLaserHeadServoPwm':
        return self._ta2_vert

    @property
    def uv_outcpl(self) -> 'NloLaserHeadServoPwm':
        return self._uv_outcpl

    @property
    def shg2_hor(self) -> 'NloLaserHeadServoPwm':
        return self._shg2_hor

    @property
    def ta2_hor(self) -> 'NloLaserHeadServoPwm':
        return self._ta2_hor

    @property
    def fhg1_hor(self) -> 'NloLaserHeadServoPwm':
        return self._fhg1_hor

    async def center_fhg_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-fhg-servos', input_stream=None, output_type=None, return_type=None)

    async def center_ta_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-ta-servos', input_stream=None, output_type=None, return_type=None)

    async def center_all_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-all-servos', input_stream=None, output_type=None, return_type=None)

    async def center_fiber_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-fiber-servos', input_stream=None, output_type=None, return_type=None)

    async def center_shg_servos(self) -> None:
        await self.__client.exec(self.__name + ':center-shg-servos', input_stream=None, output_type=None, return_type=None)


class NloLaserHeadServoPwm:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._display_name = DecofString(client, name + ':display-name')
        self._value = MutableDecofInteger(client, name + ':value')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def display_name(self) -> 'DecofString':
        return self._display_name

    @property
    def value(self) -> 'MutableDecofInteger':
        return self._value

    async def center_servo(self) -> None:
        await self.__client.exec(self.__name + ':center-servo', input_stream=None, output_type=None, return_type=None)


class LaserAmp:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._output_limits = AmpPower(client, name + ':output-limits')
        self._cc = Cc5000Drv(client, name + ':cc')
        self._legacy = DecofBoolean(client, name + ':legacy')
        self._seed_limits = AmpPower(client, name + ':seed-limits')
        self._ontime_txt = DecofString(client, name + ':ontime-txt')
        self._ontime = DecofInteger(client, name + ':ontime')
        self._seedonly_check = AmpSeedonlyCheck(client, name + ':seedonly-check')
        self._type_ = DecofString(client, name + ':type')
        self._factory_settings = AmpFactory(client, name + ':factory-settings')
        self._tc = TcChannel(client, name + ':tc')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._version = DecofString(client, name + ':version')

    @property
    def output_limits(self) -> 'AmpPower':
        return self._output_limits

    @property
    def cc(self) -> 'Cc5000Drv':
        return self._cc

    @property
    def legacy(self) -> 'DecofBoolean':
        return self._legacy

    @property
    def seed_limits(self) -> 'AmpPower':
        return self._seed_limits

    @property
    def ontime_txt(self) -> 'DecofString':
        return self._ontime_txt

    @property
    def ontime(self) -> 'DecofInteger':
        return self._ontime

    @property
    def seedonly_check(self) -> 'AmpSeedonlyCheck':
        return self._seedonly_check

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def factory_settings(self) -> 'AmpFactory':
        return self._factory_settings

    @property
    def tc(self) -> 'TcChannel':
        return self._tc

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def version(self) -> 'DecofString':
        return self._version

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)


class AmpPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power = DecofReal(client, name + ':power')
        self._status = DecofInteger(client, name + ':status')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._power_max_shutdown_delay = MutableDecofReal(client, name + ':power-max-shutdown-delay')
        self._power_max_warning_delay = MutableDecofReal(client, name + ':power-max-warning-delay')
        self._power_max = MutableDecofReal(client, name + ':power-max')
        self._power_min_warning_delay = MutableDecofReal(client, name + ':power-min-warning-delay')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._power_min_shutdown_delay = MutableDecofReal(client, name + ':power-min-shutdown-delay')
        self._power_min = MutableDecofReal(client, name + ':power-min')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def power_max_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_max_shutdown_delay

    @property
    def power_max_warning_delay(self) -> 'MutableDecofReal':
        return self._power_max_warning_delay

    @property
    def power_max(self) -> 'MutableDecofReal':
        return self._power_max

    @property
    def power_min_warning_delay(self) -> 'MutableDecofReal':
        return self._power_min_warning_delay

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def power_min_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_min_shutdown_delay

    @property
    def power_min(self) -> 'MutableDecofReal':
        return self._power_min

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class AmpSeedonlyCheck:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._pump = DecofBoolean(client, name + ':pump')
        self._warning_delay = MutableDecofReal(client, name + ':warning-delay')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._shutdown_delay = MutableDecofReal(client, name + ':shutdown-delay')
        self._status = DecofInteger(client, name + ':status')
        self._seed = DecofBoolean(client, name + ':seed')

    @property
    def pump(self) -> 'DecofBoolean':
        return self._pump

    @property
    def warning_delay(self) -> 'MutableDecofReal':
        return self._warning_delay

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def shutdown_delay(self) -> 'MutableDecofReal':
        return self._shutdown_delay

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def seed(self) -> 'DecofBoolean':
        return self._seed


class AmpFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power = MutableDecofReal(client, name + ':power')
        self._seedonly_check = AmpFactorySeedonly(client, name + ':seedonly-check')
        self._modified = DecofBoolean(client, name + ':modified')
        self._output_limits = AmpFactoryPower(client, name + ':output-limits')
        self._cc = AmpFactoryCc(client, name + ':cc')
        self._last_modified = DecofString(client, name + ':last-modified')
        self._wavelength = MutableDecofReal(client, name + ':wavelength')
        self._seed_limits = AmpFactoryPower(client, name + ':seed-limits')
        self._tc = TcFactorySettings(client, name + ':tc')

    @property
    def power(self) -> 'MutableDecofReal':
        return self._power

    @property
    def seedonly_check(self) -> 'AmpFactorySeedonly':
        return self._seedonly_check

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def output_limits(self) -> 'AmpFactoryPower':
        return self._output_limits

    @property
    def cc(self) -> 'AmpFactoryCc':
        return self._cc

    @property
    def last_modified(self) -> 'DecofString':
        return self._last_modified

    @property
    def wavelength(self) -> 'MutableDecofReal':
        return self._wavelength

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
        self._power_max_warning_delay = MutableDecofReal(client, name + ':power-max-warning-delay')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._power_min_shutdown_delay = MutableDecofReal(client, name + ':power-min-shutdown-delay')
        self._power_min = MutableDecofReal(client, name + ':power-min')
        self._power_max_shutdown_delay = MutableDecofReal(client, name + ':power-max-shutdown-delay')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')
        self._power_max = MutableDecofReal(client, name + ':power-max')
        self._power_min_warning_delay = MutableDecofReal(client, name + ':power-min-warning-delay')

    @property
    def power_max_warning_delay(self) -> 'MutableDecofReal':
        return self._power_max_warning_delay

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def power_min_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_min_shutdown_delay

    @property
    def power_min(self) -> 'MutableDecofReal':
        return self._power_min

    @property
    def power_max_shutdown_delay(self) -> 'MutableDecofReal':
        return self._power_max_shutdown_delay

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset

    @property
    def power_max(self) -> 'MutableDecofReal':
        return self._power_max

    @property
    def power_min_warning_delay(self) -> 'MutableDecofReal':
        return self._power_min_warning_delay


class AmpFactoryCc:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._current_clip_modified = DecofBoolean(client, name + ':current-clip-modified')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._current_clip_last_modified = DecofString(client, name + ':current-clip-last-modified')

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def current_clip_modified(self) -> 'DecofBoolean':
        return self._current_clip_modified

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def current_clip_last_modified(self) -> 'DecofString':
        return self._current_clip_last_modified


class TcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._d_gain = MutableDecofReal(client, name + ':d-gain')
        self._p_gain = MutableDecofReal(client, name + ':p-gain')
        self._temp_set = MutableDecofReal(client, name + ':temp-set')
        self._c_gain = MutableDecofReal(client, name + ':c-gain')
        self._current_max = MutableDecofReal(client, name + ':current-max')
        self._temp_max = MutableDecofReal(client, name + ':temp-max')
        self._temp_min = MutableDecofReal(client, name + ':temp-min')
        self._ntc_series_resistance = MutableDecofReal(client, name + ':ntc-series-resistance')
        self._temp_roc_enabled = MutableDecofBoolean(client, name + ':temp-roc-enabled')
        self._power_source = MutableDecofInteger(client, name + ':power-source')
        self._ok_time = MutableDecofReal(client, name + ':ok-time')
        self._temp_roc_limit = MutableDecofReal(client, name + ':temp-roc-limit')
        self._current_min = MutableDecofReal(client, name + ':current-min')
        self._timeout = MutableDecofInteger(client, name + ':timeout')
        self._ok_tolerance = MutableDecofReal(client, name + ':ok-tolerance')
        self._i_gain = MutableDecofReal(client, name + ':i-gain')

    @property
    def d_gain(self) -> 'MutableDecofReal':
        return self._d_gain

    @property
    def p_gain(self) -> 'MutableDecofReal':
        return self._p_gain

    @property
    def temp_set(self) -> 'MutableDecofReal':
        return self._temp_set

    @property
    def c_gain(self) -> 'MutableDecofReal':
        return self._c_gain

    @property
    def current_max(self) -> 'MutableDecofReal':
        return self._current_max

    @property
    def temp_max(self) -> 'MutableDecofReal':
        return self._temp_max

    @property
    def temp_min(self) -> 'MutableDecofReal':
        return self._temp_min

    @property
    def ntc_series_resistance(self) -> 'MutableDecofReal':
        return self._ntc_series_resistance

    @property
    def temp_roc_enabled(self) -> 'MutableDecofBoolean':
        return self._temp_roc_enabled

    @property
    def power_source(self) -> 'MutableDecofInteger':
        return self._power_source

    @property
    def ok_time(self) -> 'MutableDecofReal':
        return self._ok_time

    @property
    def temp_roc_limit(self) -> 'MutableDecofReal':
        return self._temp_roc_limit

    @property
    def current_min(self) -> 'MutableDecofReal':
        return self._current_min

    @property
    def timeout(self) -> 'MutableDecofInteger':
        return self._timeout

    @property
    def ok_tolerance(self) -> 'MutableDecofReal':
        return self._ok_tolerance

    @property
    def i_gain(self) -> 'MutableDecofReal':
        return self._i_gain


class ScopeT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channel1 = ScopeChannelT(client, name + ':channel1')
        self._data = DecofBinary(client, name + ':data')
        self._variant = MutableDecofInteger(client, name + ':variant')
        self._channelx = ScopeXAxisT(client, name + ':channelx')
        self._timescale = MutableDecofReal(client, name + ':timescale')
        self._channel2 = ScopeChannelT(client, name + ':channel2')
        self._update_rate = MutableDecofInteger(client, name + ':update-rate')

    @property
    def channel1(self) -> 'ScopeChannelT':
        return self._channel1

    @property
    def data(self) -> 'DecofBinary':
        return self._data

    @property
    def variant(self) -> 'MutableDecofInteger':
        return self._variant

    @property
    def channelx(self) -> 'ScopeXAxisT':
        return self._channelx

    @property
    def timescale(self) -> 'MutableDecofReal':
        return self._timescale

    @property
    def channel2(self) -> 'ScopeChannelT':
        return self._channel2

    @property
    def update_rate(self) -> 'MutableDecofInteger':
        return self._update_rate


class ScopeChannelT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._unit = DecofString(client, name + ':unit')
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._name = DecofString(client, name + ':name')

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def name(self) -> 'DecofString':
        return self._name


class ScopeXAxisT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._xy_signal = MutableDecofInteger(client, name + ':xy-signal')
        self._spectrum_omit_dc = MutableDecofBoolean(client, name + ':spectrum-omit-dc')
        self._scope_timescale = MutableDecofReal(client, name + ':scope-timescale')
        self._spectrum_range = MutableDecofReal(client, name + ':spectrum-range')
        self._unit = DecofString(client, name + ':unit')
        self._name = DecofString(client, name + ':name')

    @property
    def xy_signal(self) -> 'MutableDecofInteger':
        return self._xy_signal

    @property
    def spectrum_omit_dc(self) -> 'MutableDecofBoolean':
        return self._spectrum_omit_dc

    @property
    def scope_timescale(self) -> 'MutableDecofReal':
        return self._scope_timescale

    @property
    def spectrum_range(self) -> 'MutableDecofReal':
        return self._spectrum_range

    @property
    def unit(self) -> 'DecofString':
        return self._unit

    @property
    def name(self) -> 'DecofString':
        return self._name


class CtlT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._scan = CtlScanT(client, name + ':scan')
        self._power = CtlPower(client, name + ':power')
        self._wavelength_max = DecofReal(client, name + ':wavelength-max')
        self._motor = CtlMotor(client, name + ':motor')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._wavelength_min = DecofReal(client, name + ':wavelength-min')
        self._wavelength_set = MutableDecofReal(client, name + ':wavelength-set')
        self._state = DecofInteger(client, name + ':state')
        self._tuning_current_min = DecofReal(client, name + ':tuning-current-min')
        self._optimization = CtlOptimizationT(client, name + ':optimization')
        self._remote_control = CtlRemoteControl(client, name + ':remote-control')
        self._tuning_power_min = DecofReal(client, name + ':tuning-power-min')
        self._factory_settings = CtlFactory(client, name + ':factory-settings')
        self._mode_control = CtlModeControl(client, name + ':mode-control')
        self._head_temperature = DecofReal(client, name + ':head-temperature')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._wavelength_act = DecofReal(client, name + ':wavelength-act')

    @property
    def scan(self) -> 'CtlScanT':
        return self._scan

    @property
    def power(self) -> 'CtlPower':
        return self._power

    @property
    def wavelength_max(self) -> 'DecofReal':
        return self._wavelength_max

    @property
    def motor(self) -> 'CtlMotor':
        return self._motor

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def wavelength_min(self) -> 'DecofReal':
        return self._wavelength_min

    @property
    def wavelength_set(self) -> 'MutableDecofReal':
        return self._wavelength_set

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def tuning_current_min(self) -> 'DecofReal':
        return self._tuning_current_min

    @property
    def optimization(self) -> 'CtlOptimizationT':
        return self._optimization

    @property
    def remote_control(self) -> 'CtlRemoteControl':
        return self._remote_control

    @property
    def tuning_power_min(self) -> 'DecofReal':
        return self._tuning_power_min

    @property
    def factory_settings(self) -> 'CtlFactory':
        return self._factory_settings

    @property
    def mode_control(self) -> 'CtlModeControl':
        return self._mode_control

    @property
    def head_temperature(self) -> 'DecofReal':
        return self._head_temperature

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def wavelength_act(self) -> 'DecofReal':
        return self._wavelength_act


class CtlScanT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._wavelength_begin = MutableDecofReal(client, name + ':wavelength-begin')
        self._progress = DecofInteger(client, name + ':progress')
        self._microsteps = MutableDecofBoolean(client, name + ':microsteps')
        self._speed = MutableDecofReal(client, name + ':speed')
        self._continuous_mode = MutableDecofBoolean(client, name + ':continuous-mode')
        self._trigger = CtlTriggerT(client, name + ':trigger')
        self._remaining_time = DecofInteger(client, name + ':remaining-time')
        self._wavelength_end = MutableDecofReal(client, name + ':wavelength-end')
        self._speed_max = DecofReal(client, name + ':speed-max')
        self._speed_min = DecofReal(client, name + ':speed-min')
        self._shape = MutableDecofInteger(client, name + ':shape')

    @property
    def wavelength_begin(self) -> 'MutableDecofReal':
        return self._wavelength_begin

    @property
    def progress(self) -> 'DecofInteger':
        return self._progress

    @property
    def microsteps(self) -> 'MutableDecofBoolean':
        return self._microsteps

    @property
    def speed(self) -> 'MutableDecofReal':
        return self._speed

    @property
    def continuous_mode(self) -> 'MutableDecofBoolean':
        return self._continuous_mode

    @property
    def trigger(self) -> 'CtlTriggerT':
        return self._trigger

    @property
    def remaining_time(self) -> 'DecofInteger':
        return self._remaining_time

    @property
    def wavelength_end(self) -> 'MutableDecofReal':
        return self._wavelength_end

    @property
    def speed_max(self) -> 'DecofReal':
        return self._speed_max

    @property
    def speed_min(self) -> 'DecofReal':
        return self._speed_min

    @property
    def shape(self) -> 'MutableDecofInteger':
        return self._shape

    async def start(self) -> None:
        await self.__client.exec(self.__name + ':start', input_stream=None, output_type=None, return_type=None)

    async def continue_(self) -> None:
        await self.__client.exec(self.__name + ':continue', input_stream=None, output_type=None, return_type=None)

    async def pause(self) -> None:
        await self.__client.exec(self.__name + ':pause', input_stream=None, output_type=None, return_type=None)

    async def stop(self) -> None:
        await self.__client.exec(self.__name + ':stop', input_stream=None, output_type=None, return_type=None)


class CtlTriggerT:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._output_threshold = MutableDecofReal(client, name + ':output-threshold')
        self._input_enabled = MutableDecofBoolean(client, name + ':input-enabled')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._output_enabled = MutableDecofBoolean(client, name + ':output-enabled')

    @property
    def output_threshold(self) -> 'MutableDecofReal':
        return self._output_threshold

    @property
    def input_enabled(self) -> 'MutableDecofBoolean':
        return self._input_enabled

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def output_enabled(self) -> 'MutableDecofBoolean':
        return self._output_enabled


class CtlPower:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power_act = DecofReal(client, name + ':power-act')

    @property
    def power_act(self) -> 'DecofReal':
        return self._power_act


class CtlMotor:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._position_hysteresis = MutableDecofInteger(client, name + ':position-hysteresis')
        self._power_save_disabled = MutableDecofBoolean(client, name + ':power-save-disabled')
        self._position_accuracy = MutableDecofInteger(client, name + ':position-accuracy')

    @property
    def position_hysteresis(self) -> 'MutableDecofInteger':
        return self._position_hysteresis

    @property
    def power_save_disabled(self) -> 'MutableDecofBoolean':
        return self._power_save_disabled

    @property
    def position_accuracy(self) -> 'MutableDecofInteger':
        return self._position_accuracy


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

    async def abort(self) -> None:
        await self.__client.exec(self.__name + ':abort', input_stream=None, output_type=None, return_type=None)

    async def smile(self) -> None:
        await self.__client.exec(self.__name + ':smile', input_stream=None, output_type=None, return_type=None)


class CtlRemoteControl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._signal = MutableDecofInteger(client, name + ':signal')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._speed = MutableDecofReal(client, name + ':speed')
        self._factor = MutableDecofReal(client, name + ':factor')

    @property
    def signal(self) -> 'MutableDecofInteger':
        return self._signal

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def speed(self) -> 'MutableDecofReal':
        return self._speed

    @property
    def factor(self) -> 'MutableDecofReal':
        return self._factor


class CtlFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._tuning_current_min = DecofReal(client, name + ':tuning-current-min')
        self._tuning_power_min = DecofReal(client, name + ':tuning-power-min')
        self._wavelength_max = DecofReal(client, name + ':wavelength-max')
        self._wavelength_min = DecofReal(client, name + ':wavelength-min')

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
    def wavelength_min(self) -> 'DecofReal':
        return self._wavelength_min

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class CtlModeControl:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._loop_enabled = MutableDecofBoolean(client, name + ':loop-enabled')

    @property
    def loop_enabled(self) -> 'MutableDecofBoolean':
        return self._loop_enabled


class LaserHead:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._legacy = DecofBoolean(client, name + ':legacy')
        self._lock = Lock(client, name + ':lock')
        self._cc = CurrDrv1(client, name + ':cc')
        self._ontime_txt = DecofString(client, name + ':ontime-txt')
        self._ontime = DecofInteger(client, name + ':ontime')
        self._type_ = DecofString(client, name + ':type')
        self._factory_settings = LhFactory(client, name + ':factory-settings')
        self._tc = TcChannel(client, name + ':tc')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._pc = PiezoDrv1(client, name + ':pc')
        self._version = DecofString(client, name + ':version')

    @property
    def legacy(self) -> 'DecofBoolean':
        return self._legacy

    @property
    def lock(self) -> 'Lock':
        return self._lock

    @property
    def cc(self) -> 'CurrDrv1':
        return self._cc

    @property
    def ontime_txt(self) -> 'DecofString':
        return self._ontime_txt

    @property
    def ontime(self) -> 'DecofInteger':
        return self._ontime

    @property
    def type_(self) -> 'DecofString':
        return self._type_

    @property
    def factory_settings(self) -> 'LhFactory':
        return self._factory_settings

    @property
    def tc(self) -> 'TcChannel':
        return self._tc

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def pc(self) -> 'PiezoDrv1':
        return self._pc

    @property
    def version(self) -> 'DecofString':
        return self._version

    async def restore(self) -> None:
        await self.__client.exec(self.__name + ':restore', input_stream=None, output_type=None, return_type=None)

    async def store(self) -> None:
        await self.__client.exec(self.__name + ':store', input_stream=None, output_type=None, return_type=None)


class Lock:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._relock = AlRelock(client, name + ':relock')
        self._pid1 = Pid(client, name + ':pid1')
        self._state_txt = DecofString(client, name + ':state-txt')
        self._candidate_filter = AlCandidateFilter(client, name + ':candidate-filter')
        self._lock_enabled = MutableDecofBoolean(client, name + ':lock-enabled')
        self._window = AlWindow(client, name + ':window')
        self._candidates = DecofBinary(client, name + ':candidates')
        self._pid2 = Pid(client, name + ':pid2')
        self._locking_delay = MutableDecofInteger(client, name + ':locking-delay')
        self._lockpoint = AlLockpoint(client, name + ':lockpoint')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._state = DecofInteger(client, name + ':state')
        self._type_ = MutableDecofInteger(client, name + ':type')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._lockin = Lockin(client, name + ':lockin')
        self._pid_selection = MutableDecofInteger(client, name + ':pid-selection')
        self._reset = AlReset(client, name + ':reset')
        self._spectrum_input_channel = MutableDecofInteger(client, name + ':spectrum-input-channel')
        self._background_trace = DecofBinary(client, name + ':background-trace')

    @property
    def relock(self) -> 'AlRelock':
        return self._relock

    @property
    def pid1(self) -> 'Pid':
        return self._pid1

    @property
    def state_txt(self) -> 'DecofString':
        return self._state_txt

    @property
    def candidate_filter(self) -> 'AlCandidateFilter':
        return self._candidate_filter

    @property
    def lock_enabled(self) -> 'MutableDecofBoolean':
        return self._lock_enabled

    @property
    def window(self) -> 'AlWindow':
        return self._window

    @property
    def candidates(self) -> 'DecofBinary':
        return self._candidates

    @property
    def pid2(self) -> 'Pid':
        return self._pid2

    @property
    def locking_delay(self) -> 'MutableDecofInteger':
        return self._locking_delay

    @property
    def lockpoint(self) -> 'AlLockpoint':
        return self._lockpoint

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def type_(self) -> 'MutableDecofInteger':
        return self._type_

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def lockin(self) -> 'Lockin':
        return self._lockin

    @property
    def pid_selection(self) -> 'MutableDecofInteger':
        return self._pid_selection

    @property
    def reset(self) -> 'AlReset':
        return self._reset

    @property
    def spectrum_input_channel(self) -> 'MutableDecofInteger':
        return self._spectrum_input_channel

    @property
    def background_trace(self) -> 'DecofBinary':
        return self._background_trace

    async def show_candidates(self) -> Tuple[str, int]:
        return await self.__client.exec(self.__name + ':show-candidates', input_stream=None, output_type=str, return_type=int)

    async def stop_scan(self) -> None:
        await self.__client.exec(self.__name + ':stop-scan', input_stream=None, output_type=None, return_type=None)

    async def open(self) -> None:
        await self.__client.exec(self.__name + ':open', input_stream=None, output_type=None, return_type=None)

    async def start_scan(self) -> None:
        await self.__client.exec(self.__name + ':start-scan', input_stream=None, output_type=None, return_type=None)

    async def close(self) -> None:
        await self.__client.exec(self.__name + ':close', input_stream=None, output_type=None, return_type=None)

    async def select_lockpoint(self, x: float, y: float, type_: int) -> None:
        assert isinstance(x, float), "expected type 'float' for parameter 'x', got '{}'".format(type(x))
        assert isinstance(y, float), "expected type 'float' for parameter 'y', got '{}'".format(type(y))
        assert isinstance(type_, int), "expected type 'int' for parameter 'type_', got '{}'".format(type(type_))
        await self.__client.exec(self.__name + ':select-lockpoint', x, y, type_, input_stream=None, output_type=None, return_type=None)

    async def find_candidates(self) -> None:
        await self.__client.exec(self.__name + ':find-candidates', input_stream=None, output_type=None, return_type=None)


class AlRelock:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._delay = MutableDecofReal(client, name + ':delay')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')

    @property
    def delay(self) -> 'MutableDecofReal':
        return self._delay

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel


class Pid:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._sign = MutableDecofBoolean(client, name + ':sign')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._lock_state = DecofBoolean(client, name + ':lock-state')
        self._output_channel = MutableDecofInteger(client, name + ':output-channel')
        self._slope = MutableDecofBoolean(client, name + ':slope')
        self._outputlimit = Outputlimit(client, name + ':outputlimit')
        self._hold_state = DecofBoolean(client, name + ':hold-state')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._regulating_state = DecofBoolean(client, name + ':regulating-state')
        self._hold = MutableDecofBoolean(client, name + ':hold')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._gain = Gain(client, name + ':gain')
        self._hold_output_on_unlock = MutableDecofBoolean(client, name + ':hold-output-on-unlock')

    @property
    def sign(self) -> 'MutableDecofBoolean':
        return self._sign

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def lock_state(self) -> 'DecofBoolean':
        return self._lock_state

    @property
    def output_channel(self) -> 'MutableDecofInteger':
        return self._output_channel

    @property
    def slope(self) -> 'MutableDecofBoolean':
        return self._slope

    @property
    def outputlimit(self) -> 'Outputlimit':
        return self._outputlimit

    @property
    def hold_state(self) -> 'DecofBoolean':
        return self._hold_state

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def regulating_state(self) -> 'DecofBoolean':
        return self._regulating_state

    @property
    def hold(self) -> 'MutableDecofBoolean':
        return self._hold

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def gain(self) -> 'Gain':
        return self._gain

    @property
    def hold_output_on_unlock(self) -> 'MutableDecofBoolean':
        return self._hold_output_on_unlock


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


class Gain:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._i_cutoff = MutableDecofReal(client, name + ':i-cutoff')
        self._fc_ip = DecofReal(client, name + ':fc-ip')
        self._p = MutableDecofReal(client, name + ':p')
        self._i = MutableDecofReal(client, name + ':i')
        self._all = MutableDecofReal(client, name + ':all')
        self._i_cutoff_enabled = MutableDecofBoolean(client, name + ':i-cutoff-enabled')
        self._fc_pd = DecofReal(client, name + ':fc-pd')
        self._d = MutableDecofReal(client, name + ':d')

    @property
    def i_cutoff(self) -> 'MutableDecofReal':
        return self._i_cutoff

    @property
    def fc_ip(self) -> 'DecofReal':
        return self._fc_ip

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def i_cutoff_enabled(self) -> 'MutableDecofBoolean':
        return self._i_cutoff_enabled

    @property
    def fc_pd(self) -> 'DecofReal':
        return self._fc_pd

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d


class AlCandidateFilter:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._negative_edge = MutableDecofBoolean(client, name + ':negative-edge')
        self._positive_edge = MutableDecofBoolean(client, name + ':positive-edge')
        self._top = MutableDecofBoolean(client, name + ':top')
        self._bottom = MutableDecofBoolean(client, name + ':bottom')
        self._edge_min_distance = MutableDecofInteger(client, name + ':edge-min-distance')
        self._peak_noise_tolerance = MutableDecofReal(client, name + ':peak-noise-tolerance')
        self._edge_level = MutableDecofReal(client, name + ':edge-level')

    @property
    def negative_edge(self) -> 'MutableDecofBoolean':
        return self._negative_edge

    @property
    def positive_edge(self) -> 'MutableDecofBoolean':
        return self._positive_edge

    @property
    def top(self) -> 'MutableDecofBoolean':
        return self._top

    @property
    def bottom(self) -> 'MutableDecofBoolean':
        return self._bottom

    @property
    def edge_min_distance(self) -> 'MutableDecofInteger':
        return self._edge_min_distance

    @property
    def peak_noise_tolerance(self) -> 'MutableDecofReal':
        return self._peak_noise_tolerance

    @property
    def edge_level(self) -> 'MutableDecofReal':
        return self._edge_level


class AlWindow:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_low = MutableDecofReal(client, name + ':level-low')
        self._level_high = MutableDecofReal(client, name + ':level-high')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')

    @property
    def level_low(self) -> 'MutableDecofReal':
        return self._level_low

    @property
    def level_high(self) -> 'MutableDecofReal':
        return self._level_high

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis


class AlLockpoint:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._position = Coordinate(client, name + ':position')
        self._type_ = DecofString(client, name + ':type')

    @property
    def position(self) -> 'Coordinate':
        return self._position

    @property
    def type_(self) -> 'DecofString':
        return self._type_


class Coordinate:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name

    async def get(self) -> Tuple[float, float]:
        return await self.__client.get(self.__name)

    async def set(self, y: float, x: float) -> None:
        assert isinstance(y, float), "expected type 'float' for 'y', got '{}'".format(type(y))
        assert isinstance(x, float), "expected type 'float' for 'x', got '{}'".format(type(x))
        await self.__client.set(self.__name, y, x)


class Lockin:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._phase_shift = MutableDecofReal(client, name + ':phase-shift')
        self._amplitude = MutableDecofReal(client, name + ':amplitude')
        self._lock_level = MutableDecofReal(client, name + ':lock-level')
        self._modulation_output_channel = MutableDecofInteger(client, name + ':modulation-output-channel')
        self._frequency = MutableDecofReal(client, name + ':frequency')
        self._modulation_enabled = MutableDecofBoolean(client, name + ':modulation-enabled')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')

    @property
    def phase_shift(self) -> 'MutableDecofReal':
        return self._phase_shift

    @property
    def amplitude(self) -> 'MutableDecofReal':
        return self._amplitude

    @property
    def lock_level(self) -> 'MutableDecofReal':
        return self._lock_level

    @property
    def modulation_output_channel(self) -> 'MutableDecofInteger':
        return self._modulation_output_channel

    @property
    def frequency(self) -> 'MutableDecofReal':
        return self._frequency

    @property
    def modulation_enabled(self) -> 'MutableDecofBoolean':
        return self._modulation_enabled

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel


class AlReset:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._enabled = MutableDecofBoolean(client, name + ':enabled')

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled


class CurrDrv1:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._emission = DecofBoolean(client, name + ':emission')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._variant = DecofString(client, name + ':variant')
        self._forced_off = MutableDecofBoolean(client, name + ':forced-off')
        self._path = DecofString(client, name + ':path')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')
        self._current_act = DecofReal(client, name + ':current-act')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._status = DecofInteger(client, name + ':status')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._current_offset = MutableDecofReal(client, name + ':current-offset')
        self._output_filter = OutputFilter1(client, name + ':output-filter')
        self._current_clip_limit = DecofReal(client, name + ':current-clip-limit')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._aux = DecofReal(client, name + ':aux')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._pd = DecofReal(client, name + ':pd')
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._external_input = ExtInput1(client, name + ':external-input')
        self._voltage_act = DecofReal(client, name + ':voltage-act')
        self._current_set_dithering = MutableDecofBoolean(client, name + ':current-set-dithering')

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def variant(self) -> 'DecofString':
        return self._variant

    @property
    def forced_off(self) -> 'MutableDecofBoolean':
        return self._forced_off

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber

    @property
    def current_act(self) -> 'DecofReal':
        return self._current_act

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def current_offset(self) -> 'MutableDecofReal':
        return self._current_offset

    @property
    def output_filter(self) -> 'OutputFilter1':
        return self._output_filter

    @property
    def current_clip_limit(self) -> 'DecofReal':
        return self._current_clip_limit

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def aux(self) -> 'DecofReal':
        return self._aux

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def pd(self) -> 'DecofReal':
        return self._pd

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def external_input(self) -> 'ExtInput1':
        return self._external_input

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act

    @property
    def current_set_dithering(self) -> 'MutableDecofBoolean':
        return self._current_set_dithering


class LhFactory:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power = MutableDecofReal(client, name + ':power')
        self._modified = DecofBoolean(client, name + ':modified')
        self._cc = LhFactoryCc(client, name + ':cc')
        self._last_modified = DecofString(client, name + ':last-modified')
        self._wavelength = MutableDecofReal(client, name + ':wavelength')
        self._pc = PcFactorySettings(client, name + ':pc')
        self._threshold_current = MutableDecofReal(client, name + ':threshold-current')
        self._tc = TcFactorySettings(client, name + ':tc')

    @property
    def power(self) -> 'MutableDecofReal':
        return self._power

    @property
    def modified(self) -> 'DecofBoolean':
        return self._modified

    @property
    def cc(self) -> 'LhFactoryCc':
        return self._cc

    @property
    def last_modified(self) -> 'DecofString':
        return self._last_modified

    @property
    def wavelength(self) -> 'MutableDecofReal':
        return self._wavelength

    @property
    def pc(self) -> 'PcFactorySettings':
        return self._pc

    @property
    def threshold_current(self) -> 'MutableDecofReal':
        return self._threshold_current

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
        self._voltage_clip = MutableDecofReal(client, name + ':voltage-clip')
        self._positive_polarity = MutableDecofBoolean(client, name + ':positive-polarity')
        self._current_clip = MutableDecofReal(client, name + ':current-clip')
        self._current_clip_modified = DecofBoolean(client, name + ':current-clip-modified')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._snubber = MutableDecofBoolean(client, name + ':snubber')
        self._current_set = MutableDecofReal(client, name + ':current-set')
        self._current_clip_last_modified = DecofString(client, name + ':current-clip-last-modified')

    @property
    def voltage_clip(self) -> 'MutableDecofReal':
        return self._voltage_clip

    @property
    def positive_polarity(self) -> 'MutableDecofBoolean':
        return self._positive_polarity

    @property
    def current_clip(self) -> 'MutableDecofReal':
        return self._current_clip

    @property
    def current_clip_modified(self) -> 'DecofBoolean':
        return self._current_clip_modified

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def snubber(self) -> 'MutableDecofBoolean':
        return self._snubber

    @property
    def current_set(self) -> 'MutableDecofReal':
        return self._current_set

    @property
    def current_clip_last_modified(self) -> 'DecofString':
        return self._current_clip_last_modified


class PcFactorySettings:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._slew_rate_enabled = MutableDecofBoolean(client, name + ':slew-rate-enabled')
        self._slew_rate = MutableDecofReal(client, name + ':slew-rate')
        self._scan_offset = MutableDecofReal(client, name + ':scan-offset')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._scan_amplitude = MutableDecofReal(client, name + ':scan-amplitude')
        self._capacitance = MutableDecofReal(client, name + ':capacitance')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')

    @property
    def slew_rate_enabled(self) -> 'MutableDecofBoolean':
        return self._slew_rate_enabled

    @property
    def slew_rate(self) -> 'MutableDecofReal':
        return self._slew_rate

    @property
    def scan_offset(self) -> 'MutableDecofReal':
        return self._scan_offset

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def scan_amplitude(self) -> 'MutableDecofReal':
        return self._scan_amplitude

    @property
    def capacitance(self) -> 'MutableDecofReal':
        return self._capacitance

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor


class PdExt:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._power = DecofReal(client, name + ':power')
        self._photodiode = DecofReal(client, name + ':photodiode')
        self._cal_factor = MutableDecofReal(client, name + ':cal-factor')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._cal_offset = MutableDecofReal(client, name + ':cal-offset')

    @property
    def power(self) -> 'DecofReal':
        return self._power

    @property
    def photodiode(self) -> 'DecofReal':
        return self._photodiode

    @property
    def cal_factor(self) -> 'MutableDecofReal':
        return self._cal_factor

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def cal_offset(self) -> 'MutableDecofReal':
        return self._cal_offset


class PwrStab:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._sign = MutableDecofBoolean(client, name + ':sign')
        self._output_channel = DecofInteger(client, name + ':output-channel')
        self._window = PwrStabWindow(client, name + ':window')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._input_channel_value_act = DecofReal(client, name + ':input-channel-value-act')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._setpoint = MutableDecofReal(client, name + ':setpoint')
        self._state = DecofInteger(client, name + ':state')
        self._input_channel = MutableDecofInteger(client, name + ':input-channel')
        self._gain = PwrStabGain(client, name + ':gain')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._hold_output_on_unlock = MutableDecofBoolean(client, name + ':hold-output-on-unlock')

    @property
    def sign(self) -> 'MutableDecofBoolean':
        return self._sign

    @property
    def output_channel(self) -> 'DecofInteger':
        return self._output_channel

    @property
    def window(self) -> 'PwrStabWindow':
        return self._window

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def input_channel_value_act(self) -> 'DecofReal':
        return self._input_channel_value_act

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def setpoint(self) -> 'MutableDecofReal':
        return self._setpoint

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def input_channel(self) -> 'MutableDecofInteger':
        return self._input_channel

    @property
    def gain(self) -> 'PwrStabGain':
        return self._gain

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def hold_output_on_unlock(self) -> 'MutableDecofBoolean':
        return self._hold_output_on_unlock


class PwrStabWindow:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._level_low = MutableDecofReal(client, name + ':level-low')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._level_hysteresis = MutableDecofReal(client, name + ':level-hysteresis')

    @property
    def level_low(self) -> 'MutableDecofReal':
        return self._level_low

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def level_hysteresis(self) -> 'MutableDecofReal':
        return self._level_hysteresis


class PwrStabGain:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._all = MutableDecofReal(client, name + ':all')
        self._d = MutableDecofReal(client, name + ':d')
        self._p = MutableDecofReal(client, name + ':p')
        self._i = MutableDecofReal(client, name + ':i')

    @property
    def all(self) -> 'MutableDecofReal':
        return self._all

    @property
    def d(self) -> 'MutableDecofReal':
        return self._d

    @property
    def p(self) -> 'MutableDecofReal':
        return self._p

    @property
    def i(self) -> 'MutableDecofReal':
        return self._i


class TcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._channel1 = TcChannel(client, name + ':channel1')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._fpga_fw_ver = DecofString(client, name + ':fpga-fw-ver')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._revision = DecofString(client, name + ':revision')
        self._channel2 = TcChannel(client, name + ':channel2')
        self._slot = DecofString(client, name + ':slot')

    @property
    def channel1(self) -> 'TcChannel':
        return self._channel1

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def fpga_fw_ver(self) -> 'DecofString':
        return self._fpga_fw_ver

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def channel2(self) -> 'TcChannel':
        return self._channel2

    @property
    def slot(self) -> 'DecofString':
        return self._slot


class Display:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._state = DecofInteger(client, name + ':state')
        self._idle_timeout = MutableDecofInteger(client, name + ':idle-timeout')
        self._brightness = MutableDecofReal(client, name + ':brightness')
        self._auto_dark = MutableDecofBoolean(client, name + ':auto-dark')

    @property
    def state(self) -> 'DecofInteger':
        return self._state

    @property
    def idle_timeout(self) -> 'MutableDecofInteger':
        return self._idle_timeout

    @property
    def brightness(self) -> 'MutableDecofReal':
        return self._brightness

    @property
    def auto_dark(self) -> 'MutableDecofBoolean':
        return self._auto_dark

    async def update_state(self, active: bool) -> None:
        assert isinstance(active, bool), "expected type 'bool' for parameter 'active', got '{}'".format(type(active))
        await self.__client.exec(self.__name + ':update-state', active, input_stream=None, output_type=None, return_type=None)


class IoBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._digital_out3 = IoDigitalOutput(client, name + ':digital-out3')
        self._digital_in2 = IoDigitalInput(client, name + ':digital-in2')
        self._digital_out2 = IoDigitalOutput(client, name + ':digital-out2')
        self._out_a = IoOutputChannel(client, name + ':out-a')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._digital_in0 = IoDigitalInput(client, name + ':digital-in0')
        self._digital_out0 = IoDigitalOutput(client, name + ':digital-out0')
        self._digital_in1 = IoDigitalInput(client, name + ':digital-in1')
        self._digital_in3 = IoDigitalInput(client, name + ':digital-in3')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._digital_out1 = IoDigitalOutput(client, name + ':digital-out1')
        self._revision = DecofString(client, name + ':revision')
        self._out_b = IoOutputChannel(client, name + ':out-b')

    @property
    def digital_out3(self) -> 'IoDigitalOutput':
        return self._digital_out3

    @property
    def digital_in2(self) -> 'IoDigitalInput':
        return self._digital_in2

    @property
    def digital_out2(self) -> 'IoDigitalOutput':
        return self._digital_out2

    @property
    def out_a(self) -> 'IoOutputChannel':
        return self._out_a

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def digital_in0(self) -> 'IoDigitalInput':
        return self._digital_in0

    @property
    def digital_out0(self) -> 'IoDigitalOutput':
        return self._digital_out0

    @property
    def digital_in1(self) -> 'IoDigitalInput':
        return self._digital_in1

    @property
    def digital_in3(self) -> 'IoDigitalInput':
        return self._digital_in3

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def digital_out1(self) -> 'IoDigitalOutput':
        return self._digital_out1

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def out_b(self) -> 'IoOutputChannel':
        return self._out_b


class IoDigitalOutput:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._value_set = MutableDecofBoolean(client, name + ':value-set')
        self._mode = MutableDecofInteger(client, name + ':mode')
        self._invert = MutableDecofBoolean(client, name + ':invert')
        self._value_act = DecofBoolean(client, name + ':value-act')

    @property
    def value_set(self) -> 'MutableDecofBoolean':
        return self._value_set

    @property
    def mode(self) -> 'MutableDecofInteger':
        return self._mode

    @property
    def invert(self) -> 'MutableDecofBoolean':
        return self._invert

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
        self._external_input = ExtInput1(client, name + ':external-input')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')
        self._output_filter = OutputFilter1(client, name + ':output-filter')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._voltage_offset = MutableDecofReal(client, name + ':voltage-offset')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')

    @property
    def external_input(self) -> 'ExtInput1':
        return self._external_input

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set

    @property
    def output_filter(self) -> 'OutputFilter1':
        return self._output_filter

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def voltage_offset(self) -> 'MutableDecofReal':
        return self._voltage_offset

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min


class PcBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._status = DecofInteger(client, name + ':status')
        self._channel1 = PiezoDrv2(client, name + ':channel1')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._fpga_fw_ver = DecofInteger(client, name + ':fpga-fw-ver')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._revision = DecofString(client, name + ':revision')
        self._slot = DecofString(client, name + ':slot')

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def channel1(self) -> 'PiezoDrv2':
        return self._channel1

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def fpga_fw_ver(self) -> 'DecofInteger':
        return self._fpga_fw_ver

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def revision(self) -> 'DecofString':
        return self._revision

    @property
    def slot(self) -> 'DecofString':
        return self._slot


class PiezoDrv2:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._path = DecofString(client, name + ':path')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._feedforward_enabled = MutableDecofBoolean(client, name + ':feedforward-enabled')
        self._voltage_min = MutableDecofReal(client, name + ':voltage-min')
        self._status = DecofInteger(client, name + ':status')
        self._output_filter = OutputFilter2(client, name + ':output-filter')
        self._voltage_set = MutableDecofReal(client, name + ':voltage-set')
        self._enabled = MutableDecofBoolean(client, name + ':enabled')
        self._feedforward_master = MutableDecofInteger(client, name + ':feedforward-master')
        self._feedforward_factor = MutableDecofReal(client, name + ':feedforward-factor')
        self._external_input = ExtInput2(client, name + ':external-input')
        self._voltage_max = MutableDecofReal(client, name + ':voltage-max')
        self._voltage_set_dithering = MutableDecofBoolean(client, name + ':voltage-set-dithering')
        self._voltage_act = DecofReal(client, name + ':voltage-act')

    @property
    def path(self) -> 'DecofString':
        return self._path

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def feedforward_enabled(self) -> 'MutableDecofBoolean':
        return self._feedforward_enabled

    @property
    def voltage_min(self) -> 'MutableDecofReal':
        return self._voltage_min

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def output_filter(self) -> 'OutputFilter2':
        return self._output_filter

    @property
    def voltage_set(self) -> 'MutableDecofReal':
        return self._voltage_set

    @property
    def enabled(self) -> 'MutableDecofBoolean':
        return self._enabled

    @property
    def feedforward_master(self) -> 'MutableDecofInteger':
        return self._feedforward_master

    @property
    def feedforward_factor(self) -> 'MutableDecofReal':
        return self._feedforward_factor

    @property
    def external_input(self) -> 'ExtInput2':
        return self._external_input

    @property
    def voltage_max(self) -> 'MutableDecofReal':
        return self._voltage_max

    @property
    def voltage_set_dithering(self) -> 'MutableDecofBoolean':
        return self._voltage_set_dithering

    @property
    def voltage_act(self) -> 'DecofReal':
        return self._voltage_act


class McBoard:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._air_pressure = DecofReal(client, name + ':air-pressure')
        self._relative_humidity = DecofReal(client, name + ':relative-humidity')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._fpga_fw_ver = DecofString(client, name + ':fpga-fw-ver')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._revision = DecofString(client, name + ':revision')

    @property
    def air_pressure(self) -> 'DecofReal':
        return self._air_pressure

    @property
    def relative_humidity(self) -> 'DecofReal':
        return self._relative_humidity

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def fpga_fw_ver(self) -> 'DecofString':
        return self._fpga_fw_ver

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def revision(self) -> 'DecofString':
        return self._revision


class PowerSupply:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._status = DecofInteger(client, name + ':status')
        self._voltage_15Vn = DecofReal(client, name + ':voltage-15Vn')
        self._current_5V = DecofReal(client, name + ':current-5V')
        self._voltage_3V3 = DecofReal(client, name + ':voltage-3V3')
        self._board_temp = DecofReal(client, name + ':board-temp')
        self._current_15V = DecofReal(client, name + ':current-15V')
        self._voltage_5V = DecofReal(client, name + ':voltage-5V')
        self._current_15Vn = DecofReal(client, name + ':current-15Vn')
        self._status_txt = DecofString(client, name + ':status-txt')
        self._voltage_15V = DecofReal(client, name + ':voltage-15V')
        self._serial_number = DecofString(client, name + ':serial-number')
        self._load = DecofReal(client, name + ':load')
        self._heatsink_temp = DecofReal(client, name + ':heatsink-temp')
        self._revision = DecofString(client, name + ':revision')

    @property
    def status(self) -> 'DecofInteger':
        return self._status

    @property
    def voltage_15Vn(self) -> 'DecofReal':
        return self._voltage_15Vn

    @property
    def current_5V(self) -> 'DecofReal':
        return self._current_5V

    @property
    def voltage_3V3(self) -> 'DecofReal':
        return self._voltage_3V3

    @property
    def board_temp(self) -> 'DecofReal':
        return self._board_temp

    @property
    def current_15V(self) -> 'DecofReal':
        return self._current_15V

    @property
    def voltage_5V(self) -> 'DecofReal':
        return self._voltage_5V

    @property
    def current_15Vn(self) -> 'DecofReal':
        return self._current_15Vn

    @property
    def status_txt(self) -> 'DecofString':
        return self._status_txt

    @property
    def voltage_15V(self) -> 'DecofReal':
        return self._voltage_15V

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def load(self) -> 'DecofReal':
        return self._load

    @property
    def heatsink_temp(self) -> 'DecofReal':
        return self._heatsink_temp

    @property
    def revision(self) -> 'DecofString':
        return self._revision


class Buzzer:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._welcome = MutableDecofString(client, name + ':welcome')

    @property
    def welcome(self) -> 'MutableDecofString':
        return self._welcome

    async def play_welcome(self) -> None:
        await self.__client.exec(self.__name + ':play-welcome', input_stream=None, output_type=None, return_type=None)

    async def play(self, melody: str) -> None:
        assert isinstance(melody, str), "expected type 'str' for parameter 'melody', got '{}'".format(type(melody))
        await self.__client.exec(self.__name + ':play', melody, input_stream=None, output_type=None, return_type=None)


class BuildInformation:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._build_number = DecofInteger(client, name + ':build-number')
        self._build_id = DecofString(client, name + ':build-id')
        self._c_compiler_id = DecofString(client, name + ':c-compiler-id')
        self._job_name = DecofString(client, name + ':job-name')
        self._c_compiler_version = DecofString(client, name + ':c-compiler-version')
        self._build_url = DecofString(client, name + ':build-url')
        self._cxx_compiler_version = DecofString(client, name + ':cxx-compiler-version')
        self._build_node_name = DecofString(client, name + ':build-node-name')
        self._build_tag = DecofString(client, name + ':build-tag')
        self._cxx_compiler_id = DecofString(client, name + ':cxx-compiler-id')

    @property
    def build_number(self) -> 'DecofInteger':
        return self._build_number

    @property
    def build_id(self) -> 'DecofString':
        return self._build_id

    @property
    def c_compiler_id(self) -> 'DecofString':
        return self._c_compiler_id

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

    @property
    def build_node_name(self) -> 'DecofString':
        return self._build_node_name

    @property
    def build_tag(self) -> 'DecofString':
        return self._build_tag

    @property
    def cxx_compiler_id(self) -> 'DecofString':
        return self._cxx_compiler_id


class Ipconfig:
    def __init__(self, client: Client, name: str) -> None:
        self.__client = client
        self.__name = name
        self._net_mask = DecofString(client, name + ':net-mask')
        self._mac_addr = DecofString(client, name + ':mac-addr')
        self._dhcp = DecofBoolean(client, name + ':dhcp')
        self._ip_addr = DecofString(client, name + ':ip-addr')
        self._mon_port = DecofInteger(client, name + ':mon-port')
        self._cmd_port = DecofInteger(client, name + ':cmd-port')

    @property
    def net_mask(self) -> 'DecofString':
        return self._net_mask

    @property
    def mac_addr(self) -> 'DecofString':
        return self._mac_addr

    @property
    def dhcp(self) -> 'DecofBoolean':
        return self._dhcp

    @property
    def ip_addr(self) -> 'DecofString':
        return self._ip_addr

    @property
    def mon_port(self) -> 'DecofInteger':
        return self._mon_port

    @property
    def cmd_port(self) -> 'DecofInteger':
        return self._cmd_port

    async def set_ip(self, ip_addr: str, net_mask: str) -> None:
        assert isinstance(ip_addr, str), "expected type 'str' for parameter 'ip_addr', got '{}'".format(type(ip_addr))
        assert isinstance(net_mask, str), "expected type 'str' for parameter 'net_mask', got '{}'".format(type(net_mask))
        await self.__client.exec(self.__name + ':set-ip', ip_addr, net_mask, input_stream=None, output_type=None, return_type=None)

    async def set_dhcp(self) -> None:
        await self.__client.exec(self.__name + ':set-dhcp', input_stream=None, output_type=None, return_type=None)

    async def apply(self) -> None:
        await self.__client.exec(self.__name + ':apply', input_stream=None, output_type=None, return_type=None)


class DLCpro:
    def __init__(self, connection: Connection) -> None:
        self.__client = Client(connection)
        self._tan = DecofInteger(self.__client, 'tan')
        self._system_messages = SystemMessages(self.__client, 'system-messages')
        self._time = MutableDecofString(self.__client, 'time')
        self._licenses = Licenses(self.__client, 'licenses')
        self._fw_update = FwUpdate(self.__client, 'fw-update')
        self._system_service_report = ServiceReport(self.__client, 'system-service-report')
        self._emission = DecofBoolean(self.__client, 'emission')
        self._frontkey_locked = DecofBoolean(self.__client, 'frontkey-locked')
        self._ampcc1 = Cc5000Board(self.__client, 'ampcc1')
        self._cc1 = CcBoard(self.__client, 'cc1')
        self._standby = Standby(self.__client, 'standby')
        self._laser1 = Laser(self.__client, 'laser1')
        self._ampcc2 = Cc5000Board(self.__client, 'ampcc2')
        self._tc1 = TcBoard(self.__client, 'tc1')
        self._display = Display(self.__client, 'display')
        self._system_health = DecofInteger(self.__client, 'system-health')
        self._io = IoBoard(self.__client, 'io')
        self._interlock_open = DecofBoolean(self.__client, 'interlock-open')
        self._pc3 = PcBoard(self.__client, 'pc3')
        self._mc = McBoard(self.__client, 'mc')
        self._tc2 = TcBoard(self.__client, 'tc2')
        self._system_health_txt = DecofString(self.__client, 'system-health-txt')
        self._power_supply = PowerSupply(self.__client, 'power-supply')
        self._pc2 = PcBoard(self.__client, 'pc2')
        self._pc1 = PcBoard(self.__client, 'pc1')
        self._buzzer = Buzzer(self.__client, 'buzzer')
        self._ul = MutableDecofInteger(self.__client, 'ul')
        self._system_type = DecofString(self.__client, 'system-type')
        self._svn_revision = DecofString(self.__client, 'svn-revision')
        self._ssw_svn_revision = DecofString(self.__client, 'ssw-svn-revision')
        self._echo = MutableDecofBoolean(self.__client, 'echo')
        self._fw_ver = DecofString(self.__client, 'fw-ver')
        self._build_information = BuildInformation(self.__client, 'build-information')
        self._ssw_ver = DecofString(self.__client, 'ssw-ver')
        self._uptime = DecofInteger(self.__client, 'uptime')
        self._system_model = DecofString(self.__client, 'system-model')
        self._decof_svn_revision = DecofString(self.__client, 'decof-svn-revision')
        self._serial_number = DecofString(self.__client, 'serial-number')
        self._system_label = MutableDecofString(self.__client, 'system-label')
        self._uptime_txt = DecofString(self.__client, 'uptime-txt')
        self._decof_ver = DecofString(self.__client, 'decof-ver')
        self._net_conf = Ipconfig(self.__client, 'net-conf')

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
    def tan(self) -> 'DecofInteger':
        return self._tan

    @property
    def system_messages(self) -> 'SystemMessages':
        return self._system_messages

    @property
    def time(self) -> 'MutableDecofString':
        return self._time

    @property
    def licenses(self) -> 'Licenses':
        return self._licenses

    @property
    def fw_update(self) -> 'FwUpdate':
        return self._fw_update

    @property
    def system_service_report(self) -> 'ServiceReport':
        return self._system_service_report

    @property
    def emission(self) -> 'DecofBoolean':
        return self._emission

    @property
    def frontkey_locked(self) -> 'DecofBoolean':
        return self._frontkey_locked

    @property
    def ampcc1(self) -> 'Cc5000Board':
        return self._ampcc1

    @property
    def cc1(self) -> 'CcBoard':
        return self._cc1

    @property
    def standby(self) -> 'Standby':
        return self._standby

    @property
    def laser1(self) -> 'Laser':
        return self._laser1

    @property
    def ampcc2(self) -> 'Cc5000Board':
        return self._ampcc2

    @property
    def tc1(self) -> 'TcBoard':
        return self._tc1

    @property
    def display(self) -> 'Display':
        return self._display

    @property
    def system_health(self) -> 'DecofInteger':
        return self._system_health

    @property
    def io(self) -> 'IoBoard':
        return self._io

    @property
    def interlock_open(self) -> 'DecofBoolean':
        return self._interlock_open

    @property
    def pc3(self) -> 'PcBoard':
        return self._pc3

    @property
    def mc(self) -> 'McBoard':
        return self._mc

    @property
    def tc2(self) -> 'TcBoard':
        return self._tc2

    @property
    def system_health_txt(self) -> 'DecofString':
        return self._system_health_txt

    @property
    def power_supply(self) -> 'PowerSupply':
        return self._power_supply

    @property
    def pc2(self) -> 'PcBoard':
        return self._pc2

    @property
    def pc1(self) -> 'PcBoard':
        return self._pc1

    @property
    def buzzer(self) -> 'Buzzer':
        return self._buzzer

    @property
    def ul(self) -> 'MutableDecofInteger':
        return self._ul

    @property
    def system_type(self) -> 'DecofString':
        return self._system_type

    @property
    def svn_revision(self) -> 'DecofString':
        return self._svn_revision

    @property
    def ssw_svn_revision(self) -> 'DecofString':
        return self._ssw_svn_revision

    @property
    def echo(self) -> 'MutableDecofBoolean':
        return self._echo

    @property
    def fw_ver(self) -> 'DecofString':
        return self._fw_ver

    @property
    def build_information(self) -> 'BuildInformation':
        return self._build_information

    @property
    def ssw_ver(self) -> 'DecofString':
        return self._ssw_ver

    @property
    def uptime(self) -> 'DecofInteger':
        return self._uptime

    @property
    def system_model(self) -> 'DecofString':
        return self._system_model

    @property
    def decof_svn_revision(self) -> 'DecofString':
        return self._decof_svn_revision

    @property
    def serial_number(self) -> 'DecofString':
        return self._serial_number

    @property
    def system_label(self) -> 'MutableDecofString':
        return self._system_label

    @property
    def uptime_txt(self) -> 'DecofString':
        return self._uptime_txt

    @property
    def decof_ver(self) -> 'DecofString':
        return self._decof_ver

    @property
    def net_conf(self) -> 'Ipconfig':
        return self._net_conf

    async def service_script(self, stream_input: bytes) -> None:
        assert isinstance(stream_input, bytes), "expected type 'bytes' for parameter 'stream_input', got '{}'".format(type(stream_input))
        await self.__client.exec('service-script', input_stream=stream_input, output_type=None, return_type=None)

    async def debug_log(self) -> str:
        return await self.__client.exec('debug-log', input_stream=None, output_type=str, return_type=None)

    async def system_connections(self) -> Tuple[str, int]:
        return await self.__client.exec('system-connections', input_stream=None, output_type=str, return_type=int)

    async def error_log(self) -> str:
        return await self.__client.exec('error-log', input_stream=None, output_type=str, return_type=None)

    async def service_report(self) -> bytes:
        return await self.__client.exec('service-report', input_stream=None, output_type=bytes, return_type=None)

    async def service_log(self) -> str:
        return await self.__client.exec('service-log', input_stream=None, output_type=str, return_type=None)

    async def change_ul(self, ul: AccessLevel, passwd: str) -> int:
        assert isinstance(ul, AccessLevel), "expected type 'AccessLevel' for parameter 'ul', got '{}'".format(type(ul))
        assert isinstance(passwd, str), "expected type 'str' for parameter 'passwd', got '{}'".format(type(passwd))
        return await self.__client.change_ul(ul, passwd)

    async def change_password(self, password: str) -> None:
        assert isinstance(password, str), "expected type 'str' for parameter 'password', got '{}'".format(type(password))
        await self.__client.exec('change-password', password, input_stream=None, output_type=None, return_type=None)

    async def system_summary(self) -> str:
        return await self.__client.exec('system-summary', input_stream=None, output_type=str, return_type=None)

