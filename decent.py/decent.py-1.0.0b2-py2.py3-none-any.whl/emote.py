import requests
import sys

# static type checking, mainly for testing
# python versions <3.5 don't have this in the standard library,
# but they can be installed from pip. it's not a big deal if the
# user doesn't have `typing` - they just won't be able to run it
# through mypy.
try:
    from typing import Dict, Any, Text, Optional
    Json = Dict[Text, Any]
except ImportError:
    pass

if sys.version_info[0] < 3:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin

from .errors import DecentError


class Emote:
    def __init__(self,
                 server,         # type: Any
                 shortcode,      # type: str
                 image_url       # type: str
                ):
        # type: (...) -> None
        self.server = server
        self.shortcode = shortcode
        self.image_url = image_url


    @classmethod
    def from_json(cls, server, json):
        # type: (type, Any, Json) -> Emote
        shortcode = json["shortcode"]
        image_url = json["imageURL"]

        return cls(server, shortcode, image_url)


    @staticmethod
    def by_shortcode(server, shortcode):
        # type: (Any, str) -> Emote
        for emote in server.emotes:
            if emote.shortcode == shortcode:
                return emote
                break
        else:
            raise DecentError("Emote with shortcode {} not found".format(shortcode))
