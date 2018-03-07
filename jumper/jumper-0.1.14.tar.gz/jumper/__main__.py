"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function
import argparse
import signal
from vlab import VlabException
from os import getcwd
import os
from time import sleep
from threading import Event
import signal
import sys
import re

from __version__ import __version__ as jumper_current_version
from .vlab import Vlab
from .vlab_hci_device import VirtualHciDevice
from . import __version__


class _VersionAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 version=None,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help="show program's version number and exit"):
        super(_VersionAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        version = self.version
        if version is None:
            version = parser.version
        formatter = parser._get_formatter()
        formatter.add_text(version)
        Vlab.check_sdk_version()
        parser.exit(message=formatter.format_help())


def validate_traces_list(traces_list):
    traces_list = traces_list.split(',')
    for trace in traces_list:
        if trace not in ['regs', 'interrupts', 'functions']:
            raise VlabException('jumper run: error: unrecognized trace:' + trace, 1)


def run(args):
    registers_trace = False
    functions_trace = False
    interrupts_trace = False

    if args.traces_list:
        for trace in args.traces_list.split(','):
            if trace == 'registers' or trace == 'regs':
                registers_trace = True
            elif trace == 'functions':
                functions_trace = True
            elif trace == 'interrupts':
                interrupts_trace = True
            else:
                raise VlabException('jumper run: error: Invalid trace type {}. Valid traces are regs, functions, interrupts'.format(trace), 1)

    vlab = None
    try:
        vlab = Vlab(
            working_directory=args.working_directory,
            sudo_mode=args.sudo_mode,
            gdb_mode=args.gdb_mode,
            registers_trace=registers_trace,
            functions_trace=functions_trace,
            interrupts_trace=interrupts_trace,
            trace_output_file=args.trace_output_file,
            print_uart=args.print_uart,
            uart_output_file=args.uart_output_file,
            token=args.token
        )
        vlab.load(args.fw)

        reached_bkpt = Event()

        def bkpt_callback(code):
            print('Firmware reached a BKPT instruction with code {}'.format(code))
            reached_bkpt.set()

        vlab.on_bkpt(bkpt_callback)

        def pins_listener(pin_number, pin_level):
            print("pin_number:", pin_number, "  pin_level:", pin_level)

        if args.gpio:
            vlab._send_gpio_event()
            vlab.on_pin_level_event(pins_listener)

        if args.stop_after:
            vlab._send_stop_after_event()
            def raise_invalid_time():
                print('Invalid time format for --stop-after: {}'.format(args.stop_after))
                exit(1)

            match = re.match('^\d+', args.stop_after)
            if not match:
                raise_invalid_time()
            time = int(match.group(0))

            if re.match('^\d+$', args.stop_after) or re.match('^\d+ms$', args.stop_after):
                time = time * 1000 * 1000
            elif re.match('^\d+s$', args.stop_after):
                time = time * 1000 * 1000 * 1000
            elif re.match('^\d+us$', args.stop_after):
                time = time * 1000
            elif re.match('^\d+ns$', args.stop_after):
                pass
            else:
                raise_invalid_time()

            vlab.run_for_ns(time)
            vlab.stop()
            return

        vlab.start()

        if not args.print_uart and not args.traces_list:
            print(
                '\nVirtual device is running without UART/Trace prints (use -u and/or -t to get your firmware '
                'execution status)\n')
        else:
            print('\nVirtual device is running\n')

        try:
            while (not reached_bkpt.is_set()) and vlab.is_running():
                sleep(0.5)
        except KeyboardInterrupt:
            vlab.stop()

        if reached_bkpt and vlab.is_running():
            vlab.stop()

        if vlab.get_return_code():
            vlab.stop()
            sys.exit(vlab.get_return_code())

    except VlabException as e:
        print('jumper run: error: {}'.format(e.message))
        try:
            if vlab:
                vlab.stop()
        finally:
            exit(e.exit_code)


def hci():
    Vlab.check_sdk_version()
    stop = Event()
    virtual_hci_device = VirtualHciDevice()

    def signal_handler(signum, frame):
        stop.set()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    virtual_hci_device.start()
    while not stop.wait(timeout=0.1):
        pass

    virtual_hci_device.stop()
    print(stop.is_set())


def command_run(args):
    if args.version:
        print("v" + jumper_current_version)
        exit(0)

    if not args.fw:
        print("jumper run: error: argument --bin/-b is required")
        exit(1)

    if args.traces_list:
        args.traces_list = args.traces_list.lower().replace(' ', '')
        validate_traces_list(args.traces_list)

    run(args)


def main():
    parser = argparse.ArgumentParser(
        prog='jumper',
        description="CLI interface for using Jumper's emulator"
    )

    parser.add_argument('--version', action=_VersionAction, version='%(prog)s {}'.format(__version__))
    parser.add_argument('--token', default=None, dest='token', type=str, help='Your secret token')

    subparsers = parser.add_subparsers(title='Commands', dest='command')

    run_parser = subparsers.add_parser(
        'run',
        help='Executes a FW file on a virtual device. Currently only support nRF52 devices'
    )
    run_parser.add_argument(
        '--fw',
        '--bin',
        '-b ',
        help="Firmware to be flashed to the virtual device (supported extensions are bin, out, elf, hex). In case more than one file needs to be flashed (such as using Nordic's softdevice), the files should be merged first. Check out https://vlab.jumper.io/docs#softdevice for more details",
    )
    run_parser.add_argument(
        '--directory',
        '-d ',
        help='Working directory, should include the bsp.json and scenario.json files. Default is current working directory',
        default=getcwd(),
        dest='working_directory'
    )

    run_parser.add_argument(
        '--sudo',
        '-s ',
        help='Run in sudo mode => FW can write to read-only registers. This should usually be used for testing low-level drivers, fuzzing (error injection) and certification tests.',
        action='store_true',
        default=False,
        dest='sudo_mode'
    )

    run_parser.add_argument(
        '--gdb',
        '-g ',
        help='Opens a GDB port for debugging the FW on port 5555. The FW will not start running until the GDB client connects.',
        action='store_true',
        default=False,
        dest='gdb_mode'
    )

    run_parser.add_argument(
        '--version',
        '-v ',
        help='Jumper sdk version.',
        action='store_true',
        default=False
    )

    run_parser.add_argument(
        '--trace',
        '-t ',
        help=
        """
        Prints a trace report to stdout.
        Valid reports: regs,interrupts,functions. (the functions trace can only be used with an out/elf file) 
        Example: jumper run -b my_bin.bin -t interrupts,regs --trace-dest trace.txt
        Default value: regs 
        This can be used with --trace-dest to forward it to a file.
        """,
        const='regs',   # default when there are 0 arguments
        nargs='?',      # 0-or-1 arguments
        dest='traces_list'
    )

    run_parser.add_argument(
        '--trace-dest',
        type=str,
        help=
        """
        Forwards the trace report to a destination file. Must be used with -t.
        To print to stdout, just hit -t.
        """,
        default='',
        dest='trace_output_file'
    )

    run_parser.add_argument(
        '--uart',
        '-u ',
        action='store_true',
        default=False,
        help='Forwards UART prints to stdout, this can be used with --uart-dest to forward it to a file.',
        dest='print_uart'
    )

    run_parser.add_argument(
        '--uart-dest',
        type=str,
        help=
        """
        Forwards UART prints to a destination file. This MUST be used -u with this flag to make it work.
        To print to stdout, just hit -u.
        """,
        default=None,
        dest='uart_output_file'
    )

    run_parser.add_argument(
        "--gpio",
        help=
        """
        Prints GPIO events (pin changes) to stdout.
        """,
        action='store_true',
        default=False,
    )

    run_parser.add_argument(
        '--stop-after',
        type=str,
        help=
        """
        Stop the execution after a specific amount of time. Units should be stated, if no units are stated, time in ms is assumed.
        Examples: "--stop-after 1s, --stop-after 1000ms, --stop-after 1000000us, --stop-after 1000000000ns" 
        """,
        default=None,
        dest='stop_after'
    )

    run_parser = subparsers.add_parser(
        'ble',
        help='Creates a virtual HCI device (BLE dongle) for regular Linux/Bluez programs to communicate with virtual devices'
    )

    args = parser.parse_args()

    if args.command == 'run':
        command_run(args)

    if args.command == 'ble':
        hci()


if __name__ == '__main__':
    try:
        main()
    except VlabException as e:
        print (e.message())
        exit(e.exit_code())
