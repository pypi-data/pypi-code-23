
from django.utils.module_loading import import_string

from flatpages.settings import FLATPAGE_EDITORS


def get_editor_widget(editor_name):

    if editor_name:
        try:
            return import_string(FLATPAGE_EDITORS[editor_name])
        except ImportError:
            raise Exception('Flatpage editor module is undefined')
        except KeyError:
            raise Exception('Unknown flatpage editor module')

    return None
