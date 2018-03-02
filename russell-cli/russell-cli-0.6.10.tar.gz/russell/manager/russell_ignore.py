import os

from russell.constants import DEFAULT_FLOYD_IGNORE_LIST
from russell.log import logger as russell_logger


class RussellIgnoreManager(object):
    """
    Manages .russellignore file in the current directory
    """

    CONFIG_FILE_PATH = os.path.join(os.getcwd(), ".russellignore")

    @classmethod
    def init(cls, path=None):
        if path:
            config_path = os.path.join(path, ".russellignore")
        else:
            config_path = cls.CONFIG_FILE_PATH
        if os.path.isfile(config_path):
            russell_logger.debug("russell ignore file already present at {}".format(config_path))
            return

        russell_logger.debug("Setting default russell ignore in the file {}".format(config_path))

        with open(config_path, "w") as config_file:
            config_file.write(DEFAULT_FLOYD_IGNORE_LIST)

    @classmethod
    def get_list(cls):
        if not os.path.isfile(cls.CONFIG_FILE_PATH):
            return []

        ignore_dirs = []
        whitelist = []
        with open(cls.CONFIG_FILE_PATH, "r") as russell_ignore_file:
            for line in russell_ignore_file:
                line = line.strip()

                # if line.startswith('!'):
                #     line = line[1:]
                #     whitelist.append(line)
                #     continue

                if line and not line.startswith('#'):
                    ignore_dirs.append(line)

        return ignore_dirs, whitelist
