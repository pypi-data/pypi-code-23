import datetime

from .core import SimpleField, FieldDescriptor, DatabaseObject, FieldGroup
from .core.enums import UserStatus, FieldKind, Gender, Country, Language, ProfileShow
from .object_events import ObjectEvents
from .subscriptions import SubscriptionsField
from .extendable_enum_field import ExtendableEnumField
from .taxes.tax_group import TaxGroup

class User(DatabaseObject):
    _object_class = 'user'

    def __init__(self,
                 context,
                 user_id):
        super(User, self).__init__(context,
                                   user_id)

        self._fields['screenname'] = SimpleField(database_object=self,
                                                 aspect=':basic',
                                                 field_locator='screenname',
                                                 dtype=str)

        self._fields['username'] = SimpleField(database_object=self,
                                                 aspect='login.*',
                                                 field_locator='login.login_username',
                                                 dtype=str)

        self._fields['status'] = SimpleField(database_object=self,
                                             aspect=':basic',
                                             field_locator='status',
                                             dtype=UserStatus,
                                             kind=FieldKind.readonly)

        self._fields['mail_blocked'] = SimpleField(database_object=self,
                                                   aspect='email.*',
                                                   field_locator='email.mail_blocked',
                                                   dtype=str)

        self._fields['login_blocked'] = SimpleField(database_object=self,
                                                    aspect='login.*',
                                                    field_locator='login.blocked',
                                                    dtype=str)

        self._fields['may_receive_mails'] = SimpleField(database_object=self,
                                                  aspect='may_receive_mails',
                                                  field_locator='may_receive_mails',
                                                  dtype=bool,
                                                  kind=FieldKind.readonly)

        self._fields['email'] = SimpleField(database_object=self,
                                            aspect='email.*',
                                            field_locator='email.email',
                                            dtype=str)

        self._fields['subscription_email'] = SimpleField(database_object=self,
                                            aspect='email.*',
                                            field_locator='email.subscription_email',
                                            dtype=str)

        self._fields['first_name'] = SimpleField(database_object=self,
                                                 aspect='masterdata.*',
                                                 field_locator='masterdata.first_name',
                                                 dtype=str)

        self._fields['last_name'] = SimpleField(database_object=self,
                                                aspect='masterdata.*',
                                                field_locator='masterdata.last_name',
                                                dtype=str)

        self._fields['gender'] = SimpleField(database_object=self,
                                             aspect='masterdata.*',
                                             field_locator='masterdata.gender',
                                             dtype=Gender)

        self._fields['academic_title'] = SimpleField(database_object=self,
                                                      aspect='masterdata.*',
                                                      field_locator='masterdata.academic_title',
                                                      dtype=str)

        self._fields['biography'] = SimpleField(database_object=self,
                                                      aspect='biography.*',
                                                      field_locator='biography.short_biography',
                                                      dtype=str)

        self._fields['company'] = SimpleField(database_object=self,
                                              aspect='masterdata.*',
                                              field_locator='masterdata.company',
                                              dtype=str)


        self._fields['last_purchase'] = LastPurchaseField(database_object=self)

        self._fields['last_upload'] = SimpleField(database_object=self,
                                                  aspect='last_upload',
                                                  field_locator='last_upload',
                                                  dtype=datetime.datetime,
                                                  kind=FieldKind.readonly,
                                                  nullable=True)
                                                
        self._fields['last_login'] = SimpleField(database_object=self,
                                                 aspect='last_login',
                                                 field_locator='last_login',
                                                 dtype=datetime.datetime,
                                                 kind=FieldKind.readonly,
                                                 nullable=True)

        self._fields['language'] = ExtendableEnumField(database_object=self,
                                                       aspect='language_id',
                                                       field_locator='language_id',
                                                       dtype=Language,
                                                       nullable=True,
                                                       serialized_null=0)

        self._fields['brands'] = SimpleField(database_object=self,
                                             aspect='brands',
                                             field_locator='brands',
                                             dtype=set,
                                             kind=FieldKind.readonly)

        self._fields['imprints'] = SimpleField(database_object=self,
                                               aspect='imprints',
                                               field_locator='imprints',
                                               dtype=set,
                                               kind=FieldKind.readonly)

        self._fields['subscriptions'] = SubscriptionsField(self)
        self._fields['documents'] = UserDocuments(self) 
        self._fields['address'] = UserAddress(self) 
        self._fields['bankdetails'] = UserBankdetails(self) 
        self._fields['statement'] = UserStatement(self) 
        self._fields['taxes'] = TaxGroup(self) 
        self._fields['profile'] = UserProfile(self) 

        self._events = ObjectEvents(self)
        self._avatar = UserAvatar(self)

    screenname = FieldDescriptor('screenname')
    username = FieldDescriptor('username')
    _status = FieldDescriptor('status')
    _mail_blocked = FieldDescriptor('mail_blocked')
    _login_blocked = FieldDescriptor('login_blocked')
    may_receive_mails = FieldDescriptor('may_receive_mails')
    email = FieldDescriptor('email')
    subscription_email = FieldDescriptor('subscription_email')
    first_name = FieldDescriptor('first_name')
    last_name = FieldDescriptor('last_name')
    gender = FieldDescriptor('gender')
    academic_title = FieldDescriptor('academic_title')
    biography = FieldDescriptor('biography')
    company = FieldDescriptor('company')
    last_purchase = FieldDescriptor('last_purchase')
    last_upload = FieldDescriptor('last_upload')
    last_login = FieldDescriptor('last_login')
    language = FieldDescriptor('language')
    brands = FieldDescriptor('brands')
    imprints = FieldDescriptor('imprints')

    subscriptions = FieldDescriptor('subscriptions')
    documents = FieldDescriptor('documents')
    address = FieldDescriptor('address')
    bankdetails = FieldDescriptor('bankdetails')
    statement = FieldDescriptor('statement')
    taxes = FieldDescriptor('taxes')
    profile = FieldDescriptor('profile')

    @property
    def events(self):
        return self._events

    @property
    def avatar(self):
        return self._avatar

    @property
    def active(self):
        return self._status is UserStatus.active

    @property
    def blocked(self):
        return (self._mail_blocked != '') or (self._login_blocked != '')

    @property
    def author(self):
        return self.last_upload is not None
    
    @property
    def buyer(self):
        return self.last_purchase is not None
    
    @property
    def user_id(self):
        return self._object_id

    def _on_changed(self):
        self._context.users._add_to_changed(self)

    def _on_flush(self):
        self._context.users._remove_from_changed(self)
        

    def reset_password(self):
        self.context.gjp.reset_password(self.user_id)

    def set_password(self,
                     password):
        self.context.gjp.set_password(self.user_id,
                                        password)

class LastPurchaseField(SimpleField):
    def __init__(self,
                 database_object):
        super(LastPurchaseField, self).__init__(database_object,
                                                aspect='last_purchase',
                                                field_locator='last_purchase',
                                                dtype=datetime.datetime,
                                                kind=FieldKind.readonly,
                                                nullable=True)

    def _parse_value(self,
                     value):
        if value is None and self._nullable:
            return value
        else :
            # return datetime.datetime.strptime(value, '%d.%m.%Y')
            return datetime.datetime(*[int(i) for i in value.split('.')][::-1])


class UserDocuments(FieldGroup):
    def __init__(self,
                 user):
        super(UserDocuments, self).__init__(user)
        self._fields['count'] = SimpleField(database_object=user,
                                            aspect='count_own_documents',
                                            field_locator='count_own_documents',
                                            dtype=int,
                                            kind=FieldKind.readonly)

    count = FieldDescriptor('count')


class UserAddress(FieldGroup):
    def __init__(self,
                 user):
        super(UserAddress, self).__init__(user)
        
        self._fields['street'] = SimpleField(database_object=user,
                                             aspect='masterdata.*',
                                             field_locator='masterdata.street',
                                             dtype=str)
        
        self._fields['city'] = SimpleField(database_object=user,
                                           aspect='masterdata.*',
                                           field_locator='masterdata.city',
                                           dtype=str)
        
        self._fields['zip'] = SimpleField(database_object=user,
                                          aspect='masterdata.*',
                                          field_locator='masterdata.zip',
                                          dtype=str)

        self._fields['country'] = ExtendableEnumField(database_object=user,
                                                      aspect='masterdata.*',
                                                      field_locator='masterdata.country_id',
                                                      dtype=Country,
                                                      nullable=True,
                                                      serialized_null=0)

        
        self._fields['tel'] = SimpleField(database_object=user,
                                          aspect='masterdata.*',
                                          field_locator='masterdata.tel',
                                          dtype=str)
        
        self._fields['fax'] = SimpleField(database_object=user,
                                          aspect='masterdata.*',
                                          field_locator='masterdata.fax',
                                          dtype=str)
        
        
    street = FieldDescriptor('street')
    city = FieldDescriptor('city')
    zip = FieldDescriptor('zip')
    country = FieldDescriptor('country')
    tel = FieldDescriptor('tel')
    fax = FieldDescriptor('fax')


class UserBankdetails(FieldGroup):
    def __init__(self,
                 user):
        super(UserBankdetails, self).__init__(user)
        
        self._fields['iban'] = SimpleField(database_object=user,
                                           aspect='account.*',
                                           field_locator='account.int_iban',
                                           dtype=str)

        self._fields['swift'] = SimpleField(database_object=user,
                                            aspect='account.*',
                                            field_locator='account.int_swift',
                                            dtype=str)

        self._fields['holder'] = SimpleField(database_object=user,
                                                     aspect='account.*',
                                                     field_locator='account.holder',
                                                     dtype=str)
    
    iban = FieldDescriptor('iban')
    swift = FieldDescriptor('swift')
    holder = FieldDescriptor('holder')

class UserStatement(FieldGroup):
    def __init__(self,
                 user):
        super(UserStatement, self).__init__(user)
        
        self._fields['statement_mail'] = SimpleField(database_object=user,
                                                     aspect='account.*',
                                                     field_locator='account.account_statement_mail',
                                                     dtype=bool)

        self._fields['generate_statement'] = SimpleField(database_object=user,
                                                     aspect='account.*',
                                                     field_locator='account.generate_statement',
                                                     dtype=bool)

    statement_mail = FieldDescriptor('statement_mail')
    generate_statement = FieldDescriptor('generate_statement')


class UserAvatar(object):
    def __init__(self,
                 user):
        self._user = user

    def upload(self, file_name):
        self._user.context.gjp.upload_avatar(self._user.user_id, file_name)

class UserProfile(FieldGroup):
    def __init__(self,
                 user):
        super(UserProfile, self).__init__(user)
        
        self._fields['show'] = SimpleField(database_object=user,
                                                   aspect='profile.*',
                                                   field_locator='profile.show_profile',
                                                   dtype=ProfileShow)


    show = FieldDescriptor('show')

