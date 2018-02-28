from .base import PersianTextBase
from .calendar import PersianCalendar
from .keymap import PersianKeymap
from .numbers import PersianNumbers
from .text_normalization import PersianTextNormalization


class PersianText(
    PersianCalendar,
    PersianKeymap,
    PersianNumbers,
    PersianTextNormalization,
):
    pass
