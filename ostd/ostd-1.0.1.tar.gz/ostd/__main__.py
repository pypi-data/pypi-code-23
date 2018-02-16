import sys

from ostd import Downloader, NotOKException

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
