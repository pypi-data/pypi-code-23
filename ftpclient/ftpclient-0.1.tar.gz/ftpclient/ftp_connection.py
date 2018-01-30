import operator
import ftplib

# from ftpclient.ftp_item import FtpItem
# from ftpclient.ftp_item_type import FtpItemType
from ftpclient import *

__all__ = ["FtpConnection"]


class FtpConnection:
    def __init__(self, host, port, user, password, logger):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.logger = logger

    def __enter__(self):
        self.site = ftplib.FTP()

        self.logger.info('Connecting to %s:%s...', self.host, self.port)
        self.site.connect(self.host, self.port)
        self.logger.info('Connection established')

        self.site.login(self.user, self.password)
        self.logger.info('Logged in')

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.site.quit()
        self.logger.info('Disconnected from server')

    def walk(self, remote_dir='.', recursively=False):
        try:
            self.logger.info('CWD %s', remote_dir)
            self.site.cwd(remote_dir)

            items = []
            current_dir = self.site.pwd()

            self.logger.info('Retrieving directory listing of "%s"...', current_dir)
            self.site.retrlines('MLSD', lambda line: items.append(FtpItem(line, current_dir)))

            items.sort(key=operator.attrgetter('type', 'name'))

            for item in items:
                if item.type in (FtpItemType.cdir, FtpItemType.pdir):
                    continue
                yield item
                if recursively and item.type == FtpItemType.dir \
                        and item.type not in (FtpItemType.cdir, FtpItemType.pdir):
                    yield from self.walk(item.full_path, recursively)
        except ftplib.error_perm as response:
            self.logger.warning(response)
