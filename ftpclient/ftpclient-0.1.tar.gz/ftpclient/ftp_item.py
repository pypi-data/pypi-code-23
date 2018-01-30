import time
import os.path

# from ftpclient.ftp_item_type import FtpItemType
from ftpclient import *

__all__ = ["FtpItem"]


class FtpItem:
    def __init__(self, line, parent_path):
        data, _, self.name = line.partition('; ')
        fields = data.split(';')
        for field in fields:
            field_name, _, field_value = field.partition('=')
            if field_name == 'type':
                if field_value == 'dir':
                    self.type = FtpItemType.dir
                elif field_value == 'cdir':
                    self.type = FtpItemType.cdir
                elif field_value == 'pdir':
                    self.type = FtpItemType.pdir
                elif field_value == 'file':
                    self.type = FtpItemType.file
                else:
                    self.type = FtpItemType.unknown

            elif field_name in ('sizd', 'size'):
                self.size = int(field_value)
            elif field_name == 'modify':
                self.mtime = field_value
            elif field_name == 'perm':
                self.perm = field_value
            elif field_name == 'unique':
                self.unique = field_value
            elif field_name == 'UNIX.group':
                self.nix_group = field_value
            elif field_name == 'UNIX.mode':
                self.nix_mode = field_value
            elif field_name == 'UNIX.owner':
                self.nix_owner = field_value

        self.full_path = os.path.join(parent_path, self.name)

        def mtime_as_secs(self):
            return time.mktime(time.strptime(self.mtime, '%Y%m%d%H%M%S'))
