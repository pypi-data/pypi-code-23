# This class was generated on Mon, 29 Jan 2018 15:08:25 PST by version 0.1.0-dev+6beb51-dirty of Braintree SDK Generator
# order_capture_request.py
# @version 0.1.0-dev+6beb51-dirty
# @type request
# @data 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
# DO NOT EDIT
import braintreehttp

try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

class OrderCaptureRequest:
    """
    Captures a payment for an order, by ID. To use this call, the original payment call must specify an `order` intent. In the JSON request body, include the payment amount and indicate whether this capture is the final capture for the authorization.
    """
    def __init__(self, order_id):
        self.verb = "POST"
        self.path = "/v1/payments/orders/{order_id}/capture?".replace("{order_id}", quote(str(order_id)))
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = None

    
    
    def request_body(self, capture):
        self.body = capture
        return self
