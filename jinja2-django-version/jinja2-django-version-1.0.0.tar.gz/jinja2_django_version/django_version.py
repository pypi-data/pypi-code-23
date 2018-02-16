"""Include Django version in Jinja2 templates."""

import django
from jinja2.ext import Extension


class DjangoVersion():
    """An object that contains django version information."""

    tuple = django.VERSION
    major = '{}'.format(tuple[0])
    minor = '{}.{}'.format(tuple[0], tuple[1])
    micro = '{}.{}.{}'.format(tuple[0], tuple[1], tuple[2])

    def __str__(self):
        """Return Django version up to minor."""
        return self.minor


class DjangoVersionExtension(Extension):
    """Jinja extension that adds Django versions globals."""

    def __init__(self, environment):
        """Extend environment by adding globals."""
        super().__init__(environment)

        environment.globals['django_version'] = DjangoVersion()
