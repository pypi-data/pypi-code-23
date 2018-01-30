class ProvisionFilterList(object):
    _filter = None
    def __init__(self,
                 provision_list):
        self._provision_list = provision_list

    @property
    def _ids(self):
        return [rule_id for rule_id, rule in list(self._provision_list._objects.items()) if rule.algorithm is self._filter]

    def __len__(self):
        return len(self._ids)

    def __getitem__(self, key):
        return self._provision_list._get_by_ids(self._ids[key])

    def __delitem__(self, key):
        return self._provision_list._remove_by_ids(self._ids[key])
        
    def __iter__(self):
        return iter(self._provision_list._get_by_ids(self._ids))

    def remove(self,
               index):
        del self[index]
    
