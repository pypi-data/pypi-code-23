import argparse
import errno
import logging
import os
import pickle
import re
import shutil
import tarfile
from tempfile import NamedTemporaryFile
from time import sleep
from warnings import catch_warnings, filterwarnings
from zipfile import ZipFile

import boto3
import httplib2
import requests
from apiclient import discovery
from googleapiclient.http import MediaIoBaseDownload
from oauth2client import client
from oauth2client import tools
from oauth2client._helpers import _MISSING_FILE_MESSAGE
from oauth2client.file import Storage

from businessoptics.utils import only

log = logging.getLogger(__name__)


class CachedFileGetter(object):
    def __init__(self, key):
        self.key = key

    def get_and_save(self, path):
        raise NotImplementedError()

    def get_metadata(self):
        return NotImplemented

    def is_cache_valid(self, new_meta, old_meta, path):
        return new_meta == old_meta

    def cache_root_location(self):
        return os.path.join(os.path.expanduser('~'),
                            '.download_cache',
                            self.__class__.__name__)

    def path(self):
        base = os.path.join(self.cache_root_location(),
                            str(self.key).lstrip('/\\'))
        path = os.path.join(base, 'thefile')
        meta_path = os.path.join(base, 'meta')

        try:
            os.makedirs(base)
        except OSError as exception:
            if exception.errno != errno.EEXIST:

                raise

        new_meta = self.get_metadata()

        cached = os.path.exists(path)
        if new_meta is not NotImplemented:
            if cached:
                try:
                    with open(meta_path, 'rb') as meta_file:
                        old_meta = pickle.load(meta_file)
                except IOError:
                    pass
                else:
                    cached = self.is_cache_valid(new_meta, old_meta, path)

            with open(meta_path, 'wb') as meta_file:
                pickle.dump(new_meta, meta_file, protocol=2)

        if not cached:
            self.get_and_save(path)
        return path

    def open(self, mode='rb', **kwargs):
        return open(self.path(), mode=mode, **kwargs)

    def unzip(self, member=None, password=None):
        return CachedUnzipper(self.path(), member, password)

    def untar(self, member=None):
        return CachedUnTar(self.path(), member)


class CachedTuplesCSV(CachedFileGetter):
    def __init__(self, has_tuples):
        self.meta = has_tuples.get()
        match = re.match(r'/api/v2/query/\d+/(result/.+)$', has_tuples.base_url)
        if match:
            client = has_tuples.root
            cached_query_url = client.get(self.meta['query'])['from_cache']
            if cached_query_url:
                log.debug('Using cached query at %s', cached_query_url)
                has_tuples = has_tuples.__class__.at(client / cached_query_url / match.group(1))
                self.meta = has_tuples.get()
        self.has_tuples = has_tuples
        super(CachedTuplesCSV, self).__init__(has_tuples.full_url.replace('/', '_'))

    def get_metadata(self):
        return self.meta

    def get_and_save(self, path):
        log.info('Downloading CSV of %s', self.has_tuples.full_url)
        download_url = self.has_tuples.get('external_stream_csv')['download_url']
        with NamedTemporaryFile() as temp_zip_file:
            while True:
                response = requests.get(download_url, stream=True)
                if response.status_code == 200:
                    break
                sleep(5)
            shutil.copyfileobj(response.raw, temp_zip_file)
            temp_zip_file.flush()
            with ZipFile(temp_zip_file) as zipfile:
                extracted_path = zipfile.extract(zipfile.infolist()[0])
        shutil.move(extracted_path, path)
        log.info('Finished downloading CSV')


class CachedGoogleDriveFile(CachedFileGetter):
    """
    Download a file from Google Drive.

    Accepts a file ID or a URL containing it in one of the following formats:

        - https://drive.google.com/open?id=<file ID>
          (obtained by clicking on a file and then 'Get shareable link')
        - https://drive.google.com/file/d/<file ID>/view
          (a link of the first type typically redirects to a link like this)

    Requires the file ~/.google-credentials/client_secret.json. If it's not present it
    will try to download it from S3, so having access to AWS credentials is useful.

    Using this for the first time will require opening a link in a browser, authenticating
    through Google, and pasting a code into the terminal.
    """
    def __init__(self, id_or_link):
        file_id = self.extract_file_id(id_or_link)

        super(CachedGoogleDriveFile, self).__init__(file_id)
        self.file_id = file_id
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.google-credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'credentials.json')
        client_secret_path = os.path.join(credential_dir, 'client_secret.json')

        store = Storage(credential_path)
        with catch_warnings():
            filterwarnings('ignore', _MISSING_FILE_MESSAGE.format(credential_path))
            credentials = store.get()

        if not credentials or credentials.invalid:
            if not os.path.exists(client_secret_path):
                log.info('Client secret not found at %s. Downloading...', client_secret_path)
                try:
                    boto3.client('s3').download_file('businessoptics-alex',
                                                     'cs.json',
                                                     client_secret_path)
                except Exception:
                    log.error('Error downloading the client secret. Request it from Alex.')
                    raise
            flow = client.flow_from_clientsecrets(
                client_secret_path, 'https://www.googleapis.com/auth/drive.readonly')
            flow.user_agent = 'businessoptics client'
            flags = argparse.ArgumentParser(parents=[tools.argparser]
                                            ).parse_args(['--noauth_local_webserver'])
            credentials = tools.run_flow(flow, store, flags)
            print('Storing credentials to ' + credential_path)

        http = credentials.authorize(httplib2.Http())

        autodetect_logger = logging.getLogger('googleapiclient.discovery_cache')
        old_level = autodetect_logger.level
        autodetect_logger.setLevel(logging.ERROR)
        try:
            self.service = discovery.build('drive', 'v3', http=http)
        finally:
            autodetect_logger.level = old_level

    @staticmethod
    def extract_file_id(id_or_link):
        for pattern in [r'drive.google.com/open\?id=([\w_-]+)$',
                        r'drive.google.com/file/\w/([\w_-]+)/\w+$',
                        r'^([\w_-]+)$']:
            match = re.search(pattern, id_or_link)
            if match:
                return match.group(1)
        raise ValueError("Failed to extract file ID from %s", id_or_link)

    def get_metadata(self):
        return self.service.files().get(fileId=self.file_id, fields='md5Checksum').execute()['md5Checksum']

    def get_and_save(self, path):
        log.info('Downloading file %s from Google Drive to %s', self.file_id, path)
        request = self.service.files().get_media(fileId=self.file_id)
        with open(path, 'wb') as outfile:
            downloader = MediaIoBaseDownload(outfile, request)
            done = False
            progress = 0
            while done is False:
                status, done = downloader.next_chunk()
                new_progress = int(status.progress() * 100)
                if new_progress > progress:
                    progress = new_progress
                    log.info('Downloaded %d%%', progress)


class CachedUnzipper(CachedFileGetter):
    def __init__(self, zip_path, member=None, password=None):
        self.zip_path = os.path.abspath(zip_path)
        self.zipfile = ZipFile(zip_path)
        if member is None:
            member = only(self.zipfile.infolist())
        else:
            member = only(m for m in self.zipfile.infolist() if m.filename == member)

        super(CachedUnzipper, self).__init__(zip_path + '/' + member.filename)
        self.member = member
        self.password = password

    def get_and_save(self, path):
        log.info('Unzipping...')
        with self.zipfile:
            outpath = self.zipfile.extract(self.member, os.path.dirname(path), self.password)
        shutil.move(outpath, path)

    def get_metadata(self):
        stat = os.stat(self.zip_path)
        m = self.member
        return (stat.st_size, stat.st_mtime,
                m.date_time, m.CRC, m.file_size)


class CachedUnTar(CachedFileGetter):
    def __init__(self, tar_path, member=None):
        self.tar_path = os.path.abspath(tar_path)
        self.tarfile = tarfile.open(tar_path)
        if member is None:
            member = only(self.tarfile.getmembers())
        else:
            member = only(m for m in self.tarfile.getmembers() if m.name == member)

        super(CachedUnTar, self).__init__(tar_path + '/' + member.name)
        self.member = member

    def get_and_save(self, path):
        log.info('Extracting tar...')
        dirname = os.path.dirname(path)
        with self.tarfile:
            self.tarfile.extractall(dirname, [self.member])
        shutil.move(os.path.join(dirname, self.member.name),
                    path)

    def get_metadata(self):
        stat = os.stat(self.tar_path)
        m = self.member
        return (stat.st_size, stat.st_mtime,
                m.size, m.mtime)
