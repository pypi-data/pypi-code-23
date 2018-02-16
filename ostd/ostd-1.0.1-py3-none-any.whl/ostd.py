import sys
from xmlrpc.client import Transport, ServerProxy

from ostd.utils import *


class Downloader:
    """
    Connects to the OpenSubtitles server and allows for file downloading.
    """

    def __init__(self, user_agent, server='http://api.opensubtitles.org/xml-rpc', language='eng'):
        self.server = server
        self.language = language

        trans = Transport()
        trans.user_agent = user_agent

        self._rpc = ServerProxy(self.server, allow_none=True, transport=trans)
        login_response = self._rpc.LogIn('', '', language, user_agent)

        assert_status(login_response)

        self._token = login_response.get('token')

    def download(self, *ids):
        """
        Downloads the subtitles with the given ids.
        :param ids: The subtitles to download
        :return: Result instances
        :raises NotOKException
        """
        bundles = sublists_of(ids, 20)  # 20 files at once is an API restriction

        for bundle in bundles:
            download_response = self._rpc.DownloadSubtitles(self._token, bundle)

            assert_status(download_response)

            download_data = download_response.get('data')

            for item in download_data:
                subtitle_id = item['idsubtitlefile']
                subtitle_data = item['data']

                decompressed = decompress(subtitle_data)

                yield Result(subtitle_id, decompressed)

    def close(self):
        """
        Closes the connection.
        """
        self._rpc.LogOut(self._token)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {} <USER-AGENT> <SUBTITLE-ID>'.format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    USER_AGENT = sys.argv[1]
    SUBTITLES_ID = sys.argv[2]

    try:
        with Downloader(USER_AGENT) as downloader:
            result = next(downloader.download(SUBTITLES_ID))

            if sys.platform == "win32":
                import os
                import msvcrt

                msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

            sys.stdout.buffer.write(result.raw)
    except NotOKException as e:
        status = e.response.get('status')
        print('The download failed because the server response contained the following status: {}'.format(status),
              file=sys.stderr)
        sys.exit(1)
