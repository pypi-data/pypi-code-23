"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function
import argparse
import signal
from vlab import VlabException
from jemu_web_api import WebException
from os import getcwd
from time import sleep
from threading import Event
from __version__ import __version__ as jumper_current_version

import sys

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
        Vlab.check_version()
        parser.exit(message=formatter.format_help())


def run(args):
    try:
        vlab = Vlab(
            working_directory=args.directory,
            sudo_mode=args.sudo,
            gdb_mode=args.gdb,
            print_trace=args.trace,
            trace_output_file=args.trace_dest,
            print_uart=args.uart,
            uart_output_file=args.uart_dest
        )
        vlab.load(args.bin)

        reached_bkpt = Event()

        def bkpt_callback(code):
            print('Firmware reached a BKPT instruction with code {}'.format(code))
            reached_bkpt.set()

        vlab.on_bkpt(bkpt_callback)

        def pins_listener(pin_number, pin_level):
            print("pin_number:", pin_number, "  pin_level:", pin_level)

        if args.gpio:
            print("gpio")
            vlab.on_pin_level_event(pins_listener)


        vlab.start()

        if (not args.uart) and (not args.trace):
            print('\nVirtual device is running without UART/Trace prints (use -u and/or -t to get your firmware execution status)')
        else:
            print('\nVirtual device is running')

        while (not reached_bkpt.is_set()) and vlab.is_running():
            sleep(0.1)

        if reached_bkpt and vlab.is_running():
            vlab.stop()

        if vlab.get_return_code():
            vlab.stop()
            sys.exit(vlab.get_return_code())

    except VlabException as e:
        print(e.message)
        try:
            vlab.stop()
        finally:
            exit(e.exit_code)


def hci():
    virtual_hci_device = VirtualHciDevice()
    virtual_hci_device.start()
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        virtual_hci_device.stop()


def signal_handler(signal, frame):
    sys.exit(1)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser(
        prog='jumper',
        description="CLI interface for using Jumper's emulator"
    )

    parser.add_argument('--version', action=_VersionAction, version='%(prog)s {}'.format(__version__))

    subparsers = parser.add_subparsers(title='Commands', dest='command')

    run_parser = subparsers.add_parser(
        'run',
        help='Runs an emulator with a binary FW file. Currently only support nRF52 devices'
    )
    run_parser.add_argument(
        '--bin',
        '-b ',
        '--fw',
        help="Firmware to be flashed to the virtual device (supported extensions are bin, out, elf, hex). In case more than one file needs to be flashed (such as using Nordic's softdevice), the files should be merged first. Check out https://vlab.jumper.io/docs#softdevice for more details",
    )
    run_parser.add_argument(
        '--directory',
        '-d ',
        help='Working directory, must include the peripherals.json and scenario.json files. Default is current working directory',
        default=getcwd()
    )

    run_parser.add_argument(
        '--sudo',
        '-s ',
        help='Run in sudo mode => FW can write to read-only registers. This should usually be used for testing low-level drivers',
        action='store_true',
        default=False
    )

    run_parser.add_argument(
        '--gdb',
        '-g ',
        help='Opens a GDB port for debugging the FW on port 5555. The FW will not start running until the GDB client connects.',
        action='store_true',
        default=False
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
        action='store_true',
        help='Prints a trace report to stdout, this can be used with --trace-dest to forward it to a file.',
        default=False
    )

    run_parser.add_argument(
        '--trace-dest',
        type=str,
        help=
        """
        Forwards the trace report to a destination file. This MUST be used -t with this flag to make it work.
        To print to stdout, just hit -t.
        """,
        default="",
    )

    run_parser.add_argument(
        '--uart',
        '-u ',
        action='store_true',
        default=False,
        help='Forwards UART prints to stdout, this can be used with --uart-dest to forward it to a file.'
    )

    run_parser.add_argument(
        '--uart-dest',
        type=str,
        help=
        """
        Forwards UART prints to a destination file. This MUST be used -u with this flag to make it work.
        To print to stdout, just hit -u.
        """,
        default="",
    )

    run_parser.add_argument(
        "--gpio",
        help=
        """
        Prints GPIO events to stdout.
        """,
        action='store_true',
        default=False,
    )

    run_parser = subparsers.add_parser(
        'ble',
        help='Creates a virtual HCI device (BLE dongle) for regular Linux/Bluez programs to communicate with virtual devices'
    )

    args = parser.parse_args()

    if args.command == 'run':
        if args.version:
            print ("v" + jumper_current_version)
            exit(0)
        if not args.bin:
            print("jumper run: error: argument --bin/-b is required")
            exit(1)
        run(args)

    if args.command == 'ble':
        hci()


if __name__ == '__main__':
    main()
