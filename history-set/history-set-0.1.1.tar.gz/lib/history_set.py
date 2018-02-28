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


    def reset(self):
        self.__added__.clear()
        self.__removed__.clear()
