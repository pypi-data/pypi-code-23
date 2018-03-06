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
import threading
import ctypes
import Queue

import timeout_decorator
import tarfile

from .jemu_uart import JemuUart
from .jemu_peripherals_parser import JemuPeripheralsParser
from .jemu_bsp_parser import JemuBspParser
from .jemu_gpio import JemuGpio
from .jemu_connection import JemuConnection
from .jemu_web_api import JemuWebApi
from .jemu_interrupts import JemuInterrupts

config_file_name = 'config.json' if 'JUMPER_STAGING' not in os.environ else 'config.staging.json'
JUMPER_DIR = os.path.join(os.path.expanduser('~'), '.jumper')
DEFAULT_CONFIG = os.path.join(JUMPER_DIR, config_file_name)
DEFAULT_JEMU_FILE = os.path.join(JUMPER_DIR, 'jemu')


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
    :param registers_trace: Adds a trace for CPU registers values before every CPU instruction.
    :param functions_trace: Adds a trace for the the functions that are being executed (requires a .out or .elf file)
    :param interrupts_trace: Adds a trace for interrupts handling.
    :param trace_output_file: If traces_list is not empty, redirects the trace from stdout to a file.
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
    _instructions_tgz_src = os.path.join(_jemu_build_dir, 'instructions_lib.tgz')

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

    @classmethod
    def check_sdk_version(cls):
        jumper_latest_version = Vlab._get_latest_version("jumper")
        if jumper_latest_version:
            if LooseVersion(jumper_current_version) < LooseVersion(jumper_latest_version):
                Vlab._print_upate_to_screen(jumper_latest_version, jumper_current_version)

    def _get_latest_jemu_version(self):
        return self._web_api.get_jemu_version() if not self._local_jemu and self._web_api else self._get_jemu_version()

    def _get_jemu_version(self):
        if not os.path.isfile(self._jemu_path):
            return None
        else:
            jemu_cmd = [self._jemu_path, '-v']
            try:
                return subprocess.check_output(jemu_cmd, cwd=self._working_directory).rstrip()
            except Exception:
                return None

    def _is_jemu_latest_version(self, jemu_latest_version):
        if self._local_jemu:
            return True
        if jemu_latest_version and os.path.isfile(self._jemu_path):
            jemu_version = self._get_jemu_version()
            if jemu_version:
                return LooseVersion(jemu_version) == LooseVersion(jemu_latest_version)
        return False

    def _is_instructions_latest_version(self, jemu_latest_version):
        if jemu_latest_version and os.path.isfile(self._instructions_lib):
            lib = ctypes.cdll.LoadLibrary(self._instructions_lib)
            try:
                version_func = lib.Version
            except AttributeError:
                return False
            version_func.restype = ctypes.c_char_p
            lib_version = version_func().strip()
            return LooseVersion(lib_version) == LooseVersion(jemu_latest_version)
        return False

    def __init__(
            self,
            working_directory=None,
            config_file=None,
            gdb_mode=False,
            sudo_mode=False,
            registers_trace=False,
            functions_trace=False,
            interrupts_trace=False,
            trace_output_file=None,
            print_uart=False,
            uart_output_file='',
            token=None
    ):
        self.check_sdk_version()
        self._working_directory = os.path.abspath(working_directory) if working_directory else self._transpiler_dir
        self._working_directory_dot_jumper = os.path.join(self._working_directory, '.jumper')
        self._local_jemu = True if (('LOCAL_JEMU' in os.environ) or ('JEMU_LOCAL' in os.environ)) else False
        self._gdb_mode = gdb_mode
        self._sudo_mode = sudo_mode
        self._jemu_process = None
        self._was_start = False
        self._uart_device_path = os.path.join(self._working_directory, 'uart')
        self._jemu_server_address = "localhost"
        self._instructions_lib = os.path.join(self._working_directory_dot_jumper, "instructions.so")
        self._program_bin = os.path.join(self._working_directory_dot_jumper, 'program.bin')
        self._instructions_tgz = os.path.join(self._working_directory_dot_jumper, 'instructions_lib.tgz')
        self._jemu_bin_tgz = os.path.join(self._working_directory_dot_jumper, 'jemu.tgz')
        self._cache_file = os.path.join(self._working_directory_dot_jumper, 'jemu.cache.sha1')
        self._uart = JemuUart(self._uart_device_path, self)
        self._uart.remove()
        self._jemu_connection = JemuConnection(self._jemu_server_address)
        self._registers_trace = registers_trace
        self._functions_trace = functions_trace
        self._interrupts_trace = interrupts_trace
        self._trace_output_file = trace_output_file
        self._print_uart = print_uart
        self._uart_output_file = uart_output_file
        self._jemu_debug = True if 'JEMU_DEBUG' in os.environ else False
        self._jemu_port = 8000 if self._jemu_debug else 0
        self._on_bkpt = None
        self._return_code = None
        self._jemu_connection.register(self.receive_packet)
        self._jemu_path = self._jemu_bin_src if self._local_jemu else DEFAULT_JEMU_FILE
        self._jemu_gpio = JemuGpio()
        self._jemu_interrupt = JemuInterrupts()
        self._threads = []
        self._stdout_thread = None
        self._build_components_methods()
        self._firmware = None
        self._events_queue = None

        if not os.path.exists(self._working_directory_dot_jumper):
            os.makedirs(self._working_directory_dot_jumper)

        self._init_web_app_with_token(token, config_file)

        if not self._local_jemu and self._web_api:
            self._events_queue = Queue.Queue()
            self._events_handler_thread = threading.Thread(target=self._event_sender)
            self._events_handler_thread.setDaemon(True)
            self._threads.append(self._events_handler_thread)
            self._events_handler_should_run = True
            self._events_handler_thread.start()

    def _init_web_app_with_token(self, token, config_file):
        secret_token = token
        if not secret_token:
            config_file = config_file or DEFAULT_CONFIG
            if not os.path.isfile(config_file):
                self.stop()
                raise MissingFileError('Token id was not found. Use "--token" flag or config file: "{}" in order to define it.'.format(os.path.abspath(config_file)))

            with open(config_file) as config_data:
                config = json.load(config_data)
            if 'token' in config:
                secret_token = config['token']

        if not self._local_jemu:
            if secret_token is not None:
                try:
                    self._web_api = JemuWebApi(jumper_token=secret_token)
                except requests.ConnectionError:
                    if os.path.isfile(self._instructions_lib) and os.path.isfile(self._program_bin) and os.path.isfile(self._jemu_path):
                        print("Could not connect to server, version will not be updated")
                        self._web_api = None
                    else:
                        raise requests.ConnectionError("Could not connect to server")
            else:
                self.stop()
                raise MissingFileError('Token id was not found. Use "--token" flag or config file: "{}" in order to define it.'.format(os.path.abspath(config_file)))

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

    def _read_file_signature_backup(self):
        data = ''
        if os.path.isfile(self._cache_file):
            if os.path.isfile(self._instructions_lib):
                with open(self._cache_file, 'r') as f:
                    data = f.read().replace('\n', '')
            else:
                os.remove(self._cache_file)

        return data

    def _write_file_signature_backup(self, sha1_cache_string):
        with open(self._cache_file, 'w+') as f:
            f.write(sha1_cache_string)

    def _unzip_jemu(self):
        try:
            tar = tarfile.open(self._jemu_bin_tgz)
            tar.extractall(path=JUMPER_DIR)
            tar.close()
        except Exception:
            raise MissingFileError('Error: Could not open jemu file. Please contact us at support@jumper.io with a copy of this trace text ')

        if os.path.isfile(self._jemu_path):
            os.chmod(self._jemu_path, 0o777)
        os.remove(self._jemu_bin_tgz)

    def _unzip_instructions_lib(self):
        try:
            tar = tarfile.open(self._instructions_tgz)
            tar.extractall(path=self._working_directory_dot_jumper)
            tar.close()
        except Exception:
            raise MissingFileError('Error: Could not open jemu file. Please contact us at support@jumper.io with a copy of this trace text')

        if os.path.isfile(self._instructions_lib):
            os.chmod(self._instructions_lib, 0o777)
        if os.path.isfile(self._program_bin):
            os.chmod(self._program_bin, 0o777)
        os.remove(self._instructions_tgz)

    def load(self, file_path):
        """
        Loads firmware to a virtual device and initialises a Virtual Lab session.
        Use :func:`~jumper.Vlab.start()` to start an emulation after this method was called.

        :param file_path: Path for a firmware file (supported extensions are bin, out, elf, hex)
        """
        ext = [".bin", ".out", ".elf", ".hex"]
        if not file_path.endswith(tuple(ext)):
            raise ArgumentError('Invalid file extension - supported extensions are bin, out, elf, hex')

        file_path = os.path.abspath(file_path)
        self._valid_file_existence(file_path)
        self._firmware = file_path
        new_signature = self._get_file_signature(self._firmware)
        self._valid_file_existence(self._firmware)

        latest_jemu_version = self._get_latest_jemu_version()
        gen_new_jemu = not self._is_jemu_latest_version(latest_jemu_version)

        gen_new_so = True
        if not gen_new_jemu:
            prev_signature = self._read_file_signature_backup()
            if prev_signature == new_signature and os.path.isfile(self._program_bin) and \
                    self._is_instructions_latest_version(latest_jemu_version):
                gen_new_so = False

        self._perform_silent_remove(gen_new_jemu, gen_new_so)
        if self._local_jemu:
            self._load_from_local(gen_new_so, self._firmware)
        else:  # from cloud
            self._load_from_cloud(gen_new_so, gen_new_jemu, self._firmware, new_signature)

        if gen_new_so and os.path.isfile(self._instructions_lib) and os.path.isfile(self._jemu_path):
            self._write_file_signature_backup(new_signature)

    def _perform_silent_remove(self, gen_new_jemu, gen_new_so):
        if gen_new_jemu:
            self._silent_remove_file(self._jemu_path)
        if gen_new_so:
            self._silent_remove_file(self._cache_file)
            self._silent_remove_file(self._instructions_lib)

    def _load_from_local(self, gen_new_so, file_path):
        try:
            if gen_new_so:
                transpiler_cmd = ["node", "index.js", "--debug", "--platform", "nrf52", "--bin", file_path, "--zip"]
                subprocess.check_call(transpiler_cmd, cwd=self._transpiler_dir)
                copyfile(self._instructions_tgz_src, self._instructions_tgz)
                self._unzip_instructions_lib()
            else:  # from cache
                make_cmd = ['make', '-C', 'emulator', 'DEBUG=1', 'PLATFORM=nrf52', '-j8', 'jemu']
                subprocess.check_call(make_cmd, cwd=self._transpiler_dir, stdout=open(os.devnull, 'w'),stderr=None)

        except subprocess.CalledProcessError as e:
            raise TranspilerError("Transpiler failed with an error: " + e.message)

    def _load_from_cloud(self, gen_new_so, gen_new_jemu, file_path, new_signature):
        filename = os.path.basename(file_path)
        if gen_new_jemu or gen_new_so:
            if new_signature in self._examples_hash_list:
                self._add_event('upload example firmware')
            else:
                self._add_event('upload new firmware')
            with open(file_path, 'r') as data:
                self._web_api.get_archived_emulator(filename, data, self._instructions_tgz, gen_new_jemu, self._jemu_bin_tgz)
                self._unzip_instructions_lib()
                if gen_new_jemu:
                    self._unzip_jemu()
        else:  # from cache
            self._add_event('using cached firmware')

    def _add_event(self, message):
        if self._events_queue:
            self._events_queue.put(message)

    def _event_sender(self):
        while self._events_handler_should_run:
            try:
                cur_event = self._events_queue.get(True, timeout=0.2)
            except Queue.Empty:
                continue

            retries = 3
            while retries > 0:
                try:
                    self._web_api.send_event(cur_event)
                except Exception:
                    retries -= 1
                    sleep(1)
                else:
                    break

    def start(self, ns=None):
        """
        Starts the emulation

        :param ns: If provided, commands the virtual device to run for the amount of time given in ns and then halt.

            If this parameter is used, this function is blocking until the virtual devices halts,
            if None is given, this function is non-blocking.
        """
        if not os.path.isfile(self._jemu_path):
            raise MissingFileError(self._jemu_path + ' is not found')
        elif not os.access(self._jemu_path, os.X_OK):
            raise MissingFileError(self._jemu_path + ' is not executable')

        self._was_start = True

        jemu_cmd = self._build_jemu_cmd()

        def jemu_connection():
            @timeout_decorator.timeout(6)
            def wait_for_connection():
                while not self._jemu_connection.connect(self._jemu_port):
                    sleep(0.1)
            try:
                wait_for_connection()
            except timeout_decorator.TimeoutError:
                self.stop()
                raise EmulationError("Error: Couldn't connect to Emulator. Please contact us at support@jumper.io with a copy of this trace text")
            if not self._jemu_connection.handshake(ns):
                raise EmulationError("Error: Couldn't connect to Emulator. Please contact us at support@jumper.io with a copy of this trace text")

            self._jemu_gpio.set_connection_manager(self._jemu_connection)
            self._jemu_interrupt.set_jemu_connection(self._jemu_connection)
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
            self._jemu_port = self._get_port_number()
            jemu_connection()
            self._stdout_thread = threading.Thread(target=self._thread_stdout_function)
            self._threads.append(self._stdout_thread)
            self._stdout_thread.start()

        @timeout_decorator.timeout(6)
        def wait_for_uart():
            while not os.path.exists(self._uart_device_path):
                sleep(0.1)

        try:
            wait_for_uart()
        except timeout_decorator.TimeoutError:
            if not self.is_running():
                raise EmulationError("Error: Emulator failed on start. Please contact us at support@jumper.io with a copy of this trace text")
            else:
                self.stop()
                raise EmulationError("Error: Uart doesn't exist. Please contact us at support@jumper.io with a copy of this trace text")

        self._uart.open()

        self._jemu_connection.start()

    def _build_jemu_cmd(self):
        jemu_cmd = [self._jemu_path, '-w', '--sdk-port', str(self._jemu_port)]

        if self._gdb_mode:
            jemu_cmd.append('-g')
        if self._sudo_mode:
            jemu_cmd.append('-s')

        traces = []
        if self._registers_trace:
            traces.append('regs')
        if self._functions_trace:
            traces.append('functions')
            self._build_obj_dump_file(jemu_cmd)
        if self._interrupts_trace:
            traces.append('interrupts')
        traces_string = ','.join(traces) if len(traces) > 0 else None

        if traces_string:
            jemu_cmd.extend(['-t', traces_string])

        if self._trace_output_file:
            jemu_cmd.append('--trace-dest')
            jemu_cmd.append(self._trace_output_file)

        if self._print_uart:
            jemu_cmd.append('-u')
            if self._uart_output_file:
                jemu_cmd.append(self._uart_output_file)

        return jemu_cmd

    def _build_obj_dump_file(self, jemu_cmd):
        if not self._firmware.endswith('.out') and not self._firmware.endswith('.elf'):
            raise ArgumentError('Invalid file extension - for running functions trace, use out or elf file')

        # check if arm-none-eabi-objdump exists
        try:
            cmd = "arm-none-eabi-objdump -v"
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self._working_directory)
            p.wait()
            sleep(0.3)
        except Exception as e:
            raise ArgumentError('arm-none-eabi-objdump not exists - please install it')

        # create dump file
        try:
            cmd = "arm-none-eabi-objdump -d " + self._firmware + " > objdump.txt"
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self._working_directory)
            p.wait()
            sleep(0.3)
        except Exception as e:
            raise EmulationError(e.message)

        jemu_cmd.extend(['--objdump', 'objdump.txt'])

    def _thread_stdout_function(self):
        self._assert_jemu_is_running()
        while True:
            data = self._jemu_process.stdout.read(1)  # todo: 1 should be removed
            if data == '':
                break
            sys.stdout.write(data)
            sys.stdout.flush()

    def _get_port_number(self):
        self._assert_jemu_is_running()

        @timeout_decorator.timeout(6)
        def get_next_stdout_line():
            return self._jemu_process.stdout.readline()

        loop_number = 0
        while loop_number < 10:
            try:
                line = get_next_stdout_line()
            except timeout_decorator.TimeoutError:
                raise EmulationError("Error: Could not read port from emulator. Please contact us at support@jumper.io with a copy of this trace text")

            line_data = line.split(' ')
            length = len(line_data)
            for index in range(0, length):
                if line_data[index] == 'port:':
                    return line_data[index + 1].split('\n')[0]
            loop_number += 1

        raise EmulationError("Error: Could not read port from emulator. Please contact us at support@jumper.io with a copy of this trace text")

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

        self._events_handler_should_run = False
        self._stop_threads()
        self._uart = None
        self._jemu_connection = None

    def _stop_threads(self):
        for t in self._threads:
            if t.is_alive():
                t.join()

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
        """

        :param callback: The callback to be called when an interrupt is being handled. The callback will be called with callback(interrupt)
        """
        self._jemu_interrupt.on_interrupt([callback])

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

    def _assert_jemu_is_running(self):
        if not self.is_running():
            raise EmulationError("Error: The Emulator is not running.")

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

