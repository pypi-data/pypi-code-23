import sys
import inspect
import hashlib
import six
import os

from rook.services.bdb_location_service import BdbLocationService
from rook.services.import_service import ImportService

from rook.exceptions import ToolException, RookHashFailedException, RookHashMismatchException

from rook.lib.logger import logger

from rook.lib.processor.error import Error


class LocationFileLine(object):

    NAME = 'file_line'

    def __init__(self, arguments, processor_factory):
        self.filename = arguments.get('filename')
        # If we have a filename, make sure pyc is removed
        if self.filename:
            self.filename = self.filename.replace('.pyc', '.py')

        if self.filename is None:
            self.module_name = arguments['module_name'].lower()
        else:
            self.module_name = None

        self.lineno = arguments['lineno']

        self.file_hash = arguments.get('sha256')

    def add_aug(self, trigger_services, output, aug):
        logger.info("Adding aug")

        def callback(module):
            try:
                self.test_hash(module)

                trigger_services.get_service(BdbLocationService.NAME).add_breakpoint_aug(module, self.lineno, aug)
            except Exception as exc:
                message = "Exception when adding aug"
                logger.exception(message)
                aug.set_error(Error(exc=exc, message=message))

        def removed():
            aug.set_removed()

        import_service = trigger_services.get_service(ImportService.NAME)
        if import_service.register_post_import_notification(aug.aug_id, self.module_name, self.filename, callback, removed):
            aug.set_pending()

    def test_hash(self, module):
        # Don't test if we don't have a hash
        if not self.file_hash:
            return

        filepath = inspect.getsourcefile(module)
        if not filepath:
            raise RookHashFailedException(module.__name__)

        with open(filepath, 'rb') as f:
            if six.PY2:
                string = f.read().replace('\r\n', '\n').replace('\r\x00\n\x00', '\n\x00').replace('\r', '\n')
            else:
                string = f.read().decode().replace('\r\n', '\n').replace('\r\x00\n\x00', '\n\x00').\
                    replace('\r', '\n').encode('UTF8')

        hash = hashlib.sha256(string).hexdigest()
        if hash != self.file_hash:
            raise RookHashMismatchException(filepath, self.file_hash, hash)
