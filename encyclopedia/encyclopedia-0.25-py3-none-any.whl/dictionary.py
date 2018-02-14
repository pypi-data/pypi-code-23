# standard
import unittest
# external
# internal
from encyclopedia.templates import Unindexed
'''
A simple application to show adding Encyclopedic features to the humble dictionary
'''
class Dictionary(dict, Unindexed):

    def __init__(self, mapping=None):
        dict.__init__(self)
        self.frozen = False
        if mapping is not None:
            self.update(mapping)

class Test_Dictionary(unittest.TestCase):

    def test_basic(self):
        mammals = Dictionary({'dog':'furry','kangaroo':'bouncy','tiger':'in Africa?'})
        fish = Dictionary({'catfish':'slimey','salmon':'suspicious','charlie':'left us'})
        creatures = mammals + fish
        assert len(creatures) == len(fish) + len(mammals)
        creatures -= fish
        assert creatures == mammals

    def test_compose(self):
        first = Dictionary({'a'+str(i):'b'+str(i) for i in range(10)})
        second = Dictionary({'b'+str(i):'c'+str(i) for i in range(5)})
        third = first * second
        assert len(third) == len(second)

        fruit = Dictionary({'apple':'red', 'blueberry':'blue'})
        colors = Dictionary({'red':'FF0000', 'blue':'0000FF', 'green':'00FF00'})
        assert fruit * colors == Dictionary({'apple': 'FF0000', 'blueberry': '0000FF'})

if __name__ == '__main__':
    unittest.main()