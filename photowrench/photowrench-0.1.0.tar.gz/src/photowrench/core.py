#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals, print_function

import sys
import os
import exifread
from datetime import datetime
from textwrap import dedent
from collections import defaultdict

try:
    input = raw_input
except NameError:
    pass


def _log(msg):
    print('photowrench: %s' % msg, file=sys.stderr)


def remove_raw_orphans(dir, pic_exts, raw_exts, batch):
    to_delete = []

    pic_paths_without_ext = set()
    raw_full_paths = []

    for file in os.listdir(dir):
        name, ext = os.path.splitext(file)
        ext = ext[1:].lower()

        if ext in pic_exts:
            pic_paths_without_ext.add(name)
            continue

        if ext in raw_exts:
            raw_full_paths.append(file)
            continue

    for raw in raw_full_paths:
        name = os.path.splitext(raw)[0]

        if name not in pic_paths_without_ext:
            to_delete.append(raw)

    if not to_delete:
        _log('No orphan raws identified')
        return

    if batch:
        delete = True
    else:
        prompt = 'Orphans identified:\n%s\n\nDo you want to delete them? (y/n) ' % '\n'.join(to_delete)
        delete = input(prompt).lower() == 'y'

    if not delete:
        return

    for name in to_delete:
        os.unlink(os.path.join(dir, name))

    _log('Done')


DATE_TAG = 'EXIF DateTimeOriginal'


def rename_to_ts(dir, pic_exts, batch):
    timestamped_name2orig_names = defaultdict(list)

    _log('Analyzing EXIF data')

    # NOTE: timestamps have a second resolution, so clashes can happen
    # easily. But it is ensured that the existing naming order is preserved
    # in case of collision.
    for file in sorted(os.listdir(dir)):
        name, ext = os.path.splitext(file)

        if ext[1:].lower() not in pic_exts:
            continue

        orig_name = os.path.join(dir, file)
        timestamped_name = os.path.join(dir, get_exif_date(orig_name)) + ext

        timestamped_name2orig_names[timestamped_name].append(orig_name)

    renamings = {}

    for timestamped_name, original_names in timestamped_name2orig_names.items():
        orig_count = len(original_names)
        # No collisions
        if orig_count == 1:
            renamings[original_names[0]] = timestamped_name
            continue

        number_width = len(str(orig_count))

        for i, orig_name in enumerate(original_names):
            base, ext = os.path.splitext(timestamped_name)
            renamings[orig_name] = '%s(%s)%s' % (base, str(i).zfill(number_width), ext)

    renamings = {key: val for key, val in renamings.items() if key != val}

    if not renamings:
        _log('No renaming necessary.')
        return

    if batch:
        rename = True
    else:
        prompt = dedent('''\
            Following files will be renamed:
            {}

            Do you want to continue? (y/n) '''
        ).format('\n'.join(sorted(['%s -> %s' % p for p in renamings.items()])))

        rename = input(prompt).lower() == 'y'

    if not rename:
        return

    for old, new in renamings.items():
        os.rename(old, new)

    _log('Done.')


def get_exif_date(pic_path):
    with open(pic_path, 'rb') as f:
        date_str = exifread.process_file(f, stop_tag=DATE_TAG).get(DATE_TAG)

    return datetime.strptime(date_str.values, '%Y:%m:%d %H:%M:%S').isoformat()
