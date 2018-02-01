#!/usr/bin/env python
from __future__ import unicode_literals
import hashlib
import multiprocessing
import os
from datetime import datetime
import argparse
import zipfile
import time
import sys

#
#  Netflix Frame Sequence package manager.
#  For use in ContentHub uploads only.
#
CHECKSUM_TXT = "checksum.txt"

if sys.version_info[0] < 3:
    import codecs
    _open_func_bak = open # Make a back up, just in case
    open = codecs.open

read_block_size = 2 ** 20

def create_zip(source_folder, target_folder, zip_file_name):
    if is_valid_folder(source_folder, os.W_OK) and is_valid_folder(target_folder, os.W_OK):
        try:
            zip_file_full_path = os.path.join(target_folder, zip_file_name)
            print("%s | Initializing zip file %s" % (datetime.utcnow(), zip_file_full_path))
            zip_file = zipfile.ZipFile(zip_file_full_path, 'w', zipfile.ZIP_STORED, True)
            zip_directory(source_folder, zip_file)
            zip_file.close()
            print("%s | Finished zip file %s" % (datetime.utcnow(), zip_file_full_path))
        except IOError as e:
            eprint("Unable to zip files from %s because %" % (source_folder, str(e)))
            sys.exit(1)


def zip_directory(path, zip_file):
    for root, dirs, files in os.walk(path):
        for file in files:
            absolute_file_path = str(os.path.join(root, file))
            if os.path.isfile(absolute_file_path):
                try:
                    file_name = os.path.basename(absolute_file_path)
                    relative_path = os.path.relpath(root, path)
                    zip_file_relative_path = os.path.join(relative_path, file_name)
                    if not file_name.startswith('.') and CHECKSUM_TXT not in file_name:
                        zip_file.write(str(absolute_file_path), arcname=str(zip_file_relative_path), compress_type=zipfile.ZIP_STORED)
                except IOError as e:
                    eprint("Error zipping file %s absolute path %s relative path %s because %s" % (file, absolute_file_path, zip_file_relative_path, str(e)))
                    sys.exit(1)
            else:
                eprint("Unrecognized file %s absolute path %s. Remove special characters and try again." % (file, absolute_file_path))
                sys.exit(1)


def eprint(data):
    sys.stderr.write('\n')
    sys.stderr.write("%s | ERROR! \n" % datetime.utcnow())
    sys.stderr.write(data)
    sys.stderr.write('\n\n')
    sys.stderr.flush()


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


def md5_file(file_path):
    try:
        with open(file_path, 'rb') as file_io:
            md5 = hashlib.md5()
            file_name = os.path.basename(file_path)
            while True:
                data = file_io.read(read_block_size)
                if not data:
                    break
                md5.update(data)
            hex_digest = md5.hexdigest()
            md5_file.queue.put(
                "%s\t%s\t%s\t%s" % (file_name.strip(), os.path.getsize(file_path), "md5", hex_digest.strip()))
    except IOError as e:
        eprint("Unable to calculate checksum for %s because of %s" % (file_path, str(e)))
        sys.stdout.flush()
        sys.exit(1)


def is_valid_file(full_path):
    file_name = os.path.basename(full_path)
    is_valid = not file_name.startswith('.') and CHECKSUM_TXT not in file_name and os.path.isfile(full_path)
    return is_valid


def is_valid_folder(folder, access_type):
    if folder is not None and os.path.exists(folder) and os.path.isdir(folder) and os.access(folder, access_type):
        return True
    else:
        raise Exception("%s | Path provided not accessible %s" % (datetime.utcnow(), str(folder)))


def init_queue(queue):
    md5_file.queue = queue


def create_checksum(sequence_folder, cpu_cores):
    req_version = (2, 7)
    cur_version = (sys.version_info[0], sys.version_info[1])
    if cur_version < req_version:
        eprint("Python interpreter is %s. Please upgrade to %s and above" % (str(cur_version), str(req_version)))
        sys.exit(1)

    files_processed = 0
    checksum_entries = []
    unique_file_names_set = set()
    queue = multiprocessing.Queue()
    pool = multiprocessing.Pool(cpu_cores, init_queue, [queue])
    if is_valid_folder(sequence_folder, os.R_OK):
        for directory_path, directory_names, file_names in os.walk(sequence_folder):
            try:
                full_path_file_names = map(lambda fn: os.path.join(directory_path, fn), file_names)
                full_path_file_names = filter(is_valid_file, full_path_file_names)
                full_path_file_names_list = list(full_path_file_names)

                unique_file_names_set = validate_uniqueness(full_path_file_names, unique_file_names_set)

                file_count = len(full_path_file_names_list)
                files_processed = files_processed + file_count
                print("%s | Identified %s files to checksum in %s" % (datetime.utcnow(), file_count, str(directory_path)))
                for full_path_file_names_batch in batch(full_path_file_names_list, 1000):
                    pool.map(md5_file, full_path_file_names_batch)
                    while not queue.empty():
                        checksum_entries.append(queue.get())
            except BaseException as e:
                eprint("Unable to traverse path %s because of %s" % (str(directory_path), str(e)))

    while not queue.empty():
        checksum_entries.append(queue.get())

    print("%s | Calculated %s checksums" % (datetime.utcnow(), len(checksum_entries)))

    if files_processed != len(checksum_entries):
        eprint("Unable to create checksum.txt, expected %s but found %s checksums" % (files_processed, len(checksum_entries)))
        sys.exit(1)

    checksum_entries.sort()

    return checksum_entries


def validate_uniqueness(full_path_file_names, unique_file_names_set):
    base_file_names_list = map(lambda fn: os.path.basename(fn), full_path_file_names)
    base_file_names_set = set(base_file_names_list)
    if len(unique_file_names_set.intersection(base_file_names_set)) > 0:
        eprint("Please separate packages, unique file names expected, found duplicates:\n%s" % ('\n'.join(unique_file_names_set.intersection(base_file_names_set))))
        sys.exit(1)
    elif len(base_file_names_list) != len(base_file_names_set):
        eprint("Please separate packages, unique file names expected, found duplicates:\n%s" % ('\n'.join(list(base_file_names_set) - base_file_names_list)))
        sys.exit(1)
    else:
        return unique_file_names_set.union(base_file_names_set)


def write_checksum_to_file(folder, checksum_entries):
    if is_valid_folder(folder, os.W_OK):
        try:
            checksum_file = open(os.path.join(folder, 'checksum.txt'), 'w', encoding='utf-8')
            for entry in checksum_entries:
                checksum_file.write("%s\n" % str(entry))
            print("%s | Completed writing to checksum.txt" % (datetime.utcnow()))
        except BaseException as e:
            eprint("Unable to write checksum.txt within folder %s because of %s" % (str(folder), str(e)))
            sys.exit(1)

def write_checksum_to_zip(target_folder, zip_file_name, checksum_entries):
    if is_valid_folder(target_folder, os.W_OK):
        try:
            zip_file_full_path = os.path.join(target_folder, zip_file_name)
            zip_file = zipfile.ZipFile(zip_file_full_path, "a", zipfile.ZIP_STORED, True)
            checksum_file_string = ""
            for entry in checksum_entries:
                checksum_file_string += "%s\n" % str(entry)
            zip_file.writestr('checksum.txt', checksum_file_string)
            print("%s | Completed writing to checksum.txt" % (datetime.utcnow()))
        except BaseException as e:
            eprint("Unable to write checksum.txt within folder %s because of %s" % (str(target_folder), str(e)))
            sys.exit(1)

def main():
    print('''
     _  _ ___ _____ ___ _    _____  __    
    | \| | __|_   _| __| |  |_ _\ \/ /    
    | .` | _|  | | | _|| |__ | | >  <     
    |_|\_|___| |_| |_| |____|___/_/\_\    npack.py version 0.5.6
                                          designed for ContentHub uploads only
                                          for questions please contact backlot.support@netflix.com''')
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')
    parser.set_defaults(act='')

    checksum_parser = subparsers.add_parser('checksum', help='Create a Checksum File')
    checksum_parser.add_argument('-s', '--source', help='Source folder', required=True)
    checksum_parser.add_argument('--preview', default=False, action='store_true', help='Calculate checksum without storing')
    checksum_parser.add_argument('-cpu', '--cpu_cores', type=int, help='hint for utilizing specific # of cpu cores for checksum',required=False)
    checksum_parser.set_defaults(act='checksum')

    zip_parser = subparsers.add_parser('zip', help='Create Zip with a Checksum File')
    zip_parser.add_argument('-s', '--source', help='Source folder', required=True)
    zip_parser.add_argument('-t', '--target', help='Target folder for zip')
    zip_parser.add_argument('-f', '--file', help='resulting zip filename', required=False, default="sequence.zip")
    zip_parser.add_argument('-cpu', '--cpu_cores', type=int, help='hint for utilizing specific # of cpu cores for checksum', required=False)
    zip_parser.set_defaults(act='zip')
    start_time = time.time()
    try:
        args = parser.parse_args()
        if args.act == "zip":
            zip_file_name = str(args.file)
            source_folder = str(args.source)
            if args.target is None:
                target_folder = str(os.path.abspath(os.path.join(source_folder, '..')))
            else:
                target_folder = str(args.target)

            checksums = create_checksum(source_folder, args.cpu_cores)
            create_zip(source_folder, target_folder, zip_file_name)
            write_checksum_to_zip(target_folder, zip_file_name, checksums)
        elif args.act == "checksum":

            source_folder = str(args.source)
            checksums = create_checksum(source_folder, args.cpu_cores)
            if args.preview:
                for c in checksums:
                    print(c)
                sys.stdout.flush()
            else:
                write_checksum_to_file(source_folder, checksums)
        else:
            eprint("%s | Please select either zip or checksum option" % datetime.utcnow())
            parser.print_help()

        print("%s | Execution completed, took %s seconds" % (datetime.utcnow(), (time.time() - start_time)))
    except Exception as e:
        eprint(e.args[0])
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()