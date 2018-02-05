import time
from decimal import Decimal, InvalidOperation
from functable import FunctionTable
from zcli.acctab import AccumulatorTable


MINCONF = 6
COMMANDS = FunctionTable()


class BaseCommand (object):
    @staticmethod
    def add_arg_parser(p):
        return

    @staticmethod
    def post_process_args(opts, usage_error):
        return opts


@COMMANDS.register
class list_balances (BaseCommand):
    """List all known address balances."""

    @staticmethod
    def run(zc):
        balances = AccumulatorTable()

        # Gather t-addr balances:
        for utxo in zc.listunspent():
            if utxo['spendable'] is True:
                balances[utxo['address']] += utxo['amount']

        # Gather t-addr balances:
        for zaddr in zc.z_listaddresses():
            balances[zaddr] = Decimal(zc.z_getbalance(zaddr.encode('utf8')))

        return {
            'total': sum(balances.values()),
            'addresses': dict(
                (k, v)
                for (k, v)
                in balances.iteritems()
                if v > 0
            ),
        }


@COMMANDS.register
class send (BaseCommand):
    """Send from an address to multiple recipients."""

    @staticmethod
    def add_arg_parser(p):
        p.add_argument(
            'SOURCE',
            help='Source address.',
        )

        p.add_argument(
            'DESTINFO',
            nargs='+',
            help='''
                Destination arguments in repeating sequence of: ADDR
                AMOUNT [MEMO]. A MEMO must begin with either "0x" for hex
                encoding or ":" for a simple string. A MEMO must not be
                present if ADDR is not a Z Address (beginning with "zc").
            ''',
        )

    @staticmethod
    def post_process_args(opts, usage_error):
        entries = []

        entry = {}
        for di in opts.DESTINFO:
            if len(entry) == 0:
                entry['address'] = di

            elif len(entry) == 1:
                try:
                    entry['amount'] = Decimal(di)
                except InvalidOperation as e:
                    usage_error(
                        ('Could not parse amount; {}')
                        .format(e)
                    )

            elif len(entry) == 2:
                hasmemo = False

                if di.startswith('0x') or di.startswith(':'):
                    hasmemo = True

                    # It's a memo field:
                    addr = entry['address']
                    if addr.startswith('zc'):
                        if di.startswith('0x'):
                            # Hex encoding:
                            memohex = di[2:]
                            try:
                                memohex.decode('hex')
                            except TypeError as e:
                                usage_error(
                                    ('Could not decode MEMO from 0x '
                                     'hexadecimal format: {}')
                                    .format(e)
                                )
                        elif di.startswith(':'):
                            memohex = di[1:].encode('hex')
                        else:
                            assert False, 'Unreachable code.'

                        entry['memo'] = memohex
                    else:
                        usage_error(
                            ('Destination address {!r} is not a Z Address '
                             'and cannot receive a memo: {!r}')
                            .format(addr, di)
                        )

                entries.append(entry)
                entry = {}

                if not hasmemo:
                    entry["address"] = di

            else:
                assert False, 'Unreachable code.'

        if len(entry) == 0:
            pass
        elif len(entry) == 1:
            usage_error(
                'No amount specified for final entry: {!r}'.format(entry)
            )
        elif len(entry) == 2:
            entries.append(entry)
        else:
            assert False, 'Unreachable code.'

        opts.DESTINFO = entries
        return opts

    @staticmethod
    def run(zc, SOURCE, DESTINFO):
        opid = zc.z_sendmany(SOURCE, DESTINFO)
        wait.run(zc, OPID=[opid])


@COMMANDS.register
class wait (BaseCommand):
    """Wait until all operations complete and have MINCONF confirmations."""

    @staticmethod
    def add_arg_parser(p):
        p.add_argument(
            'OPID',
            nargs='+',
            help='Operation id.',
        )

    @staticmethod
    def run(zc, OPID):
        opids = set(OPID)

        txids = []

        somefailed = False
        while len(opids) > 0:
            print 'Waiting for completions:'
            completes = []
            for opinfo in zc.z_getoperationstatus(list(opids)):
                opid = opinfo['id']
                status = opinfo['status']
                print '  {} - {}'.format(opid, status)

                if status not in {'queued', 'executing'}:
                    opids.remove(opid)
                    completes.append(opid)

            for opinfo in zc.z_getoperationresult(completes):
                if opinfo['status'] == 'success':
                    opid = opinfo['id']
                    txid = opinfo['result']['txid'].encode('utf8')
                    txids.append((opid, txid))
                else:
                    somefailed = True
                    print 'FAILED OPERATION: {!r}'.format(opinfo)

            print
            if len(opids) > 0:
                time.sleep(13)

        while txids:
            print 'Waiting for confirmations:'
            newtxids = []
            for (opid, txid) in txids:
                txinfo = zc.gettransaction(txid, True)
                confs = txinfo['confirmations']
                print '  {} - txid: {} - confirmations: {}'.format(
                    opid,
                    txid,
                    confs,
                )
                if confs < 0:
                    print 'FAILED TO CONFIRM: {!r}'.format(txinfo)
                elif confs < MINCONF:
                    newtxids.append((opid, txid))
            txids = newtxids

            print
            if len(txids) > 0:
                time.sleep(131)

        return not somefailed
