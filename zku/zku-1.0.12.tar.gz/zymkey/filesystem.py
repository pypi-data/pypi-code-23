import json
import os
import sh
import shlex

from . import vault

from .exceptions import CommandError
from .utils import Map, get_random


class Filesystem(object):
    """
    An encrypted filesystem object
    """
    def __init__(self, base, name):
        self.base = base
        self.name = name

        self.config = FilesystemConfig(self)

        self._secret_key = None

    @property
    def root(self):
        """
        Returns (str): full path to the filesystem's base directory
        """
        return os.path.join(self.base, self.name)

    @property
    def loopback_path(self):
        return os.path.join(self.root, 'fs')

    @property
    def key_path(self):
        return os.path.join(self.root, 'key')

    @property
    def mapper_path(self):
        return '/dev/mapper/{}'.format(self.name)

    @property
    def secret_key(self):
        if self._secret_key:
            return self._secret_key

        self._secret_key = vault.unlock(self.key_path).decode('utf8')

        return self._secret_key

    def create(self, mountpoint, size, automount=True):
        """
        creates a new encrypted filesystem

        Args:
            mountpoint (str): path to mount the filesystem
            size (int): filesystem size in MB
            automount (bool): whether to mount at boot
        """
        if os.path.exists(self.root):
            raise CommandError('filesystem {} already exists'.format(self.name))

        if not os.path.exists(self.root):
            os.makedirs(self.root)

        self._secret_key = get_random()

        # print('secret_key={}'.format(secret_key))

        vault.lock(self.key_path, self.secret_key)

        dd_command = shlex.split('dd if=/dev/zero of={} bs=1M seek={} count=1'.format(self.loopback_path, size-1))
        dd = sh.Command(dd_command[0])
        dd(*dd_command[1:])

        luks_format_command = shlex.split('cryptsetup -q -v luksFormat {} -'.format(self.loopback_path))
        command = sh.Command(luks_format_command[0])
        command(*luks_format_command[1:], _in=self.secret_key)

        self.unlock()

        mkfs = sh.Command("mkfs.ext4")
        mkfs(self.mapper_path)

        self.lock()

        self.config.write(mountpoint, automount)

        self.enable_service()

    def enable_service(self):
        systemctl_command = shlex.split('systemctl enable zymkey-filesystem@{}'.format(self.name))

        command = sh.Command(systemctl_command[0])
        command(*systemctl_command[1:])

    def mount(self, automount=True):
        """
        Mounts the filesystem

        Args:
            automount (bool): when True, check the filesystem's config for automount to be True
        """
        # when automount=True and the config's automount is False, do nothing
        if automount and not self.config.automount:
            return

        self.unlock()

        mountpoint = self.config.mountpoint
        if not os.path.exists(mountpoint):
            os.makedirs(mountpoint)

        mount_command = shlex.split('mount {} {}'.format(self.mapper_path, mountpoint))

        command = sh.Command(mount_command[0])
        command(*mount_command[1:])

    def unmount(self):
        unmount_command = shlex.split('umount {}'.format(self.config.mountpoint))

        command = sh.Command(unmount_command[0])

        # try to unmount, but continue if error
        # error 32 is raised when the filesystem is not mounted
        try:
            command(*unmount_command[1:])
        except sh.ErrorReturnCode_32:
            pass

        try:
            self.lock()
        except sh.ErrorReturnCode_4:
            pass

    def lock(self):
        luks_close_command = shlex.split('cryptsetup luksClose {}'.format(self.name))

        command = sh.Command(luks_close_command[0])
        command(*luks_close_command[1:])

    def unlock(self):
        luks_open_command = shlex.split('cryptsetup luksOpen {} {} -'.format(self.loopback_path, self.name))

        command = sh.Command(luks_open_command[0])
        command(*luks_open_command[1:], _in=self.secret_key)


class FilesystemConfig(Map):
    def __init__(self, filesystem):
        super(FilesystemConfig, self).__init__()

        self.filesystem = filesystem

        self.check_config()

    @property
    def config_path(self):
        return os.path.join(self.filesystem.root, 'config.json')

    def check_config(self):
        """
        checks to see if a configuration file exists

        when a configuration file is found, read its contents

        Returns (dict): the configuration file contents
        """
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as fh:
                data = json.load(fh)
                self.update(data)

    def write(self, mountpoint, automount):
        self.mountpoint = mountpoint
        self.automount = automount

        # do not attempt to serialize the filesystem attribute
        data = self.copy()
        data.pop('filesystem')

        with open(self.config_path, 'w') as fh:
            json.dump(data, fh)
