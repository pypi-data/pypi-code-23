#!/usr/bin/env python
import tempfile
import zipfile
import os

from six.moves.urllib.request import urlretrieve


LDRAW_URL = 'http://www.ldraw.org/library/updates/complete.zip'


def dowload_data(output_directory):
    fd, retrieved = tempfile.mkstemp(suffix='.zip')

    if not os.path.exists(retrieved):
        print('retrieve the complete.zip from ldraw.org ...')
        retrieved, _ = urlretrieve(LDRAW_URL, filename=retrieved)

    if not os.path.exists(os.path.join(output_directory, 'ldraw')):
        print('unzipping the complete.zip ...')
        zip_ref = zipfile.ZipFile(retrieved, 'r')
        zip_ref.extractall(output_directory)
        zip_ref.close()
