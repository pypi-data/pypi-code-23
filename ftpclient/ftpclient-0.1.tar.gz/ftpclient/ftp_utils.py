__all__ = ["FtpUtils"]


class FtpUtils:
    @staticmethod
    def formurl(user, password, host, port, remote_dir):
        slash = '/'
        if remote_dir.startswith('/'):
            slash = ''
        return 'ftp://{0}:{1}@{2}:{3}{4}{5}'.format(user, password, host, port, slash, remote_dir)
