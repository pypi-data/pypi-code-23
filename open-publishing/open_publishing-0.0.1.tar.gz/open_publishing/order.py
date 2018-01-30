import datetime
import traceback

from .core import SequenceItem, SequenceField
from .core import SimpleField, FieldDescriptor, DatabaseObject, FieldGroup
from .core.enums import ValueStatus, FieldKind, OrderItemType, ShippingLevel
from .currency import CurrencyValue

class Order(DatabaseObject):
    _object_class = 'order'

    def __init__(self,
                 context,
                 order_id):
        super(Order, self).__init__(context,
                                    order_id)

        self._fields['provider'] = SimpleField(database_object=self,
                                               aspect='*',
                                               field_locator='provider',
                                               dtype=str,
                                               nullable=True,
                                               kind=FieldKind.readonly)

        self._fields['shipping_level'] = SimpleField(database_object=self,
                                                     aspect='*',
                                                     field_locator='shipping_level',
                                                     dtype=ShippingLevel,
                                                     nullable=True,
                                                     kind=FieldKind.readonly)

        self._fields['datetime'] = SimpleField(database_object=self,
                                               aspect='*',
                                               field_locator='datetime',
                                               dtype=datetime.datetime,
                                               nullable=True,
                                               kind=FieldKind.readonly)

        self._fields['country_code'] = SimpleField(database_object=self,
                                                   aspect='*',
                                                   field_locator='country_code',
                                                   dtype=str,
                                                   nullable=True,
                                                   kind=FieldKind.readonly)

        self._fields['language_code'] = SimpleField(database_object=self,
                                                    aspect='*',
                                                    field_locator='language_code',
                                                    dtype=str,
                                                    nullable=True,
                                                    kind=FieldKind.readonly)
        
        self._fields['distribution_channel'] = SimpleField(database_object=self,
                                                           aspect='*',
                                                           field_locator='distribution_channel',
                                                           dtype=str,
                                                           nullable=True,
                                                           kind=FieldKind.readonly)

        self._fields['channel_id'] = SimpleField(database_object=self,
                                                 aspect='*',
                                                 field_locator='channel_id',
                                                 dtype=str,
                                                 nullable=True,
                                                 kind=FieldKind.readonly)

        self._fields['external_id'] = SimpleField(database_object=self,
                                                  aspect='*',
                                                  field_locator='external_id',
                                                  dtype=str,
                                                  nullable=True,
                                                  kind=FieldKind.readonly)

        self._fields['user_external_id'] = SimpleField(database_object=self,
                                                       aspect='*',
                                                       field_locator='user_external_id',
                                                       dtype=str,
                                                       nullable=True,
                                                       kind=FieldKind.readonly)

        self._fields['payment_external_id'] = SimpleField(database_object=self,
                                                       aspect='*',
                                                       field_locator='payment_external_id',
                                                       dtype=str,
                                                       nullable=True,
                                                       kind=FieldKind.readonly)

        self._fields['shipping_address'] = AddressGroup(order=self,
                                                        address_locator='shipping_address')

        self._fields['invoice_address'] = AddressGroup(order=self,
                                                       address_locator='invoice_address')


        self._fields['items'] = OrderItemsList(order=self)

        self._fields['seller'] = PersonGroup(order=self,
                                             person_locator='seller')

        self._fields['buyer'] = PersonGroup(order=self,
                                            person_locator='buyer')
        
    provider = FieldDescriptor('provider')
    shipping_level = FieldDescriptor('shipping_level')
    datetime = FieldDescriptor('datetime')
    country_code = FieldDescriptor('country_code')
    language_code = FieldDescriptor('language_code')
    distribution_channel = FieldDescriptor('distribution_channel')
    channel_id = FieldDescriptor('channel_id')
    external_id = FieldDescriptor('external_id')
    user_external_id = FieldDescriptor('user_external_id')
    payment_external_id = FieldDescriptor('payment_external_id')
    shipping_address = FieldDescriptor('shipping_address')
    invoice_address = FieldDescriptor('invoice_address')
    items = FieldDescriptor('items')
    seller = FieldDescriptor('seller')
    buyer = FieldDescriptor('buyer')

    def flush(self):
        if self._object_id is None:
            super(Order, self).flush()


class AddressGroup(FieldGroup):
    def __init__(self,
                 order,
                 address_locator):
        super(AddressGroup, self).__init__(order)
        self._address_locator = address_locator
        self._is_null = None

        self._fields['zip'] = SimpleField(database_object=order,
                                          aspect='*',
                                          field_locator=address_locator + '.zip',
                                          dtype=str,
                                          nullable=True,
                                          kind=FieldKind.readonly)

        self._fields['city'] = SimpleField(database_object=order,
                                           aspect='*',
                                           field_locator=address_locator + '.city',
                                           dtype=str,
                                           nullable=True,
                                           kind=FieldKind.readonly)

        self._fields['state'] = SimpleField(database_object=order,
                                           aspect='*',
                                           field_locator=address_locator + '.state',
                                           dtype=str,
                                           nullable=True,
                                           kind=FieldKind.readonly)

        self._fields['street'] = SimpleField(database_object=order,
                                             aspect='*',
                                             field_locator=address_locator + '.street',
                                             dtype=str,
                                             nullable=True,
                                             kind=FieldKind.readonly)

        self._fields['line2'] = SimpleField(database_object=order,
                                            aspect='*',
                                            field_locator=address_locator + '.line2',
                                            dtype=str,
                                            nullable=True,
                                            kind=FieldKind.readonly)

        self._fields['line3'] = SimpleField(database_object=order,
                                            aspect='*',
                                            field_locator=address_locator + '.line3',
                                            dtype=str,
                                            nullable=True,
                                            kind=FieldKind.readonly)


        self._fields['academic_title'] = SimpleField(database_object=order,
                                                     aspect='*',
                                                     field_locator=address_locator + '.academic_title',
                                                     dtype=str,
                                                     nullable=True,
                                                     kind=FieldKind.readonly)


        self._fields['first_name'] = SimpleField(database_object=order,
                                                 aspect='*',
                                                 field_locator=address_locator + '.first_name',
                                                 dtype=str,
                                                 nullable=True,
                                                 kind=FieldKind.readonly)


        self._fields['last_name'] = SimpleField(database_object=order,
                                                aspect='*',
                                                field_locator=address_locator + '.last_name',
                                                dtype=str,
                                                nullable=True,
                                                kind=FieldKind.readonly)


        self._fields['country_code'] = SimpleField(database_object=order,
                                                   aspect='*',
                                                   field_locator=address_locator + '.country_code',
                                                   dtype=str,
                                                   nullable=True,
                                                   kind=FieldKind.readonly)

        self._fields['phone_number'] = SimpleField(database_object=order,
                                                   aspect='*',
                                                   field_locator=address_locator + '.phone_number',
                                                   dtype=str,
                                                   nullable=True,
                                                   kind=FieldKind.readonly)

        self._fields['external_address_id'] = SimpleField(database_object=order,
                                                          aspect='*',
                                                          field_locator=address_locator + '.external_address_id',
                                                          dtype=str,
                                                          nullable=True,
                                                          kind=FieldKind.readonly)

    zip = FieldDescriptor('zip')
    city = FieldDescriptor('city')
    state = FieldDescriptor('state')
    street = FieldDescriptor('street')
    line2 = FieldDescriptor('line2')
    line3 = FieldDescriptor('line3')
    academic_title = FieldDescriptor('academic_title')
    first_name = FieldDescriptor('first_name')
    last_name = FieldDescriptor('last_name')
    country_code = FieldDescriptor('country_code')
    phone_number = FieldDescriptor('phone_number')
    external_address_id = FieldDescriptor('external_address_id')

    @property
    def value(self):
        if self._is_null:
            return None
        else:
            return self

    def update(self,
               gjp):
        value = self._master_object(gjp)
        for fname in self._address_locator.split("."):
            if fname in value:
                value = value[fname]
            else :
                return
        self._is_null = value is None
        self._status = ValueStatus.soft

        if not self._is_null:
            for name, field in list(self._fields.items()):
                try:
                    field.update(gjp)
                except Exception as e:
                    raise RuntimeError("Update failed for field: '{0}'\n{1}"
                                       .format(name,
                                               ''.join(traceback.format_exception_only(type(e), e))))

    def __str__(self):
        return '{firstname} {lastname}; {street}; {line2}; {line3}; {city} {state} {zip}; {country}'.format(
            firstname=self.first_name,
            lastname=self.last_name,
            street=self.street,
            line2=self.line2,
            line3=self.line3,
            city=self.city,
            state=self.state,
            zip=self.zip,
            country=self.country_code
        )

def Address(first_name,
            last_name,
            street,
            zip,
            city,
            country_code,
            state = None,
            academic_title = None,
            line2 = None,
            line3 = None,
            phone_number = None,
            external_address_id = None):
    res = AddressGroup(None, "")
    res.first_name = first_name
    res.last_name = last_name
    res.street = street
    res.zip = zip
    res.city = city
    res.country_code = country_code
    if state is not None:
        res.state = state
    if line2 is not None:
        res.line2 = line2
    if line3 is not None:
        res.line3 = line3
    if phone_number is not None:
        res.phone_number = phone_number
    if external_address_id is not None:
        res.external_address_id = external_address_id
    if academic_title is not None:
        res.academic_title = academic_title
    return res


class OrderItem(SequenceItem):
    def __init__(self,
                 identifier,
                 quantity,
                 type,
                 net_margin_per_unit,
                 net_distributor_price_per_unit,
                 vat_percentage,
                 external_id):
        super(OrderItem, self).__init__(ValueStatus.soft)
        self.identifier = identifier
        self.quantity = quantity
        self.net_margin_per_unit = net_margin_per_unit
        self.type = type
        self.vat_percentage = vat_percentage
        self.external_id = external_id
        self.net_distributor_price_per_unit = net_distributor_price_per_unit
        self._status = ValueStatus.soft

    @property
    def status(self):
        return self._status

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        if isinstance(value, str) or value is None:
            self._identifier = value
            self._status = ValueStatus.hard
        else:
            raise TypeError("identifier should be instance of str or None")

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value in OrderItemType:
            self._type = value
            self._status = ValueStatus.hard
        else:
            raise TypeError("type should be one of op.order.item.type.*")

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if isinstance(value, int):
            self._quantity = value
            self._status = ValueStatus.hard
        else:
            raise TypeError("quantity should be instance of int")

    @property
    def vat_percentage(self):
        return self._vat_percentage

    @vat_percentage.setter
    def vat_percentage(self, value):
        if isinstance(value, int):
            value = float(value)
        if isinstance(value, float) or (value is None):
            self._vat_percentage = value
            self._status = ValueStatus.hard
        else:
            raise TypeError("vat_percentage should be instance of float or int")

    @property
    def net_margin_per_unit(self):
        return self._net_margin_per_unit

    @net_margin_per_unit.setter
    def net_margin_per_unit(self, value):
        self._net_margin_per_unit = CurrencyValue.create(value)
        self._status = ValueStatus.hard

    @property
    def net_distributor_price_per_unit(self):
        return self._net_distributor_price_per_unit

    @net_distributor_price_per_unit.setter
    def net_distributor_price_per_unit(self, value):
        if value is not None:
            self._net_distributor_price_per_unit = CurrencyValue.create(value)
        else:
            self._net_distributor_price_per_unit = value
        self._status = ValueStatus.hard

    @property
    def external_id(self):
        return self._external_id

    @external_id.setter
    def external_id(self, value):
        if isinstance(value, str) or value is None:
            self._external_id = value
            self._status = ValueStatus.hard
        else:
            raise TypeError("external_id should be instance of str")

    @classmethod
    def from_gjp(cls, gjp, database_object):
        identifier = gjp['identifier']
        quantity = gjp['quantity']
        type = OrderItemType.from_id(gjp['type'])
        net_margin_per_unit = CurrencyValue.from_gjp(gjp['net_margin_per_unit'])
        vat_percentage = gjp['vat_percentage']
        net_distributor_price_per_unit = CurrencyValue.from_gjp(gjp['net_distributor_price_per_unit'])
        external_id = gjp['external_id']

        return cls(identifier,
                   quantity,
                   type,
                   net_margin_per_unit,
                   net_distributor_price_per_unit,
                   vat_percentage,
                   external_id)

    def to_gjp(self):
        return {'identifier': self.identifier,
                'quantity': self.quantity,
                'net_margin_per_unit': self.net_margin_per_unit.to_gjp(),
                'net_distributor_price_per_unit': self.net_distributor_price_per_unit.to_gjp() if self.net_distributor_price_per_unit else None,
                'type': self.type.identifier,
                'vat_percentage': self.vat_percentage,
                'external_id' : self.external_id}



class OrderItemsList(SequenceField):
    _item_type = OrderItem

    def __init__(self,
                 order):
        super(OrderItemsList, self).__init__(order,
                                             "*",
                                             "items")
        self._status = ValueStatus.default

    def add(self,
            type,
            quantity,
            net_margin_per_unit,
            identifier = None,
            net_distributor_price_per_unit = None,
            vat_percentage = None,
            external_id = None):
        self._list.append(self._item_type(identifier,
                                          quantity,
                                          type,
                                          net_margin_per_unit,
                                          net_distributor_price_per_unit,
                                          vat_percentage,
                                          external_id))
        self._status = ValueStatus.hard

class PersonGroup(FieldGroup):
    def __init__(self,
                 order,
                 person_locator):
        super(PersonGroup, self).__init__(order)
        self._person_locator = person_locator
        self._is_null = None

        self._fields['id'] = SimpleField(database_object=order,
                                                 aspect='*',
                                                 field_locator=person_locator + '.id',
                                                 dtype=str,
                                                 nullable=True,
                                                 kind=FieldKind.readonly)
        
        self._fields['first_name'] = SimpleField(database_object=order,
                                                 aspect='*',
                                                 field_locator=person_locator + '.first_name',
                                                 dtype=str,
                                                 nullable=True,
                                                 kind=FieldKind.readonly)

        self._fields['last_name'] = SimpleField(database_object=order,
                                                aspect='*',
                                                field_locator=person_locator + '.last_name',
                                                dtype=str,
                                                nullable=True,
                                                kind=FieldKind.readonly)
        
        self._fields['email'] = SimpleField(database_object=order,
                                            aspect='*',
                                            field_locator=person_locator + '.email',
                                            dtype=str,
                                            nullable=True,
                                            kind=FieldKind.readonly)
        
        
    id = FieldDescriptor('id')
    first_name = FieldDescriptor('first_name')
    last_name = FieldDescriptor('last_name')
    email = FieldDescriptor('email')


    @property
    def value(self):
        if self._is_null:
            return None
        else:
            return self

    def update(self,
               gjp):
        value = self._master_object(gjp)
        for fname in self._person_locator.split("."):
            if fname in value:
                value = value[fname]
            else :
                return
        self._is_null = value is None
        self._status = ValueStatus.soft
        
        if not self._is_null:
            for name, field in list(self._fields.items()):
                try:
                    field.update(gjp)
                except Exception as e:
                    raise RuntimeError("Update failed for field: '{0}'\n{1}"
                                       .format(name,
                                               ''.join(traceback.format_exception_only(type(e), e))))
        

def Person(id = None,
           first_name = None,
           last_name = None,
           email = None):
    res = PersonGroup(None, "")
    res.id = id
    res.first_name = first_name
    res.last_name = last_name
    res.email = email
    return res
                
