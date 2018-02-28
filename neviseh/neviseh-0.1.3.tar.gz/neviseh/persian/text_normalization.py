import re
from . import PersianTextBase


class PersianTextNormalization(PersianTextBase):

    def __init__(self, value):
        super().__init__(value)
        punctuation_after, punctuation_before = (
            '\.:!،؛؟»\]\)\}',
            '«\[\(\{'
        )

        self.patterns.update({
            'remove_keshida': r'[ـ\r]',
            'remove_diacritics': r'[\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652]',
            'replace_quotation': r'"([^\n"]+)"',
            'replace_decimal_dots': '([\d+])\.([\d+])',

            'remove_space_before_and_after_quotation': r'" ([^\n"]+) "',
            'remove_space_before': ' ([' + punctuation_after + '])',
            'remove_space_after': '([' + punctuation_before + ']) ',
            'put_space_after_dot': '([' + punctuation_after[:3] + '])([^ \d' + punctuation_after + '])',
            'put_space_after': '([' + punctuation_after[3:] + '])([^ ' + punctuation_after + '])',
            'put_space_before': '([^ ' + punctuation_before + '])([' + punctuation_before + '])',
        })

    def remove_keshida(self):
        """
        Remove Keshida/ARABIC_TATWEEL
        :return:
        """
        self.value = re.sub(self.patterns['remove_keshida'], '', self.value)
        return self

    def remove_diacritics(self):
        """
        Remove Arabic/Persian diacritics.
        includes: FATHATAN, DAMMATAN, KASRATAN, FATHA,
                  DAMMA, KASRA, SHADDA, SUKUN
        :return:
        """
        self.value = re.sub(self.patterns['remove_diacritics'], '', self.value)
        return self

    def apply_punctuation_spacing(self):
        """
        Apply punctuation spacing
        :return:
        """
        self.value = re.sub(self.patterns['remove_space_before_and_after_quotation'], r'"\1"', self.value)
        self.value = re.sub(self.patterns['remove_space_before'], r'\1', self.value)
        self.value = re.sub(self.patterns['remove_space_after'], r'\1', self.value)
        self.value = re.sub(self.patterns['put_space_after_dot'], r'\1 \2', self.value)
        self.value = re.sub(self.patterns['put_space_after'], r'\1 \2', self.value)
        self.value = re.sub(self.patterns['put_space_before'], r'\1 \2', self.value)
        return self

    def replace_quotation(self):
        """
        Replace quotation with gyoomeh
        :return:
        """
        self.value = re.sub(self.patterns['replace_quotation'], r'«\1»', self.value)
        return self

    def replace_decimal_dots(self):
        """
        Replace decimal Dot with Momayez
        :return:
        """
        self.value = re.sub(self.patterns['replace_decimal_dots'], r'\1٫\2', self.value)
        return self

    def replace_similar_letters(self):
        """
        Replace similar letters in persian
        :return:
        """
        characters_map = {
            'ك': 'ک',
            'دِ': 'د',
            'بِ': 'ب',
            'زِ': 'ز',
            'ذِ': 'ذ',
            'شِ': 'ش',
            'سِ': 'س',
            'ى': 'ی',
            'ي': 'ی'
        }
        self.replace_by_character_map('arabic_persian_letters_replace', characters_map)
        return self

    def normalize(self):
        """
        Apply all normalizations
        :return:
        """
        super().normalize()
        return (
            self.remove_keshida()
                .replace_similar_letters()
                .replace_quotation()
                .remove_diacritics()
                .apply_punctuation_spacing()
        )
