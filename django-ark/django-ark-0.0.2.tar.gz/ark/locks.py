from ark.models import Lock
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
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
            print(lock)
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
            return Lock.objects.get(name=self.name).locked
        except ObjectDoesNotExist:
            lock = Lock.objects.select_for_update().create(name=self.name, locked=False)
            return lock.locked