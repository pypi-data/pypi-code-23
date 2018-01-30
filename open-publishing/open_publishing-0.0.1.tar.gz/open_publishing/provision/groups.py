import uuid

from open_publishing.core.enums import ProvisionRuleAlgorithm

from .percentage_rule import PercentageChannel, PercentageRule
from .progression_rule import ProgressionChannel, ProgressionRule
from .retainer_rule import RetainerRule

class ProvisionGroup(object):
    def __init__(self,
                 document,
                 name):
        self._name = name
        self._document = document

    @property
    def name(self):
        return self._name
    
    def __iter__(self):
        res = []
        for rule in self._document.provision_rules:
            if rule.algorithm in [ProvisionRuleAlgorithm.retainer]:
                if rule.group == self._name:
                    res.append(rule)
            elif rule.algorithm in [ProvisionRuleAlgorithm.percentage, ProvisionRuleAlgorithm.progression]:
                for channel in rule.channels:
                    if channel.group == self._name:
                        res.append(channel)
        return iter(res)

    @property
    def channels(self):
        res = []
        for rule in self._document.provision_rules:
            if rule.algorithm in [ProvisionRuleAlgorithm.percentage, ProvisionRuleAlgorithm.progression]:
                for channel in rule.channels:
                    if channel.group == self._name:
                        res.append(channel)
        return res

    @property
    def rules(self):
        res = []
        for rule in self._document.provision_rules:
            if rule.algorithm in [ProvisionRuleAlgorithm.retainer]:
                if rule.group == self._name:
                    res.append(rule)
        return res

    def insert(self,
               item):
        if isinstance(item, (RetainerRule, PercentageChannel, ProgressionChannel)):
            item.group = self._name
        elif isinstance(item, (PercentageRule, ProgressionRule)):
            for channel in item.channels:
                channel.group = self._name
        else:
            raise TypeError('Unexpected argument: {0}'.format(item))
        

class ProvisionGroups(object):
    def __init__(self,
                 document):
        self._document = document

    def __iter__(self):
        group_names = {None}
        res = []
        for rule in self._document.provision_rules:
            if rule.algorithm in [ProvisionRuleAlgorithm.retainer]:
                if rule.group not in group_names:
                    res.append(ProvisionGroup(self._document, rule.group))
                    group_names.add(rule.group)
            elif rule.algorithm in [ProvisionRuleAlgorithm.percentage, ProvisionRuleAlgorithm.progression]:
                for channel in rule.channels:
                    if channel.group not in group_names:
                        res.append(ProvisionGroup(self._document, channel.group))
                        group_names.add(channel.group)
                        
        return iter(res)

    def create(self,
               name = None,
               items = []):
        if name is None:
            name = str(uuid.uuid4())
        self[name] = items
        return ProvisionGroup(self._document, name)


    def __getitem__(self,
                    key):
        return ProvisionGroup(self._document, key)


    def __setitem__(self,
                    key,
                    value):
        del self[key]
        group = ProvisionGroup(self._document, key)
        for item in value:
            group.insert(item)

    def __delitem__(self,
                    key):
        group = ProvisionGroup(self._document, key)
        for item in group:
            item.group = None
