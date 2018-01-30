from datetime import datetime

from open_publishing.core.enums import ValueStatus

from .price import Price, _convert_to_price
from .date import _convert_to_date


class Campaign(object):
    def __init__(self,
                 price,
                 from_date,
                 to_date):
        self._status = ValueStatus.soft
        self._price = _convert_to_price(price)
        self._from_date = _convert_to_date(from_date)
        self._to_date = _convert_to_date(to_date)

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
        
    @property
    def to_date(self):
        return self._to_date

    @to_date.setter
    def to_date(self, value):
        self._to_date = _convert_to_date(value)
        self._status = ValueStatus.hard


    @classmethod
    def from_gjp(cls, gjp):
        price = Price.from_gjp(gjp['price'])
        # from_date = datetime.strptime(gjp['from_date'], '%Y-%m-%d').date()
        # to_date = datetime.strptime(gjp['to_date'], '%Y-%m-%d').date()
        from_date = datetime(*[int(i) for i in gjp['from_date'].split('-')]).date()
        to_date = datetime(*[int(i) for i in gjp['to_date'].split('-')]).date()

        return cls(price,
                   from_date,
                   to_date)

    def to_gjp(self):
        return {'price' : self._price.to_gjp(),
                'from_date' : self._from_date.strftime("%Y-%m-%d"),
                'to_date' : self._to_date.strftime("%Y-%m-%d")}
                
    

class CampaignList(object):
    _item_type = Campaign
    
    def __init__(self,
                 camp_list):
        self._status = ValueStatus.soft
        self._list = camp_list

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
            camp_list.append(Campaign.from_gjp(item))
        return cls(camp_list)

    def to_gjp(self):
        return [item.to_gjp() for item in self._list]

    def add(self,
            price,
            from_date,
            to_date):
        new_camp = Campaign(price,
                            from_date,
                            to_date)
        
        if new_camp.from_date > new_camp.to_date:
            raise ValueError("from_date should be less than to_date")
        for camp in self._list:
            if ((camp.from_date <= new_camp.from_date <= camp.to_date)
                or (camp.from_date <= new_camp.to_date <= camp.to_date)):
                raise ValueError("Campaign time period should not overlap with other campaigns")
        self._list.append(new_camp)
        self._status = ValueStatus.hard
               
