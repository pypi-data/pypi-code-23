"""Module used to sync local backups to Amazon Glacier"""
from time import monotonic as timer
import logging
import os
import click
from colorama import init, Fore, Style

from classes.glacync import Glacync

# Configure logging
logging.basicConfig(format=Fore.YELLOW + '[%(asctime)s] ' + Fore.RESET +
                    Style.BRIGHT + '%(levelname)s' + Style.RESET_ALL +
                    ': %(message)s', level=logging.INFO,
                    datefmt='%H:%M:%S')
init()


@click.command()
@click.argument('folder')
@click.argument('vaultName')
@click.option('--mode', default='weekly',
              help='Set the sync-mode for glacier, can be \'daily\' or \'weekly\' (default)')
@click.option('--account-id', default='',
              help='Set the id of your AWS account')
@click.option('--skip/--no-skip', default=False,
              help='Only simulate the sync run, skip the actual cleanup and sync')
@click.option('--pattern', default='*',
              help='The file pattern to search for')
@click.option('--weekly-cycle', default=0,
              help='''Defines after how many weeks the weekly backups are being removed
              (default = infinite retention)''')
def cli(folder, vaultname, mode, account_id, skip, pattern, weekly_cycle):
    """Runs the CLI for the glacier sync tool"""

    start = timer()

    sync = Glacync(folder, vaultname, mode, account_id, skip, pattern, weekly_cycle)

    # Start sync run
    logging.info("Starting sync run from '%s' to vault '%s'...", folder, vaultname)

    try:
        # Cleanup/rotate backups
        rotated = sync.rotate_and_cleanup()

        if rotated:
            # Determine latest file to sync based on weekly folder
            sync_file = sync.get_latest_fileinfo(os.path.join(sync.folder, 'weekly'))
            logging.info("Determined '%s' as the latest file to be synced to glacier.", sync_file)

            # Push file to glacier
            sync_res = sync.do_sync(sync_file)
            if not sync_res:
                logging.error("Sync run aborted, see errors above!")
                return
    except Exception as ex:
        logging.exception(ex)
    else:
        logging.info("Sync run completed.")
    finally:
        end = timer()
        logging.info("Run took %ss.", round(end - start, 2))
