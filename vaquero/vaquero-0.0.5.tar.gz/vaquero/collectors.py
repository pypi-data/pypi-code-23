import jmespath
import random

# See also: fill_in_unknowns in transformations as a collector.


def sampling(items, p):
    for item in items:
        if random.random() < p:
            yield item


class Collector:
    def update(self, item):
        raise NotImplementedError("Collector#update(item) not implemented")

    def update_over_all(self, items):
        for item in items:
            self.update(item)

    @property
    def collected(self):
        raise NotImplementedError("Collector#collected not implemented")


class SetCollector(Collector):
    """
    Collect the set of values for jmespaths over applied items.
    """
    def __init__(self, paths):
        self._paths = {}
        self._sets = {}
        self.add_paths(paths)

    def add_paths(self, paths):
        """
        :param paths: an interable of jmespath paths
        """
        for path in paths:
            self.add_path(path)

    def add_path(self, path):
        """
        :param path: a jmespath
        """
        self._paths[path] = jmespath.compile(path)

    def update(self, item):
        """
        Apply the paths to an item, collecting the values.

        :param item: an item to process
        """
        for path, jmes_obj in self._paths.items():
            res = jmes_obj.search(item)
            if res is not None:
                result_set = self._sets.get(path)
                if not result_set:
                    result_set = set()
                    self._sets[path] = result_set
                result_set.add(res)

    @property
    def collected(self):
        return self._sets


class GroupCollector(Collector):
    """
    Collect one item per group.
    """

    def __init__(self, group_f):
        """
        :param group_f: function which returns some key representing the group
        """
        self._group_f = group_f
        self._groups = {}

    def update(self, item):
        k = self._group_f(item)
        if k not in self._groups:
            self._groups[k] = item

    @property
    def collected(self):
        return self._groups
