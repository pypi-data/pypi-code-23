from rest_framework.parsers import BaseParser
import json


class PlainTextParser(BaseParser):
    """
    Plain text parser. We need this for <= IE 10 where we need to use XDR and are unable to set content-type headers
    """
    media_type = 'text/plain'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        :raises: ValueError if the content of the body has no json decodable content
        """
        content = stream.read()
        return json.loads(content)
