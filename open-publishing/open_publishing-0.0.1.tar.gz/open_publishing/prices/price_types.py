import datetime

from open_publishing.core import FieldGroup
from open_publishing.core import FieldDescriptor
from open_publishing.core.enums import PriceType

from .territories import TerritoryList
from .auto_price import  AutoPrice
from .price import Price

class PriceTypeBase(FieldGroup):
    _price_type = None
    def __init__(self,
                 document,
                 price_locator):
        super(PriceTypeBase, self).__init__(document)
        self._price_locator = price_locator

    @property
    def price_type(self):
        return self._price_type

    def periods(self,
                country,
                date_from=None,
                date_to=None,
                include_campains=True,
                remove_outdated=None):
        result = self.database_object.context.gjp.get_price_periods(self.database_object.document_id,
                                                                    country,
                                                                    date_from,
                                                                    date_to,
                                                                    include_campains,
                                                                    remove_outdated)
        country_code = list(result.keys())[0]
        periods = []
        class Period(object):
            def __init__(self,
                         country_code,
                         price,
                         since,
                         until):
                self.country_code = country_code
                self.price = price 
                self.since = since
                self.until = until

        for period in list(result.values())[0][self._price_locator.split('.')[-1]]:
            periods.append(Period(country_code,
                                  Price.from_gjp(period['price']),
                                  datetime.date(*period['from']) if period['from'] else None,
                                  datetime.date(*period['until']) if period['until'] else None,))
        return periods
        
        

    
class OpenAccess(PriceTypeBase):
    _price_type = PriceType.open_access
    def __init__(self,
                 document,
                 price_locator):
        super(OpenAccess, self).__init__(document,
                                         price_locator)
class Auto(PriceTypeBase):
    _price_type = PriceType.auto
    def __init__(self,
                 document,
                 price_locator):
        super(Auto, self).__init__(document,
                                   price_locator)
        self._fields["price"] = AutoPrice(document=document,
                                          price_locator=price_locator)
    price = FieldDescriptor("price")


class NoPrice(PriceTypeBase):
    _price_type = PriceType.no_price
    def __init__(self,
                 document,
                 price_locator):
        super(NoPrice, self).__init__(document,
                                      price_locator)



class Manual(PriceTypeBase):
    _price_type = PriceType.manual
    def __init__(self,
                 document,
                 price_locator):
        super(Manual, self).__init__(document,
                                     price_locator)
        self._fields["territories"] = TerritoryList(document=document,
                                                    price_locator=price_locator)
        

    territories = FieldDescriptor("territories")

