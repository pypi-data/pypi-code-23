from marshmallow import Schema, fields, validates, validates_schema, ValidationError
import re
import math

class PermataVASchema(Schema):
    payment_type = fields.Str(required=True)
    transaction_details = fields.Nested('TransactionDetailsSchema', required=True)
    bank_transfer = fields.Nested('BankTransferSchema', required=True)
    item_details = fields.Nested('ItemDetailsSchema', many=True, required=True)
    customer_details = fields.Nested('CustomerDetailsSchema', required=True)

    @validates('payment_type')
    def validate_payment_type(self, data):
        if data != 'bank_transfer':
            raise ValidationError('Payment Type is not valid.')

class BCAVASchema(Schema):
    payment_type = fields.Str(required=True)
    transaction_details = fields.Nested('TransactionDetailsSchema', required=True)
    bank_transfer = fields.Nested('BankTransferSchema', required=True)
    item_details = fields.Nested('ItemDetailsSchema', many=True, required=True)
    customer_details = fields.Nested('CustomerDetailsSchema', required=True)

    @validates('payment_type')
    def validate_payment_type(self, data):
        if data != 'bank_transfer':
            raise ValidationError('Payment Type is not valid.')

class MandiriBillSchema(Schema):
    payment_type = fields.Str(required=True)
    transaction_details = fields.Nested('TransactionDetailsSchema', required=True)
    echannel = fields.Nested('EchannelSchema', required=True)
    item_details = fields.Nested('ItemDetailsSchema', many=True, required=True)
    customer_details = fields.Nested('CustomerDetailsSchema', required=True)
    custom_expiry = fields.Nested('CustomExpirySchema')

    @validates('payment_type')
    def validate_payment_type(self, data):
        if data != 'echannel':
            raise ValidationError('Payment Type is not valid.')

    @validates_schema
    def validate_total_item_details(self, data):
        item_details = data.get('item_details', [])
        gross_amount = data.get('transaction_details', {}).get('gross_amount', 0)

        if item_details:
            if sum([(x.get('price', 0) * x.get('quantity', 0)) for x in item_details]) != gross_amount:
                raise ValidationError("Transaction Details' Gross Amount is not equal to sum of Item Details")

class CIMBClicksSchema(Schema):
    payment_type = fields.Str(required=True)
    transaction_details = fields.Nested('TransactionDetailsSchema', required=True)
    cimb_clicks = fields.Nested('CIMBClicksDetailsSchema', required=True)
    item_details = fields.Nested('ItemDetailsSchema', many=True, required=True)
    customer_details = fields.Nested('CustomerDetailsSchema', required=True)
    custom_expiry = fields.Nested('CustomExpirySchema')

    @validates('payment_type')
    def validate_payment_type(self, data):
        if data != 'cimb_clicks':
            raise ValidationError('Payment Type is not valid.')

class BankTransferSchema(Schema):
    bank = fields.Str(required=True)
    va_number = fields.Str()
    free_text = fields.Dict()
    bca = fields.Dict()
    permata = fields.Dict()

    @validates_schema
    def validate_bank(self, data):
        if data.get('bank') not in ['permata', 'bca', 'bni']:
            raise ValidationError('Bank name is not valid.')

    @validates_schema
    def validate_permata(self, data):
        if data.get('permata', False) and data.get('bank') != 'permata' :
            raise ValidationError('Only fill out this field if the bank is Permata')

    @validates_schema
    def validate_bca_free_text(self, data):
        if data.get('free_text', False) and data.get('bank') != 'bca':
            raise ValidationError('Only fill out this field if the bank is BCA')

        if data.get('bca', False) and data.get('bank') != 'bca':
            raise ValidationError('Only fill out this field if the bank is BCA')

    @validates_schema
    def validate_va_number(self, data):
        if data.get('bank') == 'permata' and data.get('va_number', False):
            if len(data.get('va_number', 0)) != 10:
                raise ValidationError('For bank transfers to Permata, VA Number must be equal to 10 digits')

    # @validates_schema
    # def validate_va_number(self, data):
    #   if data.get('bank') is 'permata':

class TransactionDetailsSchema(Schema):
    order_id = fields.Str(required=True)
    gross_amount = fields.Int(required=True)

    @validates_schema
    def validate_order_id(self, data):
        regex = re.compile('^[\w\-\_\~\.]*$')
        if regex.match(data.get('order_id', '')) is None:
            raise ValidationError("Order ID can only contains alphanumerics, dash ('-'), tilde ('~'), underscore ('_'), and dot ('.')")

    @validates_schema
    def validate_gross_amount(self, data):
        number_separation = math.modf(data.get('gross_amount'))
        if number_separation[0] != 0:
            raise ValidationError('Gross Amount must be a whole number.')

class ItemDetailsSchema(Schema):
    id = fields.Str()
    price = fields.Int(required=True)
    quantity = fields.Int(required=True)
    name = fields.Str(required=True)
    category = fields.Str()
    merchant_name = fields.Str()

    @validates_schema
    def validate_price(self, data):
        number_separation = math.modf(data.get('price'))
        if number_separation[0] != 0:
            raise ValidationError('Price must be a whole number.')

class CustomerDetailsSchema(Schema):
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()
    phone = fields.Str()
    billing_address = fields.List(fields.Str())
    shipping_address = fields.List(fields.Str())

class CustomExpirySchema(Schema):
    order_time = fields.Str()
    expiry_duration = fields.Str()
    unit = fields.Str()

    @validates('unit')
    def validate_unit(self, data):
        if data not in ['second', 'minute', 'hour', 'day']:
            raise ValidationError('Unit must be either second, minute, hour or day.')

    @validates('expiry_duration')
    def validate_expiry_duration(self, data):
        regex = re.compile('^[0-9]*$')
        if regex.match(data) is None:
            raise ValidationError('Expiry Duration must be a number')

        number_separation = math.modf(float(data))
        if number_separation[0] != 0:
            raise ValidationError('Expiry Duration must be a whole number.')

class EchannelSchema(Schema):
    bill_info1 = fields.Str(required=True)
    bill_info2 = fields.Str(required=True)
    bill_info3 = fields.Str()
    bill_info4 = fields.Str()
    bill_info5 = fields.Str()
    bill_info6 = fields.Str()
    bill_info7 = fields.Str()
    bill_info8 = fields.Str()

class CIMBClicksDetailsSchema(Schema):
    description = fields.Str(required=True)
