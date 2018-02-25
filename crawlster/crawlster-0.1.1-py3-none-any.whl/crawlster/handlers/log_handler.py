import pprint

from .base import BaseItemHandler


class LogItemHandler(BaseItemHandler):
    """Item handler that logs the submitted items via the crawler logger"""

    valid_levels = (
        'debug', 'info', 'warning', 'error', 'critical'
    )

    def __init__(self, level='warning'):
        """Initializes the """
        if level not in self.valid_levels:
            err_msg = 'Invalid logging level. Accepted only one of {}'.format(
                ', '.join(self.valid_levels))
            raise ValueError(err_msg)

        super(LogItemHandler, self).__init__()
        self.logger = None
        self.level = level

    def handle(self, item):
        method = getattr(self.crawler.log, self.level)
        method(pprint.pformat(item, indent=4) + '\n')
