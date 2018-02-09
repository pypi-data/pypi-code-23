# This class was generated on Mon, 29 Jan 2018 15:08:25 PST by version 0.1.0-dev+6beb51-dirty of Braintree SDK Generator
# refund_get_request.py
# @version 0.1.0-dev+6beb51-dirty
# @type request
# @data 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
# DO NOT EDIT
import braintreehttp

try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

class RefundGetRequest:
    """
    Shows details for a refund, by ID.
    """
    def __init__(self, refund_id):
        self.verb = "GET"
        self.path = "/v1/payments/refund/{refund_id}?".replace("{refund_id}", quote(str(refund_id)))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = None

    
