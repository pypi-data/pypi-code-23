from collections import Set


class HistorySet(Set):
    def __init__(self, data, eidetic=False):
        self.__eidetic__ = eidetic
        self.__data__ = set(data)
        self.__added__ = set([])
        self.__removed__ = set([])

    def __contains__(self, item):
        return item in self.__data__

    def __iter__(self):
        return self.__data__.__iter__()

    def __len__(self):
        return len(self.__data__)

    def __repr__(self):
        return self.__data__.__repr__()

    def add(self, item):
        if(item not in self.__data__):
            if(not self.__eidetic__ and item in self.__removed__):
                self.__removed__.remove(item)
            else:
                self.__added__.add(item)
            self.__data__.add(item)

    def remove(self, item):
        if(item not in self.__data__):
            raise KeyError

        if(not self.__eidetic__ and item in self.__added__):
            self.__added__.remove(item)
        else:
            self.__removed__.add(item)
        self.__data__.remove(item)

    def added(self):
        return self.__added__

    def removed(self):
        return self.__removed__

    def clear(self):
        for item in self.__data__:
            self.__removed__.add(item)
        self.__data__.clear()

    def reset(self, added=None, removed=None):
        if added:
            self.__added__.clear()
        elif removed:
            self.__removed__.clear()
        else:
            self.__added__.clear()
            self.__removed__.clear()