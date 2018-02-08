from intermake import MENV
from csveditor import extensions

__version__ = "0.0.0.10"

MENV.name = "CsvEditor"
MENV.version = __version__
MENV.plugins.register( extensions )
