#encoding: UTF-8


class TimeIntervalMixin():

    @property
    def t1(self):
        return getattr(self, '_t1', None)

    @t1.setter
    def t1(self, value):
        if not hasattr(self, '_t1'):
            #Случай 1. Когда нет ничего
            self._t1 = value
            self.t2 = value
        elif self._t1 > value:
            #Случай подгруза из истории
            self._t1 = value
        elif self.t2 < value:
            #Случай повторного присвоения временной метки
            self.pre_time = self.t2
            self.t2 = value
            self._last_interval = self.t2 - self.pre_time
            self._sum_intervals = getattr(self, '_sum_intervals', 0) + self._last_interval
            self._count_intervals = getattr(self, '_count_intervals', 0) + 1
            self.avg_interval = float(self._sum_intervals) / float(self._count_intervals)
            self.min_interval = min(getattr(self, 'min_interval', float('inf')), self._last_interval)
            self.max_interval = max(getattr(self, 'max_interval', 0), self._last_interval)

if __name__ == "__main__":

    o = TimeIntervalMixin()
    print(o.__dict__)
    o.t1 = 1
    print(o.__dict__)
    o.t1 = 10
    print(o.__dict__)
    o.t1 = 20
    print(o.__dict__)
    o.t1 = 50
    print(o.__dict__)
