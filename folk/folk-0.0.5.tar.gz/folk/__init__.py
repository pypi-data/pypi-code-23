"""Utilities for pandas."""

from .model import (  # noqa: F401
    ParameterizedModel,
    ConstrainedParameterizedModel,
)
from .pipe import ParameterizedPipeline  # noqa: F401
from .metricsdb import MetricKey  # noqa: F401
from .evaluate import (  # noqa: F401
    eval_param_pipeline_n_model,
)

from ._version import get_versions
__version__ = get_versions()['version']

for name in ['get_versions', '_version', 'model', 'pipe', 'name']:
    try:
        globals().pop(name)
    except KeyError:
        pass
