from open_publishing.core.enums import ValueStatus, FieldKind
from open_publishing.core import Field

from .price import Price, _convert_to_price

class AutoPrice(Field):
    def __init__(self,
                 document,
                 price_locator):
        super(AutoPrice, self).__init__(database_object=document,
                                        aspect="prices.*",
                                        kind=FieldKind.readonly)

        self._price_locator = price_locator
        self._price = None
        
    @property
    def value(self):
        if self._status is ValueStatus.none:
            raise RuntimeError("Accessing to field which is not set")
        else :
            return self._price

    def gjp(self,
            gjp):
        pass
    
    def update(self,
               gjp):
        if self._status is not ValueStatus.hard :
            value = self._master_object(gjp)
            for fname in self._price_locator.split("."):
                if fname in value:
                    value = value[fname]
                else :
                    value = None
                    break
            if value is not None:
                if value['auto_price'] is not None:
                    self._price = Price.from_gjp(value['auto_price'])
                else:
                    self._price = None
                self._status = ValueStatus.soft

        
