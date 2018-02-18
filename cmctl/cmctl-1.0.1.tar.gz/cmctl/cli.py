'''CLI module.'''

import datetime
import os
import sys
import time
import click
from .talker import Talker, TalkerException

FILTERS = ['none', 'average', 'hybrid', 'median']

@click.group()
def cli():
    '''Conductometer Control Tool.'''

@cli.command()
def devices():
    '''Print available devices.'''
    if os.name == 'nt' or sys.platform == 'win32':
        from serial.tools.list_ports_windows import comports
    elif os.name == 'posix':
        from serial.tools.list_ports_posix import comports
    for port in sorted(comports()):
        click.echo(port[0], err=True)

@cli.command()
@click.option('--device', '-d', type=str, required=True, help='Device path.')
@click.option('--interval', '-i', default=1, type=click.IntRange(1, 86400), help='Scan interval in milliseconds.')
@click.option('--frequency', '-f', default=10000, type=click.IntRange(10, 1000000), help='Modulation frequency in Hz.')
@click.option('--filtering', '-q', default='none', type=click.Choice(FILTERS), help='Algorithm for filtering.')
@click.option('--samples', '-a', default=1, type=click.IntRange(1, 256), help='Number of samples for filtering.')
@click.option('--no-sync', '-s', is_flag=True, help='Disable synchronous demodulation.')
@click.argument('channels', default='1,2,3,4,5,6,7,8,9,10,11,12')
def scan(device, interval, frequency, filtering, samples, no_sync, channels):
    '''Scan specified channels.'''
    channels = list(set(map(str.strip, channels.split(','))))
    for channel in channels:
        if not channel.isdigit() or int(channel) < 1 or int(channel) > 12:
            raise click.BadArgumentUsage('Channels must be supplied as comma-separated numbers.')
    click.echo('Scan interval: %d seconds' % (interval), err=True)
    click.echo('Modulation frequency: %d Hz' % (frequency), err=True)
    click.echo('Filtering algorithm: %s' % (filtering), err=True)
    click.echo('Number of samples: %d' % (samples), err=True)
    click.echo('Synchronous demodulation: %s' % ('no' if no_sync else 'yes'), err=True)
    for i in range(1, 13):
        click.echo('Channel %d enabled: %s' % (i, 'yes' if str(i) in channels else 'no'), err=True)
    talker = Talker(device)
    talker.command('F%d' % (frequency))
    talker.command('A%d' % (samples))
    if filtering == 'average':
        talker.command('Q1')
    elif filtering == 'hybrid':
        talker.command('Q2')
    elif filtering == 'median':
        talker.command('Q3')
    else:
        talker.command('Q0')
    talker.command('D%d' % (0 if no_sync else 1))
    while True:
        record = datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds')
        click.echo('Scanning at %s...' % (record), err=True)
        for i in range(1, 13):
            record += ';'
            if str(i) in channels:
                value = talker.query('R%d' % (i))
                if not value.isdigit() or int(value) < 0 or int(value) > 65535:
                    raise TalkerException
                record += value
        click.echo(record)
        time.sleep(interval)

def main():
    '''Application entry point.'''
    try:
        cli()
    except TalkerException:
        click.echo('Communication error occurred!', err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
