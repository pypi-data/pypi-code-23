import arky.rest
from ark.models import Transaction
import random
from django.db.models import ObjectDoesNotExist
import time
from ark.locks import DbLock

class TX:
    '''
    Get transaction from DB or bake a single transaction, and add to the transaction db
    '''
    def __init__(self, **kw):

        self.network = kw.get('network', 'dark')
        try:
            if not arky.core:
                # first time this check fails with an AttributeError, thus we initialize arky.core
                pass
        except AttributeError:
            arky.rest.use(self.network)
        # try to bake the tx ourselves if sufficient kw is supplied
        # if no variables for baking a transaction are supplied, we try to retrieve it from the DB
        try:
            self.tx = Transaction.objects.get(tx_id=kw.get('tx_id'))
        except ObjectDoesNotExist:
            trs = arky.core.crypto.bakeTransaction(
                recipientId=kw.get('recipient', None),
                amount=kw.get('amount'),
                vendorfield=kw.get('smartbridge'),
                secret=kw.get('secret'),
                secondSecret=kw.get('secondsecret', None),
            )

            self.tx = Transaction.objects.create(
                tx=trs,
                tx_id=arky.core.crypto.getId(trs),
                confirmations=0,
                desc=kw.get('desc', None),
                network=self.network
            )

    def send(self, use_open_peers=True, **kw):
        """
        send a transaction immediately. Failed transactions are picked up by the TxBroadcaster

        :param ip: specific peer IP to send tx to
        :param port: port of specific peer
        :param use_open_peers: use Arky's broadcast method
        """

        if not use_open_peers:
            ip = kw.get('ip')
            port = kw.get('port')
            peer = 'http://{}:{}'.format(ip, port)
            res = arky.rest.POST.peer.transactions(peer=peer, transactions=[self.tx.tx])

        else:
            res = arky.core.sendPayload(self.tx.tx)

        if self.tx.success != '0.0%':
            self.tx.error = None
            self.tx.success = True
        else:
            self.tx.error = res['messages']
            self.tx.success = False

        self.tx.tries += 1
        self.tx.res = res
        self.__save()

        print(res)
        return res

    def confirmations(self):
        res = arky.rest.GET.api.transactions.get(id=self.tx.tx_id)

        if res.get('error', None) == 'Transaction not found':
            self.tx.confirmations = 0
        elif 'ReadTimeout' in res.get('error', ''):
            self.confirmations()
        else:
            self.tx.confirmations = res.get('transaction').get('confirmations')
        self.__save()
        return self.tx.confirmations

    def check_confirmations_or_resend(self, use_open_peers=False, **kw):
        """
        check if a tx is confirmed, else resend it.

        :param use_open_peers: select random peers fro api/peers endpoint
        """
        if self.confirmations() == 0:
            self.send(use_open_peers, **kw)

    def queue(self):
        """
        queue a transaction to be picked up by the background transaction broadcaster
        """
        self.tx.send = True
        self.__save()

    def delay(self):
        """
        save a transaction, but don't let it be picked up by the broadcaster
        """
        self.tx.send = False
        self.__save()

    def __save(self):
        self.tx.save()


class TxBroadcaster:
    """
    Broadcasts transactions and rechecks if they have been sent until a specified amount of confirmations.
    """

    def __init__(self, **kw):
        self.max_retry = kw.get('max_retry', 10)
        self.min_confs = kw.get('check_until_confs', 51)
        self.use_open_peers = kw.get('use_open_peers', True)
        self.network = kw.get('network', 'dark')
        self.uid = kw.get('uid', 0)
        self.peers = kw.get('peers', None)
        self.wait = kw.get('wait_time', 30)
        self.caster = kw.get("broadcaster", 0)
        self.singlerun = kw.get("singlerun", False)
        arky.rest.use(self.network)

    def run(self):
        # we lock the run to ensure we don't get multiple instances of the same broadcaster sending out transactions
        lock = DbLock(name=self.uid)
        try:
            lock.set()
            while True:
                for x in Transaction.objects.all()\
                        .filter(confirmations__lte=self.min_confs)\
                        .filter(tries__lt=self.max_retry)\
                        .filter(send=True)\
                        .filter(broadcaster=self.caster):

                    tx = TX(tx_id=x.tx_id)

                    if self.peers:
                        peer = list(random.choice([self.peers.keys()]))[0]
                        port = self.peers.get(peer)
                    else:
                        peer = None,
                        port = None

                    tx.check_confirmations_or_resend(
                        use_open_peers=self.use_open_peers,
                        ip=peer,
                        port=port,
                )

                # lets give the network some time to incorporate our transactions before rebroadcasting again, while doing
                # so we reselect our peers
                if self.singlerun:
                    lock.release()
                    break

                arky.rest.use(self.network)
                time.sleep(self.wait)


        except Exception:
            lock.release()
            raise
