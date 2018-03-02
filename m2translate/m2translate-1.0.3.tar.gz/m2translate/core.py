from m2translate.interfaces import StoreConnector
from math import fabs

__author__ = 'Maxim Dutkin (max@dutkin.ru)'


class M2Translate:
    def __init__(self, connector: StoreConnector, not_found_val: str=''):
        """
        Init core class.
        :param connector: previously inited class of `StoreConnector`
        :param not_found_val: default value, returned for non-existent values and placeholders
        """
        self.__connector = connector
        self.locales = dict()
        self.__cur_locale = None
        self.reload_locales()
        self.not_found_val = not_found_val

    def p(self, ph, v: int or bool or float=None, l=None) -> str:
        """
        Returns NONE v for placeholder, but only if current l is set.
        :param ph: placeholder name
        :param v: value, which placeholder references to
        :param l: locale name
        """
        if not l:
            self.__check_cur_locale()

        if l and l not in self.locales.keys():
            raise KeyError('you tried to access locale, which is not presented')

        loc_to_go = l if l else self.__cur_locale

        converted_v = M2Translate.__v_2_int(v)
        if converted_v == 0:
            v_index = 0
        elif converted_v == 1:
            v_index = 1
        else:
            v_index = 2

        if self.__check_ph_in_locale(loc_to_go, ph):
            return self.locales[loc_to_go][ph][v_index]
        else:
            # TODO maybe raise exception on non-existent ph?
            # raise KeyError('no placeholder `%s` found in current l' % ph)
            return self.not_found_val

    def set_p(self, ph, none=None, single=None, multi=None, l=None):
        """
        Sets placeholder value(s). Different values may be set separately or in one time.
        Also may be used with `cur_locale` set, this way you shouldn't specify `l` param.
        :param ph: placeholder name
        :param none: different value, also value for zero `v` (when you request it via `p`
                     method)
        :param single: value for single `v` (when you request it via `p` method)
        :param multi: value for multiple `v` (when you request it via `p` method)
        :param l: locale name
        """
        if not l:
            self.__check_cur_locale()

        if l and l not in self.locales.keys():
            raise KeyError('you tried to access locale, which is not presented')

        loc_to_go = l if l else self.__cur_locale

        if self.__check_ph_in_locale(loc_to_go, ph):
            old_values = self.locales[loc_to_go][ph]
            values = [
                old_values[0] if none is None else none,
                old_values[1] if single is None else single,
                old_values[2] if multi is None else multi,
            ]
        else:
            values = [
                self.not_found_val if none is None else none,
                self.not_found_val if single is None else single,
                self.not_found_val if multi is None else multi,
            ]
        self.locales[loc_to_go][ph] = values

    def set_cur_locale(self, locale):
        """
        Sets current locale. You need current locale for functions, which need
        locale name, but you're too lazy to pass it again and again, i.e. `p(self, ph)`
        :param locale:
        :return:
        """
        if locale not in self.locales:
            raise KeyError('you can\'t set non-existent locale as your current')

        self.__cur_locale = locale

    def reload_locales(self):
        """
        Reloads locales from store
        """
        self.locales = {l: self.__connector.load_locale(l) for l in self.__connector.locales()}
        self.__cur_locale = None if not len(self.locales) else list(self.locales.keys())[0]

    def dump_locales(self):
        """
        Dumps current state of placeholders in locales to DB. Sorts keys inside each locale.
        If ph is added in one locale, but missing in another - fixes it. So, this method is
        kind of syncing.
        """
        # first, collect all unique placeholders
        unq_phs = []
        for l in self.locales:
            [unq_phs.append(ph) for ph in self.locales[l].keys() if ph not in unq_phs]
        unq_phs = sorted(unq_phs)

        # form ordered locale data with
        for l in self.locales:
            data = {}
            for ph in unq_phs:
                if ph in self.locales[l].keys():
                    data[ph] = self.locales[l][ph]
                else:
                    data[ph] = [
                        self.not_found_val,
                        self.not_found_val,
                        self.not_found_val
                    ]
                    self.locales[l][ph] = [
                        self.not_found_val,
                        self.not_found_val,
                        self.not_found_val
                    ]
            self.__connector.save_locale(l, data)

    @property
    def cur_locale(self) -> str:
        """
        Returns current locale
        """
        return self.__cur_locale

    def add_locale(self, locale: str, dump_permanently: bool=True):
        """
        Adds new locale to system and dumps it to store (by default) with all placeholders, including
        placeholders from other locales
        :param locale: locale name
        :param dump_permanently: whether or not to dump all locales after adding new one
        """
        if locale in self.locales:
            raise ValueError('locale you want to set is already in store')

        self.locales[locale] = dict()

        # set default locale if locales list was empty
        if len(self.locales) == 1:
            self.set_cur_locale(locale)

        if dump_permanently:
            self.dump_locales()

    def remove_locale(self, locale: str, dump_permanently: bool=True):
        """
        Removes locale from system and store, also refreshing all other locales
        :param locale: locale name
        :param dump_permanently: whether or not to dump all locales after removing old one
        """
        if locale not in self.locales:
            raise ValueError('locale you want to set is already deleted from store')

        del self.locales[locale]
        if self.__cur_locale == locale:
            self.__cur_locale = None
        self.__connector.remove_locale(locale)

        if dump_permanently:
            self.dump_locales()

    def clear_store(self):
        """
        Removes all data from the store (all locales, all placeholders)
        """
        self.__connector.clear_store()
        self.locales = dict()
        self.__cur_locale = None

    def __check_cur_locale(self) -> None:
        """
        Checks that current locale is set (used in some methods) and is in locales list
        """
        if not self.__cur_locale:
            raise KeyError('current locale is not set')
        if self.__cur_locale not in self.locales:
            raise KeyError('current locale is not in loaded locales list')

    def __check_ph_in_locale(self, locale, ph) -> bool:
        """
        Checks that requested placeholder is in locale dict
        :param locale: locale name
        :param ph: placeholder name
        """
        return ph in self.locales[locale].keys()

    @staticmethod
    def __v_2_int(v) -> int:
        """
        Converts `v` to int val, whatever value is inside
        :param v: value to convert
        """
        # int, float or boolean
        if type(v) in (int, float, bool):
            return int(fabs(v))
        # string
        if type(v) == str:
            try:
                result = int(v)
                return int(fabs(result))
            except ValueError or TypeError:
                return 0
        # other types are not able to convert, so return 0
        return 0
