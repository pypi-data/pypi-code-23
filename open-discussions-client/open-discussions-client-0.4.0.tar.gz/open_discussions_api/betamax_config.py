"""Configuration for betamax"""
import json

from betamax import Betamax
from betamax.util import deserialize_prepared_request
from betamax.matchers.body import BodyMatcher
from betamax_serializers.pretty_json import PrettyJSONSerializer


def _parse_request_body(request):
    """Parse the JSON from the request body, or return its bytes"""
    body = request.body
    if not body:
        return b''

    if request.headers.get("Content-Type") == "application/json":
        if isinstance(body, bytes):
            return json.loads(body.decode())
        return json.loads(body)

    if isinstance(body, str):
        return body.encode()
    return body


class CustomBodyMatcher(BodyMatcher):
    """Override BodyMatcher to convert str to bytes and compare JSON if applicable"""

    name = 'custom-body'

    def match(self, request, recorded_request):
        recorded_request = deserialize_prepared_request(recorded_request)

        request_body = _parse_request_body(request)
        recorded_body = _parse_request_body(recorded_request)

        return recorded_body == request_body


def setup_betamax():
    """Do global configuration for betamax. This function is idempotent."""
    Betamax.register_request_matcher(CustomBodyMatcher)
    Betamax.register_serializer(PrettyJSONSerializer)

    config = Betamax.configure()
    config.cassette_library_dir = "cassettes"
    config.default_cassette_options['match_requests_on'] = ['uri', 'method', 'custom-body']
    config.default_cassette_options['serialize_with'] = 'prettyjson'
