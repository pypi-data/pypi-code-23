import click
import os

from .api_client import ApiClient, ApiException
from .util.hashing import hash_path
from collections import namedtuple


@click.command(short_help="upload file for analysis")
@click.option("--recursive/--norecursive", is_flag=True)
@click.argument('upload_path', type=click.Path(exists=True, resolve_path=True))
def upload(upload_path, recursive):
    # `upload_path` should be a real, absolute path to a file or directory that exists.
    processor = UploadProcessor(upload_path, recursive)

    processor.process()

    if processor.results:
        click.echo("Uploading Results:")
        click.echo("sha1,result,message,filepath")
    for result in processor.results:
        click.echo(",".join(result))


class UploadProcessor(object):
    """
    Attributes
    ----------
    path: str
    recursive: bool
    is_directory: bool
    is_file: bool
    results: List[self.UploadStatus]
        The results of all uploaded files. List is cleared when `process()` called.
    """

    class UploadResult(namedtuple("UploadStatus", "sha1 result message filepath")):
        """ Internal class for storing result of uploading a single file.
        Attributes
        ----------
        sha1: str
        result: str
            One of: 'uploaded' | 'preexisting' | 'error'
        message: str
            The message returned by the API.
        filepath: str
            The filepath of the uploaded file. Includes full path.
        """

    def __init__(self, upload_path, recursive=True):
        """
        Parameters
        ----------
        upload_path: str
            Real, absolute path to the file or directory to upload
        recursive: bool
            If true, recurse into subdirectories. If `upload_path` is a directory and
            `recursive` is False, only files in `upload_path` and *not* files in subdirectories
            will be uploaded.
        """
        self.path = upload_path
        self.recursive = True
        self.is_directory = os.path.isdir(self.path)
        self.is_file = not self.is_directory and os.path.isfile(self.path)
        self.results = list()
        if not self.is_directory and not self.is_file:
            raise ValueError("Path must be a directory or file.")

    def process(self):
        self.results = list()
        if self.is_file:
            self.upload_file(self.path)
        # If it's not a file, it MUST be a directory.
        else:
            self.upload_directory(self.path)

    def upload_file(self, filepath):
        # The API gateway is *supposed* to strip the directory, but we'll just
        # go ahead and do it here as well. This adds redundancy and entirely avoids
        # transmitting potentially sensitive path names.
        filename = os.path.basename(filepath)
        # Manually hash the file because we can't rely on the response to have the hash.
        sha1 = hash_path(filepath)
        try:
            response = ApiClient().create_file(filepath, filename=filename)
        except ApiException as exc:
            # If we have a response, try and get the response's message.
            # Fall back onto the exception's stored reason if needed.
            message = None
            if exc.body and hasattr(exc.body, 'message'):
                message = exc.body.message
            message = message or exc.reason

            result = self.UploadResult(sha1=sha1, result='error', message=message, filepath=filepath)
            self.results.append(result)
            return result

        # Get the status
        if response.code == 200:
            status = 'preexisting'
        elif response.code == 201:
            status = 'uploaded'
        # This shoudln't happen because code > 299 raises ApiException.
        # Still keeping in for completeness.
        else:
            status = 'error'

        result = self.UploadResult(sha1=sha1, result=status, message=response.message, filepath=filepath)
        self.results.append(result)
        return result

    def upload_directory(self, directory):
        file_generator = os.walk(directory, topdown=True)
        # Always upload files in the first level
        root, _, files = next(file_generator)
        assert directory == root
        for filename in files:
            self.upload_file(os.path.join(root, filename))
        # If recursive, upload the rest.
        if self.recursive:
            for root, _, files in file_generator:
                for filename in files:
                    self.upload_file(os.path.join(root, filename))
