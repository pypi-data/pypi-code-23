from open_publishing.core import SequenceItem, SequenceField, SequenceItemProperty
from open_publishing.core import FieldDescriptor, DatabaseObjectField, SimpleField
from open_publishing.user import User
from open_publishing.core.enums import ValueStatus
from open_publishing.core.enums import ProvisionRuleRole, ProvisionChannelType, ProvisionChannelBase
from open_publishing.core.enums import ProvisionRuleAlgorithm

from .rule import ProvisionRule
from .filter_list import ProvisionFilterList

class Progression(SequenceItem):
    def __init__(self,
                 threshold,
                 rate):
        super(Progression, self).__init__(ValueStatus.soft)
        self.threshold = threshold
        self.rate = rate
        self._status = ValueStatus.soft

    threshold = SequenceItemProperty('threshold')
    rate = SequenceItemProperty('rate')
        
    @classmethod
    def from_gjp(cls, gjp, database_object):
        threshold = gjp['threshold']
        rate = gjp['value']
        return cls(threshold,
                   rate)
    
    def to_gjp(self):
        return {'threshold': self.threshold,
                'value': self.rate}

class ChannelProgressionList(SequenceField):
    _item_type = Progression
    
    def __init__(self,
                 rule):
        super(ChannelProgressionList, self).__init__(rule,
                                                     'channels.*',
                                                     'progressions')
        
    def add(self,
            threshold,
            value):
        self._list.append(Progression(threshold,
                                      value))
        self._status = ValueStatus.hard
        return self[-1]

    def from_gjp(self,
                 gjp):
        self._list = []
        for item in gjp['progressions'] if gjp['progressions'] else []:
            self._list.append(self._item_type.from_gjp(item, self.database_object))
        self._status = ValueStatus.soft
                
    def to_gjp(self):
        return [item.to_gjp() for item in self._list]

class ProgressionChannel(SequenceItem):
    def __init__(self,
                 rule,
                 channel_type,
                 base,
                 group):
        super(ProgressionChannel, self).__init__(ValueStatus.soft)
        self._rule = rule
        self.channel_type = channel_type
        self.base = base
        self.progressions = ChannelProgressionList(self._rule)
        self.group = group
        self._status = ValueStatus.soft

    channel_type = SequenceItemProperty('channel_type')
    base = SequenceItemProperty('base')
    group = SequenceItemProperty('group')


    @property
    def rule(self):
        return self._rule

    @property
    def status(self):
        if self.progressions.status is ValueStatus.hard:
            return ValueStatus.hard
        else:
            return super(ProgressionChannel, self).status
        
    @classmethod
    def from_gjp(cls, gjp, database_object):
        channel_type = ProvisionChannelType.from_id(gjp['channel'])
        base = ProvisionChannelBase.from_id(gjp['basis'])
        group = gjp['group']
        res = cls(database_object,
                  channel_type,
                  base,
                  group if group !='' else None)
        res.progressions.from_gjp(gjp)
        return res
    
    def to_gjp(self):
        res = {'channel': self.channel_type.identifier,
               'basis': self.base.identifier,
               'group': self.group if self.group else '',
               'progressions': self.progressions.to_gjp()}
        return res
      
class ProgressionChannelsList(SequenceField):
    _item_type = ProgressionChannel
    
    def __init__(self,
                 rule):
        super(ProgressionChannelsList, self).__init__(rule,
                                                     'channels.*',
                                                     'channels')
        
    def add(self,
            rate,
            channel_type = ProvisionChannelType.book_and_ebook,
            base = ProvisionChannelBase.net_price,
            progressions = None,
            group = None):
        progression_channel = ProgressionChannel(self.database_object,
                                         channel_type,
                                         base,
                                         group)
        progression_channel.progressions.add(1, rate)
        if progressions is not None:
            for threshold, rate in progressions:
                progression_channel.progressions.add(threshold, rate)
        
        self._list.append(progression_channel)
        self._status = ValueStatus.hard
        return self[-1]

class ProgressionRule(ProvisionRule):
    
    def __init__(self,
                 context,
                 rule_id):
        super(ProgressionRule, self).__init__(context,
                                             rule_id)
        self._fields['recipient'] = DatabaseObjectField(parent=self,
                                                        aspect='*',
                                                        field_locator='recipient_user_id',
                                                        dtype=User)

        self._fields['role'] = SimpleField(database_object=self,
                                           aspect='*',
                                           field_locator='role',
                                           dtype=ProvisionRuleRole)
                                                
        self._fields['channels'] = ProgressionChannelsList(rule=self)

    recipient = FieldDescriptor('recipient')
    role = FieldDescriptor('role')
    channels = FieldDescriptor('channels')
        

class ProgressionList(ProvisionFilterList):
    _filter = ProvisionRuleAlgorithm.progression

    def __init__(self,
                 provision_list):
        super(ProgressionList, self).__init__(provision_list)
    

    def add(self,
            recipient,
            role):
        with ProgressionRule._create(self._provision_list._database_object._context,
                                    channels=[]) as rule:
            rule._algorithm = ProvisionRuleAlgorithm.progression
            rule._source_type = 'DOCUMENT'
            rule._reference_id = self._provision_list._document.document_id
            rule._scope = 'SALE'
            rule.recipient = recipient
            rule.role = role

        new_rule = ProgressionRule(self._provision_list._database_object._context,
                                    rule.rule_id)
        self._provision_list._objects[rule.rule_id] = new_rule
        self._provision_list._ids.append(rule.rule_id)
        return self[-1]
        
