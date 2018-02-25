from ark.models import Lock
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
import time
"""
Atomic locks to ensure only a single instance of a process is running.
"""


class LockOnError(Exception):
    pass


class LockOffError(Exception):
    pass


class DbLock:
    def __init__(self, name):
        self.name = name

    @transaction.atomic
    def set(self, hard=False):
        try:
            lock = Lock.objects.select_for_update().filter(name=self.name, locked=False).update(locked=True)
            if not lock:
                try:
                    Lock.objects.select_for_update().create(name=self.name, locked=True)
                except IntegrityError:
                    if hard:
                        pass
                    raise LockOnError("Lock {} was on while trying to turn it on")

        except ObjectDoesNotExist:
            Lock.objects.select_for_update().create(name=self.name, locked=False).update(locked=True)

    @transaction.atomic
    def release(self, hard=False):
        lock = Lock.objects.select_for_update().filter(name=self.name, locked=True).update(locked=False)
        if not lock and not hard:
            raise LockOffError("Lock {} was off while trying to turn it off".format(self.name))

    def state(self):
        try:
            lock = Lock.objects.get(name=self.name).locked
            return lock.locked
        except ObjectDoesNotExist:
            lock = Lock.objects.select_for_update().create(name=self.name, locked=False)
            return lock.locked

    def delete(self):
        """
        remove the lock from the db
        """
        try:
            Lock.objects.get(name=self.name).delete()
            return True
        except ObjectDoesNotExist:
            return False



"""
some very useful functions for cleaner code
"""


def lock_and_log(logger, uid, raise_error=True, sleep=0):
    """
    decorator to create a unique lock for a function, log the function and release the lock if an exception occurs.
    if raise_error is set to false, it will simple exit the function (handy for if you don't want to log)
    if sleep is set, it will sleep for x seconds before releasing the lock
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            lock_name = func.__name__ + __name__ + uid
            lock = DbLock(lock_name)
            lock.set()
            try:
                res = func(*args, **kwargs)
                time.sleep(sleep)
                lock.delete()
                return res
            except Exception:
                time.sleep(sleep)
                lock.delete()
                logger.exception('error in {}'.format(func.__name__))
                return None
        return wrapper
    return decorator
