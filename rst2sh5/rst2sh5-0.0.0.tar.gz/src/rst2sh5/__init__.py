#


""" Docutils writer outputting semantic HTML5 """


import pkg_resources

from . import main
from . import meta
from . import writer


# PEP 396
__version__ = pkg_resources.get_distribution(
    meta.NAME,  # https://stackoverflow.com/a/22845276
).version


# EOF
