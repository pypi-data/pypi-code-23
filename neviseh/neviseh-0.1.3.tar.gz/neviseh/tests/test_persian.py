import unittest
from neviseh import PersianText


class PersianTextTestCase(unittest.TestCase):

    def test_base(self):
        # Class representation
        self.assertEqual(repr(PersianText('سلام')), 'PersianText("سلام")')
        self.assertEqual(repr(PersianText('سلام').translate_keymap()), 'PersianText("سلام")')

    def test_keymap(self):
        self.assertEqual(
            str(PersianText('sghl').translate_keymap()),
            'سلام'
        )

    def test_normalization(self):
        # Remove keshida
        self.assertEqual(
            str(PersianText('ســـــلام').remove_keshida()),
            'سلام'
        )

        # Remove diacritics
        self.assertEqual(
            str(PersianText('بُشقابِ مَن را بِگیر').remove_diacritics()),
            'بشقاب من را بگیر'
        )

        # Apply punctuation spacing
        self.assertEqual(
            str(PersianText('اصلاح ( پرانتزها ) در متن .').apply_punctuation_spacing()),
            'اصلاح (پرانتزها) در متن.'
        )
        self.assertEqual(
            str(PersianText('نسخه 0.5 در ساعت 22:00 تهران،1396').apply_punctuation_spacing()),
            'نسخه 0.5 در ساعت 22:00 تهران، 1396'
        )

        # Replace quotation with gyoomeh
        self.assertEqual(
            str(PersianText('نام او "جک" است').replace_quotation()),
            'نام او «جک» است'
        )

        # Replace decimal dots with Momayez
        self.assertEqual(
            str(PersianText('مبلغ برابر با 4.2 میلیارد است').replace_decimal_dots()),
            'مبلغ برابر با 4٫2 میلیارد است'
        )

        # Replace replace arabic letters
        self.assertEqual(
            str(PersianText('اصلاح كاف و ىاي عربي و سایر چیزهای مشابه').replace_similar_letters()),
            'اصلاح کاف و یای عربی و سایر چیزهای مشابه'
        )

        # Apply all
        self.assertEqual(
            str(PersianText('اصلاح كــاف و ىاي عربي و سایر چیزهای مشابه').normalize()),
            'اصلاح کاف و یای عربی و سایر چیزهای مشابه'
        )

    def test_numbers(self):

        # Translate latin numbers
        self.assertEqual(
            str(PersianText('0123456789۰۱۲۳۴۵۶۷۸۹').translate_latin_numbers()),
            '۰۱۲۳۴۵۶۷۸۹۰۱۲۳۴۵۶۷۸۹'
        )

        # Translate Arabic numbers
        self.assertEqual(
            str(PersianText('۰۱۲۳٤۵٦۷۸۹۰۱۲۳۴۵۶۷۸۹').translate_arabic_numbers()),
            '۰۱۲۳۴۵۶۷۸۹۰۱۲۳۴۵۶۷۸۹'
        )

        # Translate calendar weekdays
        self.assertEqual(
            str(PersianText('دوشنبه').translate_weekdays_to_number()),
            '2'
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
