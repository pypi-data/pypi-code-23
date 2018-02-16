import time
from typing import cast, List, Dict, Iterable, Optional

from iota import (  # noqa: F401
    Iota, ProposedTransaction, Address, Bundle, TransactionHash, Transaction
)

DEPTH = 3


class WalletException(Exception):
    pass


class BundleAlreadyPromoted(WalletException):
    pass


class _Account:
    def __init__(self,
                 addresses: List[Address],
                 balance: int,
                 bundles: List[Bundle]) -> None:
        self.addresses = addresses
        self.balance = balance

        confirmed_bundles = {
            bundle.hash: bundle for bundle in bundles if bundle.is_confirmed
        }

        duplicates = []  # type: List[Bundle]
        unconfirmed = {}  # type: Dict[TransactionHash, Bundle]

        for bundle in bundles:
            if bundle.is_confirmed:
                # Already got these
                pass
            else:
                if bundle.hash in confirmed_bundles:
                    duplicates.append(bundle)
                elif bundle.hash in unconfirmed:
                    # Check timestamps
                    unconfirmed_bundle = unconfirmed[bundle.hash]
                    bundle_timestamp = bundle.tail_transaction.attachment_timestamp
                    unconfirmed_timestamp = unconfirmed_bundle.tail_transaction.attachment_timestamp
                    if bundle_timestamp > unconfirmed_timestamp:
                        duplicates.append(unconfirmed_bundle)
                        unconfirmed[bundle.hash] = bundle
                    else:
                        duplicates.append(bundle)
                else:
                    unconfirmed[bundle.hash] = bundle

        self._confirmed_bundles = confirmed_bundles
        self.duplicate_bundles = duplicates
        self._unconfirmed_bundles = unconfirmed

    @property
    def confirmed_bundles(self) -> Iterable[Bundle]:
        return self._confirmed_bundles.values()

    @property
    def unconfirmed_bundles(self) -> Iterable[Bundle]:
        return self._unconfirmed_bundles.values()


class Wallet:
    """docstring for Wallet"""
    def __init__(self,
                 uri: str,
                 seed: Optional[str] = None) -> None:
        self._iota_api = Iota(uri, seed)
        self._account: _Account

    @property
    def account(self) -> _Account:
        try:
            return self._account
        except AttributeError:
            # We get an attibute error if we check this property before ever
            # calling refresh_account.
            self.refresh_account()
            return self._account

    @property
    def addresses(self) -> List[Address]:
        return self.account.addresses

    @property
    def balance(self) -> int:
        return self.account.balance

    @property
    def bundles(self) -> Dict[str, Iterable[Bundle]]:
        return {
            'confirmed': self.account.confirmed_bundles,
            'unconfirmed': self.account.unconfirmed_bundles,
            'duplicate': self.account.duplicate_bundles,
        }

    def _is_above_max_depth(self,
                            transaction: Transaction) -> bool:
        current_millis = time.time() * 1000
        max_age = 11 * 60 * 1000  # 11 minutes
        diff = current_millis - cast(float, transaction.attachment_timestamp)
        return (0 < diff < max_age)

    def _is_promotable(self,
                       bundle: Bundle) -> bool:
        return (
            self._is_above_max_depth(bundle.tail_transaction) and
            self._iota_api.helpers.is_promotable(bundle.tail_transaction.hash)
        )

    def _promote(self,
                 bundle: Bundle) -> Bundle:
        tail_hash = bundle.tail_transaction.hash
        response = self._iota_api.get_latest_inclusion([tail_hash])
        if response['states'][tail_hash]:
            raise BundleAlreadyPromoted()

        response = self._iota_api.promote_transaction(transaction=tail_hash, depth=DEPTH)
        return response['bundle']

    def _reattach(self,
                  bundle: Bundle) -> Bundle:
        response = self._iota_api.replay_bundle(
            bundle.tail_transaction.hash,
            DEPTH,
        )
        return Bundle.from_tryte_strings(response['trytes'])

    def create_new_address(self) -> Address:
        response = self._iota_api.get_new_addresses(count=None)
        address = response['addresses'][0]

        # Attach the address
        self._iota_api.send_transfer(
            depth=DEPTH,
            transfers=[ProposedTransaction(address, value=0)],
        )

        return address

    def refresh_account(self) -> None:
        response = self._iota_api.get_account_data(inclusion_states=True)
        addresses = response['addresses']
        balance = response['balance']
        bundles = response['bundles']

        self._account = _Account(addresses, balance, bundles)

    def retry_unconfirmed_bundles(self,
                                  *bundles: Bundle) -> None:
        if len(bundles) == 0:
            bundles = tuple(self.bundles['unconfirmed'])
        for bundle in bundles:
            print(f'Retrying bundle: {bundle.hash}')
            if not self._is_promotable(bundle):
                bundle = self._reattach(bundle)
                while True:
                    time.sleep(2)
                    if self._is_promotable(bundle):
                        break
            for attempt in range(5):
                try:
                    promote_bundle = self._promote(bundle)
                except BundleAlreadyPromoted:
                    break
                else:
                    print(f'Promotion attempt ({attempt}): Bundle {promote_bundle.hash}')

    def send(self,
             address: str,
             value: int) -> None:
        print(f'Sending {value} iota to {address}...')
        response = self._iota_api.send_transfer(
            depth=DEPTH,
            transfers=[ProposedTransaction(Address(address), value=value)]
        )
        bundle = response['bundle']
        print(f'Iota sent! Bundle hash: {bundle.hash}')
