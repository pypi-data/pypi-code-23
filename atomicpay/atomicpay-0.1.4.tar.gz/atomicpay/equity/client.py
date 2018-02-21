# Copyright (c) 2017 Turbopay Holdings Ltd

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

from atomicpay import utils
from atomicpay.equity import api, exceptions, routes
from atomicpay.equity.auth import Auth


class Equity(object):
    """Equity Client
    Attributes:
        consumer_key: A string Consumer Key
        consumer_secret: A string Consumer Secret
        username: App Username
        passwd: App password
        live: A boolean indicating if sandbox or production(live)
    """

    def __init__(self, key, secret, username, passwd, live=False):
        self.live = live
        self.auth = Auth(key, secret, username, passwd, live)

    def remit(self, destination, transfer, name, reference, **kwargs):

        callback = kwargs.pop('callback', None)

        EXPECTED_TO_KEYS = {
            "accountNumber",
            "bicCode",
            "mobileNumber",
            "walletName",
            "bankCode",
            "branchCode"
        }

        EXPECTED_FROM_KEYS = {
            "countryCode",
            "currencyCode",
            "amount",
            "paymentType",
            "paymentReferences",
            "remarks"
        }

        data = {
            "transactionReference": reference,
            "source": {
                "senderName": name
            },
            "destination": utils.ensure_exact_keys(destination, EXPECTED_TO_KEYS),
            "transfer": utils.ensure_exact_keys(transfer, EXPECTED_FROM_KEYS)
        }

        return api.call(
            route=routes.REMITTANCE,
            data=data,
            access_token=self.auth.access_token,
            live=self.live,
            callback=callback
        )

    def airtime(self, phone, amount, telco, reference, **kwargs):

        callback = kwargs.pop('callback', None)

        data = {
            "customer": {
                "mobileNumber": phone
            },
            "airtime": {
                "amount": amount,
                "reference": reference,
                "telco": telco
            }
        }

        return api.call(
            route=routes.AIRTIME,
            data=data,
            access_token=self.auth.access_token,
            live=self.live,
            callback=callback
        )

    def create_payment(self, phone, amount, type, desc, reference, **kwargs):

        callback = kwargs.pop('callback', None)

        data = {
            "customer": {
                "mobileNumber": phone
            },
            "transaction": {
                "amount": amount,
                "description": desc,
                "type": type,
                "auditNumber": reference
            }
        }

        return api.call(
            route=routes.CREATEPAYMENT,
            data=data,
            access_token=self.auth.access_token,
            live=self.live,
            callback=callback
        )

    def payment_status(self, transaction_id, **kwargs):

        callback = kwargs.pop('callback', None)

        return api.call(
            route=routes.PAYMENTSTATUS.format(id=transaction_id),
            access_token=self.auth.access_token,
            live=self.live,
            method='get',
            callback=callback
        )

    def change_password(self, id, current_passord, new_password, **kwargs):

        callback = kwargs.pop('callback', None)

        data = {
            "currentPassword": current_passord,
            "newPassword": new_password
        }

        return api.call(
            route=routes.CHANGEPASSWORD.format(id=id),
            data=data,
            access_token=self.auth.access_token,
            live=self.live,
            callback=callback
        )
