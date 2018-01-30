from open_publishing.core.enums import ValueStatus
from open_publishing.core import Field
from open_publishing.core.enums import Subscription

class SubscriptionsField(Field):
    def __init__(self,
                 user):
        super(SubscriptionsField, self).__init__(database_object=user,
                                                 aspect='email.*')
        self._value = None

    @property
    def value(self):
        if self.status is ValueStatus.none:
            raise RuntimeError('Accessing to field which is not set')
        else :
            return self._value.copy()

    def hard_set(self,
                 value):
        if isinstance(value, set):
            for sub in value:
                if sub not in Subscription:
                    raise ValueError('Unknown subscriptions used : {0}'.format(sub))
            self._value = value
            self._status = ValueStatus.hard
        else:
            raise ValueError('Expected set of subscriptions, got {0}'.format(type(value)))

    def update(self,
               gjp):
        if self._status is not ValueStatus.hard:
            master_obj = self._master_object(gjp)
            if 'email' in master_obj:
                self._value = set()
                if master_obj['email']['grin_info_mail']:
                    if master_obj['email']['buyer_newsletter']:
                        self._value.add(Subscription.buyer)
                    if master_obj['email']['author_newsletter']:
                        self._value.add(Subscription.author)
                    if master_obj['email']['general_newsletter']:
                        self._value.add(Subscription.general)
                self._status = ValueStatus.soft

    def gjp(self,
            gjp):
        if self._status is ValueStatus.hard:
            if 'email' not in gjp:
                gjp['email'] = {}

            gjp['email']['grin_info_mail'] = True if self._value else False
            gjp['email']['buyer_newsletter'] = Subscription.buyer in self._value
            gjp['email']['author_newsletter'] = Subscription.author in self._value
            gjp['email']['general_newsletter'] = Subscription.general in self._value
