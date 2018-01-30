from open_publishing.core.enums import ValueStatus
from open_publishing.core import Field

class PriceField(Field):
    def __init__(self,
                 document,
                 valid_price_types,
                 price_locator):

        super(PriceField, self).__init__(database_object=document,
                                         aspect="prices.*" )  #price_locator + ".type"
        self._valid_price_types = valid_price_types
        self._price_locator = price_locator
        self._value = None

    @property
    def value(self):
        if self.status is ValueStatus.none:
            raise RuntimeError("Accessing to field which is not set")
        else :
            return self._value

    def hard_set(self,
                 value):
        if isinstance(value, self._valid_price_types):
            price_type = self._find_price_type(value.price_type.identifier)
            self._value = price_type(self._database_object,
                                     self._price_locator)
            self._value.hard_set(value)
            self._status = ValueStatus.hard
        else :
            raise ValueError("Expected instance of {0}, got {1}".format(self._valid_price_types, type(value)))

    def update(self,
               gjp):
        cursor = self._master_object(gjp)
        for fname in self._price_locator.split(".") + ['type']:
            if fname in cursor:
                cursor = cursor[fname]
            else :
                return 
        price_type = self._find_price_type(cursor)
        if self._status is not ValueStatus.hard:
            if not isinstance(self._value, price_type):
                self._value = price_type(self._database_object,
                                         self._price_locator)
            self._status = ValueStatus.soft

        if self._status is not ValueStatus.none:
            self._value.update(gjp)
            
    def gjp(self,
            gjp):
        if self._status is not ValueStatus.none:
            if self._status is ValueStatus.hard:
                cursor = gjp
                for fname in self._price_locator.split("."):
                    if fname not in cursor:
                        cursor[fname] = {}
                    cursor = cursor[fname]
                cursor['type'] = self._value.price_type.identifier
            self._value.gjp(gjp)

    def _find_price_type(self,
                         name):
        for price_type in self._valid_price_types:
            if name == price_type._price_type.identifier:
                return price_type
        return None
