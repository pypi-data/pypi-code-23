#!/usr/bin/env python
"""The ampio command line implementation."""

import asyncio
from pyampio.gateway import AmpioGateway
import pyampio.version as v
import logging


try:
    import click
except ImportError:
    print("Install click python package\n pip install click")
    exit()


class BasedIntParamType(click.ParamType):
    """Type for based int."""

    name = 'integer'

    def convert(self, value, param, ctx):
        """Convert value from hex, oct, dec to dec."""
        try:
            if value[:2].lower() == '0x':
                return int(value[2:], 16)
            elif value[:1] == '0':
                return int(value, 8)
            return int(value, 10)
        except ValueError:
            self.fail('%s is not a valid integer' % value, param, ctx)


BASED_INT = BasedIntParamType()


def on_value_changed(modules, can_id, attribute, index, old_value, new_value, unit):
    """Handle the value changed event.

    Args:
        modules (ModuleManager): Module manager object
        can_id (int): CAN ID
        attribute (str): The attribute name i.e. input, bin_input, temperature, flag, etc.
        index (int): The attribute index (1-based)
        old_value: Old value
        new_value: New value
        unit (str): Unit

    """
    mod = modules.get_module(can_id)
    if mod:
        print("{:08x}/{:08x} {:16} {:32} {}({}) changed {}{}->{}{}".format(
            mod.physical_can_id, can_id, mod.part_number, mod.name, attribute, index, old_value, unit, new_value, unit)
        )


# @asyncio.coroutine
# def on_discovered_call(loop, can_id, command, index, value, ampio, modules):
#
#     # yield from ampio.send_value_with_index(0x1ae0, 0x0, 4)
#     yield from ampio.send_value_with_index(0x13ec, 0x00, 5)
#
#     #ampio.protocol.close()
#
#     # loop.stop()

@asyncio.coroutine
def send_command(ampio, can_id, command, index, value):
    """Send command to Ampio Module."""
    while not ampio.is_connected:
        yield
    if command == 'set_value':
        yield from ampio.send_value_with_index(can_id, value, index)
    # yield from ampio.send_value_with_mask(0x1ae0, 0x00, 0x08) # mask 0x08 - index = 4

    # yield from ampio.send_value_with_index(0x13ec, 0xff, 4)
    # yield from ampio.send_value_with_mask(0x13ec, 0x00, 0x10)
    yield from ampio.close()


@asyncio.coroutine
def on_discovered(modules):
    """Handle the on discovered event when discovery phase is finished."""
    for _, mod in modules.modules.items():
        print(mod)
    print("Discovered {} modules.".format(len(modules.modules)))
    print("Registering for value change events.")
    # Subscribe to all values
    for can_id, mod in modules.modules.items():
        modules.add_on_value_changed_callback(can_id=can_id, attribute=None, index=None, callback=on_value_changed)
    # modules.add_on_value_changed_callback(can_id=0x1ecc, attribute='bin_input', index=9, callback=on_value_changed)


log_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "ERROR": logging.ERROR,
    "NONE": logging.NOTSET,
}


@click.group()
def cli():
    """CLI Entry."""
    pass


@cli.command("call", help="Call the API function", short_help="Call API")
@click.option("--port", required=True, envvar='AMPIO_PORT', type=click.Path(),
              help='The USB interface full path i.e. /dev/cu.usbserial-DN01D1W1. '
                   'If no --port option provided the AMPIO_PORT environment variable is used.')
@click.option("--log-level", type=click.Choice(["NONE", "DEBUG", "INFO", "ERROR"]),
              show_default=True, default='ERROR',
              help='Logging level.')
@click.option("--can_id", required=True, type=BASED_INT,
              help="CAN ID")
@click.option("--command", required=True, type=str,
              help="Command to execute: [set_value,]")
@click.option("--index", required=True, type=int,
              help="Value Index")
@click.option("--value", required=True, type=BASED_INT,
              help="Value")
def call(port, log_level, can_id, command, index, value):
    """Call module function."""
    formatter = "[%(asctime)s] %(levelname)s - %(message)s"
    logging.basicConfig(level=log_levels[log_level], format=formatter)

    loop = asyncio.get_event_loop()
    ampio_gw = AmpioGateway(port=port, loop=loop)
    # ampio_gw.add_on_discovered_callback(partial(on_discovered_call, loop, can_id, command, index, value, ampio_gw))
    loop.create_task(send_command(ampio_gw, can_id, command, index, value))
    loop.run_forever()
    loop.close()
    pass


@cli.command("run", help="Run Ampio Gateway", short_help="Run Gateway")
@click.option("--port", required=True, envvar='AMPIO_PORT', type=click.Path(),
              help='The USB interface full path i.e. /dev/cu.usbserial-DN01D1W1. '
                   'If no --port option provided the AMPIO_PORT environment variable is used.')
@click.option("--no-query-details", required=False, is_flag=True,
              help='Run the full module details query')
@click.option("--log-level", type=click.Choice(["NONE", "DEBUG", "INFO", "ERROR"]),
              show_default=True, default='ERROR',
              help='Logging level.')
def run(port, log_level, no_query_details):
    """Run main function."""
    formatter = "[%(asctime)s] %(levelname)s - %(message)s"
    logging.basicConfig(level=log_levels[log_level], format=formatter)

    loop = asyncio.get_event_loop()
    ampio_gw = AmpioGateway(port=port, loop=loop, no_query_module_details=no_query_details)
    ampio_gw.add_on_discovered_callback(on_discovered)
    loop.run_forever()
    loop.close()


@cli.command("version", help="Display the PyAMPIO version", short_help="Version")
def show_version():
    """Display module version number."""
    click.echo("PyAMPIO Version {}\n(c) 2018, Klaudiusz Staniek".format(v.__version__))


if __name__ == '__main__':
    cli()
