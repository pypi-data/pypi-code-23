from .. import Text


class PersianTextBase(Text):
    language = 'persian'
    iso_639_1_code = 'fa'

    def __repr__(self):
        return 'PersianText("%s")' % self.value
