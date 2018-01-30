from open_publishing.core.enums import ValueStatus
from open_publishing.core import Field

class BrandsField(Field):
    def __init__(self,
                 document):
        super(BrandsField, self).__init__(database_object=document,
                                              aspect='brands.*')
        self._value = None

    @property
    def _all_brands(self):
        return self.database_object.context.brands
    
    @property
    def value(self):
        if self.status is ValueStatus.none:
            raise RuntimeError('Accessing to field which is not set')
        else :
            return self._value.copy()

    def hard_set(self,
                 value):
        if isinstance(value, set):
            diff = value.difference(self._all_brands)
            if diff:
                raise ValueError('Not available brands used : {0}'.format(diff))
            self._value = value
            self._status = ValueStatus.hard
        else :
            raise ValueError('Expected set of brands, got {0}'.format(type(value)))

    def update(self,
               gjp):
        if self._status is not ValueStatus.hard:
            master_obj = self._master_object(gjp)
            if 'brands' in master_obj:
                self._value = set()
                for brand in master_obj['brands']:
                    if brand['used']:
                        self._value.add(brand['name'])
                self._status = ValueStatus.soft
            
    def gjp(self,
            gjp):
        if self._status is ValueStatus.hard:
            gjp['brands'] = []
            for brand in self._all_brands:
                gjp['brands'].append({'name': brand,
                                      'used': brand in self._value,
                                      'html_index': False})


