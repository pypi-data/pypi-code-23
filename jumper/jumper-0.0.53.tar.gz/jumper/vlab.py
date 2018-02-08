"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function
from builtins import input
import os
import errno
import subprocess
import hashlib
import sys
from time import sleep
from shutil import copyfile
from shutil import copymode
import requests
from distutils.version import LooseVersion
from __version__ import __version__ as jumper_current_version
import json
from termcolor import colored
from terminaltables import SingleTable
from threading import Thread

import timeout_decorator

from .jemu_uart import JemuUart
from .jemu_peripherals_parser import JemuPeripheralsParser
from .jemu_bsp_parser import JemuBspParser
from .jemu_gpio import JemuGpio
from .jemu_connection import JemuConnection
from .jemu_web_api import JemuWebApi
from .jemu_interrupts import JemuInterrupts
from .common import TimeoutException
import tarfile

config_file_name = 'config.json' if 'JUMPER_STAGING' not in os.environ else 'config.staging.json'
DEFAULT_CONFIG = os.path.join(os.path.expanduser('~'), '.jumper', config_file_name)


class VlabException(Exception):
    def __init__(self, message, exit_code):
        super(VlabException, self).__init__(message)
        self.exit_code = exit_code
        self.message = message


class EmulationError(VlabException):
    def __init__(self, message):
        super(EmulationError, self).__init__(message, 5)


class MissingFileError(VlabException):
    def __init__(self, message):
        super(MissingFileError, self).__init__(message, 2)


class ArgumentError(VlabException):
    def __init__(self, message):
        super(ArgumentError, self).__init__(message, 1)


class TranspilerError(VlabException):
    def __init__(self, message):
        super(TranspilerError, self).__init__(message, 3)

class Vlab(object):
    """
    The main class for using Jumper Virtual Lab

    :param working_directory: The directory that holds the bsp.json abd scenario.json files for the virtual session
    :param config_file: Config file holding the API token (downloaded from https://vlab.jumper.io)
    :param gdb_mode: If True, a GDB server will be opened on port 5555
    :param sudo_mode: If True, firmware can write to read-only registers. This is useful for injecting a mock state to the hardware.
    :param print_trace: If ture, a trace with the registers value at each tick of the execution will be generated.
    :param trace_output_file: If print_trace is True, sets the trace file. Default is stdout.
    :param print_uart: If True UART prints coming from the device will be printed to stdout or a file
    :param uart_output_file: If print_uart is True, sets the UART output file. Default is stdout.
    """
    if os.environ.get('JEMU_DIR') is None:
        _transpiler_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'jemu'))
    else:
        _transpiler_dir = os.path.abspath(os.environ['JEMU_DIR'])

    _jemu_build_dir = os.path.abspath(os.path.join(_transpiler_dir, 'emulator', '_build'))
    _jemu_bin_src = os.path.join(_jemu_build_dir, 'jemu')
    _jemu_bin_tgz_src = os.path.join(_jemu_build_dir, 'jemu.tgz')
    _local_cache_file = os.path.abspath(os.path.join(_transpiler_dir, 'emulator', '_build','jemu.cache.sha1'))

    _INT_TYPE = "interrupt_type"

    _TYPE_STRING = "type"
    _BKPT = "bkpt"
    _VALUE_STRING = "value"

    _examples_hash_list = [
        b'f9cf392be5ac94b89e0b0837f258a6c177efb2be',
        b'1ef133cfe2a956cf6a61f629f818c2dbfd866367',
        b'be24b36eab847ea1268c21a75f992d5a63f91d4b',
        b'bcf18382d0c130e5f34e8053bb3ab56493d6c589',
        b'16572d43ccfdcef0e769fc934daed287946c1156']

    @staticmethod
    def _get_latest_version(name):
        url = "https://pypi.python.org/pypi/{}/json".format(name)
        try:
            return list(reversed(sorted(requests.get(url).json()["releases"], key=LooseVersion)))[0]
        except Exception as e:
            return None

    @staticmethod
    def _print_upate_to_screen(jumper_latest_version, jumper_current_version):
        update_message = "Update available {0} ".format(jumper_current_version) + u'\u2192' + colored(" " + jumper_latest_version, 'green', attrs=['bold'])
        how_to_updtae_message = "\n  Run " + colored(" sudo pip install jumper --upgrade ", "blue", attrs=['bold']) + "to update"
        table_data = [[update_message + how_to_updtae_message]]
        table = SingleTable(table_data)
        table.padding_left = 2
        table.padding_right = 2
        print()
        print(table.table.encode('utf-8'))
        print()

    @staticmethod
    def check_version():
        jumper_latest_version = Vlab._get_latest_version("jumper")
        if jumper_latest_version:
            if LooseVersion(jumper_current_version) < LooseVersion(jumper_latest_version):
                Vlab._print_upate_to_screen(jumper_latest_version, jumper_current_version)

    def is_jemu_latest_version(self):
        if self._local_jemu:
            return True
        jumper_latest_version = self._web_api.get_jemu_version()
        if jumper_latest_version and os.path.isfile(self._jemu_bin):
            jemu_cmd = [self._jemu_bin, '-v']
            try:
                jemu_version = subprocess.check_output(jemu_cmd, cwd=self._working_directory)
                jemu_version = jemu_version.rstrip()
            except Exception as e:
                return False
            result = LooseVersion(jemu_version) == LooseVersion(jumper_latest_version)
            return result
        return False

    def __init__(self, working_directory=None, config_file=None, gdb_mode=False, sudo_mode=False, print_trace=False, trace_output_file="", print_uart=False, uart_output_file=""):
        self.check_version()
        self._working_directory = os.path.abspath(working_directory) if working_directory else self._transpiler_dir
        self._local_jemu = True if (('LOCAL_JEMU' in os.environ) or ('JEMU_LOCAL' in os.environ)) else False
        self._gdb_mode = gdb_mode
        self._sudo_mode = sudo_mode
        self._jemu_process = None
        self._was_start = False
        self._uart_device_path = os.path.join(self._working_directory, 'uart')
        self._jemu_server_address = "localhost"
        self._jemu_bin = os.path.join(self._working_directory, 'jemu')
        self._jemu_bin_tgz = os.path.join(self._working_directory, 'jemu.tgz')
        self._cache_file = self._jemu_bin + ".cache.sha1"
        self._uart = JemuUart(self._uart_device_path, self)
        self._uart.remove()
        self._jemu_connection = JemuConnection(self._jemu_server_address)
        self._print_trace = print_trace
        self._trace_output_file = trace_output_file
        self._print_uart = print_uart
        self._uart_output_file = uart_output_file
        self._jemu_debug = True if 'JEMU_DEBUG' in os.environ else False
        self._on_bkpt = None
        self._return_code = None
        self._jemu_gpio = JemuGpio()
        self._jemu_interrupt = None
        self._stdout_thread = None
        self._build_components_methods()
        self.jemu_server_port = 8000
        token = None

        config_file = config_file or DEFAULT_CONFIG

        if not os.path.isfile(config_file):
            raise MissingFileError('Config file not found at: {}'.format(os.path.abspath(config_file)))

        with open(config_file) as config_data:
            config = json.load(config_data)
        if 'token' in config:
            token = config['token']

        if not self._local_jemu:
            if token is not None:
                self._web_api = JemuWebApi(jumper_token=token)
            else:
                raise MissingFileError('Config file not found at: {}'.format(config_file))

    @staticmethod
    def _silent_remove_file(filename):
        try:
            if os.path.isfile(filename):
                os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def _valid_file_existence(self, file_path):
        if not os.path.isfile(file_path):
            raise MissingFileError("Failed to open binary file (at: '" + file_path + "')")

    @property
    def uart(self):
        """
        The main UART device for the Virtual Lab session

        :return: :class:`~jumper.jemu_uart.JemuUart`
        """
        return self._uart

    @property
    def gpio(self):
        return self._jemu_gpio

    @property
    def interrupts(self):
        return self._jemu_interrupt

    # @property
    # def interrupt_type(self):
    #     return self._INT_TYPE

    def _build_components_methods(self):
        peripherals_json = os.path.join(self._working_directory, "peripherals.json")
        bsp_json = os.path.join(self._working_directory, "bsp.json")
        default_bsp_json = os.path.join(os.path.dirname(__file__), "default_bsp.json")

        if os.path.isfile(bsp_json):
            components_list = self._parse_bsp_json(bsp_json)
        elif os.path.isfile(peripherals_json):
            components_list = self._parse_peripherals_json(peripherals_json)
        else:
            components_list = self._parse_bsp_json(default_bsp_json)

        for component in components_list:
            setattr(self, component["name"], component["obj"])

    def _parse_bsp_json(self, bsp_path):
        bsp_json_parser = JemuBspParser(bsp_path)
        return bsp_json_parser.get_components(self._jemu_connection)

    def _parse_peripherals_json(self, peripherals_path):
        """Backwards compatibility"""
        self._peripherals_json_parser = \
            JemuPeripheralsParser(os.path.join(self._working_directory, peripherals_path))
        return self._peripherals_json_parser.get_peripherals(self._jemu_connection)

    @staticmethod
    def _get_file_signature(file_path):
        sha1 = hashlib.sha1()

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)

        return sha1.hexdigest()

    def _read_file_signature_backup(self, file_path):
        data = ''
        if os.path.isfile(file_path):
            if os.path.isfile(self._jemu_bin):
                with open(file_path, 'r') as f:
                    data = f.read().replace('\n', '')
            else:
                os.remove(file_path)

        return data

    def _write_file_signature_backup(self, sha1_cache_string, file_path):
        with open(file_path, 'w+') as f:
            f.write(sha1_cache_string)

    def _unzip_jemu(self, gen_new):
        if gen_new:
            try:
                tar = tarfile.open(self._jemu_bin_tgz)
                tar.extractall(path=self._working_directory)
                tar.close()
            except Exception:
                raise VlabException('Error: Could not open jemu file')

            os.chmod(self._jemu_bin, 0o777)
            os.remove(self._jemu_bin_tgz)

    def load(self, file_path):
        """
        Loads firmware to a virtual device and initialises a Virtual Lab session.
        Use :func:`~jumper.Vlab.start()` to start an emulation after this method was called.

        :param file_path: Path for a firmware file (supported extensions are bin, out, elf, hex)
        """

        ext = [".bin", ".out", ".elf", ".hex"]
        if not file_path.endswith(tuple(ext)):
            raise ArgumentError('Invalid file extension - supported extensions are bin, out, elf, hex')

        self._valid_file_existence(file_path)
        file_path = os.path.abspath(file_path)
        filename = os.path.basename(file_path)
        gen_new = True
        new_signature = self._get_file_signature(file_path)

        prev_signature = self._read_file_signature_backup(self._cache_file)
        if prev_signature == new_signature and self.is_jemu_latest_version():
            if not self._local_jemu:
                gen_new = False
            else:
                local_signature = self._read_file_signature_backup(self._local_cache_file)
                if local_signature == new_signature:
                    gen_new = False

        if gen_new:
            self._silent_remove_file(self._jemu_bin)
            self._silent_remove_file(self._cache_file)
            if self._local_jemu:
                self._silent_remove_file(self._local_cache_file)

        if self._local_jemu:
            try:
                if gen_new:
                    transpiler_cmd = ["node", "index.js", "--debug", "--platform", "nrf52", "--bin", file_path, "--zip"]
                    subprocess.check_call(transpiler_cmd, cwd=self._transpiler_dir, stdout=open(os.devnull, 'w'), stderr=None)
                    copyfile(self._jemu_bin_tgz_src, self._jemu_bin_tgz)
                else:  # from cache
                    make_cmd = ['make', '-C', 'emulator', 'DEBUG=1', 'PLATFORM=nrf52', '-j8']
                    subprocess.check_call(make_cmd, cwd=self._transpiler_dir, stdout=open(os.devnull, 'w'), stderr=None)
                    copyfile(self._jemu_bin_src, self._jemu_bin)
                    copymode(self._jemu_bin_src, self._jemu_bin)

            except subprocess.CalledProcessError as e:
                raise TranspilerError("Transpiler failed with an error: " + e.message)

        else:  # from cloud
            if gen_new:
                if new_signature in self._examples_hash_list:
                    self._web_api.send_event('upload example firmware')
                else:
                    self._web_api.send_event('upload new firmware')

                with open(file_path, 'r') as data:
                    self._web_api.get_archived_emulator(filename, data, self._jemu_bin_tgz)
            else:  # from cache
                self._web_api.send_event('using cached firmware')

        self._unzip_jemu(gen_new)

        if gen_new and os.path.isfile(self._jemu_bin):
            self._write_file_signature_backup(new_signature, self._cache_file)
            if self._local_jemu:
                copyfile(self._cache_file, self._local_cache_file)
                copymode(self._cache_file, self._local_cache_file)

    def start(self, ns=None):
        """
        Starts the emulation

        :param ns: If provided, commands the virtual device to run for the amount of time given in ns and then halt.

            If this parameter is used, this function is blocking until the virtual devices halts,
            if None is given, this function is non-blocking.
        """
        if not os.path.isfile(self._jemu_bin):
            raise MissingFileError(self._jemu_bin + ' is not found')
        elif not os.access(self._jemu_bin, os.X_OK):
            raise MissingFileError(self._jemu_bin + ' is not executable')

        self._was_start = True

        jemu_cmd = []
        # if self._jemu_debug:
        #     jemu_cmd = ['gdbserver', 'localhost:7777']
        jemu_cmd.append(self._jemu_bin)
        jemu_cmd.append('-w')
        jemu_cmd.append('--sdk-port')
        jemu_cmd.append('0')

        if self._gdb_mode:
            jemu_cmd.append('-g')
        if self._sudo_mode:
            jemu_cmd.append('-s')
        if self._print_trace:
            jemu_cmd.append('-t')
            if self._trace_output_file != "":
                jemu_cmd.append(self._trace_output_file)
        if self._print_uart:
            jemu_cmd.append('-u')
            if self._uart_output_file != "":
                jemu_cmd.append(self._uart_output_file)

        def jemu_connection():
            @timeout_decorator.timeout(6)
            def wait_for_connection():
                while not self._jemu_connection.connect(self.jemu_server_port):
                    sleep(0.1)
            try:
                wait_for_connection()
            except timeout_decorator.TimeoutError:
                self.stop()
                raise EmulationError("Error: Couldn't connect to Emulator")
            if not self._jemu_connection.handshake(ns):
                raise EmulationError("Error: Couldn't connect to Emulator")

            self._jemu_gpio.set_connection_manager(self._jemu_connection)
            self._jemu_interrupt = JemuInterrupts(self._jemu_connection)
            self._jemu_connection.register(self.receive_packet)

        if self._jemu_debug:
            input("Start a debugger with the following parameters:\n\
            cwd: {}\n\
            command: {}\n\
            Press Enter to continue...".format(self._working_directory, ' '.join(jemu_cmd))
                  )
            jemu_connection()
        else:
            try:
                self._jemu_process = subprocess.Popen(jemu_cmd, cwd=self._working_directory, stdout=subprocess.PIPE)
                sleep(0.3)
            except Exception as e:
                raise EmulationError(e.message)

            self.jemu_server_port = self.get_port_number()
            jemu_connection()
            self._stdout_thread = Thread(target=self._thread_stdout_function)
            self._stdout_thread.start()

        @timeout_decorator.timeout(6)
        def wait_for_uart():
            while not os.path.exists(self._uart_device_path):
                sleep(0.1)

        try:
            wait_for_uart()
        except timeout_decorator.TimeoutError:
            if not self.is_running():
                raise EmulationError("Error: Emulator failed on start")
            else:
                self.stop()
                raise EmulationError("Error: Uart doesn't exist")

        self._uart.open()

        self._jemu_connection.start()

    def _thread_stdout_function(self):
        while True:
            data = self._jemu_process.stdout.read(1)
            if data == '':
                break
            sys.stdout.write(data)

    def get_port_number(self):
        @timeout_decorator.timeout(6)
        def get_next_stdout_line():
            return self._jemu_process.stdout.readline()

        loop_number = 0
        while loop_number < 10:
            try:
                line = get_next_stdout_line()
            except timeout_decorator.TimeoutError:
                raise EmulationError("Error: Could not read port from emulator")

            line_data = line.split(' ')
            length = len(line_data)
            for index in range(0, length):
                if line_data[index] == 'port:':
                    return line_data[index + 1].split('\n')[0]
            loop_number += 1

        raise EmulationError("Error: Could not read port from emulator")

    def stop(self):
        """
        Stops the Virtual Lab session.

        Opposing to halting the session, the virtual device cannot be resumed after a stop command.

        """
        if self._jemu_connection:
            self._jemu_connection.close()
        if self._uart:
            self._uart.close()
            self._uart.remove()

        if self._jemu_process and self._jemu_process.poll() is None:
            self._jemu_process.terminate()
            self._jemu_process.wait()
            self._return_code = 0

        self._stop_stdout_thread()
        self._uart = None
        self._jemu_connection = None

    def _stop_stdout_thread(self):
        if self._stdout_thread.is_alive():
            self._stdout_thread.join()

    def run_for_ms(self, ms):
        """
        Starts or resumes the virtual device, the device will halt after the amount of time specified.

        This function is blocking until the virtual device has halted. Use this when the virtual device is stopped
        or halted.

        :param ms: Time to run in ms
        """
        self.run_for_us(ms * 1000)

    def run_for_us(self, us):
        """
        Starts or resumes the virtual device, the device will halt after the amount of time specified.

        This function is blocking until the virtual device has halted. Use this when the virtual device is stopped
        or halted.

        :param ms: Time to run in us
        """
        self.run_for_ns(us * 1000)

    def run_for_ns(self, ns):
        """
        Starts or resumes the virtual device, the device will halt after the amount of time specified.

        This function is blocking until the virtual device has halted. Use this when the virtual device is stopped
        or halted.

        :param ns: Time to run in ns
        """
        if not self._was_start:
            self.start(ns)
            self.SUDO.wait_until_stopped()
        else:
            self.SUDO.run_for_ns(ns)

    def stop_after_ms(self, ms):
        # """
        # Causes the virtual device to halt after the amount of time specified.
        # This function is non-blocking and does not cause the device to resume.
        #
        # Use this when the virtual device is halted.
        #
        # :param ms: Time to run in ms
        # """
        self.stop_after_ns(ms * 1000000)

    def stop_after_ns(self, ns):
        # """
        # Causes the virtual device to halt after the amount of time specified.
        # This function is non-blocking and does not cause the device to resume.
        #
        # Use this when the virtual device is halted.
        #
        # :param ns: Time to run in ns
        # """
        self.SUDO.stop_after_ns(ns)

    def resume(self):
        """
        Resumes a paused device.

        """
        self.SUDO.resume()

    def cancel_stop(self):
        self.SUDO.cancel_stop()

    def pause(self):
        """
        Pause the device.

        """
        self.run_for_ns(0)

    def on_interrupt(self, callback):
        self.interrupts.on_interrupt([callback])

    def set_timer(self, ns, callback):
        self.SUDO.set_timer(ns, callback)

    def get_state(self):
        if not self._was_start:
            return "init"
        elif not self.is_running():
            return "stopped"
        return self.SUDO.get_state()

    def on_pin_level_event(self, callback):
        """
        Specifies a callback for a pin transition event.

        :param callback: The callback to be called when a pin transition occures. The callback will be called with callback(pin_number, pin_level)
        """
        self.gpio.on_pin_level_event(callback)

    def get_pin_level(self, pin_num):
        """
        Specifies get the pin level for a pin num.

        :param pin num: pin number id
        """
        return self.gpio.get_pin_level(pin_num)

    def on_bkpt(self, callback):
        """
        Sets a callback to be called when the virtual device execution reaches a BKPT assembly instruction.

        :param callback: The callback to be called. Callback will be called with callback(code)\
        where code is the code for the BKPT instruction.
        """
        self._on_bkpt = callback

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._TYPE_STRING] == self._BKPT:
            if self._on_bkpt is not None:
                bkpt_code = jemu_packet[self._VALUE_STRING]
                self._on_bkpt(bkpt_code)

    def is_running(self):
        """
        Checks if the virtual device has been started.

        :return: True if running or pause, False otherwise.
        """
        if not self._jemu_process:
            if self._jemu_debug:
                return True
            else:
                return False

        self._return_code = self._jemu_process.poll()
        return self._return_code is None

    def get_return_code(self):
        """
        Checks a return code from the device.

        :return:
            - 0 if device was stopped using the :func:`~stop()` method
            - Exit code from firmware if the Device exited using the jumper_sudo_exit_with_exit_code() \
            command from jumper.h
        """
        if not self._jemu_process:
            return None

        if self._return_code is None:
            self._return_code = self._jemu_process.poll()

        return self._return_code

    def get_device_time_ns(self):
        """
        How much time passed from beginning of the emulation.

        :return: Emulation time in nanoseconds.
        """
        return self.SUDO.get_device_time_ns()

    def get_device_time_us(self):
        """
        How much time passed from beginning of the emulation.

        :return: Emulation time in microseconds.
        """
        return self.get_device_time_ns() / 1000

    def get_device_time_ms(self):
        """
        How much time passed from beginning of the emulation.

        :return: Emulation time in milliseconds.
        """
        return self.get_device_time_us() / 1000

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *err):
        self.stop()

    def __del__(self):
        self.stop()

