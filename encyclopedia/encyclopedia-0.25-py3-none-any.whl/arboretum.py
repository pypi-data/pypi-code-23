# standard
import unittest
# external
# internal
from encyclopedia.relate import Function
from encyclopedia.forest import Forest

class Arboretum(Forest):
    '''
    A Forest with inhertiable attributes
    Note: as attributes are assigned using setitem syntax, tuples cannot be used as node aliases
    '''

    def __init__(self,
            offset:int=0,
            parent=None):

        Forest.__init__(self,
            offset=offset,
            parent=parent)
        self.attributes = Function()

    def __getitem__(self, key):
        if isinstance(key, tuple):
            assert len(key) == 2
            alias, attribute = key
            for node in self.aliased(alias):
                for other in reversed(self.limb(node).sorted()):
                    if (other, attribute) in self.attributes:
                        return self.attributes[(other, attribute)]
            return None
        else:
            return Forest.__setitem__(self, key)

    @Forest.unfrozen
    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            assert len(key) == 2
            alias, attribute = key
            for node in self.aliased(alias):
                self.attributes[(node, attribute)] = value
        else:
            Forest.__setitem__(self, key, value)

class Test_Arboretum(unittest.TestCase):
    '''
    Arboretum regression tests go here
    '''
    def setUp(self):
        self.larch = larch = Arboretum()
        larch += 'G01'
        larch['G01'] = 'G11'
        larch['G01'] = 'G12'
        larch['G11'] = 'G21'
        larch['G21'] = 'G31'
        larch['G21'] = 'G32'
        larch['G21'] = 'G33'
        larch['G32'] = 'G41'
        larch['G11','color'] = 'red'
        larch['G11','shape'] = 'diamond'
        larch['G01','shape'] = 'circle'
        larch['G21','color'] = 'blue'
        larch +=  'G02'

    def tearDown(self):
        pass

    def test_basic(self):
        larch = self.larch
        assert larch['G01','shape'] == 'circle'
        assert larch['G12','shape'] == 'circle'
        assert larch['G32','color'] == 'blue'
        assert larch['G32','smell'] is None

if __name__ == '__main__':
    unittest.main()
