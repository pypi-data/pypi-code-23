from django.test import TestCase
from ark.models import Lock
from ark.locks import DbLock, LockOffError, LockOnError
from ark.transactions import TX, TxBroadcaster

class LockTestCase(TestCase):

    def setUp(self):
        lock = Lock.objects.create(name="A")
        lock.save()

    def test_pre_created_lock(self):
        """Test locking behaviour of precreated lock"""
        lock = DbLock(name="A")

        lock.release(hard=True)

        # test if concurrent process is stopped
        lock.set()

        self.assertRaises(LockOnError, lock.set)

        # check if incorrect releasing of locks raises errors
        lock.release()

        self.assertRaises(LockOffError, lock.release)

    def test_auto_lock_creation(self):
        lock = DbLock("B")
        lock.set()
        self.assertRaises(LockOnError, lock.set)


class TxTestCase(TestCase):
    def test_single_tx(self):
        tx = TX(
            amount=1,
            secret="talk coral spatial wall pipe wolf orient attack soft favorite ordinary buzz",
            recipient="DA1SPukujJqfVqiGfq9yFUnnEucpxevgbA",
            network="dark",
        )

        tx.send(use_open_peers=True)
        self.assertNotEqual(tx.tx.res["success"], '0,0%')


class TxBroadCasterTestCase(TestCase):
    def setUp(self):
        """
        We bake some transactions and store them in the db.
        """
        for i in range(10):
            tx = TX(
                amount=i+1,
                secret="talk coral spatial wall pipe wolf orient attack soft favorite ordinary buzz",
                recipient="DA1SPukujJqfVqiGfq9yFUnnEucpxevgbA",
                network="dark",
            )

            tx.queue()

    def test_broadcaster(self):
        caster = TxBroadcaster(uid=0, singlerun=True)
        caster.run()



