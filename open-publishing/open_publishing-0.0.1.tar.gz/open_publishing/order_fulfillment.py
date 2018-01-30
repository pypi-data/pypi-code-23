import datetime
from collections import namedtuple

from .core import SequenceItem, SequenceField, SimpleField, SequenceItemProperty
from .core import FieldDescriptor, DatabaseObject
from .core.enums import ValueStatus, FieldKind, ShippingStatus, ShippingType

class OrderFulfillment(DatabaseObject):
    _object_class = 'order_fulfillment'

    def __init__(self,
                 context,
                 order_fulfillment_id):
        super(OrderFulfillment, self).__init__(context,
                                    order_fulfillment_id)

        self._fields['status'] = SimpleField(database_object=self,
                                             aspect='*',
                                             field_locator='status',
                                             dtype=ShippingStatus,
                                             kind=FieldKind.readonly)

        self._fields['shippings'] = ShippingsList(order_fulfillment=self)
        self._fields['external_supplier_references'] = ExternalSupplierReferenceList(order_fulfillment=self)
        
    shippings = FieldDescriptor('shippings')
    status = FieldDescriptor('status')
    external_supplier_references = FieldDescriptor('external_supplier_references')

class ShippingsItem(SequenceItem):
    def __init__(self,
                 shipped_at,
                 type,
                 tracking_id,
                 tracking_url):
        super(ShippingsItem, self).__init__(ValueStatus.soft)
        self._shipped_at = shipped_at
        self._type = type
        self._tracking_id = tracking_id
        self._tracking_url = tracking_url

    @property
    def shipped_at(self):
        return self._shipped_at

    @property
    def type(self):
        return self._type

    @property
    def tracking_id(self):
        return self._tracking_id

    @property
    def tracking_url(self):
        return self._tracking_url

    @classmethod
    def from_gjp(cls, gjp, database_object):
        shipped_at = datetime.datetime.fromtimestamp(gjp['shipped_at'])
        type = ShippingType.from_id(gjp['type'])
        tracking_id = gjp['tracking_id']
        tracking_url = gjp['tracking_url']

        return cls(shipped_at,
                   type,
                   tracking_id,
                   tracking_url)

    def to_gjp(self):
        raise RuntimeError('Shippings items are read-only')



class ShippingsList(SequenceField):
    _item_type = ShippingsItem

    def __init__(self,
                 order_fulfillment):
        super(ShippingsList, self).__init__(order_fulfillment,
                                            "*",
                                            "shippings",
                                            kind = FieldKind.readonly)



class ExternalSupplierReferenceItem(SequenceItem):
    def __init__(self,
                 id_type_name,
                 id_value,
                 products):
        super().__init__(ValueStatus.soft)
        self._id_type_name = id_type_name
        self._id_value = id_value
        self.products = ProductList(products)

    id_type_name = SequenceItemProperty('id_type_name')
    id_value = SequenceItemProperty('id_value')

    @property
    def id_type_name(self):
        return self._id_type_name

    @property
    def id_value(self):
        return self._id_value

    @classmethod
    def from_gjp(cls, gjp, database_object):
        id_type_name = gjp['id_type_name']
        id_value = gjp['id_value']
        products = gjp['products']

        return cls(id_type_name,
                   id_value,
                   products)

    def to_gjp(self):
        raise RuntimeError('External supplier reference items are read-only')



class ExternalSupplierReferenceList(SequenceField):
    _item_type = ExternalSupplierReferenceItem

    def __init__(self,
                 order_fulfillment):
        super().__init__(order_fulfillment,
                         '*',
                         'external_supplier_references',
                         kind = FieldKind.readonly)


ProductItem = namedtuple('ProductItem', ['ean', 'quantity', 'source_type', 'reference_id'])

class ProductList:
    def __init__(self,
                 products):
        self._content = [ProductItem(product['ean'], product['quantity'], product['source_type'], product['reference_id']) for product in products]

    def __iter__(self):
        return iter(self._content)

    def __len__(self):
        return len(self._content)

    def __getitem__(self, i):
        return self._content[i]

