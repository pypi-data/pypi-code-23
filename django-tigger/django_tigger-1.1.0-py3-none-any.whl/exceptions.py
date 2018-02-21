from django.contrib.messages import constants
from django.shortcuts import resolve_url


class Bounce(Exception):

    def __init__(self, url, message=None, level=None, *args):
        """
        :param url: Where you want the user to be bounced to, this can be
                    anything that ``resolve_url()`` will accept.
        :param level: one of the following (we're limited to the values in the
                      messaging framework:
                        * ``DEBUG``
                        * ``INFO``
                        * ``SUCCESS``
                        * ``WARNING``
                        * ``ERROR``
        :param message: The message to send the user, if any.
        :param args: Everything else is passed to ``Exception()``.
        """

        self.url = resolve_url(url)
        self.message = message
        self.level = constants.INFO
        if level:
            self.level = getattr(constants, level.upper(), self.level)

        super().__init__("Bouncing user to {}".format(self.url), *args)
