import sys
import traceback
import time
import threading
import six
import os
import inspect

from six.moves import builtins
from six import iteritems, raise_from

from rook.lib.logger import logger

from rook.interfaces.config import ImportServiceConfig


class ImportService(object):

    NAME = "Import"

    class Notification(object):
        def __init__(self, module_name, module_filename, callback, removed):
            self.module_name = module_name
            self.module_filename = module_filename
            self.callback = callback
            self.removed = removed

    def __init__(self, bdb_location_service):
        self._bdb_location_service = bdb_location_service

        self._modules = dict(sys.modules)
        self._post_import_notifications = {}
        self._lock = threading.RLock()

        self._thread = None
        self._quit = False

        self._old_import = None

        if ImportServiceConfig.USE_IMPORT_HOOK:
            self._old_import = builtins.__import__
            builtins.__import__ = self._my_import
        else:
            self._thread = threading.Thread(target=self._query_thread,
                                            name=ImportServiceConfig.THREAD_NAME)
            self._thread.daemon = True
            self._thread.start()

    def close(self):
        if self._old_import:
            builtins.__import__ = self._old_import

        if self._thread:
            self._quit = True

            # If threading was monkey patched by gevent waiting on thread will likely throw an exception
            try:
                from gevent.monkey import is_module_patched
                if is_module_patched("threading"):
                    time.sleep(ImportServiceConfig.SYS_MODULES_QUERY_INTERVAL)
            except:
                pass

            self._thread.join()

    def register_post_import_notification(self, aug_id, name, filename, callback, removed):
        # Normalize file path
        if filename:
            filename = os.path.normcase(os.path.normpath(filename))

        notification = self.Notification(name, filename, callback, removed)

        with self._lock:
            # Attempt to satisfy notification using known modules
            for module_name, module_object in six.iteritems(self._modules):

                # If module is not valid, ignore
                if not self._is_valid_module(module_object):
                    continue

                # Get module details and check if it matches
                module_filename = self._get_module_path(module_object)
                if module_filename:
                    if self._does_module_match_notification(module_name, module_filename, notification):
                        notification.callback(module_object)
                        return False

            # Register notification for future loads
            self._post_import_notifications[aug_id] = notification

        return True

    def remove_aug(self, aug_id):
        with self._lock:
            try:
                notification = self._post_import_notifications[aug_id]
            except KeyError:
                return

            notification.removed()
            del self._post_import_notifications[aug_id]

    def clear_augs(self):
        with self._lock:
            for aug_id in list(self._post_import_notifications.keys()):
                self.remove_aug(aug_id)

            self._post_import_notifications.clear()

    def _is_valid_module(self, module_object):
        return module_object and inspect.ismodule(module_object) and hasattr(module_object, '__file__')

    def _my_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        # Call original function
        result = self._old_import(name, globals, locals, fromlist, level)

        self._evaluate_module_list()

        # Return original result
        return result

    def _query_thread(self):
        self._bdb_location_service.ignore_current_thread()

        while not self._quit:
            try:
                self._evaluate_module_list()
            except:
                if logger:
                    logger.exception("Error while evaluating module list")

            # time can be None if interpreter is in shutdown
            if not time:
                return
            time.sleep(ImportServiceConfig.SYS_MODULES_QUERY_INTERVAL)

    def _evaluate_module_list(self):
        try:
            # Nobody is waiting for notifications
            if not self._post_import_notifications:
                return

            # No new modules
            if len(self._modules) == len(sys.modules):
                return

            with self._lock:

                # Get a fresh list
                modules = dict(sys.modules)

                # For everybody not in the old list, check notifications
                for name, module in six.iteritems(modules):
                    if name not in self._modules and self._is_valid_module(module):
                        self._notify_of_new_module(name, module)

                # Update the "old" list
                self._modules = modules

        except:
            logger.exception("Exception in ImportService")

    def _notify_of_new_module(self, module_name, module_object):
        augs_to_remove = set()

        module_filename = self._get_module_path(module_object)
        if module_filename:
            for aug_id, notification in six.iteritems(self._post_import_notifications):
                if self._does_module_match_notification(module_name, module_filename, notification):
                    augs_to_remove.add(aug_id)
                    try:
                        notification.callback(module_object)
                    except:
                        logger.exception("Error on module load callback")

        for aug_id in augs_to_remove:
            del self._post_import_notifications[aug_id]


    @staticmethod
    def _get_module_path(module):
        path = inspect.getsourcefile(module)
        if path:
            return os.path.normcase(os.path.abspath(path))
        else:
            return None

    @staticmethod
    def _does_module_match_notification(module_name, module_filename, notification):
        if notification.module_filename and ImportService.path_contains_path(module_filename, notification.module_filename) or \
                        notification.module_name and module_name == notification.module_name:
            return True
        else:
            return False

    @staticmethod
    def path_contains_path(full_path, partial_path):
        if full_path.endswith(partial_path):
            return len(full_path) == len(partial_path) or full_path[-len(partial_path)-1] in ('/', '\\')
        else:
            return False
