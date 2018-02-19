from warnings import warn

from .dataimport import *  # noqa F401


warn(
    '[1.3.0] "post321_import" module got renamed into "dataimport"',
    DeprecationWarning,
)
