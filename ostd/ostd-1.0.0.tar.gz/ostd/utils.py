import base64
import zlib

import chardet


def decompress(data):
    return zlib.decompress(base64.b64decode(data), 16 + zlib.MAX_WBITS)


def sublists_of(l, max_size: int):
    all_sublists = []

    sublist = []

    for e in l:
        sublist.append(e)

        if len(sublist) >= max_size:
            all_sublists.append(sublist)
            sublist = []

    if len(sublist) > 0:
        all_sublists.append(sublist)

    return all_sublists


def assert_status(response):
    if not response.get('status').startswith('200'):
        raise NotOKException(response)


class NotOKException(Exception):
    def __init__(self, response):
        super(NotOKException, self).__init__('Response was not OK: {}'.format(response))
        self.response = response


class Result:
    """
    Contains the downloaded subtitles. The content is lazily decoded.
    """

    def __init__(self, subtitle_id, raw):
        self.subtitle_id = subtitle_id
        self.raw = raw
        self._content = None

    @property
    def content(self):
        if not self._content:
            charset_analysis = chardet.detect(self.raw)
            encoding = charset_analysis['encoding']
            self._content = self.raw.decode(encoding, 'replace')
        return self._content
