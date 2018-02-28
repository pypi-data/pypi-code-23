from . import EnglishTextBase


class EnglishNumbers(EnglishTextBase):

    def translate_persian_numbers(self):
        """
        Translate Persian numbers to Latin
        :return:
        """
        characters_map = {
            '۰': '0',
            '۱': '1',
            '۲': '2',
            '۳': '3',
            '۴': '4',
            '۵': '5',
            '۶': '6',
            '۷': '7',
            '۸': '8',
            '۹': '9',
            '.': '.',
            '٪': '%',
        }
        self.replace_by_character_map('persian_numbers_replace', characters_map)
        return self
