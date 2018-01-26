import threading
from commonconf import settings
"""
This is a wrapper around threading.Thread, but it will only actually thread
if django configuration is enabled.  Otherwise, it will be an object with the
same api where start just calls run and.
"""


class Thread(threading.Thread):
    _use_thread = False
    parent = None

    def __init__(self, *args, **kwargs):
        # Threading has been tested w/ the mysql backend.
        # It should also work with the postgres/oracle/and so on backends,
        # but we don't use those.
        self.parent = threading.currentThread()

        if is_django_mysql():
            if hasattr(settings, "RESTCLIENTS_DISABLE_THREADING"):
                if not settings.RESTCLIENTS_DISABLE_THREADING:
                    self._use_thread = True
            else:
                self._use_thread = True

        elif hasattr(settings, "RESTCLIENTS_USE_THREADING"):
            if settings.RESTCLIENTS_USE_THREADING:
                self._use_thread = True

        super(Thread, self).__init__(*args, **kwargs)

    def start(self):
        if self._use_thread:
            super(Thread, self).start()

        else:
            # Needed to test failures in the threads.
            # But it can't be on all the time - sqlite dbs aren't shared to
            # threads.
            if hasattr(settings, "RESTCLIENTS_USE_INLINE_THREADS"):
                super(Thread, self).start()
                super(Thread, self).join()
            else:
                self.run()

    def join(self):
        if self._use_thread:
            return super(Thread, self).join()

        return True


def is_django_mysql():
    db = getattr(settings, 'DATABASES', None)

    if isinstance(db, dict):
        engine = db.get('default', {}).get('ENGINE', '')
        return engine == 'django.db.backends.mysql'

    return False


class GenericPrefetchThread(Thread):
    method = None

    def run(self):
        if self.method is None:
            return
        try:
            self.method()
        except Exception as ex:
            # Errors in prefetching should also manifest during actual
            # processing, where they can be handled appropriately
            pass


def generic_prefetch(method, args):
    def ret():
        return method(*args)
    return ret
