"""Contains the acutal sync implementation"""
import os
import sys
import shutil
import platform
import glob
import logging
import datetime
import json
import concurrent.futures
import threading
import hashlib
import binascii

import boto3
import botocore
from colorama import Style

from classes.fileinfo import FileInfo


MAX_ATTEMPTS = 10
MULTIPART_PART_SIZE = 512  # in MB
fileblock = threading.Lock()


class Glacync(object):
    """Class containing all implementation details concerning the glacier sync"""
    folder = ""
    vault_name = ""
    mode = ""
    account_id = ""
    skip = ""
    pattern = ""
    weekly_cycle = 0

    glacier_resource = None
    glacier_client = None

    def __init__(self, folder, vault_name, mode, account_id, skip, pattern, weekly_cycle):
        self.folder = folder
        self.vault_name = vault_name
        self.mode = mode
        self.weekly_cycle = weekly_cycle
        self.account_id = account_id
        self.skip = skip
        self.pattern = pattern

        self.glacier_resource = boto3.resource('glacier')
        self.glacier_client = boto3.client('glacier')

    def get_latest_fileinfo(self, path=''):
        """Determines the most current file in a folder"""
        if not path:
            path = self.folder

        # Sanitary work
        if not path.endswith('/'):
            path += '/'

        try:
            files = [s for s in glob.glob(path + self.pattern)
                     if os.path.isfile(os.path.join(path, s))]
            files.sort(key=lambda s: os.path.getmtime(os.path.join(path, s)))
            source_path = os.path.join(path, files[len(files) - 1])
        except IndexError:
            logging.debug("Folder at '%s' is empty", path)
            raise
        else:
            return FileInfo(source_path, os.path.getmtime(source_path))

    def rotate_and_cleanup(self):
        """Cleanup backup files after sync run and rotate daily/weekly/monthly backups.
        Returns true when a new file was copied, deletions happen silently."""
        weekly_folder = os.path.join(self.folder, 'weekly')
        if not os.path.exists(weekly_folder):
            os.mkdir(weekly_folder)

        latest_file_weekly = None
        latest_file_local = None
        try:
            latest_file_weekly = self.get_latest_fileinfo(weekly_folder)
        except IndexError:
            logging.info("No weekly backups found, will use latest backup as init")

        try:
            latest_file_local = self.get_latest_fileinfo()
        except IndexError:
            logging.error("No backup files found at '%s' matching pattern '%s'",
                          self.folder, self.pattern)
            return False

        file_copied = False
        # If last file in weekly is missing or older than 7 days, move current backup
        if not latest_file_weekly or (
            latest_file_weekly.created + datetime.timedelta(days=7) < latest_file_local.created
        ):
            new_name = "%s_%s" % (datetime.datetime.now().strftime('%Y-%m-%d'),
                                  latest_file_local.name)

            target_path = os.path.join(self.folder, 'weekly', new_name)
            if not self.skip:
                shutil.copyfile(latest_file_local.path, target_path)
                file_copied = True
            else:
                logging.info(Style.DIM + "[cleanup] cp %s %s" + Style.RESET_ALL,
                             latest_file_local.path, target_path)
                file_copied = True

        # Cleanup old backups
        old_daily_backups = (bak for bak in glob.glob(os.path.join(self.folder, self.pattern))
                             if datetime.datetime.fromtimestamp(os.path.getmtime(bak)) +
                             datetime.timedelta(days=7) < datetime.datetime.now())
        for backup in old_daily_backups:
            if not self.skip:
                os.remove(backup)
            else:
                logging.info(Style.DIM + "[cleanup] rm %s" + Style.RESET_ALL, backup)

        # Cleanup old weekly backups if configured
        if self.weekly_cycle > 0:
            day_offset = self.weekly_cycle * 7
            old_weekly_backups = (bak for bak in glob.glob(os.path.join(weekly_folder, self.pattern))
                                  if datetime.datetime.fromtimestamp(os.path.getmtime(bak)) +
                                  datetime.timedelta(days=day_offset) < datetime.datetime.now())
            for backup in old_weekly_backups:
                if not self.skip:
                    os.remove(backup)
                else:
                    logging.info(Style.DIM + "[cleanup] rm %s" + Style.RESET_ALL, backup)

        return file_copied

    def do_sync(self, file):
        """Do the actual synchronization to AWS Glacier"""
        try:
            if not any(v for v in self.glacier_resource.vaults.all() if v.name == self.vault_name):
                # Auto-create vault
                self.glacier.create_vault(vaultName=self.vault_name)
        except botocore.exceptions.ClientError as cli_error:
            logging.error(cli_error.response)
            return False

        desc = "python-glacier-sync run on %s against %s%s" % (platform.node(),
                                                               self.folder, self.pattern)
        fs_obj = open(file.path, 'rb')
        if not self.skip:
            part_size = MULTIPART_PART_SIZE * 1024 * 1024
            file_size = fs_obj.seek(0, 2)

            job_list = []
            checksums = []

            multipart_res = self.glacier_client.initiate_multipart_upload(
                vaultName=self.vault_name,
                archiveDescription=desc,
                partSize=str(part_size)
            )
            upload_id = multipart_res['uploadId']
            logging.info('Fetched upload_id %s' % upload_id)
            for byte_pos in range(0, file_size, part_size):
                job_list.append(byte_pos)
                checksums.append(None)

            num_parts = len(job_list)
            logging.info('Starting threads...')

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures_list = {executor.submit(
                    upload_part, job, self.vault_name, upload_id, part_size, fs_obj,
                    file_size, num_parts, self.glacier_client
                ): job // part_size for job in job_list}
                done, not_done = concurrent.futures.wait(
                    futures_list, return_when=concurrent.futures.FIRST_EXCEPTION)

                if len(not_done) > 0:
                    for future in not_done:
                        future.cancel()
                    for future in done:
                        e = future.exception()
                        if e is not None:
                            logging.error('Exception while uploading: %r' % e)
                    logging.info('Upload not aborted, uploadId is %s' % upload_id)
                else:
                    for future in done:
                        job_index = futures_list[future]
                        checksums[job_index] = future.result()

            if len(checksums) != num_parts:
                logging.info('List of checksums incomplete, recalculating...')
                checksums = []
                for byte_pos in range(0, file_size, part_size):
                    part_num = int(byte_pos / part_size)
                    logging.info('Checksum %s of %s...' % (part_num + 1, num_parts))
                    fs_obj.seek(byte_pos)
                    part = fs_obj.read(part_size)
                    checksums.append(calculate_tree_hash(part, part_size))

            total_tree_hash = calculate_total_tree_hash(checksums)

            logging.info('Completing multipart upload...')
            upload_res = self.glacier_client.complete_multipart_upload(
                vaultName=self.vault_name, uploadId=upload_id,
                archiveSize=str(file_size), checksum=total_tree_hash
            )
            logging.info('Upload successful.')
            fs_obj.close()

            # Write metadata-file with archive id
            with open(file.path + '.awsmeta.json', 'w') as metafile:
                json.dump({
                    "archive_id": upload_res['archiveId'],
                    "account_id": self.account_id,
                    "vault": self.vault_name
                }, metafile)
        else:
            logging.info(Style.DIM + "[do_sync] desc: %s" + Style.RESET_ALL, desc)
            logging.info(Style.DIM + "[do_sync] fsObject: %s" + Style.RESET_ALL, fs_obj)

        return True


def upload_part(byte_pos, vault_name, upload_id, part_size, fileobj, file_size,
                num_parts, glacier_cli):
    fileblock.acquire()
    fileobj.seek(byte_pos)
    part = fileobj.read(part_size)
    fileblock.release()

    range_header = 'bytes {}-{}/{}'.format(
        byte_pos, byte_pos + len(part) - 1, file_size)
    part_num = byte_pos // part_size
    percentage = part_num / num_parts

    logging.info('Uploading part {0} of {1}... ({2:.2%})'.format(
        part_num + 1, num_parts, percentage))

    for i in range(MAX_ATTEMPTS):
        try:
            response = glacier_cli.upload_multipart_part(
                vaultName=vault_name, uploadId=upload_id,
                range=range_header, body=part)
            checksum = calculate_tree_hash(part, part_size)
            if checksum != response['checksum']:
                logging.info('Checksums do not match. Will try again.')
                continue

            # if everything worked, then we can break
            break
        except:
            logging.error('Upload error:', sys.exc_info()[0])
            logging.info('Trying again. Part {0}'.format(part_num + 1))
    else:
        logging.error('After multiple attempts, still failed to upload part')
        logging.info('Exiting.')
        sys.exit(1)

    del part
    return checksum


def calculate_tree_hash(part, part_size):
    checksums = []
    upper_bound = min(len(part), part_size)
    step = 1024 * 1024  # 1 MB
    for chunk_pos in range(0, upper_bound, step):
        chunk = part[chunk_pos:chunk_pos+step]
        checksums.append(hashlib.sha256(chunk).hexdigest())
        del chunk
    return calculate_total_tree_hash(checksums)


def calculate_total_tree_hash(list_of_checksums):
    tree = list_of_checksums[:]
    while len(tree) > 1:
        parent = []
        for i in range(0, len(tree), 2):
            if i < len(tree) - 1:
                part1 = binascii.unhexlify(tree[i])
                part2 = binascii.unhexlify(tree[i + 1])
                parent.append(hashlib.sha256(part1 + part2).hexdigest())
            else:
                parent.append(tree[i])
        tree = parent
    return tree[0]
