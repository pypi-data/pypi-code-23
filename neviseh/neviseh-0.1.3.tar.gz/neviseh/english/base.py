from .. import Text


class EnglishTextBase(Text):
    language = 'english'
    iso_639_1_code = 'en'

    def __repr__(self):
        return 'EnglishText("%s")' % self.value
