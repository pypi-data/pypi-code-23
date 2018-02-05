from bitshares.instance import shared_bitshares_instance
from bitshares.asset import Asset
from bitshares.amount import Amount
from bitsharesbase.operations import Operation, Asset as LLAsset


class OperationsFee(list):
    """ Obtain the fee associated with an actual operation

        :param list operations: list of operations as dictionary
        :param bitshares.asset.Asset: Asset to pay fee in
        :param bitshares bitshares_instance: BitShares() instance to use when
            accesing a RPC
    """
    def __init__(self, opsOrg, asset="1.3.0", bitshares_instance=None):
        ops = opsOrg.copy()
        assert isinstance(ops, list)

        self.bitshares = bitshares_instance or shared_bitshares_instance()
        asset = Asset(
            asset,
            bitshares_instance=self.bitshares)

        if isinstance(ops[0], (object, dict)):
            ops = [Operation(i) for i in ops]

        fees = self.bitshares.rpc.get_required_fees([i.json() for i in ops], asset["id"])
        ret = []
        for i, d in enumerate(ops):
            if isinstance(fees[i], list):
                # Operation is a proposal
                ret.append([Amount(dict(
                    amount=fees[i][0]["amount"],
                    asset_id=fees[i][0]["asset_id"]),
                    bitshares_instance=self.bitshares
                )])
                for j, _ in enumerate(ops[i].op.data["proposed_ops"].data):
                    ret[-1].append(
                        Amount(dict(
                            amount=fees[i][1][j]["amount"],
                            asset_id=fees[i][1][j]["asset_id"]),
                            bitshares_instance=self.bitshares
                        ))
            else:
                # Operation is a regular operation
                ret.append(Amount(dict(
                    amount=fees[i]["amount"],
                    asset_id=fees[i]["asset_id"]),
                    bitshares_instance=self.bitshares
                ))
        list.__init__(self, ret)


class Fee(dict):
    """ Obtain fees associated with individual operations on the blockchain

        :param str identifier: Operation id or name
        :param bitshares bitshares_instance: BitShares() instance to use when
            accesing a RPC

    """
    pass
