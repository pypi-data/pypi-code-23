"""Main module."""

from logging import getLogger

from rest_framework.renderers import BaseRenderer

from potential_spork.util import entabulate

logger = getLogger(__name__)


class FixedWidthRenderer(BaseRenderer):
    """
    Renderer that generates fixed width files.
    """

    media_type = 'text/text'
    format = 'txt'
    field_config = {}

    def render(self, data, media_type=None, renderer_context={}):
        if data is None:
            return ''

        field_config = renderer_context.get('field_config', self.field_config)

        if not field_config:
            raise ValueError("A non-empty field_config is required.")

        output = entabulate(data, field_config)

        return output
