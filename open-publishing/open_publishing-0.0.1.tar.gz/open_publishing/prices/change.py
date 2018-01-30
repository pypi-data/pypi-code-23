from datetime import datetime

from open_publishing.core.enums import ValueStatus

from .price import Price, _convert_to_price
from .date import _convert_to_date

class Change(object):
    def __init__(self,
                 price,
                 from_date):
        self._status = ValueStatus.soft
        self._price = _convert_to_price(price)
        self._from_date = _convert_to_date(from_date)

    @property
    def status(self):
        return self._status

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = _convert_to_price(value)
        self._status = ValueStatus.hard

    @property
    def from_date(self):
        return self._from_date

    @from_date.setter
    def from_date(self, value):
        self._from_date = _convert_to_date(value)
        self._status = ValueStatus.hard
        
    @classmethod
    def from_gjp(cls, gjp):
        price = Price.from_gjp(gjp['price'])
        # from_date = datetime.strptime(gjp['from_date'], '%Y-%m-%d').date()
        from_date = datetime(*[int(i) for i in gjp['from_date'].split('-')]).date()
        return cls(price,
                   from_date)

    def to_gjp(self):
        return {'price' : self._price.to_gjp(),
                'from_date' : self._from_date.strftime("%Y-%m-%d")}
                
    

class ChangeList(object):
    _item_type = Change
    def __init__(self,
                 change_list):
        self._status = ValueStatus.soft
        self._list = change_list
        
    def add(self,
            price,
            from_date):
        new_change = Change(price, from_date)
        for change in self._list:
            if new_change.from_date == change.from_date:
                raise ValueError("This date has been used before")
        self._list.append(new_change)
        self._status = ValueStatus.hard

    @property
    def status(self):
        for item in self._list:
            if item.status == ValueStatus.hard:
                return ValueStatus.hard
        else:
            return self._status

    def __len__(self):
        return len(self._list)

    def __getitem__(self, key):
        items = self._list[key]
        if isinstance(items, list):
            return [item for item in items]
        else :
            return items

    def __delitem__(self, key):
        del self._list[key]
        self._status = ValueStatus.hard
        
    def __iter__(self):
        return iter([item for item in self._list])

    @classmethod
    def from_gjp(cls, gjp):
        camp_list = []
        for item in gjp:
            camp_list.append(Change.from_gjp(item))
        return cls(camp_list)

    def to_gjp(self):
        return [item.to_gjp() for item in self._list]

