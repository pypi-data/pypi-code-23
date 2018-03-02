__author__ = 'Maxim Dutkin (max@dutkin.ru)'


class StoreConnector:
    def locales(self) -> list:
        """
        Retrieve list of available locales in store
        """
        raise NotImplementedError()

    def load_locale(self, locale: str):
        """
        Retrieve all placeholders for `locale`
        :param locale: locale name
        """
        raise NotImplementedError()

    def save_locale(self, locale: str, data: dict):
        """
        Save locale data
        :param locale: locale name
        :param data: locale data
        """
        raise NotImplementedError()

    def remove_locale(self, locale: str):
        """
        Delete locale from store
        :param locale: locale name
        """
        raise NotImplementedError()

    def clear_store(self):
        """
        Removes all data from the store (all locales, all placeholders)
        """
        raise NotImplementedError()
