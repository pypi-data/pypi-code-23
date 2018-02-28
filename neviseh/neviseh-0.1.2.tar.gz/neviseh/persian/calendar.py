from . import PersianTextBase


class PersianCalendar(PersianTextBase):

    def translate_weekdays_to_number(self, include_common_styles: bool = True):
        """
        Translate weekdays to their number.
        based on python datetime, weekday numbers starts from 0 to 6.
        references:
            https://docs.python.org/3/library/datetime.html#datetime.date.weekday
            https://en.wikipedia.org/wiki/Names_of_the_days_of_the_week
        :return:
        """
        pattern_name = 'persian_weekdays_name_replace'
        words_map = {
            'شنبه': '0',
            'یکشنبه': '1',
            'دوشنبه': '2',
            'سه شنبه': '3',
            'چهارشنبه': '4',
            'پنجشنبه': '5',
            'جمعه': '6',
            'آدینه': '6'
        }
        if include_common_styles:
            pattern_name = 'persian_all_weekdays_name_replace'
            words_map.update(
                {
                    'یک شنبه': '1',
                    'دو شنبه': '2',
                    'دوشنبه': '2',
                    'چهار شنبه': '4',
                    'چارشنبه': '4',
                    'پنج شنبه': '5'
                }
            )

        self.replace_by_character_map(
            pattern_name,
            words_map
        )
        return self
