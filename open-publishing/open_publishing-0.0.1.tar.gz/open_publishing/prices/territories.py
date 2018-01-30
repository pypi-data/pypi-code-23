from datetime import datetime

from open_publishing.core import SequenceItem, SequenceField
from open_publishing.core.enums import ValueStatus

from .price import Price, _convert_to_price
from .change import ChangeList
from .campaign import CampaignList


class TerritoryPrice(SequenceItem):
    def __init__(self,
                 base_price,
                 is_gross,
                 campaigns,
                 changes,
                 territory_codes):
        super(TerritoryPrice, self).__init__(ValueStatus.soft)
        self._base_price = _convert_to_price(base_price)
        self._is_gross = is_gross
        self._campaigns = campaigns
        self._changes = changes
        self._territory_codes = territory_codes

    @property
    def base_price(self):
        return self._base_price

    @base_price.setter
    def base_price(self, value):
        self._base_price = _convert_to_price(value)
        self._status = ValueStatus.hard


    @property
    def is_gross(self):
        return self._is_gross

    @is_gross.setter
    def is_gross(self, value):
        if isinstance(value, bool):
            self._is_gross = value
            self._status = ValueStatus.hard
        else:
            raise ValueError("is_gross should be bool")
        
    @property
    def campaigns(self):
        return self._campaigns

    @property
    def changes(self):
        return self._changes

    @property
    def territory_codes(self):
        return self._territory_codes

    @territory_codes.setter
    def territory_codes(self, value):
        self._territory_codes = value
        self._status = ValueStatus.hard

    @property
    def status(self):
        for field in [self._campaigns, self._changes]:
            if field.status == ValueStatus.hard:
                return ValueStatus.hard
        else:
            return self._status

    @classmethod
    def from_gjp(cls, gjp, database_object):
        base_price = Price.from_gjp(gjp['base_price'])
        is_gross = bool(gjp['gross_price'])
        campaigns = CampaignList.from_gjp(gjp['campaigns'])
        changes = ChangeList.from_gjp(gjp['changes'])
        territory_codes = set(gjp['territory_codes'])

        return cls(base_price,
                   is_gross,
                   campaigns,
                   changes,
                   territory_codes)

    def to_gjp(self):
        return {'base_price' : self._base_price.to_gjp(),
                'gross_price' : self._is_gross,
                'campaigns' : self._campaigns.to_gjp(),
                'changes' : self._changes.to_gjp(),
                'territory_codes' : list(self._territory_codes)}
    

class TerritoryList(SequenceField):
    _item_type = TerritoryPrice
    
    def __init__(self,
                 document,
                 price_locator):
        super(TerritoryList, self).__init__(document,
                                            "prices.*",
                                            price_locator + ".territories")
        
        
    def add(self,
            base_price,
            is_gross,
            territory_codes):

        if not isinstance(territory_codes, set):
            raise TypeError('Expected set, got {0}'.format(type(territory_codes)))
        if territory_codes.difference(self.database_object.context.territories):
            raise ValueError("Unexpected territory codes: {0}".format(territory_codes.difference(self.database_object.context.territories)))
        if territory_codes == set():
            raise ValueError('Territory codes cannot be empty set')
        if ('WORLD' in territory_codes) and (territory_codes != {'WORLD'}):
            raise ValueError("Territory codes should be {'WORLD'} or should not contain 'WORLD' territory")

        all_ter = set({})
        for item in self:
            all_ter = all_ter | item.territory_codes
        all_ter = all_ter ^ {'WORLD'}
        
        if all_ter & territory_codes:
            raise ValueError('Overlapping territory codes {0}'.format(all_ter & territory_codes))

        new_territory = TerritoryPrice(base_price,
                                       is_gross,
                                       CampaignList([]),
                                       ChangeList([]),
                                       territory_codes)
        
        self._list.append(new_territory)
        self._status = ValueStatus.hard
               
    def __delitem__(self, key):
        if isinstance(key,slice):
            new_len = len(self) - len(self[key]) 
        else :
            new_len = len(self) - 1
        if new_len > 0:
            super(TerritoryList, self).__delitem__(key)
        else:
            raise RuntimeError('Cannot remove all territories')
