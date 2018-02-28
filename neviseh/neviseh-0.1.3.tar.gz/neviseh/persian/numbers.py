from . import PersianTextBase


class PersianNumbers(PersianTextBase):

    def translate_arabic_numbers(self):
        """
        Translate Arabic numbers to Persian
        :return:
        """
        characters_map = {
            '١': '۱',
            '٢': '۲',
            '٣': '۳',
            '٤': '۴',
            '٥': '۵',
            '٦': '۶',
            '٧': '۷',
            '٨': '۸',
            '٩': '۹',
            '٠': '۰',
        }
        self.replace_by_character_map('arabic_numbers_replace', characters_map)
        return self

    def translate_latin_numbers(self):
        """
        Translate Latin numbers to Persian
        :return:
        """
        characters_map = {
            '0': '۰',
            '1': '۱',
            '2': '۲',
            '3': '۳',
            '4': '۴',
            '5': '۵',
            '6': '۶',
            '7': '۷',
            '8': '۸',
            '9': '۹',
            '.': '.',
            '%': '٪'
        }
        self.replace_by_character_map('latin_numbers_replace', characters_map)
        return self
