from open_publishing.core import DatabaseObject, FieldDescriptor, SimpleField
from open_publishing.core.enums import ProvisionRuleAlgorithm

class ProvisionRule(DatabaseObject):
    _object_class = 'provision_rule'

    def __init__(self,
                 context,
                 rule_id):
        super(ProvisionRule, self).__init__(context,
                                            rule_id)
        self._fields['algorithm'] = SimpleField(database_object=self,
                                                aspect='*',
                                                field_locator='algorithm',
                                                dtype=ProvisionRuleAlgorithm)

        self._fields['source_type'] = SimpleField(database_object=self,
                                                  aspect='*',
                                                  field_locator='source_type',
                                                  dtype=str)

        self._fields['reference_id'] = SimpleField(database_object=self,
                                                    aspect='*',
                                                    field_locator='reference_id',
                                                    dtype=int)

        self._fields['scope'] = SimpleField(database_object=self,
                                                  aspect='*',
                                                  field_locator='scope',
                                                  dtype=str)

    _algorithm = FieldDescriptor('algorithm')
    _source_type = FieldDescriptor('source_type')
    _reference_id = FieldDescriptor('reference_id')
    _scope = FieldDescriptor('scope')

    @property
    def algorithm(self):
        return self._algorithm

    @property
    def rule_id(self):
        return self._object_id



