# -*- coding: utf-8 -*-

from .container import Container
import logging
logger = logging.getLogger(__name__)


class ApplicationContext(Container):
    def __init__(self, config=None):
        super(ApplicationContext, self).__init__(config)

        for define in self.defines.values():
            if not define.lazy_init and define.id not in self.objects:
                logger.debug("Eagerly fetching %s" % define.id)
                self.get_object(define.id)
