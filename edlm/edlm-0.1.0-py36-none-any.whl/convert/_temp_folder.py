# coding=utf-8
"""
Manages temporary folder
"""

import shutil
import tempfile

import elib

from edlm import LOGGER

from ._context import Context


class TempDir:
    """
    Manages temporary folder
    """

    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.path = elib.path.ensure_dir(tempfile.mkdtemp(dir='.', prefix='__TMP')).absolute()

    def __enter__(self):
        LOGGER.debug(f'"{self.ctx.source_folder}": using temporary folder: "{self.path}"')
        self.ctx.temp_dir = self.path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            if self.ctx.keep_temp_dir:
                LOGGER.info(f'"{self.ctx.source_folder}": build successful, keeping temp dir: "{self.path}"')
            else:
                LOGGER.debug(f'"{self.ctx.source_folder}": build successful, removing temp dir')
                shutil.rmtree(self.path)
                self.ctx.temp_dir = None
        else:
            LOGGER.warning(f'"{self.ctx.source_folder}": build failed, keeping temp dir: "{self.path}"')
