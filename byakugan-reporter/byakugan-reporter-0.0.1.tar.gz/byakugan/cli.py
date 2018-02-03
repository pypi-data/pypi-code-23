"""
Byakugan

Usage:
    byakugan scan [--ip=<ip> --out_dir=<out_dir>]
    byakugan -h | --help
    byakugan --version

Options:
    --ip=<ip>           [default: 192.168.0.1]
    --out_dir=<out_dir>         [default: current_dir]
    -h --help           Show this screen.
    --version           Show version.

Examples:
    byakugan scan

Help:
    Help Information
"""

from inspect import getmembers, isclass

from docopt import docopt

from . import __version__ as VERSION


def main():
    """Main Cli entry_point."""
    import byakugan.commands
    options = docopt(__doc__, version=VERSION)

    for (k, v) in options.items():
        if hasattr(byakugan.commands, k) and v:
            module = getattr(byakugan.commands, k)
            byakugan.commands = getmembers(module, isclass)
            command = [command[1] for command in byakugan.commands if command[0] != 'Base'][0]
            command = command(options)
            command.run()
