import uuid

from open_publishing.core import DatabaseObjectsList
from open_publishing.core.enums import ProvisionRuleAlgorithm

from .rule import ProvisionRule
from .percentage_rule import PercentageList, PercentageRule
from .progression_rule import ProgressionList, ProgressionRule
from .fixed_rule import FixedList, FixedRule
from .retainer_rule import RetainerList, RetainerRule
from .groups import ProvisionGroups

class ProvisionRulesList(DatabaseObjectsList):
    _database_object_type = ProvisionRule

    def __init__(self,
                 document):
        super(ProvisionRulesList, self).__init__(database_object=document,
                                                 aspect='provision_rules.algorithm',
                                                 list_locator = 'provision_rules')
        self._document = document


    def _create_object(self,
                       guid,
                       gjp):
        obj_id = self._database_object_type.id_from_guid(guid)
        algorithm = ProvisionRuleAlgorithm.from_id(gjp[guid]['algorithm'])
        if algorithm is ProvisionRuleAlgorithm.percentage:
            self._objects[obj_id] = PercentageRule(self._database_object._context,
                                                   obj_id)
        elif algorithm is ProvisionRuleAlgorithm.progression:
            self._objects[obj_id] = ProgressionRule(self._database_object._context,
                                                   obj_id)
        elif algorithm is ProvisionRuleAlgorithm.fixed:
            self._objects[obj_id] = FixedRule(self._database_object._context,
                                              obj_id)
        elif algorithm is ProvisionRuleAlgorithm.retainer:
            self._objects[obj_id] = RetainerRule(self._database_object._context,
                                                 obj_id)
        else:
            self._objects[obj_id] = self._database_object_type(self._database_object._context,
                                                               obj_id)
        self._objects[obj_id]._update(gjp)
        self._ids.append(obj_id)

    @property
    def percentage(self):
        return PercentageList(self)

    @property
    def progression(self):
        return ProgressionList(self)

    @property
    def fixed(self):
        return FixedList(self)

    @property
    def retainer(self):
        return RetainerList(self)

    @property
    def groups(self):
        return ProvisionGroups(self._document)


