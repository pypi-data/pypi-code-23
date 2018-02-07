from .vaquero import Vaquero, VaqueroException
from .invocation_tools import callables_from
from .pipeline import ModulePipeline, Done
from .collectors import SetCollector
from .util import examine_pairwise_result


__title__ = "vaquero"
__description__ = "A library for iterative and interactive data wrangling"
__uri__ = "https://github.com/jbn/vaquero"
__doc__ = __description__ + " <" + __uri__ + ">"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2017 John Bjorn Nelson"
__version__ = "0.0.4"
__author__ = "John Bjorn Nelson"
__email__ = "jbn@abreka.com"
