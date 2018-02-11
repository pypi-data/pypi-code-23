""" Main application module """


import docutils.core

from . import meta
from . import writer


def entry_point():
    """ Entry point for main console script """
    description = docutils.core.default_description

    docutils.core.publish_cmdline(
        writer=writer.Writer(),
        writer_name=meta.NAME,
        description=description,
    )

    return


# EOF
