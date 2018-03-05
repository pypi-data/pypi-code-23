
from django.conf import settings

from flatpages.constants import FLATPAGE_EDITORS


DEFAULT_EDITOR = getattr(settings, 'FLATPAGE_DEFAULT_EDITOR', None)

EDITORS = getattr(settings, 'FLATPAGE_EDITORS', FLATPAGE_EDITORS)

DEFAULT_TEMPLATE = getattr(
    settings, 'FLATPAGE_DEFAULT_TEMPLATE', 'flatpages/default.html')
