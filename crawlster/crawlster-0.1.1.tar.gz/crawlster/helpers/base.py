class BaseHelper(object):
    """Base class for helpers"""
    is_helper = True
    #: A mapping of name - option definition.
    #: Option definition must be an instance of :py:class:`ConfigOption`
    config_options = {}

    def __init__(self):
        self.config = None
        self.crawler = None

    def initialize(self):
        """Perform initial configuration

        Called right after self.config and self.crawler is populated.
        """
        pass

    def finalize(self):
        """Perform cleanup on crawl finish"""
        pass
