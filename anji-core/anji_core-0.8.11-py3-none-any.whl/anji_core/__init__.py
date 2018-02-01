import errbot
import errbot.bootstrap
import errbot.specific_plugin_manager

from .prehooks import *
from .backend import *
from .cartridges import *
from .flow import *
from .nodes import *
from .messages import *
from .manager import *
from .render import *
from .report import *
from .tasks import *
from .types import *
from .services import *
from .signals import *
from .users import *
from .utils import *
from .events import *
from .help import *
from .test import *

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class AnjiArgumentParser(errbot.ArgumentParser):

    def _get_formatter(self):
        return self.formatter_class(prog=self.prog, width=1000)


errbot.ArgumentParser = AnjiArgumentParser


def bpm_from_config(config):
    """Creates a backend plugin manager from a given config."""
    extra = getattr(config, 'BOT_EXTRA_BACKEND_DIR', [])
    return errbot.specific_plugin_manager.SpecificPluginManager(
        config,
        'backends',
        AnjiBackendMixin,
        errbot.bootstrap.CORE_BACKENDS,
        extra_search_dirs=extra
    )


errbot.bootstrap.bpm_from_config = bpm_from_config
