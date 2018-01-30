from open_publishing.core import FieldDescriptor, DatabaseObjectField, SimpleField
from open_publishing.user import User
from open_publishing.core.enums import ProvisionRuleRole
from open_publishing.currency import CurrencyValueField
from open_publishing.core.enums import ProvisionRuleAlgorithm

from .rule import ProvisionRule
from .filter_list import ProvisionFilterList


class FixedRule(ProvisionRule):
    
    def __init__(self,
                 context,
                 rule_id):
        super(FixedRule, self).__init__(context,
                                             rule_id)
        self._fields['recipient'] = DatabaseObjectField(parent=self,
                                                        aspect='*',
                                                        field_locator='recipient_user_id',
                                                        dtype=User)

        self._fields['amount'] = CurrencyValueField(database_object=self,
                                                    aspect='*',
                                                    field_locator='fixed_amount')

        self._fields['role'] = SimpleField(database_object=self,
                                           aspect='*',
                                           field_locator='role',
                                           dtype=ProvisionRuleRole)

        self._fields['one_time'] = SimpleField(database_object=self,
                                               aspect='*',
                                               field_locator='one_time',
                                               dtype=str)
    recipient = FieldDescriptor('recipient')
    amount = FieldDescriptor('amount')
    _role = FieldDescriptor('role')
    _one_time = FieldDescriptor('one_time')


class FixedList(ProvisionFilterList):
    _filter = ProvisionRuleAlgorithm.fixed

    def __init__(self,
                 provision_list):
        super(FixedList, self).__init__(provision_list)
    

    def add(self,
            recipient,
            amount):
        with FixedRule._create(self._provision_list._database_object._context,
                               channels=[]) as rule:
            rule._algorithm = ProvisionRuleAlgorithm.fixed
            rule._source_type = 'DOCUMENT'
            rule._reference_id = self._provision_list._document.document_id
            rule._scope = 'PUBLISH'
            rule.recipient = recipient
            rule._role = ProvisionRuleRole.author
            rule.amount = amount

        new_rule = FixedRule(self._provision_list._database_object._context,
                             rule.rule_id)
        new_rule._one_time = 'YES'
        self._provision_list._objects[rule.rule_id] = new_rule
        self._provision_list._ids.append(rule.rule_id)
        return self[-1]
        

