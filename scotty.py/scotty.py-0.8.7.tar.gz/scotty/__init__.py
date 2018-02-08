from  scotty import log
log.setup_logging()

__all__ = ['__version__']

import pbr.version

version_info = pbr.version.VersionInfo('scotty.py')
try:
    __version__ = version_info.version_string()
except AttributeError:
    __version__ = None
