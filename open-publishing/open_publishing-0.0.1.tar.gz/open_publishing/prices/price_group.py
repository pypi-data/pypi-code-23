from open_publishing.core import FieldGroup
from open_publishing.core import FieldDescriptor

from .price_field import PriceField
from . import price_types
from .price import Price

class CurrentPrice(object):
    def __init__(self,
                 price_json):
        self._free = price_json['free']
        if price_json['price'] is not None:
            self._price = Price.from_gjp(price_json['price'])
        else:
            self._price = None

    @property
    def price(self):
        return self._price

    @property
    def free(self):
        return self._free

class PriceGroup(FieldGroup):
    def __init__(self,
                 document):
        super(PriceGroup, self).__init__(document)
        self._fields["pod"] = PriceField(document=document,
                                         valid_price_types = (price_types.Auto,
                                                              price_types.Manual,
                                                              price_types.NoPrice),
                                         price_locator="prices.pod")

        self._fields["ebook"] = PriceField(document=document,
                                           valid_price_types = (price_types.Auto,
                                                                price_types.Manual,
                                                                price_types.OpenAccess,
                                                                price_types.NoPrice),
                                           price_locator="prices.ebook")

    pod = FieldDescriptor("pod")
    ebook = FieldDescriptor("ebook")


    def recalculate(self):
        self.database_object.context.gjp.recalculate_prices(self.database_object.document_id)

    def current(self, 
                product, 
                country_code, 
                currency_code=None):
        price_json = self.database_object.context.gjp.current_price(self.database_object.document_id,
                                                                    product=product,
                                                                    country_code=country_code,
                                                                    currency_code=currency_code)
        return CurrentPrice(price_json)
