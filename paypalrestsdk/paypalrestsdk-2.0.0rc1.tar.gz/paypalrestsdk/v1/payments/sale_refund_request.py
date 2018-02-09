# This class was generated on Mon, 29 Jan 2018 15:08:25 PST by version 0.1.0-dev+6beb51-dirty of Braintree SDK Generator
# sale_refund_request.py
# @version 0.1.0-dev+6beb51-dirty
# @type request
# @data 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
# DO NOT EDIT
import braintreehttp

try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

class SaleRefundRequest:
    """
    Refunds a sale, by ID. For a full refund, include an empty payload in the JSON request body. For a partial refund, include an `amount` object in the JSON request body.
    """
    def __init__(self, sale_id):
        self.verb = "POST"
        self.path = "/v1/payments/sale/{sale_id}/refund?".replace("{sale_id}", quote(str(sale_id)))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = None

    
    
    def request_body(self, refund_request):
        self.body = refund_request
        return self
