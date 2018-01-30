from open_publishing.core import SequenceItem, SequenceField, SequenceItemProperty
from open_publishing.core import FieldDescriptor, DatabaseObjectField, SimpleField
from open_publishing.user import User
from open_publishing.core.enums import ValueStatus
from open_publishing.core.enums import ProvisionRuleRole, ProvisionChannelType, ProvisionChannelBase
from open_publishing.core.enums import ProvisionRuleAlgorithm

from .rule import ProvisionRule
from .filter_list import ProvisionFilterList

class PercentageChannel(SequenceItem):
    def __init__(self,
                 rule,
                 rate,
                 channel_type,
                 base,
                 group):
        super(PercentageChannel, self).__init__(ValueStatus.soft)
        self._rule = rule
        self.rate = rate
        self.channel_type = channel_type
        self.base = base
        self.group = group
        self._status = ValueStatus.soft

    rate = SequenceItemProperty('rate')
    channel_type = SequenceItemProperty('channel_type')
    base = SequenceItemProperty('base')
    group = SequenceItemProperty('group')

    @property
    def rule(self):
        return self._rule
        
    @classmethod
    def from_gjp(cls, gjp, database_object):
        rate = gjp['value']
        channel_type = ProvisionChannelType.from_id(gjp['channel'])
        base = ProvisionChannelBase.from_id(gjp['basis'])
        group = gjp['group']
        return cls(database_object,
                   rate,
                   channel_type,
                   base,
                   group if group !='' else None)
    
    def to_gjp(self):
        return {'channel': self.channel_type.identifier,
                'basis': self.base.identifier,
                'value': self.rate,
                'group': self.group if self.group else ''}

class PercentageChannelsList(SequenceField):
    _item_type = PercentageChannel
    
    def __init__(self,
                 rule):
        super(PercentageChannelsList, self).__init__(rule,
                                                     'channels.*',
                                                     'channels')
        
    def add(self,
            rate,
            channel_type = ProvisionChannelType.book_and_ebook,
            base = ProvisionChannelBase.net_price,
            group = None):
        self._list.append(PercentageChannel(self.database_object,
                                            rate,
                                            channel_type,
                                            base,
                                            group))
        self._status = ValueStatus.hard
        return self[-1]
    
class PercentageRule(ProvisionRule):
    
    def __init__(self,
                 context,
                 rule_id):
        super(PercentageRule, self).__init__(context,
                                             rule_id)
        self._fields['recipient'] = DatabaseObjectField(parent=self,
                                                        aspect='*',
                                                        field_locator='recipient_user_id',
                                                        dtype=User)

        self._fields['role'] = SimpleField(database_object=self,
                                           aspect='*',
                                           field_locator='role',
                                           dtype=ProvisionRuleRole)
                                                
        self._fields['channels'] = PercentageChannelsList(rule=self)
        
    recipient = FieldDescriptor('recipient')
    role = FieldDescriptor('role')
    channels = FieldDescriptor('channels')

class PercentageList(ProvisionFilterList):
    _filter = ProvisionRuleAlgorithm.percentage

    def __init__(self,
                 provision_list):
        super(PercentageList, self).__init__(provision_list)
    

    def add(self,
            recipient,
            role):
        with PercentageRule._create(self._provision_list._database_object._context,
                                    channels=[]) as rule:
            rule._algorithm = ProvisionRuleAlgorithm.percentage
            rule._source_type = 'DOCUMENT'
            rule._reference_id = self._provision_list._document.document_id
            rule._scope = 'SALE'
            rule.recipient = recipient
            rule.role = role
        new_rule = PercentageRule(self._provision_list._database_object._context,
                                  rule.rule_id)
        self._provision_list._objects[rule.rule_id] = new_rule
        self._provision_list._ids.append(rule.rule_id)
        return self[-1]
