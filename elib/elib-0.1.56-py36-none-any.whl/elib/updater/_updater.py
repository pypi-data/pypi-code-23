# coding=utf-8
"""
Manage in-place executable updates
"""
import subprocess
import sys
import typing
from pathlib import Path

from packaging import version

from ..custom_logging import get_logger
from ._github import Release, get_latest_release

LOGGER = get_logger('ELIB')


class Updater:
    """
    Manage in-place executable updates
    """

    def __init__(self, repo: str, current_version: str, local_executable: typing.Union[Path, str]):
        self._repo = repo
        self._current_version = current_version
        self._local_executable = Path(local_executable).absolute()
        self._latest_release: Release = None

    @staticmethod
    def _write_bat(local_executable: Path):
        LOGGER.debug('write bat file')
        update_bat = Path('update.bat').absolute()
        update_bat.write_text(f"""
    @echo off
    echo Updating to latest version...
    ping 127.0.0.1 -n 5 -w 1000 > NUL
    move /Y "update" "{local_executable.name}" > NUL
    echo restarting...
    start "" "{local_executable.name}"
    DEL update.vbs
    DEL "%~f0"
        """)

    @staticmethod
    def _write_vbs():
        LOGGER.debug('write vbs script')
        update_vbs = Path('update.vbs').absolute()
        # http://www.howtogeek.com/131597/can-i-run-a-windows-batch-file-without-a-visible-command-prompt/
        update_vbs.write_text('CreateObject("Wscript.Shell").Run """" & WScript.Arguments(0) & """", 0, False')

    def _install_latest_version(self):
        LOGGER.info(f'installing latest version')

        local_executable = Path(self._local_executable).absolute()
        LOGGER.debug(f'local executable: "{local_executable}"')

        self._write_bat(local_executable)
        self._write_vbs()

        LOGGER.debug('starting update batch file')
        args = ['wscript.exe', 'update.vbs', 'update.bat']
        subprocess.Popen(args)

        sys.exit(0)

    def _download_latest_release(self) -> bool:
        LOGGER.debug('downloading latest release')
        for asset in self._latest_release.assets:
            if asset.name.endswith('.exe'):
                LOGGER.debug(f'executable asset found: {asset.name}')
                return asset.download('update')

        LOGGER.error('no executable asset found')
        return False

    def update(self):
        """
        Updates this application in place
        """
        self._latest_release = get_latest_release(self._repo)
        if not self._latest_release:
            LOGGER.error('unable to obtain a release from Github')
            return
        LOGGER.debug(f'latest release: {self._latest_release}')
        latest_version = version.parse(self._latest_release.tag_name)
        LOGGER.debug(f'latest version: {latest_version}')
        current_version = version.parse(self._current_version)
        LOGGER.debug(f'current version: {current_version}')
        if latest_version > current_version:
            LOGGER.info('new version found')
            if self._download_latest_release():
                self._install_latest_version()
        else:
            LOGGER.debug('already up-to-date')
