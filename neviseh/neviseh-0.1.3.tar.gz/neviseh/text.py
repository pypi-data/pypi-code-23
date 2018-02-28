import re
from typing import Union
from .utils import multiple_replace, generate_multiple_replace_pattern
from .pattern import PatternDict


class TextBase:
    language = None
    _initial_value = None
    iso_639_1_code = None

    def __init__(self, value: Union[str, int, float]):
        self.value = self._initial_value = str(value)
        self.patterns = PatternDict()

    def __str__(self):
        return self.value

    def __repr__(self):
        return 'Text("%s")' % self._initial_value

    def replace_by_character_map(self, pattern_name: str, characters_map: dict):
        """
        Replace value with dictionary of characters
        :param pattern_name: Pattern name will cache on memory
        :param characters_map: Characters map dictionary
        :return:
        """
        if pattern_name not in self.patterns:
            self.patterns[pattern_name] = generate_multiple_replace_pattern(characters_map)

        self.value = multiple_replace(
           characters_map, self.value, self.patterns[pattern_name]
        )
        return self


class TextNormalization(TextBase):

    def __init__(self, value):
        super().__init__(value)
        self.patterns.update({
            'extra_spaces': ' +',
            'extra_newlines': '\n\n+',
            'replace_three_dots': ' ?\.\.\.'
        })

    def replace_three_dots(self):
        """
        Replace three dots with unicode ellipsis
        :return:
        """
        self.value = re.sub(self.patterns['replace_three_dots'], ' …', self.value)
        return self

    def remove_extra_spaces(self):
        """
        Replace extra spaces
        :return:
        """
        self.value = re.sub(self.patterns['extra_spaces'], ' ', self.value)
        return self

    def remove_extra_newlines(self):
        """
        Replace extra new lines
        :return:
        """
        self.value = re.sub(self.patterns['extra_newlines'], '\n', self.value)
        return self

    def normalize(self):
        """
        Apply all normalizations
        :return:
        """
        self.remove_extra_newlines()
        self.remove_extra_spaces()
        self.replace_three_dots()
        return self


class Text(TextNormalization):
    pass
