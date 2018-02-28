from . import PersianTextBase


class PersianKeymap(PersianTextBase):

    def translate_keymap(self):
        """
        Translate english keyboard layout to persian
        Note: Assumes that characters written with standard
        persian keyboard, not windows arabic layout.
        :return: string
        """
        keymap_dict = {
            'q': 'ض',
            'w': 'ص',
            'e': 'ث',
            'r': 'ق',
            't': 'ف',
            'y': 'غ',
            'u': 'ع',
            'i': 'ه',
            'o': 'خ',
            'p': 'ح',
            '[': 'ج',
            ']': 'چ',
            'a': 'ش',
            's': 'س',
            'd': 'ی',
            'f': 'ب',
            'g': 'ل',
            'h': 'ا',
            'j': 'ت',
            'k': 'ن',
            'l': 'م',
            ';': 'ک',
            "'": 'گ',
            'z': 'ظ',
            'x': 'ط',
            'c': 'ز',
            'v': 'ر',
            'b': 'ذ',
            'n': 'د',
            'm': 'پ',
            ',': 'و',
            '?': '؟',
        }
        self.replace_by_character_map('persian_keymap_replace', keymap_dict)
        return self
