from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc
from abc import ABCMeta
from builtins import *  # NOQA

from zsl_openapi.api import ApiDescription  # NOQA


class ApiDescriptionBuilder:
    __metaclass__ = ABCMeta

    @abc.abstractmethod
    def build(self, api_description):
        # type: (ApiDescription)->None
        pass
