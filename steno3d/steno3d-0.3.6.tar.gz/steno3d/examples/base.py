"""base.py sets up BaseExample class that allows examples to be accessed
as properties at the class level
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os import makedirs, mkdir
from os.path import exists, expanduser, isdir, realpath, sep

from requests import get
from six import string_types
from zipfile import ZipFile


class exampleproperty(object):
    """wrapper that sets class method as property"""

    def __init__(self, func):
        self.func = classmethod(func)

    def __get__(self, cls, owner):
        return self.func.__get__(None, owner)()


class BaseExample(object):
    """basic class that all examples inherit from"""

    def __init__(self, *args, **kwargs):
        raise TypeError('Examples cannot be instantiated. Please access '
                        'the properties directly.')

    @exampleproperty
    def example_name(self):
        return self.__name__

    @exampleproperty
    def data_directory(self):
        """path to directory containing all assets"""
        return sep.join([expanduser('~'), '.steno3d_client', 'assets'])

    @exampleproperty
    def sub_directory(self):
        return self.example_name.lower()

    @exampleproperty
    def filenames(self):
        return []

    @exampleproperty
    def data_url(self):
        return 'https://storage.googleapis.com/steno3d-examples'

    @classmethod
    def fetch_data(cls, directory=None, download_if_missing=True,
                   filename=None, verbose=True):
        """method fetch_data

        This method checks for example data locally and downloads and
        extracts the archive if necessary.

        Inputs:
            directory:           Local folder to save the archive and
                                 extracted data.
                                 (default: ~/.steno3d_client/assets/)
            download_if_missing: Download the data archive if it is not
                                 found locally. (default: True)
            filename:            Specific data file to fetch. If none,
                                 fetch all example data. (default: None)
            verbose:             Print download/extraction status.
                                 (default: True)
        """

        if filename is not None and not isinstance(filename, string_types):
            raise ValueError('filename: must be the name of one file')
        if cls.filenames == []:
            raise ValueError('Example does not require any files')
        if directory is not None and not isinstance(directory, string_types):
            raise ValueError('directory: must be the name of a directory')
        if directory is not None:
            directory = realpath(expanduser(directory))
            if not isdir(directory):
                raise ValueError(
                    '{}: directory does not exist'.format(directory)
                )
            cls._data_directory = directory
        if verbose:
            print('Fetching data...')
        destination = sep.join([cls.data_directory, cls.sub_directory])
        archive = sep.join([destination, cls.sub_directory + '.zip'])
        if download_if_missing and not exists(cls.data_directory):
            makedirs(cls.data_directory)
        if download_if_missing and not exists(destination):
            mkdir(destination)
        if verbose:
            print('Destination: ' + destination)
        filenames = cls.filenames if filename is None else [filename]
        for fname in filenames:
            if verbose:
                print('    Fetching: ' + fname)
            destination_file = sep.join([destination, fname])
            if exists(destination_file):
                if verbose:
                    print('... Local copy found')
                if filename is not None:
                    return destination_file
                continue
            if not exists(archive) and download_if_missing:
                if verbose:
                    print('        Downloading archive...')
                url = '/'.join([cls.data_url, cls.sub_directory + '.zip'])
                resp = get(url, stream=True)
                if resp.status_code != 200:
                    raise IOError('Error downloading {exclass} data: '
                                  '{archfile}'.format(
                                    exclass=cls.example_name,
                                    archfile=archive
                                  ))
                with open(archive, 'wb') as arch:
                    for chunk in resp:
                        arch.write(chunk)
                if verbose:
                    print('        Archive downloaded successfully!')
            if exists(archive):
                if verbose:
                    print('        Local archive found: extracting...')
                try:
                    zf = ZipFile(archive)
                    zf.extract(fname, destination)
                    if verbose:
                        print('... File extracted successfully!')
                    if filename is not None:
                        return destination_file
                except KeyError:
                    raise IOError(
                        """Required file(s) not found in archive:
                        Archive file may be out of date. Please delete archive
                        and {exclass}.fetch_data() again: {archfile}""".format(
                            exclass=cls.example_name,
                            archfile=archive
                        )
                    )
                continue
            raise IOError(
                """Required file(s) not found:
                Please call {exclass}.fetch_data() to download and
                save to a default folder in your home directory or
                {exclass}.fetch_data(directory=your_local_directory)
                to set an alternative local directory.""".format(
                    exclass=cls.example_name
                )
            )
