from m2translate.interfaces import StoreConnector
import os
import json

__author__ = 'Maxim Dutkin (max@dutkin.ru)'


class JSONConnector(StoreConnector):
    def __init__(self, path: str = 'json_store'):
        self.store_path = path
        super(JSONConnector, self).__init__()

    def save_locale(self, locale: str, data: dict):
        file_path = self.__locale_path(locale)
        with open(file_path, 'w') as f:
            content = json.dumps(data, indent=2, ensure_ascii=False)
            f.write(content)

    def remove_locale(self, locale: str):
        json_path = os.path.join(self.store_path)
        for f in os.listdir(json_path):
            file_path = os.path.join(json_path, f)
            if os.path.isfile(file_path):
                basename = os.path.split(file_path)[1]
                l, ext = os.path.splitext(basename)
                if ext == '.json' and l == locale:
                    os.remove(file_path)
                    break

    def load_locale(self, locale: str):
        file_path = self.__locale_path(locale)
        with open(file_path, 'r') as ff:
            data = json.load(ff)
        return data

    def locales(self) -> list:
        locales = list()
        json_path = os.path.join(self.store_path)
        for f in os.listdir(json_path):
            file_path = os.path.join(json_path, f)
            if os.path.isfile(file_path):
                basename = os.path.split(file_path)[1]
                l, ext = os.path.splitext(basename)
                if ext == '.json':
                    locales.append(l)
        return locales

    def clear_store(self):
        json_path = os.path.join(self.store_path)
        for f in os.listdir(json_path):
            file_path = os.path.join(json_path, f)
            if os.path.isfile(file_path):
                basename = os.path.split(file_path)[1]
                l, ext = os.path.splitext(basename)
                if ext == '.json':
                    os.remove(file_path)

    def __locale_path(self, locale: str):
        return os.path.join(self.store_path, '%s.json' % locale)
