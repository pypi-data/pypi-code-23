from . import EnglishTextBase


class EnglishKeymap(EnglishTextBase):

    def translate_keymap(self):
        """
        Translate Persian keyboard layout to English
        Note: Assumes that characters written with standard
              persian keyboard layout (ISIRI 2901).
              http://www.isiri.gov.ir/portal/files/std/9147.pdf
        :return: string
        """
        keymap_dict = {
            'خ': 'o',
            '؟': '?',
            'ک': ';',
            'ض': 'q',
            'ذ': 'b',
            'ز': 'c',
            'ح': 'p',
            'و': ',',
            'ف': 't',
            'چ': ']',
            'ج': '[',
            'پ': 'm',
            'ن': 'k',
            'ص': 'w',
            'س': 's',
            'ث': 'e',
            'ش': 'a',
            'ط': 'x',
            'گ': '\'',
            'ع': 'u',
            'غ': 'y',
            'ق': 'r',
            'م': 'l',
            'ی': 'd',
            'ظ': 'z',
            'د': 'n',
            'ه': 'i',
            'ل': 'g',
            'ر': 'v',
            'ت': 'j',
            'ا': 'h',
            'ب': 'f',
        }
        self.replace_by_character_map('english_keymap_replace', keymap_dict)
        return self
